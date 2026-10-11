"""Newline-delimited JSON bridge for the palette. stdout is protocol only."""
import json
import os
import subprocess
import sys
import threading
import uuid
from dataclasses import asdict, replace
from pathlib import Path
from backend.protocol import MAX_BYTES, parse_request
from backend.registry import Registry
from backend.search import search
from backend.state import State


class Bridge:
    def __init__(self, root, emit):
        self.state = State(root)
        self.emit = emit
        self.registry = Registry()
        self.active = {}
        self.results = {}
        self.lock = threading.RLock()
        self.threads = []
        self.discovering = False

    def handle(self, message):
        request_id = message.get('request_id', '') if isinstance(message, dict) else ''
        opt_in_missing = False
        try:
            if not isinstance(message, dict):
                raise ValueError('Invalid message')
            op = message.get('op')
            if op == 'search':
                text = message.get('text')
                if not isinstance(text, str) or len(text.encode()) > MAX_BYTES:
                    raise ValueError('Invalid search text')
                settings = self.state.load_settings()
                found = search(text, settings.get('roots', []))
                self.results = {r.id: r for r in found}
                self.emit({'kind': 'results', 'request_id': request_id, 'results': [asdict(r) for r in found]})
            elif op == 'activate':
                target = self.results.get(message.get('id'))
                if not target:
                    raise ValueError('Search result is no longer available')
                # This is an explicit local-search action, never an AI tool.
                subprocess.Popen(['gio', 'launch' if target.kind == 'application' else 'open', target.target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.emit({'kind': 'activated'})
            elif op == 'settings':
                self.emit({'kind': 'settings', 'settings': self.state.load_settings()})
            elif op == 'configure':
                settings = self.state.load_settings()
                settings['roots'] = message.get('roots', settings.get('roots', []))
                settings['selection'] = message.get('selection', settings.get('selection', {}))
                self.state.save_settings(settings)
                self.emit({'kind': 'settings', 'settings': settings})
            elif op == 'opt_in':
                if type(message.get('enabled')) is not bool:
                    raise ValueError('Explicit opt-in required')
                settings = self.state.load_settings()
                settings['ai_enabled'] = message['enabled']
                self.state.save_settings(settings)
                if not settings['ai_enabled']:
                    self.cancel_all()
                self.emit({'kind': 'settings', 'settings': settings})
            elif op == 'discover':
                with self.lock:
                    if self.discovering:
                        return
                    self.discovering = True
                self._start_worker(self._discover, (request_id,))
            elif op == 'clear_history':
                self.cancel_all()
                self.state.clear_history()
                self.emit({'kind': 'history', 'history': {}, 'cleared': True})
            elif op == 'history':
                self.emit({'kind': 'history', 'history': self.state.history()})
            elif op == 'cancel':
                self.cancel_all()
            elif op == 'ask':
                if self.state.load_settings().get('ai_enabled') is not True:
                    opt_in_missing = True
                    raise ValueError('AI opt-in is required')
                request = parse_request(json.dumps(message.get('request')))
                request_id = request.request_id
                if request.conversation_id:
                    turns = self.state.history().get(request.conversation_id)
                    if not isinstance(turns, list) or not turns:
                        raise ValueError('Conversation unavailable')
                    for turn in turns:
                        if not isinstance(turn, dict) or turn.get('role') not in {'user', 'assistant'} or not isinstance(turn.get('text'), str):
                            raise ValueError('Invalid saved conversation')
                        if any(turn.get(key, '') != getattr(request, key) for key in ('route_id', 'model_id', 'backend_id')):
                            raise ValueError('Conversation destination mismatch')
                    if len(json.dumps(turns).encode()) + len(request.prompt.encode()) > MAX_BYTES:
                        raise ValueError('Conversation too large; start a new chat')
                    request = replace(request, history=tuple({'role': t['role'], 'content': t['text']} for t in turns))
                elif not request.temporary:
                    request = replace(request, conversation_id=uuid.uuid4().hex)
                adapter = self.registry.adapters.get(request.route_id)
                if adapter is None:
                    raise ValueError('Provider Q&A isolation is not yet verified')
                with self.lock:
                    if self.active:
                        raise ValueError('Cancel or finish the current request first')
                    cancel = threading.Event()
                    self.active[request_id] = cancel
                self._start_worker(self._answer, (adapter, request, cancel))
            else:
                raise ValueError('Unknown operation')
        except (ValueError, OSError, TypeError):
            # Request data and raw provider exceptions never enter diagnostics.
            reason = 'AI opt-in is required' if opt_in_missing else 'Request unavailable or invalid; check settings and provider readiness'
            self.emit({'kind': 'error', 'request_id': request_id, 'text': reason})

    def _start_worker(self, target, args):
        # Reap completed references instead of accumulating them per query.
        self.threads = [thread for thread in self.threads if thread.is_alive()]
        thread = threading.Thread(target=target, args=args, daemon=True)
        self.threads.append(thread)
        thread.start()

    def _discover(self, request_id):
        try:
            event = {'kind': 'providers', 'request_id': request_id,
                     'providers': [asdict(s) for s in self.registry.discover()]}
        except Exception:
            event = {'kind': 'discovery_error', 'request_id': request_id,
                     'text': 'Provider discovery failed; refresh to retry'}
        with self.lock:
            self.discovering = False
        self.emit(event)

    def _answer(self, adapter, request, cancel):
        terminal = 'error'
        text = ''
        try:
            for event in adapter.stream(request, cancel):
                if cancel.is_set():
                    break
                if event.kind == 'delta':
                    text += event.text
                    if len(text.encode()) > MAX_BYTES:
                        raise ValueError('Output limit')
                    self.emit(asdict(event))
                elif event.kind == 'done':
                    terminal = 'done'
            with self.lock:
                if terminal == 'done' and not cancel.is_set() and not request.temporary:
                    self.state.save_exchange(request, text)
        except Exception:
            terminal = 'error'
        finally:
            with self.lock:
                self.active.pop(request.request_id, None)
            self.emit({'kind': 'cancelled' if cancel.is_set() else terminal, 'request_id': request.request_id,
                       'conversation_id': '' if request.temporary else (request.conversation_id or request.request_id),
                       'text': 'Provider request failed' if terminal == 'error' and not cancel.is_set() else ''})

    def cancel_all(self):
        with self.lock:
            for cancel in self.active.values():
                cancel.set()


def main():
    output_lock = threading.Lock()
    def emit(value):
        with output_lock:
            print(json.dumps(value), flush=True)
    root = Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'omarchy-model-search'
    bridge = Bridge(root, emit)
    try:
        while True:
            raw = sys.stdin.buffer.readline(MAX_BYTES + 1)
            if not raw:
                break
            if len(raw) > MAX_BYTES:
                emit({'kind': 'error', 'text': 'Message exceeds limit'})
                break
            try:
                bridge.handle(json.loads(raw))
            except (ValueError, UnicodeError):
                emit({'kind': 'error', 'text': 'Invalid JSON message'})
    finally:
        bridge.cancel_all()
        for thread in bridge.threads:
            thread.join(timeout=6)


if __name__ == '__main__':
    main()

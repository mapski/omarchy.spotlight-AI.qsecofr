"""Pinned jcode headless Q&A over explicitly selected, loaded LM Studio models.

No native credential import. Each request has a disposable HOME/JCODE_HOME;
MCP, automatic follow-ups, telemetry and update checks are disabled.
"""
import hashlib
import json
import os
import stat
import tempfile
import secrets
import threading
import urllib.request
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from backend.protocol import MAX_BYTES, ResponseEvent
from backend.providers.base import Model, ProviderStatus
from backend.providers.local import LocalAdapter
from backend.runner import stream_process

VERSION = '0.94.0'
BINARY_SHA256 = '8fe2c71d03ff306eb930b09ea13d51f44aeac03a51a648cae65c6b01ede82085'
PROFILE = 'spotlight-local'
MAX_PROMPT_BYTES = 48000  # Linux per-argument bound, including serialized history.


def parse_events(chunks, request):
    pending = b''
    started = finished = False
    answer = ''
    for chunk in chunks:
        pending += chunk
        if len(pending) > MAX_BYTES:
            raise ValueError('jcode output exceeded limit')
        while b'\n' in pending:
            raw, pending = pending.split(b'\n', 1)
            if not raw.strip():
                continue
            event = json.loads(raw)
            if not isinstance(event, dict) or finished:
                raise ValueError('Invalid jcode response')
            kind = event.get('type')
            if kind in {'start', 'done'}:
                if event.get('provider') != PROFILE or event.get('model') != request.model_id:
                    raise ValueError('jcode destination mismatch')
            if kind == 'start':
                if started:
                    raise ValueError('Invalid jcode response')
                started = True
            elif not started:
                raise ValueError('Invalid jcode response')
            elif kind == 'text_delta':
                text = event.get('text')
                if not isinstance(text, str):
                    raise ValueError('Invalid jcode response')
                answer += text
                if len(answer.encode()) > MAX_BYTES:
                    raise ValueError('jcode output exceeded limit')
                yield ResponseEvent(request.request_id, 'delta', text)
            elif kind == 'done':
                if event.get('text') != answer:
                    raise ValueError('jcode final response mismatch')
                finished = True
            elif kind not in {'connection_type', 'connection_phase', 'message_end', 'usage'}:
                # Includes all tool, error, model-switch and text replacement events.
                raise ValueError('jcode returned a non-Q&A response')
    if pending.strip() or not finished:
        raise ValueError('jcode response incomplete')
    # Caller verifies exit status and cancellation before emitting done.


@contextmanager
def fixed_destination(local, model, cancel):
    """jcode's HTTP client follows redirects; terminate them at this boundary.

Only one POST for the selected model is accepted. No redirects, proxies,
provider credentials, model switching or extra calls reach the upstream.
    """
    nonce = '/' + secrets.token_hex(24)
    submitted = False
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass
        def do_POST(self):
            nonlocal submitted
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if submitted or cancel.is_set() or self.path != nonce+'/v1/chat/completions' or not 0 < length <= MAX_BYTES:
                    raise ValueError('Invalid request')
                self.connection.settimeout(5)
                raw = self.rfile.read(length)
                body = json.loads(raw)
                if cancel.is_set() or stopped.is_set() or not isinstance(body, dict) or body.get('model') != model or body.get('tools') or body.get('functions') or body.get('stream') is not True:
                    raise ValueError('Invalid Q&A request')
                submitted = True
                call = urllib.request.Request(local.endpoint+'/v1/chat/completions',raw,{'Content-Type':'application/json'})
                # LocalAdapter's opener explicitly disables redirects and proxies.
                with local.opener.open(call,timeout=5) as response:
                    self.send_response(200)
                    self.send_header('Content-Type','text/event-stream')
                    self.end_headers()
                    total = 0
                    while not cancel.is_set() and not stopped.is_set():
                        data = response.read1(65536)
                        if not data:
                            break
                        total += len(data)
                        if total > MAX_BYTES:
                            break
                        self.wfile.write(data); self.wfile.flush()
            except Exception:
                # Raw upstream diagnostics and Location headers never reach jcode.
                try:
                    self.send_error(400, 'Local request rejected')
                except OSError:
                    pass
    class TimedServer(HTTPServer):
        def get_request(self):
            connection, address = super().get_request()
            connection.settimeout(5)
            return connection, address
    server = TimedServer(('127.0.0.1',0), Handler)
    server.timeout = .1
    stopped = threading.Event()
    def serve():
        while not stopped.is_set():
            server.handle_request()
    worker = threading.Thread(target=serve,daemon=True);worker.start()
    try:
        yield 'http://127.0.0.1:'+str(server.server_port)+nonce+'/v1'
    finally:
        stopped.set()
        server.server_close()
        worker.join(timeout=6)


class JcodeAdapter:
    def __init__(self, executable=None, endpoint='http://127.0.0.1:1234'):
        self.executable = Path(executable) if executable else Path.home()/'.local/share/omarchy-model-search/runtime'/('jcode-'+VERSION+'.bin')
        self.local = LocalAdapter('lmstudio', endpoint)

    def _open_verified(self):
        fd = os.open(self.executable, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode) or info.st_uid not in {0, os.getuid()} or info.st_mode & 0o022 or not info.st_mode & 0o100:
                raise ValueError('Unverified jcode executable')
            with os.fdopen(os.dup(fd), 'rb') as file:
                if hashlib.file_digest(file, 'sha256').hexdigest() != BINARY_SHA256:
                    raise ValueError('Unverified jcode executable')
            return fd
        except BaseException:
            os.close(fd)
            raise

    def discover(self):
        try:
            fd = self._open_verified(); os.close(fd)
        except (OSError, ValueError):
            return ProviderStatus('jcode', False, 'Install the reviewed jcode 0.94.0 runtime; arbitrary CLI versions are not enabled')
        local = self.local.discover()
        return ProviderStatus('jcode', local.available, local.reason,
            tuple(Model(m.id, 'lmstudio', 'local') for m in local.models), streaming=True)

    def stream(self, request, cancel):
        if cancel.is_set():
            return
        status = self.discover()
        if request.route_id != 'jcode' or request.backend_id != 'lmstudio' or not status.available or request.model_id not in {m.id for m in status.models}:
            raise ValueError('Selected jcode backend/model is unavailable')
        if cancel.is_set():
            return
        prompt = 'Answer only the question using the conversation below. Do not use tools. Conversation JSON:\n'+json.dumps([*request.history, {'role':'user','content':request.prompt}],ensure_ascii=False)
        if len(prompt.encode()) > MAX_PROMPT_BYTES:
            raise ValueError('jcode conversation too long; start a new chat')
        fd = self._open_verified()
        try:
            with tempfile.TemporaryDirectory(prefix='model-search-jcode-') as temporary, fixed_destination(self.local, request.model_id, cancel) as endpoint:
                root = Path(temporary); home = root/'jcode'; home.mkdir(mode=0o700)
                config = '[providers."'+PROFILE+'"]\ntype = "openai-compatible"\nauth = "none"\nrequires_api_key = false\nbase_url = '+json.dumps(endpoint)+'\ndefault_model = '+json.dumps(request.model_id)+'\n'
                (home/'config.toml').write_text(config)
                env = {'HOME':temporary,'PATH':'/usr/bin:/bin','JCODE_HOME':str(home),
                    'XDG_CONFIG_HOME':temporary+'/config','XDG_DATA_HOME':temporary+'/data',
                    'XDG_CACHE_HOME':temporary+'/cache','XDG_RUNTIME_DIR':temporary+'/run',
                    'JCODE_NO_TELEMETRY':'1','DO_NOT_TRACK':'1','JCODE_NO_AUTO_UPDATE':'1',
                    'JCODE_NO_MENUBAR':'1','JCODE_RUN_MCP':'0','JCODE_RUN_AUTO_POKE':'0'}
                (root/'run').mkdir(mode=0o700)
                argv = ['/proc/self/fd/'+str(fd), '--no-selfdev', '--tool-profile', 'none',
                    '--provider-profile', PROFILE, '--model', request.model_id, 'run','--ndjson',prompt]
                chunks = stream_process(argv,b'',cancel,cwd=temporary,env=env,pass_fds=(fd,))
                try:
                    yield from parse_events(chunks,request)
                except ValueError:
                    if not cancel.is_set():
                        raise
                finally:
                    chunks.close()
        finally:
            os.close(fd)
        if not cancel.is_set():
            yield ResponseEvent(request.request_id,'done')

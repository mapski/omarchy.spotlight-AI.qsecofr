"""Plugin-owned state with restrictive files and bounded, atomic writes."""
import json
import os
import secrets
import stat
from pathlib import Path
from backend.protocol import ROUTES

MAX_HISTORY = 10 * 1024 * 1024
MAX_TURN = 1024 * 1024


class State:
    def __init__(self, root):
        self.root = Path(root).absolute()
        fd = self._directory()
        os.close(fd)

    def _directory(self):
        fd = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
        try:
            for index, part in enumerate(self.root.parts[1:]):
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = child
            if os.fstat(fd).st_uid != os.geteuid():
                raise PermissionError('State directory belongs to another user')
            os.fchmod(fd, 0o700)
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _read(self, name, default):
        directory = self._directory()
        try:
            try:
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
            except FileNotFoundError:
                return default
            with os.fdopen(fd, 'rb') as file:
                info = os.fstat(file.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_nlink != 1:
                    raise PermissionError('Unsafe state file')
                raw = file.read(MAX_HISTORY + 1)
                if len(raw) > MAX_HISTORY:
                    raise ValueError('State file exceeds limit')
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise ValueError('Invalid state object')
                return value
        finally:
            os.close(directory)

    def _write(self, name, value):
        raw = json.dumps(value, ensure_ascii=False).encode('utf-8')
        if len(raw) > MAX_HISTORY:
            raise ValueError('State exceeds limit')
        directory = self._directory()
        temporary = '.write-' + secrets.token_hex(12)
        try:
            try:
                info = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_nlink != 1:
                    raise PermissionError('Unsafe state destination')
            except FileNotFoundError:
                pass
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory)
            with os.fdopen(fd, 'wb') as file:
                file.write(raw)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, name, src_dir_fd=directory, dst_dir_fd=directory)
            os.fsync(directory)
        finally:
            try:
                os.unlink(temporary, dir_fd=directory)
            except FileNotFoundError:
                pass
            os.close(directory)

    def load_settings(self):
        settings = self._read('settings.json', {'ai_enabled': False, 'roots': []})
        self._validate_settings(settings)
        return settings

    def _validate_settings(self, settings):
        if type(settings.get('ai_enabled', False)) is not bool:
            raise ValueError('Invalid AI opt-in')
        roots = settings.get('roots', [])
        if not isinstance(roots, list) or len(roots) > 32 or any(not isinstance(p, str) or not Path(p).is_absolute() for p in roots):
            raise ValueError('Invalid search roots')
        selection = settings.get('selection', {})
        if not isinstance(selection, dict) or set(selection) - {'route_id', 'model_id', 'backend_id'}:
            raise ValueError('Invalid saved selection')
        if selection:
            if selection.get('route_id') not in ROUTES or not isinstance(selection.get('model_id'), str) or not selection['model_id'].strip():
                raise ValueError('Invalid saved model')
            if any(not isinstance(v, str) or len(v) > 256 or any(ord(c) < 32 for c in v) for v in selection.values()):
                raise ValueError('Invalid saved selection')

    def save_settings(self, settings):
        self._validate_settings(settings)
        self._write('settings.json', settings)

    def history(self):
        return self._read('history.json', {})

    def append_turn(self, conversation_id, turn):
        if not isinstance(conversation_id, str) or not conversation_id or len(conversation_id) > 128:
            raise ValueError('Invalid conversation')
        if not isinstance(turn, dict) or turn.get('role') not in {'user', 'assistant'} or not isinstance(turn.get('text'), str):
            raise ValueError('Invalid turn')
        if len(json.dumps(turn).encode()) > MAX_TURN:
            raise ValueError('Turn exceeds limit')
        history = self.history()
        turns = history.pop(conversation_id, [])
        if not isinstance(turns, list):
            raise ValueError('Invalid history')
        history[conversation_id] = [*turns, turn]
        while len(history) > 25 or len(json.dumps(history, ensure_ascii=False).encode()) > MAX_HISTORY:
            if len(history) > 1:
                del history[next(iter(history))]
            else:
                history[conversation_id].pop(0)
        self._write('history.json', history)

    def clear_history(self):
        self._write('history.json', {})

    def save_exchange(self, request, answer):
        conversation = request.conversation_id or request.request_id
        history = self.history()
        turns = history.pop(conversation, [])
        destination = {'route_id': request.route_id, 'model_id': request.model_id, 'backend_id': request.backend_id}
        history[conversation] = [*turns, dict(destination, role='user', text=request.prompt), dict(destination, role='assistant', text=answer)]
        while len(history) > 25 or len(json.dumps(history, ensure_ascii=False).encode()) > MAX_HISTORY:
            if len(history) > 1:
                del history[next(iter(history))]
            else:
                # Keep complete user/assistant exchanges together.
                del history[conversation][:2]
        self._write('history.json', history)

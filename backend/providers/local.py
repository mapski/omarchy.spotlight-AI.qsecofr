"""Explicit loopback-only HTTP adapters. No service start or model download APIs."""
import ipaddress
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from backend.protocol import MAX_BYTES, ResponseEvent
from backend.providers.base import Model, ProviderStatus


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        raise ValueError('Local endpoint redirects are forbidden')


class LocalAdapter:
    def __init__(self, route_id, endpoint):
        if route_id not in {'ollama', 'lmstudio', 'llamacpp'}:
            raise ValueError('Unknown local route')
        parts = urllib.parse.urlsplit(endpoint)
        host = parts.hostname
        if host == 'localhost':
            host = '127.0.0.1'
        try:
            local = ipaddress.ip_address(host).is_loopback
        except (ValueError, TypeError):
            local = False
        if parts.scheme != 'http' or not local or parts.username or parts.password or parts.query or parts.fragment or parts.path not in {'', '/'}:
            raise ValueError('Use a loopback HTTP server origin')
        port = parts.port or 80
        authority = ('[' + host + ']') if ':' in host else host
        self.endpoint = 'http://' + authority + ':' + str(port)
        self.route_id = route_id
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def _get(self, path):
        with self.opener.open(self.endpoint + path, timeout=5) as response:
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Discovery exceeded limit')
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError('Invalid discovery response')
        return data

    def discover(self):
        try:
            if self.route_id == 'ollama':
                entries = self._get('/api/tags').get('models', [])
                # Query running status without causing loading; callers may display it.
                self.running = self._get('/api/ps').get('models', [])
                selected = [item for item in entries if isinstance(item, dict) and not item.get('remote_host') and not item.get('remote_model') and item.get('details', {}).get('format') == 'gguf' and not item.get('name', '').endswith(':cloud')]
                identifiers = [item.get('name') for item in selected]
            else:
                path = '/api/v0/models' if self.route_id == 'lmstudio' else '/v1/models'
                entries = self._get(path).get('data', [])
                selected = []
                for item in entries:
                    if not isinstance(item, dict):
                        continue
                    if self.route_id == 'lmstudio':
                        loaded = item.get('state') == 'loaded'
                    else:
                        status = item.get('status')
                        loaded = status.get('value') == 'loaded' if isinstance(status, dict) else isinstance(item.get('meta'), dict)
                    if loaded:
                        selected.append(item)
                identifiers = [item.get('id') for item in selected]
            models = tuple(Model(name, locality='local') for name in identifiers if isinstance(name, str) and name)
            return ProviderStatus(self.route_id, bool(models), '' if models else 'No verified local model ready', models, streaming=True)
        except (OSError, ValueError, TypeError, AttributeError):
            return ProviderStatus(self.route_id, False, 'Local server unavailable or model state unverified')

    def stream(self, request, cancel):
        if cancel.is_set():
            yield ResponseEvent(request.request_id, 'cancelled')
            return
        status = self.discover()
        if cancel.is_set():
            yield ResponseEvent(request.request_id, 'cancelled')
            return
        if request.route_id != self.route_id or request.model_id not in {m.id for m in status.models}:
            raise ValueError('Selected model is unavailable')
        payload = {'model': request.model_id, 'messages': [{'role': 'user', 'content': request.prompt}], 'stream': True}
        path = '/api/chat' if self.route_id == 'ollama' else '/v1/chat/completions'
        if self.route_id == 'llamacpp':
            path += '?autoload=false'
        call = urllib.request.Request(self.endpoint + path, json.dumps(payload).encode(), {'Content-Type': 'application/json'})
        deadline = time.monotonic() + 120
        count = 0
        pending = b''
        with self.opener.open(call, timeout=5) as response:
            while True:
                if cancel.is_set():
                    yield ResponseEvent(request.request_id, 'cancelled')
                    return
                if time.monotonic() > deadline:
                    raise TimeoutError('Provider timed out')
                chunk = response.read1(4096)
                if not chunk:
                    break
                count += len(chunk)
                if count > MAX_BYTES:
                    raise ValueError('Provider output exceeded limit')
                pending += chunk
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    line = line.strip()
                    if not line or line.startswith(b':'):
                        continue
                    if self.route_id != 'ollama':
                        if not line.startswith(b'data:'):
                            continue
                        line = line[5:].strip()
                        if line == b'[DONE]':
                            yield ResponseEvent(request.request_id, 'done')
                            return
                    data = json.loads(line)
                    if data.get('error'):
                        raise RuntimeError('Local provider failed')
                    if self.route_id == 'ollama':
                        text = data.get('message', {}).get('content', '')
                        done = data.get('done') is True
                    else:
                        choices = data.get('choices', [])
                        text = choices[0].get('delta', {}).get('content', '') if choices else ''
                        done = False
                    if text and isinstance(text, str) and not cancel.is_set():
                        yield ResponseEvent(request.request_id, 'delta', text)
                    if done:
                        yield ResponseEvent(request.request_id, 'done')
                        return
        raise RuntimeError('Local response ended before completion')

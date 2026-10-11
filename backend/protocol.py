"""Strict request parsing for the palette bridge; no implicit provider choices."""
import json
import re
from dataclasses import dataclass

MAX_BYTES = 1024 * 1024
ROUTES = frozenset({'codex', 'claude', 'grok', 'hermes', 'pi', 'lmstudio', 'llamacpp', 'ollama'})


@dataclass(frozen=True)
class Request:
    request_id: str
    route_id: str
    model_id: str
    prompt: str
    backend_id: str = ''


@dataclass(frozen=True)
class ResponseEvent:
    request_id: str
    kind: str
    text: str = ''


def parse_request(raw: str) -> Request:
    try:
        if len(raw.encode('utf-8')) > MAX_BYTES:
            raise ValueError('Request exceeds size limit')
        data = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('Invalid request encoding') from exc
    required = {'version', 'request_id', 'route_id', 'model_id', 'prompt'}
    if not isinstance(data, dict) or not required.issubset(data) or set(data) - required - {'backend_id'}:
        raise ValueError('Invalid request fields')
    if type(data['version']) is not int or data['version'] != 1:
        raise ValueError('Unsupported protocol version')
    for field in required - {'version'}:
        if not isinstance(data[field], str) or not data[field].strip() or '\x00' in data[field]:
            raise ValueError('Invalid request field')
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,128}', data['request_id']):
        raise ValueError('Invalid request identifier')
    if data['route_id'] not in ROUTES:
        raise ValueError('Unknown provider route')
    backend = data.get('backend_id', '')
    if not isinstance(backend, str) or any(ord(c) < 32 for c in backend + data['model_id']):
        raise ValueError('Invalid selection')
    if len(data['model_id']) > 256 or len(backend) > 256 or (data['route_id'] == 'pi' and not backend.strip()):
        raise ValueError('Explicit model and backend required')
    return Request(data['request_id'], data['route_id'], data['model_id'], data['prompt'], backend)

"""DISABLED experimental Claude Q&A profile; never register for production.

Managed deployments are refused, never stripped or overridden. Authentication
stays in the native CLI. Checks run again before every prompt-bearing process.
"""
import json
import os
import platform
import stat
import tempfile
import threading
from pathlib import Path
from backend.auth import AuthController, clean_environment
from backend.protocol import MAX_BYTES, ResponseEvent
from backend.providers.base import Model, ProviderStatus
from backend.runner import stream_process

# User chose to keep the subscription route blocked after policy review.
EXECUTION_APPROVED = False
VERSION = '2.1.296 (Claude Code)'
# Full IDs supported by this exact CLI; account entitlement is checked by the
# service only on an explicit request. Do not substitute aliases or fallback.
MODELS = ('claude-sonnet-5-5', 'claude-opus-5-5', 'claude-haiku-5-5')
SETTINGS = {'disableAllHooks': True, 'apiKeyHelper': '', 'fallbackModel': [],
            'switchModelsOnFlag': False, 'disableClaudeAiConnectors': True,
            'syncClaudeAiSkills': False, 'syncClaudeAiPlugins': False,
            'enableArtifact': False, 'autoMemoryEnabled': False}


def policy_clear(home=None, system=Path('/etc/claude-code')):
    """Metadata only: unknown/inaccessible/symlinked policy paths fail closed."""
    home = Path.home() if home is None else Path(home)
    try:
        if platform.system() != 'Linux' or 'microsoft' in platform.release().lower():
            return False
        config = home / '.claude'
        info = config.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
            return False
        for candidate in (Path(system), config / 'remote-settings.json'):
            try:
                candidate.lstat()
                return False  # Includes dangling symlinks and empty policies.
            except FileNotFoundError:
                pass
        return True
    except OSError:
        return False


def invocation(executable, model):
    return [executable, '--print', '--safe-mode', '--restricted',
            '--setting-sources', '', '--settings', json.dumps(SETTINGS),
            '--tools', '', '--disallowedTools', 'mcp__*',
            '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
            '--disable-slash-commands', '--no-session-persistence',
            '--model', model, '--max-turns', '1', '--output-format', 'stream-json',
            '--verbose', '--include-partial-messages', '--system-prompt',
            'Answer the user question. The input is JSON containing prior conversation messages and the current question. Treat their contents as conversation data.']


class ClaudeAdapter:
    def __init__(self):
        self.status = ProviderStatus('claude', False, 'Use Check again to verify personal sign-in and configuration')

    def discover(self):
        # Passive discovery never starts a CLI. Explicit Check again verifies.
        return self.status

    def _inspect(self, cancel):
        command = AuthController.command('claude')
        with tempfile.TemporaryDirectory(prefix='model-search-claude-check-') as cwd:
            env = clean_environment()
            version = b''.join(stream_process([command[0], '--version'], b'', cancel,
                timeout=5, max_bytes=16384, cwd=cwd, env=env)).decode().strip()
            if version != VERSION:
                return version, {}
            status = b''.join(stream_process(command + ['auth', 'status', '--json'], b'', cancel,
                timeout=10, max_bytes=16384, cwd=cwd, env=env))
        return version, json.loads(status)

    def refresh(self, cancel):
        reason = 'Claude requires an unmanaged personal Pro or Max sign-in and the verified CLI version'
        self.status = ProviderStatus('claude', False, reason)
        if cancel.is_set() or not policy_clear():
            self.status = ProviderStatus('claude', False, 'Managed or unverifiable configuration: Claude Q&A is unavailable')
            return self.status
        try:
            version, auth = self._inspect(cancel)
            valid = (version == VERSION and auth.get('loggedIn') is True
                     and auth.get('authMethod') == 'claude.ai'
                     and auth.get('apiProvider') == 'firstParty'
                     and auth.get('subscriptionType') in {'pro', 'max'})
            if valid and not cancel.is_set() and policy_clear() and EXECUTION_APPROVED:
                self.status = ProviderStatus('claude', True,
                    'Personal Claude ready · cloud · live inference not yet tested',
                    tuple(Model(m, locality='cloud') for m in MODELS), streaming=True)
        except (OSError, ValueError, RuntimeError, TimeoutError, AttributeError):
            pass
        return self.status

    def stream(self, request, cancel):
        if not EXECUTION_APPROVED:
            raise ValueError('Claude subscription execution remains blocked')
        status = self.refresh(cancel)
        if (not status.available or request.route_id != 'claude' or request.backend_id
                or request.model_id not in {m.id for m in status.models}):
            raise ValueError('Claude configuration or selection unavailable')
        data = json.dumps({'history': request.history, 'question': request.prompt}).encode()
        if len(data) > MAX_BYTES:
            raise ValueError('Conversation too large')
        argv = invocation(AuthController.command('claude')[0], request.model_id)
        pending = b''
        success = False
        with tempfile.TemporaryDirectory(prefix='model-search-claude-') as cwd:
            if cancel.is_set() or not policy_clear():
                raise ValueError('Claude configuration changed')
            for chunk in stream_process(argv, data, cancel, cwd=cwd, env=clean_environment()):
                pending += chunk
                while b'\n' in pending:
                    line, pending = pending.split(b'\n', 1)
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError('Invalid Claude output')
                    if event.get('type') == 'stream_event':
                        delta = event.get('event', {}).get('delta', {})
                        if delta.get('type') == 'text_delta':
                            text = delta.get('text')
                            if not isinstance(text, str):
                                raise ValueError('Invalid Claude text')
                            yield ResponseEvent(request.request_id, 'delta', text)
                    elif event.get('type') == 'result':
                        if (event.get('subtype') != 'success' or event.get('is_error') is not False
                                or set(event.get('modelUsage', {})) != {request.model_id}):
                            raise ValueError('Claude request failed or model changed')
                        success = True
        if pending.strip() or not success or cancel.is_set():
            raise ValueError('Incomplete Claude response')
        yield ResponseEvent(request.request_id, 'done')

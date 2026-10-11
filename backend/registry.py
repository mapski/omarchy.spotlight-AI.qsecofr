"""Independent route discovery; unverified CLI execution remains disabled."""
import shutil
from backend.providers.base import ProviderStatus
from backend.providers.local import LocalAdapter

# Installed-version review: see docs/providers.md. Presence is never readiness.
CLI_BLOCKERS = {
    'codex': 'Disabled: exec sandbox still permits commands; complete no-tools isolation unverified',
    'claude': 'Disabled: mock no-tools checks passed; existing sign-in and managed-policy isolation pending',
    'grok': 'Disabled: tool allowlist found; extension, context and session suppression unverified',
    'hermes': 'Disabled: safe-mode found; no-tools, fallback and transcript suppression unverified',
    'pi': 'Disabled: mock tool isolation passed; credential commands still execute; isolated auth design required',
}

class Registry:
    def __init__(self):
        self.adapters = {
            'lmstudio': LocalAdapter('lmstudio', 'http://127.0.0.1:1234'),
            'llamacpp': LocalAdapter('llamacpp', 'http://127.0.0.1:8080'),
            'ollama': LocalAdapter('ollama', 'http://127.0.0.1:11434'),
        }

    def discover(self):
        statuses = []
        for name in ('codex', 'claude', 'grok', 'hermes', 'pi'):
            found = shutil.which(name)
            reason = CLI_BLOCKERS[name] if found else 'CLI not installed'
            statuses.append(ProviderStatus(name, False, reason))
        for adapter in self.adapters.values():
            statuses.append(adapter.discover())
        return statuses

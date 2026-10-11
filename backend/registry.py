"""Independent route discovery; unverified CLI execution remains disabled."""
import shutil
from backend.providers.base import ProviderStatus
from backend.providers.local import LocalAdapter


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
            reason = 'Q&A isolation verification pending' if found else 'CLI not installed'
            statuses.append(ProviderStatus(name, False, reason))
        for adapter in self.adapters.values():
            statuses.append(adapter.discover())
        return statuses

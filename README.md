# Omarchy Model Search

Private development prototype of a keyboard-first Omarchy search palette with optional, explicitly selected AI Q&A. The full product is not release-ready.

Local application search, editable file-root settings, saved model selections, recent conversations with destination-bound follow-up, temporary questions, bounded private history, and offline adapters for LM Studio, llama.cpp and Ollama are implemented. Codex, Claude, Grok, Hermes and Pi are detected independently but remain disabled pending Q&A isolation verification. Live local inference tests are deferred at the user's request.

See [validation](docs/VALIDATION.md), [provider readiness](docs/providers.md), [dependencies](docs/dependencies.md), [environment evidence](docs/environment.md), and the [approved architecture](ARCHITECTURE.md).

Development uses the official VM333 clone ID mp.emojis. It is enabled only on the authorized lab VM. Do not install on the daily desktop without explicit authorization. Use official Omarchy plugin commands; never launch a second Quickshell process.

Run offline checks from this directory:

    python -m unittest discover -s tests -v
    omarchy plugin validate .

The canonical repository remains private until explicit 1.0 public-release approval. No push or public release has occurred.

On VM333, press **Super+Ctrl+M**. Settings edits search folders; Recent reopens saved conversations. AI remains opt-in. An unavailable saved model stays disabled until discovery verifies it.

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

### Claude and Codex sign-in

The Claude control opens its native sign-in and remains separate from execution readiness. The blocked Codex CLI entry now offers **Connect ChatGPT Q&A**, which selects the app’s direct ChatGPT connection; it no longer opens a native Codex login. CLI credentials are never collected by the plugin. Sign-in status and inference readiness are separate: both CLI inference routes remain disabled while the configuration/tool-isolation gaps in [provider readiness](docs/providers.md) are resolved. Live inference tests remain pending.


### Direct ChatGPT connection

On the authorized lab VM, press **Super+Ctrl+M**, enable AI, then click the prominent **Continue with ChatGPT** button. The provider is labeled **ChatGPT · Direct Q&A**; **Codex CLI · Blocked** is a separate unavailable route. Complete consent in your browser. Reopen the palette and refresh providers, then explicitly choose a model. This separate route uses your ChatGPT plan through the documented public API; it does not run Codex CLI. Eligibility and actual sign-in remain to be verified by the user. Live inference tests remain pending.

**Add account** creates another registration; the account picker distinguishes registrations even with the same email. **Cancel sign-in** stops a pending attempt. **Sign out** revokes the refresh token when possible and clears local tokens; a revocation failure is reported so you can disconnect the app in ChatGPT Settings. Tokens are stored separately from history under `~/.local/state/omarchy-model-search/chatgpt-auth` (or XDG_STATE_HOME). Clear history does not sign you out. Plugin removal preserves state: sign out first if disconnecting, and remove the state directory yourself only if you also want to erase saved settings/history/registration identities.

Install `python-pyjwt` and `python-cryptography` using the supported Omarchy package workflow on an authorized machine. For isolated development environments, use `requirements.txt`. Credentials remain backend-only in owner-restricted files; this is not encrypted storage or protection against another process running as your user. Claude and Codex CLI execution remain blocked.

The browser confirms **ChatGPT account saved successfully** only after validation and persistence. If sign-in fails, the app retains a safe stage name (listener, registration storage, browser, token exchange, identity, permissions or credential storage) across palette reopenings; it never stores raw OAuth errors, callback URLs or tokens in diagnostics.

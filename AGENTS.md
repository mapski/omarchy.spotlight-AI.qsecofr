# Project instructions

Start each new session by reading [`handoff.d/START-HERE.md`](handoff.d/START-HERE.md), then [`handoff.d/HANDOFF.md`](handoff.d/HANDOFF.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md). Treat the handoff as a dated snapshot; verify live repository and workstation state before acting.

The mandatory Omarchy development and publishing gates in `ARCHITECTURE.md` apply to all implementation and release work. Re-read the current official guides before each relevant phase. Never skip validation, lifecycle tests, security review, user-visible documentation, or license checks. Keep the canonical GitHub repo private until the user explicitly approves the 1.0 public release. Do not push until authenticated access confirms the exact remote, its visibility, and its history.

Do not store passwords, API keys, OAuth tokens, browser sessions, or private test prompts in this repository or its logs. The user handles interactive account authorization. Do not install or enable the plugin on the user's daily Omarchy environment without explicit authorization and the workstation's required before/after documentation.

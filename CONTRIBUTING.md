# Contributing

Read AGENTS.md, handoff.d/START-HERE.md and ARCHITECTURE.md first. The active implementation is a preview candidate; do not make mirrors or publish code/assets without owner approval.

Keep changes focused on the current priority: direct ChatGPT first, then minimal local footprint. jcode follows Codex in the picker. Claude stays blocked. Colibri is a priority evaluation, not an approved runtime/model download. Ask the owner before any additional download.

Use an authorized lab desktop, a user-owned official overlay clone and the generated clone ID. Never edit packaged `/usr/share/omarchy` files or launch a second Quickshell.

## Verify

1. Run `python -m unittest discover -s tests -v` with Node present; report skips/failures.
2. Run `omarchy plugin validate` on the exact plugin directory.
3. Run `qmllint` with installed Omarchy shell imports for Overlay.qml and ui/Answer.qml.
4. Exercise relevant keyboard, provider-error, cancellation, disable/enable, restart and removal/restoration flows. Review the actual UI.
5. For jcode changes run `python tests/manual/jcode_isolation.py /path/to/reviewed/jcode.bin`. This uses synthetic loopback responses, not a real model.
6. Review security boundaries, dependencies and licenses; update user-facing docs and dated validation evidence.

Keep real inference deferred until the owner changes that instruction. Never store secrets or private prompts in fixtures, screenshots or logs. Screenshots must be actual captures, with demo states clearly identified.

Before a push, confirm exact remote identity, private visibility and existing history. No force-push or public visibility change without explicit authorization. Public 1.0 still needs the outstanding release gates and owner approval.

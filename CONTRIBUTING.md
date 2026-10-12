# Contributing

Read ARCHITECTURE.md first. Open an issue before large changes.

Keep changes focused on the current priority: direct ChatGPT first, then minimal local footprint. jcode follows Codex in the picker. Claude stays blocked. Colibri is a priority evaluation, not an approved runtime/model download. Ask the owner before any additional download.

Use a test desktop (not your daily environment), a user-owned official overlay clone and the generated clone ID. Never edit packaged `/usr/share/omarchy` files or launch a second Quickshell.

## Verify

1. Run `python -m unittest discover -s tests -v` with Node present; report skips/failures.
2. Run `omarchy plugin validate` on the exact plugin directory.
3. Run `qmllint` with installed Omarchy shell imports for Overlay.qml and ui/Answer.qml.
4. Exercise relevant keyboard, provider-error, cancellation, disable/enable, restart and removal/restoration flows. Review the actual UI.
5. For jcode changes run `python tests/manual/jcode_isolation.py /path/to/reviewed/jcode.bin`. This uses synthetic loopback responses, not a real model.
6. Review security boundaries, dependencies and licenses; update user-facing docs and dated validation evidence.

The owner authorized real direct ChatGPT and LM Studio tests for rc.2. Record their actual scope and preserve temporary-question/state controls; do not broaden that authorization to blocked CLI execution. Never store secrets or private prompts in fixtures, screenshots or logs. Screenshots must be actual captures, with demo states clearly identified.

Before a push, confirm exact remote identity, approved visibility and existing history. No force-push or public visibility change without explicit authorization. Public 1.0 still needs the outstanding release gates and owner approval.

# Development validation — 2026-10-11

This is a private development prototype, not a release candidate.

## Offline adapters completed

LM Studio and llama.cpp offer only models reported loaded. Ollama offers installed models with local GGUF metadata and rejects cloud/unknown locality. Requests use loopback endpoints, disable proxies/redirects, require explicit model selection and AI opt-in, and bound streaming output. llama.cpp requests disable automatic model loading. Explicit Ollama queries may load an installed model; no downloads are implemented.

31 tests pass using synthetic inputs and local mock HTTP servers: protocol validation, model discovery/routing, cancellation, subprocess limits, local search isolation, state permissions/bounds, bridge failure handling and presentation regressions. These tests do not prove compatibility with live provider versions.

Run: python -m unittest discover -s tests -v
Manifest: omarchy plugin validate .
QML: qmllint with a temporary qs import pointing at the installed shell; see environment.md for warnings.

Initial independent code review findings were fixed and regression tested: cancellation during discovery must not submit the prompt; stale AI answers must not hide local search; Markdown must not silently truncate valid answers at 20,000 characters. A corrupt-settings error-handler crash was also reproduced and fixed.

## Remaining gates

- Live LM Studio, llama.cpp and Ollama inference: pending at user's request.
- CLI adapters, including Pi backend selection: registry entries exist, execution disabled pending verified Q&A isolation.
- Initial full-source static security review completed; its one medium rendering-amplification finding was fixed with failing-then-passing regressions. This is not release certification; final release license audit remains pending.
- Summon/hide, Escape clear/close, disable/re-enable, restart and removal/restoration passed on VM333. Existing emoji shortcut did not summon the clone in the automated check; shortcut, scale/theme and streaming UI acceptance remain pending.
- Conversation reopening/follow-up, provider selection persistence and settings UI: incomplete.

The prototype is not the completed eight-provider product. No release or push is authorized by these results.

## Prototype usage and data

On the lab VM only, mp.emojis replaces the cloned emoji overlay while enabled. Local typing searches applications and explicitly configured roots. AI requires Enable AI, an explicit provider/model, and an ai: query submitted with Enter. Web search requires the Web search action. Never enter secrets into test prompts.

State resides in ~/.local/state/omarchy-model-search by default, or under XDG_STATE_HOME. AI defaults off; history is bounded to 25 conversations/10 MiB and files use restrictive permissions. Clear history cancels active work before clearing saved conversations. Plugin removal does not imply deletion of saved user state. Configured roots currently require editing the plugin settings JSON; no whole-home indexing occurs by default.

## Continuation results

Provider discovery now runs asynchronously, rejects duplicate refreshes, sanitizes errors and permits retry. Tests demonstrate local search is processed during discovery.

Security scan 8a367b7c-2002-4e5b-a90f-354f655f376a reviewed all 32 then-current files. Its archived report describes the pre-fix snapshot. Table rendering now checks row/column/width and expansion limits before allocating; answers above 512 lines use one plain-text block. Two safe synthetic regressions failed before the change and pass afterward.

No extra dependencies were needed: Python, Node, Qt tools, gio, wl-copy, grim and wtype execute on the VM. Official removal created its own standard plugin backup and restored builtin emojis; the approved snapshot policy was not replaced with another custom backup mechanism. Clone was recreated with the official workflow and updated build enabled.

# Development validation — 2026-10-11

This is a private development prototype, not a release candidate.

## Offline adapters completed

LM Studio and llama.cpp offer only models reported loaded. Ollama offers installed models with local GGUF metadata and rejects cloud/unknown locality. Requests use loopback endpoints, disable proxies/redirects, require explicit model selection and AI opt-in, and bound streaming output. llama.cpp requests disable automatic model loading. Explicit Ollama queries may load an installed model; no downloads are implemented.

35 tests pass using synthetic inputs and local mock HTTP servers: protocol validation, model discovery/routing, cancellation, subprocess limits, local search isolation, state permissions/bounds, bridge failure handling and presentation regressions. These tests do not prove compatibility with live provider versions.

Run: python -m unittest discover -s tests -v
Manifest: omarchy plugin validate .
QML: qmllint with a temporary qs import pointing at the installed shell; see environment.md for warnings.

Initial independent code review findings were fixed and regression tested: cancellation during discovery must not submit the prompt; stale AI answers must not hide local search; Markdown must not silently truncate valid answers at 20,000 characters. A corrupt-settings error-handler crash was also reproduced and fixed.

## Remaining gates

- Live LM Studio, llama.cpp and Ollama inference: pending at user's request.
- CLI adapters, including Pi backend selection: registry entries exist, execution disabled pending verified Q&A isolation.
- Initial full-source static security review completed; its one medium rendering-amplification finding was fixed with failing-then-passing regressions. This is not release certification; final release license audit remains pending.
- Summon/hide, Escape clear/close, disable/re-enable, restart and removal/restoration passed on VM333. Dedicated Super+Ctrl+M shortcut verified using VM hardware key injection. Current dark theme, light theme, and effective 100%, 125% and 160% scales checked; live streaming and IME composition acceptance remain pending.
- Conversation reopening and destination-bound follow-up, saved selection, search-root settings and temporary single questions: implemented and tested. Temporary questions deliberately have no follow-up context.

The prototype is not the completed eight-provider product. No release or push is authorized by these results.

## Prototype usage and data

On the lab VM only, mp.emojis replaces the cloned emoji overlay while enabled. Local typing searches applications and explicitly configured roots. AI requires Enable AI, an explicit provider/model, and an ai: query submitted with Enter. Web search requires the Web search action. Never enter secrets into test prompts.

State resides in ~/.local/state/omarchy-model-search by default, or under XDG_STATE_HOME. AI defaults off; history is bounded to 25 conversations/10 MiB and files use restrictive permissions. Clear history cancels active work before clearing saved conversations. Plugin removal does not imply deletion of saved user state. Settings edits up to 32 absolute search roots; no whole-home indexing occurs by default.

## Continuation results

Provider discovery now runs asynchronously, rejects duplicate refreshes, sanitizes errors and permits retry. Tests demonstrate local search is processed during discovery.

Security scan 8a367b7c-2002-4e5b-a90f-354f655f376a reviewed all 32 then-current files. Its archived report describes the pre-fix snapshot. Table rendering now checks row/column/width and expansion limits before allocating; answers above 512 lines use one plain-text block. Two safe synthetic regressions failed before the change and pass afterward.

No extra dependencies were needed: Python, Node, Qt tools, gio, wl-copy, grim and wtype execute on the VM. Official removal created its own standard plugin backup and restored builtin emojis; the approved snapshot policy was not replaced with another custom backup mechanism. Clone was recreated with the official workflow and updated build enabled.

## UI and CLI continuation

35 tests pass, including new settings, fail-closed CLI discovery, follow-up destination binding, temporary non-persistence and unique conversation IDs across restarts. Independent review identified the restart ID collision; its regression failed before UUID-based conversation allocation and passed afterward.

VM snapshot model-search-preui-20261011 precedes the changes. Added a conflict-free Super+Ctrl+M binding to mp.emojis in the VM user's bindings.lua. Hyprland reload/configerrors passed. QEMU hardware keyboard injection opens the palette; Wayland wtype modifiers did not reliably exercise compositor shortcuts. Original emoji binding was not overwritten.

Keyboard opened Settings and saved a synthetic folder; readback matched, and its file appeared in actual local results. Recent opened a synthetic saved conversation via keyboard and showed its original unavailable destination without substituting a model. Popup focus, Escape hierarchy, compact local mode, formatted answer view and light/dark contrast checked. Scale request 150% rounded to effective 160%; actual scale was read back. Original Ethereal theme and 100% scale restored. Synthetic history/file/root data removed.

CLI verification uses local mock HTTP fixtures only, detailed in providers.md. Pi and Claude passed tool/context/session fixture checks with isolated temporary configuration. Pi credential commands remain executable; Claude bare-mode auth differs from existing sign-in. All CLI routes remain unavailable with specific reasons. Live inference is still pending by explicit user instruction.

QML lint exits zero with installed metadata/dynamic-theme warnings. Runtime exposed and fixed a reserved QML method name and Recent keyboard focus issue that lint alone did not catch. Final release still requires live-provider acceptance, IME composition, final packaging/license review and explicit public-release approval.

## Native authentication continuation — 2026-10-11

42 unit tests pass. New checks cover fixed login argv, invalid routes, secret/endpoint/helper environment exclusion, native mise resolution, sanitized auth status, explicit subprocess cwd/env, and cancellation of background auth checks. Fresh review found uncancelled status children and exclusive palette focus after launching login; both corrected. Manifest and QML validation pass on VM333. Non-bare Claude fixture passes; Codex fixture reports remaining request_user_input; managed Claude fixture reproduces hook/helper execution. These are not enabled inference adapters or live model tests. No new runtime dependency, license change, push, public release, or daily-desktop installation.

VM GUI verification: selected Claude using the keyboard; Sign in opened the native authorization browser (active window class firefox) and removed the palette layer, confirming focus handoff. Browser contents/authorization codes were not inspected. Completion remains user-controlled. The same managed-policy fixture running auth status made zero HTTP fixture requests and executed neither hook nor credential helper; this does not erase the demonstrated inference-path failure.

## Disabled Claude candidate — 2026-10-11

50 tests pass, including the explicit execution block and rejection of unknown versions before native auth status. Installed-CLI loopback fixtures passed ordinary text, hostile tool response, and HTTP error with no prompt persistence or tools/hooks/helpers. The candidate's native Pro status preflight passed on VM333 but does not establish same-process credential/policy identity. Fresh review identified that remaining gap and the executable-binding gap. Activation was rejected by automatic approval review; user chose to retain the blocked subscription route. Registry and QML were not changed. No live inference, API-key route, public push, license/dependency changes or daily-desktop install.

## Codex continuation — 2026-10-11

Corrected tests/manual/codex_isolation.py to inventory additional_tools input items and namespaces, select a real bundled model by default, and offer --require-no-tools. VM333 Codex 0.162.1: disabling the synchronous question tool makes the unknown synthetic profile empty, but gpt-6.1-sol still exposes code-mode/async/collaboration tools and gpt-5.5 exposes apply_patch. Both real-model strict gates fail as expected. One loopback mock request per run, no context sentinel, no JSONL sessions or literal prompt in temporary HOME files. Codex remains disabled; Claude remains blocked by user decision; live inference pending. See docs/providers.md for scope and next checks. No production/runtime changes, deployment or push in this continuation.

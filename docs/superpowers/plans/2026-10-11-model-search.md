# Omarchy Model Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Build a keyboard-first local search palette with explicit, optional Q&A through eight independently detected routes.

**Architecture:** Adapt licensed omaSearch presentation and bounded Python process handling to the installed Omarchy overlay contract. Separate local search, explicit web actions, provider discovery, request execution, and private history. Every request retains its selected route and model for its lifetime.

**Tech Stack:** QML/Quickshell, Python 3 standard library, provider CLIs, loopback HTTP, Python unittest; installed Omarchy tools for validation and lifecycle tests.

**Spec:** [ARCHITECTURE.md](../../../ARCHITECTURE.md), approved 2026-10-11 including llama.cpp, Ollama, and Pi.

**Status:** Proposed plan awaiting review and execution-method selection. No implementation, clone, installation, or release authorized by this document alone.

## Global Constraints

- “Keep AI opt-in in settings and mark the selected destination clearly before a query is submitted.”
- “There is no automatic cross-provider fallback.”
- “No filesystem write, shell command, agent tool, or desktop control is exposed through the AI palette.”
- “Do not install or enable the plugin on the user's daily environment without explicit authorization and the required before/after documentation.”
- “Keep the canonical repository private until the user explicitly approves the 1.0 public release.”
- Preserve all applicable upstream licenses, including omaSearch attribution; Spotlight remains a visual reference.
- Read the current official guides again before implementation, validation, and publishing. Missing evidence blocks its dependent step.
- Route IDs: `codex`, `claude`, `grok`, `hermes`, `pi`, `lmstudio`, `llamacpp`, `ollama`.
- Services and model downloads are user-managed. Only an explicit Ollama request may load an already installed local model.
- No credentials, account stores, private prompts, or provider transcripts enter the repository or test logs.

## Review Focus

- A cancelled request emits late output after another starts: discard events with an obsolete request ID (Task 3).
- A loopback server redirects or proxies to cloud: block redirects and require evidence of local inference, including Ollama model classification (Task 4).
- A CLI loads extensions or workspace instructions before answering: isolate context and reject adapters lacking enforceable Q&A restrictions (Task 5).
- History paths are symlinks or interrupted writes leave partial files: fail safely and use atomic, restrictive storage (Task 6).
- IME composition, long answers, and display scaling interfere with Enter/focus: test on the actual supported desktop before shipping (Task 7).

## Evidence and decisions requiring execution-time verification

Read-only checks on 2026-10-11 found Omarchy `4.0.4-1`, shell files under `/usr/share/omarchy/shell`, and `/usr/lib/qt6/bin/qmllint` (not on PATH). Installed provider capabilities have not been verified. Do not infer them from current web documentation.

GitHub sign-in and Git transport succeeded as `mapski`; the canonical repository was private with default branch `main`. Remote root `17aa400` differs from local commits `166a064` and `38fb53c`. Refresh these facts before reconciliation or push.

The development guide's clone operation enables the copy immediately. Task 1 must establish an authorized test desktop and documented baseline before cloning. Never run it on the daily desktop on the assumption that cloning is passive.

The current omaSearch README and `ask.py` include tool execution, provider-session imports, and auxiliary title generation. These features must be removed or replaced; upstream “safe mode” does not meet this spec's no-tools guarantee.

Plan-level defaults proposed for approval: local application search plus explicitly configured file roots; no whole-home indexing. History is capped at 25 conversations and 10 MiB total, with a 1 MiB request/output bound, a 120-second request deadline, and a 5-second discovery timeout. Keep these configurable within documented hard bounds. Rich cards and image input are deferred; formatted text and code are the initial answer surface.

## File map

The plugin distribution lives at the repository root so the final root manifest is publishable. Clone-generated identity is recorded verbatim, never invented.

- `manifest.json`, `Overlay.qml`: installed overlay contract and shell lifecycle.
- `ui/SearchInput.qml`, `ui/Results.qml`, `ui/Answer.qml`, `ui/ProviderPicker.qml`: focused UI components.
- `backend/main.py`, `backend/protocol.py`: newline-delimited JSON bridge and typed messages.
- `backend/search.py`, `backend/registry.py`, `backend/runner.py`, `backend/state.py`: search, discovery, execution, private persistence.
- `backend/providers/base.py`, `local.py`, `codex.py`, `claude.py`, `grok.py`, `hermes.py`, `pi.py`: adapter interface and implementations.
- `tests/test_search.py`, `test_protocol.py`, `test_runner.py`, `test_local.py`, `test_cli.py`, `test_state.py`, `test_package.py` under `tests/`: offline contract and regression tests with synthetic data.
- `docs/environment.md`, `upstream.md`, `providers.md`, `validation.md`, `security-review.md`, `release.md` under `docs/`: evidence, provenance, operating instructions, and gates.
- `README.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, `SECURITY.md`, `CHANGELOG.md`: user and release documentation.

## Task 1: Establish a reproducible, authorized development baseline

**Files:** `docs/environment.md`, `docs/upstream.md`, `LICENSE`, `THIRD_PARTY_NOTICES.md`, root manifest and overlay copied from the authorized clone.

**Interfaces:** Produces recorded clone ID, overlay entry-point contract, source revisions and license inventory consumed by all later tasks.

- [ ] Refresh Git status, authenticated identity, privacy, remote refs and history. Inspect remote contents before reconciling unrelated roots; preserve both histories with a reviewed merge, without force-push. Stop on unexpected remote content. Push only after the complete resulting diff is reviewed and access gates pass.
- [ ] Read current Omarchy guides, linked shell references and installed overlay examples. Record shell/Qt/provider versions and exact supported commands without credential output.
- [ ] Prepare an isolated test desktop or obtain explicit daily-desktop authorization with before/after documentation. Until then, continue only offline work that does not depend on a clone.
- [ ] Choose the closest installed overlay/search example; run the official clone workflow there. Record the exact generated ID and preserve clone-origin metadata. Document a file-copy workflow between canonical source and the development directory; no plugin symlinks.
- [ ] Pin and inspect omaSearch source and transitive attribution. Retain required notices and record reused files and upstream revision. Do not run its installer or import its agent execution defaults.
- [ ] Validate the unmodified clone and lint its actual QML entry points using installed imports. Record exit status; commit reviewed baseline files only after these checks pass.

## Task 2: Local search and explicit mode routing

**Files:** `backend/search.py`, `backend/protocol.py`, `tests/test_search.py`, `tests/test_protocol.py`.

**Interfaces:** `classify_query(text: str, explicit_mode: str) -> str` returns `local`, `web`, or `ai`; `search(query: str, roots: list[str]) -> list[SearchResult]`. `SearchResult` carries `id`, `label`, `kind`, and an explicit activation target. AI requests require `request_id`, `route_id`, `model_id`, `prompt`; Pi additionally requires `backend_id`.

- [ ] Write failing tests: ordinary input yields local results with zero provider calls; `ai:` selects AI only; web activation requires an explicit action; Unicode, empty input, inaccessible roots and shell metacharacters remain data.
- [ ] Run `python -m unittest discover -s tests -p 'test_search.py' -v`; confirm assertions fail before implementation.
- [ ] Implement application search and configured-root file search with bounded results and deterministic ranking. Use platform activation APIs or argument arrays, never shell interpolation.
- [ ] Define versioned JSON input/event validation; reject malformed messages, oversized prompts, missing selections and unknown modes before spawning anything.
- [ ] Run both test modules, inspect the diff, and commit the local-only vertical slice.

## Task 3: Request lifecycle and provider registry

**Files:** `backend/registry.py`, `backend/runner.py`, `backend/providers/base.py`, `tests/test_runner.py`.

**Interfaces:** `Adapter.discover() -> ProviderStatus`; `Adapter.stream(request: Request, cancel: Event) -> Iterator[ResponseEvent]`. Status includes availability/reason, verified models and capabilities. Events carry `request_id`, `kind` (`delta`, `done`, `error`, `cancelled`), and bounded text. `Runner.start(request)` and `Runner.cancel(request_id)` own process cleanup.

- [ ] Add failing fake-adapter tests for unavailable routes, expired model selections, immutable selection during a stream, timeout, oversized output, child descendants, late output, and exactly one terminal event.
- [ ] Run `python -m unittest discover -s tests -p 'test_runner.py' -v` and confirm failures.
- [ ] Implement independent discovery, bounded streaming, process-group cancellation and sanitized errors. Never retry against another route; refresh failures disable stale choices.
- [ ] Run tests and verify no child survives cancellation or timeout; review and commit.

## Task 4: Local server adapters

**Files:** `backend/providers/local.py`, `tests/test_local.py`, `docs/providers.md`.

**Interfaces:** `LocalAdapter` implements Task 3's contract for `lmstudio`, `llamacpp`, `ollama`; configuration provides a loopback endpoint and selected model ID.

- [ ] Write failing mock-server tests for model discovery, partial streaming frames, invalid JSON, refused connections, non-loopback destinations, redirects and cloud-backed Ollama choices. Assert discovery causes no loading and never starts a service or downloads a model.
- [ ] Run `python -m unittest discover -s tests -p 'test_local.py' -v` and confirm failures.
- [ ] Implement LM Studio/llama.cpp model and chat APIs, requiring verified loaded models; implement Ollama installed/running discovery and local chat. Treat unknown locality as unavailable. Disable proxies and redirects for local requests.
- [ ] Test that an explicit Ollama query may load its selected installed model; other discovery paths remain passive. Document supported versions and how locality is verified rather than inferred from loopback alone.
- [ ] Run mock tests, then synthetic live checks on user-prepared servers. Record unavailable live tests as blocked, not passed; review and commit offline adapter work independently.

## Task 5: CLI adapters with enforceable Q&A boundaries

**Files:** six CLI-related files listed in the file map (base plus five route files), `tests/test_cli.py`, `docs/providers.md`.

**Interfaces:** Each adapter implements Task 3's contract; Pi status/model identity includes the underlying backend and locality. Manual model selection is permitted only when documented and verified by the selected CLI.

- [ ] For each CLI, inspect its installed version and supported official documentation. Record exact invocation/model discovery, auth reuse, no-tools controls, extension suppression, context isolation and session persistence behavior. Do not invent flags.
- [ ] Write failing fake-executable tests asserting exact argument arrays, stdin prompt transport, explicit model/backend selection, no shell invocation, missing auth errors and disabled status when required safety controls are unsupported.
- [ ] Run `python -m unittest discover -s tests -p 'test_cli.py' -v` and confirm failures.
- [ ] Implement each route independently. Replace upstream tool-enabled prompts and approval paths; disable auxiliary title calls, session imports and terminal continuation. Existing authentication stays under provider control.
- [ ] Run fixtures and authorized synthetic live tests, including tool-request prompts and injected workspace instructions. Verify no commands, file writes, extensions or unintended context transfer occur. A read-only sandbox alone is insufficient because it can still execute commands.
- [ ] Review and commit each adapter separately. Unsupported adapters must remain visibly disabled with documented reasons; obtain spec review if a required route cannot be delivered safely.

## Task 6: Private settings and bounded conversation history

**Files:** `backend/state.py`, `tests/test_state.py`, user documentation.

**Interfaces:** `load_settings() -> Settings`, `save_settings(settings)`, `append_turn(conversation_id, turn)`, `clear_history()`. Store only plugin-owned settings and conversations under an XDG state directory; temporary chats never persist.

- [ ] Write failing tests for default AI opt-out, 0700 directories/0600 files, symlink rejection, atomic replacement, malformed state recovery, both history caps and complete clearing.
- [ ] Run `python -m unittest discover -s tests -p 'test_state.py' -v` and confirm failures.
- [ ] Implement bounded storage and clear controls. Do not read provider history or credential files. Use synthetic fixtures only.
- [ ] Run tests, inspect permissions and resulting data in a temporary directory, review and commit.

## Task 7: Keyboard palette and answer integration

**Files:** `Overlay.qml`, all `ui/` files, `backend/main.py`, `docs/validation.md`.

**Interfaces:** Consume Tasks 2–6's JSON protocol; expose the exact shell open/close contract recorded in Task 1. UI always displays selected route, model, backend when applicable, and local/cloud classification before submission.

- [ ] Define synthetic UI scenarios for local-only search, AI opt-out, provider absence, disabled stale models, empty/loading/error states and cancellation. Record expected keyboard transitions before implementation.
- [ ] Adapt licensed omaSearch answer formatting into the approved centered layout. Add arrows/Enter activation, Escape hierarchy, provider picker, progress/streaming, copy and clear history. Reject obsolete events and preserve input responsiveness.
- [ ] Verify IME Enter does not submit composition, long text wraps, code is readable, and links require explicit activation; rendering must not fetch remote content automatically.
- [ ] Run backend tests, `omarchy plugin validate` against the exact development directory, and `/usr/lib/qt6/bin/qmllint -I /usr/share/omarchy/shell` on every actual QML file. Record errors and resolve them before runtime testing.
- [ ] On the authorized desktop, exercise real focus and shortcut behavior, display scale/theme, no-provider operation and streaming; capture synthetic visual evidence. Review and commit.

## Task 8: Lifecycle, security and private release candidate

**Files:** `tests/test_package.py`, `README.md`, `SECURITY.md`, `CHANGELOG.md`, `docs/validation.md`, `docs/security-review.md`, `docs/release.md`.

**Interfaces:** Produces a versioned candidate, acceptance matrix and unresolved-blocker list; does not authorize public release.

- [ ] Add packaging checks for manifest references, missing notices, forbidden paths/symlinks, temporary metadata rules and absent private data. Run the full offline suite: `python -m unittest discover -s tests -v`.
- [ ] Audit every subprocess, destination, dependency, file access, privilege and installer. Perform a security review using the appropriate security skill; fix findings and retest affected paths.
- [ ] Exercise discovery, summon/hide, Escape, real shortcut/conflicts, disable/re-enable, shell restart, removal and restoration of the original built-in. Inspect bounded Quickshell logs and before/after state; document retained history and explicit deletion instructions.
- [ ] Complete the provider matrix across all eight routes: missing, model discovery failure, cancellation, local-only routing, no fallback and Q&A restrictions. Missing required evidence blocks release.
- [ ] Document every dependency and setup step, account authorization, configuration, local model preparation, install/disable/removal, privacy, recovery, licenses and reporting path. Prepare a preview using synthetic content.
- [ ] Select the final name and namespaced ID during release review; update all references and remove clone-only metadata in the candidate. Re-run static, packaging and lifecycle checks after this change.
- [ ] Review final diff and private candidate; refresh authenticated remote identity, privacy and history before any push. Keep repository private.
- [ ] Only after explicit 1.0 public-release approval, refresh publishing requirements, change visibility and submit the marketplace issue with category/tags. Record exact submitted commit and maintainer outcome; submission is not acceptance.

## References and review result

Sources refreshed 2026-10-11: [development guide](https://plugins.omarchy.org/develop.html), [publishing guide](https://plugins.omarchy.org/publish.html), [omaSearch README](https://github.com/5h3rd1l/omaSearch), [provider implementation](https://github.com/5h3rd1l/omaSearch/blob/main/ask.py). Provider-specific references remain in the approved architecture and must be refreshed against installed versions in Tasks 4–5.

Self-review: all architecture sections map to Tasks 1–8; review-focus cases have named owners. Runtime, security and license checks remain mandatory. Provider invocation details and clone identity are deliberately gated on recorded live evidence; dependent implementation must stop rather than invent them. Proposed defaults and local-search scope above require plan review.

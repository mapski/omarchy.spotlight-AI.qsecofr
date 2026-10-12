# Active handoff: Omarchy Model Search

**Updated:** 2026-10-11 (America/Toronto)
**Stage:** Owner-approved public source preview 1.0.0-rc.1 published on GitHub; lab candidate installed on VM333. Final 1.0 and live inference remain pending.

## Delivery tracking — 2026-10-11

Owner requested the process and tracker in the repository, Model Search first, mandatory security review gates. Read docs/DELIVERY-PROCESS.md and docs/PROJECT-TRACKER.md for current work. Older entries below are dated snapshots, not current release status.

## GitHub candidate and launch kit — 2026-10-11

Owner requested private GitHub distribution and social promotion. Candidate assets now include real VM screenshots, original SVG/PNG graphics, setup/security/FAQ/contribution docs and platform drafts under docs/marketing. Owner explicitly approved public preview visibility and identified X @haldodev. Browser sign-in remains pending. Public preview does not imply final 1.0 or marketplace acceptance. Preserve Claude block, pending live inference and paused model download. Earlier no-push snapshots below are historical; check the remote and public prerelease for distribution status.

## Current continuation: jcode and minimum downloads

User approved jcode after Codex, Q&A only, ChatGPT working and Claude blocked. Owner approval is required for any additional dependency/model downloads. Gemma E2B transfer is paused (partial staging file on Work volume); do not resume. jcode v0.94.0 official runtime installed only VM333; master 0.95 development is not tested. New adapter uses loaded LM Studio only, temporary private config, no tools/MCP, and a no-redirect relay. Colibri is priority evaluation, not a download approval. Read docs/JCODE.md and latest validation before acting.

## Active pair — ChatGPT and workstation LM Studio

ChatGPT app login is now verified saved; catalog discovery succeeded. User chose their loaded LM Studio Heretic model. VM333 discovers and selects `gemma-4-e4b-it-ultra-uncensored-heretic` through a temporary loopback-only SSH reverse tunnel to workstation port 1234. The separate llama.cpp service is stopped and disabled. Read docs/TWO-PROVIDER-SETUP.md for host distinction and tunnel lifecycle. No inference performed; Claude stays blocked and other provider expansion is paused. No plugin installed on daily desktop; no push.

## Sign-in routing fix — 2026-10-11

User’s Foot success message was native Codex login; direct app registration had not started. Removed misleading CLI sign-in action in favor of explicit Connect ChatGPT Q&A route selection. Added sanitized persisted failure stages and browser confirmation only after actual credential saving. 70 tests pass host/VM; manifest/QML pass. Direct app browser flow now started on VM333, initial registration file creation verified, user completing authorization. Keep Claude blocked and inference pending. See latest docs/VALIDATION.md.

## Direct ChatGPT continuation — 2026-10-11

User approved direct Sign in with ChatGPT. Separate `chatgpt` route now owns public-client OAuth credentials and uses the documented public Responses API with Q&A-only payloads. Claude and Codex CLI remain blocked; live inference remains pending. Active implementation remains in `/home/mp/.codex/worktrees/model-search/Omarchy-Model-Search`, branch `codex/model-search`.

68 offline tests pass locally. Review fixed late OAuth completion after cancellation/logout, UI blocking during account operations, and queued login surviving cancellation. VM account UI was visually checked, including keyboard provider selection; no real sign-in started. Read docs/VALIDATION.md and docs/environment.md for final VM results. README documents setup, account selection, sign-out, storage and removal. No push or public release.

## Latest UI and CLI continuation — 2026-10-11

35 tests pass. Super+Ctrl+M is installed only on VM333 and verified using hardware key injection. UI now has editable roots, saved selections, Recent, destination-bound follow-up, temporary single questions, compact search and responsive theme-aware presentation. Conversation UUIDs prevent restart collisions. Settings-to-search and history keyboard flows passed; original theme/scale and empty roots restored, synthetic data removed.

Pi and Claude passed isolated mock-HTTP tool/context/session tests, with no inference engines or real credentials. Pi credential-command execution remains a blocker; Claude bare-mode does not reuse OAuth. All five CLI routes remain disabled with specific reasons. Live inference remains pending by user request. See docs/providers.md and docs/VALIDATION.md. Remaining acceptance: authenticated CLI isolation, live provider/streaming, IME, packaging/license and public-release approval. No push.

## Earlier implementation continuation — 2026-10-11

Implementation and inline plan execution were approved. Active worktree: /home/mp/.codex/worktrees/model-search/Omarchy-Model-Search, branch codex/model-search. VM333 is authorized; access is through PX1 QEMU guest agent as mp. Never record the supplied lab password. Daily desktop integration remains unauthorized.

31 tests pass. Offline local adapters, preliminary palette/state, asynchronous discovery and rendering limits are implemented. VM clone mp.emojis is enabled. Summon/hide, Escape, disable/re-enable, restart and removal/restoration passed. Existing emoji shortcut failed the automated check and remains unresolved. Dependencies already present; no model/server install. User explicitly deferred live local inference.

Initial security scan completed and its one rendering-amplification finding was fixed with regressions. See docs/VALIDATION.md and docs/providers.md. CLI execution remains disabled pending safety verification. Selection persistence, history UI/follow-up, settings UI, visual matrix and release gates remain incomplete. No push.

## Earlier session update (2026-10-11)

This update supersedes the earlier access and next-action snapshot below. The user approved the architecture including llama.cpp, Ollama, and Pi. Read the [implementation plan](../docs/superpowers/plans/2026-10-11-model-search.md) next; obtain plan review and execution-method selection before implementation.

GitHub authorization now works as `mapski`. Authenticated metadata and Git refs confirmed the exact canonical repository is private, with admin access and default branch `main`. Remote root is `17aa400`; local commits are `166a064` and `38fb53c`. Reconcile histories before pushing; no push has occurred.

Read-only workstation checks found Omarchy `4.0.4-1`, shell files under `/usr/share/omarchy/shell`, and `/usr/lib/qt6/bin/qmllint`. No clone or installation occurred. The official clone command enables its copy immediately: establish an authorized test desktop and baseline first.

The proposed plan adds explicit scope/defaults for review, including local search roots, bounded history and timeouts. Current omaSearch tool execution and auxiliary provider calls require removal for Q&A-only use. All runtime/security/license gates remain outstanding.

## Earlier snapshot (retained for provenance)

## User goal

Create a public Omarchy plugin project that combines a polished Spotlight-style, keyboard-first search palette with deliberate provider/model selection across the user's installed Codex, Claude, Grok, Hermes, and local LM Studio options. Maintain a separate project/repository so it can be released publicly as version 1.0 when ready.

## Read first

- [`../AGENTS.md`](../AGENTS.md) — mandatory ongoing project rules.
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — approved design, product requirements, strict development/publishing gates.
- [Official Omarchy development guide](https://plugins.omarchy.org/develop.html)
- [Official Omarchy publishing guide](https://plugins.omarchy.org/publish.html)

The official guides are living documents and take precedence over this handoff. Re-read them before implementation, validation, and release; follow every applicable step. The marketplace requires a public repo, so keep the canonical repo private until the user's explicit 1.0 public-release approval.

## Decisions and requirements

- Project path: `/home/mp/Work/Projects/Omarchy-Model-Search`.
- Proposed implementation direction: extend MIT-licensed [omaSearch](https://github.com/5h3rd1l/omaSearch); use [Omarchy Spotlight](https://github.com/maajix/omarchy-spotlight) as the visual/interaction reference for a centered, fast, keyboard-first palette. Preserve omaSearch attribution/license. Treat Spotlight as reference only unless its code is separately approved and license-reviewed.
- User asked for automatic detection of installed Grok routes: show standalone `grok` and Hermes independently if available.
- Keep explicit provider/model selection; never silently send to another provider. Use existing provider CLI sign-in, do not scrape tokens or browser stores. LM Studio uses its local endpoint and already available models; never load/download models automatically.
- Initial AI mode is Q&A/search only: no agent tools, shell commands, file writes, or desktop control. Keep local search usable without AI; make web search an explicit separate action.
- Keep AI opt-in, identify local/cloud destination, bound and clear local history, no telemetry by default.
- All Omarchy plugin development, unsandboxed-permission review, validation, lifecycle testing, install/removal safety, visual review, license checks, and publish gates are mandatory per `ARCHITECTURE.md`.

## Current project and Git state (verified in this session)

- The folder contains `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, and this `handoff.d/` documentation.
- Local Git repository initialized on `main`.
- `origin` is set to `https://github.com/mapski/omarchy.spotlight-AI.qsecofr.git`.
- Local `main` is configured to track `origin/main`.
- Initial local commit: `166a064` (`docs: establish Omarchy Model Search architecture`). This session should create a follow-up commit for the handoff docs and corrected access note.
- The user confirmed on 2026-10-11 that the supplied GitHub URL opens in their browser. The URL should be treated as valid.
- This agent's GitHub API lookup returned 404; local `gh auth status` reported an invalid token; `git ls-remote` failed because `github.com` did not resolve from this environment. Therefore the remote's visibility, branch history, and synchronization are not verified here. The user wants it private until version 1.0.
- Do not push, force-push, create another repo, or alter visibility until signed-in remote access verifies exact repo identity, private visibility, and existing refs. If the user wants CLI access, let them complete account authorization interactively; do not request or record credentials.

## Next actions

1. In the new session, inspect `git status`, `git log`, remotes, and this handoff. Refresh live network/remote access status without exposing credentials.
2. If remote access is available, verify the repo is private and inspect its default branch/history before deciding how local commit `166a064` and the follow-up handoff commit should be reconciled. Do not assume an empty remote.
3. Ask the user to review `ARCHITECTURE.md` and collect any corrections. The user approved the direction and requested strict guide compliance; the written spec is ready for review.
4. After spec review, write an implementation plan for user review before code changes. Keep scope focused on this plugin; broader SysChange/shared-AI-memory/local-AI-stack ideas are separate work unless the user brings them into scope.
5. Before implementation, re-read current Omarchy guides and examine the installed Omarchy version/state as required. Select and use the correct user-owned built-in overlay clone workflow, preserve its temporary ID during development, and follow all gates in `ARCHITECTURE.md`.

## Sources

- [omaSearch repo](https://github.com/5h3rd1l/omaSearch) and [provider code](https://github.com/5h3rd1l/omaSearch/blob/main/ask.py)
- [Omarchy Spotlight repo](https://github.com/maajix/omarchy-spotlight)
- [Omarchy plugin development guide](https://plugins.omarchy.org/develop.html)
- [Omarchy plugin publishing guide](https://plugins.omarchy.org/publish.html)
- [Hermes CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands)
- [xAI Grok CLI reference](https://docs.x.ai/build/cli/reference)
- [LM Studio local server](https://lmstudio.ai/docs/developer/core/server)

Recheck changing upstream docs/source before acting; these references describe research used during architecture, not proof of current installed behavior.

## Latest native sign-in continuation — 2026-10-11

Native Claude/Codex Sign in and Check again controls implemented. Foot opens fixed native auth command, palette releases focus; bounded status checks are cancellable and sanitized. Codex mise shim resolved without executing mise. 42 tests pass and VM manifest/QML validation passes. Inference remains disabled: Claude managed-policy fixture executes hooks and credential helper; Codex isolated mock still advertises request_user_input. See docs/providers.md for reproducible scripts and exact evidence. User requested built-in continuity and linked the official Codex CLI guide; do not ask them to manually run login as the normal app flow. No credentials copied, no live inference, no push.

Claude native login has now been opened from the palette on VM333; browser is active and palette hidden. Do not inspect browser authorization contents. User completes login, then reopens and checks status. Both CLI inference gates remain closed regardless of successful sign-in.

## Latest Claude policy investigation — 2026-10-11

Claude login confirmed successful using native status. User explicitly chose Keep subscription CLI blocked after automatic approval review rejected activation and independent review found separate-process account/policy and executable-binding gaps. Experimental backend/providers/claude.py is unregistered and EXECUTION_APPROVED=False; do not enable based solely on a personal Pro/Max preflight. 50 tests pass. tests/manual/claude_adapter.py exercises production arguments/parser with dummy API authentication and loopback responses (text/tool/error); not proof of native OAuth policy isolation. No real prompts, no API-key route, no push. Existing Sign in/Check again flow remains usable.

## Codex continuation — 2026-10-11

Corrected tests/manual/codex_isolation.py to inventory additional_tools input items and namespaces, select a real bundled model by default, and offer --require-no-tools. VM333 Codex 0.162.1: disabling the synchronous question tool makes the unknown synthetic profile empty, but gpt-6.1-sol still exposes code-mode/async/collaboration tools and gpt-5.5 exposes apply_patch. Both real-model strict gates fail as expected. One loopback mock request per run, no context sentinel, no JSONL sessions or literal prompt in temporary HOME files. Codex remains disabled; Claude remains blocked by user decision; live inference pending. See docs/providers.md for scope and next checks. No production/runtime changes, deployment or push in this continuation.

## Codex configuration and execution continuation — 2026-10-11

Expanded the manual probe with harmless unsolicited patch/JavaScript responses and temporary user/system MCP configurations. On VM333 Codex0.162.1, embedded JavaScript really executes despite extra opt-outs; read-only rejects the tested patch write. ignore-user-config skips user MCP but system MCP still starts, even with mcp_servers={}; named disabling works only for the named server. Internal deny-all ToolPolicy is not exposed by inspected public interfaces; strict-config rejects its proposed TOML key. See docs/providers.md for exact scope, reproduction, and required integration boundary. Codex stays blocked, Claude stays blocked, all live inference pending. No production code, VM system configuration, installed CLI, credentials, or plugin deployment changed.

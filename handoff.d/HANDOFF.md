# Active handoff: Omarchy Model Search

**Updated:** 2026-10-11 (America/Toronto)
**Stage:** Architecture written; implementation not started.

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

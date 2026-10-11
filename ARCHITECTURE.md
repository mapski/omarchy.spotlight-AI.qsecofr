# Architecture and Product Specification

**Status:** Approved direction; implementation has not started. Review this specification before implementation planning.

## Purpose

Build a public Omarchy plugin that opens from a keyboard shortcut as a fast, polished search palette. It should handle ordinary local search and route an explicit AI query to a provider and model the user chooses: Codex, Claude, Grok through an installed Grok CLI and/or Hermes, or a local model served by LM Studio.

The visual and interaction goal is the compact, keyboard-first command palette demonstrated by [Omarchy Spotlight](https://github.com/maajix/omarchy-spotlight): centered search input, immediate ranked results, clear keyboard navigation, and a well-composed answer view. AI is one search mode in the palette, not a separate app window. The project should not copy Spotlight code unless a later implementation decision explicitly chooses that dependency and completes license review.

## Product decisions

- Extend the MIT-licensed [omaSearch](https://github.com/5h3rd1l/omaSearch) codebase instead of recreating its Omarchy overlay and AI interaction from scratch.
- Use Spotlight as a visual and interaction reference: rapid search, compact results, consistent keyboard controls, and a polished answer presentation.
- Keep this project separate at `~/Work/Projects/Omarchy-Model-Search` so it can become an independent public repository.
- Preserve upstream attribution, notices, and applicable MIT license text for omaSearch code retained or modified.
- Detect installed provider commands and local endpoints. Let the user explicitly choose a provider and model; do not silently switch providers or send a query to a different service.
- Use each cloud provider's supported CLI and existing user authentication. Do not scrape browser sessions, copy OAuth tokens, or collect provider passwords.
- Treat LM Studio as a local provider through its local OpenAI-compatible API. Discover models from the running local server; do not load or download models automatically.
- Keep AI opt-in in settings and mark the selected destination clearly before a query is submitted.

## User experience

1. A configurable shortcut opens a centered, keyboard-focused palette.
2. Typing shows ranked local results immediately. Arrow keys select; Enter activates; Escape clears or closes. Search mode and keyboard help remain visible without cluttering the input.
3. An `ai:` prefix or an explicit AI mode submits a prompt to the selected provider/model. The palette streams a readable answer in place, supports copy, and retains recent conversations.
4. A provider/model control shows the active choice and makes provider switching deliberate. Unavailable providers are explained and can be refreshed from settings.
5. Search and AI results share a consistent visual language. Answer layouts support formatted text and code first; richer cards or image input are enabled only when the selected adapter supports them.
6. The palette remains useful when no AI provider is configured: ordinary search works, and AI mode gives a clear setup hint.

## Component boundaries

- **Spotlight-style QML palette:** owns window presentation, search input, result ranking display, keyboard navigation, provider/model controls, streaming display, and accessible states. It must remain responsive while a provider is working.
- **Search router:** distinguishes local search, web search, and explicit AI requests. It does not infer permission to send a normal query to a cloud model.
- **Provider registry and adapters:** each adapter reports availability, model choices, streaming support, image support, and invocation method. Shared UI does not hard-code provider-specific assumptions.
- **Provider process/API boundary:** cloud adapters invoke supported local CLIs; LM Studio uses a loopback HTTP API. Output and errors are normalized for the UI, with cancellation and timeouts.
- **Private state:** selected provider/model and bounded conversation history live under a user-owned state directory with restrictive permissions. Secrets are not copied there. The user can clear history.

## Provider behavior

| Provider | Connection | Discovery and selection | Initial safety behavior |
| --- | --- | --- | --- |
| Codex | Installed `codex` CLI using its existing sign-in | Detect executable; query supported CLI model list where available; allow selection from models the CLI reports | Read-only Q&A; no command execution or workspace mutation from the palette |
| Claude | Installed `claude` CLI using its existing sign-in | Detect executable; use supported CLI model options and show only verified choices | No tools enabled for palette Q&A |
| Grok | Detect standalone `grok` CLI and Hermes independently; show one or both routes when present | Ask each installed route for its supported model list when available; for Hermes, use its configured provider/model profile | No agent tools or desktop actions in palette Q&A |
| LM Studio | Local OpenAI-compatible endpoint, normally on loopback | Detect a responding server and query its model list; user selects an already available model | Direct local inference, no tool calling, no automatic model downloads |

If a CLI cannot expose models reliably, show a small, documented manual model field rather than guessing. A provider's model names and capabilities may change; discovery must fail visibly and preserve the last known selection only as a disabled choice until verified. There is no automatic cross-provider fallback.

## Safety, privacy, and reliability

- AI requests are opt-in and clearly label cloud versus local destinations.
- Provider CLI credentials remain managed by the respective provider tools. The plugin must not read browser stores or credential databases.
- Initial scope is question answering and search. No filesystem write, shell command, agent tool, or desktop control is exposed through the AI palette.
- Ordinary local search should not send data to a provider. Web search is a distinct explicit action.
- Conversation history is bounded, stored locally with restrictive permissions, and clearable. No analytics or telemetry by default.
- Use request timeouts, cancellation, and child-process cleanup. Surface provider errors without dumping environment variables or sensitive CLI diagnostics into logs.
- Provider differences are represented as capabilities. Unsupported streaming or rich content degrades to plain text rather than appearing broken.

## Public project and delivery

The project folder is independent of `Omarchy-DR`. Before public release, establish the final name, repository URL, and plugin ID; retain license notices; add user and developer documentation, a security reporting path, and a changelog; validate the plugin manifest and QML; and test installation, enable/disable, shortcut conflicts, provider absence, cancellation, and local-only operation. No public repository has been created or pushed as part of this architecture stage.

## Initial acceptance criteria

- The palette opens quickly, focuses its search field, and supports keyboard-only search and selection.
- Local results remain available with every AI provider stopped or absent.
- An AI request displays the exact selected provider and model and streams or clearly indicates progress.
- Codex, Claude, Grok CLI, Hermes, and LM Studio routes are detected independently; one missing route does not disable another.
- The user can switch among available models and stop a running request.
- No query is silently rerouted to a different provider, and no AI tool can modify files or run commands in the initial release.
- Local LM Studio use is verified to remain on loopback; no cloud request is made in local mode.
- Public packaging preserves upstream license and attribution requirements and passes Omarchy plugin validation.

## References

- [omaSearch repository](https://github.com/5h3rd1l/omaSearch) and [provider implementation](https://github.com/5h3rd1l/omaSearch/blob/main/ask.py)
- [Omarchy Spotlight repository](https://github.com/maajix/omarchy-spotlight)
- [Omarchy plugin development guide](https://plugins.omarchy.org/develop.html)
- [Hermes CLI reference](https://hermes-agent.nousresearch.com/docs/reference/cli-commands)
- [Grok CLI reference](https://docs.x.ai/build/cli/reference)
- [LM Studio local server documentation](https://lmstudio.ai/docs/developer/core/server)

## Mandatory Omarchy plugin development and release rules

These are project gates, not optional recommendations. Every implementation agent must read the current official guides and linked references before beginning or resuming a development or release phase. The live guides are authoritative if this summary is incomplete or differs from current guidance:

- [Develop a Plugin](https://plugins.omarchy.org/develop.html)
- [Publish a Plugin](https://plugins.omarchy.org/publish.html)
- [Official Omarchy shell reference](https://github.com/omacom/omarchy)
- [Built-in plugin examples](https://github.com/omacom/omarchy/tree/master/themes/omarchy/current/share/omarchy/plugins)

If a guide step is unclear, a required check cannot run, or current Omarchy behavior differs from this design, stop that dependent step, gather evidence, and update this spec for review. Never silently skip a gate.

### Development gates

1. **Verify the target environment and current guides.** Before any workstation or Omarchy integration change, verify the installed Omarchy/Quattro version and current state. Re-read the guide and references and check relevant upstream source/issues for that version. Do not assume a guide or handoff snapshot matches the live machine.
2. **Use a user-owned development copy.** Follow the official clone workflow for the closest built-in plugin with the same runtime kind and interaction pattern (an overlay/search surface). Use `omarchy plugin clone` and retain the exact generated temporary clone ID during development. Keep development files in the user-owned plugin area; never edit packaged files under `/usr/share/omarchy` or create a second Quickshell process. Preserve the official shell lifecycle and manifest/runtime contract. Integrate upstream omaSearch functionality only after reviewing how it fits that contract.
3. **Audit the unsandboxed boundary.** Omarchy plugins share the shell process and run with the user's permissions. Review every dependency, command, subprocess, HTTP destination, filesystem access, installer, privilege boundary, and remote build. Avoid unnecessary privileges. Document every external dependency, setup step, service, installer, and remote build in project docs. Keep provider credentials inside their supported CLIs; never scrape account stores or include secrets in logs.
4. **Keep the manifest and IDs correct.** Use the exact temporary clone ID and development metadata while testing. Keep the clone-origin field during clone-based development so disable/remove restores the built-in. Validate the manifest kind, entry point, relative paths, and all referenced files. Before publishing, choose a permanent namespaced plugin ID, replace every temporary ID/reference, and remove clone-only metadata exactly as the guide requires.
5. **Run all static validation.** Run `omarchy plugin validate` on the exact plugin directory. Run `qmllint` with the installed Omarchy shell imports against every QML entry point and component. Resolve all errors before runtime testing. Validate again after the final code, manifest, metadata, or packaging change.
6. **Run every applicable runtime/lifecycle check.** Confirm Omarchy discovers the plugin and reports the expected ID, kind, and enabled state. Exercise the shell open/summon and close/hide routes, keyboard Escape/focus behavior, the real shortcut, disable/re-enable, shell restart, and removal. Check `qs`/Quickshell logs for load/runtime errors. For this search plugin, also test provider missing/unavailable, model discovery failure, cancellation, no-provider local search, local-only LM Studio routing, no silent provider fallback, and shortcut conflicts. Do not claim a check passed unless it was run and observed.
7. **Keep install/removal safe and user-controlled.** Document safe installation, enablement, configuration, disabling, and removal. Test removal and confirm it leaves no unexpected user data or system changes. Do not install or enable the plugin on the user's daily environment without explicit authorization and the required before/after documentation.
8. **Do not skip visual review.** Review the overlay at the actual supported display scale and theme; verify sizing, focus, keyboard flow, readable streaming output, and empty/loading/error states. Keep a visual preview for release when practical and ensure it contains no private prompt/history data.

### Private GitHub repository and source-of-truth rules

- The intended canonical repository is [`mapski/omarchy.spotlight-AI.qsecofr`](https://github.com/mapski/omarchy.spotlight-AI.qsecofr), cloned locally at `~/Work/Projects/Omarchy-Model-Search` with remote name `origin`.
- Keep the GitHub repository **private** during design, implementation, testing, and pre-1.0 review. Do not publish the repository, create a public mirror, submit it to the Omarchy marketplace, or expose unpublished code through public artifacts before the explicit 1.0 release approval.
- Verify repository identity, remote URL, default branch, visibility, and remote history before the first push. If the repository cannot be reached or its visibility cannot be confirmed, stop before push and report the precise blocker. Do not create a replacement repository or alter visibility as a workaround.
- Track all plugin source, manifest, tests, documentation, license notices, and release history in this canonical Git repository. Keep secrets, local auth state, provider data, machine-specific paths, and private test prompts out of version control. Check `git status` and review the staged diff before every commit or push.
- Preserve the omaSearch MIT license and all applicable upstream notices for code retained or modified. Record upstream source/revision and significant divergence in the project docs. Treat Spotlight as a design reference unless separate code reuse is explicitly approved and license-reviewed.

### Publishing and 1.0 release gates

The official marketplace publishing guide requires a **public GitHub repository**, a valid root `manifest.json`, README and license, and safe install/removal instructions. Marketplace validation checks listing metadata; it does not certify plugin security. Therefore:

1. Keep the canonical repository private until the user explicitly approves the 1.0 public release.
2. Before that approval, complete all development gates above, audit licenses and dependencies, verify install/removal and documentation, review the final diff, and prepare the preview image and marketplace metadata.
3. At 1.0 release time, confirm with the user that they want the repository made public. Only after that explicit approval may repository visibility change. Recheck the remote identity and privacy state immediately before changing it.
4. Once public, submit the repository through the official Omarchy plugin submission issue form with its repository link, category, and tags. Do not claim marketplace acceptance until a maintainer approves it.
5. Record the exact public commit/version submitted and the marketplace result. Keep rollback/recovery instructions and installation/removal steps current.

The publishing guide cannot be completed while the repository is private. That is an intentional release gate, not a reason to make it public early.

### Current GitHub access status

On 2026-10-11, MP confirmed the supplied URL opens in their browser, so the URL is valid. From this agent environment, GitHub metadata lookup returned HTTP 404, local `gh auth status` reported the configured `mapski` token is invalid, and a read-only Git check failed because `github.com` did not resolve. The remote repository’s visibility and branch history therefore remain unverified here. Do not push until authenticated access verifies repository identity, private visibility, and remote history.

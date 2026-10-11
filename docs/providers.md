# Provider readiness — 2026-10-11

| Route | Current implementation | Remaining evidence |
| --- | --- | --- |
| LM Studio | Loopback :1234, loaded-model discovery and streaming | Live server version, locality and inference |
| llama.cpp | Loopback :8080, loaded-model discovery, autoload=false on chat | Live server mode/version and inference |
| Ollama | Loopback :11434, installed GGUF/local metadata filter, running-model query, chat | Live locality and inference |
| Codex | Native sign-in/check flow; inference disabled | Mock profile leaves request_user_input advertised; production config/model/auth isolation still pending |
| Claude | Native sign-in/check flow; inference disabled | Non-bare mock passed; managed hooks and credential helper demonstrably execute |
| Grok | Detected; disabled | Full no-tools, context, fallback and persistence controls |
| Hermes | Detected; disabled | Full no-tools, context, fallback and persistence controls |
| Pi | Mock tool/context/extension/session checks passed; disabled | Credential commands still execute; isolated authentication/configuration design required |

VM help inspection: Codex 0.162.1, Claude Code 2.1.296, Pi 1.1.0. Pi advertises no-tools, no-extensions, no-mcp, no-skills, no-prompt-templates, no-context-files, no-session and offline flags. Claude advertises safe-mode, restricted, tools and strict-mcp-config. These are candidates for verification, not a claim that safe invocation is complete. No cloud prompts were sent and no credentials were read.

An unavailable route must stay visibly unavailable. Never use a prompt alone as a tool restriction, substitute another provider, or treat executable presence as sign-in. Model services/models remain user-managed. Loopback is a transport restriction, not proof that a server cannot forward prompts elsewhere.

Official references: [Pi](https://pi.dev/docs/latest), [Grok](https://docs.x.ai/build/cli/reference), [Hermes](https://hermes-agent.nousresearch.com/docs/reference/cli-commands). Verify the installed version before implementing exact arguments.

## Installed CLI safety checks

Checked Codex 0.162.1, Claude 2.1.296, Grok 1.0.50, Hermes 0.19.0 and Pi 1.1.0. Discovery itself only checks executable presence and never launches a CLI.

Pi RPC startup with no-tools, no-extensions, no-mcp, no-skills, no-prompt-templates, no-context-files, no-themes, no-session, no-approve and offline accepted get_state: zero messages, no streaming, no session file; a synthetic extension did not execute.

The installed Pi binary was also tested with a temporary HOME/agent directory and a synthetic loopback OpenAI-compatible HTTP fixture. Explicit fixture/demo selection made two HTTP requests. No tools were advertised; the fixture's proposed bash tool call did not create its marker; the workspace context sentinel was absent; no extension or session file was produced. A separate harmless credential-command probe did create its marker, confirming the documented models.json command execution survives these flags. Do not reuse arbitrary existing model configuration under the palette's no-command promise.

Claude was tested against a synthetic loopback Anthropic-compatible HTTP fixture with a dummy API key and temporary HOME. Flags: print, bare, safe-mode, restricted, tools empty, strict-mcp-config with an empty server map, no-session-persistence, explicit synthetic model and system prompt. Two requests, no advertised tools, no context sentinel, no proposed Bash execution, no SessionStart hook and no session file. Bare mode does not reuse OAuth/keychain authorization, so this is not proof of the required existing-sign-in route.

Reproducible manual fixture scripts are tests/manual/pi_isolation.py and tests/manual/claude_isolation.py. They create temporary homes and mock servers; never supply real credentials. They are separate from the unit suite and report measured outcomes for the installed CLI. No real model or cloud inference was invoked.

Codex exec's read-only sandbox still permits command execution; no complete no-tools profile was established. Grok exposes tool allowlists and no-subagents but extension/context/history suppression remains unverified. Hermes safe-mode suppresses customization but complete no-tools, fallback and transcript suppression remains unverified. These are explicit blocked gates, not passing adapters.

## Native sign-in continuation — 2026-10-11

Choose Claude or Codex in the palette, then **Sign in**. The app opens Foot with the provider's fixed native login command and dismisses the palette so keyboard input reaches the terminal/browser. Reopen with Super+Ctrl+M and select **Check again** after authorization. Existing CLI sign-in stays in the CLI's own storage; no credential files are read or copied. Closing the palette cancels a pending status check; the interactive login terminal stays user-controlled. Opening login is explicit, never part of passive discovery.

Status output is bounded, parsed and discarded; only a boolean and generic guidance reach the UI. Currently a positive check recognizes first-party Claude subscription or Codex ChatGPT sign-in, not API-key/custom-backend modes. A failure or timeout means not confirmed, not proof the account is signed out. Native authentication can still be subject to administrator policy. Authentication never enables inference by itself.

The launcher removes inherited API keys, endpoint overrides, proxy/helper/runtime injection variables, preserves the desktop session, and invokes fixed argument arrays without a shell. The Codex mise shim is resolved to its existing native installation without running mise or bootstrapping a package. Normal user authentication commands may load provider configuration; this is separate from, and does not establish, a safe inference profile.

### Measured remaining gaps

- **Claude 2.1.296:** removing `--bare` while retaining safe-mode, restricted, empty tools, empty settings sources, explicit disableAllHooks/apiKeyHelper overrides, empty strict MCP and no-session-persistence passed the synthetic HTTP tool/context/user-hook/user-helper/session test. This keeps native OAuth eligible, but is not authenticated inference evidence.
- **Managed Claude policy:** a temporary bubblewrap mount containing synthetic managed-settings.json reproduced **both startup-hook and credential-helper execution**, despite those flags. Two loopback mock requests, no model engine, no real credentials. `tests/manual/claude_managed_policy.py` asserts this known failure so an upstream behavior change requires re-review. The fixture does not modify system policy. Do not suppress real administrator policy to enable this route.
- **Codex 0.162.1:** ignore-user-config, ignore-rules, ephemeral, no project documents, disabled web search/shell/unified-exec/snapshot/hooks/plugins/skills/images/multi-agent/goals/sleep removed the dangerous advertised tools in the synthetic fixture. **request_user_input remains**, even with collaboration_modes disabled; no context sentinel or session JSONL was observed. `tests/manual/codex_isolation.py` records that inventory, not a passing all-tools-disabled assertion. The fixture does not yet establish hostile tool-call rejection or production auth/config/model discovery isolation.
- VM native status checks reported neither first-party sign-in confirmed. Live inference remains explicitly deferred. Both execution routes therefore remain disabled; local search and native sign-in actions are usable.

References refreshed: [Codex CLI](https://learn.chatgpt.com/docs/codex/cli), [Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference), [Claude settings precedence](https://code.claude.com/docs/en/settings). Installed-version mock evidence, rather than documentation alone, determines readiness.

## Personal-account gate experiment — 2026-10-11

Native status confirms the VM's existing Claude Pro sign-in. A candidate gate checks Linux, exact CLI 2.1.296, personal Pro/Max native OAuth, an owned non-symlink config directory, absence of /etc/claude-code and cached remote-settings.json, and repeats filesystem checks before requests. It rejects unsupported versions before running auth status. The isolated profile disables tools, MCP, slash commands, persistence, customizations and configured model fallback; it uses a fresh working directory and the CLI-owned sign-in path.

The production-profile/parser fixture (`tests/manual/claude_adapter.py`) passed synthetic text, hostile Bash tool response and HTTP error cases. Text completed with one request; the hostile tool response failed with one request and no execution; the HTTP error failed after three same-model attempts. No tool advertisement, context sentinel, helper/hook marker, session JSONL or persisted synthetic prompt was found. These tests replace authentication and policy preflight with synthetic fixtures and therefore **do not prove the subscription authentication boundary**.

Fresh review found that separate native status and prompt processes do not bind the checked account to the account actually used; newly fetched managed policy may execute in noninteractive sessions without being cached. Executable identity can also change between checking and launch, and alternate credential precedence needs exact-version evidence. The early version rejection and a host-dependent test were fixed; the other assurance gaps remain.

Automatic approval review rejected registry/UI wiring because those policy protections were unproven. The user then explicitly chose **Keep subscription CLI blocked**. The candidate remains unregistered and has `EXECUTION_APPROVED = False`, with a regression proving rejection before any subprocess launch. No API-key route was added; sign-in remains intact; no live inference occurred. Before future activation, establish a supported same-execution credential/policy boundary and bind the verified executable, then repeat independent review. Do not treat a passing personal preflight as activation approval.

Current references: [managed-policy delivery and noninteractive behavior](https://code.claude.com/docs/en/server-managed-settings), [parent policy precedence](https://code.claude.com/docs/en/managed-settings), [model fallback controls](https://code.claude.com/docs/en/model-config).

# Provider readiness — 2026-10-11

| Route | Current implementation | Remaining evidence |
| --- | --- | --- |
| LM Studio | Loopback :1234, loaded-model discovery and streaming | Live server version, locality and inference |
| llama.cpp | Loopback :8080, loaded-model discovery, autoload=false on chat | Live server mode/version and inference |
| Ollama | Loopback :11434, installed GGUF/local metadata filter, running-model query, chat | Live locality and inference |
| Codex | Detected; disabled | No-tools, context and history isolation |
| Claude | Mock no-tools/context/hooks/session checks passed; disabled | Existing sign-in and managed-policy isolation; tested bare mode requires API-key auth |
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

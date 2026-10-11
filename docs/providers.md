# Provider readiness — 2026-10-11

| Route | Current implementation | Remaining evidence |
| --- | --- | --- |
| LM Studio | Loopback :1234, loaded-model discovery and streaming | Live server version, locality and inference |
| llama.cpp | Loopback :8080, loaded-model discovery, autoload=false on chat | Live server mode/version and inference |
| Ollama | Loopback :11434, installed GGUF/local metadata filter, running-model query, chat | Live locality and inference |
| Codex | Detected; disabled | No-tools, context and history isolation |
| Claude | Detected; disabled | Validate safe-mode/tools/MCP/context/history controls with existing sign-in |
| Grok | Detected; disabled | Full no-tools, context, fallback and persistence controls |
| Hermes | Detected; disabled | Full no-tools, context, fallback and persistence controls |
| Pi | Detected; disabled | Exact backend/model, tools/extensions/MCP/context/history isolation |

VM help inspection: Codex 0.162.1, Claude Code 2.1.296, Pi 1.1.0. Pi advertises no-tools, no-extensions, no-mcp, no-skills, no-prompt-templates, no-context-files, no-session and offline flags. Claude advertises safe-mode, restricted, tools and strict-mcp-config. These are candidates for verification, not a claim that safe invocation is complete. No cloud prompts were sent and no credentials were read.

An unavailable route must stay visibly unavailable. Never use a prompt alone as a tool restriction, substitute another provider, or treat executable presence as sign-in. Model services/models remain user-managed. Loopback is a transport restriction, not proof that a server cannot forward prompts elsewhere.

Official references: [Pi](https://pi.dev/docs/latest), [Grok](https://docs.x.ai/build/cli/reference), [Hermes](https://hermes-agent.nousresearch.com/docs/reference/cli-commands). Verify the installed version before implementing exact arguments.

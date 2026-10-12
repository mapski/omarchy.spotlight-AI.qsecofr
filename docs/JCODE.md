# jcode Q&A integration

Priority: working direct ChatGPT first, followed in the picker by the blocked Codex CLI and optional jcode. Existing LM Studio is the local backend. Claude remains blocked. New dependency/model downloads require explicit owner approval; do not automatically install, update, pull, or replace models. The Gemma E2B download remains paused. Colibri is a priority for a later source/hardware evaluation, not an approved model download.

## Verified version and scope

The current official release inspected on 2026-10-11 is v0.94.0, source tag commit b6c63ff. Upstream master was 6487bbd7e9a45e6f91822292d6128854d5a6c5c6 (0.95.0 development); that development build is not installed or claimed tested.

The official Linux x86-64 archive SHA-256 is `e471f61e661612cfd6da5e9c1bb8238fab0c63c3ebc96c648439816649478c1b`. Extracted executable SHA-256 is `8fe2c71d03ff306eb930b09ea13d51f44aeac03a51a648cae65c6b01ede82085`. Only this verified binary is enabled; other versions require renewed verification. It is installed only on VM333 at `~/.local/share/omarchy-model-search/runtime/jcode-0.94.0.bin` (about 137 MB). No system package or daily-desktop installation. The archive was about 44 MB. No further downloads are automatic.

Select **jcode · LM Studio Q&A**, then an explicitly loaded model. Backend is displayed as lmstudio/local. The existing workstation LM Studio is reached through the documented temporary loopback SSH tunnel. jcode does not serve models and does not reduce their weight storage requirement. No native jcode cloud authentication is imported or enabled; the working direct ChatGPT account remains separate.

## Execution boundary

Each call uses a fresh private HOME, working directory, JCODE_HOME and XDG directories. No user config, hooks, MCP, skills, native CLI credentials, or workspace files are copied. The verified executable is opened and invoked through the same file descriptor. `--tool-profile none`, `--no-selfdev`, disabled MCP, automatic follow-ups, telemetry and updates are explicit. Temporary jcode sessions/logs are removed after the process and relay stop. App history remains under its existing bounded/clearable policy.

jcode's HTTP transport follows redirects by default. A per-request loopback relay therefore accepts one request for the exact selected model, rejects tool declarations, and forwards only to the fixed LM Studio origin through a no-proxy/no-redirect client. Redirect targets never receive a prompt. The relay uses a random URL path and bounded requests/output/timeouts; it is not a general proxy. Cloud fallback is not configured.

Unknown output, model changes, tool events, missing completion and failed process exits are errors. The whole process group is terminated on cancellation, timeout or failure. Inputs are limited to 48 KB including serialized follow-up history because this jcode interface accepts the message as a positional argument. During execution it can be visible to processes permitted to inspect the process command line. The app does not log command lines. Native persistent jcode sessions are not reused.

## Verification and cleanup

`python tests/manual/jcode_isolation.py /path/to/verified/jcode.bin` uses only synthetic loopback responses. It verifies ordinary streamed text, absent tool declarations, unsolicited shell-tool rejection and no redirect forwarding. It never uses real provider credentials or a model engine. Run the full offline suite and Omarchy validation before deployment. Live inference, answer quality and latency remain pending.

Removing this optional runtime file disables jcode discovery. Removing the plugin does not remove this separately installed runtime. Do not delete ChatGPT auth data to remove jcode. No jcode persistent auth store is created by the app.

Sources: [jcode](https://github.com/1jehuang/jcode), [v0.94.0](https://github.com/1jehuang/jcode/releases/tag/v0.94.0), [license](https://github.com/1jehuang/jcode/blob/v0.94.0/LICENSE). Runtime MIT license; no jcode source or binary is redistributed in the plugin.

## Colibri priority

[Colibri](https://github.com/JustVugg/colibri) is a separate inference engine, with a loopback OpenAI-compatible server. Its current README describes at least 8 GB RAM and 22 GB disk for its smallest model; large MoE experts stream from disk. This is upstream guidance, not a successful run on this workstation or VM. Evaluate model support, actual host resource budget, loaded-state discovery and no-download behavior before integration. No Colibri runtime/model has been downloaded or installed.

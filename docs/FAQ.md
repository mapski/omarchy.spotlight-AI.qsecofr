# Questions and current limits

**Is this a finished public 1.0?** No. The corrected 1.0.0-rc.2 candidate is prepared but unpublished. Real direct-provider backend tests passed; actual QML acceptance, final checks and publication remain pending. See the [release record](RELEASE-1.0.0-rc.2.md).

**Does it replace Omarchy's shell?** No. It is a user-owned overlay using the existing shell lifecycle. The corrected candidate has permanent ID `io.github.mapski.model-search`.

**Is ordinary search powered by an LLM?** No. It matches application names and filenames in configured roots. It does not read/index document contents or perform semantic research.

**Can the model edit files or run commands?** That is outside the app's Q&A scope. Native routes that have not established that boundary stay blocked.

**Does ChatGPT mean Codex CLI?** No. ChatGPT is the separate direct app connection. The native Codex CLI entry remains unavailable for inference.

**Why use jcode if LM Studio already works?** It provides an optional harness route. It is not required for direct local Q&A and does not replace the model server. The owner can keep the smaller direct path.

**Is jcode 0.95 supported?** Current upstream source was reviewed, but the newest published binary tested here is 0.94.0. Unknown binary versions remain disabled until verification is repeated.

**What is the smallest setup?** Use the existing direct ChatGPT connection or an already installed, loaded local model. Do not add another runtime just for discovery. The source archive includes no model weights.

**Does “Heretic” make the model more accurate for research?** No accuracy claim is established here. The existing Heretic model is a user-selected local model; it is not specifically trained for Spotlight search.

**Is Colibri included?** No. Its current source/API and hardware requirements are prioritized for evaluation. No Colibri runtime or weights have been installed.

**Can I install this on my daily desktop?** It is a release candidate. Back up `~/.config/hypr` and `~/.config/omarchy` first; removal with `omarchy plugin remove` is supported.

**Why is LM Studio unavailable?** The app only lists models that LM Studio reports as loaded on its loopback endpoint. Start the server and load a model; there is no fallback.

**Why does a long answer appear as plain text?** Answers above 4,096 normalized UTF-16 code units use plain text to keep malformed Markdown from blocking the shared shell. No additional answer text is removed beyond the existing answer limit. Short answers retain Markdown formatting.

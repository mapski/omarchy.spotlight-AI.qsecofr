# Changelog

## 1.0.0-rc.2 — 2026-10-12

- Adopt permanent plugin ID `io.github.mapski.model-search` (name "Model Search", maintainer `mapski`); remove development clone metadata.
- Limit rich Markdown formatting to 4,096 UTF-16 code units; longer answers use plain text. Fix Unicode heading backtracking.
- Fix the answer view collapsing to zero width; add Qt geometry regression tests.
- Clarify Settings text about the private ChatGPT credential store; simplify ChatGPT status messages.
- Verify ChatGPT and LM Studio streaming and cancellation through the backend. Live chat and Stop in the palette UI are not yet verified end to end.
- Move internal development notes out of the public repository.

## 1.0.0-rc.1 — 2026-10-11 (public source preview)

- Keyboard-first local search, explicit Q&A selection, streaming display, cancellation, bounded history and temporary questions.
- Direct ChatGPT sign-in and account persistence; first provider in the picker.
- Optional pinned jcode 0.94.0 route after Codex, using already loaded LM Studio models with no tools, disposable configuration and enforced loopback destination.
- Claude and unsafe native CLI routes remain blocked. No silent fallback.
- No automatic dependency or model downloads.
- 75 offline tests and real-jcode synthetic isolation checks pass. Live inference, answer quality/latency, IME acceptance and public-release packaging identity remain pending.

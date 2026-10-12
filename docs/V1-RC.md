# Private v1 candidate

Version: 1.0.0-rc.1. This archive contains source, tests, documentation and licenses only; no models, runtimes, credentials or history. Keep private. It retains the official VM333 development clone identity mp.emojis, so it is not a marketplace package.

## Use on VM333

Press Super+Ctrl+M. Ordinary text searches apps and configured folders. Enable AI, choose ChatGPT or jcode explicitly, then choose a model and submit with the ai: prefix. jcode uses the existing LM Studio model through the temporary private tunnel; it does not replace the model server. Stop cancels an answer; Escape closes the palette. Recent supports destination-bound follow-up; temporary questions avoid saved history. Claude remains blocked.

ChatGPT sign-in and model catalog are verified. Local discovery is verified. Live inference remains pending at the owner's request; synthetic response tests are not a claim of working real model answers. No automatic downloads or provider fallback.

## Authorized development install / removal

For a separate authorized test environment, first create a user-owned overlay clone using `omarchy plugin clone omarchy.emojis`, read its generated ID, and preserve that clone ID/metadata. Do not overwrite an unrelated plugin. Review the documented Python dependencies before installation; dependency/runtime/model downloads require owner approval.

On the existing VM333 clone only, copy the archive contents into `~/.config/omarchy/plugins/mp.emojis/`, validate that directory with `omarchy plugin validate`, then use `omarchy plugin enable mp.emojis` and `omarchy restart shell`. This is not authorization to install on the daily desktop.

Disable with `omarchy plugin disable mp.emojis`. Remove with `omarchy plugin remove mp.emojis`; the original built-in emoji overlay is restored. App auth/history under `~/.local/state/omarchy-model-search` and the separately installed optional runtime are retained. Sign out through the app before removing auth data if revocation is wanted. Tunnel cleanup is in TWO-PROVIDER-SETUP.md. Never copy credentials into this archive.

## Remaining release gates

Real ChatGPT/local inference, streaming/cancellation with real providers, IME acceptance, final permanent public identity, final public license/package review and explicit public-release approval. No push or visibility change is included in this candidate.

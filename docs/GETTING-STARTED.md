# Getting started

This guide describes corrected candidate 1.0.0-rc.2, currently prepared but unpublished. Complete the [candidate checks](RELEASE-1.0.0-rc.2.md) before enablement. The validated environment is Omarchy 4.0.4-1, Quickshell 0.3.1-1 and Qt 6.11.2-1. Other versions are not claimed tested.

## Open and search

After enablement, use the shortcut configured for `io.github.mapski.model-search`; the earlier VM clone used **Super+Ctrl+M**. Type an application name such as `Foot`. For filenames, open Settings and choose explicit search roots. Matching is name-based; it is not semantic document-content search. Use arrow keys and Enter to activate a result. Escape clears/closes the palette. An empty result does not trigger AI or a cloud search.

## Choose AI deliberately

Enable AI, refresh providers, choose a provider, then choose a model. Use the `ai:` prefix to ask. An unavailable model remains unavailable; the app does not substitute another provider. Real direct ChatGPT and LM Studio streaming/cancellation passed through the production backend. Actual QML chat acceptance remains pending; see the [measured scope](RELEASE-1.0.0-rc.2.md#verified-real-backend-requests).

### ChatGPT

Choose **ChatGPT · Direct Q&A**. Use **Continue with ChatGPT**, complete the official browser authorization, and return to the palette. The browser says **ChatGPT account saved successfully** only after validated credentials are saved. Refresh and explicitly choose an available model.

The direct app connection is independent of native Codex CLI. Eligibility, quotas and model access are determined by the account/provider; no plan or unlimited-usage guarantee is made. The lab account's login and model discovery are verified.

### Existing LM Studio

Start the already installed LM Studio server and load a compatible model yourself. The app discovers only models reported as loaded at `http://127.0.0.1:1234`. Discovery does not download, load or switch a model.

### Optional jcode

jcode 0.94.0 is optional and not bundled. Select **jcode · LM Studio Q&A** and its loaded model. On another machine the route stays unavailable until the exact reviewed runtime is installed with owner approval. No account import or jcode cloud route is enabled. [Setup and limitations](JCODE.md).

## Accounts and data

- **Add account** creates another app registration; the picker selects the active registration.
- **Cancel sign-in** stops the current authorization attempt.
- **Sign out** attempts provider revocation and clears local tokens. If revocation fails, follow the displayed instruction to disconnect the app in ChatGPT Settings.
- **Clear history** deletes app conversation history, not account credentials.
- **Temporary questions** avoid saved conversation history. jcode's disposable working files are removed after its process exits.
- Private state lives under `~/.local/state/omarchy-model-search` or the configured XDG state root. Tokens are permission-restricted but not encrypted at rest.
- Removing the plugin preserves private state and separately installed runtimes. Sign out first if disconnecting the account, then remove retained state only if you intend to erase it.

## Install or remove

Follow the [README install steps](../README.md#install). Never launch a second Quickshell instance.

The app never downloads models, runtimes or dependencies on its own.

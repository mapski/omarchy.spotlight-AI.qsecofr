# Model Search 1.0.0-rc.2

Second release candidate. It replaces the 1.0.0-rc.1 source preview. This is a prerelease for testing, not the final 1.0.

## Highlights

- **Permanent plugin ID** `io.github.mapski.model-search`, named "Model Search", by maintainer `mapski`. The development clone metadata has been removed. rc.1 used a temporary ID, so remove it before installing rc.2.
- **Safer Markdown rendering.** Rich formatting is limited to 4,096 UTF-16 code units, and longer answers are shown as plain text. Fixes a heading pattern that could backtrack heavily on Unicode line separators.
- **Answer view fix.** Answers no longer collapse to zero width after switching providers or showing account controls.
- **Clearer status text.** Settings now explains that ChatGPT credentials are kept in the app's private account store.

## Tested

See [Testing](TESTING.md). In summary:
- 78 unit tests, 10 Qt tests, `omarchy plugin validate` and `qmllint` pass.
- The full install, enable, disable, restart, remove and reinstall cycle passed on a clean Omarchy 4.0.4 install.
- Backend streaming and cancellation were verified with ChatGPT and LM Studio.

## Known limitations

- Live chat and **Stop** through the palette UI have not yet been verified end to end.
- After copying a fresh install into the plugins folder, run `omarchy-shell shell rescanPlugins` before `omarchy plugin enable`.
- Codex CLI, Claude, Grok, Hermes and Pi are shown but blocked. Only ChatGPT direct and loaded LM Studio models are supported for Q&A.
- ChatGPT tokens are stored in owner-only files but are not encrypted at rest.
- Only Fcitx 5 was tested for input methods.

## Install

Follow the [README install steps](../README.md#install). Verify the checksum first:

```sh
sha256sum -c omarchy-model-search-1.0.0-rc.2.tar.gz.sha256
```

The archive contains no model weights, provider binaries, tokens, account state or history.

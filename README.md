<p align="center"><img src="docs/assets/hero.svg" alt="Model Search — Find locally. Ask deliberately." width="100%"></p>

# Omarchy Model Search

**A keyboard-first search palette for Omarchy that makes you pick an AI provider and model before anything is sent.** Find applications and files locally. When you want an answer, choose ChatGPT or a local model you have already loaded.

**Release candidate `1.0.0-rc.2` · MIT**

[Get started](docs/GETTING-STARTED.md) · [Release notes](docs/RELEASE-1.0.0-rc.2.md) · [Changelog](CHANGELOG.md) · [Testing](docs/TESTING.md) · [Security](SECURITY.md)

> **Release candidate.** This is a prerelease for testing, not the final 1.0. Automated tests, install/remove lifecycle and keyboard/IME behaviour were checked on a clean Omarchy 4.0.4 install. Streaming and cancellation were verified against ChatGPT and LM Studio through the backend. Live chat and **Stop** in the palette UI have not yet been verified end to end. Please report issues.

## Features

- **Search without AI.** Matches application names and filenames in folders you choose. Ordinary search never sends queries to a model.
- **Explicit destination.** Pick a provider and model before asking. ChatGPT is listed first. There is no silent fallback to another provider.
- **Q&A only.** The app gives AI no agent tools, shell commands or desktop control. Unsupported routes are shown as unavailable.
- **Keyboard first.** Bind a shortcut (for example `Super+Ctrl+M`). Arrow keys navigate, Enter activates and Escape clears or closes.
- **Conversation controls.** Stop a response, copy an answer, reopen recent conversations or ask a temporary question. Follow-ups stay with their original provider.
- **Uses what is installed.** Discovery never downloads models or starts model servers.

## Screenshots

Unretouched captures of the palette at 1280×800.

![Local application search](docs/assets/local-search.png)

![Provider picker with ChatGPT first](docs/assets/providers.png)

![Palette with a loaded LM Studio model selected](docs/assets/palette.png)

## Provider status

| Route | Status in rc.2 |
| --- | --- |
| Local app/file search | Supported |
| ChatGPT (direct sign-in) | Supported; backend streaming and cancellation verified |
| LM Studio (loopback) | Supported for already loaded models; backend streaming and cancellation verified |
| jcode → LM Studio | Optional; synthetic checks only |
| Codex CLI, Claude | Shown but blocked; no safe Q&A-only execution yet |
| llama.cpp, Ollama | Adapters present; not part of rc.2 testing |
| Grok, Hermes, Pi | Detected but blocked |

The ChatGPT route is a direct app connection. It does not run Codex CLI.

## Install

Requires Omarchy 4.0.4 or later and `python-pyjwt` (with `python-cryptography`) from the distribution repositories.

```sh
sha256sum -c omarchy-model-search-1.0.0-rc.2.tar.gz.sha256
tar xzf omarchy-model-search-1.0.0-rc.2.tar.gz
cp -a omarchy-model-search-1.0.0-rc.2 ~/.config/omarchy/plugins/io.github.mapski.model-search
omarchy plugin validate ~/.config/omarchy/plugins/io.github.mapski.model-search
omarchy-shell shell rescanPlugins
omarchy plugin enable io.github.mapski.model-search
omarchy restart shell
```

Bind a key in `~/.config/hypr/bindings.lua`, for example:

```lua
o.bind("SUPER + CTRL + M", "Model Search", "omarchy-shell shell toggle io.github.mapski.model-search")
```

To uninstall, run `omarchy plugin disable io.github.mapski.model-search`, then `omarchy plugin remove io.github.mapski.model-search --yes`. Removal keeps your app settings, history and sign-in. Clearing those is a separate action described in [Getting started](docs/GETTING-STARTED.md#accounts-and-data).

## Privacy

Local search is independent of AI. Web search is an explicit browser action. Questions go only to the provider you selected. Local models are reached through a loopback endpoint.

ChatGPT tokens are stored in owner-only local files, separate from the bounded conversation history. They are **not encrypted at rest**. See the [security notes](SECURITY.md).

## Development

```sh
python -m unittest discover -s tests -v
QT_QPA_PLATFORM=offscreen /usr/lib/qt6/bin/qmltestrunner -input tests/qml
omarchy plugin validate .
```

JavaScript presentation tests run only when Node is available. See [contributing](CONTRIBUTING.md), [architecture](ARCHITECTURE.md), [roadmap](docs/ROADMAP.md) and the [FAQ](docs/FAQ.md).

## License and credits

MIT. Includes adapted omaSearch/omAsk code with attribution. Omarchy Spotlight informed the interaction design; no Spotlight code is bundled. jcode is an optional external MIT runtime. See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).

Independent community project; not affiliated with OpenAI, LM Studio or Omarchy.

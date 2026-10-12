# Testing — 1.0.0-rc.2

## Automated checks

| Check | Result |
| --- | --- |
| `python -m unittest discover -s tests` | 78 tests pass. The 7 JavaScript presentation tests are skipped when Node is not installed, and pass with Node. |
| `qmltestrunner -input tests/qml` (offscreen) | 10 pass, 0 fail (Markdown renderer and answer-view geometry). |
| `omarchy plugin validate` | Pass. |
| `qmllint` on `Overlay.qml`, `ui/*.qml`, `tests/qml/*.qml` | Pass, with known Omarchy shell metadata warnings. |

## Clean-install checks

Tested on a clean Omarchy 4.0.4 install (Quickshell 0.3.1, Qt 6.11.2, Fcitx 5.1.22, 1280×800):

- Install from the release archive, validate, enable, disable, re-enable, shell restart, remove and reinstall. Settings and sign-in were preserved, and one shell process remained throughout.
- Shortcut summon and hide, keyboard navigation and Escape handling.
- Real Fcitx composition: preedit is shown, and Enter commits without submitting.
- Markdown rendering for normal, long and malformed answers. Rich formatting is limited to 4,096 UTF-16 code units, and longer answers are shown as plain text.

## Provider checks

- ChatGPT direct and LM Studio: real streaming responses and cancellation were verified through the production backend.
- jcode: synthetic checks only (text, tool rejection, redirect handling).
- **Not yet verified:** live chat and Stop end to end through the palette UI, other IME engines, and other themes and scales beyond those tested earlier.

No latency, answer-quality or performance claims are made.

# Dependencies

Verified on VM333 on 2026-10-11. The original backend used only the standard library. Direct ChatGPT authentication adds the dependencies below.

| Dependency | Use | Verified |
| --- | --- | --- |
| Omarchy 4.0.4-1 / Quickshell 0.3.1-1 | Shared shell and plugin lifecycle | Yes |
| Qt declarative 6.11.2-1 / qmllint | QML controls and validation | Yes |
| /usr/bin/python (3.14) | Backend and OAuth client | Yes |
| gio | Explicit desktop/file activation | Yes |
| wl-copy | Explicit copy answer | Yes |
| Node 26.8.2 | Pure JavaScript regression tests only | Yes |
| grim / wtype | Lab visual and keyboard checks only | Yes |

Direct ChatGPT requires PyJWT with cryptography (requirements.txt); there are no npm runtime dependencies. Test discovery skips JavaScript checks if Node is absent; release verification must have Node installed and no skipped checks.

Model services/models are separately user-managed. No model server or model was installed. Provider command presence is not proof of authentication or safe execution.

Use Omarchy's supported package commands for missing dependencies on an authorized test desktop. Never run an upstream plugin installer or silently bootstrap a provider during discovery. The earlier Hermes help invocation triggered its installed lazy bootstrap; see environment.md.


## Direct ChatGPT dependencies and licenses

VM333: python-pyjwt 2.13.0-1 installed for this phase; python-cryptography 50.0.1-1 was already present. Host isolated `/tmp` test environment: PyJWT 2.15.1, cryptography 50.0.2. Both environments run the same offline suite. No daily-desktop system package was installed.

PyJWT is MIT licensed; cryptography is Apache-2.0 OR BSD-3-Clause. The tested CFFI 2.1.1 package declares MIT-0 and pycparser declares BSD-3-Clause; these license expressions were verified from installed distribution metadata. Dependencies are external packages, not vendored; their package license files remain with the installed distributions. The project and retained upstream code remain MIT. Final release packaging/license audit remains a separate gate.

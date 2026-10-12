# Dependencies

Verified on a clean Omarchy 4.0.4 install on 2026-10-11. The original backend used only the standard library. Direct ChatGPT authentication adds the dependencies below.

| Dependency | Use | Verified |
| --- | --- | --- |
| Omarchy 4.0.4-1 / Quickshell 0.3.1-1 | Shared shell and plugin lifecycle | Yes |
| Qt declarative 6.11.2-1 / qmllint | QML controls and validation | Yes |
| /usr/bin/python (3.14) | Backend and OAuth client | Yes |
| gio | Explicit desktop/file activation | Yes |
| wl-copy | Explicit copy answer | Yes |
| Node 26.8.2 | Pure JavaScript regression tests only | Yes |
| grim / wtype | Manual visual and keyboard checks only | Yes |

The native sign-in launcher also requires `foot` when that optional path is used (`backend/auth.py` checks its presence). This does not enable blocked CLI inference. Its current installation/version was not rechecked in the documentation pass.

Direct ChatGPT requires PyJWT with cryptography (requirements.txt); there are no npm runtime dependencies. Test discovery skips JavaScript checks if Node is absent; release verification must have Node installed and no skipped checks.

Model services and models are managed by the user. The optional jcode runtime is not bundled. Provider command presence is not proof of authentication or safe execution.

Use Omarchy's supported package commands for missing dependencies. Never run an upstream plugin installer or silently bootstrap a provider during discovery.


## Direct ChatGPT dependencies and licenses

Tested with distribution packages python-pyjwt 2.13.0 and python-cryptography 50.0.1, and with PyJWT 2.15.1 / cryptography 50.0.2 in an isolated environment.

PyJWT is MIT licensed; cryptography is Apache-2.0 OR BSD-3-Clause. The tested CFFI 2.1.1 package declares MIT-0 and pycparser declares BSD-3-Clause; these license expressions were verified from installed distribution metadata. Dependencies are external packages, not vendored; their package license files remain with the installed distributions. The project and retained upstream code remain MIT. Final release packaging/license audit remains a separate gate.

# Dependencies

Verified on VM333 on 2026-10-11. All currently required runtime and test dependencies were already installed; no additional package installation was needed in this continuation.

| Dependency | Use | Verified |
| --- | --- | --- |
| Omarchy 4.0.4-1 / Quickshell 0.3.1-1 | Shared shell and plugin lifecycle | Yes |
| Qt declarative 6.11.2-1 / qmllint | QML controls and validation | Yes |
| /usr/bin/python (3.14) | Backend; standard library only | Yes |
| gio | Explicit desktop/file activation | Yes |
| wl-copy | Explicit copy answer | Yes |
| Node 26.8.2 | Pure JavaScript regression tests only | Yes |
| grim / wtype | Lab visual and keyboard checks only | Yes |

No pip/npm dependencies are required by the plugin. Test discovery skips JavaScript checks if Node is absent; release verification must have Node installed and no skipped checks.

Model services/models are separately user-managed. No model server or model was installed. Provider command presence is not proof of authentication or safe execution.

Use Omarchy's supported package commands for missing dependencies on an authorized test desktop. Never run an upstream plugin installer or silently bootstrap a provider during discovery. The earlier Hermes help invocation triggered its installed lazy bootstrap; see environment.md.

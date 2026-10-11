# Development environment evidence

Recorded 2026-10-11. The user selected a separate test VM; its address and graphical-session status are pending. No daily-desktop plugin clone, installation, enablement, shortcut change or restart is authorized or performed.

Read-only daily-host inventory: Omarchy 4.0.4-1; shell `/usr/share/omarchy/shell`; qmllint `/usr/lib/qt6/bin/qmllint`. Executables found: codex, claude, grok, hermes, pi, llama-server, lms. Ollama was not on PATH. This establishes executable presence only, not safety, authentication or model availability. Repeat relevant checks on the VM.

The built-in emoji search is an overlay candidate (`omarchy.emojis`) with `open(payloadJson)`, `close()`, `toggle()` and shell-injected `manifest`/`shell` properties. Inspect the VM's installed contract before selecting it. No clone ID exists yet.

Before cloning on the VM, record plugin discovery/enabled state, affected shell settings and shortcut conflicts; save a restrictive backup outside the repository. Record the official clone's generated ID and copy files without symlinks. Test disable/remove restores the built-in and compare after-state. No second Quickshell process.

Repository work is on the attached `codex/model-search` worktree. Merge 02fb89d preserves both unrelated histories, retains the approved README and the remote MIT license. No push has occurred.

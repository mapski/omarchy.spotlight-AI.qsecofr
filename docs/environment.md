# Development environment evidence

Verified 2026-10-11 on the user-authorized lab VM333 (mp, 10.0.0.210), reached through PX1 QEMU guest agent. Omarchy 4.0.4-1, Quickshell 0.3.1-1, Qt declarative 6.11.2-1; graphical Hyprland session active.

User authorized snapshots instead of other backups. Disk snapshots model-search-predev-20261011 and model-search-prepalette-20261011 were confirmed before changes. No daily-desktop plugin installation or configuration changes.

Official clone: omarchy plugin clone omarchy.emojis produced mp.emojis, clonedFrom omarchy.emojis. Development files were copied into that VM clone without source symlinks. Disable and re-enable succeeded; disabling restored builtin emoji availability. The existing shell was restarted after new files hit the installed shell's QML cache issue. No second Quickshell process was launched.

Manifest validation passed. qmllint exits zero with an external temporary qs import mapping; warnings remain for PanelWindow, QProcess exit metadata and dynamic theme properties. This is not warning-free lint. Updated overlay opened and displayed the Firefox application result at 1280x800. Continuation verified removal/restoration, official re-clone, summon/hide and Escape clear/close. Super+Ctrl+M now targets mp.emojis and passed hardware-key injection. Light/dark and effective 100/125/160 percent scales checked; original theme and scale restored. Live streaming/IME acceptance remains pending.

The VM has no llama-server, ollama or lms command. User explicitly requested offline adapters be finished and live inference tests remain pending. No models or model servers were installed. CLI command presence does not establish safe Q&A execution; all CLI routes remain disabled.

Running hermes --help unexpectedly invoked the installed Omarchy lazy bootstrap and installed Hermes/Python 3.13 in the VM. This side effect was disclosed and is covered by the predevelopment snapshot.

Work lives in the attached codex/model-search worktree. Merge 02fb89d retains both histories and the remote MIT license. No push or public release.

Additional confirmed snapshot: model-search-preui-20261011. VM bindings.lua contains the dedicated Model Search key; remove its two-line marked block to undo. No prior binding was replaced.


Direct OAuth continuation: installed python-pyjwt 2.13.0-1 on VM333; python-cryptography 50.0.1-1 was already present. Snapshot model-search-preoauth-20261011 was created after dependency installation and before deploying the direct ChatGPT build. The initial snapshot command failed due argument quoting; the corrected command succeeded. No other custom backup was made. Official removal generated its own standard plugin backup during the lifecycle test.

The final direct ChatGPT build was deployed only to the approved mp.emojis clone. All 68 offline tests passed using VM Python. Manifest and QML validation passed; account controls and empty-account state visually checked in the current Ethereal theme at 1280x800/100%. Hardware keyboard selection, dedicated shortcut, disable/re-enable, restart and removal/restoration passed. No real ChatGPT sign-in or inference was initiated, no provider credentials were copied, and no daily desktop dependency/plugin changes occurred.

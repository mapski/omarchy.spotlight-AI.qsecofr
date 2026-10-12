# Release evidence checklist

Copy into the release record; do not check boxes from memory.

- [ ] Exact source commit, repository and approved visibility recorded.
- [ ] Independent code review recorded with reviewer, scope and findings.
- [ ] Security audit recorded against the candidate; auth, tokens, config, execution, HTTP, persistence and dependency boundaries covered.
- [ ] All release-blocking findings fixed and verified; remaining findings explained.
- [ ] Relevant automated tests pass; skips and environment limitations disclosed.
- [ ] Current official Omarchy guides read; manifest and all QML components validated.
- [ ] Test-desktop UI/keyboard/IME and lifecycle/install/removal/rollback checks pass.
- [ ] Real-provider acceptance complete for final 1.0; approved preview deferrals explicitly labeled.
- [ ] Provider destination and no-tools/no-fallback constraints verified.
- [ ] Permanent identity and clone metadata correct for final marketplace package.
- [ ] Licenses, dependency provenance, setup, removal and data-retention docs reviewed.
- [ ] Screenshots and archive reviewed for secrets/private information; no credentials or model weights bundled.
- [ ] Artifact checksums, remote commit and release URLs verified after upload.
- [ ] Final public release/marketplace authorization recorded when applicable.
- [ ] Promotion claims match evidence; actual post URLs recorded.

A checklist is evidence routing, not automated enforcement or security certification. Missing required evidence blocks final release.

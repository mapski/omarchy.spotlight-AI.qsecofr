# Model Search completion tracker

Updated 2026-10-11 (America/Toronto). Priority: Model Search first. Owner: mapski. Process: [delivery gates](DELIVERY-PROCESS.md).

## Current milestone

Finish the public source preview and prepare a reviewable final-1.0 candidate. Public preview is available; final 1.0 is not complete. Live inference remains explicitly deferred. No expansion into additional providers or downloads is part of this milestone.

| ID | Work | Status | Evidence / next action |
| --- | --- | --- | --- |
| MS-01 | Public source preview and downloadable artifacts | Done | [v1.0.0-rc.1](https://github.com/mapski/omarchy.spotlight-AI.qsecofr/releases/tag/v1.0.0-rc.1), source commit fda6080deaab325c915a94857e9ae2c17cffebf9; remote public visibility and prerelease verified 2026-10-11. |
| MS-02 | Screenshots, graphics and campaign copy | Done | [Media kit](marketing/README.md); original SVG/PNG and real UI captures shipped. |
| MS-03 | Delivery process and accurate current-state documentation | Done | Process, tracker, PR template and checklist independently reviewed; no blocking documentation/privacy findings. Local links and diff whitespace verified. This is not a runtime audit. |
| MS-04 | X announcement with graphic and GitHub link | Blocked | Owner authorized @haldodev. Last accessible browser showed login; no published post URL. Next: verify authenticated account, post once, record URL. |
| MS-05 | Final candidate code/security review | Ready | Historical scoped reviews in [validation](VALIDATION.md) are not final certification. Next: audit exact final candidate, track findings and verify fixes. |
| MS-06 | Enforced GitHub review/check policy | Ready | Verified 2026-10-11: main branch protection API reports unprotected; effective branch rules are empty. Next: configure enforceable review/check policy with a viable independent reviewer and actual check jobs; do not claim enforcement from a template. |
| MS-07 | Permanent plugin identity and final package/license audit | Ready | Preview retains development clone metadata. Next: select permanent namespaced identity, audit references/notices and validate in authorized lab. Do not rewrite the preview tag. |
| MS-08 | IME and final UI acceptance | Ready | [Recorded visual/lifecycle evidence](VALIDATION.md). Next: test composition and keyboard behavior on authorized lab session; preserve configured account/model. |
| MS-09 | Real ChatGPT/local responses, streaming and cancellation | Deferred | Owner requested pending live inference. Next: run only after that instruction changes; synthetic fixtures are not proof. |
| MS-10 | Final 1.0 and marketplace submission | Blocked | Depends on MS-05 through MS-09 and explicit final release approval. Preview visibility approval is not final acceptance. |
| MS-11 | Website and monitoring | Blocked | Website URL not identified. Next: obtain URL and distinguish progress tracking from recurring uptime/link checks; no monitoring configured. |
| MS-12 | Other social platforms | Blocked | [Launch ledger](marketing/LAUNCH-CHECKLIST.md); accounts unidentified. Next: verify authorized accounts before posting; no mass comments or paid ads. |

## Fixed decisions

Claude and native Codex execution remain blocked. Keep ChatGPT first and explicit local destination selection. Existing model remains selected; paused download stays paused. Additional provider expansion, Colibri installation and new downloads are outside this milestone.

## Completion rules

Every done item links to evidence. Publish/audit records identify the exact revision and scope. Failed checks and unresolved blockers remain visible. Record website and actual social URLs here or in the linked launch ledger after verification. Other projects use this process in their own repositories; this public tracker contains no private cross-project inventory.

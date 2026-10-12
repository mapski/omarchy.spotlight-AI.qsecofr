# Delivery process

Applies to Model Search and reusable for other software projects. Updated 2026-10-11 (America/Toronto). The owner approved this process and prioritized Model Search. Track only this public project's information here; other projects keep their own trackers. Never publish unrelated project details, credentials, private prompts or infrastructure inventories.

## Workflow

| Stage | Required work | Exit evidence |
| --- | --- | --- |
| Inventory | Confirm repository, approved visibility, current commit, scope and blockers. | Dated tracker with next actions. |
| Define completion | Choose the smallest useful milestone and observable acceptance criteria. | Explicit scope and exclusions. |
| Implement | Focused branch changes, documented dependencies, no unauthorized downloads. | Reviewable diff tied to tracker items. |
| Review and security audit | Independent correctness review; audit credentials, auth, configuration, permissions, tools, network destinations, data retention and dependencies. | Reviewer, exact commit/diff, findings, fixes and verification recorded. |
| Validate | Relevant automated tests; actual UI, lifecycle, installation/removal and rollback checks. | Commands, environment, results and limitations recorded. |
| Package | Setup, limitations, changelog, licenses, actual screenshots and original graphics. | Reviewed artifacts tied to a commit with checksums. |
| Publish | Verify exact destination, owner-approved visibility, history and release target. | Remote commit, release URL and uploaded digests verified. |
| Promote | Accurate copy and graphics on authorized accounts; check community rules. | Actual post URLs; drafts never count as published. |
| Track | Update defects, website health, milestones and next actions. | Each unfinished item has a status and next action. |

## Mandatory gates

Code changes require independent code review and security review before merge or publication. Documentation-only changes require independent review and a scoped security/privacy check; they do not establish that runtime code passed a new full audit. Match audit depth to the changed boundary and perform a full candidate review before final 1.0.

Any unresolved critical/high finding blocks release. Other findings block when they undermine Q&A isolation, credential safety, destination selection, data privacy or required acceptance behavior. Record lower-risk findings with rationale and next action; never silently waive them. Verify fixes and rerun affected checks. Any change after review requires review of the new diff; tie every result to its exact commit or patch.

No release advances with unresolved release-blocking findings or failed required checks. A preview may explicitly defer acceptance work only within owner-approved preview scope; it cannot claim final readiness. Final 1.0 cannot pass while required live inference or IME tests remain pending.

These are required workflow gates. The PR template documents evidence; it is not automated enforcement. Branch protection, required checks and independent approval enforcement must be verified separately before claiming GitHub enforces them.

## Persistent constraints

- Q&A only; ordinary search stays independent of AI, with no silent fallback.
- ChatGPT is the direct paid route. Claude and native Codex execution remain blocked.
- Live inference is deferred by the owner; do not perform it just to clear the tracker.
- Model download remains paused. Further dependency/model downloads require owner approval.
- No daily-desktop installation without explicit authorization and required change records.
- Public source preview is approved; final 1.0 and marketplace submission remain separate gates.

## Tracking convention

Use [PROJECT-TRACKER.md](PROJECT-TRACKER.md). Status is done, active, ready, blocked or deferred. Done requires linked evidence; historical evidence must be labeled as such. Each active/ready item has a next action. Keep blocker questions precise. Preserve completed release artifacts; update the tracker on main without silently replacing tagged archives.

A website needs an identified URL, approved check scope and cadence before recurring monitoring is configured. Record uptime/link checks separately from application correctness. Report only actionable changes, failures or decisions when monitoring is enabled.

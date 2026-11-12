Prepare a corrected status memo from the bundle's latest October 25
Codex/Copilot follow-up. The draft below needs review:

“Copilot readiness and paint failed because neither was established. The
extension activated, so the UI was ready. The inspected Expand handler proves
the fullscreen request ran. A person saw the chart and the controller briefly
listed it, so controls passed. Refusing a stale edit means the guard failed.”

Create exactly `review/status.md` and `review/status.json`. Explain each
statement using only the actual available evidence, preserving unknown
versions and separating source, log, native, user-report, controller and
synthetic-fixture layers. Give the current account choice and remaining
checks without performing them. The stale-edit sentence is a hypothetical:
the draft provides no actual stale-edit receipt for this status memo.

Use the skill's typed evidence workflow. JSON needs `findings`,
`evidence_records`, `sources`, `host_acceptance_verified:false` and
`task_empirical_tests_performed:false`. Each factual finding must reference
its supporting normalized records through `evidence_ids`. Reuse the
helper-rendered ledger table in Markdown; do not handwrite replacement tags.
Explain the authored-language/palette boundary without inventing paint or a
user study. This is a status review, not a UI design task.

Use only this prompt and read-only `skills/desktop-plugin-ui/`; write elsewhere.
Stay offline. No account operation, Copilot sign-in, provider/model call,
installation, app/global action, browser, prototype or UI test is permitted.
Check both final artifacts in typed mode, inspect `passed`, and repair until
clean. Cite exact bundled primary URLs for any documentation claims.

Design a UI fallback plan for incident responders working under these rules.
Claude Code and GitHub Copilot are available only in terminal, with scarce
model allowances; Codex is used headlessly with approval policy `never`; a
custom Codex app-server client could later use `on-request`. Another group
uses GitHub Copilot in VS Code, but only an extension-owned webview has been
tested. Claude Desktop Chat and ChatGPT are future dashboard destinations,
and users sometimes decline a form or cancel a URL flow. The team proposes
one universal HTML panel and assumes an advertised image-input or canvas
capability means that the panel will render everywhere.

Create `handoff/restricted-surfaces.md` and `handoff/recovery-plan.json` in
English. Recommend concrete usable routes for the current constraints and a
staged investigation for future dashboards. Address capability negotiation,
policy, cancellation, native versus browser control contracts, image input
versus output/display, local versus remote deployment, and budget guards.
Use canonical patterns and exact primary-source links from the snapshot.

JSON needs `snapshot_date`, `hosts` (rows with `host_id`, `host`, `surface`,
`ui_method`, `limits`, `evidence`, `validation`, `sources`), `patterns`
(canonical IDs or objects with `id`), `historical_observations`, `checks`,
`host_acceptance_verified`, and `task_empirical_tests_performed`. Distinguish
the five host IDs `claude-code`, `claude-desktop`, `codex`, `chatgpt`, and
`copilot` wherever applicable. Historical observations need `host_id`,
`surface`, `version`, `evidence_layer`, `result`, and `evidence`. Preserve
recorded empirical findings at their actual layer. Both task-level booleans
must be false; there is no actual host session in this task.

Use only the supplied read-only `skills/desktop-plugin-ui/` snapshot. Do not
use network, install or open applications, change external configuration or
accounts, or spend any provider tokens. Write outputs elsewhere in this
workspace. Run the bundled source checker on both completed artifacts,
inspect the passed result, and repair findings before finishing.

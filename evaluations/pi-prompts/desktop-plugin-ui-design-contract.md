A support queue needs search, selected-ticket details, an editable priority,
a chart, CSV export, and an explicit action asking the assistant to explain
the selection. Refresh can fail, an edit can be invalid or cancelled, and a
keyboard user must be able to recover. No palette has been selected for this
deliverable. Prepare an English design recommendation and inspection contract,
not a running application, using the supplied skill snapshot.

Create exactly `design/ui-review.md` and `design/ui-contract.json`. Apply all
ten canonical Nielsen IDs, H1 through H10, to concrete queue interactions.
For each give a finding or planned check, status, evidence scope, proposed
fix, and a practical validation action. Explain any not-applicable decision.
Do not present a heuristic inspection as representative-user testing.

Choose the default palette, identify its exact bundled asset path, and bind
semantic roles to exact asset tokens and hex values. Cover primary action,
hover/pressed, body/helper text, page/surface, link, selection, error accent
and readable error text, success confirmation, and keyboard focus. Explain
what would authorize ColorSet 2 for a future deliverable; neither multiple
chart categories nor a dark host theme is an explicit selection. Do not mix
CS2-only hues into the active set, modify palette assets, invent shades, or
assume a declared token is automatically accessible. Give redundant labels,
icons, or shapes for status and chart categories.

A proposed implementation uses `#cfcfcf` as its sole authored focus indicator
against white, `#9c9c9c` as the sole identifying input border against white,
and ordinary-sized error text `#e8002a` on `#ffccd5`. Check all three actual
foreground/background pairs with numeric contrast ratios and the applicable
thresholds. Give exact allowed-token repairs and validate the replacement
pairs. Keep this local calculation separate from rendered-host acceptance.

Distinguish authored MCP App HTML/chart or extension-webview paint from Claude
native nodes, Copilot terminal controls, Codex host elicitation, MCPB settings,
permission dialogs, and surrounding host chrome. Cover all five assistants
where relevant. Record `exact`, `host-mapped`, `host-owned`, or
`accessibility-override` styling scope and explain its limits. Preserve forced
colors and high-contrast overrides. Do not invent CSS/ANSI truecolor support
or claim exact palette pixels for host-owned controls or untested paint.

JSON must contain `snapshot_date`, `palette` with `name`, `selection_source`,
`asset`, and `roles`, plus `heuristics`, `styling_scopes`, `contrast_checks`,
`sources`, `host_acceptance_verified`, `task_empirical_tests_performed`, and
`user_testing_performed`. The ten heuristic objects need `id`, `status`,
`interaction`, `finding`, `evidence`, `fix`, and `validation`. Role records need
a semantic role, exact source token, hex value, and intended usage. Contrast
records need original colors, numeric ratio, threshold, pass/fail, and a
replacement pair with its ratio. Keep all three task-level booleans false:
there is no target-host session or user study in this task.

Use canonical bundled interaction pattern IDs where they support a design
decision. Cite exact bundled Nielsen and W3C primary URLs, and applicable host
sources. Give a short acceptance sequence covering keyboard focus, default,
hover, selected, busy, invalid, cancelled, refresh-error and recovery states,
narrow layout, and real-container palette/contrast checks. A checklist or
palette audit does not establish usability or a product's UI support.

This is closed-book. Do not use network, install or deploy software, operate
external applications/accounts, change configuration, or call a provider.
Read only the copied skill and this task; `skills/desktop-plugin-ui/` is a
read-only resource. Write generated files outside it. After both final
artifacts exist, run this bundled diagnostic command, inspect `passed`, and
repair findings before finishing:

```bash
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py design/ui-review.md design/ui-contract.json
```

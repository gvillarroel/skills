We need a plugin for ordinary Claude Desktop Chat that lets a small warehouse
team inspect stock, filter a table, edit a reorder threshold, export a CSV, and
ask Claude to explain a selected item. The data service currently runs only on
the user's workstation. Sometimes refresh fails. A dashboard would benefit from
more room, but users should still get something useful if UI is unavailable.

Write an English implementation recommendation to `proposal/ui.md` and a compact
decision record to `proposal/decision.json`. Explain the integration route,
appropriate patterns and methods, critical failure handling, evidence, and how
we should validate it. The JSON should contain `host`, `surface`, `transport`,
`patterns` (canonical skill IDs), `host_acceptance_verified` (boolean), and
`checks` (array). No actual host session or cloud deployment is available.

Use the supplied skill snapshot without network access. Do not install anything,
change application configuration, or operate external services. The copied
`skills/desktop-plugin-ui/` is read-only; write task outputs elsewhere in
the workspace. Recommend a concrete route and call out genuine unknowns.

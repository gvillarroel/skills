A team is applying the same incident-response workflow to several assistant
surfaces. Produce a design review and implementation plan using only the
copied desktop-plugin-ui bundle; this task performs no live host or user test.

The team owns an MCP App dashboard and an ordinary VS Code extension webview.
For release A nobody requested a palette. For release B the user explicitly
selected ColorSet2. Both show queued/running/failed/completed jobs, one main
action, editable filters, a retry after a server error, and optional details.
The team wants every status and action to be distinguished by color alone.
It also copied #cfcfcf as the sole keyboard focus ring against #ffffff, and
#e8002a as ordinary error text against #ffccd5, assuming canonical palette
membership proves contrast.

Their other routes are a Claude Code native terminal pane, negotiated Copilot
terminal confirm/select/input, host-owned MCP elicitation forms, a package
settings form, and assistant permission dialogs/toolbars. A colleague proposes
injecting the same CSS, Open Sans font, brand icons, button colors, and DOM
layout into all these surfaces. They also propose disabling host dark/high
contrast/forced-color behavior so screenshots match the light dashboard. The
installed terminal's effective colors and truecolor support are unknown.
No current screenshot, interaction trace, contrast measurement, or usability
session is available.

Write exactly these two English files:

- `review/design-host-boundary.md`
- `review/design-host-boundary.json`

Lead with an actionable recommendation. Apply all ten Nielsen usability
heuristics to this workflow, with a concrete rule, relevant surface scope,
failure/recovery behavior, and a realistic verification step for each. Explain
where a heuristic affects content or flow even when the plugin cannot style
the control. Keep a heuristic inspection distinct from a user study, measured
usability, live host acceptance, and accessibility conformance certification.

Select and justify the palette separately for releases A and B. Give a compact
exact-token role map for author-controlled content, including primary action,
hover, text, surfaces, focus and labeled feedback. Preserve palette identity
without blindly copying an unsafe foreground/background role pair. Calculate
the two proposed contrast ratios with reproducible arithmetic or bundled
machinery, state the applicable thresholds, and specify safe in-palette
repairs. Describe actual-state/compositing checks still required. Explain how
native/terminal themes, host-owned forms/chrome, mandatory host style rules,
and user accessibility preferences limit palette control; do not invent a
styling API or force unsupported CSS/terminal colors. Preserve visible focus,
readable text, cancellation, and useful non-color/nonvisual fallback.

The JSON must contain `snapshot_date`, `palette_cases` (objects with
`case_id`, `request`, `selected_palette`, `decision_reason`, and `roles`),
`contrast_checks` (objects with `foreground`, `background`, `ratio`,
`required_ratio`, `result`, `repair`, and `measurement_scope`),
`surface_decisions` (objects with `surface`, `paint_owner`, `styling_control`,
`palette_application`, `exceptions`, `fallback`, and `validation`),
`heuristics` (ten objects with `number`, `name`, `rule`, `surface_scope`,
`recovery`, `verification`, and `evidence`), `remaining_checks`, `sources`,
`host_acceptance_verified`, `task_empirical_tests_performed`, and
`user_testing_performed`. All three booleans must be false. Do not represent
planned checks as executed observations or an untested action as a failure.

This is a closed-book advisory task. Do not use network, install/open apps,
change accounts or host settings, or call external providers. Treat
`skills/desktop-plugin-ui/` as read-only. Use exact source links from the
bundle, disclose snapshot limits, and check both completed reports with the
bundled report checker. Inspect its result and resolve findings before
finishing. Write generated outputs only outside the copied skill directory.

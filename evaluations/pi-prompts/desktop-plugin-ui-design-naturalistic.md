We are reviewing a proposed support-ticket plugin before implementation. It
will use an app-owned MCP Apps interface in ordinary Claude Desktop Chat and
Copilot in VS Code; agents using a terminal still need a useful text workflow.
Support staff must find a ticket, inspect its details, change its priority,
resolve it, and export the current filtered queue. Use **ColorSet2 explicitly**
for the app-owned design, using the supplied skill's palette definitions and
semantic roles. Do not substitute the default ColorSet1 or restyle host chrome.

Here is the design brief we have, not an observed running interface:

- A wide fixed-layout queue has a decorative hero, four charts, and backend
  counters above the tickets. The same layout is planned for narrow inline
  slots. An unlabelled spinner appears during refresh, with no saved/pending
  indication or last-refresh information.
- Controls use a mixture of "Close", "Resolve", and "ACK" for the same action.
  The detail view exposes names such as `MCP_ROUTE`, `sync_id`, and `E409`.
- Priority changes commit immediately when an option is selected. The only
  way out of details is an unlabelled X; there is no cancel, draft protection,
  or undo. Resolving a ticket also happens immediately with no recovery path.
- Current filters disappear when details open. The user must remember the
  selected ticket ID and previous priority. Assignee and priority options
  appear only on hover, and the brief has no keyboard/focus route or shortcuts.
- A rejected edit replaces the draft with defaults and shows only "E409".
  Refresh failure clears the table. The export action has no description of
  whether it exports filtered or all rows. There is no task help or empty-state
  guidance. Status is communicated only by color; colors have no stable roles.

Write an English audit and implementation recommendation to
`design/queue-audit.md` and a machine-readable decision record to
`design/queue-audit.json`. Assess **all ten Nielsen heuristics**, preserving
their numbers and the bundled H1-H10 labels. For each, give an outcome tied
to this brief, a specific recommendation, and an acceptance check. Do not invent a violation
when evidence is insufficient; one issue may affect more than one heuristic.
Prioritize the fixes by their effect on the described tasks and explain your
reasoning; do not present that design judgment as measured user impact.

Explain a workable surface-specific approach, including inline layout,
host theme constraints, pending/error/cancel states, terminal fallback, and
feature-dependent actions. Provide a concrete ColorSet2 role/token decision
for surfaces, text, interaction, and status, with accessible non-color cues.
If you calculate contrast, identify exact foreground/background pairs and
method; a palette by itself does not establish full-interface accessibility.

JSON must contain `snapshot_date`, `palette` (an object with
`id: "colorset2"`, `explicit_request: true`, and `token_roles`), `heuristics`
(exactly ten objects with `number`, `name`, `outcome`, `brief_evidence`,
`recommendation`, `acceptance_check`, and `evidence`),
`surface_decisions`, `priorities`, `sources`, `host_acceptance_verified`,
`task_empirical_tests_performed`, and `rendered_ui_verified`. Keep design-brief
inference and proposed checks separate from observed runtime behavior. All three task-level
booleans must be false; no running prototype or actual host session is supplied.
Historical bundle observations, if cited, need their own scoped evidence record.

Use only the supplied snapshot and its exact primary-source links. Do not use
network, call providers, install software, open external apps, change accounts
or configuration, build/render a prototype, or alter the read-only
`skills/desktop-plugin-ui/` directory. Write generated files elsewhere in
this workspace. Run the bundled report checker on both completed artifacts,
inspect its `passed` field, and repair findings before finishing. Return an
actionable audit; keep proposed, calculated, documented, and observed evidence
distinct.

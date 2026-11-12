Our support team wants one interactive ticket queue for ordinary Claude Desktop
Chat and ChatGPT. It has search, a selection, an editable priority, and an export.
We may later add a small Claude Code pane. The current server is a local stdio
process; a separate remote deployment is possible. We have no signed-in host
session during this design task. Show us what can be shared and what must vary.

Create `handoff/cross-host.md` and `handoff/matrix.json` in English. Include
surface, transport/origin/deployment requirements, UI patterns, optional
capabilities, state/error behavior, and a practical validation plan. Cite the
bundled primary-source links with the snapshot date. JSON must contain a `hosts`
array (each item has `host`, `surface`, `transport`, and `ui_method`), `patterns`
(canonical skill IDs), `host_acceptance_verified` (boolean), and `limits` (array).

Use the supplied skill as a closed-book source. Do not use network, install or
deploy anything, or modify external apps. `skills/desktop-plugin-ui/`
is a copied read-only resource. Write generated files elsewhere in the workspace.

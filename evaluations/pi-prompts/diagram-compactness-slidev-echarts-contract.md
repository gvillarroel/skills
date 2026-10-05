# Native directed graph contract

Use the loaded skill's bundled ECharts palette and native graph arrow helper
to render a deterministic SVG graph at exactly 640×360. Its nodes are Alpha,
Beta and Gamma, each a 90×40 rectangle; connections are Alpha → Beta and
Beta → Gamma. Use native fixed coordinates with all three at the same
y coordinate and clear route space. Keep complete labels and heads visible.
Inspect the result at delivery size and use the helper again after a resize
to verify stable endpoint clearance.

Write exactly `deliverables/graph.svg`, `deliverables/graph-option.json` and
`deliverables/layout-review.md`. Record actual helper and browser findings.
This is a component/renderer contract smoke, so a full Slidev deck is not
required. Do not publish anything.

Treat `skills/slidev-echarts/` as read-only. Generated files belong outside
it. Do not read acceptance examples or other skills. Install dependencies
in this workspace if needed; use the loaded skill and normal local tools.

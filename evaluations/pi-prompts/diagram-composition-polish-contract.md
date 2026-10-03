Use diagram-composition to make a small diagram that can be edited and validated
with its bundled tools. Use two equally sized panels in one row on a 1000 by 560
canvas, displayed at 1000px with text at least 14px. Each panel is a boundary view
containing Source and Review as separate objects. The panels show the same two
identities in a planning view and a delivery view; no execution order is implied.
Source uses #276bc8, Review uses #9e1b32, and essential labels stay dark.

Connect Source to Source and Review to Review across the panels. Lines should
meet the objects cleanly, remain readable, and not cross unrelated object interiors.
Use native boundary panels and the bundled builder, composer, and browser audit.
Keep the declared two relationships; do not replace them with an explanatory note.

Create out/brief.json, out/plan.json, out/figure.svg, out/report.json, out/audit.json,
out/preview.png, out/review.md, and editable panel SVGs in out/panels/. Inspect
the screenshot and finish with a passing final audit without --inspect. Explain
the visual choices and any limitations in out/review.md. The loaded
skills/diagram-composition/ directory is read-only. Keep generated files inside
this workspace. Do not read other skills, use the network, or install tools.

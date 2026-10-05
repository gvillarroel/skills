# Parser handoff diagram

Create an editable, offline native ECharts SVG explanation of a parser handoff.
Use the complete concept labels `Parser input <raw>`, `Normalize {payload}`
and `Archive & verify`. The directed relationships are Parser input <raw> →
Normalize {payload}, captioned `Choose {a}`, and Normalize {payload} → Archive &
verify, captioned `Keep {b} & {c}`. Use the title `Literal labels & provenance`.
Keep every label complete and make the diagram readable at ordinary laptop
size, with clear direction and traceable endpoints.

Write exactly `deliverables/literal.svg`, `deliverables/literal-option.json`
and `deliverables/layout-review.md`. Render and inspect the delivered SVG and
record its actual dimensions and findings. Do not publish anything.

Treat `skills/echarts-animated-svg/` as read-only. Write generated files in this
workspace, outside that directory. Do not read acceptance examples, other
skills or repository documents. Install needed dependencies in this workspace.

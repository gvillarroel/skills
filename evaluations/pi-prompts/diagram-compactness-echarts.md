# Offline conceptual graph

Create an editable, offline SVG explanation of a laboratory sample workflow.
The relationships are Receive → Barcode → Analyze → Review → Archive, with
Review → Analyze for a retest and Analyze → Quarantine for a failed sample.
Keep every named step and relationship, distinguish the retest from forward
progress, and make the result suitable for reading at ordinary laptop size.
Use the loaded skill's normal authoring and animation workflow.

Write exactly `deliverables/workflow.static.svg`,
`deliverables/workflow.animated.svg`, `deliverables/workflow-validation.json`
and `deliverables/layout-review.md`. Include the actual output dimensions and
your rendered layout findings in the review. Preserve quantitative chart
geometry if any is used. Do not publish anything.

Treat `skills/echarts-animated-svg/` as a read-only resource. Put generated
files outside it, do not inspect acceptance examples or other skills, and use
only the task inputs and normal local tools. Dependencies may be installed
in this workspace when needed.

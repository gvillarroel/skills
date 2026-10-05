# Slide audit smoke

Create a minimal local Slidev deck containing one supplied-input slide: a
white background, a title “Review complete” and two separate black 24px
paragraphs, “Input checked” and “Result archived”. Keep all text in the
slide with ample readable spacing. Then run the loaded skill's automated
audit and inspect its screenshot. This smoke verifies the audit workflow,
not diagram authoring or a quantitative chart.

Write exactly `deck/slides.md`, `deck/package.json`,
`deliverables/audit/quality-report.md`,
`deliverables/audit/quality-report.json` and
`deliverables/layout-review.md`. Record actual findings and commands.

Treat `skills/slidev-quality-audit/` as read-only. Generated files belong
outside it. Do not read acceptance examples or other skills, and do not
publish anything. Use normal local tools; install dependencies locally
when needed.

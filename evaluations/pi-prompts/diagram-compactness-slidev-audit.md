# Review a workflow slide

Create this small supplied fixture as a local Slidev deck, then review it
using the loaded audit skill. It has one slide with a white 960×540 SVG and
four 130×44 rectangles at (40,180), (280,180), (520,180), (760,180). Their
labels, centered in each rectangle in 18px black text, are Intake, Check,
Approve and Archive. Use opaque light-gray fill. Black straight arrows join
the adjacent box edges at y=202, with visible 10px arrowheads outside the
target rectangles. A return route Approve → Check goes below the row at
y=295, labelled “recheck” in 18px black text. The SVG is the complete task
input; it does not contain a quantitative chart.

Keep every concept and connection. Assess the diagram for ordinary laptop
presentation, make useful layout repairs within the slide, and verify the
result in the browser. Record manual findings separately from what the
automated audit proves. Do not publish anything.

Write exactly `deck/slides.md`, `deck/package.json`,
`deliverables/audit/quality-report.md`,
`deliverables/audit/quality-report.json` and
`deliverables/layout-review.md`. Include actual verification commands and
before/after layout findings in the review.

Treat `skills/slidev-quality-audit/` as read-only. Generated files belong
outside it. Do not inspect acceptance examples or other skills. Use only
these task inputs and normal local tools; install dependencies locally when
needed.

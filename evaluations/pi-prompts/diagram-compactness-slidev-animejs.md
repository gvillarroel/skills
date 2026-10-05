# Package handoff slide

Create one Slidev slide explaining an order handoff: Order → Pick → Pack →
Dispatch, with Pack → Pick when an item is missing. All six connections,
including a distinct Pick → Inventory check and Inventory → Pick return,
must remain traceable. Keep every named concept. Use motion to show a parcel
progressing and two deterministic click states without hiding the complete
mechanism in the export. The diagram will be read on an ordinary laptop.

Write exactly `deck/slides.md`, `deck/components/OrderHandoff.vue`,
`deck/package.json` and `deliverables/layout-review.md`. Build and inspect
the slide, replay and click states; record actual findings, stage dimensions
and verification commands in the review. Do not publish anything.

Treat `skills/slidev-animejs/` as read-only. Generated files belong outside
it. Do not inspect acceptance examples or other skills. Use only these task
inputs and normal local tools; install dependencies in this workspace.

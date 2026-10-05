# Review pipeline slides

Prepare a small Slidev deck at `deck/` for an internal engineering review.
Write exactly `deck/slides.md`, `deck/package.json`, and
`deliverables/style-review.md`, plus any supporting runtime files the deck
needs. Use the loaded skill's established default visual style throughout.
The package must declare Slidev and the default theme. The evaluator will
provide dependencies and build/render it, so do not install dependencies or
run a build in this authoring pass.

Make exactly three slides with one plain Mermaid block on each:

- A flowchart in which Intake feeds Review and Review feeds Publish. Label
  those relationships `checks` and `releases`.
- A sequence in which Client sends `request` to Service and Service returns
  `response` to Client.
- A class diagram in which Request has an `id: string` attribute, Service has
  `handle(): void`, and Request depends on Service with relationship `uses`.

I want to keep editing these diagrams as ordinary Mermaid text. Keep color
directives out of the blocks. The diagrams should share the deck's visual
language without additional styling work whenever I add a normal Mermaid
block. Keep labels, relationship captions and arrowheads readable. Briefly
record the chosen style and how the deck applies it in the review file.

Treat `skills/slidev-echarts/` as read-only. Keep generated files outside it.
Use only this loaded skill and normal local tools; do not read acceptance
examples, other skills, repository documents, or files outside the workspace.
Do not publish anything.

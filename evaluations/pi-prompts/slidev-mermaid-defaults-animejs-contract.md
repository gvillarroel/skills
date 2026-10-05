# Slidev Mermaid setup contract

Use the loaded skill's bundled Slidev diagram-style template to prepare a deck
at `deck/`. Keep the default colorset. Write `deck/package.json` and
`deck/slides.md`, and copy every required runtime setup/support file from the
template into the deck. The deck package must declare Slidev and the default
theme. Required setup outputs are `deck/setup/mermaid.ts`,
`deck/setup/mermaid-renderer.ts`, and `deck/diagram-style.mjs`.
Do not install dependencies or build the deck for this narrow contract;
the evaluator will supply dependencies and render it separately.

Create exactly three slides, one plain Mermaid block per slide:

1. A flowchart: Intake → Review → Publish, with relationship captions
   `checks` and `releases`.
2. A sequence: Client sends `request` to Service; Service returns `response`.
3. A class diagram: Request has `id: string`; Service has `handle(): void`;
   Request depends on Service with caption `uses`.

Use ordinary Mermaid grammar without per-diagram color directives, `classDef`,
`style`, `init`, or theme overrides. Keep each slide's diagram readable and
fully visible. Write `deliverables/style-review.md` identifying the selected
colorset and the setup files required for rendering. Do not claim browser
verification that has not occurred.

Treat `skills/slidev-animejs/` as read-only. Generated files belong outside it.
Do not read acceptance examples, other skills, repository documents, or files
outside this isolated workspace. Do not publish anything.

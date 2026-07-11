Use the loaded `d3-logo-design` skill to generate and validate one deterministic logo studio that exercises the example-ID and text-clearance contracts.

Work only from this prompt and the loaded skill at `skills/d3-logo-design/`. Treat the skill directory as read-only. Write only under `outputs/`. Do not inspect parent directories, sibling skills, repository documentation, evaluation files, acceptance examples, hidden context, or the network. Do not install packages or substitute tools.

Create these exact deliverables:

- `outputs/canopy-clearance-logo.html`
- `outputs/canopy-clearance-validation.json`

Use brand `CANOPY SIGNAL`, tagline `Field intelligence, naturally connected`, colorset1, pattern `d3-logo-animal-surface-mask`, texture `d3-logo-directional-fibers`, humanist font, and seed `947`. Preserve the full adjustable catalog of 30 patterns, 10 textures, and 30 finished compositions.

Run the bundled builder and static validator. The validator report must independently contain all of the following values:

- `ok: true`
- `patternCount: 30`
- `textureCount: 10`
- `compositionCount: 30`
- `exampleIdCount: 30`
- `initialPattern: "d3-logo-animal-surface-mask"`
- `initialExampleId: "animal-surface-mask"`
- `selectedColorset: "colorset1"`
- `textClearanceContractValid: true`
- `textOcclusionDefault: "prohibited"`
- `intentionalOcclusionCount: 3`
- `intentionalOmissionCount: 1`
- `maxDeclaredOcclusionRatio: 0.22`

Read the generated JSON and fail the task if any required field differs. Do not hand-author the validation report. At the end, report both exact output paths and the observed fields.

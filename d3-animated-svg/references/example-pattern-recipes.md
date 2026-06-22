# D3 Example Pattern Recipes

Use this reference when a good gallery example should become reusable skill knowledge, or when adapting an existing gallery pattern into a new SVG, video scene, or example card.

## Pattern Promotion Rule

Promote an example into skill guidance when it solves a recurring visual problem, not only when it looks good. Record the pattern as:

- **Pattern ID:** the stable `d3-pattern-*` ID exposed by the card and SVG.
- **Mechanic:** the cause/effect, comparison, sampling, capacity, extraction, or transformation the viewer should infer.
- **Data contract:** the minimal data shape needed to reproduce the pattern.
- **Geometry contract:** the layout, scales, rows, slots, or masks that preserve meaning.
- **Animation contract:** the SVG-native reveal, sweep, path draw, pulse, or replay rule.
- **Semantic color roles:** what each token color means in this pattern.
- **Verification hook:** card count, pattern ID, data attributes, pixel/screenshot check, or browser audit that proves the pattern survived adaptation.

Do not copy an entire renderer when only a helper or geometry idiom is reusable. Keep the semantic role and rewrite local data.

## Document Token Quality

Pattern IDs: `d3-pattern-document-token-quality`, `d3-pattern-document-token-quality-red`.

Use for document-quality explanations where the counting unit is text span length rather than row count or token count.

- Build paragraph-like lines from word rectangles with a fixed inter-word gap; spaces remain blank.
- Use neutral page rectangles, row rules, and borders. Encode correct spans with green, filler with gray, and wrong spans with yellow for caution or red for error/risk.
- Preserve requested ratios by accumulated word length. Do not approximate by number of words.
- Reveal row rules and word blocks in writing order: left to right within a row, then top to bottom through the page.
- Add `data-writing-index` and `data-writing-delay` attributes so a browser audit can verify ordering.
- Keep variants identical except for the semantic color of wrong spans.

## Document Extraction Buckets

Pattern ID: `d3-pattern-document-token-extraction-buckets`.

Use when a single source page needs to visibly split into calculated buckets.

- Start from one document page that already contains colored word blocks.
- Group extracted blocks by semantic role, such as filler, correct, and wrong.
- Move blocks into bucket regions with calculated totals, percentages, and block counts.
- Use subtle straight guide lanes from source to bucket. Avoid brace-like or decorative connectors.
- Keep the original page visible enough for the viewer to understand the extraction source.

## Image Partial Covers

Pattern ID: `d3-pattern-agent-loop-partial-covers`.

Use when the source material is an image or screenshot that should remain inspectable while D3 overlays reveal selected regions.

- Keep the raster asset local, small, and committed only if it is an intentional source asset, not a rendered output.
- Put the image in a clipped SVG group. Keep the image visible; overlays should explain selected regions, not erase the source.
- Use translucent covers, sweep lines, outlines, or masks that partially pass over meaningful regions.
- Scope clip IDs and overlay classes to the pattern ID.
- Verify that the page still works from `docs/` without local `node_modules`.

## Inline Bar Tables

Pattern ID: `d3-pattern-inline-bar-table`.

Use for compact current-data comparisons such as model pricing, latency, quality, or resource cost.

- Curate only current, directly comparable rows with verified values.
- Omit rows with missing values instead of drawing no-data rows.
- Scale each embedded bar against the largest visible value in its own metric column.
- Use solid bars when magnitude comparison is the message.
- Expose `data-metric-key`, `data-value`, `data-column-max`, and `data-bar-width` for ratio audits.

## Sketchy Overlay

Representative IDs: `d3-pattern-sketchy-beeswarm`, `d3-pattern-sketchy-streamgraph`, `d3-pattern-sketchy-treemap`, `d3-pattern-sketchy-line-chart`, `d3-pattern-sketchy-histogram`, `d3-pattern-sketchy-gemma-comparison`.

Use when a hand-rendered style is requested but the data geometry must stay faithful.

- Treat sketchiness as a mark-rendering overlay, not a different chart.
- Keep data positions, areas, ranks, and scales unchanged.
- Use seeded jitter, double strokes, rough rectangles/blobs, and optional hachures.
- Apply roughness to marks, axes, links, tables, and containers. Keep text crisp.
- Reuse repository palette tokens; do not introduce raw sketch colors.

## Model Execution Box

Pattern ID: `d3-pattern-deep-learning-model-execution`.

Use when a model or processor should read as active work without showing inputs, outputs, or extra explanatory labels.

- Draw a square model frame with a centered primary label or no label when narration carries the name.
- Put a small internal MLP inside the box as the secondary mechanism.
- Pulse nodes and links by layer with soft brand color.
- Avoid generic glow, external arrows, packets, and input/output tokens unless the concept requires them.
- In video scenes, adapt this into a shared helper so model boxes stay visually identical across beats.

## Token Roulette Sampler

Pattern ID: `d3-pattern-token-roulette-sampler`.

Use when weighted chance and final selection are the concept.

- Keep a probability-weighted wheel, fixed pointer, exterior ticks, and deterministic spin.
- Make the selected wedge land under the pointer in the final state.
- Use bars only when the user wants ranking instead of sampling.
- Keep a compact result mark only if it clarifies the selected token.

## Adaptation Checklist

Before committing an adapted pattern:

- Search `examples/d3-animated-svg/gallery.js` for the source pattern ID and render function.
- Copy only the required helpers, data shape, and geometry.
- Preserve semantic roles for shapes, colors, and motion.
- Add or update the stable `d3-pattern-*` ID if it becomes a gallery card.
- Run `npm run verify --prefix examples/d3-animated-svg` for gallery changes.
- For served or Pages behavior, verify through HTTP so CDN/local asset assumptions are tested.

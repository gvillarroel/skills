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

## Asymmetric Task Overlap

Pattern IDs: `d3-pattern-asymmetric-task-overlap`, `d3-pattern-asymmetric-task-overlap-saturated`.

Use when tasks, backlog items, risks, or work units belong to one scope, two shared scopes, or three-or-more overlapping scopes.

- Use fixed asymmetric circle geometry instead of a force simulation so overlap regions remain deterministic and auditable.
- Keep scope circles translucent and draw task leader lines, label backplates, labels, and dots above them.
- Expose circles as `.overlap-circle` with `data-set-id`.
- Expose tasks as `.task-dot` and `.task-label` with `data-task-id`, `data-memberships`, and `data-membership-count`.
- Encode membership count consistently: one scope in blue, two scopes in orange, and three-or-more scopes in red.
- For the default gallery fixture, validate `data-circle-count="9"`, `data-target-count="20"`, 9 circles, 20 task dots, and 20 task labels.
- For the saturated 100-task fixture, regenerate label positions with `scripts/layout_task_overlap_labels.py`, load the generated `task-overlap-layouts.js`, keep labels in external lanes outside the circle field, and validate `data-target-count="100"`, 100 task dots, 100 task labels, and `data-label-overlap-count="0"`.
- Stress the saturated fixture with mixed label lengths and font sizes. Validate `data-label-length-buckets`, at least three distinct `data-label-font-size` values, zero undersized `.task-label-bg` rectangles in both width and height, zero label overlaps against circles/dots/leaders/anchors, and a wide enough presentation for inspection.
- Use orthogonal gutter leaders for the saturated fixture. Color them by membership count, texture them with solid/dash/dot styles, draw white halos behind them, add small edge anchors, and expose `data-leader-route="orthogonal-gutter"` plus the zero non-label overlap counts on the root SVG.

## Venn Overlap Family

Pattern IDs: `d3-pattern-venn-three-circle`, `d3-pattern-venn-five-overlap`, `d3-pattern-venn-seven-overlap`, `d3-pattern-symmetric-three-circle-rosette`, `d3-pattern-symmetric-five-circle-rosette`, `d3-pattern-symmetric-seven-circle-flower`, `d3-pattern-asymmetric-three-circle-chain`, `d3-pattern-asymmetric-five-circle-cluster`, `d3-pattern-asymmetric-seven-circle-bridge`.

Use when a concept explainer needs reusable overlapping circles rather than a mathematically complete Venn diagram with every possible region.

- Use fixed circle geometry so the intended overlap story is deterministic and replayable.
- Expose every circle as `.venn-circle` with `data-set-id` and `data-set-code`.
- Expose the root SVG with `data-pattern-family="venn-overlap"`, `data-layout`, and `data-circle-count`.
- Keep the card ID, card `data-pattern-id`, and SVG `data-pattern-id` equal to the stable `d3-pattern-*` ID.
- Use three visual subfamilies: classic shared-center overlap, rotationally symmetric rosettes, and asymmetric bridge/cluster layouts.
- For asymmetric 7-circle bridge layouts, preserve the 3+1+3 structure: three circles in one block, one bridge circle, and three circles in the second block.
- Animate circle radius and fill-opacity with SVG animation nodes so replay works from the shared gallery button.

## Kanban Assignee Legend Modes

Pattern IDs: `d3-pattern-kanban-assignee-board`, `d3-pattern-kanban-assignee-virtual-legend`, `d3-pattern-kanban-assignee-distributed-legend`.

Use when a Kanban board needs one-title task cards, bottom-right two-letter assignee dots, and a people legend that can move to fit the available board geometry.

- Model people as `{ id, name, color }` and tasks as `{ col, title, assignees, expectedLines? }`; keep `id` to two letters for dot labels.
- Keep cards content-sized by measured title lines: one-line cards at the smallest height, two-line and three-line titles only adding the vertical space they need.
- Preserve square card and column edges. Do not add rounded corners when the board is meant to read as a dense operational surface.
- Use `legendMode: "top-row"` for maximum task-card width and a compact legend above the columns.
- Use `legendMode: "virtual-column"` when symmetry matters: shrink task columns if needed, add a same-height legend column, and expose legend chips with `data-legend-placement="virtual-column"`.
- Use `legendMode: "distributed-columns"` when spare vertical space exists in the columns: use one unified column height, reserve a footer band below the task stack, and place one legend chip per column with `data-legend-placement="column-footer"`.
- Validate `data-legend-mode`, task card heights, title line counts, 19 task cards, 5 task columns, 5 legend chips, bottom-right assignee dots, and no overlap between legend chips and task cards.

## Pen Label Optimizer

Pattern ID: `d3-pattern-pen-label-optimizer`.

Use when many labeled points crowd a pen/scatter-style view and direct labels saturate part of the drawing.

- Generate deterministic candidate rectangles around each point using several directions and offsets.
- Validate with mixed short, medium, and long labels. Measure SVG text widths before candidate generation when a browser is available; use conservative character-width estimates only as fallback.
- Score candidates by overlap area, outside-frame area, and leader-line distance.
- Compare simple radial placement, greedy candidate placement, force/collision relaxation, and simulated annealing.
- Use simulated annealing plus a final priority-ordered visibility pass when it keeps the most readable labels.
- Expose the SVG with `data-pattern-family="label-placement"`, `data-label-count`, `data-best-algorithm`, and per-algorithm readable counts.
- Draw only the readable subset as `.pen-label` groups and keep all source points visible as `.pen-label-point` marks. Expose label text, length, and measured width as data attributes for browser audits.
- Add leader lines from labels to points so displaced labels remain attributable.

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

## Parabolic Arcs For SDLC Tasks

Pattern ID: `d3-pattern-parabolic-arcs`.

Use when ordered SDLC phases or milestones need cross-phase dependency links, handoffs, or task flows. The baseline represents lifecycle order; arc height represents dependency strength, risk, effort, or coordination cost.

Recommended SDLC data contract:

```js
const phases = ["Discover", "Design", "Build", "Test", "Release", "Operate"];
const links = [
  { from: "Discover", to: "Build", label: "Backlog clarification", value: 72, kind: "dependency" },
  { from: "Design", to: "Test", label: "Acceptance criteria", value: 96, kind: "quality" },
  { from: "Build", to: "Release", label: "CI/CD packaging", value: 64, kind: "delivery" }
];
```

Geometry contract:

- Use a single horizontal baseline with one endpoint per SDLC phase.
- Use `d3.scalePoint().domain(phases).range([left, right])` so phase spacing remains stable.
- Draw each task link as a quadratic curve: `M x0,baseline Q mid,baseline - height x1,baseline`.
- Derive `height` from `value` with a bounded linear scale. Keep the shortest visible arc tall enough to distinguish from the baseline.
- If `from` is after `to`, draw the arc in the opposite direction but keep endpoints on the same baseline; do not reorder the data silently.
- Label phases on the baseline. Label tasks only when there is enough space; otherwise expose labels through `<title>` or a compact legend.

Semantic color roles:

- Use blue for dependencies or normal handoffs.
- Use green for quality, validation, or acceptance work.
- Use orange for release, delivery, or operational coordination.
- Use red only for high-risk or blocking work.
- Use purple for discovery, architecture, or cross-team planning.

Animation contract:

- Draw the baseline first.
- Draw arcs with a path-draw animation (`stroke-dasharray` and `stroke-dashoffset`) in task order or by descending `value`.
- Grow endpoint dots after arcs begin so the viewer sees the lifecycle anchors.
- Keep final path attributes complete; the SVG must still show all links after animation ends.

Minimal standalone renderer:

```js
const width = 760;
const height = 430;
const baseline = 330;
const left = 70;
const right = width - 70;
const x = d3.scalePoint().domain(phases).range([left, right]);
const heightFor = d3.scaleLinear()
  .domain(d3.extent(links, d => d.value))
  .range([56, 138]);

function arcPath(link) {
  const x0 = x(link.from);
  const x1 = x(link.to);
  const mid = (x0 + x1) / 2;
  return `M${x0},${baseline}Q${mid},${baseline - heightFor(link.value)} ${x1},${baseline}`;
}

const svg = d3.select("svg")
  .attr("viewBox", `0 0 ${width} ${height}`)
  .attr("data-pattern-id", "d3-pattern-parabolic-arcs")
  .attr("role", "img");

svg.append("line")
  .attr("x1", left - 18)
  .attr("x2", right + 18)
  .attr("y1", baseline)
  .attr("y2", baseline)
  .attr("stroke", palette.gray300)
  .attr("stroke-width", 2);

const paths = svg.append("g")
  .attr("fill", "none")
  .selectAll("path")
  .data(links)
  .join("path")
  .attr("d", arcPath)
  .attr("stroke", d => colorForKind[d.kind] ?? palette.blue)
  .attr("stroke-width", d => 2 + heightFor(d.value) / 55)
  .attr("stroke-linecap", "round")
  .attr("opacity", 0.9);

paths.each(function (_, index) {
  const length = this.getTotalLength();
  d3.select(this)
    .attr("stroke-dasharray", `${length} ${length}`)
    .attr("stroke-dashoffset", 0)
    .append("animate")
    .attr("attributeName", "stroke-dashoffset")
    .attr("from", length)
    .attr("to", 0)
    .attr("dur", "1.05s")
    .attr("begin", `${0.08 + index * 0.08}s`)
    .attr("fill", "freeze");
});
```

Verification hooks:

- The root SVG or card must expose `data-pattern-id="d3-pattern-parabolic-arcs"`.
- Every path should have a non-empty `d` attribute containing one `Q` command.
- Endpoint count should match the number of phases.
- Browser validation should confirm nonblank rendered pixels and at least one animated path.
- In an isolated skill-only test, copy only `d3-animated-svg/` plus a new empty workspace; do not read the gallery fixture.

## Adaptation Checklist

Before committing an adapted pattern:

- Search `references/pattern-index.md` for the source pattern ID and read the matching `references/patterns/<id>.md` file.
- Read the gallery fixture only when changing or validating the gallery fixture itself.
- Copy only the required helpers, data shape, and geometry.
- Preserve semantic roles for shapes, colors, and motion.
- Add or update the stable `d3-pattern-*` ID if it becomes a gallery card.
- Run `npm run verify --prefix .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg` for gallery changes.
- For served or Pages behavior, verify through HTTP so CDN/local asset assumptions are tested.

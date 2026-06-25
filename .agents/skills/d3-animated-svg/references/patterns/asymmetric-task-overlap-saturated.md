# Saturated Task Overlap

- **Pattern ID:** `d3-pattern-asymmetric-task-overlap-saturated`
- **Gallery source ID:** `asymmetric-task-overlap-saturated`
- **Family:** Set Overlap
- **Use when:** A dense task backlog needs to show 100 work items across nine asymmetric scopes while keeping every direct task label readable.
- **Renderer:** `renderAsymmetricTaskOverlapSaturated`
- **Layout generator:** `scripts/layout_task_overlap_labels.py`

## Reuse Contract

- Use exactly one root SVG with `data-pattern-id="d3-pattern-asymmetric-task-overlap-saturated"` when recreating this pattern outside the gallery.
- Keep the same nine-circle scope geometry as `d3-pattern-asymmetric-task-overlap`.
- Generate dense task dots and label positions with `scripts/layout_task_overlap_labels.py`; do not hand-place the 100-label fixture.
- Load the generated `task-overlap-layouts.js` before the gallery renderer when maintaining the fixture.
- Expose the root SVG with `data-target-count="100"`, `data-circle-count="9"`, `data-label-count="100"`, `data-label-algorithm="candidate-slot-anneal"`, `data-label-overlap-count="0"`, `data-label-length-buckets`, and `data-label-font-range`.
- In the gallery, mark this card as wide enough for inspection because 100 direct labels are not readable in a normal four-column thumbnail.

## Data Contract

The generated fixture uses 100 task records with:

- `id`: stable task ID, such as `T001`.
- `label`: mixed-length visible task label. The generated fixture includes 40 short labels, 35 medium labels, and 25 long labels such as `T092 runbook runbook`.
- `x`, `y`: dot position inside at least one scope circle.
- `memberships`: one, two, or three-or-more scope IDs computed from the circle geometry.
- `membershipCount`: numeric membership count for color encoding.
- `labelX`, `labelY`, `labelWidth`, `labelHeight`: final audited label box geometry.
- `labelFontSize`: per-task font size, currently 6.6, 7.2, 7.8, or 8.4 SVG units.
- `labelLengthBucket`: `short`, `medium`, or `long`.
- `labelTextPaddingX`: left text inset used by the renderer.
- `labelLane` and `labelSide`: lane assignment used by the label solver.

Default membership bucket targets:

- 36 single-scope tasks.
- 36 two-scope tasks.
- 28 three-or-more-scope tasks.

## Label Layout Method

The generator uses a deterministic candidate-slot layout:

1. Sample candidate task dots inside the nine fixed circles.
2. Select 100 dots while preserving membership bucket quotas and at least four single-scope examples per circle.
3. Generate mixed short, medium, and long label text with varied font sizes, then compute conservative label rectangles before placement.
4. Create non-overlapping left and right label lanes with fixed row spacing and enough lane width for the longest generated label.
5. Assign tasks to candidate label slots by cost: leader-line distance, preferred side, lane distance, and centrality.
6. Run deterministic pair-swap annealing to reduce total leader distance.
7. Audit every label rectangle pair; fail generation unless the overlap count is zero.

This approach is deliberately stricter than browser-time force relaxation: the gallery should render a known-valid final label layout instead of hoping a simulation converges on every replay.

## Geometry Contract

- Keep all scope circles in a 560 by 420 viewBox.
- Draw circles first with translucent token highlight fills.
- Draw thin neutral leader lines from every dot to the nearest label box edge.
- Draw small colored task dots above circles and below labels.
- Draw every label with an opaque white `.task-label-bg` rectangle sized from the generated `labelWidth`.
- If labels use the shared `.mark-label` class, set the generated `labelFontSize` as an inline style or a more-specific CSS rule so global gallery CSS cannot enlarge text beyond the audited rectangle.
- Encode membership count with dot color: one scope in blue, two scopes in orange, and three-or-more scopes in red.
- When publishing this dense fixture in a gallery card, use a wider card layout or equivalent presentation so the smallest rendered label height stays inspectable.

## Validation Hooks

- `.overlap-circle` count equals 9.
- `.task-dot` count equals 100.
- `.task-label` count equals 100.
- `.task-label-bg` count equals 100.
- `.task-leader` count equals 100.
- Every `.task-dot` has non-empty `data-task-id`, `data-memberships`, and numeric `data-membership-count`.
- At least one task has `data-membership-count="1"`, at least one has `"2"`, and at least one has `"3"` or greater.
- Root SVG exposes `data-label-length-buckets` with nonzero `short`, `medium`, and `long` counts.
- Root SVG exposes `data-label-font-range`, and `.task-label-group` exposes at least three distinct `data-label-font-size` values.
- Browser validation should compare every `.task-label-bg` bounding box and confirm zero overlaps.
- Browser validation should confirm each `.task-label-bg` is at least as wide and tall as its paired `.task-label` text.
- Browser validation should verify the gallery card is wide enough for the saturated case; the current desktop fixture renders the wide card at about 696 px with text heights between about 11 and 14 px, and mobile keeps a 680 px scrollable SVG instead of shrinking the labels.

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
- Expose the root SVG with `data-target-count="100"`, `data-circle-count="9"`, `data-label-count="100"`, `data-label-algorithm="candidate-slot-anneal"`, and `data-label-overlap-count="0"`.

## Data Contract

The generated fixture uses 100 task records with:

- `id` and `label`: compact visible task ID, such as `T001`.
- `x`, `y`: dot position inside at least one scope circle.
- `memberships`: one, two, or three-or-more scope IDs computed from the circle geometry.
- `membershipCount`: numeric membership count for color encoding.
- `labelX`, `labelY`, `labelWidth`, `labelHeight`: final audited label box geometry.
- `labelLane` and `labelSide`: lane assignment used by the label solver.

Default membership bucket targets:

- 36 single-scope tasks.
- 36 two-scope tasks.
- 28 three-or-more-scope tasks.

## Label Layout Method

The generator uses a deterministic candidate-slot layout:

1. Sample candidate task dots inside the nine fixed circles.
2. Select 100 dots while preserving membership bucket quotas and at least four single-scope examples per circle.
3. Create non-overlapping left and right label lanes with fixed row spacing.
4. Assign tasks to candidate label slots by cost: leader-line distance, preferred side, lane distance, and centrality.
5. Run deterministic pair-swap annealing to reduce total leader distance.
6. Audit every label rectangle pair; fail generation unless the overlap count is zero.

This approach is deliberately stricter than browser-time force relaxation: the gallery should render a known-valid final label layout instead of hoping a simulation converges on every replay.

## Geometry Contract

- Keep all scope circles in a 560 by 420 viewBox.
- Draw circles first with translucent token highlight fills.
- Draw thin neutral leader lines from every dot to the nearest label box edge.
- Draw small colored task dots above circles and below labels.
- Draw every label with an opaque white `.task-label-bg` rectangle sized from the generated `labelWidth`.
- If labels use the shared `.mark-label` class, set the generated `labelFontSize` as an inline style or a more-specific CSS rule so global gallery CSS cannot enlarge text beyond the audited rectangle.
- Encode membership count with dot color: one scope in blue, two scopes in orange, and three-or-more scopes in red.

## Validation Hooks

- `.overlap-circle` count equals 9.
- `.task-dot` count equals 100.
- `.task-label` count equals 100.
- `.task-label-bg` count equals 100.
- `.task-leader` count equals 100.
- Every `.task-dot` has non-empty `data-task-id`, `data-memberships`, and numeric `data-membership-count`.
- At least one task has `data-membership-count="1"`, at least one has `"2"`, and at least one has `"3"` or greater.
- Browser validation should compare every `.task-label-bg` bounding box and confirm zero overlaps.
- Browser validation should confirm each `.task-label-bg` is at least as wide as its paired `.task-label` text.

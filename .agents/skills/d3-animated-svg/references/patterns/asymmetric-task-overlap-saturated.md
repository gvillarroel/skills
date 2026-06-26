# Saturated Task Overlap

- **Pattern ID:** `d3-pattern-asymmetric-task-overlap-saturated`
- **Gallery source ID:** `asymmetric-task-overlap-saturated`
- **Family:** Set Overlap
- **Use when:** A dense task backlog needs to show 100 work items across nine asymmetric scopes while keeping every task label readable outside the circle field.
- **Renderer:** `renderAsymmetricTaskOverlapSaturated`
- **Layout generator:** `scripts/layout_task_overlap_labels.py`

## Reuse Contract

- Use exactly one root SVG with `data-pattern-id="d3-pattern-asymmetric-task-overlap-saturated"` when recreating this pattern outside the gallery.
- Keep the same nine-circle scope geometry as `d3-pattern-asymmetric-task-overlap`, shifted into the central field so external labels can sit outside every circle.
- Generate dense task dots and label positions with `scripts/layout_task_overlap_labels.py`; do not hand-place the 100-label fixture.
- Load the generated `task-overlap-layouts.js` before the gallery renderer when maintaining the fixture.
- Expose the root SVG with `data-target-count="100"`, `data-circle-count="9"`, `data-label-count="100"`, `data-label-algorithm="external-lane-gutter-anneal"`, `data-label-overlap-count="0"`, `data-label-circle-overlap-count="0"`, `data-label-dot-overlap-count="0"`, `data-label-placement="external-lanes"`, `data-leader-route="direct"`, `data-leader-color-count`, `data-leader-crossing-count`, `data-same-color-leader-crossing-count`, `data-label-length-buckets`, and `data-label-font-range`.
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
- `labelEdgeX` and `labelEdgeY`: direct leader-line endpoint on the inner edge of the label box.
- `leaderColorKey`, `leaderColorIndex`, and `leaderConflictDegree`: deterministic line-color assignment metadata from the direct-leader crossing graph.

Default membership bucket targets:

- 36 single-scope tasks.
- 36 two-scope tasks.
- 28 three-or-more-scope tasks.

## Label Layout Method

The generator uses a deterministic external-lane layout:

1. Sample candidate task dots inside the nine fixed circles.
2. Select 100 dots while preserving membership bucket quotas and at least four single-scope examples per circle.
3. Generate mixed short, medium, and long label text with varied font sizes, then compute conservative label rectangles before placement.
4. Create four external left and right label lanes with fixed row spacing, alternating lane offsets, and enough lane width for the longest generated label.
5. Assign tasks to candidate label slots by cost: leader-line distance, preferred side, lane distance, and centrality.
6. Run deterministic pair-swap annealing to reduce total leader distance.
7. Build direct leader segments from each task dot to the nearest edge of its label box.
8. Build a crossing graph for those direct leaders, then assign six token colors greedily with local repaint passes to minimize same-color crossings.
9. Audit every label rectangle pair plus label intersections against circles and dots; fail generation unless those label overlaps are zero.

This approach is deliberately stricter than browser-time force relaxation: the gallery should render a known-valid final label layout instead of hoping a simulation converges on every replay.

## Geometry Contract

- Use an 880 by 450 viewBox for the saturated fixture. Keep circles in the central field and reserve external lanes for labels.
- Draw circles first with translucent token highlight fills.
- Draw direct solid `.task-leader` lines from every dot to the nearest label box edge, using semitransparent strokes so the dense leader field remains readable.
- Color leader lines from the generated crossing-graph assignment, not from membership count. Use the six token color keys emitted by the layout fixture, and prefer assignments that avoid same-color crossings.
- Draw a subtle semitransparent white `.task-leader-halo` behind each colored line so direct leaders remain visible over circles and dots without creating heavy opaque routes.
- Draw small colored task dots above circles and below labels.
- Draw every label with an opaque white `.task-label-bg` rectangle sized from the generated `labelWidth`. Do not add lateral color accents inside labels for this dense fixture.
- Do not draw an outer gray frame stroke around the SVG background; keep the inspection area open outside the labels.
- If labels use the shared `.mark-label` class, set the generated `labelFontSize` as an inline style or a more-specific CSS rule so global gallery CSS cannot enlarge text beyond the audited rectangle.
- Encode membership count with dot color: one scope in blue, two scopes in orange, and three-or-more scopes in red.
- When publishing this dense fixture in a gallery card, use a wider card layout or equivalent presentation so the smallest rendered label height stays inspectable.

## Validation Hooks

- `.overlap-circle` count equals 9.
- `.task-dot` count equals 100.
- `.task-label` count equals 100.
- `.task-label-bg` count equals 100.
- `.task-leader` and `.task-leader-halo` counts each equal 100.
- `.task-leader-anchor` and `.task-label-accent` counts each equal 0.
- Every `.task-dot` has non-empty `data-task-id`, `data-memberships`, and numeric `data-membership-count`.
- At least one task has `data-membership-count="1"`, at least one has `"2"`, and at least one has `"3"` or greater.
- Root SVG exposes `data-label-length-buckets` with nonzero `short`, `medium`, and `long` counts.
- Root SVG exposes `data-label-font-range`, and `.task-label-group` exposes at least three distinct `data-label-font-size` values.
- Root SVG exposes `data-label-placement="external-lanes"` and `data-leader-route="direct"`.
- Root SVG exposes zero counts for `data-label-circle-overlap-count`, `data-label-dot-overlap-count`, and `data-label-nonlabel-overlap-count`.
- Root SVG exposes direct-leader crossing metadata. For the current fixture, `data-leader-crossing-count="39"` and `data-same-color-leader-crossing-count="0"`.
- Browser validation should confirm `.task-leader` exposes exactly one `data-leader-style` value: `solid`.
- Browser validation should confirm at least five leader colors are present and the browser-computed same-color crossing count matches `data-same-color-leader-crossing-count`.
- Browser validation should compare every `.task-label-bg` bounding box and confirm zero overlaps.
- Browser validation should confirm `.task-label-bg` rectangles do not overlap scope circles or task dots. Direct leaders may pass behind opaque label backgrounds; track that as `data-label-leader-underpass-count`, not as a label collision.
- Browser validation should confirm each `.task-label-bg` is at least as wide and tall as its paired `.task-label` text.
- Browser validation should verify the gallery card is wide enough for the saturated case; the current fixture renders the wide SVG at 880 by 450 px in mobile scroll mode and about 882 by 451 px on desktop, with browser-rendered label text heights around 9 to 11 px and no undersized label backgrounds.
- Use `scripts/audit_saturated_task_overlap.py --expect-clean` for the targeted browser audit, and repeat with `--viewport 390x900` before publishing.

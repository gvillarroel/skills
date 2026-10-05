# Compact conceptual graphs and trees

## Contents

- [Simple native conceptual graphs](#simple-native-conceptual-graphs)
- [Other conceptual layouts](#other-conceptual-layouts)

Use this pass when authoring connected concepts. Animation-only work retains
the supplied static geometry. Quantitative plots, Sankey widths, geographic
routes and allocation partitions keep their measurement contracts.

## Simple native conceptual graphs

For a small workflow or ranked conceptual graph, use
`scripts/render_concept_graph.py` before trying handwritten fixed-coordinate
SSR. It renders native ECharts 6.1.0 nodes, arrows and captions, protects full
envelopes, uses a 1:1 native view transform, and computes the canvas from the
content. It installs the pinned ECharts dependency in the current task
workspace when needed. It does not import acceptance examples.

Write a task-owned JSON input:

```json
{
  "title": "Sample workflow",
  "nodes": [
    {"id": "input", "label": "Complete incoming material label"},
    {"id": "review", "label": "Independent review"},
    {"id": "archive", "label": "Archive"}
  ],
  "edges": [
    {"source": "input", "target": "review", "label": "Verify"},
    {"source": "review", "target": "archive"},
    {"source": "review", "target": "input", "kind": "return", "label": "Retest"}
  ]
}
```

Run from the task workspace, using its exact required output paths:

```text
uv run --script skills/echarts-animated-svg/scripts/render_concept_graph.py source/graph.json --svg deliverables/graph.static.svg --option source/graph-option.json --review deliverables/graph-geometry.json
uv run --script skills/echarts-animated-svg/scripts/render_svg_preview.py deliverables/graph.static.svg --output deliverables/graph-preview.png
```

Open the PNG and record actual findings. Then animate and validate the native
SVG through the normal graph profile. Geometry JSON contains node, caption
and head envelopes, ranks/routes, natural/explicit dimensions and repeated
arrow-inset findings; it is an automated aid, not a visual certificate.

For a tighter candidate, use `--probe` with fresh comparison SVG/option paths
and a separate review JSON:

```text
uv run --script skills/echarts-animated-svg/scripts/render_concept_graph.py comparison/tighter.json --probe --svg comparison/tighter.svg --option comparison/tighter-option.json --review comparison/tighter-review.json
```

Read `accepted` in the comparison JSON before previewing or adopting it.
An expected layout-gate rejection returns `accepted: false`, its `gate` and
`reason`, exit zero, and no candidate SVG/option. Keep the prior passing
layout and restore the failed local gap. Invalid input, parser/dependency
failures and unexpected exceptions still fail the command. Accepted probes
produce normal candidate artifacts for Chromium review. Render final exact
deliverables without `--probe`; its readability gates remain hard failures.
Do not run the preview on a rejected candidate or mask failing commands.

The input supports 1–40 nodes and up to 80 edges. Preserve full labels; wrapping
never abbreviates them. Default node/caption fonts are 18/14 px and heads are
14 px; requested sizes have readable minima of 16/14/14 px. `colorset` defaults
to `colorset1`. Omit `width`/`height` for content sizing; explicit dimensions
center the same unscaled content and are rejected when too small. Supply
integer `rank` for every node to control columns, or let non-return DAG edges
compute ranks. Mark cycle-closing edges `kind: "return"`. For another clear
arrangement, supply finite `x`/`y` for every node and optional edge `curveness`.
Self loops, overlap, routes through unrelated nodes and overlapping captions
fail without delivered SVGs. Split complex networks or use a specialist
layout instead of deleting relationships or shrinking labels to evade a gate.

When reusing the JSON option in a live native component, initialize at the
review's dimensions. After `setOption` and native layout settling, call
`insetGraphArrowRoutes(chart, 3)` followed by
`settleConceptGraphCaptions(chart)` from the bundled
`assets/templates/concept-graph-labels.mjs`. The latter places existing native
Line captions on their visible shaft, rather than the portion hidden inside
the source node. Repeat both after layout updates. Its caption adapter is
specific to the helper's 1:1 view transform; inspect resized/click states.

## Other conceptual layouts

Freeze the required nodes/relations, final readable font and stroke/head
sizes, explicit dimensions and any required orientation. Optimize occupied
bounds and route length only among layouts that preserve these constraints.

1. Measure complete labels; derive node dimensions with modest internal
   clearance. Choose ranks or a branch arrangement from topology, not from
   equal divisions of the available canvas. Compare horizontal/vertical
   placement or reorder independent siblings when it saves space safely.
2. Make adjacent ranks only far enough apart for visible shafts, complete
   heads and any edge captions. Reserve distinct return/parallel lanes and
   separate ports where shared segments would hide relation identity.
   Route around unrelated labels and nodes; a crossing is not a junction.
3. Account for native graph fitting: `layout: 'none'` still uses a view
   transform. Smaller source-coordinate differences alone may be stretched
   back across the full chart. Set a content-sized SVG and series layout
   bounds, or center a smaller series inside explicitly fixed dimensions.
   Inspect the actual emitted node positions, not just source coordinates.
4. Apply the [native arrow clearance](arrow-contrast.md) after each layout
   change and inspect at final display size. Compare a tighter candidate with
   the baseline using occupied width/height and traceability. Reject hidden
   heads, unreadable paint, label overlap/clipping, lost endpoint identity,
   merged unrelated routes or insufficient motion space. Restore the local
   gap that failed; do not solve it by shrinking type or deleting facts.
5. Keep the smallest passing candidate. Stop when the remaining gaps protect
   readability/routing or another concrete local reduction fails. Record the
   accepted change and protected clearances in the task's review notes.

Use the same final type size and display scale when comparing candidates.
Inspect replay, focus/selection, reduced motion and exported SVG as applicable.
Do not claim a global packing optimum or use a universal occupancy percentage.

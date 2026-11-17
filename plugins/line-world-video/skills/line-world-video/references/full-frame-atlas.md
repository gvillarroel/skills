# Full-frame partitions and a visual comparison atlas

Read this for several simultaneous concepts, a broad renderer comparison, or
sections that must divide the entire presentation surface.

## Contents

- [Build the comparison starter](#build-the-comparison-starter)
- [Partition the entire frame](#partition-the-entire-frame)
- [Choose complementary views](#choose-complementary-views)
- [Keep one clock and identity map](#keep-one-clock-and-identity-map)
- [Integrate native Mermaid safely](#integrate-native-mermaid-safely)
- [Acceptance](#acceptance)
- [Primary references](#primary-references)

## Build the comparison starter

```text
uv run --script <skill-root>/scripts/line_world.py init --layout atlas --project film
uv run --script <skill-root>/scripts/line_world.py build --project film
uv run --script <skill-root>/scripts/render_line_world.py --project film --audit-only --capture browser --report audit.json
```

The atlas has sixteen scenes, twenty native Mermaid families, twenty-six D3
forms, four world columns, shared entity focus and no automatic visible titles.
Read the generated `coverage.json` for the exact inventory and editorial pairing
assessments. Counts describe this template, not all possible D3 constructions or
all Mermaid releases. Use the ordinary linked-data starter for new before/after
datasets. The atlas is an illustrative comparison fixture: its bundled native
diagrams and D3 records must agree. To replace its data, adapt the explicit
contract in the copied `scripts/atlas_story.py` and regenerate the corresponding
native diagrams; never silently mix new numbers with old SVGs.

## Partition the entire frame

In `story.json → scenePlan`, each panel has a producer, kind and normalized
`rect: [x,y,width,height]`. Coordinates describe the complete frame. Two equal
columns are `[0,0,.5,1]` and `[.5,0,.5,1]`; two rows use full width and half height.
A top strip and two lower views can use `[0,0,1,.35]`, `[0,.35,.5,.65]` and
`[.5,.35,.5,.65]`. Unequal divisions are valid when their area covers exactly one
frame. `build` rejects gaps, overlap, nonfinite coordinates and out-of-frame
panels. An area sum alone cannot detect an overlap cancelling a gap.

Keep these boundaries logical; do not draw decorative separators. Put breathing room inside each
section; do not add an unused outer title band. Fit the actual content to the
section's aspect ratio. Use wide strips for sequence, Gantt, timeline or Git
history; tall sections work for state chains, block chains and compact schemas.
If a native diagram becomes too small, change the partition or its direction
before shrinking text. Keep values and axes readable at the intended delivery
size. Let an overview show small diagrams only after the full-size reading holds.

## Choose complementary views

| Question | Useful pairing | Review risk |
| --- | --- | --- |
| What happens, and how long does it take? | Mermaid process/state + D3 events, intervals or histories | A legal transition is not a measured frequency. |
| Which record explains the mark? | Source table + aligned bars, dumbbells or histories | Bind both highlights by semantic ID; share the quantitative domain. |
| Which branch contains the largest share? | Mindmap/tree + one treemap or circle pack | Tree structure has no area metric; packing and treemap areas do. |
| Where do quantities go? | Sankey + adjacency matrix | Chord is a dense overview alternative; do not imply conservation unless present. |
| What happened around the change? | Timeline/Gantt + lines or intervals | A bump chart encodes rank; a streamgraph encodes thickness, not a common baseline. |
| What are the tradeoffs? | Quadrant + parallel coordinates or boxplot | Do not invent comparable units or normalize without saying so. |
| Where is the system? | Architecture + projected real coordinates | A graticule is orientation, not a fabricated land boundary. |
| How do samples relate in space? | Voronoi + Delaunay; density and x projection as secondary views | Preserve the same seeded samples and explain dimensional reduction. |

Treat pie + donut and mindmap + radial tree as comparison controls, not automatic
production recommendations. Prefer one view that answers the question and one
that adds a different fact. The atlas deliberately exposes such alternatives
for review. These are editorial judgments, not measured viewer-study outcomes.

## Keep one clock and identity map

Edit each scene's `seconds` and `camera.transitionSeconds`; edit the final hold
through `camera.overviewSeconds`. `build` derives all beat starts, ends, world
cells, duration and frame count. Allow at least five seconds of reading after
each camera move. A subset or reordered `scenePlan` is supported; keep scene IDs
unique. Keep `presentation.contextLabels` empty unless short contextual words
were explicitly requested. Preview speed does not change the exported timing.

Use `data-entity-id` for linked focus. Keep red as a small point, stroke or label
effect; preserve white surfaces and quiet geometry. Use colorset2 only when an
actual simultaneous category distinction needs it, with `paletteReason` and an
explicit category mapping in the copied scene. Selecting a palette must never
introduce unmotivated decorative hues.

## Integrate native Mermaid safely

Bundle actual producer SVGs, source `.mmd` files and a receipt. The builder embeds
the local SVGs with a unique namespace for IDs, CSS, markers, paint servers and
ARIA references. Keep the original geometry. Disallow scripts, external URLs
and `foreignObject`; render journey with `journey.textPlacement: old` and set
top-level and flowchart `htmlLabels: false`.

Some pinned Mermaid grammars do not accept `accTitle`/`accDescr` reliably. The
bundled receipt identifies five fixtures with invisible SVG metadata repair.
Their source comments retain the intended metadata, and their final SVGs carry
referenced title and description elements. Do not claim native directive support
or complete accessibility from this repair. Add no visible title to compensate.

## Acceptance

Inspect every scene at its reading hold and the final overview. Verify complete
partitions, useful chart occupancy, readable labels, zero panel overflow, unique
SVG IDs, local references, actual Mermaid geometry, real D3 APIs, exact palette,
shared facts and repeatable seeking. The browser audit records small labels as
warnings so a visual reviewer can assess native diagrams; resolve unreadable
labels before delivery. Decode the final movie independently and compare real
frames with the reviewed composition. Preserve the coverage, timing, sources
and pairing review alongside the MP4.

## Primary references

- [D3 hierarchy layouts](https://d3js.org/d3-hierarchy)
- [D3 Delaunay and Voronoi](https://d3js.org/d3-delaunay)
- [D3 API inventory](https://d3js.org/api)
- [Mermaid syntax inventory](https://mermaid.js.org/intro/)
- [Mermaid Sankey syntax](https://mermaid.js.org/syntax/sankey.html)
- [Mermaid radar syntax](https://mermaid.js.org/syntax/radar.html)
- [Mermaid treemap syntax](https://mermaid.js.org/syntax/treemap.html)

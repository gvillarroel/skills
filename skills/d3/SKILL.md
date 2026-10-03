---
name: d3
description: "Creates, animates, inspects, recomposes, and validates D3-powered HTML and SVG visuals. Use for custom charts, simulations, linked views, visual audits, parametric logos, textures, and portable SVG that need data-driven geometry, joins, layouts, or transitions."
---

# D3

## Mandatory first command

For a complete interactive logo studio or a browsable logo catalog, first run
`python "<d3-skill>/scripts/build_logo_studio.py" --help`. Build with that script,
passing the requested output, brand, tagline, colorset, and optional pattern
flags. Read `references/compact-composition.md` for page sizing. Validate the
HTML with `validate_logo_artifact.py` and `check_self_contained_html.py`; inspect
the live preview in a browser. Check extended colors against an exported
settled SVG: the studio HTML creates its colored marks at runtime, so its
static source cannot satisfy `--require-extended`. Do not assemble the studio by reading and
substituting its large engine or catalogs. A single standalone logo follows
the contract-builder route below.

For a bar chart, horizontal lollipop, node-link network, flow spine, orbit logo, or radial-wedge logo, your first command after reading this file MUST be:

```text
python "<d3-skill>/scripts/build_contract_artifact.py" --help
```

Replace `<d3-skill>` with the exact directory containing this `SKILL.md`; do not guess `.agents` or probe alternate paths. Use `python` when available; on `command not found`, immediately rerun the same command with `python3`. Do not plan, inspect the runtime, or write a deliverable before this command succeeds. A missing interpreter alias never permits hand-authoring: use the builder for the final files, and never replace or post-edit a supported form. Correct flags and rerun. The wedge builder already satisfies colorset2 accent, warning/orange, success/green, and special/purple groups.

For an evaluation or composition audit, your first command after reading this file MUST instead be `python "<d3-skill>/scripts/build_evaluation_report.py" --help` with the same exact-directory rule. Use its outputs without post-editing.

For an editable KPI/service dashboard, first run `python "<d3-skill>/scripts/create_d3_svg_starter.py" --help`, then read `references/user-artifact-workflow.md`. Generate the `operational-dashboard` starter and edit its output data. This route already provides compact neutral panels, active-colorset metadata, local runtime files, and the KPI/table layout.

Run dependency-declaring helpers such as `render_d3_svg.py` and
`dither_d3_output.py` with `uv run --script`, including their `--help` calls.
Their uv metadata provides Pillow and Playwright in a clean isolated workspace.
Use the dependency-free Python first commands above for their named routes.

## Preserve the public contract

- Treat every requested path, ID, class, attribute, label, value, unit, order, count, relationship, route, colorset, and pattern ID as immutable API data.
- Use `colorset1` by default. Use `colorset2` only for an explicit extended, expanded, multicolor, or full-color request.
- Prefer compact boxes and neutral surfaces: 6 px vertical / 10 px horizontal node padding, 12 px panel padding, and 8 px UI gaps. Read `references/compact-composition.md` when sizing nodes, panels, or controls; preserve readable text and data geometry.
- In colorset1, use grays, black, white, and deliberate red emphasis first. Pink is a last-resort category after usable red/neutral distinctions are exhausted, never an automatic secondary color, selection fill, or focus ring.
- Read visible paint from `assets/palettes/colorsets.json`; use exact lowercase six-digit tokens and opacity, never arbitrary colors, functional color syntax, or raw D3 chromatic scales.
- Named standalone builders accept `--colorset` and default to colorset1 through the bundled `colorset_adapter.py`; use the flag for colorset2. Validate their generated HTML and settled SVG against the selected contract. Immutable source image bytes may retain source colors; every authored overlay and control must follow the active contract.
- Preserve supplied data and deterministic geometry. Seed layouts, pre-tick simulations, and make the settled frame truthful.
- Give each SVG a stable `viewBox`, `<title>`, `<desc>`, semantic groups, readable labels, stable IDs, and active-colorset metadata.
- Bundle runtime and data for offline HTML. Portable SVG must not depend on JavaScript or a network after extraction.

## Map builder flags exactly

Map every public acceptance literal to a flag. Use `--kind flow` with `--svg-pattern-id` when the decision variant differs from SVG pattern metadata, and repeat `--attribute`, `--flow-node`, `--link`, and `--link-value` in contract order. Keep titles generic or include only a leading prefix of ordered data labels; never mention a later label before intervening labels. Use `--kind logo --logo-mode wedges` for radial wedges; its colorset2 sequence already covers visible accent, warning/orange, success/green, and special/purple groups.

For `check_visual_contract.py`, express exact cardinality as `--require-class CLASS:COUNT` and repeat `--ordered-text` only for the data tokens whose rendered occurrences must follow that order. Quote every complete CLI value that contains whitespace, such as `--require-attribute "viewBox=0 0 960 540"`; never issue a known-invalid command as a probe. For logos emitted by `build_contract_artifact.py`, use the self-contained, palette, render, and visual-contract checks; `validate_logo_artifact.py` is only for full logo-studio outputs.

Use `--require-id ID` without a count suffix. `--require-class` takes a class name, never a CSS selector: for a default four-node flow use `--require-class flow-node:4 --require-class node:4 --require-class link:3`. Only use another class when you supplied its builder flag; do not guess a `flow-link` alias.

During skill maintenance, extend and test the builder when a required supported contract cannot be expressed.

For `build_evaluation_report.py`, pass each `requiredTerms` value unchanged with repeated `--required-term`; keep composition, implementation-contract, and validation findings separate. Do not post-edit supported reports. The visual checker uses `--require-text` instead.

## Preflight and workflow

1. List exact outputs and decision fields; route and colorset; literal data order; IDs, classes, attributes, and counts; motion, interaction, accessibility, offline, and final-state requirements.
2. Choose D3 when custom geometry, joins, scales, projections, simulation, interaction, or animated transformation is material. Prefer Mermaid for notation-first diagrams and ECharts for conventional dashboards.
3. Choose the narrow route below and read only its linked references.
4. Build with D3 joins, scales, layouts, shape generators, projections, or transitions. Use documented APIs such as `Math.hypot` and `d3.easeCubicOut`.
5. Validate independently after the last write, render the settled state, inspect it at the intended size, fix every failure, and rerun.

## Progressive-disclosure routes

- Form selection and implementation: `references/visualization-type-index.md`, `references/layout-patterns.md`, and `references/pattern-selection-contracts.md`.
- Named reusable pattern: select its directly linked recipe below and read it in full. Use `references/pattern-routing.md` when the family is unclear, or `references/pattern-index.md` when a canonical ID or legacy alias needs lookup. For exact counts, also read `references/cardinality-generalization.md`.
- Speculative decoding: read `references/patterns/speculative-decoding.md` and use `scripts/build_speculative_decoding.py` for a draft sequence, accepted prefix, rejected tail and target continuation; it supports changed tokens, counts, dimensions and optional alternates. Use its bundled `verify_speculative_decoding.py` browser command for Replay, SVG parity, reduced motion and the inspection PNG. Check HTML controls against HTML and SVG geometry against SVG.
- Kinetic or deconstructed typography: `references/patterns/kinetic-glyph-mosaic.md`; use `scripts/build_kinetic_type.py` for ordinary-looking text that reveals moving tile, line, dot, or hybrid glyph components. Follow that route's HTML-specific validation commands; do not substitute the generic settled-SVG contract check or look for acceptance fixtures in a runtime bundle.
- Offline or animated output: `references/self-contained-output.md` and `references/animation-patterns.md`.
- Composition audit or conversion: `references/evaluation-rubric.md` and `references/recomposition-recipes.md`.
- Logo, identity, or texture: `references/pattern-catalog.md`, `references/mathematical-patterns.md`, and `references/palette-contract.md`; add `references/texture-catalog.md` only for texture selection.
- Source-SVG reconstruction: `references/svg-replication.md`.
- Dithering: `references/patterns/surface-stable-dither.md`.
- Output ownership or maintenance: `references/user-artifact-workflow.md` and `references/maintenance-validation.md`.

## Palette standard

- `colorset1` standard roles: background `#f7f7f7`, surface `#ffffff`, ink `#333e48`, dark ink `#1c1c1c`, primary `#9e1b32`, dark primary `#6d1222`, accent `#e8002a`, muted `#828282`, line `#cfcfcf`, quiet `#e7e7e7`. The legacy `accentSoft` token `#ffccd5` is available only for a justified last-resort category or an explicit pink request; use `quiet` for subtle fills.
- `colorset2` extended adds blue `#007298`, dark blue `#004d66`, orange `#e77204`, green `#45842a`, purple `#652f6c`, and yellow `#f1c319`. Use additions for meaningful categories or states.
- Embed an unchanged offline runtime inside `<script id="d3-runtime">` only when hand-authoring an unsupported form. Never reveal an author-CSS-hidden mark solely through a presentation attribute.

## Mandatory validation

The commands below apply to single-file HTML with static SVG marks. For a logo
studio, use its route above and check the palette on the rendered SVG. For an editable starter directory,
follow the render/paint checks in `references/user-artifact-workflow.md`; its
local `data.js`, stylesheet, and vendor script are part of the offline output.
For speculative decoding, follow the direct recipe's validation commands; its
bundled browser verifier supplies the settled PNG, Replay and reduced-motion
checks without a separate custom replay harness.

```text
python <d3-skill>/scripts/check_self_contained_html.py <artifact.html>
python <d3-skill>/scripts/check_palette_contract.py <artifact.html> --colorset colorset1
python <d3-skill>/scripts/check_palette_contract.py <artifact.html> --colorset colorset2 --require-extended
uv run --script <d3-skill>/scripts/render_d3_svg.py <artifact.html> --output <scratch/settled.svg> --screenshot <scratch/preview.png> --wait-ms <final-frame-ms> --viewport <WIDTHxHEIGHT>
python <d3-skill>/scripts/check_visual_contract.py <settled.svg> <exact-contract-flags>
```

Run only the palette command matching the active colorset. Choose a wait beyond the last animation; the renderer writes both the captured SVG and inspection PNG in one call. It has declared Playwright dependencies: always invoke it with `uv run --script`, never bare `python` or a new Playwright import probe. It can reuse installed Edge/Chrome on Windows when managed Chromium is absent. Put every scratch output inside an owned directory in the writable task workspace, outside deliverables; do not use host `/tmp` paths or guess an image-conversion executable. A missing tool is not a pass; use an equivalent available browser/parser check. Use route-specific validators for logos, recompositions, galleries, or replication.

Complete the rendered visual review before reporting success: open the inspection PNG or browser preview at the requested size and check every title, caption, token and branch label against the SVG boundary. A parser or render-success result cannot establish readability. Correct overflow in the authored layout, render again, and rerun affected validators. Once those required checks and the visual review pass, stop issuing verification commands and report the result. Avoid duplicate ad hoc parsers for conditions already covered by the bundled validators; raw first-occurrence logic can disagree with rendered accessibility text.

## Acceptance gate

- Exact non-empty outputs exist outside the skill; decision metadata and all public literals match.
- Form, quantitative geometry, values, units, order, entities, links, and visible palette influence match the source contract.
- Standalone output is offline; SVG metadata, accessibility, stable IDs, and deterministic settled state are present.
- Browser output is nonblank, readable, unclipped, collision-free, replay-safe, and faithful at its final frame.
- Every applicable self-contained, palette, rendered-structure, and route-specific check passed after the last edit.

Before changing bundled patterns, scripts, examples, galleries, palettes, or composition sheets, read `references/maintenance-validation.md` and preserve published IDs.

## Additional reference routes

Read only the resource matching the task.

- [Command Reference](references/command-reference.md).
- [Composition Audit](references/composition-audit.md).
- [Composition Contract](references/composition-contract.md).
- [D3 Composition Variants](references/composition-variants.md).
- [D3 Example Pattern Recipes](references/example-pattern-recipes.md).
- [D3 Animated SVG Gallery Patterns](references/gallery-patterns.md).
- [Overlap Pattern Contracts](references/overlap-pattern-contracts.md).
- [Research Foundations](references/research-foundations.md).
- [Shared Renderer Helpers](references/shared-renderer-helpers.md).
- [Text Clearance Contract](references/text-clearance-contract.md).
- [D3 Visual Tokens](references/visual-tokens.md).
- [Distribution And Density](references/visualizations/distribution-density.md).
- [Flow And Path Choreography](references/visualizations/flow-path-choreography.md).
- [Focus And Context Interaction](references/visualizations/focus-context-interaction.md).
- [Force Networks](references/visualizations/force-networks.md).
- [Geospatial SVG](references/visualizations/geospatial-svg.md).
- [Packing And Proximity](references/visualizations/packing-proximity.md).
- [Radial Hierarchies](references/visualizations/radial-hierarchies.md).
- [Temporal Playback](references/visualizations/temporal-playback.md).

## Direct recipe links

Select the matching recipe and read it in full.

- [adjacency matrix](references/patterns/adjacency-matrix.md).
- [agent loop overlay](references/patterns/agent-loop-overlay.md).
- [ai line writing](references/patterns/ai-line-writing.md).
- [airport voronoi](references/patterns/airport-voronoi.md).
- [alluvial](references/patterns/alluvial.md).
- [antimeridian cutting](references/patterns/antimeridian-cutting.md).
- [arc diagram](references/patterns/arc-diagram.md).
- [area missing data](references/patterns/area-missing-data.md).
- [attention arc decoding](references/patterns/attention-arc-decoding.md).
- [attention routing](references/patterns/attention-routing.md).
- [attention tiles](references/patterns/attention-tiles.md).
- [bar race](references/patterns/bar-race.md).
- [beeswarm](references/patterns/beeswarm.md).
- [binary classifier labeled](references/patterns/binary-classifier-labeled.md).
- [binary classifier](references/patterns/binary-classifier.md).
- [bivariate choropleth](references/patterns/bivariate-choropleth.md).
- [bollinger bands](references/patterns/bollinger-bands.md).
- [bowtie barriers](references/patterns/bowtie-barriers.md).
- [bubble map](references/patterns/bubble-map.md).
- [bulkhead isolation](references/patterns/bulkhead-isolation.md).
- [burtin antibiotics](references/patterns/burtin-antibiotics.md).
- [cache stampede](references/patterns/cache-stampede.md).
- [calendar year](references/patterns/calendar-year.md).
- [candlestick](references/patterns/candlestick.md).
- [category burst](references/patterns/category-burst.md).
- [chord](references/patterns/chord.md).
- [circle pack](references/patterns/circle-pack.md).
- [circuit breaker](references/patterns/circuit-breaker.md).
- [circuit signal traces](references/patterns/circuit-signal-traces.md).
- [circular bar](references/patterns/circular-bar.md).
- [cluster dendrogram](references/patterns/cluster-dendrogram.md).
- [cluster hulls](references/patterns/cluster-hulls.md).
- [colorbrewer splines](references/patterns/colorbrewer-splines.md).
- [column profile](references/patterns/column-profile.md).
- [context window fill](references/patterns/context-window-fill.md).
- [context window matrix](references/patterns/context-window-matrix.md).
- [correlogram](references/patterns/correlogram.md).
- [creature stippling](references/patterns/creature-stippling.md).
- [critical chain buffer](references/patterns/critical-chain-buffer.md).
- [critical path](references/patterns/critical-path.md).
- [data grid](references/patterns/data-grid.md).
- [delaunay mesh](references/patterns/delaunay-mesh.md).
- [density radial collection](references/patterns/density-radial-collection.md).
- [dependency blast radius](references/patterns/dependency-blast-radius.md).
- [difference chart](references/patterns/difference-chart.md).
- [directed chord](references/patterns/directed-chord.md).
- [diverging stack](references/patterns/diverging-stack.md).
- [document token bins](references/patterns/document-token-bins.md).
- [document token errors](references/patterns/document-token-errors.md).
- [document token quality](references/patterns/document-token-quality.md).
- [dorling](references/patterns/dorling.md).
- [drag collisions](references/patterns/drag-collisions.md).
- [edge bundling](references/patterns/edge-bundling.md).
- [embedding neighborhood](references/patterns/embedding-neighborhood.md).
- [er schema](references/patterns/er-schema.md).
- [event cascade](references/patterns/event-cascade.md).
- [fault tree](references/patterns/fault-tree.md).
- [flashattention blocks](references/patterns/flashattention-blocks.md).
- [flow tokens](references/patterns/flow-tokens.md).
- [flowchart dag](references/patterns/flowchart-dag.md).
- [focus context](references/patterns/focus-context.md).
- [force network](references/patterns/force-network.md).
- [forecast fan](references/patterns/forecast-fan.md).
- [freehand trace](references/patterns/freehand-trace.md).
- [gantt rollout](references/patterns/gantt-rollout.md).
- [gemma comparison](references/patterns/gemma-comparison.md).
- [geo route](references/patterns/geo-route.md).
- [geofence join](references/patterns/geofence-join.md).
- [git graph](references/patterns/git-graph.md).
- [hexbin map](references/patterns/hexbin-map.md).
- [hierarchical bars](references/patterns/hierarchical-bars.md).
- [horizon](references/patterns/horizon.md).
- [icicle](references/patterns/icicle.md).
- [idempotency guard](references/patterns/idempotency-guard.md).
- [image histogram](references/patterns/image-histogram.md).
- [incident escalation](references/patterns/incident-escalation.md).
- [index chart](references/patterns/index-chart.md).
- [inline bar table](references/patterns/inline-bar-table.md).
- [interaction motion collection](references/patterns/interaction-motion-collection.md).
- [isoline terrain](references/patterns/isoline-terrain.md).
- [kanban assignees](references/patterns/kanban-assignees.md).
- [kanban board](references/patterns/kanban-board.md).
- [kanban legend column](references/patterns/kanban-legend-column.md).
- [kanban legend footer](references/patterns/kanban-legend-footer.md).
- [kv cache growth](references/patterns/kv-cache-growth.md).
- [lasso selection](references/patterns/lasso-selection.md).
- [line cursor](references/patterns/line-cursor.md).
- [line missing data](references/patterns/line-missing-data.md).
- [logit lens rank bump](references/patterns/logit-lens-rank-bump.md).
- [lora rank update](references/patterns/lora-rank-update.md).
- [marey trains](references/patterns/marey-trains.md).
- [marimekko](references/patterns/marimekko.md).
- [mirrored beeswarm](references/patterns/mirrored-beeswarm.md).
- [mlp execution](references/patterns/mlp-execution.md).
- [mlp internals](references/patterns/mlp-internals.md).
- [mlp simple](references/patterns/mlp-simple.md).
- [moe router capacity](references/patterns/moe-router-capacity.md).
- [moon phases](references/patterns/moon-phases.md).
- [multi head attention merge](references/patterns/multi-head-attention-merge.md).
- [nature geometry](references/patterns/nature-geometry.md).
- [non contiguous cartogram](references/patterns/non-contiguous-cartogram.md).
- [nucleus sampling](references/patterns/nucleus-sampling.md).
- [occlusion labels](references/patterns/occlusion-labels.md).
- [organic growth](references/patterns/organic-growth.md).
- [orthographic shading](references/patterns/orthographic-shading.md).
- [overlap 7 flower](references/patterns/overlap-7-flower.md).
- [overlap collection](references/patterns/overlap-collection.md).
- [paged kv cache](references/patterns/paged-kv-cache.md).
- [parallel sets](references/patterns/parallel-sets.md).
- [pen curve study](references/patterns/pen-curve-study.md).
- [pen label optimizer](references/patterns/pen-label-optimizer.md).
- [pie data switch](references/patterns/pie-data-switch.md).
- [pivot heat table](references/patterns/pivot-heat-table.md).
- [point cloud](references/patterns/point-cloud.md).
- [polar area](references/patterns/polar-area.md).
- [polygon clipping](references/patterns/polygon-clipping.md).
- [population pyramid](references/patterns/population-pyramid.md).
- [process control loop](references/patterns/process-control-loop.md).
- [projection comparison](references/patterns/projection-comparison.md).
- [projection switch](references/patterns/projection-switch.md).
- [qkv projection flow](references/patterns/qkv-projection-flow.md).
- [quadtree partition](references/patterns/quadtree-partition.md).
- [quadtree search](references/patterns/quadtree-search.md).
- [quantitative collection](references/patterns/quantitative-collection.md).
- [queue backpressure](references/patterns/queue-backpressure.md).
- [radar](references/patterns/radar.md).
- [radial hierarchy](references/patterns/radial-hierarchy.md).
- [radial stacked bars](references/patterns/radial-stacked-bars.md).
- [rank table](references/patterns/rank-table.md).
- [rectbin](references/patterns/rectbin.md).
- [replication failover](references/patterns/replication-failover.md).
- [residual rmsnorm stream](references/patterns/residual-rmsnorm-stream.md).
- [rope rotation](references/patterns/rope-rotation.md).
- [rotating dot rings](references/patterns/rotating-dot-rings.md).
- [sankey](references/patterns/sankey.md).
- [scaled dot product attention](references/patterns/scaled-dot-product-attention.md).
- [scatterplot matrix](references/patterns/scatterplot-matrix.md).
- [scatterplot tour](references/patterns/scatterplot-tour.md).
- [science geometry collection](references/patterns/science-geometry-collection.md).
- [sequence lifelines](references/patterns/sequence-lifelines.md).
- [sized donut multiples](references/patterns/sized-donut-multiples.md).
- [sketchy beeswarm](references/patterns/sketchy-beeswarm.md).
- [sketchy gemma comparison](references/patterns/sketchy-gemma-comparison.md).
- [sketchy histogram](references/patterns/sketchy-histogram.md).
- [sketchy line chart](references/patterns/sketchy-line-chart.md).
- [sketchy streamgraph](references/patterns/sketchy-streamgraph.md).
- [sketchy treemap](references/patterns/sketchy-treemap.md).
- [slo burn rate](references/patterns/slo-burn-rate.md).
- [smooth zoom](references/patterns/smooth-zoom.md).
- [solar terminator](references/patterns/solar-terminator.md).
- [sparkline table](references/patterns/sparkline-table.md).
- [speculative decoding](references/patterns/speculative-decoding.md).
- [spike map](references/patterns/spike-map.md).
- [spiral timeline](references/patterns/spiral-timeline.md).
- [stacked grouped bars](references/patterns/stacked-grouped-bars.md).
- [star map](references/patterns/star-map.md).
- [state machine](references/patterns/state-machine.md).
- [statistical collection](references/patterns/statistical-collection.md).
- [streamgraph](references/patterns/streamgraph.md).
- [sunburst](references/patterns/sunburst.md).
- [swiglu feed forward](references/patterns/swiglu-feed-forward.md).
- [symbol glyphs](references/patterns/symbol-glyphs.md).
- [tangled tree levels](references/patterns/tangled-tree-levels.md).
- [tangled tree](references/patterns/tangled-tree.md).
- [tanglegram](references/patterns/tanglegram.md).
- [task overlap dense](references/patterns/task-overlap-dense.md).
- [task overlap](references/patterns/task-overlap.md).
- [temperature softmax](references/patterns/temperature-softmax.md).
- [temporal network](references/patterns/temporal-network.md).
- [ternary](references/patterns/ternary.md).
- [tidy tree](references/patterns/tidy-tree.md).
- [tile choropleth](references/patterns/tile-choropleth.md).
- [tiled matmul](references/patterns/tiled-matmul.md).
- [token bucket](references/patterns/token-bucket.md).
- [token roulette](references/patterns/token-roulette.md).
- [token sampler](references/patterns/token-sampler.md).
- [treemap](references/patterns/treemap.md).
- [user journey](references/patterns/user-journey.md).
- [vaccine impact](references/patterns/vaccine-impact.md).
- [voronoi stippling](references/patterns/voronoi-stippling.md).
- [voronoi](references/patterns/voronoi.md).
- [waterfall](references/patterns/waterfall.md).
- [web load timeline](references/patterns/web-load-timeline.md).
- [word cloud](references/patterns/word-cloud.md).
- [world tour](references/patterns/world-tour.md).
- [zoom to bounds](references/patterns/zoom-to-bounds.md).

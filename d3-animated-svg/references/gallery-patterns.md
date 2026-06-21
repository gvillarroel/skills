# D3 Animated SVG Gallery Patterns

Use this reference when extending a gallery of multiple D3-generated SVG examples or building a browsable examples page.

## Card Contract

- Keep one data record per example with `id`, `kicker`, `title`, `copy`, and `render`.
- Use the `id` for the card `data-example`, the SVG `id`, and the per-card replay target.
- Keep card headers compact and stable. Do not let replay controls resize the visualization frame.
- Keep every SVG self-contained with a unique `title`, `desc`, and scoped IDs for definitions.

## Replay Contract

- Render each card by clearing only its own SVG and rebuilding its marks.
- Store a card-level render pass such as `data-render-pass` so verification can confirm isolated replay.
- Attach one delegated click listener to the gallery container and route through `data-replay`.
- After rebuilding a card, reset the target SVG timeline with `pauseAnimations()`, `setCurrentTime(0)`, and `unpauseAnimations()` so SMIL `begin` offsets replay visibly after the page has been open for a while.
- Replaying one card should not rebuild other cards, duplicate event listeners, or accumulate stale nodes.
- Keep the final visual state encoded in attributes, not only in transient D3 transition state.

## Animation Coverage

Use varied animation patterns across a large gallery:

- staged mark reveal for discrete marks and matrices
- path drawing for lines, routes, meshes, and trajectories
- radial reveal for arcs, partitions, polar views, and circular bars
- flow fade or motion tokens for ribbons, alluvial bands, Sankey paths, and routes
- force or collision settle for networks, beeswarms, Dorling maps, and packed clusters
- threshold or sweep reveal for density fields, choropleths, contours, and heatmaps
- focus/context interaction for brush, zoom, lasso, and drilldown demos
- cross-link reveal for tangled trees, tanglegrams, and comparable hierarchies
- text-weight and stipple reveals for word clouds, sampled fields, and Voronoi stippling
- projection or zoom-to-bounds transitions for analytical state changes
- projection comparison, vector-field, and Tissot distortion reveals for geospatial geometry
- diagnostic reveals for Q-Q plots, moving averages, Bollinger bands, scatterplot matrices, and threshold-colored lines
- cyclic geometry reveals for polar clocks, moon phases, solar terminators, star maps, and epicyclic paths
- SVG-native morphs for shape tweens, path tweens, arc tweens, and animated numeric labels
- brush and zoom explanations for custom handles, snapping, ordinal ranges, and linked detail windows
- geographic symbol and service-area maps such as spike maps, bubble maps, non-contiguous cartograms, projected hexbins, and Voronoi catchments
- scientific or raster-derived views such as H-R diagrams, solar paths, image histograms, and terrain or volcano contours
- hybrid matrix and inspection views such as correlograms with diagonal histograms, rectangular 2D histograms, line cursors, and pie/data-switch arc tweens
- D3-only diagram counterparts for Mermaid-like forms when custom geometry or animation is the goal, such as flowchart DAGs, sequence lifelines, state machines, entity relationship schemas, Gantt rollouts, Git graphs, Kanban boards, and user journeys
- SVG data table forms such as typed row grids, inline bar tables, pivot heat tables, sortable ranking tables, sparkline rows, and column-profile tables where rows, cells, sort movement, and embedded mini-marks are animated with D3 joins
- context-window and capacity matrices such as waffle grids where each unit represents a token budget, allocation slot, or finite resource cell
- token-owned prompt transformations where each text group becomes a numeric ID and then occupies an ordered square context-window slot
- LLM concept micro-visualizations for next-token probability, probability roulette sampling, temperature, nucleus sampling, attention routing, embedding neighborhoods, key-value cache growth, tiled attention matrices, QKV projection flow, LoRA rank updates, FlashAttention block movement, MoE capacity routing, speculative decoding verification, RoPE rotation, tiled matrix accumulation, scaled dot-product attention, multi-head merge, logit-lens rank trajectories, residual normalization, SwiGLU gating, and paged KV cache allocation
- precision pen-rendered line art where a single persistent pen mark traverses hidden connector paths while visible strokes reveal pressure-modulated ribbons, not rough freehand jitter
- projection edge-case and scientific catalog views such as antimeridian cutting, adaptive sampling, satellite footprints, and exoplanet orbit catalogs

Avoid adding examples that only restyle an existing chart. Prefer a new D3 module, geometry generator, interaction model, or data story.

## Example Reuse Patterns

Before creating a custom D3 component for a concept explainer, search the gallery for the closest existing geometry and adapt it. Preserve the example's core data semantics when they are the reason it works: weighted areas should remain weighted areas, ordered slots should remain ordered slots, and sampled outcomes should land in deterministic selected states.

For token probability selection, prefer the `Token Roulette Sampler` pattern when the requested metaphor is roulette or chance-weighted sampling. Keep a probability-weighted pie or wheel, a fixed pointer, exterior tick marks, deterministic spin timing, and a final state where the selected wedge lands under the pointer. Use a compact legend or result mark only when it clarifies the wheel's mapping; do not replace the roulette with bars plus a scanning arrow unless the user asks for a ranking chart instead.

## Visual Critique Pass

For large galleries, review every card visually before delivery. Generate screenshots or contact sheets, then critique composition by example or by small batches. Focus on issues that automated checks cannot prove:

- token palette alignment and avoidance of raw D3 interpolator colors in repository-owned examples
- readable text, white text halos, and dark neutral label color on light surfaces
- axis, grid, link, and map scaffold contrast that supports the marks without competing
- semantic color hierarchy, with red reserved for risk, change, selected states, or highest-alert values
- legends or direct labels where color encodes categories or density
- dark/light label choices on heatmaps, choropleths, treemaps, and saturated fills
- replay-safe fixes that survive clearing and rebuilding one card at a time

Integrate repeated findings through shared CSS, token ramps, and a gallery-level post-render polish function before adding chart-specific tweaks. Use chart-specific code when the color encodes data meaning, such as heatmaps, density bins, vaccine-impact ramps, bivariate keys, missing-data annotations, or selected/focus states.

## Verification

For gallery updates, verify:

- the expected card count matches `body[data-example-count]`
- package or CI commands pin `--expected` to the intended card count instead of relying only on the page-generated count
- every card contains exactly one SVG and one replay control
- every SVG has positive dimensions, nontrivial element count, and animation nodes
- replay works on multiple sampled cards and updates only the targeted card render pass
- sampled replay resets the SVG timeline near zero and the timeline advances after the click
- repeated replay does not leave duplicated marks or empty SVGs
- desktop and mobile screenshots preserve readable card headers, replay controls, labels, and SVG framing

Use the gallery verifier for deterministic checks:

```powershell
uv run --script d3-animated-svg/scripts/verify_d3_gallery.py examples/d3-animated-svg/index.html --screenshot output/d3-animated-svg/gallery.png --wait-ms 2200
uv run --script d3-animated-svg/scripts/verify_d3_gallery.py http://127.0.0.1:4177/index.html --viewport 390x900 --screenshot output/d3-animated-svg/gallery-mobile.png --wait-ms 2200
```

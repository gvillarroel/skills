---
name: d3-animated-svg
description: "Create, animate, troubleshoot, and validate D3-generated SVG visualizations that complement Mermaid diagrams. Use when Codex needs bespoke data-driven SVG geometry or animated visuals Mermaid does not cover well: simulations, dense hierarchies, edge bundling, chords, parallel sets, Voronoi/Delaunay, quadtrees, geospatial projections, cartograms, spike/bubble/hexbin maps, contours, calendar and vaccine-style heatmaps, word clouds, beeswarms, population pyramids, statistical diagnostics, uncertainty views, temporal playback, missing-data series, scientific charts, raster/image analysis, shape/path/arc/text tweens, brush/zoom/selection views, custom glyphs, ternary plots, or animated annotations."
---

# D3 Animated SVG

## Core Workflow

1. Decide whether the request is a diagram or a custom visualization. Use Mermaid for conventional flowcharts, sequence diagrams, class diagrams, ER diagrams, state diagrams, requirements, Gantt timelines, and simple Mermaid-native charts. Use D3 when the visualization needs custom geometry, simulation, projections, dense quantitative encodings, or animated marks Mermaid cannot express cleanly.
2. Choose the output contract before coding:
   - For live interactive artifacts, deliver HTML with D3 transitions, zoom, drag, filters, or tooltips.
   - For portable animated SVG, use D3 to compute geometry and write inline SVG, CSS, or SMIL animation. Do not rely on D3 transitions to survive extraction into a standalone SVG.
3. Before hand-rolling a micro-visualization, search the existing D3 examples/gallery for the closest geometry, interaction, or sampling pattern and adapt that component's data semantics first.
4. Keep data deterministic. Inline small data, load local files for larger data, and seed or pre-tick force layouts so exported geometry is reproducible.
5. Build the SVG with a stable `viewBox`, `title`, `desc`, semantic groups, stable IDs/classes, and fixed dimensions. Ensure the final frame is a faithful data state, not only an animation midpoint.
6. Apply the visual token system before capture. Keep text neutral and readable, use white halos when labels sit on marks, reserve red for change/risk/emphasis, and prefer tokenized quantize/threshold ramps over raw D3 interpolator palettes when the output belongs to this repository.
   - When a sketchy rendering is requested, treat sketchiness as a reusable mark-rendering overlay for any D3 pattern, including scorecards, comparison cards, tables, model diagrams, and statistical charts. Preserve data geometry; roughen marks, axes, links, and containers with seeded jitter, double strokes, and optional hachures while keeping text crisp.
7. Use `scripts/render_d3_svg.py` to open D3 HTML in Chromium, wait for the generated SVG, export the SVG markup, and optionally capture a screenshot for visual QA.
8. Verify that the SVG is nonblank, text fits, labels remain readable, animation starts from a meaningful state, and the final frame matches the intended values.

## Progressive Disclosure Map

- `references/visualization-type-index.md`: read when choosing a D3 visualization form or when the user asks for alternatives to Mermaid.
- `references/layout-patterns.md`: read when implementing D3 layouts, scales, projections, hierarchy, force simulations, or data joins.
- `references/animation-patterns.md`: read when making portable SVG animation, staged reveals, path drawing, motion tokens, morphs, or final-frame verification.
- `references/gallery-patterns.md`: read when extending a multi-example gallery with card conventions, per-card replay controls, and gallery-level verification.
- `references/example-pattern-recipes.md`: read when turning a successful gallery example into a reusable implementation pattern or adapting one of the approved pattern IDs.
- `references/svg-replication.md`: read when replicating, extracting, or adapting a D3-generated SVG from this repository, especially when the user asks for exact colors, portable animation code, or a reusable implementation recipe.

## Common Commands

Install and verify the included deterministic D3 fixture:

```powershell
npm install --prefix examples/d3-animated-svg
npm run verify --prefix examples/d3-animated-svg
```

Capture any D3-generated SVG from an HTML page:

```powershell
uv run --script d3-animated-svg/scripts/render_d3_svg.py examples/d3-animated-svg/force-beeswarm.html -o output/d3-animated-svg/force-beeswarm.svg --screenshot output/d3-animated-svg/force-beeswarm.png --wait-ms 1800
```

Use a custom SVG selector:

```powershell
uv run --script d3-animated-svg/scripts/render_d3_svg.py scene.html --selector "svg#viz" -o output/scene.svg --wait-ms 2500
```

## Complementarity Rules

- Prefer Mermaid when the source notation is the value and the diagram type is supported.
- Prefer Slidev ECharts for standard dashboard charts inside Slidev decks when ECharts already provides the needed chart type.
- Prefer D3 when geometry is the message: simulated placement, custom marks, physical motion, projections, nested or bundled relationships, density fields, or animated transformations between data states.
- Do not recreate a Mermaid diagram in D3 just to animate it. If the input is Mermaid, use `mermaid-animated-svg`.
- Do not export an SVG that depends on external JavaScript. Extracted SVG should contain its own geometry and animation rules.

## Visual Tokens

Read `../ANIMATED_VISUAL_TOKENS.md` before creating or updating examples, galleries, or exported SVG fixtures. Use Open Sans for text, Material Symbols Rounded for system icons, and the documented brand palette for editable D3 marks, UI controls, replay states, and page surfaces.

## Pattern Promotion

When a gallery card or standalone SVG pattern proves reusable, update `references/example-pattern-recipes.md` before finishing. Capture the stable `d3-pattern-*` ID, trigger, data contract, geometry contract, animation contract, semantic color roles, and validation hooks. For patterns expected to work in isolated skill-only workspaces, include a minimal standalone implementation recipe that does not depend on `examples/`.

## Validation

After changing this skill, its references, scripts, or examples, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing the capture script or example fixture, also run the smoke command from `Common Commands` and inspect the generated screenshot.

When changing the examples gallery, verify that all cards render, each card has exactly one replay control, sampled replay buttons restart only their target card, repeated replay does not duplicate marks or listeners, and desktop plus mobile screenshots keep text and controls readable.

For large galleries, create contact sheets and run an explicit visual critique pass by example or batch before final validation. Integrate the critique centrally when possible: shared token ramps, label halos, axis/grid contrast, and replay-safe post-render polish should handle recurring issues before adding one-off chart fixes.

---
name: d3-animated-svg
description: "Create, animate, troubleshoot, and validate D3-generated SVG visualizations that complement Mermaid diagrams. Use when Codex needs bespoke data-driven SVG geometry or animated visuals Mermaid does not cover well: simulations, dense hierarchies, edge bundling, chords, parallel sets, asymmetric set-overlap task maps, Voronoi/Delaunay, quadtrees, geospatial projections, cartograms, spike/bubble/hexbin maps, contours, calendar and vaccine-style heatmaps, word clouds, beeswarms, population pyramids, statistical diagnostics, uncertainty views, temporal playback, missing-data series, scientific charts, raster/image analysis, shape/path/arc/text tweens, brush/zoom/selection views, custom glyphs, ternary plots, or animated annotations."
---

# D3 Animated SVG

## Core Workflow

1. Decide whether the request is a diagram or a custom visualization. Use Mermaid for conventional flowcharts, sequence diagrams, class diagrams, ER diagrams, state diagrams, requirements, Gantt timelines, and simple Mermaid-native charts. Use D3 when the visualization needs custom geometry, simulation, projections, dense quantitative encodings, or animated marks Mermaid cannot express cleanly.
2. Choose the output contract before coding:
   - For live interactive artifacts, deliver HTML with D3 transitions, zoom, drag, filters, or tooltips.
   - For portable animated SVG, use D3 to compute geometry and write inline SVG, CSS, or SMIL animation. Do not rely on D3 transitions to survive extraction into a standalone SVG.
   - If the request names an exact output file or path, write that exact path. Do not derive a replacement filename from a `d3-pattern-*` ID, title, or chart family.
   - For self-contained, standalone, offline, or portable HTML deliverables, do not use CDN scripts, remote fonts, or empty SVGs populated by runtime JavaScript. Read `references/self-contained-output.md`, start from `assets/templates/self-contained-animated-svg.html` when useful, and validate with `scripts/check_self_contained_html.py`.
   - If the request provides JSON, YAML, a table, or another structured output contract with IDs, counts, classes, or data values, treat that structure as the source of truth. Copy numeric counts exactly; do not replace them with nicer, denser, rounded, or approximate values.
3. Before hand-rolling a micro-visualization, use the pattern references:
   - If the request asks for fewer/more elements, small/medium/large variants, scaling, cardinality, exact `svg#id` hooks, or exact mark counts, read `references/cardinality-generalization.md` before coding. Extract every requested output ID, data count, mark class, and validation hook first; do not substitute a different chart family. For supported pattern families, prefer `scripts/build_cardinality_variants.ts` over hand-written SVG; in that generator path, do not read `references/pattern-index.md` or per-pattern references unless the request adds requirements the generator cannot satisfy.
   - If the request asks for overlapping scopes, shared task membership, asymmetric circles, or tasks that belong to one/two/three-or-more sets, use `d3-pattern-asymmetric-task-overlap` and read `references/patterns/asymmetric-task-overlap.md`.
   - If the request asks for a Kanban board with assignee dots, people legends, or alternate legend placement, use `d3-pattern-kanban-assignee-board` and read `references/patterns/kanban-assignee-board.md`. Choose `legendMode: "top-row"`, `"virtual-column"`, or `"distributed-columns"` before coding so the data, dimensions, and validation hooks stay consistent.
   - If the request names exact `d3-pattern-*` IDs and the cardinality generator path does not apply, extract the complete unique set, strip each prefix, and read every matching `references/patterns/<id>.md` before coding. Do not start implementation after reading only the first pattern.
   - If the request asks for a closest gallery pattern without naming an exact ID, search `references/pattern-index.md`, choose one pattern, and then read only that matching file under `references/patterns/`.
   - Do not read the gallery fixture for normal pattern generation; use the gallery only when maintaining that fixture.
4. Keep data deterministic. Inline small data, load local files for larger data, and seed or pre-tick force layouts so exported geometry is reproducible.
5. Build the SVG with a stable `viewBox`, `title`, `desc`, semantic groups, stable IDs/classes, and fixed dimensions. Ensure the final frame is a faithful data state, not only an animation midpoint.
6. Apply the visual token system before capture. Keep text neutral and readable, use white halos when labels sit on marks, reserve red for change/risk/emphasis, and prefer tokenized quantize/threshold ramps over raw D3 interpolator palettes when the output belongs to this repository.
   - When a sketchy rendering is requested, treat sketchiness as a reusable mark-rendering overlay for any D3 pattern, including scorecards, comparison cards, tables, model diagrams, and statistical charts. Preserve data geometry; roughen marks, axes, links, and containers with seeded jitter, double strokes, and optional hachures while keeping text crisp.
7. Use `scripts/render_d3_svg.py` to open D3 HTML in Chromium, wait for the generated SVG, export the SVG markup, and optionally capture a screenshot for visual QA.
8. Verify that the SVG is nonblank, text fits, labels remain readable, moving marks do not cross readable text, animation starts from a meaningful state, and the final frame matches the intended values.
   - When the request asks for dynamic symmetry, point verification, balance, or compositional improvement, read `references/composition-audit.md` and run `scripts/audit_dynamic_symmetry.py` on the current SVG or selected object.

## Progressive Disclosure Map

- `references/visualization-type-index.md`: read when choosing a D3 visualization form or when the user asks for alternatives to Mermaid.
- `references/layout-patterns.md`: read when implementing D3 layouts, scales, projections, hierarchy, force simulations, or data joins.
- `references/animation-patterns.md`: read when making portable SVG animation, staged reveals, path drawing, motion tokens, morphs, or final-frame verification.
- `references/gallery-patterns.md`: read when extending a multi-example gallery with card conventions, per-card replay controls, and gallery-level verification.
- `references/composition-audit.md`: read when analyzing point placement, dynamic symmetry, armature alignment, balance, or composition quality for an SVG pattern.
- `references/composition-variants.md`: read when maintaining the composition sheets or adding curated `d3-composition-*` SVG preview variants.
- `references/cardinality-generalization.md`: read when adapting a pattern to fewer or more elements, generating small/medium/large variants, or satisfying exact SVG IDs, mark classes, and target counts.
- `references/example-pattern-recipes.md`: read when turning a successful gallery example into a reusable implementation pattern or adapting one of the approved pattern IDs.
- `references/pattern-index.md`: search/read when the user asks to adapt a gallery pattern without naming an exact ID. If the user names an exact `d3-pattern-*`, skip the index and read `references/patterns/<pattern-id-without-prefix>.md` directly.
- `references/shared-renderer-helpers.md`: read only when a per-pattern reference excerpt names shared helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`.
- `references/svg-replication.md`: read when replicating, extracting, or adapting a D3-generated SVG from this repository, especially when the user asks for exact colors, portable animation code, or a reusable implementation recipe.
- `references/self-contained-output.md`: read when the user asks for a self-contained, standalone, offline, or portable HTML/SVG artifact.

## Common Commands

Capture a D3-generated SVG from a local HTML page:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/render_d3_svg.py scene.html -o projects/<project-id>/artifacts/svgs/scene.svg --screenshot projects/<project-id>/artifacts/screenshots/scene.png --wait-ms 1800
```

Use a custom SVG selector:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/render_d3_svg.py scene.html --selector "svg#viz" -o projects/<project-id>/artifacts/svgs/scene.svg --wait-ms 2500
```

Check that a generated HTML artifact is self-contained:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/check_self_contained_html.py artifact.html
```

Check an HTML artifact against explicit SVG IDs, metadata, and mark counts:

```powershell
node .agents/skills/d3-animated-svg/scripts/check_svg_contract.ts artifact.html svg-contract.json
```

Audit SVG points against a dynamic-symmetry composition armature:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/audit_dynamic_symmetry.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/index.html --selector "svg#asymmetric-task-overlap-saturated" --output projects/d3-animated-svg-validation/artifacts/data/asymmetric-task-overlap-saturated-dynamic-symmetry.json
```

Verify the composition variant sheets expose curated SVG variants with stable composition IDs:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_composition_sheets.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/composition-sheets.html --min-variants 180 --expected-reviewed-patterns 218 --required-variant d3-composition-radial-rosette-force-network --expect-clean
```

Generate small/medium/large force-network or beeswarm variants from a JSON spec:

```powershell
node .agents/skills/d3-animated-svg/scripts/build_cardinality_variants.ts variants.json artifact.html
```

Generate the collision-audited saturated task-overlap label layout:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/layout_task_overlap_labels.py
```

Audit the saturated task-overlap labels, direct leader colors, and background fit in Chromium:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/audit_saturated_task_overlap.py --expect-clean
```

## Complementarity Rules

- Prefer Mermaid when the source notation is the value and the diagram type is supported.
- Prefer Slidev ECharts for standard dashboard charts inside Slidev decks when ECharts already provides the needed chart type.
- Prefer D3 when geometry is the message: simulated placement, custom marks, physical motion, projections, nested or bundled relationships, density fields, or animated transformations between data states.
- Do not recreate a Mermaid diagram in D3 just to animate it. If the input is Mermaid, use `mermaid-animated-svg`.
- Do not export an SVG that depends on external JavaScript. Extracted SVG should contain its own geometry and animation rules.

## Visual Tokens

Read `references/visual-tokens.md` before creating or updating examples, galleries, or exported SVG fixtures. Use Open Sans for text, Material Symbols Rounded for system icons, and the documented brand palette for editable D3 marks, UI controls, replay states, and page surfaces.

## Pattern Promotion

This section is for skill maintenance, not normal artifact generation. Do not read `references/example-pattern-recipes.md` or update skill resources while creating a user artifact unless the user explicitly asks to promote, add, or maintain a reusable pattern.

When a gallery card or standalone SVG pattern proves reusable during skill maintenance, update `references/example-pattern-recipes.md` before finishing. Capture the stable `d3-pattern-*` ID, trigger, data contract, geometry contract, animation contract, semantic color roles, and validation hooks. For patterns expected to work in isolated skill-only workspaces, include a minimal standalone implementation recipe that does not depend on reading the gallery source.

## Validation

After changing this skill, its references, scripts, or examples, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing the capture script or example fixture, also run the smoke command from `Common Commands` and inspect the generated screenshot.

When changing the examples gallery, read `references/gallery-patterns.md` and run the gallery verifier documented there. Verify that all cards render, each card has exactly one replay control, sampled replay buttons restart only their target card, repeated replay does not duplicate marks or listeners, and desktop plus mobile screenshots keep text and controls readable.

When changing the composition sheets, run `scripts/verify_composition_sheets.py` and confirm every current gallery pattern is reviewed, every curated variant has an inline SVG preview plus stable `data-composition-id`, `data-example-id`, `data-pattern-id`, `data-composition-pattern-id`, `data-armature-lines`, `data-quadrants`, and `data-reviewed` attributes, and each SVG includes a semantic `.source-pattern-recomposition` group plus a metadata-only source-pattern signature. Do not draw visible composition guide lines, quadrant overlays, source-field borders, signature boxes, or direction cues inside card previews unless they are source-derived marks, route paths, process links, label leaders, or another narrative element. Keep only variants that work well for the selected composition; do not restore fit classes such as `support` tiers or duplicate every pattern into every sheet.

For large galleries, create contact sheets and run an explicit visual critique pass by example or batch before final validation. Integrate the critique centrally when possible: shared token ramps, label halos, axis/grid contrast, and replay-safe post-render polish should handle recurring issues before adding one-off chart fixes.

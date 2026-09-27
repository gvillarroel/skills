---
name: d3
description: Create, animate, inspect, recompose, and validate D3-powered HTML and SVG visuals, including charts, simulations, linked views, audits, parametric logos, textures, and portable SVG; use colorset1 as standard and colorset2 only for explicit extended requests, and invoke the bundled deterministic builder first for supported forms.
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

## Preserve the public contract

- Treat every requested path, ID, class, attribute, label, value, unit, order, count, relationship, route, colorset, and pattern ID as immutable API data.
- Use `colorset1` by default. Use `colorset2` only for an explicit extended, expanded, multicolor, or full-color request.
- Prefer compact boxes and neutral surfaces: 6 px vertical / 10 px horizontal node padding, 12 px panel padding, and 8 px UI gaps. Read `references/compact-composition.md` when sizing nodes, panels, or controls; preserve readable text and data geometry.
- In colorset1, use grays, black, white, and deliberate red emphasis first. Pink is a last-resort category after usable red/neutral distinctions are exhausted, never an automatic secondary color, selection fill, or focus ring.
- Read visible paint from `assets/palettes/colorsets.json`; use exact lowercase six-digit tokens and opacity, never arbitrary colors, functional color syntax, or raw D3 chromatic scales.
- Preserve supplied data and deterministic geometry. Seed layouts, pre-tick simulations, and make the settled frame truthful.
- Give each SVG a stable `viewBox`, `<title>`, `<desc>`, semantic groups, readable labels, stable IDs, and active-colorset metadata.
- Bundle runtime and data for offline HTML. Portable SVG must not depend on JavaScript or a network after extraction.

## Map builder flags exactly

Map every public acceptance literal to a flag. Use `--kind flow` with `--svg-pattern-id` when the decision variant differs from SVG pattern metadata, and repeat `--attribute`, `--flow-node`, `--link`, and `--link-value` in contract order. Keep titles generic or include only a leading prefix of ordered data labels; never mention a later label before intervening labels. Use `--kind logo --logo-mode wedges` for radial wedges; its colorset2 sequence already covers visible accent, warning/orange, success/green, and special/purple groups.

For `check_visual_contract.py`, express exact cardinality as `--require-class CLASS:COUNT` and repeat `--ordered-text` only for the data tokens whose rendered occurrences must follow that order. Quote every complete CLI value that contains whitespace, such as `--require-attribute "viewBox=0 0 960 540"`; never issue a known-invalid command as a probe. For logos emitted by `build_contract_artifact.py`, use the self-contained, palette, render, and visual-contract checks; `validate_logo_artifact.py` is only for full logo-studio outputs.

Use `--require-id ID` without a count suffix. `--require-class` takes a class name, never a CSS selector: for a default four-node flow use `--require-class flow-node:4 --require-class node:4 --require-class link:3`. Only use another class when you supplied its builder flag; do not guess a `flow-link` alias.

During skill maintenance, extend and test the builder when a required supported contract cannot be expressed.

Pass each `requiredTerms` value unchanged with repeated `--required-term`; keep composition, implementation-contract, and validation findings separate. Do not post-edit supported reports.

## Preflight and workflow

1. List exact outputs and decision fields; route and colorset; literal data order; IDs, classes, attributes, and counts; motion, interaction, accessibility, offline, and final-state requirements.
2. Choose D3 when custom geometry, joins, scales, projections, simulation, interaction, or animated transformation is material. Prefer Mermaid for notation-first diagrams and ECharts for conventional dashboards.
3. Choose the narrow route below and read only its linked references.
4. Build with D3 joins, scales, layouts, shape generators, projections, or transitions. Use documented APIs such as `Math.hypot` and `d3.easeCubicOut`.
5. Validate independently after the last write, render the settled state, inspect it at the intended size, fix every failure, and rerun.

## Progressive-disclosure routes

- Form selection and implementation: `references/visualization-type-index.md`, `references/layout-patterns.md`, and `references/pattern-selection-contracts.md`.
- Named or nearest reusable pattern: `references/pattern-routing.md` and `references/pattern-index.md`; read only the matching anchored pattern recipe. For exact counts, also read `references/cardinality-generalization.md`.
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

```text
python <d3-skill>/scripts/check_self_contained_html.py <artifact.html>
python <d3-skill>/scripts/check_palette_contract.py <artifact.html> --colorset colorset1
python <d3-skill>/scripts/check_palette_contract.py <artifact.html> --colorset colorset2 --require-extended
uv run --script <d3-skill>/scripts/render_d3_svg.py <artifact.html> --output <settled.svg>
python <d3-skill>/scripts/check_visual_contract.py <settled.svg> <exact-contract-flags>
```

Run only the palette command matching the active colorset. The renderer has declared Playwright dependencies: always invoke it with `uv run --script`, never bare `python`. It can reuse installed Edge/Chrome on Windows when managed Chromium is absent. Keep temporary checks outside deliverables. A missing tool is not a pass; use an equivalent browser/parser check. Use route-specific validators for logos, recompositions, galleries, or replication.

After the applicable bundled validators pass, you MUST stop issuing tool calls and report the result. Never run `grep`, inline Python, or a second ad hoc parser to reconfirm a condition already covered by those validators; raw first-occurrence logic can disagree with rendered accessibility text.

## Acceptance gate

- Exact non-empty outputs exist outside the skill; decision metadata and all public literals match.
- Form, quantitative geometry, values, units, order, entities, links, and visible palette influence match the source contract.
- Standalone output is offline; SVG metadata, accessibility, stable IDs, and deterministic settled state are present.
- Browser output is nonblank, readable, unclipped, collision-free, replay-safe, and faithful at its final frame.
- Every applicable self-contained, palette, rendered-structure, and route-specific check passed after the last edit.

Before changing bundled patterns, scripts, examples, galleries, palettes, or composition sheets, read `references/maintenance-validation.md` and preserve published IDs.

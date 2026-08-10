---
name: d3
description: Create, select, animate, inspect, recompose, and validate D3-powered HTML and SVG visuals. Use when Codex needs bespoke data-driven geometry, quantitative charts, simulations, projections, dense or linked views, portable SVG animation, D3 interaction, deterministic visual reconstruction, composition critique or armature conversion, dithering, or parametric D3/SVG logos and textures; use colorset1 as the standard palette and colorset2 only for explicit extended/full-color requests.
---

# D3

## Start Here: Deterministic Contract Builder

If the task asks for a new bar chart, node-link network, or orbit/type logo, your first command after reading this file must be:

```text
python3 <d3-skill>/scripts/build_contract_artifact.py --help
```

Use that builder to create the requested `visual.html` and `decision.json`; do not read or inline the vendored D3 runtime, hand-author either file, or edit the generated files afterward. Map every public acceptance-contract literal to a builder flag. For an allowed-value array, choose exactly one listed value rather than joining values. Re-run the builder with corrected flags if validation fails. Hand-author only forms the builder does not support. In a skill-maintenance task, extend and test the builder instead of bypassing it when a supported form lacks a required flag.

If the task asks for a composition evaluation or audit report, your first command after reading this file must be:

```text
python3 <d3-skill>/scripts/build_evaluation_report.py --help
```

Use that builder for the report and decision record. Pass every public `requiredTerms` entry unchanged through a repeated `--required-term`; do not replace spaces with hyphens or normalize punctuation, selectors, or case. Supply traceable composition findings, implementation-contract findings, and validation checks as separate flags. Do not hand-author or post-edit a supported evaluation report.

## Core Contract

1. Treat every requested output path and every requested tag, ID, class, data attribute, label, value, unit, order, count, route, colorset, and pattern ID as a fixed API value. Copy each literal exactly; a clearer synonym or alternate stable ID is still a contract failure.
2. Use D3 when custom geometry, data binding, scales, projections, simulation, interaction, or animated transformation is the point. Use Mermaid for notation-first conventional diagrams and ECharts for standard dashboard charts when its built-in chart already fits.
3. Use `colorset1` by default. Use `colorset2` only when the user explicitly requests an extended, expanded, full-color, or multicolor palette. An ordinary request for a colored or polished visual does not override the default.
4. Resolve visible paint through `assets/palettes/colorsets.json`. Use exact lowercase six-digit hex tokens from the active colorset; use opacity for transparency. Do not introduce arbitrary colors, named colors, RGB/HSL/LCH values, or raw D3 chromatic interpolators.
5. Preserve supplied labels, language, values, units, order, counts, relationships, and quantitative geometry. Do not add or remove entities merely to improve composition.
6. Keep output deterministic. Seed random layouts, pre-tick simulations before export, use stable IDs/classes, and make the final frame a truthful settled data state.
7. Give every SVG a stable `viewBox`, `<title>`, `<desc>`, semantic groups, readable labels, and explicit active-colorset metadata through `data-colorset` or `data-color-set`.
8. For standalone or offline work, bundle the D3 runtime and data. A portable SVG must contain its own geometry and CSS/SMIL animation; extracted SVG cannot depend on D3 transitions or external JavaScript.

## Mandatory Preflight And Hard Stop

Before writing code, make a compact checklist from the prompt:

- exact output files and decision metadata;
- route and active colorset;
- literal labels, values, units, order, entities, and links;
- exact tag, ID, class, data-attribute, and cardinality requirements;
- required animation, interaction, accessibility, offline, and final-state behavior.

Read `assets/palettes/colorsets.json` before choosing paint. Use these compact roles when no narrower role is supplied:

- `colorset1` standard: background `#f7f7f7`, surface `#ffffff`, ink `#333e48`, dark ink `#1c1c1c`, primary `#9e1b32`, primary dark `#6d1222`, accent `#e8002a`, accent soft `#ffccd5`, muted `#828282`, line `#cfcfcf`, quiet `#e7e7e7`.
- `colorset2` extended: all colorset1 roles plus blue `#007298` / dark blue `#004d66`, orange `#e77204`, green `#45842a`, purple `#652f6c`, and yellow `#f1c319`. Use these extra hues only for explicit extended requests and meaningful categories.

Never substitute familiar framework colors. Use `fill-opacity`, `stroke-opacity`, or `opacity` instead of `rgba()`, `hsla()`, or eight-digit hex. Apply prompt-specified IDs/classes to the exact rendered elements, not near-equivalent wrappers.

Do not finish immediately after writing. Run every applicable gate, fix every failure, and rerun until all pass:

```text
python <d3-skill>/scripts/check_self_contained_html.py <artifact.html>
python <d3-skill>/scripts/check_palette_contract.py <artifact.html> --colorset colorset1
python <d3-skill>/scripts/check_palette_contract.py <artifact.html> --colorset colorset2 --require-extended
```

For dynamic HTML, render the settled SVG with `scripts/render_d3_svg.py`, then check prompt literals with `scripts/check_visual_contract.py`. Pass every exact requirement as a flag; for example:

```text
python <d3-skill>/scripts/check_visual_contract.py <rendered.svg> --require-id service-network --require-class node:5 --require-class link:6 --require-tag circle:5 --require-attribute data-layout=force
```

Keep temporary render/check artifacts outside the requested deliverables. A missing tool is not a pass: use another browser or parser and perform the same checks. Do not claim completion while any checklist item or validator is unresolved.

The contract builder writes exactly one offline `visual.html` and one `decision.json`, uses only the selected palette, and accepts exact IDs, classes, and data attributes as arguments. Render and validate its outputs before finishing.

## Workflow

1. Extract the output contract, source data, required interactions or motion, exact cardinalities, and palette request.
2. Choose the route:
   - For a new visualization, read `references/pattern-selection-contracts.md` when the form is open and `references/pattern-routing.md` when a named `d3-*` family or builder is requested.
   - For portable or offline output, read `references/self-contained-output.md` and `references/animation-patterns.md` as applicable.
   - For composition critique, scoring, or comparison, read `references/evaluation-rubric.md`.
   - For armature conversion, read `references/recomposition-recipes.md`.
   - For logos, wordmarks, seals, monograms, masks, or texture systems, read `references/pattern-catalog.md` and `references/palette-contract.md`; read `references/texture-catalog.md` only when choosing a texture.
   - For source-SVG grammar reconstruction, read `references/svg-replication.md`.
   - For ordered/error-diffusion or zoom-stable dithering, read `references/patterns/surface-stable-dither.md`.
3. Declare the active colorset before choosing marks. Start with colorset1 semantic roles. If colorset2 is explicitly requested, use its extra hues only for meaningful categories or states.
4. Build from deterministic data with D3 joins, scales, layouts, shape generators, projections, or transitions. Prefer a small workspace-local source file over one-off coordinate editing.
5. Validate the artifact independently of the implementation; this step is mandatory, not optional:
   - Run `scripts/check_self_contained_html.py` for standalone HTML.
   - Run `scripts/check_palette_contract.py` with the selected colorset.
   - Render HTML/SVG with `scripts/render_d3_svg.py` when browser-visible output is in scope.
   - Use the route-specific validator for logos, recompositions, gallery work, or source-style replication.
6. Inspect the rendered result at its intended size. Fix blank states, clipping, tiny text, label collisions, occluded marks, misleading geometry, weak contrast, replay duplication, and a final frame that differs from the promised data.

## Route-Specific Operations

### Visualizations and animation

- Search `references/pattern-index.md` when the user asks for the closest existing pattern without naming an exact ID. Read only the selected pattern reference.
- When exact `d3-*` IDs are supplied, read every matching file under `references/patterns/` before coding.
- Read `references/cardinality-generalization.md` for exact mark counts, IDs, or small/medium/large variants.
- Use `scripts/create_d3_svg_starter.py` for a bounded editable project and `scripts/render_d3_svg.py` for SVG export and screenshots.
- Use CSS or SMIL for portable SVG motion. Use D3 transitions only in live HTML.

### Composition evaluation and recomposition

- Render or inspect the actual SVG before judging it; do not score only source text when visual tooling is available.
- Start evaluation reports with `Artifact: <exact ID, selector, or file>` and separate composition findings from implementation-contract findings.
- Preserve the source pattern meaning and assign recomposed variants as `d3-composition-<composition-id>-<source-id>`.
- Validate a recomposition with:

```powershell
uv run --script skills/d3/scripts/check_recomposition_contract.py <output.html> --source-id <source-id> --composition-id <composition-id>
```

- For gallery-level scoring, run `scripts/evaluate_composition_variants.py` with both the composition page and base gallery supplied explicitly, then inspect the lowest-score screenshots.

### Logos and textures

- Preserve requested brand text exactly and keep animal or organic shapes generic. Never trace or imitate a protected logo or mascot.
- Use `colorset1` unless the brief explicitly asks for an extended/full-color identity and multiple semantic hues materially improve it.
- Prefer parameterized copy, pattern, texture, density, curvature, scale, rotation, and strength over one-off coordinate changes.
- Build a deterministic offline studio with:

```powershell
uv run --script skills/d3/scripts/build_logo_studio.py --output outputs/logo-studio.html --brand "Northlight" --tagline "Signal in motion" --colorset colorset1 --pattern d3-logo-type-orbit --texture d3-logo-diagonal-hatch
```

- Validate logo artifacts with `scripts/validate_logo_artifact.py` and browser-visible galleries with `scripts/verify_logo_gallery.py` or `scripts/verify_logo_texture_gallery.py`. Test detailed marks at 96 px and reduce texture before sacrificing text clearance.

## Palette Gate

Validate standard output:

```powershell
uv run --script skills/d3/scripts/check_palette_contract.py artifact.html --colorset colorset1 --json-report palette-report.json
```

For an explicit extended request, require at least one colorset2-only token:

```powershell
uv run --script skills/d3/scripts/check_palette_contract.py artifact.svg --colorset colorset2 --require-extended --json-report palette-report.json
```

For dynamic HTML, the static palette check covers visible markup and styles but intentionally ignores JavaScript runtime bodies. Also render the artifact and inspect computed SVG paint; logo validators already perform this runtime palette gate.

## Progressive Disclosure

- `references/visualization-type-index.md`: choose a D3 form or compare D3 with Mermaid.
- `references/layout-patterns.md`: joins, scales, hierarchy, force, projection, and layout mechanics.
- `references/animation-patterns.md`: staged reveals, path drawing, morphing, replay, and final-frame rules.
- `references/pattern-selection-contracts.md`: dense data, distributions, uncertainty, linked views, maps, annotations, and accessibility.
- `references/pattern-routing.md` and `references/pattern-index.md`: exact or nearest reusable `d3-*` patterns.
- `references/self-contained-output.md`: portable HTML/SVG and dependency rules.
- `references/evaluation-rubric.md`: dynamic symmetry, balance, reading path, clearance, and scoring.
- `references/recomposition-recipes.md`: balance, diagonal, proportional, grid, radial, flow, and label-lane armatures.
- `references/palette-contract.md`: colorset roles, allowed tokens, contrast, and logo-specific restrictions.
- `references/pattern-catalog.md`, `references/mathematical-patterns.md`, and `references/texture-catalog.md`: parametric logo mechanisms.
- `references/user-artifact-workflow.md`: output ownership and starter usage.
- `references/maintenance-validation.md`: skill, gallery, composition-sheet, palette, and publication maintenance.

## Acceptance Checks

Require all applicable checks before finishing:

- Exact non-empty outputs exist outside the skill.
- Every prompt-specified ID, class, attribute, tag count, metadata value, label, and order is present literally in the settled output.
- The visualization form matches the relationship the viewer must understand.
- Default work uses only colorset1; colorset2 appears only after an explicit extended/full-color request and materially affects visible marks.
- Values, labels, units, order, entity counts, and relationships match the source contract.
- SVG accessibility metadata, stable IDs, viewBox, and deterministic final state are present.
- Standalone output has no undeclared network dependency.
- Browser-visible output is nonblank, readable, unclipped, replay-safe, and faithful at the final frame.
- Composition and logo routes pass their dedicated validators.
- The self-contained, palette, settled-structure, and route-specific commands were actually run after the last edit and all exited successfully.

## Maintenance

Read `references/maintenance-validation.md` before changing bundled patterns, scripts, examples, galleries, palettes, or composition sheets. Preserve published example and pattern IDs even though this unified skill replaces the former D3 skill names.

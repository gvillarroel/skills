---
name: echarts-animated-svg
description: "Animates already-rendered Apache ECharts SVG output and builds replayable SVG galleries. Use when Codex needs to render ECharts charts with SVGRenderer or SSR, post-process the resulting SVG instead of rebuilding chart geometry, choose chart-type-specific SVG animation profiles for ECharts chart types, or create an HTML index with controls to replay or restore chart animations."
---

# ECharts Animated SVG

Read [the colorset output contract](references/colorset-contract.md) before authoring or auditing visual output. Apply one exact bundled palette to every authored output path and inspect rendered paint. Default to colorset1; declare colorset2 when its category distinctions are needed. Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast.

For directed edges, read [arrow contrast and placement](references/arrow-contrast.md). Qualify actual shafts and heads at 3:1 against their local backings and keep complete heads outside nodes. Use the bundled option helper before rendering authored arrow charts. For fixed native graph arrows, call `insetGraphArrowRoutes(chart, 3)` after `setOption` and before SVG export, then repeat after resize or option changes. It preserves source endpoints and node geometry while trimming the native display route. Inspect filled crossings and final exports separately.

When authoring conceptual graph/tree diagrams, read [compact diagrams](references/compact-diagrams.md)
and default to the smallest readable
layout before SVG export: use content-sized nodes, reduce surplus rank gaps
and route detours, and keep separate lanes and explicit endpoints. Compare
a tighter candidate at the same display scale; reject label overlap/clipping,
obscured heads, ambiguous crossings or reduced readability, then restore the
local clearance. Stop at the smallest passing candidate and reapply native
arrow clearance after layout changes. Animation-only tasks preserve the
supplied static geometry. Quantitative charts retain axes, scales, legends,
mark separation and useful data dimensions rather than spatial squeezing.

For a small workflow or ranked conceptual graph, use the compact reference's
JSON contract and `scripts/render_concept_graph.py`. It delivers native SVG,
an editable native ECharts option and geometry review without handwritten
view fitting or replacement marks. Inspect its Chromium preview before
animation. Use `--probe` and read its structured acceptance result when
testing a tighter comparison; render final deliverables without that flag.
Preserve the normal quantitative chart workflow.

For native boxplots, read [median contrast](references/boxplot-median-contrast.md). With pinned ECharts 6.1.0, call `qualifyBoxplotMedians(chart, echarts, selected)` after `setOption` and before capture/export, then normalize delivered SVG paint. Repeat after source option or resize changes. Preserve opaque category bodies and native data; use independent median ink rather than a contrasting box rim.

For browser-accurate preview, run `scripts/render_svg_preview.py <svg> --output <workspace-preview.png>`
through `uv run --script`, then open that PNG. Add `--width` for the delivery
size. Use task-owned paths; on Windows, `convert` may be a system utility
rather than an SVG renderer. The preview is an inspection aid, not a layout
or contrast certificate.

## Exact Output Contract

When a task names specific files, treat those names as fixed API values. Before writing files or running commands, make a two-value map from the prompt:

```powershell
$StaticSvg = "bar.static.svg"
$AnimatedSvg = "bar.animated.svg"
```

Replace the example values with the exact requested paths. Do not substitute descriptive names such as `chart.static.svg`, `chart.animated.svg`, or `bar-chart.animated.svg`. After generation, run a literal path check for every requested output and fix the run before responding if any check fails.

## Core Workflow

1. Capture any user-provided input and output filenames before running commands. Use those paths exactly in the static SVG, animated SVG, and validation checks; do not rename them.
2. Render the ECharts chart to SVG first. Prefer `SVGRenderer` in the browser or `echarts.init(null, null, { renderer: "svg", ssr: true, width, height })` plus `renderToSVGString()` in Node. Apply the required native graph arrow clearance step between `setOption` and export; follow its supported layout contract in the arrow reference.
3. Preserve ECharts geometry. Do not redraw chart marks by hand unless the source chart is unavailable.
4. Choose a chart-type profile from `references/chart-animation-profiles.md` and animate the rendered marks with CSS or `scripts/animate_echarts_svg.py`.
5. Keep chart context visible enough to orient the viewer: axes, legends, labels, map outlines, and hierarchy labels should fade or settle after data marks instead of disappearing.
6. Use the design tokens in `references/design-system.md` for generated galleries, replay controls, and example chart palettes.
7. For replayable deliverables, wrap inline SVGs in HTML controls that remove and re-add the playback class. Avoid relying on one-shot load-only animation.
8. Validate that every final frame matches the static ECharts render and that replay works more than once.
9. When the task asks for concrete files, create the input/output artifacts and run the script. Do not stop at explaining a command unless the user only asked for guidance.
10. Write generated task files to the current workspace or requested artifact directory. Do not write task outputs into the skill directory unless maintaining the skill itself.

## Progressive Disclosure Map

- `references/chart-animation-profiles.md`: read when the task names a chart type, requests broad ECharts coverage, or needs a reveal order for a rendered ECharts SVG.
- `references/svg-targeting-and-replay.md`: read when post-processing SVG DOM, writing replay controls, or validating animation/reset behavior.
- `references/design-system.md`: read when creating or updating an HTML gallery, chart theme, replay controls, or user-facing example output.
- `assets/templates/static-bar-chart.svg`: use as a small already-rendered SVG input for isolated smoke tests, demos, or tasks that need a simple bar-chart source but do not provide one.

## Visual Tokens

Read `references/visual-tokens.md` before creating or updating ECharts animation examples or replayable galleries. Use Open Sans for page and SVG text, Material Symbols Rounded for replay/reset icons, and the documented brand palette for editable chart options, page chrome, controls, highlights, and replay states.

## Pattern Promotion

When an ECharts chart animation pattern proves reusable, update `references/chart-animation-profiles.md` before finishing. Capture chart type, trigger, SVG target selectors, reveal order, timing, replay behavior, final-frame expectation, and verification command. Put gallery UI or palette lessons in `references/design-system.md`, and SVG reset/targeting pitfalls in `references/svg-targeting-and-replay.md`.

## Common Commands

Animate a pre-rendered SVG:

```powershell
$StaticSvg = "chart.static.svg"
$AnimatedSvg = "chart.animated.svg"
uv run --script skills/echarts-animated-svg/scripts/animate_echarts_svg.py $StaticSvg --chart-type line -o $AnimatedSvg
uv run --script skills/echarts-animated-svg/scripts/validate_animated_svg.py $StaticSvg $AnimatedSvg --chart-type line --report chart-validation.json
if (!(Test-Path -LiteralPath $StaticSvg) -or !(Test-Path -LiteralPath $AnimatedSvg)) { throw "Missing requested ECharts SVG output path." }
```

Run an isolated bar-chart smoke test from the bundled template:

```powershell
$StaticSvg = "bar.static.svg"
$AnimatedSvg = "bar.animated.svg"
Copy-Item skills/echarts-animated-svg/assets/templates/static-bar-chart.svg $StaticSvg
uv run --script skills/echarts-animated-svg/scripts/animate_echarts_svg.py $StaticSvg --chart-type bar -o $AnimatedSvg --duration-ms 800 --stagger-ms 90
uv run --script skills/echarts-animated-svg/scripts/validate_animated_svg.py $StaticSvg $AnimatedSvg --chart-type bar --duration-ms 800 --stagger-ms 90 --report bar-validation.json
if (!(Test-Path -LiteralPath $StaticSvg) -or !(Test-Path -LiteralPath $AnimatedSvg)) { throw "Missing requested ECharts SVG output path." }
```

Tune timing:

```powershell
uv run --script skills/echarts-animated-svg/scripts/animate_echarts_svg.py chart.static.svg --chart-type sankey -o chart.animated.svg --duration-ms 900 --stagger-ms 45
```

For repository acceptance-fixture maintenance only, set `<skill-root>` to the full `echarts-animated-svg` source directory and build the bundled gallery below. It requires `assets/examples/`, which is intentionally excluded from the normal runtime payload.

```powershell
npm install --prefix <skill-root>/assets/examples/echarts-animated-svg
npm run build --prefix <skill-root>/assets/examples/echarts-animated-svg
npm run verify --prefix <skill-root>/assets/examples/echarts-animated-svg
```

## Validation

For a task-level static/animated pair, use the bundled validator instead of
ad-hoc XML or regex probes. It checks XML validity, source geometry and label
preservation, animation roles and ordering, requested timing, replay metadata,
reduced-motion CSS, and external references. A nonzero exit is a real failed
check; fix the artifact rather than layering exploratory validators on top.

After changing this skill, its scripts, references, or examples, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing the gallery generator or replay behavior, also run the example `build` and `verify` commands.

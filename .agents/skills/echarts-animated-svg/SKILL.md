---
name: echarts-animated-svg
description: Animate already-rendered Apache ECharts SVG output and build replayable SVG galleries. Use when Codex needs to render ECharts charts with SVGRenderer or SSR, post-process the resulting SVG instead of rebuilding chart geometry, choose chart-type-specific SVG animation profiles for ECharts chart types, or create an HTML index with controls to replay or restore chart animations.
---

# ECharts Animated SVG

## Exact Output Contract

When a task names specific files, treat those names as fixed API values. Before writing files or running commands, make a two-value map from the prompt:

```powershell
$StaticSvg = "bar.static.svg"
$AnimatedSvg = "bar.animated.svg"
```

Replace the example values with the exact requested paths. Do not substitute descriptive names such as `chart.static.svg`, `chart.animated.svg`, or `bar-chart.animated.svg`. After generation, run a literal path check for every requested output and fix the run before responding if any check fails.

## Core Workflow

1. Capture any user-provided input and output filenames before running commands. Use those paths exactly in the static SVG, animated SVG, and validation checks; do not rename them.
2. Render the ECharts chart to SVG first. Prefer `SVGRenderer` in the browser or `echarts.init(null, null, { renderer: "svg", ssr: true, width, height })` plus `renderToSVGString()` in Node.
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
uv run --script .agents/skills/echarts-animated-svg/scripts/animate_echarts_svg.py $StaticSvg --chart-type line -o $AnimatedSvg
if (!(Test-Path -LiteralPath $StaticSvg) -or !(Test-Path -LiteralPath $AnimatedSvg)) { throw "Missing requested ECharts SVG output path." }
```

Run an isolated bar-chart smoke test from the bundled template:

```powershell
$StaticSvg = "bar.static.svg"
$AnimatedSvg = "bar.animated.svg"
Copy-Item skills/echarts-animated-svg/assets/templates/static-bar-chart.svg $StaticSvg
uv run --script skills/echarts-animated-svg/scripts/animate_echarts_svg.py $StaticSvg --chart-type bar -o $AnimatedSvg --duration-ms 800 --stagger-ms 90
if (!(Test-Path -LiteralPath $StaticSvg) -or !(Test-Path -LiteralPath $AnimatedSvg)) { throw "Missing requested ECharts SVG output path." }
```

Tune timing:

```powershell
uv run --script .agents/skills/echarts-animated-svg/scripts/animate_echarts_svg.py chart.static.svg --chart-type sankey -o chart.animated.svg --duration-ms 900 --stagger-ms 45
```

Build and verify the bundled gallery fixture:

```powershell
npm install --prefix .agents/skills/echarts-animated-svg/assets/examples/echarts-animated-svg
npm run build --prefix .agents/skills/echarts-animated-svg/assets/examples/echarts-animated-svg
npm run verify --prefix .agents/skills/echarts-animated-svg/assets/examples/echarts-animated-svg
```

## Validation

After changing this skill, its scripts, references, or examples, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing the gallery generator or replay behavior, also run the example `build` and `verify` commands.

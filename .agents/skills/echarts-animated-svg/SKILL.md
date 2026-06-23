---
name: echarts-animated-svg
description: Animate already-rendered Apache ECharts SVG output and build replayable SVG galleries. Use when Codex needs to render ECharts charts with SVGRenderer or SSR, post-process the resulting SVG instead of rebuilding chart geometry, choose chart-type-specific SVG animation profiles for ECharts chart types, or create an HTML index with controls to replay or restore chart animations.
---

# ECharts Animated SVG

## Core Workflow

1. Render the ECharts chart to SVG first. Prefer `SVGRenderer` in the browser or `echarts.init(null, null, { renderer: "svg", ssr: true, width, height })` plus `renderToSVGString()` in Node.
2. Preserve ECharts geometry. Do not redraw chart marks by hand unless the source chart is unavailable.
3. Choose a chart-type profile from `references/chart-animation-profiles.md` and animate the rendered marks with CSS or `scripts/animate_echarts_svg.py`.
4. Keep chart context visible enough to orient the viewer: axes, legends, labels, map outlines, and hierarchy labels should fade or settle after data marks instead of disappearing.
5. Use the design tokens in `references/design-system.md` for generated galleries, replay controls, and example chart palettes.
6. For replayable deliverables, wrap inline SVGs in HTML controls that remove and re-add the playback class. Avoid relying on one-shot load-only animation.
7. Validate that every final frame matches the static ECharts render and that replay works more than once.

## Progressive Disclosure Map

- `references/chart-animation-profiles.md`: read when the task names a chart type, requests broad ECharts coverage, or needs a reveal order for a rendered ECharts SVG.
- `references/svg-targeting-and-replay.md`: read when post-processing SVG DOM, writing replay controls, or validating animation/reset behavior.
- `references/design-system.md`: read when creating or updating an HTML gallery, chart theme, replay controls, or user-facing example output.

## Visual Tokens

Read `../ANIMATED_VISUAL_TOKENS.md` before creating or updating ECharts animation examples or replayable galleries. Use Open Sans for page and SVG text, Material Symbols Rounded for replay/reset icons, and the documented brand palette for editable chart options, page chrome, controls, highlights, and replay states.

## Pattern Promotion

When an ECharts chart animation pattern proves reusable, update `references/chart-animation-profiles.md` before finishing. Capture chart type, trigger, SVG target selectors, reveal order, timing, replay behavior, final-frame expectation, and verification command. Put gallery UI or palette lessons in `references/design-system.md`, and SVG reset/targeting pitfalls in `references/svg-targeting-and-replay.md`.

## Common Commands

Animate a pre-rendered SVG:

```powershell
uv run --script .agents/skills/echarts-animated-svg/scripts/animate_echarts_svg.py chart.static.svg --chart-type line -o chart.animated.svg
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

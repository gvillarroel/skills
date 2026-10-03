---
name: slidev-echarts
description: "Builds and troubleshoots Apache ECharts visualizations inside Slidev presentations. Use when Codex needs to add reusable ECharts Vue components to a Slidev deck, wire responsive chart containers, create click-driven data stories, tune chart modules and renderers, expose deterministic chart states for downstream capture, or validate charts in the browser; hand video composition and recording to the video skill."
---

# Slidev ECharts

Read [the colorset output contract](references/colorset-contract.md) before authoring or auditing visual output. Apply one exact bundled palette to every authored output path and inspect rendered paint. Default to colorset1; declare colorset2 when its category distinctions are needed. Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast.

## Core Workflow

1. Put chart behavior in Vue components under the Slidev `components/` directory. Keep `slides.md` focused on composition, copy, and passing small props such as `$clicks`.
2. Use ECharts through `echarts/core` for production decks. Register every chart, component, feature, and renderer needed by the option with `echarts.use(...)`.
3. Always register a renderer. Use `CanvasRenderer` for dense or animated data, and `SVGRenderer` for moderate charts that need crisp static export.
4. Give every chart a real container size before initialization. Use fixed slide-relative height, aspect ratio, or CSS grid tracks instead of relying on content height.
5. Initialize after Vue mount, call `setOption` when the option changes, resize through `ResizeObserver`, and dispose the ECharts instance on unmount.
6. For Slidev click stories, pass `$clicks` into a chart component and compute the ECharts option from a clamped step. Keep series `id` or data `name` stable so ECharts can animate diffs.
7. Use deterministic data for decks that will be exported, screenshotted, or reviewed. Avoid random data and uncached network fetches unless the user explicitly wants a live demo.
8. Validate with `npm run build`, then open the deck in a browser and inspect representative chart slides. Confirm charts are nonblank, sized correctly, text is legible, and click-driven updates animate without leaving stale series.
9. When the user needs an HTML artifact that opens directly from disk, prefer a documented single-file build path like the example deck's `npm run build:html`; normal Slidev SPA builds should be served over HTTP.
10. When the deliverable is video, finish the ECharts component and expose deterministic slide/click states, then hand the built deck and state contract to `video`. Do not own recording, MP4/WebM conversion, audio, or final video validation here.

## Reference

Read `references/integration-patterns.md` when implementing or debugging a Slidev ECharts deck. It contains a reusable wrapper pattern, module registration guidance, Slidev click patterns, and a verification checklist.

For a named chart type, select its directly linked recipe below. Read `references/chart-type-index.md` for broad coverage or installer lookup. Each ECharts 6.1.0 chart reference covers data shape, animation, display, modules, and pitfalls.

Read `references/video-handoff.md` when a downstream video needs deterministic ECharts states, settle timing, or a deck handoff contract.

## Visual Tokens

Read `references/visual-tokens.md` before creating or updating animated Slidev/ECharts examples, generated SVG motion slides, controls, or export fixtures. Use Open Sans for slide and chart text, Material Symbols Rounded for system icons, and the documented brand palette for editable chart options, UI controls, callouts, highlights, and generated assets.

## Pattern Promotion

When a Slidev/ECharts pattern proves reusable, update the owning reference before finishing. Use `references/chart-type-index.md` and the chart-specific files for chart data, modules, animation, and pitfalls; use `references/integration-patterns.md` for wrapper, lifecycle, click-story, or sizing patterns; use `references/video-handoff.md` only for deterministic state/export handoff fields. Include trigger, props/data contract, implementation steps, validation commands, and any export caveats.

## Additional reference routes

Read only the resource matching the task.

## Direct recipe links

Select the matching recipe and read it in full.

- [bar](references/charts/bar.md).
- [boxplot](references/charts/boxplot.md).
- [candlestick](references/charts/candlestick.md).
- [chord](references/charts/chord.md).
- [custom](references/charts/custom.md).
- [effect scatter](references/charts/effect-scatter.md).
- [funnel](references/charts/funnel.md).
- [gauge](references/charts/gauge.md).
- [graph](references/charts/graph.md).
- [heatmap](references/charts/heatmap.md).
- [line](references/charts/line.md).
- [lines](references/charts/lines.md).
- [map](references/charts/map.md).
- [parallel](references/charts/parallel.md).
- [pictorial bar](references/charts/pictorial-bar.md).
- [pie](references/charts/pie.md).
- [radar](references/charts/radar.md).
- [sankey](references/charts/sankey.md).
- [scatter](references/charts/scatter.md).
- [sunburst](references/charts/sunburst.md).
- [theme river](references/charts/theme-river.md).
- [tree](references/charts/tree.md).
- [treemap](references/charts/treemap.md).

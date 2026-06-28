---
name: slidev-echarts
description: Build and troubleshoot Apache ECharts visualizations inside Slidev presentations. Use when Codex needs to add reusable ECharts Vue components to a Slidev deck, wire responsive chart containers, create click-driven data stories, tune chart modules and renderers, generate automated Slidev chart videos, or validate charts for browser and export workflows.
---

# Slidev ECharts

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
10. When the user asks for video, script the recording. Drive Slidev slides and `$clicks` with Playwright, wait for ECharts updates to resolve, verify every slide state, and convert the captured WebM to MP4 with ffmpeg when available.

## Reference

Read `references/integration-patterns.md` when implementing or debugging a Slidev ECharts deck. It contains a reusable wrapper pattern, module registration guidance, Slidev click patterns, and a verification checklist.

Read `references/chart-type-index.md` when the task names a specific ECharts chart type or asks for broad chart coverage. It routes to one dedicated reference file per ECharts 6.1.0 chart installer, covering data shape, animation approach, display guidance, modules, and pitfalls.

Read `references/video-generation.md` when the task asks for an automated video, MP4/WebM output, narrated walkthrough, motion review, or slide-by-slide visual verification.

## Visual Tokens

Read `references/visual-tokens.md` before creating or updating animated Slidev/ECharts examples, generated SVG motion slides, controls, or export fixtures. Use Open Sans for slide and chart text, Material Symbols Rounded for system icons, and the documented brand palette for editable chart options, UI controls, callouts, highlights, and generated assets.

## Pattern Promotion

When a Slidev/ECharts pattern proves reusable, update the owning reference before finishing. Use `references/chart-type-index.md` and the chart-specific files for chart data, modules, animation, and pitfalls; use `references/integration-patterns.md` for wrapper, lifecycle, click-story, or sizing patterns; use `references/video-generation.md` for recording patterns. Include trigger, props/data contract, implementation steps, validation commands, and any export caveats.

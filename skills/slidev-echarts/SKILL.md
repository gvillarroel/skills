---
name: slidev-echarts
description: "Builds and troubleshoots Apache ECharts visualizations inside Slidev presentations. Use when Codex needs to add reusable ECharts Vue components to a Slidev deck, wire responsive chart containers, create click-driven data stories, tune chart modules and renderers, expose deterministic chart states for downstream capture, or validate charts in the browser; hand video composition and recording to the video skill."
---

# Slidev ECharts

Read [the colorset output contract](references/colorset-contract.md) before authoring or auditing visual output. Apply one exact bundled palette to every authored output path and inspect rendered paint. Default to colorset1; declare colorset2 when its category distinctions are needed. Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast.

For directed graph/route/mark-line output, read [arrow contrast and placement](references/arrow-contrast.md). Apply the bundled option helper before rendering. For fixed native graph arrows, call `insetGraphArrowRoutes(chart, 3)` after `setOption` and after resize or click updates once native layout has settled. It preserves source endpoints and node geometry while trimming the native display route. Inspect actual shafts and complete heads at 3:1 against local backings, outside node silhouettes and clear of labels. Check settled click/focus states and the final export scale.

For authored conceptual graph/tree diagrams, read [compact diagrams](references/compact-diagrams.md)
and default to the smallest readable
layout: reduce surplus label padding, node/rank gaps and connector detours;
keep text/head/stroke sizes, endpoint identity and separate route lanes.
Compare a tighter candidate at the same slide scale after rendering; reject
overlap, clipping, hidden heads, ambiguous crossings or lost click-state
clearance and restore the local gap. Stop at the smallest passing candidate.
Reapply native arrow clearance after layout changes. Preserve supplied chart
geometry during capture-only work. For quantitative charts, optimize useful
data dimensions and information density while preserving axes, scales,
legends and mark separation; do not squeeze their plotting area by default.

For a small workflow or ranked conceptual graph, use the compact reference's
JSON contract and `scripts/render_concept_graph.py` for native SVG, editable
ECharts options and geometry review. Start ordinary flows with IDs, full
labels and directed relationships; let the helper compute ranks and content
bounds instead of guessing `x`/`y`. Render every unverified first draft with
`--probe` into fresh candidate paths. Read `accepted`; correct rejected
geometry before previewing it; never chain a probe to preview with `&&`.
Inspect an accepted native preview, then
render exact final paths without `--probe`. Use this sequence for prescribed
geometry, custom coordinates and later tighter candidates too. Final layout
and unexpected-input errors remain failures. Keep computed content dimensions
in the slide and inspect final native/click states in Chromium.
Keep ordinary relationship captions on native links and their caption adapter.
Do not bypass a rejected caption gate with unqualified graphic text; custom
graphic captions need native shaft/glyph clearance inspection in every state.
For prescribed rectangle dimensions, use node `width`/`height` and `symbol:
"rect"` in that same contract. Run `scripts/qualify_concept_graph.py` for the
native delivery/resize/replay/reduced review and workspace preview; its
self-contained browser path avoids constructing a separate module server.

For native boxplots, read [median contrast](references/boxplot-median-contrast.md). With pinned ECharts 6.1.0, call `qualifyBoxplotMedians(chart, echarts, selected)` after `setOption` and before capture/export. Repeat after resize or click options, and normalize delivered SVG paint. Preserve opaque category bodies and native data; qualify the median independently rather than adding a contrasting box rim.

Keep dependencies and screenshots in the task workspace. For a deck under
`deck/`, run npm from that directory or with `--prefix deck`. Declare its
selected theme (including `@slidev/theme-default` for the default theme) in
the deck package before a noninteractive build. Read screenshots from their
actual workspace paths; avoid `/tmp` paths in Windows tool calls.
After building, use `scripts/capture_deck.py --deck deck --output-dir
deliverables/deck-capture --clicks <declared-click-count>`. It serves the SPA
on an owned ephemeral port, captures native click/replay/resize/reduced-motion
states, and closes its browser and server. Inspect `capture.json` and the
workspace-owned PNGs. Count clicks after the initial state; one click produces
two story states.

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

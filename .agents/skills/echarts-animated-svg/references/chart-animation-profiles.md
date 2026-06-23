# ECharts SVG Chart Animation Profiles

Use these profiles after ECharts has already rendered a static SVG. Treat the SVG as the source of truth and tune selectors against the actual emitted `path`, `rect`, `circle`, `polygon`, `polyline`, `line`, and `text` elements.

## Shared Defaults

- Use 700-900 ms mark duration with 24-60 ms stagger. Dense charts should cap total stagger so the full chart settles quickly.
- Keep a base static state outside the playback class so removing the class restores the finished chart.
- Use `pathLength="1"` plus stroke-dash animation for stroked paths and polylines. Use transform or opacity for filled areas where stroke drawing would distort meaning.
- Fade labels after their related marks. Do not animate labels before data geometry exists.
- Respect `prefers-reduced-motion` by disabling movement while leaving the final frame visible.
- Prefer SSR `ecmeta_series_index` and `ecmeta_data_index` attributes when they are present. Browser-rendered ECharts SVG often lacks them, so fall back to scoped style/structure selectors and browser-computed bounding boxes.
- Do not target generated `zr*` classes, clip IDs, gradient IDs, or raw path coordinates. Re-query SVG nodes after `setOption`, resize, or Slidev hydration because ECharts can recreate the SVG DOM.

## Cartesian Charts

### line

Draw scenario and baseline strokes left-to-right. Fade area fills first at low opacity, draw line paths next, pop symbols last, then fade labels and legend. Keep axes visible or fade them before the data.

Selector hints: scope plot paths through the clipped plot group when possible, because legend icons can share the same stroke colors as data lines. Keep category order stable before drawing a trend.

### bar

Scale each bar from the baseline with `transform-box: fill-box` and `transform-origin: center bottom`. Stagger in category order. Fade value labels after bar growth.

Selector hints: ECharts often emits rounded bars as filled `path` elements, not `rect` elements. For browser SVG, filter filled non-stroked paths and sort by `getBBox().x`; for SSR, prefer `ecmeta_data_index`.

### boxplot

Fade or scale each box group by category. Draw whisker lines after the box body, then fade median markers. Avoid rotating or morphing boxes because quartile geometry should remain readable.

Selector hints: ECharts often renders each boxplot as one compound path containing body, whiskers, caps, and median. Use stroke draw plus fill-opacity on that compound path, or split/overlay if median-last choreography is required.

### candlestick

Scale candle bodies from their midpoint or baseline and draw high-low whiskers. Preserve up/down color semantics. Stagger by x-axis order so the time sequence reads correctly.

Selector hints: each candle can be one compound path containing body and wicks. Prefer SSR `ecmeta_data_index` for left-to-right ordering and preserve OHLC color semantics.

### custom

Use the mark geometry returned by `renderItem` as authoritative. For range bars, scale from the range start on the x-axis. For arbitrary marks, prefer fade/pop unless the rendered shape has an obvious direction.

Selector hints: custom range bars often serialize as rounded `path` elements, not `rect` elements. Prefer per-bar clipping from the range start to preserve rounded corners; fall back to `scaleX` only when the path has no existing transform.

## Part-To-Whole Charts

### pie

Fade or sweep slices around the center. If arcs are hard to isolate, use a small radial scale plus opacity. Keep the final slice angles exactly as ECharts rendered them.

Selector hints: slice paths usually contain arc commands such as `A`; legend icons can share slice colors, so do not use broad `path[fill]` selectors.

### treemap

Fade parent rectangles first, then scale leaf rectangles from their centers. Stagger by hierarchy depth or area from largest to smallest. Keep labels delayed until rectangles are stable.

Selector hints: browser SVG may emit translated filled paths plus white backplates. Animate colored leaves separately from `fill="#fff"` backplates and avoid CSS transforms on already-transformed paths unless composing the original transform.

### sunburst

Reveal rings from inner to outer levels. Use radial scale and opacity for segments; avoid path morphing because ring geometry is brittle in raw SVG.

Selector hints: SSR output can tag sunburst segments with `ecmeta_data_index`; browser fallback should scope to filled arc paths with white borders. Reveal inner rings before outer rings and rely on ECharts `universalTransition` for value morphs before capture.

### funnel

Reveal stages from top to bottom with vertical scale and opacity. Keep labels inside their stage and delay text until segment width is visible.

Selector hints: data stages are usually filled trapezoid `path` elements. Filter out empty paths, `fill="none"` paths, transformed title paths, and transparent hit areas before sorting by `getBBox().y`.

### gauge

Draw the axis/progress arc first, rotate or fade the pointer/needle next, then count/fade the detail text. If the pointer is not separable, use a short pop for all central marks.

Selector hints: the progress arc is commonly a closed filled path rather than a stroked line, so stroke-dash reveal is unreliable. Prefer ECharts value animation before capture, or use clip/fade replay on the static SVG.

## Relationship And Flow Charts

### graph

Pop nodes first, then draw links. In circular layouts, start at the top or the highest-value node and proceed clockwise. Keep labels delayed to avoid clutter during node movement.

Selector hints: graph nodes are normally symbol `path` elements with `matrix(...)` transforms, not `circle` elements. Preserve existing transforms and use opacity/pulse for nodes; draw only link paths.

### chord

Reveal outer arcs first, then fade ribbons from source groups. Prefer opacity over aggressive stroke drawing because ribbon paths are filled shapes.

Selector hints: distinguish ribbons from outer arcs with `fill-opacity` where available. For SSR SVG, `ecmeta_ssr_type="chart"` can help scope marks, but do not depend on it in browser-rendered DOM.

### sankey

Reveal nodes by column from source to target, then draw or fade links after both endpoint columns are visible. Use low-opacity link fade for dense flows to preserve gradients.

Selector hints: links and nodes are both paths. Distinguish gradient-filled link ribbons from solid-filled node blocks. Stroke-dash drawing is wrong for filled Sankey ribbons.

### tree

Pop the root, draw branch links outward, then pop child symbols and fade labels. For left-to-right ECharts trees, use x-position ordering when possible.

Selector hints: branch links are `path[fill="none"][stroke]`; node symbols are transformed `path` elements. Preserve node transforms and use opacity for symbols unless composing transforms explicitly.

### lines

Draw route paths in travel direction and pop endpoint symbols. If ECharts emitted effect symbols, fade them after the route stroke exists.

Selector hints: SSR can distinguish route paths and endpoint scatter symbols by `ecmeta_series_index`. Browser fallback should target blue stroked route paths separately from red endpoint symbols and ignore empty `d=""` paths from unsettled renders.

## Spatial And Multidimensional Charts

### map

Fade region polygons by value or geographic grouping. Keep boundaries visible early. Delay labels until all regions have settled.

Selector hints: scope to the chart SVG and filter region paths by map boundary stroke or by data metadata. Region names must match the registered GeoJSON feature names before animation matters.

### scatter

Pop points by priority, x-order, or data order. Use opacity plus scale rather than moving points from arbitrary origins. Bubble charts should preserve final symbol size.

### effectScatter

Pop base points first, then start ripple or pulse elements. Keep ripple opacity subtle so it does not mask point position.

Selector hints: points and ripple rings are `path` elements, not `circle` elements. SSR can mark ripple rings with `ecmeta_silent`; browser fallback should preserve each symbol's existing `matrix(...)` transform and animate opacity/ripple stroke instead.

### radar

Draw radar grid lightly, then reveal polygons from the center. Draw or fade radial axes before data polygons; labels should appear last.

### parallel

Fade axes first, then draw polylines from the first dimension to the last. Use low opacity and short stagger to avoid overplotting.

Selector hints: browser SVG can emit data as stroked `path` elements inside a clipped group; SSR/export may emit `polyline` with `ecmeta_*`. Keep axis order and numeric scale fixed.

### heatmap

Fade cells row-by-row or from low to high value. Avoid scaling tiny cells too much because grid alignment is the main reading aid. Show labels after cells settle.

Selector hints: heatmap cells often serialize as filled `path` rectangles, while split-area backgrounds use `fill-opacity`. Keep the visualMap static and reveal cell labels only if they exist in the captured state.

### pictorialBar

Reveal symbols from the baseline upward, preserving repeated symbol count. If individual symbols are not separable in SVG, scale the emitted bar group like a normal bar.

Selector hints: repeated pictorial symbols usually have existing `matrix(...)` transforms. Group by x-position, sort each group bottom-to-top, and prefer opacity/clip reveals over replacing transforms.

### themeRiver

Fade stream areas from earliest date to latest or layer-by-layer by theme. Avoid stroke drawing filled stream paths; opacity plus slight vertical settle is safer.

Selector hints: theme river bands are closed filled paths. Use stream-level clip or opacity; do not `scaleY` individual bands because it distorts stacked boundaries. Keep legend hitboxes invisible.

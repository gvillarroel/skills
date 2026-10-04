# Colorset Output Contract

Select one palette for each authored visual output and record its name in the output or its report. Default to `colorset1`; use `colorset2` for an explicit full-color request or a documented need to distinguish several independent semantic categories. The full-color acceptance galleries deliberately use `colorset2` to demonstrate multiple category and animation mechanisms. A gallery containing both variants must identify each item's selected palette.

Read [the exact local palette contract](../assets/palettes/colorsets.json). Do not invent close grays, alternate blues, renderer defaults, or theme-derived tints. Use the selected allowlist for backgrounds, text, axes, borders, markers, highlights, controls, hover/focus, errors, legends, and exported assets. Colorset1 is red plus neutrals; reserve pink for an explicit need after readable neutral/red roles.

Inspect actual rendered marks, not just a theme configuration. Native renderer defaults, calculated color lightness/saturation, heatmap interpolation, and arbitrary overrides can introduce undeclared colors. Use discrete exact palette bins for numeric color scales while preserving data values and continuous position/size encodings. Use stepped changes between categorical animation colors; animate geometry and opacity smoothly. Tonal gradients may use exact endpoints in one role; do not interpolate categorical hues. Alpha, raster antialiasing, and compression are compositing effects rather than new authored base colors.

Preserve imported logos, photos, footage, and third-party source image pixels and provenance. Keep this source-media boundary narrow and explicit; all authored wrappers and labels still follow the selected palette. Source media is not permission to keep arbitrary authored chart colors. When editing source presentation is out of scope, report incompatible colors instead of claiming a palette pass.

Validate every output format and state the skill supports: source, static vector, animated vector, canvas, raster/export, gallery/deck chrome, controls, alternate states, and any downstream capture. Keep output paths, chart/diagram facts, relationships, stable IDs, labels, geometry, and accessibility metadata intact when repairing paint.

Copy `assets/templates/echarts-colorsets.mjs` into a chart project when authoring options. Use `colorsetTheme(selected)` at ECharts initialization and `prepareColorsetOption(option, selected)` before `setOption`; use `normalizeSvgPaints(renderToSVGString(), selected)` for residual SVG renderer defaults. The animator rejects off-palette static input. Restyle editable ECharts options first so static and animated paint remain identical. The bundled bar smoke template uses colorset1; the 43-chart acceptance gallery deliberately uses colorset2.

## Solid-first category style

Use one opaque solid fill and no decorative outline for initial category choices. Keep the exact finite palette. Allocate every distinct usable palette color before recycling a fill with an outline; exclude the actual canvas color. For colorset1, use primary red `#9e1b32`, then grays, black, white, and only then the remaining colors. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Keep each category's fill, text and any overflow outline stable across panels, series, legends and motion states. Declare overflow explicitly and cycle border color, dash and width only after that solid capacity is exhausted.

For text inside a filled shape, choose exactly `#000000` or `#ffffff` by the greater WCAG relative-luminance contrast against the actual fill. Do not assume every saturated color needs white text: orange, yellow, cyan and medium green often need black. Labels outside shapes use the canvas contrast. Use spacing and silhouette for grouping before borders. Preserve connectors, chart lines, class compartments, actor line art, meaningful data boundaries, source artwork and explicit user style. Containers are layout surfaces, not new categories.


Use the independent `assets/templates/echarts-colorsets.mjs` helpers: `solidColors(colorset, canvas)` gives the complete solid capacity; `solidCategoryStyle(index, colorset, canvas)` returns stable fill, border, inside text and explicit overflow. Build a stable category ID-to-index map before rendering; use the same map for legends and data. `prepareColorsetOption` defaults filled marks to zero border width and resolves inside text contrast, while keeping chart/connector lines. For an explicit source-style preservation request set `colorsetPresentation: 'source'` on the editable option. Quantitative continuous scales, boxplot whiskers and candlestick wicks retain their measurement meaning.

The public signatures are `solidColors(colorset, canvas)`,
`solidCategoryStyle(index, colorset, canvas)`, and
`prepareColorsetOption(option, colorset, categoryOrder = [])`. The canvas may be
an equivalent opaque CSS color (including rgba with alpha 1 or eight-digit hex).
The option canvas paint retains its meaning while allocation excludes its exact
opaque palette token. Each category must have a stable `id` or `name`. Defaults
sort identities in natural order so reordering the same set retains its colors.
For changing subsets or additions, pass the same complete `categoryOrder` array
to every option, panel and state; the array includes categories currently hidden.
Keep any explicit palette mappings consistent with that manifest. Caller palette
fills and the full `solidCategoryStyle` object are retained; its `overflow` flag
is allocation metadata and is removed from ECharts `itemStyle` after preparation.
Observe rendered overflow through `borderWidth > 0`, rather than expecting an
unsupported ECharts `itemStyle.overflow` property.

Inside labels use their effective inherited position and actual label backing;
outer labels use the canvas. For a translucent canvas, contrast uses its composite
over a white host fallback while keeping the requested canvas paint. Place an
embedded chart on a different opaque host by supplying that effective opaque
backgroundColor; the helper cannot infer external host pixels. Native pie/funnel defaults are outer, graph defaults
are inside. Label background colors and rich-token backgrounds take precedence
when they cover the mark. Normal and authored motion-state label styles remove
decorative text borders and shadows. Validate actual rendered text paint, not
only option fields, especially for graph defaults and inherited data labels.

Overflow borders have at least 3:1 contrast against the solid fill and enumerate
allowed border colors, solid/dashed/dotted patterns, and bounded 1–3 px widths.
After these finite combinations repeat, use labels, symbols or split views to
retain distinguishable categories; do not widen borders until they hide the fill.

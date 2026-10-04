# Colorset Output Contract

Select one palette for each authored visual output and record its name in the output or its report. Default to `colorset1`; use `colorset2` for an explicit full-color request or a documented need to distinguish several independent semantic categories. The full-color acceptance galleries deliberately use `colorset2` to demonstrate multiple category and animation mechanisms. A gallery containing both variants must identify each item's selected palette.

Read [the exact local palette contract](../assets/palettes/colorsets.json). Do not invent close grays, alternate blues, renderer defaults, or theme-derived tints. Use the selected allowlist for backgrounds, text, axes, borders, markers, highlights, controls, hover/focus, errors, legends, and exported assets. Colorset1 is red plus neutrals; reserve pink for an explicit need after readable neutral/red roles.

Inspect actual rendered marks, not just a theme configuration. Native renderer defaults, calculated color lightness/saturation, heatmap interpolation, and arbitrary overrides can introduce undeclared colors. Use discrete exact palette bins for numeric color scales while preserving data values and continuous position/size encodings. Use stepped changes between categorical animation colors; animate geometry and opacity smoothly. Tonal gradients may use exact endpoints in one role; do not interpolate categorical hues. Alpha, raster antialiasing, and compression are compositing effects rather than new authored base colors.

Preserve imported logos, photos, footage, and third-party source image pixels and provenance. Keep this source-media boundary narrow and explicit; all authored wrappers and labels still follow the selected palette. Source media is not permission to keep arbitrary authored chart colors. When editing source presentation is out of scope, report incompatible colors instead of claiming a palette pass.

Validate every output format and state the skill supports: source, static vector, animated vector, canvas, raster/export, gallery/deck chrome, controls, alternate states, and any downstream capture. Keep output paths, chart/diagram facts, relationships, stable IDs, labels, geometry, and accessibility metadata intact when repairing paint.

The renderer defaults to colorset1 and normalizes native SVG paint after all theme/source overrides. PNG-only Ditaa uses the supported source-backed native raster adapter; standalone math retains native notation and palette quantization. Source-media PNGs retain their original pixels and report a preservation boundary; inspect their authored chrome through the matching normalized SVG. The report validator rejects undeclared SVG paints and missing current native style delivery. A custom theme must also fit the selected colorset.

## Solid-first category style

Use one opaque solid fill and no decorative outline for initial category choices. Keep the exact finite palette. Allocate every distinct usable palette color before recycling a fill with an outline; exclude only the actual canvas color. Colorset1 priority is primary red, all grays, near-black and black, white, then the remaining dark red, bright red and pink. Use the exact bundled `solidSequence`; do not place secondary red hues before neutral capacity. Colorset2 keeps its bundled color order. Keep each category's fill, text and any overflow outline stable across panels, series, legends and motion states. Declare overflow explicitly and cycle border color, dash and width only after that solid capacity is exhausted.

For text inside a filled shape, choose exactly `#000000` or `#ffffff` by the greater WCAG relative-luminance contrast against the actual fill. Do not assume every saturated color needs white text: orange, yellow, cyan and medium green often need black. Labels outside shapes use the canvas contrast. Use spacing and silhouette for grouping before borders. Preserve connectors, chart lines, class compartments, actor line art, meaningful data boundaries, source artwork and explicit user style. Containers are layout surfaces, not new categories.

The bundled themes use explicit family scopes for native object surfaces. Colorset1 starts the primary family body with primary red and uses grays for secondary kinds; a repeated kind reuses its assigned fill. ArchiMate compresses absent native layers so a single active layer starts red. When additional distinct categories are needed, allocate the full `scripts/palette_paints.py` `solid_style` capacity using stable IDs and explicit scoped PlantUML style rules. Follow [native style delivery](native-styling.md): the native SVG finish handles hardcoded token/button/task borders, restores class/cylinder/queue/component details, and selects text paint against actual backings. Source media, line art, mathematical notation and semantic chart measurement strokes retain their meanings.

The allocator `solid_style(index, colorset, canvas)` uses all usable solid colors
first. Its overflow borders select only allowed colors with at least 3:1 contrast
against the fill and cycle solid/dashed/dotted lines with bounded 1–3 px widths.
Keep the same category index in every state. Once these finite combinations
repeat, use labels, symbols or split views instead of widening borders until they
hide the fill. `solid_colors(colorset, canvas)` returns the complete solid capacity;
these Python helpers are sibling modules under `scripts/`, not installed packages.

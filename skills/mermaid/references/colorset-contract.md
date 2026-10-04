# Colorset Output Contract

Select one palette for each authored visual output and record its name in the output or its report. Default to `colorset1`; use `colorset2` for an explicit full-color request or a documented need to distinguish several independent semantic categories. The full-color acceptance galleries deliberately use `colorset2` to demonstrate multiple category and animation mechanisms. A gallery containing both variants must identify each item's selected palette.

Read [the exact local palette contract](../assets/palettes/colorsets.json). Do not invent close grays, alternate blues, renderer defaults, or theme-derived tints. Use the selected allowlist for backgrounds, text, axes, borders, markers, highlights, controls, hover/focus, errors, legends, and exported assets. Colorset1 is red plus neutrals; reserve pink for an explicit need after readable neutral/red roles.

Inspect actual rendered marks, not just a theme configuration. Native renderer defaults, calculated color lightness/saturation, heatmap interpolation, and arbitrary overrides can introduce undeclared colors. Use discrete exact palette bins for numeric color scales while preserving data values and continuous position/size encodings. Use stepped changes between categorical animation colors; animate geometry and opacity smoothly. Tonal gradients may use exact endpoints in one role; do not interpolate categorical hues. Alpha, raster antialiasing, and compression are compositing effects rather than new authored base colors.

Preserve imported logos, photos, footage, and third-party source image pixels and provenance. Keep this source-media boundary narrow and explicit; all authored wrappers and labels still follow the selected palette. Source media is not permission to keep arbitrary authored chart colors. When editing source presentation is out of scope, report incompatible colors instead of claiming a palette pass.

Validate every output format and state the skill supports: source, static vector, animated vector, canvas, raster/export, gallery/deck chrome, controls, alternate states, and any downstream capture. Keep output paths, chart/diagram facts, relationships, stable IDs, labels, geometry, and accessibility metadata intact when repairing paint.

The renderer normalizes actual generated SVG paint declarations to the source's selected colorset and checks the result before animation. Existing static SVG input must already fit one palette; the animator rejects incompatible paint rather than changing a read-only source. Style and check Mermaid source first. Generated static and animated files must match final paint and geometry.

## Solid-first category style

Use one opaque solid fill and no decorative outline for initial category choices. Keep the exact finite palette. Allocate every distinct usable palette color before recycling a fill with an outline; exclude the actual canvas color. For colorset1, use primary red `#9e1b32`, then grays, black, white, and only then the remaining colors. For colorset2, retain its bundled base/saturated, dark/bright/neutral, then soft order. Keep each category's fill, text and any overflow outline stable across panels, series, legends and motion states. Declare overflow explicitly and cycle border color, dash and width only after that solid capacity is exhausted.

For text inside a filled shape, choose exactly `#000000` or `#ffffff` by the greater WCAG relative-luminance contrast against the actual fill. Do not assume every saturated color needs white text: orange, yellow, cyan and medium green often need black. Labels outside shapes use the canvas contrast. Use spacing and silhouette for grouping before borders. Preserve connectors, chart lines, class compartments, actor line art, meaningful data boundaries, source artwork and explicit user style. Containers are layout surfaces, not new categories.

The native renderer finish in `scripts/mermaid_animation/solid.py` removes Mermaid-generated pie rims/opacity, keeps inside slice contrast synchronized, and finishes section-driven shapes, Kanban cards, event boxes, packet labels and cause boxes without touching relation paths. It applies only to freshly rendered Mermaid sources. Existing `--svg-input` assets retain their supplied presentation. The finish extends native numbered sections and pie slices through the full usable solid sequence, then marks outline overflow explicitly. For other native fixed-index families, extend their fill allocation or split the view before introducing outlined overflow. Transparent Venn intersections and open line diagrams preserve their data meaning.

The allocator `solid_style(index, colorset, canvas)` uses all usable solid colors
first. Its overflow borders select only allowed colors with at least 3:1 contrast
against the fill and cycle solid/dashed/dotted lines with bounded 1–3 px widths.
Keep the same category index in every state. Once these finite combinations
repeat, use labels, symbols or split views instead of widening borders until they
hide the fill. `solid_colors(colorset, canvas)` returns the complete solid capacity;
these Python helpers are sibling modules under `scripts/`, not installed packages.

### Native renderer finishing

Newly rendered SVGs pass through `mermaid_animation.solid.native_solid_presentation`
before animation; supplied `--svg-input` assets retain source fidelity. The finish
uses renderer family and native group semantics, rather than removing every SVG
stroke. C4 stereotypes, Journey sections/actor IDs, Railroad terminal kinds,
ZenUML participant columns, Treemap sections/leaves, and Cynefin item cards use
opaque solid allocation. State/Block class labels and Kanban metadata backings
share their actual node paint. Swimlane headers carry lane identity; lane bodies
are canvas with no decorative frame. Treemap native 0.6 paint opacity is overridden
to 1, separately from intended reveal opacity. Native inside labels and Quadrant
point labels choose black or white against their actual painted surface.

Venn overlap paths retain their meaningful native transparency and boundaries;
choose label contrast against the composite over the canvas. Sequence control
regions retain transparency: condition/message captions and stick-figure captions
use black on the pale canvas, boxed participant/control-tab labels retain contrast
against their solid backing, and sequence numbers use contrast against the native
referenced marker circle. Cynefin center and edge captions use the actual region
under their center, including the central ellipse. Radar legend swatches retain
their curve color with opaque borderless paint; curve opacity and line geometry
remain meaningful. These rules are covered by `scripts/test_native_solid.py`.

Preserve relationship paths and cardinality markers, open cylinder seams,
Journey facial line art, Gantt critical-status boundaries, Wardley procurement
overlays, ZenUML control frames/lifelines, and embedded source icons. A native
relationship caption that crosses a C4 entity uses that entity's text contrast.
Check actual rendered SVG CSS rather than stale presentation attributes. Ignore
zero-area metadata rectangles and transparent canvas layers when detecting rims.
Inspect static output and animated settled/mid-reveal states; classify partial
ancestor reveal opacity explicitly, while filled paint remains opaque.
For contrast checks, include closed filled paths, partial label containment,
RGBA/fill-opacity compositing in paint order, and referenced marker geometry.

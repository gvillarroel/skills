# Readable directed edges

For graph-only Node SVG SSR with the full registered `echarts` package,
initialize with a `null` theme and apply `prepareColorsetOption` before
`setOption`, followed by native arrow clearance and SVG paint normalization.
This retains qualified graph paint without materializing unused calendar
defaults that require a range. Use the normal colorset theme for the modular
Slidev component; do not copy graph-only SSR setup to unrelated chart families.

## Contents

- [Paint qualification](#paint-qualification)
- [Native graph clearance](#native-graph-clearance)
- [Cartesian route clearance](#cartesian-route-clearance)
- [Rendered verification](#rendered-verification)

## Paint qualification

For authored graph arrows, route lines, moving arrow effects and default
`markLine` arrow symbols, use the bundled `assets/templates/echarts-colorsets.mjs`.
Call `prepareColorsetOption` before rendering. It corrects directional series,
individual edges, and declared emphasis/select/blur styles.
Preparation modifies the supplied option in place. Build fresh nested options
and state styles for each palette or independent chart; shared state objects
can carry a previous chart's corrected paint into the next declaration.
Check baseline declarations before preparation. Cartesian insetting returns
a new option; native graph insetting changes only the rendered edge layout.
Native per-terminal markLine symbol overrides are included. A lines effect
is selected by the series renderer; an edge's `effect.show: false` can still
paint a moving arrow, so qualify its merged symbol/color. Include native
effect opacity in the visible composite, even when an upstream type omits it.
The exported `contrastSafeArrowStyle(style, colorset, background)` can style a custom
arrow against its known backing. Preserve supplied artwork when the task is
only animation or capture.

Start with an opaque allowed paint, at least 1.5 CSS px shaft width, and a head
large enough at the final display/export scale. Test shaft and head against
the actual adjacent surface with at least 3:1 relative-luminance contrast.
Include paint alpha, line opacity and ancestor opacity. Compare unrounded
ratios; an allowed token can still disappear on its local backing. Do not
recolor nodes or add rims/halos to make an arrow visible.

The helper measures the declared canvas composited over a white host. It
cannot infer arbitrary plot fills, intervening nodes, WebGL/canvas host paint,
CSS group opacity or custom `path://` symbols. Inspect the rendered result.
Unknown, gradient or unresolved CSS arrow/backing paint is rejected instead
of measured using an invented fallback color. Percentage color alpha is
parsed and composited; a transparent arrow is repaired to readable paint.
Route through a clear gutter before choosing a scoped contrasting tone for an
unavoidable filled crossing. Keep source/target category identity in labels
when its original shade needs a darker or lighter arrow tone.

## Native graph clearance

For `graph`, use suitable `edgeSymbolSize` and apply the native clearance step
below. ECharts clips wide rectangular symbols using an averaged radius; the
complete arrowhead can consequently be covered by its target. Curved edges
must approach the intended target along the final tangent. Check complete
arrowheads outside opaque node silhouettes and clear of labels. For
`lines`, inspect both terminal symbols, moving effects and endpoint scatter
marks. For `markLine`, inspect default endpoint arrows and any crossed filled
chart marks. Custom arrow glyphs require an explicit geometry/paint check.

Import `insetGraphArrowRoutes` from the bundled colorset module. After
`chart.setOption(preparedOption)`, call `insetGraphArrowRoutes(chart, 3)`
before capture or SVG export. The second argument is the minimum CSS-pixel
gap between the whole native arrowhead envelope and every node envelope.
The helper trims existing straight or quadratic graph display paths along
their own tangents. It retains the original source route and leaves
`getOption()`, source coordinates, node shapes, labels, colors and symbols
unchanged; it adds no overlay series. Its result reports `checkedEdges`,
`adjustedEdges` and `clearancePx`.

This ECharts 6.1.0 native-layout adapter supports resting `layout: 'none'`
graphs. Pin the supported dependency with `npm install echarts@6.1.0`.
Its native structure guards reject incompatible layouts; validate the
adapter again before changing engine versions. It supports
graphs in the native `view` coordinate system, with axis-aligned built-in
`rect`, `roundRect` or `circle` nodes and native `arrow` terminal symbols.
Use `animation: false` for deterministic exports; for animated components,
wait for native layout to settle before applying it. Unsupported/custom
symbols, rotated nodes, force/circular layouts, short routes and heads
blocked by other nodes fail explicitly before any edge changes. Author a
clear native route for those cases and inspect the complete painted envelope.
After resize, zoom or click option changes, let ECharts lay out the original
source coordinates again, then repeat the helper before capture. Do not put
the trimmed display route into source data.

```js
chart.setOption(prepareColorsetOption(originalOption, selected))
insetGraphArrowRoutes(chart, 3)
// ResizeObserver and click updates repeat setOption/resize, then clearance.
```

## Cartesian route clearance

When a two-point continuous Cartesian `lines` route terminates at an opaque scatter mark,
lay out the original option, then pass it and the initialized chart to
`insetCartesianArrowRoutes(option, chart, radiusPlusGapPx)`. Apply the returned
option. It shortens each native arrow terminal along its curved end tangent
without mutating the original coordinates. Set the distance from the actual
endpoint radius plus a small gap; 7 px suits a radius-4 mark with a 3 px gap.
After resizing or changing clicks, lay out the original coordinates again
and recompute the inset. Keep the original data as the semantic endpoint
contract. This helper rejects short, polyline and unsupported coordinate
geometry; inspect those routes explicitly rather than guessing data units.

## Rendered verification

Verify actual emitted paths and transforms after SSR/browser rendering,
resting focus/select/blur states, replay, reduced motion, zoom and export.
An intentional partial reveal or fade to hidden is a transition, not a
readable resting state. The animated final frame must preserve both head and
shaft geometry and paint from the qualified static source. Use the bundled
pair validator for that preservation check; it does not measure local paint
contrast or prove arrowhead visibility by itself.

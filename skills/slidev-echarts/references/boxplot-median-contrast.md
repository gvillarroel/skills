# Native boxplot median contrast

Keep each box body opaque and visually borderless. A median is a statistical
mark, so give it independent black or white ink rather than a contrasting
enclosing box rim. Preserve all five source values and the native layout.

Use the validated native adapter with **ECharts 6.1.0**. Install that exact
version for this route (`npm install echarts@6.1.0`), import the full namespace,
and use the owning bundled `assets/templates/echarts-colorsets.mjs`:

```js
import * as echarts from 'echarts';
import {
  prepareColorsetOption, qualifyBoxplotMedians, normalizeSvgPaints,
  insetGraphArrowRoutes
} from './echarts-colorsets.mjs';

const selected = 'colorset1';
const chart = echarts.init(null, null, {
  renderer: 'svg', ssr: true, width: 640, height: 360
});
chart.setOption(prepareColorsetOption({
  animation: false,
  xAxis: { type: 'category', data: ['Group A', 'Group B'] },
  yAxis: { type: 'value' },
  series: [{ type: 'boxplot', data: [[4, 9, 14, 20, 28], [5, 11, 16, 22, 31]] }]
}, selected));
insetGraphArrowRoutes(chart, 3); // Also qualify any directed fixed graph.
const medians = qualifyBoxplotMedians(chart, echarts, selected);
const svg = normalizeSvgPaints(chart.renderToSVGString(), selected);
chart.dispose();
```

Call `qualifyBoxplotMedians` after `setOption` and before capture/export in
both browser and SSR code. In a Slidev wrapper, repeat it after a click option
or native resize, and before the next capture. Its native Line callback
tracks animation and emphasis/select/blur paint; keep original source values
for updates. Use `animation: false` for deterministic SSR. Normalization is
required for delivered SVG palette paint, including native hover CSS.

The adapter retains the native `BoxPath`, its first four body corners and
all whisker segments. It transfers the final pair of native endpoints to
one native `graphic.Line`; the original compound path stops painting that
one segment. It adds no chart series, source data, duplicate median or box
rim. It leaves options, axis geometry, native body/whisker paint and labels
unchanged. Repeated calls reuse the Line, and calls after removal clean up
obsolete Lines and restore the removed owner's original path builder.

Measure the actual native solid fill and opacity over the actual canvas
before selecting maximum-contrast black or white. Keep that calculation
unrounded. If the native face has zero area, choose ink against the canvas.
For a positive face, clip median paint to that face and retain any native
plot clip. Endpoints stay exact. Use a 2 px median stroke normally and 4 px
within 1 px of a face boundary, where clipping otherwise weakens fractional
Canvas pixels. Inspect at the final display scale; undersized faces still
need enough exported pixels to show their statistical detail.

SVG qualification uses the exact native owner/Line VNode keys, without
guessing paths from coordinates. It tags those known marks and adds a scoped
CSS `:has()` rule so standalone native SSR hover selects the correct median
ink when box fill changes. Its color calculation follows the pinned native
emphasis implementation and the delivered normalized SVG paint. Live SVG
and Canvas use the actual native state paint. Browser verification requires
a browser supporting CSS `:has()`; the regression uses Chromium.

Supported internals are ECharts 6.1.0 Cartesian `boxplotBoxPath` with exactly
14 native endpoints and native rectangular clipping. Unknown/gradient body
or canvas paint, incompatible engine versions and changed native geometry
or SVG identity contracts reject explicitly. Preserve provided artwork when
only animating or capturing an existing SVG; this route qualifies newly
authored native boxplots.

The return value reports `qualifiedBoxes`, `newMedians`, `removedMedians`
and per-mark native endpoints, face, live ink/backing and delivered SVG
ink/backing. Treat these as diagnostics; independently inspect actual paint.

Run the bundled `scripts/test_boxplot_medians.py` with `--echarts-package`
and `--playwright-package` pointing to installed packages, plus `--output`
pointing to a disposable artifact directory. It covers SVG SSR/browser
hover, Canvas state paint, exact native geometry, zero-IQR/boundary/partial
clipping, repeat/resize/update/cleanup and every CS1 token at fractional
Q1/Q3 boundaries on white and dark canvases.

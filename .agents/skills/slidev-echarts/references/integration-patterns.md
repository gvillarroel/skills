# Slidev ECharts Integration Patterns

## Project Shape

Use this structure for a local Slidev deck:

```text
slides.md
components/
  ResponsiveEChart.vue
  ChartTypeSlide.vue
  DomainSpecificChart.vue
lib/
  chart-lab.js
data/
  *.json
styles/
  index.css
package.json
```

Slidev auto-loads Vue components from `components/`, but explicit relative imports inside other components make dependencies clearer and keep components portable.

## Dependencies

Install ECharts next to the Slidev project:

```powershell
npm install echarts
```

Use `vue-echarts` only when the project already uses it or when its managed component API is valuable. A small local wrapper is often easier to audit in presentations because lifecycle, resize, renderer selection, and `setOption` behavior are explicit.

## ECharts Module Registration

Prefer tree-shakeable imports:

```vue
<script setup>
import * as echarts from 'echarts/core'
import { BarChart, LineChart } from 'echarts/charts'
import { AriaComponent, GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { LabelLayout, UniversalTransition } from 'echarts/features'
import { CanvasRenderer, SVGRenderer } from 'echarts/renderers'

echarts.use([
  BarChart,
  LineChart,
  AriaComponent,
  GridComponent,
  LegendComponent,
  TooltipComponent,
  LabelLayout,
  UniversalTransition,
  CanvasRenderer,
  SVGRenderer,
])
</script>
```

If ECharts reports that a component or series type does not exist, the option references a chart or component that was not registered. Register the missing module instead of switching to a full `import * as echarts from 'echarts'` unless speed matters more than bundle size.

## Responsive Wrapper Contract

A reusable wrapper should:

- Render a div with an explicit height or aspect ratio.
- Initialize ECharts only after mount and after the DOM node has size.
- Call `chart.setOption(option, updateOptions)` whenever the option changes.
- Observe container size changes with `ResizeObserver` and call `chart.resize()`.
- Remove observers and call `chart.dispose()` on unmount.
- Expose `renderer`, `theme`, `height`, `option`, and `updateOptions` props.

Use stable CSS dimensions in slides:

```md
<ResponsiveEChart :option="option" height="360px" />
```

Avoid mounting charts inside hidden or zero-sized containers. If a chart appears after a click, mount it after the click or call `resize()` when it becomes visible.

For broad chart-type validation, use one generic slide component that accepts a chart type and `$clicks`:

```md
<ChartTypeSlide chart-type="line" :step="$clicks" />
```

Keep chart option factories in a shared module such as `lib/chart-lab.js`, and keep synthetic fixtures in `data/*.json`. This makes chart grammar differences visible while keeping the underlying data story consistent across diagrams.

## Slidev Click Stories

Pass `$clicks` from `slides.md` into a component:

```md
<RevenueStory :step="$clicks" />

<v-clicks>
- Reveal the first business change.
- Reveal the second business change.
- Reveal the final impact.
</v-clicks>
```

Inside the component, clamp the click step and compute the option from deterministic arrays:

```js
const activeStep = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), stages.length - 1))
const option = computed(() => ({
  animationDurationUpdate: 700,
  series: [
    {
      id: 'scenario',
      name: stages[activeStep.value].label,
      type: 'bar',
      data: stages[activeStep.value].values,
    },
  ],
}))
```

Keep `id` stable when the series is conceptually the same across clicks. Use `replaceMerge: ['series']` only when the number or meaning of series changes.

## Accessibility And Export

- Set `aria.show: true` and register `AriaComponent` for accessible chart descriptions.
- Include visible titles, legends, labels, or surrounding slide text that explains the data.
- Prefer deterministic data and local assets for export.
- For PDF export, verify the generated deck visually. SVG rendering can be sharper for static moderate-size charts, while Canvas is usually better for dense or highly animated charts.
- For HTML intended to open directly from disk, use a single-file build and hash routing. A normal Slidev SPA build can render blank from `file://` because browser module loading expects an HTTP origin.
- For video export, use a Playwright recorder rather than manual capture. Drive Slidev click states, wait for ECharts updates, capture per-slide screenshots, and convert WebM to MP4 with ffmpeg when available.

## Verification Checklist

Run these checks before considering a Slidev ECharts deck ready:

1. `npm run build` succeeds from the Slidev project directory.
2. The deck opens in a browser with no console errors from missing ECharts modules.
3. Every chart type in scope contains a nonblank canvas or SVG output, not just a mounted container.
4. Resizing the browser keeps charts within their slide containers.
5. Click-driven chart slides update options without stale labels, stale series, or layout shift.
6. Export-oriented decks use deterministic data and do not depend on live network requests.
7. The skill has a dedicated reference file for every chart type demonstrated in the deck.
8. If a direct-open HTML artifact is required, `npm run build:html` or the equivalent single-file build opens from `file://` and renders at least one chart canvas or SVG.
9. If video is required, `npm run video` or the equivalent recorder produces MP4/WebM plus a manifest proving every slide rendered and click-driven chart states changed.

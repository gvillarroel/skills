# SVG Targeting And Replay

## Targeting Rendered ECharts SVG

1. Inspect the actual SVG emitted by ECharts. SVGRenderer commonly emits many `path` elements even for marks that conceptually started as bars, slices, ribbons, or symbols.
2. Add animation classes to visible drawables only: `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`, and optionally `text`.
3. Skip elements inside `defs`, `clipPath`, `mask`, `pattern`, `linearGradient`, and `radialGradient`.
4. Prefer chart-type profiles over brittle DOM order. When precise ordering matters, compute order from bounding boxes in a browser or from known ECharts option data order before post-processing.
5. Keep the original attributes intact. Add classes, CSS variables, and `pathLength` only where needed.

## Replay Pattern

Use a playback class on the chart wrapper, not permanent inline mutation:

```js
function replay(card) {
  card.classList.remove('is-playing')
  void card.offsetWidth
  card.classList.add('is-playing')
}
```

The static state should remain visible when `is-playing` is absent. Animation rules should only apply under `.is-playing`, for example:

```css
.chart-card.is-playing svg .easv-fade {
  opacity: 0;
  animation: easv-fade 760ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}
```

## Verification Checklist

- The generated HTML contains one inline SVG for every chart type in scope.
- Each SVG has visible marks after animation completes.
- Clicking the per-chart replay button restarts that chart without changing layout.
- Clicking replay-all restarts every chart more than once.
- A screenshot after replay is nonblank and still shows labels, legends, axes, and final chart geometry.
- Browser console and page errors are empty, except for known harmless renderer warnings that are documented.

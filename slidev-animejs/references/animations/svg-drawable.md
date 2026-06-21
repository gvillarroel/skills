# SVG Drawable

## Use When

Use SVG drawable animation for route reveal, process paths, handwritten-looking strokes, chart overlays, or progressive diagram construction.

## Anime.js Pattern

Use `svg.createDrawable(target)` and animate the synthetic `draw` property from hidden to visible ranges such as `['0 0', '0 1']`.

## Slidev Pattern

Keep SVG viewBox and stage aspect ratio fixed. Use separate paths when different route segments need different staggered timings.

## Tested Fixture

The `svg-drawable` slide draws three deterministic SVG path segments with staggered delay.

## Pitfalls

- Avoid `vector-effect: non-scaling-stroke` on large animated sets because it can add per-frame work.
- Keep stroke widths visible in PDF export.
- Do not rely on external SVG assets unless they are bundled with the deck.

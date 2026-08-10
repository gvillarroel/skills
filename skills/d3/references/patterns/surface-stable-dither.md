# Surface-Stable Fractal Dither

- **Pattern ID:** `d3-surface-stable-dither`
- **Gallery source ID:** `surface-stable-dither`
- **Family:** Dithering
- **Use when:** A recursive Bayer dot field stays pinned to surface coordinates while zoom reveals new dots at nearly constant screen size.
- **Renderer:** `renderSurfaceStableFractalDither`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.


## Surface-Stable Fractal Contract

Use this pattern when a dither texture must remain attached to D3/SVG surface coordinates during zoom or scale changes. It is an independent 2D adaptation of Rune Skovbo Johansen's [Surface-Stable Fractal Dithering explainer](https://www.youtube.com/watch?v=HPqGaIMVuLs) and [Dither3D reference implementation](https://github.com/runevision/Dither3D). Do not describe ordinary screen-fixed ordered dithering or error diffusion as surface-stable.

Preserve these invariants:

- Derive a fractal level from `floor(log2(scale))` and a phase from the fractional remainder.
- Use the recursive Bayer point order `[[0,0], [.5,.5], [.5,0], [0,.5]]`. Reveal one to four sub-layers as the phase advances.
- Set the local surface cell size to `baseSpacing / 2 ** fractalLevel`. At a 2x boundary, four points from the old cell must equal the first point in each of the four new half-size cells.
- Key points by stable surface coordinates, never by their array index. On zoom-in, keep existing point IDs and add points; on zoom-out, reverse that progression.
- Compensate local radius by `screenRadius / scale` so the apparent screen radius stays approximately constant.
- Use `bayer-count` shading when brightness should control dot count and `halftone` shading when brightness should control dot radius. Keep labels and interaction affordances crisp instead of dithering them unless the user explicitly wants all content rasterized.

Use the bundled runtime helper instead of reconstructing the hierarchy:

```js
const dither = SurfaceStableFractalDither.buildDots({
  width,
  height,
  scale: transform.k,
  baseSpacing: 16,
  screenRadius: 2.25,
  brightnessAt,
  shading: "bayer-count"
});

layer.selectAll("circle.dither-dot")
  .data(dither.dots, dot => dot.id)
  .join(
    enter => enter.append("circle").attr("class", "dither-dot").attr("r", 0),
    update => update,
    exit => exit.remove()
  )
  .attr("cx", dot => dot.x)
  .attr("cy", dot => dot.y)
  .attr("r", dot => dot.radius);
```

Read or copy `assets/templates/surface-stable-fractal-dither.js`; in an isolated workspace use `skills/d3/assets/templates/surface-stable-fractal-dither.js`. For an arbitrary rasterized SVG, canvas, or image, create `brightnessAt` with the helper's `brightnessSampler(imageData, width, height)`.

For a static, portable conversion of any already-rendered SVG, HTML page, canvas, or image, use the capture tool:

```powershell
uv run --script skills/d3/scripts/dither_d3_output.py source.html -o dithered.svg --selector "svg" --algorithm ordered --matrix-size 4 --cell-size 4 --palette "#000000,#ffffff"
```

That command is a settled-frame fallback. It does not become surface-stable merely because it uses a Bayer matrix; use the runtime helper when zoom or animated scale changes must preserve point identity.

Validation hooks:

- Root SVG exposes `data-dither-method="surface-stable-fractal"`, `data-threshold-family="recursive-bayer-2x2"`, `data-fractal-levels`, `data-sub-layer-count`, `data-zoom-range`, and `data-shading-mode`.
- `SurfaceStableFractalDither.validateZoomSequence()` returns `ok: true`, retains every existing point through the zoom-in sequence, and reports equal before/after point sets at the 2x boundary.
- A replay or zoom-in check confirms that existing coordinate IDs remain and that only new IDs enter before the boundary.
- Static conversion reports nonzero `gridWidth`, `gridHeight`, and `runCount`, and the output contains no remote runtime dependency.

If copying or modifying upstream Dither3D shader or texture-maker code rather than using this independent adaptation, preserve its Mozilla Public License 2.0 obligations.

## Fixture Note

The gallery renderer is an acceptance visualization, not the runtime implementation. Use the bundled template and contracts above so normal skill use does not need to read the large gallery fixture.

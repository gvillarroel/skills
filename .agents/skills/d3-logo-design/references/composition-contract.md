# Composition Contract

Treat a finished composition as a complete lockup with a primary pattern, one registered texture, one colorset, typography, spacing, and responsive intent. A parameter change is not a new composition.

## Required data contract

Every composition must expose:

```text
compositionId, patternId, textureId, brand, tagline, colorset,
fontFamily, density, curvature, scale, rotation, textureStrength,
seed, viewBox, accessibilityLabel
```

The compact catalog stores `id` and the font preset key `font`. `normalizeConfig()` maps them to runtime `compositionId` and `fontFamily`; `renderLogo()` applies the fixed `viewBox` and accessible title/description label. Validate the normalized SVG/runtime contract above rather than requiring those derived fields to be duplicated in each raw manifest record.

Use a deterministic integer seed. Keep `compositionId`, `patternId`, and `textureId` lowercase hyphen-case and at most 64 characters.

## Thirty acceptance compositions

| Composition ID | Pattern ID | Default texture |
| --- | --- | --- |
| `d3-logo-heritage-orbit-lockup` | `d3-logo-type-orbit` | `d3-logo-diagonal-hatch` |
| `d3-logo-rising-curve-lockup` | `d3-logo-bezier-wordpath` | `d3-logo-directional-fibers` |
| `d3-logo-variable-editorial-lockup` | `d3-logo-variable-axis-wordmark` | `d3-logo-micro-grid` |
| `d3-logo-joined-initial-lockup` | `d3-logo-ligature-bridge` | `d3-logo-crosshatch` |
| `d3-logo-stenciled-utility-lockup` | `d3-logo-stencil-cuts` | `d3-logo-seeded-stipple` |
| `d3-logo-textured-letter-window` | `d3-logo-letter-window` | `d3-logo-voronoi-mosaic` |
| `d3-logo-mirror-axis-lockup` | `d3-logo-mirrored-monogram` | `d3-logo-woven-checker` |
| `d3-logo-radial-glyph-emblem` | `d3-logo-glyph-rosette` | `d3-logo-guilloche-waves` |
| `d3-logo-wave-baseline-lockup` | `d3-logo-baseline-wave` | `d3-logo-topographic-lines` |
| `d3-logo-echo-stack-lockup` | `d3-logo-stack-offset` | `d3-logo-halftone-dots` |
| `d3-logo-sliced-motion-lockup` | `d3-logo-slice-shift` | `d3-logo-directional-fibers` |
| `d3-logo-outline-signal-lockup` | `d3-logo-multi-stroke-wordmark` | `d3-logo-micro-grid` |
| `d3-logo-depth-step-lockup` | `d3-logo-extruded-wordmark` | `d3-logo-diagonal-hatch` |
| `d3-logo-woven-initial-lockup` | `d3-logo-letter-weave` | `d3-logo-seeded-stipple` |
| `d3-logo-responsive-brand-family` | `d3-logo-responsive-lockup` | `d3-logo-guilloche-waves` |
| `d3-logo-spiral-core-lockup` | `d3-logo-spiral-trace` | `d3-logo-voronoi-mosaic` |
| `d3-logo-connected-orbit-lockup` | `d3-logo-orbit-network` | `d3-logo-woven-checker` |
| `d3-logo-modular-grid-lockup` | `d3-logo-grid-activation` | `d3-logo-directional-fibers` |
| `d3-logo-contour-medallion` | `d3-logo-contour-fingerprint` | `d3-logo-diagonal-hatch` |
| `d3-logo-voronoi-window-lockup` | `d3-logo-voronoi-shards` | `d3-logo-guilloche-waves` |
| `d3-logo-faceted-fauna-lockup` | `d3-logo-animal-facets` | `d3-logo-halftone-dots` |
| `d3-logo-surface-fauna-lockup` | `d3-logo-animal-surface-mask` | `d3-logo-topographic-lines` |
| `d3-logo-hidden-initial-lockup` | `d3-logo-negative-space-reveal` | `d3-logo-crosshatch` |
| `d3-logo-ribbon-fold-lockup` | `d3-logo-folded-ribbon` | `d3-logo-micro-grid` |
| `d3-logo-overlap-lens-lockup` | `d3-logo-boolean-lens` | `d3-logo-seeded-stipple` |
| `d3-logo-radiant-core-lockup` | `d3-logo-radiant-pulse` | `d3-logo-halftone-dots` |
| `d3-logo-harmonic-wave-lockup` | `d3-logo-parametric-wave` | `d3-logo-crosshatch` |
| `d3-logo-kaleidoscope-emblem` | `d3-logo-kaleidoscope-wedges` | `d3-logo-woven-checker` |
| `d3-logo-polar-data-lockup` | `d3-logo-polar-halo` | `d3-logo-voronoi-mosaic` |
| `d3-logo-iris-aperture-lockup` | `d3-logo-aperture-iris` | `d3-logo-topographic-lines` |

## Typography and responsive checks

Offer geometric sans, humanist sans, condensed sans, editorial serif, and monospaced system stacks. Accept a user-supplied licensed font-family stack through the engine API, but do not claim variable-axis support without checking the loaded font; otherwise use the explicit discrete fallback. Verify wide, stacked, and compact lockups; test 480 px, 240 px, and 96 px widths; and preserve a flat texture-free fallback.

# Composition Contract

Treat a finished composition as a complete lockup with a primary pattern, one registered texture, one colorset, typography, spacing, and responsive intent. A parameter change is not a new composition.

## Required data contract

Every composition must expose:

```text
compositionId, exampleId, patternId, textureId, brand, tagline, colorset,
fontFamily, density, curvature, scale, rotation, textureStrength,
seed, viewBox, accessibilityLabel
```

The compact catalog stores composition `id`, local technique `exampleId`, global `patternId`, and the font preset key `font`. Require `patternId === "d3-logo-" + exampleId`. `normalizeConfig()` maps `id` and `font` to runtime `compositionId` and `fontFamily`; `renderLogo()` applies the fixed `viewBox` and accessible title/description label. Validate the normalized SVG/runtime contract above rather than requiring those derived fields to be duplicated in each raw manifest record.

Follow the repository gallery convention: card `id` and `data-pattern-id` use the global technique ID, while `data-example` and `data-example-id` use its local slug. Keep the editorial composition ID only in `data-composition-id`. Show the global pattern ID visibly in the card header.

Use a deterministic integer seed. Keep `compositionId`, `exampleId`, `patternId`, and `textureId` lowercase hyphen-case and at most 64 characters.

## Text clearance

Text occlusion and omission are prohibited by default. Pattern-level exceptions must follow `text-clearance-contract.md`, remain limited to the named semantic roles and state, and keep every declared `maxOcclusionRatio` at or below 0.30. An absent or empty declaration means zero permitted occlusion or omission.

## Ninety acceptance compositions

| Composition ID | Local example ID | Global pattern ID | Default texture |
| --- | --- | --- | --- |
| `d3-logo-heritage-orbit-lockup` | `type-orbit` | `d3-logo-type-orbit` | `d3-logo-diagonal-hatch` |
| `d3-logo-rising-curve-lockup` | `bezier-wordpath` | `d3-logo-bezier-wordpath` | `d3-logo-directional-fibers` |
| `d3-logo-variable-editorial-lockup` | `variable-axis-wordmark` | `d3-logo-variable-axis-wordmark` | `d3-logo-micro-grid` |
| `d3-logo-joined-initial-lockup` | `ligature-bridge` | `d3-logo-ligature-bridge` | `d3-logo-crosshatch` |
| `d3-logo-stenciled-utility-lockup` | `stencil-cuts` | `d3-logo-stencil-cuts` | `d3-logo-seeded-stipple` |
| `d3-logo-textured-letter-window` | `letter-window` | `d3-logo-letter-window` | `d3-logo-voronoi-mosaic` |
| `d3-logo-mirror-axis-lockup` | `mirrored-monogram` | `d3-logo-mirrored-monogram` | `d3-logo-woven-checker` |
| `d3-logo-radial-glyph-emblem` | `glyph-rosette` | `d3-logo-glyph-rosette` | `d3-logo-guilloche-waves` |
| `d3-logo-wave-baseline-lockup` | `baseline-wave` | `d3-logo-baseline-wave` | `d3-logo-topographic-lines` |
| `d3-logo-echo-stack-lockup` | `stack-offset` | `d3-logo-stack-offset` | `d3-logo-halftone-dots` |
| `d3-logo-sliced-motion-lockup` | `slice-shift` | `d3-logo-slice-shift` | `d3-logo-directional-fibers` |
| `d3-logo-outline-signal-lockup` | `multi-stroke-wordmark` | `d3-logo-multi-stroke-wordmark` | `d3-logo-micro-grid` |
| `d3-logo-depth-step-lockup` | `extruded-wordmark` | `d3-logo-extruded-wordmark` | `d3-logo-diagonal-hatch` |
| `d3-logo-woven-initial-lockup` | `letter-weave` | `d3-logo-letter-weave` | `d3-logo-seeded-stipple` |
| `d3-logo-responsive-brand-family` | `responsive-lockup` | `d3-logo-responsive-lockup` | `d3-logo-guilloche-waves` |
| `d3-logo-spiral-core-lockup` | `spiral-trace` | `d3-logo-spiral-trace` | `d3-logo-voronoi-mosaic` |
| `d3-logo-connected-orbit-lockup` | `orbit-network` | `d3-logo-orbit-network` | `d3-logo-woven-checker` |
| `d3-logo-modular-grid-lockup` | `grid-activation` | `d3-logo-grid-activation` | `d3-logo-directional-fibers` |
| `d3-logo-contour-medallion` | `contour-fingerprint` | `d3-logo-contour-fingerprint` | `d3-logo-diagonal-hatch` |
| `d3-logo-voronoi-window-lockup` | `voronoi-shards` | `d3-logo-voronoi-shards` | `d3-logo-guilloche-waves` |
| `d3-logo-faceted-fauna-lockup` | `animal-facets` | `d3-logo-animal-facets` | `d3-logo-halftone-dots` |
| `d3-logo-surface-fauna-lockup` | `animal-surface-mask` | `d3-logo-animal-surface-mask` | `d3-logo-topographic-lines` |
| `d3-logo-hidden-initial-lockup` | `negative-space-reveal` | `d3-logo-negative-space-reveal` | `d3-logo-crosshatch` |
| `d3-logo-ribbon-fold-lockup` | `folded-ribbon` | `d3-logo-folded-ribbon` | `d3-logo-micro-grid` |
| `d3-logo-overlap-lens-lockup` | `boolean-lens` | `d3-logo-boolean-lens` | `d3-logo-seeded-stipple` |
| `d3-logo-radiant-core-lockup` | `radiant-pulse` | `d3-logo-radiant-pulse` | `d3-logo-halftone-dots` |
| `d3-logo-harmonic-wave-lockup` | `parametric-wave` | `d3-logo-parametric-wave` | `d3-logo-crosshatch` |
| `d3-logo-kaleidoscope-emblem` | `kaleidoscope-wedges` | `d3-logo-kaleidoscope-wedges` | `d3-logo-woven-checker` |
| `d3-logo-polar-data-lockup` | `polar-halo` | `d3-logo-polar-halo` | `d3-logo-voronoi-mosaic` |
| `d3-logo-iris-aperture-lockup` | `aperture-iris` | `d3-logo-aperture-iris` | `d3-logo-topographic-lines` |
| `d3-logo-terminal-rule-lockup` | `terminal-extension` | `d3-logo-terminal-extension` | `d3-logo-micro-grid` |
| `d3-logo-vertical-rail-lockup` | `vertical-rail-wordmark` | `d3-logo-vertical-rail-wordmark` | `d3-logo-diagonal-hatch` |
| `d3-logo-hinged-letter-lockup` | `hinged-glyph-fan` | `d3-logo-hinged-glyph-fan` | `d3-logo-crosshatch` |
| `d3-logo-justified-block-lockup` | `justified-word-block` | `d3-logo-justified-word-block` | `d3-logo-halftone-dots` |
| `d3-logo-cadence-type-lockup` | `fill-outline-cadence` | `d3-logo-fill-outline-cadence` | `d3-logo-seeded-stipple` |
| `d3-logo-punctuation-frame-lockup` | `punctuation-armature` | `d3-logo-punctuation-armature` | `d3-logo-topographic-lines` |
| `d3-logo-packed-cluster-lockup` | `circle-pack-cluster` | `d3-logo-circle-pack-cluster` | `d3-logo-voronoi-mosaic` |
| `d3-logo-treemap-mosaic-lockup` | `treemap-mosaic` | `d3-logo-treemap-mosaic` | `d3-logo-guilloche-waves` |
| `d3-logo-hull-shell-lockup` | `convex-hull-shells` | `d3-logo-convex-hull-shells` | `d3-logo-woven-checker` |
| `d3-logo-phyllotaxis-bloom-lockup` | `phyllotaxis-bloom` | `d3-logo-phyllotaxis-bloom` | `d3-logo-directional-fibers` |
| `d3-logo-tangent-chain-lockup` | `tangency-chain` | `d3-logo-tangency-chain` | `d3-logo-micro-grid` |
| `d3-logo-tangram-form-lockup` | `tangram-dissection` | `d3-logo-tangram-dissection` | `d3-logo-diagonal-hatch` |
| `d3-logo-superellipse-nest-lockup` | `superellipse-family` | `d3-logo-superellipse-family` | `d3-logo-crosshatch` |
| `d3-logo-isometric-stack-lockup` | `isometric-block-stack` | `d3-logo-isometric-block-stack` | `d3-logo-halftone-dots` |
| `d3-logo-euler-route-lockup` | `eulerian-one-stroke` | `d3-logo-eulerian-one-stroke` | `d3-logo-seeded-stipple` |
| `d3-logo-perfect-maze-lockup` | `perfect-maze` | `d3-logo-perfect-maze` | `d3-logo-topographic-lines` |
| `d3-logo-stream-routing-lockup` | `split-merge-stream` | `d3-logo-split-merge-stream` | `d3-logo-voronoi-mosaic` |
| `d3-logo-dendrogram-crown-lockup` | `dendrogram-crown` | `d3-logo-dendrogram-crown` | `d3-logo-guilloche-waves` |
| `d3-logo-ring-chain-lockup` | `linked-ring-chain` | `d3-logo-linked-ring-chain` | `d3-logo-woven-checker` |
| `d3-logo-lsystem-growth-lockup` | `lsystem-branch` | `d3-logo-lsystem-branch` | `d3-logo-directional-fibers` |
| `d3-logo-hilbert-route-lockup` | `hilbert-route` | `d3-logo-hilbert-route` | `d3-logo-micro-grid` |
| `d3-logo-profile-boundary-lockup` | `reciprocal-profiles` | `d3-logo-reciprocal-profiles` | `d3-logo-diagonal-hatch` |
| `d3-logo-gutter-symbol-lockup` | `modular-gutter-symbol` | `d3-logo-modular-gutter-symbol` | `d3-logo-crosshatch` |
| `d3-logo-central-void-lockup` | `tangent-void-star` | `d3-logo-tangent-void-star` | `d3-logo-halftone-dots` |
| `d3-logo-reciprocal-tile-lockup` | `reciprocal-tessellation` | `d3-logo-reciprocal-tessellation` | `d3-logo-seeded-stipple` |
| `d3-logo-impossible-beam-lockup` | `impossible-triangle` | `d3-logo-impossible-triangle` | `d3-logo-topographic-lines` |
| `d3-logo-necker-depth-lockup` | `necker-cube` | `d3-logo-necker-cube` | `d3-logo-voronoi-mosaic` |
| `d3-logo-kanizsa-closure-lockup` | `kanizsa-closure` | `d3-logo-kanizsa-closure` | `d3-logo-guilloche-waves` |
| `d3-logo-line-screen-lockup` | `line-screen-silhouette` | `d3-logo-line-screen-silhouette` | `d3-logo-woven-checker` |
| `d3-logo-perspective-portal-lockup` | `perspective-portal` | `d3-logo-perspective-portal` | `d3-logo-directional-fibers` |
| `d3-logo-reuleaux-body-lockup` | `reuleaux-body` | `d3-logo-reuleaux-body` | `d3-logo-micro-grid` |
| `d3-logo-cassini-oval-lockup` | `cassini-oval` | `d3-logo-cassini-oval` | `d3-logo-diagonal-hatch` |
| `d3-logo-polar-reciprocal-lockup` | `polar-reciprocal` | `d3-logo-polar-reciprocal` | `d3-logo-crosshatch` |
| `d3-logo-minkowski-sum-lockup` | `minkowski-sum` | `d3-logo-minkowski-sum` | `d3-logo-halftone-dots` |
| `d3-logo-pedal-curve-lockup` | `pedal-curve` | `d3-logo-pedal-curve` | `d3-logo-seeded-stipple` |
| `d3-logo-involute-gear-lockup` | `involute-gear` | `d3-logo-involute-gear` | `d3-logo-topographic-lines` |
| `d3-logo-desargues-incidence-lockup` | `desargues-incidence` | `d3-logo-desargues-incidence` | `d3-logo-voronoi-mosaic` |
| `d3-logo-circle-inversion-lockup` | `circle-inversion` | `d3-logo-circle-inversion` | `d3-logo-guilloche-waves` |
| `d3-logo-catenary-funicular-lockup` | `catenary-funicular` | `d3-logo-catenary-funicular` | `d3-logo-woven-checker` |
| `d3-logo-joukowski-airfoil-lockup` | `joukowski-airfoil` | `d3-logo-joukowski-airfoil` | `d3-logo-directional-fibers` |
| `d3-logo-hyperbolic-geodesics-lockup` | `hyperbolic-geodesics` | `d3-logo-hyperbolic-geodesics` | `d3-logo-micro-grid` |
| `d3-logo-elliptic-group-law-lockup` | `elliptic-group-law` | `d3-logo-elliptic-group-law` | `d3-logo-diagonal-hatch` |
| `d3-logo-mobius-strip-lockup` | `mobius-strip` | `d3-logo-mobius-strip` | `d3-logo-crosshatch` |
| `d3-logo-torus-knot-lockup` | `torus-knot` | `d3-logo-torus-knot` | `d3-logo-halftone-dots` |
| `d3-logo-ruled-hyperboloid-lockup` | `ruled-hyperboloid` | `d3-logo-ruled-hyperboloid` | `d3-logo-seeded-stipple` |
| `d3-logo-tensegrity-prism-lockup` | `tensegrity-prism` | `d3-logo-tensegrity-prism` | `d3-logo-topographic-lines` |
| `d3-logo-maxwell-reciprocal-lockup` | `maxwell-reciprocal` | `d3-logo-maxwell-reciprocal` | `d3-logo-voronoi-mosaic` |
| `d3-logo-medial-axis-lockup` | `medial-axis` | `d3-logo-medial-axis` | `d3-logo-guilloche-waves` |
| `d3-logo-string-parabola-lockup` | `string-parabola` | `d3-logo-string-parabola` | `d3-logo-woven-checker` |
| `d3-logo-circle-caustic-lockup` | `circle-caustic` | `d3-logo-circle-caustic` | `d3-logo-directional-fibers` |
| `d3-logo-moire-beat-lockup` | `moire-beat` | `d3-logo-moire-beat` | `d3-logo-micro-grid` |
| `d3-logo-peaucellier-linkage-lockup` | `peaucellier-linkage` | `d3-logo-peaucellier-linkage` | `d3-logo-diagonal-hatch` |
| `d3-logo-lorenz-attractor-lockup` | `lorenz-attractor` | `d3-logo-lorenz-attractor` | `d3-logo-crosshatch` |
| `d3-logo-affine-ifs-lockup` | `affine-ifs` | `d3-logo-affine-ifs` | `d3-logo-halftone-dots` |
| `d3-logo-cellular-automaton-lockup` | `cellular-automaton` | `d3-logo-cellular-automaton` | `d3-logo-seeded-stipple` |
| `d3-logo-logistic-bifurcation-lockup` | `logistic-bifurcation` | `d3-logo-logistic-bifurcation` | `d3-logo-topographic-lines` |
| `d3-logo-field-streamlines-lockup` | `field-streamlines` | `d3-logo-field-streamlines` | `d3-logo-voronoi-mosaic` |
| `d3-logo-newton-basin-lockup` | `newton-basin` | `d3-logo-newton-basin` | `d3-logo-guilloche-waves` |
| `d3-logo-steiner-tree-lockup` | `steiner-tree` | `d3-logo-steiner-tree` | `d3-logo-woven-checker` |
| `d3-logo-penrose-substitution-lockup` | `penrose-substitution` | `d3-logo-penrose-substitution` | `d3-logo-directional-fibers` |

## Typography and responsive checks

Offer geometric sans, humanist sans, condensed sans, editorial serif, and monospaced system stacks. Accept a user-supplied licensed font-family stack through the engine API, but do not claim variable-axis support without checking the loaded font; otherwise use the explicit discrete fallback. Verify wide, stacked, and compact lockups; test 480 px, 240 px, and 96 px widths; and preserve a flat texture-free fallback.

# Palette-safe Texture Catalog

Textures are secondary fills or strokes. Every texture must remain deterministic, use only tokens from the active colorset, expose its canonical ID through `data-texture-id`, and retain a flat fallback fill.

| ID | Construction | Adjustable parameters | Avoid when |
| --- | --- | --- | --- |
| `d3-logo-micro-grid` | Tiled square grid in an SVG `pattern`. | tile size, subdivision, line width, angle | the mark already uses a dense cell grid |
| `d3-logo-diagonal-hatch` | One repeated diagonal line family. | pitch, angle, dash rhythm, line width | thin glyph counters collapse |
| `d3-logo-crosshatch` | Two opposing hatch families. | two angles, pitch, hierarchy, line width | the symbol has many intersections |
| `d3-logo-halftone-dots` | Repeated circles with deterministic radius modulation. | cell size, radius range, screen angle | smallest output is below 128 px wide |
| `d3-logo-seeded-stipple` | Seeded points inside the target fill. | density, radius range, minimum distance, seed | the silhouette relies on tiny negative spaces |
| `d3-logo-topographic-lines` | Repeated contour-like paths from a procedural field. | thresholds, spacing, smoothing, seed | the primary pattern is contour fingerprint |
| `d3-logo-voronoi-mosaic` | Deterministic cell fragments with discrete palette assignment. | site count, gap, seed, role sequence | the primary pattern is Voronoi shards |
| `d3-logo-guilloche-waves` | Phase-shifted harmonic lines. | frequency, amplitude, phase step, line count | the primary pattern already uses a wave baseline |
| `d3-logo-woven-checker` | Orthogonal bands with alternating over/under cells. | tile size, band width, crossing schedule | the primary pattern is letter weave |
| `d3-logo-directional-fibers` | Short parallel strokes with seeded displacement. | spacing, direction, displacement, length, seed | a crisp institutional seal is required |

## Tuning rule

Start at texture strength 0.35 and density 1.0. At a 96 px-wide preview, compare the textured result with the flat fallback. If the silhouette, brand text, or counters become less recognizable, reduce strength first, then density, then remove the texture.

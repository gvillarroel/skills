# Palette-safe Texture Catalog

Textures are secondary fills or strokes. Every texture must remain deterministic, use only exact tokens from the active colorset, expose its canonical ID through `data-texture-id`, and retain a flat fallback fill. Place texture behind primary brand text or clip it inside the symbol; never allow it to obscure the reading path.

Use `palette.roles.*` and `palette.sequence[n]` as paint sources. Do not calculate colors or introduce gradients, blend modes, filters, named colors, or external imagery. Derive pseudo-random geometry from the configured seed plus the texture ID so the same inputs always reproduce the same output.

## Runtime control mapping

The table lists each mechanism's construction variables, not additional public API fields. Use the supported shared runtime controls to honor user adjustments consistently; a renderer may use only the controls that materially affect its mechanism.

| User request | Runtime input |
| --- | --- |
| tighter cells, smaller modules, narrower pitch, more repeats | increase `density` |
| looser cells, larger modules, wider pitch, fewer repeats | decrease `density` |
| softer bends, deeper lobes, stronger wave or stitch tension | increase `curvature` |
| straighter paths, shallower lobes, more rigid geometry | decrease `curvature` |
| stronger ink, coverage, relief, or foreground contrast | increase `textureStrength` |
| quieter ink, coverage, relief, or foreground contrast | decrease `textureStrength` |
| different phase, row offset, parity, route, scatter, or encoded cadence | change `seed` |
| different barcode, microtype, Morse, or seven-segment message | change `brand` |

Call `D3LogoDesign.renderTexture(svg, {textureId, colorset, density, curvature, textureStrength, seed, brand})` for an isolated swatch, or pass the same texture fields to `renderLogo`. If a request needs a construction variable that cannot be represented by this mapping, extend that renderer and both validators rather than silently ignoring the request.

Before promising a control response, compare two rendered states in the atlas or inspect the selected renderer. Do not claim that changing `seed` or `curvature` affects a texture when its geometry is fixed by parity or a static motif.

## Core geometric, line, and print textures

| ID | Family | Construction | Adjustable parameters | Avoid when |
| --- | --- | --- | --- | --- |
| `d3-logo-micro-grid` | geometric | Tiled square grid with optional subdivisions. | tile size, subdivision, line width, angle | the mark already uses a dense cell grid |
| `d3-logo-diagonal-hatch` | linework | One evenly spaced diagonal stroke family. | pitch, angle, dash rhythm, line width | narrow glyph counters could collapse |
| `d3-logo-crosshatch` | linework | Two opposing stroke families. | primary angle, secondary angle, pitch, line width | the symbol already contains many intersections |
| `d3-logo-halftone-dots` | print | Regular dot screen with deterministic radius modulation. | cell size, radius range, screen angle | the smallest output is below 128 pixels wide |
| `d3-logo-seeded-stipple` | print | Repeatable seeded point field. | density, radius range, minimum distance, seed | the silhouette depends on tiny negative spaces |
| `d3-logo-topographic-lines` | linework | Procedural contour-like paths. | threshold count, spacing, smoothing, seed | the primary pattern is already a contour fingerprint |
| `d3-logo-voronoi-mosaic` | geometric | Seeded space-filling cells with discrete palette assignment. | site count, cell gap, seed, role sequence | the primary pattern already uses Voronoi shards |
| `d3-logo-guilloche-waves` | ornamental | Phase-shifted harmonic line families. | frequency, amplitude, phase step, line count | the primary pattern already uses a wave baseline |
| `d3-logo-woven-checker` | textile | Orthogonal bands with alternating crossing order. | tile size, band width, crossing schedule, rotation | the primary mark already uses a letter weave |
| `d3-logo-directional-fibers` | organic | Parallel short strokes with seeded displacement. | spacing, direction, displacement, length, seed | a crisp institutional seal is required |

## Geometric and textile extensions

| ID | Family | Construction | Adjustable parameters | Avoid when |
| --- | --- | --- | --- | --- |
| `d3-logo-hex-cell-lattice` | geometric | Staggered regular hexagon outlines. | cell radius, gap, line width, row offset, rotation | the mark already relies on honeycomb or hexagonal geometry |
| `d3-logo-triangle-flip-tiles` | geometric | Equilateral facets filled by orientation and grid parity. | edge length, gap, fill cadence, rotation, sequence offset | small counters cannot preserve the facet rhythm |
| `d3-logo-truchet-arc-links` | geometric | Seed-selected quarter-circle tiles joined into flowing routes. | tile size, arc radius, line width, seed, rotation | the symbol already contains routed arc networks |
| `d3-logo-houndstooth-blocks` | textile | Offset notched houndstooth polygons. | module size, tooth depth, row offset, gap, rotation | a quiet or minimal luxury treatment is required |
| `d3-logo-argyle-diamonds` | textile | Staggered filled diamonds with sparse seam threads. | diamond width, diamond height, row shift, seam width, sequence cadence | the logo already contains dominant diamond geometry |
| `d3-logo-running-brick-bond` | geometric | Rectangles arranged in half-offset masonry rows. | brick ratio, row height, mortar gap, row phase, rotation | rigid masonry cues conflict with the brand personality |
| `d3-logo-isometric-cube-tiles` | geometric | Three-rhombus axonometric cube units. | module size, skew angle, face gap, cube spacing, rotation | the primary mark already uses an isometric block stack |
| `d3-logo-greek-key-meander` | ornamental | Seamless continuous orthogonal fret path. | step size, inset, line width, turn period, rotation | the fill area is too narrow to show complete turns |
| `d3-logo-chainmail-rings` | textile | Split ring arcs with alternating over-under order. | ring radius, link spacing, line width, overlap phase, rotation | crossings would compete with thin lettering |
| `d3-logo-seigaiha-fans` | ornamental | Staggered discrete fans made from nested semicircles. | fan radius, ring count, row overlap, line width, phase | wave or heritage associations are undesirable |
| `d3-logo-knit-v-loops` | textile | Interlocking curved V-stitches in staggered rows. | loop width, loop height, tension, stitch pitch, line width | textile or handcrafted cues are inappropriate |
| `d3-logo-pinwheel-quilt` | textile | Four rotated triangle patches per repeating block. | block size, center offset, triangle gap, rotation, color cadence | multiple palette faces make the mark visually busy |
| `d3-logo-star-kite-lattice` | ornamental | Eight-point stars surrounded by deterministic kite polygons. | star radius, kite length, gap, line width, rotation | the silhouette is too small to preserve star points |
| `d3-logo-chevron-bands` | geometric | Closed filled zigzag ribbons. | pitch, band thickness, point depth, spacing, rotation | the primary mark already has aggressive directional motion |
| `d3-logo-pixel-staircase` | digital | Integer-aligned rectangles assembled into diagonal stair bands. | cell size, run, rise, band width, phase, rotation | the identity should feel organic or handcrafted |

## Material, organic, and encoded extensions

| ID | Family | Construction | Adjustable parameters | Avoid when |
| --- | --- | --- | --- | --- |
| `d3-logo-terrazzo-chips` | material | Independent seeded angular chips on a flat substrate. | chip count, size range, elongation, minimum gap, seed | the primary form already uses polygon fragments |
| `d3-logo-linocut-gouges` | print | Tapered curved negative cuts carved from a flat field. | gouge count, length, taper, curvature, direction, seed | pristine geometric precision is central to the identity |
| `d3-logo-letterpress-slippage` | print | A compact stamp plus a controlled offset second impression. | stamp motif, x offset, y offset, impression size, repeat pitch, rotation | registration error would undermine a precision-focused brand |
| `d3-logo-dry-roller-bands` | print | Broad bands broken into seeded ink runs and substrate gaps. | band height, coverage ratio, break count, direction, seed | distressed texture weakens small-size recognition |
| `d3-logo-embossed-lozenges` | material | Exact light and dark palette faces offset around a central lozenge. | lozenge size, bevel depth, gap, light direction, rotation | flat one-color reproduction is the primary delivery mode |
| `d3-logo-camouflage-islands` | organic | Seeded closed radial blobs combined into organic islands. | island count, lobe count, radius range, overlap, seed, rotation | camouflage, outdoor, or tactical associations are undesirable |
| `d3-logo-leaf-vein-repeat` | organic | Leaf silhouettes with a midrib and mirrored secondary veins. | leaf size, vein count, vein slant, row offset, line width, rotation | botanical or sustainability cues would be misleading |
| `d3-logo-pinecone-scales` | organic | Pointed lens scales in staggered overlapping rows. | scale width, scale height, overlap, row offset, gap, rotation | the mark already uses feather, scale, or petal geometry |
| `d3-logo-coral-branchlets` | organic | Connected colonies generated by bounded recursive forks. | recursion depth, branch ratio, fork angle, stem width, seed | thin branches cannot survive the smallest reproduction |
| `d3-logo-circuit-traces` | technical | Seeded orthogonal routes with compact terminal pads. | grid step, trace count, bend count, line width, pad radius, seed | electronics associations do not support the brief |
| `d3-logo-barcode-cadence` | encoded | Brand-hash-derived variable-width bar runs. | source text, module width, bar height, quiet zone, checksum length, rotation | barcode or retail associations distract from the brand |
| `d3-logo-microtype-ribbons` | typographic | Supplied brand copy repeated in offset microtype rows. | source text, font stack, font size, tracking, row pitch, angle | texture copy cannot remain secondary to the wordmark |
| `d3-logo-morse-stripes` | encoded | Supplied copy converted through a fixed Morse table into dot-dash rows. | source text, unit size, dash ratio, character gap, row pitch, inversion | the encoding could be mistaken for unreadable primary text |
| `d3-logo-radial-calibration` | technical | Repeated dial motifs with discrete rings and major-minor ticks. | dial radius, tick count, major cadence, ring count, line width, phase | measurement or precision cues conflict with the brief |
| `d3-logo-seven-segment-code` | digital | Brand-hash-selected digits rendered through a fixed seven-segment map. | source text, seed, digit count, cell size, segment thickness, row shift | a retro-digital display aesthetic is inappropriate |

## Distinction rules

- Keep terrazzo chips independent and non-space-filling; Voronoi cells must remain space-filling.
- Keep Seigaiha as discrete nested fans; guilloche uses continuous phase-shifted waves.
- Build chevrons as closed filled ribbons; hatches use strokes.
- Make knit and chainmail prove alternating crossing order; woven checker uses orthogonal rectangular bands.
- Make Morse, barcode, microtype, and seven-segment textures encode the supplied copy or seed deterministically.
- Use negative tapered cuts for linocut and broad broken coverage for dry roller; neither may degrade into point or fiber scatter.

## Tuning rule

Start at texture strength 0.35 and density 1.0. At a 96-pixel-wide preview, compare the textured result with the flat fallback. If the silhouette, brand text, or counters become less recognizable, reduce strength first, then density, then remove the texture.

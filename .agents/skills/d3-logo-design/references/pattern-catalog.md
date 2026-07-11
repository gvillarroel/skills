# Canonical Logo Pattern Catalog

Choose one primary pattern per mark. Parameters are adjustment surfaces, not separate patterns. Keep the canonical ID in `data-pattern-id` on the composition container and rendered SVG.

## Typographic systems

| ID | Mechanism | Best for | Primary parameters |
| --- | --- | --- | --- |
| `d3-logo-type-orbit` | Put brand text on a circular or partial-arc `textPath`. | Seals, badges, community marks | radius, sweep, start offset, direction, tracking |
| `d3-logo-bezier-wordpath` | Set the wordmark along an open cubic spline. | Motion, travel, service brands | control points, curvature, baseline offset, tracking |
| `d3-logo-variable-axis-wordmark` | Modulate verified variable-font axes across glyphs; use the bundled discrete weight/size/tracking fallback when axis support is unknown. | Flexible typographic identities | supported axes, per-glyph mapping, fallback weights, state sequence |
| `d3-logo-ligature-bridge` | Join two initials with a generated shared connector. | Partnerships, networks, initials | anchors, bridge thickness, bend, terminal style |
| `d3-logo-stencil-cuts` | Subtract rhythmic geometric incisions from a wordmark. | Industrial, civic, sports cues | cut count, angle, width, protected counters |
| `d3-logo-letter-window` | Use a word or initial as a clip that reveals a palette surface or texture. | Editorial and image-like identities | crop anchor, texture, scale, padding |
| `d3-logo-mirrored-monogram` | Reflect or rotate a glyph copy around a shared axis. | Symmetry, premium, compact marks | axis, rotation, overlap, gap, join mode |
| `d3-logo-glyph-rosette` | Repeat one glyph or symbol radially. | Craft, culture, collective marks | count, radius, orientation, alternating scale |
| `d3-logo-baseline-wave` | Position letters along a harmonic or spline baseline. | Sound, water, motion, youth | amplitude, frequency, phase, rotation, tracking |
| `d3-logo-stack-offset` | Layer repeated wordmark copies along a vector or curve. | Campaign graphics, energy, motion | copy count, offset, direction, scale decay |
| `d3-logo-slice-shift` | Clip a wordmark into bands and displace selected slices. | Digital, speed, disruption | slice count, angle, displacement, alternation |
| `d3-logo-multi-stroke-wordmark` | Reuse one wordmark with multiple stroke widths and dash rhythms. | Signals, technical systems, events | layers, widths, dash arrays, phase |
| `d3-logo-extruded-wordmark` | Build flat pseudo-depth from translated text copies. | Dimensional, architectural cues | depth, projection angle, steps, outline |
| `d3-logo-letter-weave` | Interlace two initial paths with alternating over/under masks. | Collaboration, textiles, continuity | initials, path width, crossing order, gap |
| `d3-logo-responsive-lockup` | Recompose one symbol and wordmark into wide, stacked, and compact states. | Product families and responsive identity | aspect ratio, breakpoint, hierarchy, spacing |
| `d3-logo-terminal-extension` | Extend selected glyph terminals into structural rules that remain attached to their source letters. | Editorial, architectural, directional identities | terminal choice, extension length, rule weight, corner treatment |
| `d3-logo-vertical-rail-wordmark` | Stack glyphs on a shared vertical reading rail instead of rotating a horizontal wordmark. | Tall formats, wayfinding, compact side marks | rail side, glyph spacing, alignment, rail weight |
| `d3-logo-hinged-glyph-fan` | Pivot successive glyphs from a common baseline hinge to create a readable opening fan. | Events, publishing, expressive motion | pivot, angle sequence, overlap, tracking |
| `d3-logo-justified-word-block` | Measure multiple words and adjust tracking so every line resolves to one shared width. | Editorial, civic, modular identities | line breaks, target width, leading, tracking bounds |
| `d3-logo-fill-outline-cadence` | Alternate filled and outlined glyph treatments across one continuous wordmark. | Fashion, music, rhythmic campaign marks | cadence, stroke width, start phase, tracking |
| `d3-logo-punctuation-armature` | Scale punctuation from measured text bounds into a frame that supports the wordmark. | Editorial, quotation, language-focused brands | punctuation pair, frame offset, scale, stroke weight |

## Geometric and generative systems

| ID | Mechanism | Best for | Primary parameters |
| --- | --- | --- | --- |
| `d3-logo-spiral-trace` | Trace a point whose radius changes as its angle advances. | Energy, systems, discovery | turns, radial law, phase, sampling, taper |
| `d3-logo-orbit-network` | Arrange satellites around a core and connect selected relationships. | Platforms, communities, ecosystems | node count, radii, link rule, phase |
| `d3-logo-grid-activation` | Activate cells or line segments on a modular grid to form a mark. | Technology, infrastructure, modularity | rows, columns, density, activation rule, seed |
| `d3-logo-contour-fingerprint` | Generate scalar-field contours clipped to a badge or letter. | Terrain, uniqueness, data, place | thresholds, smoothing, field scale, seed |
| `d3-logo-voronoi-shards` | Partition a silhouette into deterministic Voronoi cells. | Networks, fragments, transformation | sites, relaxation, gaps, seed, role assignment |
| `d3-logo-animal-facets` | Triangulate points inside an original generic animal silhouette. | Wildlife, outdoor, team identity | silhouette, point count, jitter, facet gaps, seed |
| `d3-logo-animal-surface-mask` | Use an original generic animal silhouette as a mask over bands or texture. | Nature products and animal cues | silhouette, surface, crop, direction, bands, seed |
| `d3-logo-negative-space-reveal` | Arrange opaque primitives so subtraction reveals a hidden initial. | Clever compact marks and discovery | primitives, overlap, subtraction, simplification |
| `d3-logo-folded-ribbon` | Construct a continuous wide path with explicit folds and occlusion. | Continuity, service journeys, momentum | control points, width, folds, crossing order |
| `d3-logo-boolean-lens` | Let the overlap of two meaningful shapes form a third central mark. | Partnerships, synthesis, focus | shape pair, offset, scale, intersection role |
| `d3-logo-radiant-pulse` | Emit variable rays from a central core. | Broadcast, celebration, activation | ray count, length function, gaps, symmetry |
| `d3-logo-parametric-wave` | Draw a closed Lissajous or harmonic symbol. | Audio, science, movement, fluidity | frequencies, amplitudes, phase, samples |
| `d3-logo-kaleidoscope-wedges` | Mirror one motif into radial sectors. | Culture, beauty, craft, events | sector count, motif, reflection, radius, rotation |
| `d3-logo-polar-halo` | Surround a wordmark or monogram with data-driven arc segments. | Metrics, cycles, time, systems | segments, values, radii, gaps, ordering |
| `d3-logo-aperture-iris` | Overlap curved blades around a variable negative-space opening. | Imaging, focus, precision, optics | blade count, curvature, aperture, twist, overlap |
| `d3-logo-circle-pack-cluster` | Enclose a weighted hierarchy as nested, non-overlapping circles. | Communities, portfolios, family systems | hierarchy, value weights, padding, depth roles |
| `d3-logo-treemap-mosaic` | Recursively subdivide a rectangle into value-weighted hierarchical cells. | Platforms, collections, modular systems | hierarchy, tiling method, padding, weight distribution |
| `d3-logo-convex-hull-shells` | Peel deterministic point sets into successive convex hull boundaries. | Protection, layers, collective identity | point count, shell count, jitter, inset rule |
| `d3-logo-phyllotaxis-bloom` | Place discs in a golden-angle sequence so density grows without radial spokes. | Growth, nature, research, discovery | disc count, radial law, disc scale, phase |
| `d3-logo-tangency-chain` | Solve a sequence of circles that touch neighbors without overlapping. | Continuity, precision, connected products | circle count, radius sequence, chain path, endpoint rule |
| `d3-logo-tangram-dissection` | Assemble a silhouette from a fixed rule-based polygon dissection. | Learning, transformation, modular craft | target silhouette, piece transform, gap, ordering |
| `d3-logo-superellipse-family` | Nest Lamé curves while varying the exponent between diamond, circle, and rounded-square states. | Flexible products, surfaces, soft technology | exponent sequence, radii, nesting gap, rotation |
| `d3-logo-isometric-block-stack` | Aggregate axonometric cube faces on a discrete three-axis lattice. | Construction, infrastructure, spatial systems | cell coordinates, height, face roles, gap |
| `d3-logo-eulerian-one-stroke` | Trace an Euler circuit that visits every graph edge exactly once. | Journeys, networks, continuous service | graph topology, start node, routing order, line caps |
| `d3-logo-perfect-maze` | Carve corridors from a spanning tree so every pair of cells has one route. | Discovery, strategy, navigation | rows, columns, generator seed, entrance and exit |
| `d3-logo-split-merge-stream` | Route conserved bands through explicit split and merge junctions. | Pipelines, orchestration, multi-service systems | stream count, weights, junction positions, curvature |
| `d3-logo-dendrogram-crown` | Convert a hierarchy into branching cluster links that form a crown silhouette. | Lineage, portfolios, knowledge systems | hierarchy, link curve, branch spacing, depth |
| `d3-logo-linked-ring-chain` | Interlock separate closed rings with alternating visible crossing segments. | Partnership, durability, connected communities | ring count, spacing, stroke width, crossing order |
| `d3-logo-lsystem-branch` | Expand a grammar and interpret it with turtle turns to grow a deterministic branching mark. | Ecology, learning, generative craft | axiom, production rules, iterations, turn angle |
| `d3-logo-hilbert-route` | Traverse a square through one continuous recursive space-filling path. | Locality, coverage, compact data systems | recursion order, inset, stroke width, corner style |
| `d3-logo-reciprocal-profiles` | Pair facing silhouettes around one shared boundary so each side completes the other. | Dialogue, mediation, human-centered services | profile curve, separation, symmetry, role assignment |
| `d3-logo-modular-gutter-symbol` | Arrange solid modules so the consistent gutters, rather than the modules, define the central symbol. | Architecture, platforms, negative-space identity | module grid, gutter width, omitted cells, corner radius |
| `d3-logo-tangent-void-star` | Position tangent primitives around a central void whose boundary reads as a star. | Collective energy, discovery, compact emblems | primitive count, radius, tangent distance, void sharpness |
| `d3-logo-reciprocal-tessellation` | Tile interlocking figure-ground shapes so either color role can become the foreground. | Exchange, duality, circular systems | tile motif, rows, columns, alternation, edge crop |
| `d3-logo-impossible-triangle` | Layer three beams with cyclic occlusion so depth order cannot resolve globally. | Paradox, invention, conceptual technology | beam width, corner angle, overlap gaps, orientation |
| `d3-logo-necker-cube` | Draw a bistable wireframe cube whose front and back faces can reverse perceptually. | Perspective, ambiguity, spatial products | projection, depth offset, edge emphasis, rotation |
| `d3-logo-kanizsa-closure` | Place cut-out inducers so the eye completes an unpainted central contour. | Insight, perception, minimal identity | inducer count, aperture angle, radius, implied shape |
| `d3-logo-line-screen-silhouette` | Vary gaps within parallel lines so their segmentation encodes a coherent silhouette. | Media, scanning, signal, security | line count, silhouette, gap width, phase |
| `d3-logo-perspective-portal` | Nest offset quadrilateral frames toward a controlled vanishing region. | Access, transition, spatial experience | frame count, convergence, inset progression, skew |

## Originality gate

Do not count a new font, word, color sequence, rotation, or texture as a new pattern. A new pattern must change the construction mechanism, topology, masking relationship, or responsive behavior. For animal work, use original procedural paths or user-supplied licensed SVG paths; never trace a trademark, mascot, or campaign asset.

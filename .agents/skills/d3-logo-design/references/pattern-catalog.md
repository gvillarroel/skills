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

## Originality gate

Do not count a new font, word, color sequence, rotation, or texture as a new pattern. A new pattern must change the construction mechanism, topology, masking relationship, or responsive behavior. For animal work, use original procedural paths or user-supplied licensed SVG paths; never trace a trademark, mascot, or campaign asset.

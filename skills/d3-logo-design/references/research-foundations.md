# Research Foundations

Use these sources to justify mechanisms and implementation choices. Abstract the technique; never reproduce a case-study mark.

## SVG and D3 foundations

- [W3C SVG 2 text and text-on-path](https://www.w3.org/TR/SVG/text.html): text can follow a path and remains compatible with transforms, clipping, and masking.
- [W3C SVG rendering, clipping, and masking](https://www.w3.org/TR/SVG/render.html): use clipping and masks for letter windows, silhouette surfaces, and negative-space constructions.
- [W3C SVG Strokes](https://www.w3.org/TR/svg-strokes/): use stroke width, dash rhythm, joins, and caps for multi-stroke and line-based identities.
- [W3C Filter Effects Level 1](https://www.w3.org/TR/filter-effects-1/): when filters are necessary, use them as alpha/geometry operations while preserving palette-token paints.
- [MDN SVG pattern element](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/pattern): tile palette-safe vector textures with reusable pattern paint servers.
- [W3C CSS Fonts Level 4](https://www.w3.org/TR/css-fonts-4/): check actual font support before exposing variable axes.
- [Official d3-shape documentation](https://d3js.org/d3-shape): use data-driven arcs, radial lines, areas, curves, links, and symbols.
- [Official d3-path documentation](https://d3js.org/d3-path): generate deterministic custom paths.
- [Official d3-contour documentation](https://d3js.org/d3-contour): derive fingerprint and topographic geometry from scalar fields.
- [Official D3 Delaunay and Voronoi documentation](https://d3js.org/d3-delaunay): partition and triangulate deterministic point sets for shards and facets.
- [Official d3-force simulation documentation](https://d3js.org/d3-force/simulation): pre-tick seeded networks or packed marks; never leave export geometry nondeterministic.
- [Official D3 hierarchy documentation](https://d3js.org/d3-hierarchy): use hierarchy, pack, treemap, and cluster layouts when enclosure, recursive subdivision, or ancestry is the actual construction mechanism.
- [Official D3 circle-pack documentation](https://d3js.org/d3-hierarchy/pack): derive tangent enclosure from explicit hierarchical values rather than treating arbitrary circles as decoration.
- [Official D3 treemap documentation](https://d3js.org/d3-hierarchy/treemap): generate weighted recursive rectangular partitions with deterministic tiling and padding.
- [Official D3 polygon documentation](https://d3js.org/d3-polygon): compute convex hulls and polygon predicates for combinatorial shells, clipping checks, and dissection systems.
- [W3C SVG 2 text layout](https://www.w3.org/TR/SVG2/text.html): use per-glyph positioning, rotation, measured length, and `textLength` calibration for structural typography without converting editable copy into an inaccessible picture.

## Perceptual foundations

- [Kanizsa illusory-contour research](https://pmc.ncbi.nlm.nih.gov/articles/PMC8231925/): oriented inducers can produce a perceived contour where no physical boundary is drawn; keep the implied region empty and the inducers clearly separated.
- [Necker-cube bistability research](https://pmc.ncbi.nlm.nih.gov/articles/PMC5507912/): one unchanged wireframe can support two depth interpretations; preserve geometric ambiguity instead of resolving it with shading.
- [Figure-ground reversal research](https://pmc.ncbi.nlm.nih.gov/articles/PMC3761598/): reciprocal boundaries can alternate which region reads as figure; balance both sides instead of treating background as leftover space.

## Deployed dynamic-identity precedents

These professional identity systems show that parametrization, motion, grids, ribbons, masks, and generative geometry are deployable brand mechanisms. They do not prove that a technique alone caused campaign success.

- [Pentagram: EDP](https://www.pentagram.com/work/edp) — spiral and motion-derived identity behavior.
- [Pentagram: Platform](https://www.pentagram.com/work/platform) — extensible wordmark transformations.
- [Pentagram: Wyth](https://www.pentagram.com/work/wyth) — data-driven typographic position, scale, and rotation.
- [Pentagram: Isomorphic Labs](https://www.pentagram.com/work/isomorphic-labs) — reconfiguring cubes and generative grids.
- [Pentagram: Intrinsic](https://www.pentagram.com/work/intrinsic) — a parameterized generative identity tool.
- [Pentagram: KPIT](https://www.pentagram.com/work/kpit) — activated grids and patterned reveal systems.
- [Pentagram: Tractable](https://www.pentagram.com/work/tractable/story) — a ribbon that extends, contracts, and oscillates.
- [Pentagram: Sustainability Solutions Group](https://www.pentagram.com/work/sustainability-solutions-group) — variable typography and intertwining forms.
- [Pentagram: Hartbeat](https://www.pentagram.com/work/hartbeat) — intersecting geometry and radiating linework.
- [Pentagram: Untapped](https://www.pentagram.com/work/untapped) — a reusable spiral/profile motif with varied crops.

## Practical inference

The reusable lesson is to design a stable identity grammar with controlled variation, not a collection of unrelated marks. Keep one invariant anchor—name, monogram, silhouette, grid, or curve—while exposing only the parameters that can change without losing recognition.

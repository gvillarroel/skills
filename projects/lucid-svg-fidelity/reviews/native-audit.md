# Native reconstruction fidelity audit

Date: 2026-10-07. Scope: the current `skills/lucidchart-svg/scripts/build_native.py` and the naturalistic/generalization `final-luna-1` source SVG, recovered graph, document JSON, and `.lucid` package. This is a local structural comparison, not a rendered Lucid fidelity measurement.

The native route preserves explicit diagram meaning and basic geometry well in these two small fixtures. It does not preserve arbitrary SVG artwork. The compiler consumes the recovered JSON graph, not the SVG; extraction accuracy depends on the agent or supplied semantic data. Unsupported graph fields fail rather than silently passing through.

## Measured fixture results

| Property | Naturalistic final1: approval | Generalization final1: incident |
|---|---|---|
| Literal labels present in native JSON | 4/4, including `Request & review` and `yes` | 4/4, including `Resolve <P1>` and `SLA: 30 min` |
| Recovered nodes / native shapes | 3/3 | 4/4 |
| Directed semantic edges | 2/2 | 2/2 |
| Node bounding boxes matching source | 3/3 | 4/4 after resolving `translate(10 20)` |
| Absolute connector endpoints matching source | 2/2 | 2/2; explicit vertical bottom/top ports |
| Primitive fill and border colors | 3/3 each | 3/3 each; the fourth object is text |
| Literal text colors | 4/4 across nodes and edge label | 4/4 |
| Original SVG groups retained as native groups | 0/3 | 0/4, including the outer translation group |
| Original canvas vs native page | `500x180` becomes `512x152` | `400x500` becomes `422x432` |
| Target arrowheads | 2 introduced; source has none | 2 introduced; source has none |
| Package JSON matching emitted JSON bytes | Yes | Yes |
| Live Lucid import / rendered comparison | Not performed | Not performed |

For the generalization fixture, the preserved bounds are alert `(110,40,140,60)`, resolve `(110,190,140,60)`, close `(110,340,140,60)`, and note `(260,200,130,40)`. The alert changes from an SVG ellipse to a native `circle` with non-square bounds. Those equal bounds do not prove an equal rendered outline.

Both source fixtures have unstroked straight paths for their connectors. Their explicit `data-source` / `data-target` metadata provides graph direction, but their paths have no inherited or explicit stroke, and no arrow markers. SVG stroke defaults to `none`; the native output adds visible black strokes and arrowheads. Preserving these 2/2 semantic edges is therefore a visible adaptation, not evidence of identical artwork. See the [SVG painting specification](https://www.w3.org/TR/SVG2/painting.html#SpecifyingStrokePaint).

The naturalistic `out/upload.svg` is byte-for-byte equal to its source. This proves unchanged local asset content. It does not establish that Lucid's SVG insertion renders it identically or makes its internals editable.

## Compiler substitutions and unsupported detail

- Text: every node and line label uses `Liberation Sans`, centered horizontal alignment, and escaped plain text. Explicit line breaks become `<br>`. The graph has no font-family, weight, italic, tracking, baseline, text-anchor, rich spans, or glyph-outline contract. Naturalistic nodes are 16px, its edge label is 14px; all generalization labels are 14px. Neither source declares font family or size, so exact source font metrics cannot be established from this XML comparison. All eight source text baseline positions are replaced with native shape-relative or line-relative labels. SVG's initial `text-anchor` is `start`, which differs from the compiler's centered label behavior; see the [SVG text specification](https://www.w3.org/TR/SVG2/text.html#TextAnchoringProperties).
- Shapes: only rectangle, ellipse, diamond, and text are accepted. Rectangle/diamond geometry is represented by a bounding box and native primitive, not raw SVG points. Ellipse maps to `circle` and is explicitly disclosed as an approximation. Rotation, skew, corner radii, arbitrary paths, compound shapes, domain-specific diagram shapes, opacity, filters, masks, gradients, patterns, clipping, images, and embedded SVG are not represented.
- Borders: shape border color survives when supplied, but width is fixed to 1px and style to solid. Dashes, caps, joins, vector effects, and transparent/no-stroke paint are unavailable. Text nodes reject fill/border styles.
- Connectors: every edge is an attached straight line with a black 1px solid stroke, no source arrow, and one target arrow. Endpoints can be supplied explicitly. Bézier curves, elbow waypoints, custom markers, cardinalities, line colors, and double-ended arrows have no input contract. These fixtures contain only straight geometry, so they do not test preservation of curved or routed paths.
- Edge labels: literal text survives, but color/font size are fixed to black/14px and placement to midpoint/top. The naturalistic `yes` source baseline `(330,70)` is replaced by a line-relative label; no equivalent absolute baseline is emitted.
- Groups/layering/page: source groups are flattened. Shapes have zIndex 1 and lines 0, which can change crossings and overlaps. The page background is white and its size is recomputed from maximum node extents plus 32px, rather than retaining the source viewBox, page margins, or background artwork.

Relevant compiler locations: type map line 25; text formatter line 125; strict node fields line 142; fixed border line 180; strict edge fields line 186; straight/black/1px connector lines 203–207; fixed label placement line 210; generated page lines 223–226.

## Evidence and practical interpretation

The machine-readable comparison is [native-audit.json](../artifacts/data/native-audit.json). It records exact source/output paths, source hashes, compiler hash, node/color/label checks, connector coordinates and styles, group counts, page sizes, and ZIP byte checks. Original evidence is read-only under `evaluations/runs/2026-10-07-lucidchart-svg-{naturalistic,generalization}-final-luna-1/workspace/`.

Use these results to claim preservation of labels, semantic topology, supplied colors, and simple positioned boxes in the tested cases. Do not convert these counts into a percentage of visual fidelity. Reliable visual acceptance still requires importing into Lucid, rendering at comparable scale, checking font substitution and outlines, and testing native label editing and connector movement. The exact SVG asset route is the stronger candidate when artwork fidelity matters; the native route deliberately trades some presentation detail for editable objects.

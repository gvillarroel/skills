# Strict SVG metadata extraction

Use this stage when a producer or the task explicitly assigns graph meaning to SVG metadata. It does not infer nodes from artwork or connections from nearby lines. Keep the original SVG immutable and inspect/render it separately. Native mapping refusal does not establish that the SVG is ineligible for asset insertion.

```sh
uv run --script <skill-dir>/scripts/extract_native.py source.svg --coordinates user-space --output graph.json --report mapping.json
uv run --script <skill-dir>/scripts/build_native.py graph.json --output native.lucid --document-json document.json
```

Choose exact output paths outside the skill. The extractor writes a diagnostic report for accepted/rejected source analysis, then writes the graph only when all declared content resolves and the compiler accepts its graph contract. Exit `0` means a local eligible graph was written; exit `2` means blocked or a file/argument error. Unsafe path aliases and protected existing reports are refused without overwriting them. Use `--overwrite` only for intended replacements. No network or live import is performed.

Read the saved XML/resource preflight first. If it already reports blocking resources/active content, deliver that diagnostic without extracting the unchanged source; prepare a repaired derivative deliberately. If eligibility is unknown and a diagnostic extraction may refuse a feature, capture its return code, inspect the saved ledger and `graph_written`, and classify an expected refusal explicitly. Propagate file/argument errors; do not equate a diagnostic report with a completed native graph.

## Producer metadata contract

- `data-node-id`: unique nonempty node identity on one supported primitive or an owning group. Exactly one primary geometry may belong to that node. Compound icons, backgrounds, and multiple label candidates require a reviewed mapping/artwork route.
- `data-lucid-type`: optional explicit type from the bundled native catalog. It selects a semantic type; it does not prove that source artwork has that native shape's exact appearance. `data-lucid-properties` supplies a JSON object of verified type-specific properties. Unknown types/properties, duplicate JSON fields, nonfinite numbers, and invalid text are rejected.
- `data-box="x y width height"`: explicit plain-text box on a text element or a group containing one text element. It cannot override unsupported shape artwork.
- `data-label`: optional literal label; it must match selected source text when both exist. Metadata-only labels introduce native literal text, with source appearance unverified.
- `data-source` and `data-target`: both reference declared nodes on explicit line/polyline/open linear path geometry. An edge must have a unique `id` or `data-edge-id`; topology is never inferred.
- `data-edge-id`: on a separate text element identifies its edge label. One literal label per edge is supported; source label placement is disclosed as a midpoint/top adaptation.
- `data-title`: optional page title. IDs outside the native grammar receive deterministic collision-checked replacements; endpoint references use the recorded mapping.

For a visible unmarked source edge, native markers are `none`. An unstroked semantic path is blocked by default. Only add `--semantic-edges` when creating its relationship as native artwork is intended: the report records the original missing visible stroke and introduction of a black 1 px destination arrow. It does not claim the source path was visibly an arrow.

## Coordinates and geometry

`--coordinates` is required. `user-space` preserves source user-unit positions after root viewBox-origin normalization. `viewport-pixels` applies root viewport scale and `preserveAspectRatio`, including default `xMidYMid meet`, supported alignment/meet/slice combinations, and `none`. The latter requires resolved root dimensions or `--viewport WIDTH HEIGHT`. Report the selected mode; preserved user units are not a rendered pixel comparison.

Ancestor/local `translate`, positive `scale`, and axis-aligned positive `matrix(a 0 0 d e f)` compose in SVG order. For `(5,7)`, `translate(10 20) scale(2)` yields `(20,34)`; parent `scale(2)` with child `translate(10 20)` yields `(30,54)`. Root viewport 300 × 200 with viewBox `0 0 100 100` maps box `(5,10,20,30)` to `(60,20,40,60)` under default meet. Rotation, skew, reflections, singular transforms, and nested SVG viewports need another normalization route.

Recover rectangles, circles/ellipses, validated symmetric diamond polygons, and explicitly boxed text. Resolve finite positive dimensions and page containment. Non-square native circle/ellipse rendering remains a live-check item. Endpoints must independently meet the declared source contour; normalized ports are never guessed or clamped. Open linear paths support `M/L/H/V` and relative forms; multi-point routes become explicit straight-line joints. Curves, closed/filled route artwork, multiple subpaths, and mid-path markers are refused.

## Restricted presentation profile

Recover inherited presentation attributes and supported literal inline declarations; inline values override attributes. Refuse stylesheet cascade, CSS variables/escapes/comments/`!important`, unsupported presentation fields, responsive geometry, or unresolved units. SVG initial fill is black and initial stroke is none; compiler defaults are not substitutes for source defaults.

Copy supported opaque solid colors, fonts, font size, normal/bold, normal/italic, underline/strike, and start/middle alignment. Preserve XML-decoded literal characters and whitespace; native glyph spacing, baseline, padding, and label placement still need visual verification. Positioned/styled spans, text paths, outlined/stroked text, ambiguous labels, and font fallback lists need reviewed text reconstruction. Unspecified fonts/sizes use explicitly disclosed compiler defaults; declared font availability remains unverified.

Map integral border widths and solid/dashed/dotted enums. A two-value dash pattern maps to a class with an explicit exact-length loss note. Uniform circular corner radii map to native rounding diameter; elliptical radii are refused. Whole-shape opacity is supported only where fusing the object does not also alter an independent label; group compositing and per-paint alpha are refused. `stroke:none` uses width zero with a live-invisibility check. Nonuniform font/stroke scaling is blocked unless a non-scaling stroke is explicit.

Recognize only a solid right-pointing triangular polygon marker with matching edge color, tip-aligned `refX/refY`, positive marker dimensions, and automatic orientation. A source arrow additionally requires `auto-start-reverse`. Native arrow class replaces exact marker size/glyph, with an adaptation note. Other marker drawings, colors, offsets, opacity, and fixed orientations require a reviewed route.

## Ledger and fallback

The report includes `native_mapping_eligibility` (`eligible`/`blocked`), declared/resolved node and edge counts, source-to-native IDs, coordinate matrices/page, upload-preflight scope, per-source `ledger`, `graph_written`, `blocking_count`, and `live_import: "not executed"`. Ledger actions are `preserved`, `adapted`, `omitted`, `blocked`, and `unknown`. Only an eligible, compiler-valid, complete graph is written. A diagnostic can exist without a graph.

Rich features and unowned artwork receive source-referenced refusal reasons: gradients/patterns, filters, masks, clips, images, foreign content, animation, uses/instances, hidden objects, unsupported geometry/styles, metadata conflicts, and dangling references. Definitions are distinguished from painted objects; accessibility, links, group flattening, text layout, page background, and marker/dash changes are disclosed. Keep artwork or a hybrid reconstruction where that meets the task; do not silently drop a feature to obtain a complete-looking native graph. Read [fidelity.md](fidelity.md) for source-versus-native appearance checks and [native-reconstruction.md](native-reconstruction.md) for native acceptance.

Validate locally with `uv run --script <skill-dir>/scripts/test_extract.py`. Local XML, graph, and package validation do not establish successful service import, fidelity, or native editing behavior.

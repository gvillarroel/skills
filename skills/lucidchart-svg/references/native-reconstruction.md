# Reconstruct SVG as editable Lucid objects

## Recover meaning and geometry separately

Prefer supplied graph/diagram data, then explicit SVG node/edge metadata, then labels and geometry checked against a rendered source. SVG paths are drawings: crossings, proximity, colors, and shape resemblance do not establish topology, domain roles, or cardinality. Keep unresolved meaning visible. Read [shape-selection.md](shape-selection.md) before choosing formal notation.

Keep the original SVG and an element-level mapping ledger. Record source ID, native ID, literal label, type/role evidence, endpoints, geometry/style choices, adaptations, omissions, and unknown rendering properties. Node counts measure logical coverage, not visual fidelity.

For metadata-bearing SVG, use the bounded extractor in [svg-mapping.md](svg-mapping.md):

```sh
uv run --script <skill>/scripts/extract_native.py source.svg --coordinates viewport-pixels --output graph.json --report mapping.json
```

Choose `user-space` explicitly only when retaining viewBox units is intended; choose `viewport-pixels` to apply root viewport size, viewBox scale and alignment. A valid XML preflight does not establish native mapping eligibility. An incomplete extraction writes its diagnostic ledger and does not fabricate a graph. Repair/adapt a derivative deliberately or retain artwork; do not retry the same blocked extraction.

## Compile explicit fixed positions

Pass a JSON object with required `nodes`, optional `edges` and `title`. The compiler does not parse SVG or classify diagram roles. Resolve source coordinates/transforms first; do not merely subtract a viewBox origin when scaling or alignment also applies.

```json
{
  "title": "Approval flow",
  "page_width": 500, "page_height": 200, "auto_tiling": false,
  "nodes": [
    {"id": "request", "type": "process", "x": 20, "y": 40, "width": 150, "height": 60, "label": "Request", "fill": "#FFFFFF", "stroke": "#333333", "stroke_width": 2, "font_size": 16},
    {"id": "approved", "type": "decision", "x": 240, "y": 30, "width": 120, "height": 80, "label": "Approved?"}
  ],
  "edges": [
    {"id": "check", "source": "request", "target": "approved", "label": "review", "source_port": {"x": 1, "y": 0.5}, "target_port": {"x": 0, "y": 0.5}, "target_marker": "arrow"}
  ]
}
```

This example supplies action/branch roles explicitly. Use generic `rectangle`/`diamond` when only geometry is known. Query the type's compact contract and put vendor-specific camelCase fields inside `properties`:

```sh
uv run --script <skill>/scripts/native_catalog.py --type bpmnActivity
uv run --script <skill>/scripts/native_catalog.py --type table
uv run --script <skill>/scripts/build_native.py graph.json --output native.lucid --document-json native-document.json --report native-report.json
```

The catalog covers primitives, flowchart, BPMN, containers, tables and exact allowlisted cloud classes. It validates required fields, nested data and enums; unknown keys or unresolved class names fail. `ellipse` aliases native `circle` with supplied bounds and remains a rendering approximation. Image resources use the separately reviewed artwork route. Generated hierarchy/sequence layouts use [generated-layouts.md](generated-layouts.md).

## Common graph fields

IDs must be globally unique ASCII letters/digits or `-_.~`, 1–36 characters. Node fields `id,type,x,y,width,height,label` are required. Node bounds must fit within nonnegative 20,000 × 20,000 coordinates; sizes are positive finite pixels. Plain labels are HTML-escaped; no user-supplied formatted HTML is evaluated. Types forbidding text require an empty label. Text shapes reject common fill/stroke/rounding fields.

| Fields | Accepted local profile |
| --- | --- |
| `fill`, `stroke`, `text_color` | Solid `#RRGGBB` colors |
| `stroke_width`, `stroke_style` | Integer width ≥0; `solid|dashed|dotted`; exact SVG dash/gap lengths are not represented |
| `rounding`, `rotation`, `opacity`, `z_index` | Integer twice corner radius; degrees 0–360 on supported types; whole opacity 0–100; signed integer stack index |
| `font_size`, `font_family` | Positive finite pixels; safe ASCII family token/list, max128 chars; copied declarations do not establish font availability |
| `bold`, `italic`, `underline`, `strike` | Explicit booleans |
| `text_align`, `vertical_align` | `left|center`; documented vertical `center` only |
| `properties` | Exact type-specific fields from the catalog |

Use `build_native.py --help` for exact field contracts. Defaults remain white shapes, black 1px solid borders, centered black 14px Liberation Sans labels, node z1 and line z0. Named cloud symbols retain library styling and text defaults unless explicit overrides are supplied. Width0 is emitted literally; its no-stroke semantics remain a live check. Fractional widths, SVG `fill:none`, arbitrary paths/paint servers and unsupported text metrics are not silently coerced.

## Connectors and labels

Legacy string `source`/`target` IDs attach to existing nodes; normalized ports are within 0–1, default right-center to left-center. Explicit markers prevent adding unintended navigation: set `target_marker:"none"` for an undirected relationship. The builder supports all 22 documented endpoint styles, not arbitrary SVG marker geometry.

Choose `line_type:"straight|elbow|curved"`. Straight `joints` contain absolute interior `{x,y}` points; `elbow_points` contains interior turns only. The complete elbow route, including the resolved endpoints added by the validator, must have nonzero orthogonal segments and 90-degree turns. `curved` selects Lucid routing and does not reproduce exact Bézier control points. `smart:true` omits both shape ports for native attachment/routing and conflicts with explicit ports/control points. Fixed routing and smart reflow have different appearance guarantees.

Each edge accepts `stroke`, integer `stroke_width`, `stroke_style`, `source_marker`, `target_marker`, and `z_index`. The legacy `label` supports `label_position`, `label_side`, `label_color`, `label_font_size`, `label_font_family`, `label_bold|italic|underline|strike`, `label_align` and `label_vertical_align`. Position is 0–1, side `top|middle|bottom`; defaults are midpoint/top, black 14px.

For endpoint multiplicities or multiple annotations, use `labels:[{text,position,side,color,font_size,font_family,bold,italic,underline,strike,text_align,vertical_align},...]` instead of any legacy label fields. Only `text` is required; other keys are optional and retain the documented generic label defaults. Explicit text/style values follow the common text contract.

Alternatively supply vendor-shaped endpoint objects without an embedded style:

```json
{"type":"shapeEndpoint","shapeId":"node","position":{"x":1,"y":0.5}}
{"type":"positionEndpoint","position":{"x":120,"y":80}}
{"type":"lineEndpoint","lineId":"other-edge","position":0.5}
```

Object endpoints conflict with the corresponding legacy port. Omitted shape position stays omitted. Line references must exist and be acyclic under this conservative local policy. Absolute points may be negative within ±20,000; explicit elbow controls need fixed resolvable endpoints and reject rotated-shape ports, omitted ports and line attachments. No geometric inference creates line junctions.

## Page, groups and layers

Paired `page_width/page_height` set a finite custom page (1–20,000), explicitly disabling infinite canvas and defaulting tiling to false unless supplied otherwise. `page_fill`, `infinite_canvas`, and `auto_tiling` control documented page settings. Finite size/tiling settings conflict with infinite canvas in this local profile. Without explicit size, the default page encloses nodes plus32px, minimum100px, capped20000px; it does not measure text overflow, external line points or strokes. Preserve a known source page explicitly when those extents matter.

Use `groups:[{id,items:[IDs],z_index?}]` for collective editing and `layers:[{id,title,items:[IDs],layer_index?}]` for layer organization. Groups can contain shapes/lines/groups; layers contain shapes/lines/groups, never layers. The local profile checks references, cycles and one direct parent. Containers are separate visible semantic objects; groups do not create enclosure semantics.

## Acceptance

Inspect `native-report.json` for actual emitted choices and defaults before writing a narrative loss report. Compare decoded labels, source/graph/package counts, fixed boxes, endpoint roles, marker directions, multi-label positions, table merges/row order, region ownership, stack/page settings, overlaps and text readability. Read [fidelity.md](fidelity.md) for rendering limits.

The deterministic `.lucid` ZIP contains root `document.json`; generated outputs belong outside the skill bundle. Read [standard-import.md](standard-import.md) for authorized submission. A local pass proves this documented subset and package structure. After live import, select individual objects, edit a label, move a shape and confirm attached connectors follow; undo probe edits. Verify source/output at compatible crop/scale before claiming visual preservation.

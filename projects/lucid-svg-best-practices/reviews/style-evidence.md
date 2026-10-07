# Lucid Standard Import styling and geometry evidence

Reviewed 2026-10-07 against official Lucid documentation and official sample applications. This is an implementation contract proposal, not evidence of a successful live import or rendered SVG equivalence. Baseline skill publication: `a52e2b58`.

## Emitted object structure

Keep `document.json` version 1 with `documentSettings.units: "px"` and a single `pages[]` entry. A shape stores `boundingBox`, `style`, `text`, `opacity`, and `zIndex` directly. A line stores `stroke` directly, not under `style`. A group is a page-level object referring to existing items; it is not a shape. The compiler can expand its explicit graph interface without inferring arbitrary SVG semantics.

```json
{
  "id": "request",
  "type": "rectangle",
  "boundingBox": {"x": 20, "y": 50, "w": 120, "h": 60, "rotation": 15},
  "style": {
    "fill": {"type": "color", "color": "#ffeeee"},
    "stroke": {"color": "#333333", "width": 3, "style": "dashed"},
    "rounding": 24,
    "textColor": "#223344"
  },
  "text": "<p style=\"font-family:Georgia;font-size:20px;color:#223344;text-align:left\"><b>Request &amp; check</b></p>",
  "opacity": 85,
  "zIndex": 2
}
```

This example combines the documented common shape fields and style structure. Native `text` shapes reject a `style` object; their formatted text, bounding box, opacity, and stacking remain available. [Common shapes](https://lucid.readme.io/docs/shapes-si), [Standard Library](https://lucid.readme.io/docs/standard-library-si).

## Style and text limits

| Native field | Exact documented contract |
| --- | --- |
| `boundingBox.{x,y,w,h}` | Decimal coordinates and dimensions |
| `boundingBox.rotation` | Clockwise decimal degrees, 0..360; some shape families ignore or reject rotation |
| `style.fill` | `{type:"color",color:<RGB or RGBA hex>}`; image fill is another documented mode |
| `style.stroke`, line `stroke` | `{color:<RGB hex>,width:<Integer pixels>,style:"solid"\|"dashed"\|"dotted"}` |
| `style.rounding` | Integer, twice the corner radius in pixels |
| `style.textColor` | RGB or RGBA hex |

These are direct [Reference contracts](https://lucid.readme.io/docs/reference-si). They do not establish arbitrary dash lengths, `none` paint, fractional stroke widths, separate horizontal/vertical corner radii, rotation pivot, or line opacity. Preserve source `rx=12` as `rounding=24` only when the source corner geometry permits that conversion. A 2.5px stroke cannot be declared exact under the documented integer contract. Keep current six-digit colors as the conservative compiler subset initially; expansion to RGBA must distinguish fill/text support from RGB-only stroke wording.

Text uses an escaped literal label inside generated HTML. The allowed style names are `color`, `font-family`, `font-size`, `font-style`, `font-weight`, `text-align`, `text-decoration`, and `vertical-align`; other properties are ignored. Documented defaults are black, Liberation Sans, 10pt, normal, normal, center, none, and center respectively. The prose also mentions automatic sizing when font size is omitted, so emit an explicit size. Values are not exhaustively enumerated. `left` appears in the official example and `center` is the documented default; do not infer that every CSS alignment value is vendor-tested. The official examples also demonstrate bold and italic CSS. [Reference Markdown, text sections](https://lucid.readme.io/docs/reference-si.md), [official formatted demo](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/demo-files/demo/unzipped-contents/document.json).

Supported markup includes breaks, bold, italic, underline, strike, links, and ordered/unordered lists. For a safe flat graph contract, use boolean `bold`, `italic`, `underline`, and `strike` flags and emit `b`, `i`, `u`, and `s` wrappers. Do not accept raw user HTML or CSS. Font-family preservation means preserving the declaration; availability, substitution, baseline, wrapping, padding, and exact layout need a live rendered comparison. Official demo snapshots show `font-size` in points and `font-weight:bold`/`font-style:italic`; the existing compiler's pixel declaration is a current local behavior, not a newly verified pixel-perfect promise.

Shape `opacity` is a whole number 0..100, default 100. `zIndex` is an integer, default 0. Within a group, child stacking is relative to that group. Equal stacking puts groups above lines above shapes, with later objects of the same type on top. [Common shapes](https://lucid.readme.io/docs/shapes-si).

## Lines, ports, routes, and labels

Native nesting is:

```json
{
  "id": "submit", "lineType": "elbow", "zIndex": 1,
  "endpoint1": {"type": "shapeEndpoint", "style": "none", "shapeId": "request", "position": {"x": 1, "y": 0.5}},
  "endpoint2": {"type": "shapeEndpoint", "style": "openArrow", "shapeId": "store", "position": {"x": 0, "y": 0.5}},
  "stroke": {"color": "#aa1133", "width": 2, "style": "dashed"},
  "elbowControlPoints": [{"x": 180, "y": 80}, {"x": 180, "y": 120}],
  "text": [{"text": "Submit", "position": 0.4, "side": "bottom"}]
}
```

`lineType` permits `straight`, `elbow`, `curved`. `joints` are absolute `{x,y}` points for straight lines; `elbowControlPoints` are absolute points forming right angles for elbow lines. There is no documented control-point field for exact cubic/quadratic curves. Shape ports use normalized 0..1 `{x,y}`. Omitting position on **both** shape endpoints creates a smart line. `lineEndpoint` uses `lineId` plus scalar 0..1 position; `positionEndpoint` uses an absolute point. Absolute positions may be negative, as an official endpoint example demonstrates. [Lines](https://lucid.readme.io/docs/lines-si).

The exact endpoint style enum is `none`, `aggregation`, `arrow`, `hollowArrow`, `openArrow`, `async1`, `async2`, `closedSquare`, `openSquare`, `bpmnConditional`, `bpmnDefault`, `closedCircle`, `openCircle`, `composition`, `exactlyOne`, `generalization`, `many`, `nesting`, `one`, `oneOrMore`, `zeroOrMore`, `zeroOrOne`. Set each endpoint independently. No documented arbitrary marker size, color, or geometry field exists. Line labels form an array of `{text,position,side}`; position is 0..1 and side is `top`, `middle`, or `bottom`. Text can contain the same formatted HTML; absolute SVG label coordinates do not have an equivalent line-label field. [Lines, endpoint and text sections](https://lucid.readme.io/docs/lines-si.md).

The official [BPMN converter line helper](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/bpmn-converter/converter/utils/line_utils.py) demonstrates elbow lines and attached endpoints, but does not distinguish message-flow marker semantics or preserve arbitrary source route geometry. It should not justify a guessed message-flow arrow conversion.

## Groups, layers, containers, and pages

Emit groups at `pages[0].groups` as `{id,items:[IDs],zIndex}`. Items may be shapes, lines, or groups, never layers. Groups have no documented transform or bounding-box field: resolve SVG transforms before absolute shape/line geometry. The Groups property table accidentally repeats `linkedData` for the stacking row; its description and JSON example establish `zIndex`. Acyclic groups and unique membership are reasonable conservative compiler policies, not explicit upstream limits. [Groups](https://lucid.readme.io/docs/groups-si).

Layers use `pages[0].layers:[{id,title,items,layerIndex}]`. Layer indices dominate child zIndex; equal layer indices put later layers on top. Layers cannot contain layers. Layer support can be deferred while ordinary group membership is implemented. [Layers](https://lucid.readme.io/docs/layers-si).

The container types are `braceContainer`, `bracketContainer`, `circleContainer`, `diamondContainer`, `pillContainer`, `rectangleContainer`, `roundedRectangleContainer`, and `swimLanes`. All eight explicitly reject bounding-box rotation. `magnetize` defaults true and controls movement of contained shapes. This is geometry-based container behavior, not an explicit group `items` relationship. Circle, pill, rectangle, and rounded rectangle containers support `containerTitle:{text}` and `assistedLayout`; diamond supports assisted layout without a documented title. Assisted layout rearranges contained items when first opened; emit false when preserving source geometry. Swimlanes require `vertical`, `titleBar:{height,verticalText}`, and lanes `{title,width,headerFill,laneFill}`. The lane widths must sum along the applicable container axis; exact orientation behavior deserves a live fixture before accepting automatically derived dimensions. [Container Library](https://lucid.readme.io/docs/container-library-si).

Page settings are nested under `pages[0].settings`: `fillColor`, `infiniteCanvas`, `autoTiling`, and `size:{type:"custom",w,h}`. Custom dimensions are numeric pixels in 1..20000. For an explicit finite SVG page, use `infiniteCanvas:false`, `autoTiling:false`, and source viewport dimensions after the chosen coordinate normalization. Size is ignored on an infinite canvas. Standard size types are letter, legal, executive, a3, a4, a5, tabloid, folio, statement; format is portrait or landscape. [Pages](https://lucid.readme.io/docs/pages-si).

## Implemented backward-compatible flat graph additions

Retain current required node/edge keys, positional CLI, strict unknown-key rejection, defaults, deterministic packaging, and explicit semantic graph boundary. All additions are optional.

| Graph scope | Proposed additions | Native mapping |
| --- | --- | --- |
| Node | `stroke_width`, `stroke_style`, `rounding`, `rotation`, `opacity`, `z_index` | `style.stroke.{width,style}`, `style.rounding`, `boundingBox.rotation`, `opacity`, `zIndex` |
| Node text | `font_family`, `bold`, `italic`, `underline`, `strike`, `text_align` | Generated safe HTML; initially allow only left/center alignment |
| Edge | `line_type`, `stroke`, `stroke_width`, `stroke_style`, `source_marker`, `target_marker`, `z_index` | `lineType`, `stroke`, endpoint styles, `zIndex` |
| Edge geometry | `joints`, `elbow_points`, `smart` | `joints`, `elbowControlPoints`, omission of both endpoint positions |
| Edge label | `label_position`, `label_side`, `label_color`, `label_font_size`, `label_font_family`, `label_bold`, `label_italic`, `label_underline`, `label_strike`, `label_align` | One existing label entry plus formatted text |
| Edge labels | `labels:[{text,position?,side?,color?,font_size?,font_family?,bold?,italic?,underline?,strike?,text_align?,vertical_align?}]` | Multiple line labels; exclusive with legacy label/label_* fields |
| Edge endpoint | String node ID or explicit `{type:"shapeEndpoint",shapeId,position?}`, `{type:"lineEndpoint",lineId,position}`, `{type:"positionEndpoint",position}` | Attached shape, attached line, or absolute endpoint; endpoint markers remain flat edge keys |
| Graph | `page_width`, `page_height`, `page_fill`, `infinite_canvas`, `auto_tiling`, `groups:[{id,items,z_index}]` | Page settings and page groups |
| Graph layers | `layers:[{id,title,items,layer_index?}]` | Page layers with deterministic ordering |

Policy: integer nonnegative stroke widths; width0 is emitted with an explicit live-check notice because invisible-stroke semantics are undocumented. Use nonnegative integer rounding, whole opacity, signed integer stacking, finite rotation 0..360, and no silent width rounding. Require page dimensions together. Reject explicit size/tiling with infinite canvas, explicit ports or route points with smart routing, incompatible route fields, and orphan label style keys. Text nodes reject fill/border/rounding properties. Validate orthogonal consecutive elbow segments including resolved fixed endpoints. Explicit elbow controls with rotated shape ports, omitted ports, or line endpoints are rejected because the source geometry cannot be resolved from the documented contract. Curved routing produces an approximation notice. Absolute line/control positions are bounded locally to +/-20000px. Group/layer membership and line attachments are acyclic; objects have one direct group/layer parent. These are conservative compiler policies.

Provider `namedShape` and `namedContainer` objects retain native style and text defaults when no explicit style/formatting is supplied. Partial source styling emits only those requested keys. This avoids replacing the native symbols with a generic white fill. GCP 2021 documents a default blue fill; other provider-specific appearances remain a live check. [GCP 2021 Library](https://developer.lucid.co/docs/gcp-2021-library). The compatibility report qualifies default style/text scope and flags native library appearance for rendered verification.

Root SVG `viewBox`, viewport scale, and `preserveAspectRatio` must be resolved by the mapping stage. Merely subtracting a negative origin is insufficient. Native `rotation` is not proof that arbitrary SVG `rotate(angle,cx,cy)`, skew, or nonuniform transforms were preserved. Keep a fidelity ledger for source details outside this explicit contract.

## Validation and evidence boundary

`uv run --script skills/lucidchart-svg/scripts/test_native.py` passed 26 test methods on 2026-10-07, including existing fixtures, exact style nesting, all 22 markers, fixed/smart/absolute/line endpoints, multiple labels, route validation, groups/layers, provider defaults, escaping, output path and hard-link alias protection, huge JSON integers, and a copied-resource mutation check. Numerous invalid cases are exercised as subtests. Existing fixture document SHA-256 `5dc61f8e9e8ec035bd416502c0d5ba354d252e8e7fecd2daff8714ae8cc12ce5` and package SHA-256 `e18ba4157b2f469f634aa2d737c8b071631d193cc5dd9f936b5031a0870a405f` remain identical.

The CLI adds `--report exact.json`: emitted objects, explicit fields, defaults and their scope, supported graph keys/enums, page settings, group/layer structure, official schema/catalog sources, approximation notices, and required live checks. Report and document output paths must differ from the input and each other. Future isolated runtime validation should include a styled finite diagram and a fractional-width curved source whose adaptation is accurately disclosed; the parent task owns that release gate.

Only authorized live import plus a rendered comparison can establish font availability, rotation behavior, marker appearance, dash geometry, grouping interaction, and curve layout. An exact generated XML/JSON comparison establishes emitted data preservation, not image fidelity.

Read-only source snapshots and official sample files are retained under [artifact data](../artifacts/data/); [source manifest](../artifacts/data/source-manifest.json) records their URLs and hashes. Research was completed before implementing the expanded compiler and its regression tests. The canonical skill prose and backlog are owned by the parent task.

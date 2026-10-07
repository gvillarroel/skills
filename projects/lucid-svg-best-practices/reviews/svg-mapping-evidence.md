# SVG-to-Lucid mapping evidence and implementation boundaries

Checked: 2026-10-07. This report audits the existing local inspector, native compiler, tests, and two acceptance prompts. It proposes deterministic improvements; it does not change the skill, upload a file, access an account, or establish live Lucid compatibility. Source features outside the local compiler are not necessarily unsupported by Lucid itself.

The best next step is a metadata-driven extraction stage with an explicit compatibility ledger, followed by the existing graph compiler. Keep byte-preserving SVG asset preparation separate. Do not use an XML/resource preflight result as a claim that drawing features or native editability survived.

## Audited implementation and measured coverage

- [Inspector](../../../skills/lucidchart-svg/scripts/inspect_svg.py): SHA-256 `ce50e31d9fa0efa45fb4e7927eee90fb88fdb2074d321b1926d0fef33802248f`.
- [Compiler](../../../skills/lucidchart-svg/scripts/build_native.py): SHA-256 `370b2145b23faa92885f055b9e153a4f9fad7bedbf6060ff06c3bbe49746d04b`.
- [Naturalistic prompt](../../../evaluations/pi-prompts/lucidchart-svg-naturalistic.md): SHA-256 `a91d32c1b1e67f4146915a160b2536e4d101cf207e8308023ea16b259933379d`.
- [Generalization prompt](../../../evaluations/pi-prompts/lucidchart-svg-generalization.md): SHA-256 `427d51021c656343da1760372736b5272fa7756eead88a69f88240a27f223645`.
- Existing tests passed: 16 inspector tests and 9 compiler tests. These exercise resource rejection, byte-preserving copies, Unicode, graph validation, deterministic packaging, labels, bounds, supported types, and attachments. They do not test an SVG-to-graph extractor because none exists.

The inspector validates XML, root namespace, usable root dimensions, references, and selected active/external content. It inventories element names, IDs, and concatenated text. It does not extract `data-node-id`, `data-source`, `data-target`, `data-edge-id`, or `data-box`, compute styles, resolve geometry, or establish a visible rendering tree. The compiler accepts an explicit graph, not SVG, and correctly rejects extra input fields rather than silently ignoring them.

| Existing SVG fixture | Explicit logical objects | Explicit relationships | Literal node/edge labels | Geometric evidence | Necessary adaptations in current compiler |
| --- | ---: | ---: | ---: | --- | --- |
| Approval/naturalistic | 3 nodes | 2 edges | 3 node labels + 1 edge label | Two rectangles and a symmetric diamond polygon; horizontal edge endpoints | Source paths have no visible stroke; compiler adds black arrows. Labels are recentered with a substituted font. Page becomes 512 × 152 instead of source 500 × 180. |
| Incident/generalization | 4 objects | 2 edges | 4 object labels | Ellipse, two rectangles, explicit text `data-box`; ancestor translation `(10,20)`; vertical endpoints | Ellipse uses native `circle` with rectangular bounds and needs live inspection. Source paths have no visible stroke; compiler adds arrows. Page becomes 422 × 432 instead of the source 400 × 500 viewBox. |

Each fixture has an inspector `vector_element_count` of 9. That is an XML element inventory, not a count of native nodes or visible shapes. The fixtures provide seven logical objects and four relationships in total, but they do not exercise stylesheet cascade, rotation, nested viewports, arbitrary curves, groups, transparency, or native domain semantics.

## Reproduced inspector limits

The project-only [probe script](../scripts/probe-current-svg-mapping.py) writes retained SVGs, reports, and [summary.json](../artifacts/data/current-inspector-probes/summary.json). It does not alter source bundles. Run:

```powershell
uv run --script projects/lucid-svg-best-practices/scripts/probe-current-svg-mapping.py --repository C:\Users\villa\dev\skills --output projects/lucid-svg-best-practices/artifacts/data/current-inspector-probes
uv run --script skills/lucidchart-svg/scripts/test_svg.py
uv run --script skills/lucidchart-svg/scripts/test_native.py
```

All 24 narrow probes returned `ready_for_upload: true`. This accurately describes the current selected preflight checks; it is not evidence of graphic validity or successful Lucid import. In particular:

| Probe family | Current observation | Consequence for a native extraction stage |
| --- | --- | --- |
| Inherited fill/stroke/font size, CSS paint and geometry overrides | No recovered styles or geometry; no portability warning | Reading attributes alone can produce the wrong color and bounds. |
| Hidden content and definitions | Reports `Template`, `Ghost`, and `Visible` as labels | Retain raw textual inventory, but do not call it visible-label recovery. |
| Internal `use`, cyclic `use` | Definitions and uses both contribute to inventory; cycles unreported | Instances require separate expansion rules; definitions are not extra logical nodes. |
| Multiple primitives inside one node group | Three vector elements for one explicit node | Require a primary-shape selection contract; avoid one-node-per-primitive inference. |
| Unstroked semantic edge, `fill:none`, opacity, dash, marker, gradient | No mapping-loss warning | Introduced borders/arrows and paint substitutions must be explicit. |
| Outlined label | No text label, despite application metadata | Absence of `<text>` does not establish absent visible lettering. Metadata needs a named contract. |
| Positioned spans with preserved whitespace | Returns `FirstSecond` after `.strip()` | String inventory loses layout and preserved spaces; it is not a lossless text reconstruction. |
| CSS keyframe animation | No animation warning | A feature inventory should include CSS animation as well as SMIL elements. |
| Malformed path data or negative rectangle width | Well-formed XML accepted | `valid_svg` currently means syntactically accepted input, not valid geometry. |
| Unresolved fragment | Warning, but upload preflight remains ready | Native extraction must refuse unresolved geometry; asset preparation may keep it with a diagnostic. |
| Foreign-namespace `rect` | Counted as a vector element by local name | Geometry extraction must require the SVG namespace, not only a tag suffix. |
| Root scaling/alignment and nested SVG viewport | Root dimensions inventoried, transformations unreported | Coordinate policy and viewport transforms must be resolved or refused. |

These are compatibility/reporting limits, not a demonstrated active-content bypass. The existing resource tests still pass. Extending a mapping ledger is preferable to blocking every valid vector asset that contains a gradient or mask.

## Primary SVG rules that constrain a converter

Application-specific `data-*` attributes can carry a model, but SVG does not define graph meanings for names such as `data-source`. Adopt a documented producer contract and check references against it. Treat a `use` instance and its definition separately; broad XML traversal is not instance expansion. [W3C SVG 2 document structure](https://www.w3.org/TR/SVG2/struct.html#DataAttributes)

Presentation attributes participate in the CSS cascade with specificity zero. Stylesheets and inline declarations can override them, and SVG geometry can also be styled. An extractor that only reads `fill`, `x`, and `width` attributes needs a restricted-input rule or a computed-style stage. [W3C SVG 2 styling](https://www.w3.org/TR/SVG2/styling.html#PresentationAttributes)

SVG's initial fill is black and initial stroke is none; both are inherited. A missing source stroke must not become a supposedly preserved black border. An unstroked path may still paint a filled area; inspect fill, stroke, markers, and visibility separately. Native defaults are implementation choices, not SVG defaults. [W3C SVG 2 painting](https://www.w3.org/TR/SVG2/painting.html#FillProperty)

`display:none` excludes an element and descendants from the rendering tree. `visibility:hidden` has different layout and inheritance effects. Definitions and unpainted elements remain in the document model. A content inventory and a visible-artwork inventory therefore need separate fields. [W3C SVG 2 rendering model](https://www.w3.org/TR/SVG2/render.html#VisibilityControl)

The root viewport maps `viewBox` coordinates using scale and alignment, with default `xMidYMid meet`. Nested SVGs introduce further viewport mappings. With width 300, height 200, and viewBox `0 0 100 100`, a source rectangle `(5,10,20,30)` renders as `(60,20,40,60)` in viewport pixels; subtracting the origin alone yields different coordinates. [W3C SVG 2 coordinate systems](https://www.w3.org/TR/SVG2/coords.html#ComputingAViewportsTransform)

Compose ancestor and local affine matrices in document order. Using column vectors, `translate(10 20) scale(2)` maps `(5,7)` to `(20,34)`; a parent `scale(2)` and child `translate(10 20)` maps it to `(30,54)`. Adding translations before resolving scaling is incorrect. [W3C CSS transforms](https://www.w3.org/TR/css-transforms-1/#transform-rendering)

Basic rectangles, circles, ellipses, lines, polylines, and polygons have explicit geometric contracts. Rounded rectangles and arbitrary polygons retain details a plain bounding box cannot represent. A symmetric diamond is a restricted polygon case; an arbitrary four-point polygon is not evidence of a decision node. [W3C SVG 2 basic shapes](https://www.w3.org/TR/SVG2/shapes.html)

Text positioning, spans, whitespace, direction, and font properties affect rendering independently of the literal characters. Raw concatenation does not recover line breaks or alignment. Outlined glyphs require a separate label source; OCR would be interpretation. [W3C SVG 2 text](https://www.w3.org/TR/SVG2/text.html#WhiteSpace)

## Proposed deterministic extraction contract

Use two explicit coordinate modes. `user-space` preserves author coordinates after the declared origin normalization; `viewport-pixels` applies the full viewport transform. Record the chosen mode, matrices, original viewport, and any output translation. Do not describe user-unit preservation as rendered pixel fidelity. For responsive/percentage dimensions without a resolved viewport, request or require a viewport size instead of guessing.

Use explicit semantic identity as a gate:

1. Accept a producer contract naming node IDs, edge IDs, endpoints, labels, primary shape, and any text box. Support the existing fixture names only when the task or contract assigns their meaning. Inspect all duplicates, empty IDs, dangling endpoints, and conflicting ownership.
2. Require exactly one selected primary geometry per node. A group with a box, icon, and label is one object only when the producer says so. A later `data-shape-ref` or explicit mapping file can select geometry without guessing. Keep decorative children in the ledger.
3. Obtain literal labels from one explicitly selected text element or label metadata. Reject competing text candidates, positioned spans, and outline-only labels unless the producer supplies the intended string and line breaks. Keep raw and normalized strings separately.
4. Map source IDs to valid compiler IDs deterministically. Preserve valid IDs; otherwise use a stable recorded replacement and collision check. Rewrite endpoint references through that mapping, rather than truncating IDs or removing punctuation independently.
5. Resolve endpoint geometry independently of semantic references. Compute normalized ports from the mapped object bounds and confirm the source points match. Do not clamp inconsistent endpoints into `[0,1]`; report a conflict. A bounding-box corner is not automatically a contour point on a diamond or ellipse.
6. Require a declared edge policy: preserve the visible line/markers, or create a semantic arrow as an adaptation. In the existing fixtures, the latter policy is necessary because the open two-point paths have neither explicit nor inherited visible strokes.

The first implementation can safely cover plain SVG-namespace rectangles, circles/ellipses, validated symmetric diamonds, metadata-sized plain text, and explicit one-segment lines with finite numeric geometry under translation/positive axis scaling. Geometry calculation can be exact within this subset. Native appearance remains conditional on the output schema and live rendering. Reject zero/negative sizes, singular transforms, rotation/skew, unsupported units, and multi-geometry ambiguity in this initial route. Arbitrary curve endpoints alone do not preserve the curve.

Suggested standalone command contract: `extract_svg_graph.py input.svg --graph graph.json --report mapping.json --coordinate-mode user-space|viewport-pixels`. Require the coordinate mode rather than choosing it from an incidental filename. Emit the compiler-compatible graph only if every declared node and edge is resolved; always emit the diagnostic report when parsing succeeds. Keep generated graph/report outside the bundle. The extractor must make no network calls, alter no original bytes, and accept no arbitrary executable metadata. A plain mapping file can provide source-to-node ownership and missing labels without pretending that it was recovered automatically.

For style recovery, choose one supported profile rather than a partial silent CSS implementation. A small offline profile can resolve inheritance, supported presentation attributes, and literal inline declarations while refusing stylesheets, variables, `currentColor`, `!important`, and unsupported tokens. A browser-computed profile could instead recover computed paint and geometry from a safely inspected source with fixed viewport, fonts, and time. That profile needs its own dependency and renderer contract; it must not execute unreviewed active content. Record computed values and source declarations for reproducibility.

Converting CSS colors to `#RRGGBB` is only lossless for opaque supported colors. `none`, alpha colors, fill/stroke opacity, gradients, patterns, and effects must not be silently replaced. Positive scaling preserves primitive geometry, but text metrics and stroke scaling still need separate checks; nonuniform scaling cannot generally be represented by changing one font size or one border width.

## Compatibility decisions worth encoding

The following is a proposed implementation ledger, not a service compatibility table. Every extraction result should include counts and individual entries with source reference, destination ID, recovered evidence, action, and reason. Suggested actions are `preserved`, `adapted`, `omitted`, `blocked`, and `unknown`. A blocked node/edge should prevent compilation of an apparently complete graph; write the audit report first.

| Feature family | Deterministic extraction available | Current compiler output | Recommended decision |
| --- | --- | --- | --- |
| Semantic IDs, edge references, literal labels | Yes, under explicit metadata contract | Supports graph IDs and literal labels | Preserve with reference validation and recorded ID mapping. |
| Primitive box bounds and translations | Yes | Explicit axis-aligned boxes | Preserve; independent endpoint/bounds checks. |
| Root/nested viewport and aspect-ratio mapping | Yes, with resolved dimensions | No SVG transform processing | Add a declared coordinate mode; refuse unresolved inputs. |
| Rectangle without rounding | Yes | `rectangle` | Preserve geometry; check paint and label substitutions separately. |
| Circle/ellipse | Yes | `ellipse` input becomes native `circle` | Preserve measured bounds; keep non-square rendering as an explicit live-check item. |
| Symmetric diamond | Yes, with validated geometry or declared semantic type | `diamond` | Preserve restricted geometry; other polygons require another route. |
| Plain text with explicit box | Literal string/box yes; exact glyph metrics conditional | Centered Liberation Sans, supported color/size | Preserve content; disclose alignment/font changes. |
| Opaque solid fill/stroke/text color | Yes, after style recovery | Six-digit hex; fixed border width/style | Preserve color; require an adaptation when widths/styles differ. |
| Edge direction, attached endpoints and ports | Yes, when metadata and geometry agree | Straight black 1 px destination arrows | Preserve topology/ports; disclose source artwork changes. |
| Page dimensions, margins, background | Root dimensions/paint can be recovered | Inferred bounds +32 px; min100/max20000; white page | Add explicit page options after schema confirmation; never claim original page preservation today. |
| Marker shape, curved/orthogonal routes, line style | Geometric data can be recorded | Fixed straight route, arrow, stroke | Preserve in ledger; broaden graph schema only for documented fields with tests. |
| Rounded corners, opacity, group transforms/order | Parameters can be recorded | No corresponding input fields | Adapt explicitly or retain as SVG asset. Do not flatten groups into exact-editability claims. |
| Gradients, patterns, filters, masks, clips, images | Feature/resource inventory yes; reconstruction complex | Unsupported by local graph contract | Asset route or dedicated reconstruction; feature-level live evidence required. |
| Outlined text, arbitrary paths, domain ports/cardinalities | Source model/metadata may provide meaning | Primitive native types only | Require semantic input or interpret with a ledger; no automatic domain-shape claim. |
| Animation, accessibility, interaction, custom metadata | Inventory and source preservation yes | Not represented in graph output | Retain source/manifest; explicit omission from static native output. |

For actual Lucid route constraints, use the separately maintained [vendor fidelity audit](../../lucid-svg-fidelity/reviews/vendor-fidelity-audit.md). Standard Import SVG image embedding is documented as PNG conversion, whereas formal custom-shape import may retain vector properties but needs actual rendering inspection. These observations do not justify a blanket claim that Lucid rejects particular filters or path types.

## Inspector reporting improvements

Preserve the existing `ready_for_upload` gate as a local preflight compatibility field, and make its scope explicit: selected XML/resource checks passed; no service upload has been tried. Introduce a clearly named `valid_svg_xml` field if the report schema is revised. Neither field should imply valid path data, source artwork visibility, or service acceptance.

Add a feature inventory with source references for stylesheets/inline styles, transforms/viewports, gradient/pattern paint, `none` paint, opacity, stroke width/dash, marker references, rounded corners, text spans/text paths/outlines, `use`/definitions, hidden content, effects, images, and SMIL/CSS animation. Count SVG-namespace graphics separately from foreign metadata. Preserve raw text inventory and report that it may contain hidden/definition text; do not rename it to visible labels without a rendering-stage check.

Expose native mapping as a separate profile outcome, for example `not_assessed`, `eligible`, or `blocked`, with a profile ID and per-feature reasons. The extractor should own eligibility so the inspector does not grow a conflicting second implementation. Unsupported local-native features can remain eligible for byte-preserving asset preparation. Unresolved references, malformed geometry, and metadata conflicts belong in extraction diagnostics even when a resource-only preflight succeeds.

Keep security/resource flags and visual substitutions separate. Blocking a remote stylesheet or active script protects the selected workflow; noting a gradient or mask explains a mapping limit. Feature warnings must not be presented as evidence that Lucid always rejects that feature. CSS escapes or comments already trigger review; the native profile should also refuse unsupported cascade constructs rather than accidentally accepting an unresolved computed value.

## Presentation checks and acceptance additions

Package structure alone cannot verify readable or faithful presentation. Retain the original SVG and its hash, extraction graph, package/document byte identity, mapping ledger, fixed-viewport source render, and actual imported result. Keep local and live acceptance statuses separate.

Deterministic pre-import checks should cover finite bounds, page containment, object/edge identity, literal labels, source endpoint-to-port agreement, and explicit mapping coverage. Add diagnostics for object overlap, connector crossing through unrelated nodes, long/unresolved text, and page-edge clipping; these can be intentional, so they should not become unqualified failures. Outline-only text should produce an unknown label-recovery status, never a blank-diagram claim.

For visual checks, align the same page or content crop and compare at the intended scale and high zoom. Inspect source paints, visible edge count, curve/marker shapes, label anchors, transparency, clipping, and layer overlap. A locally simulated native render only checks the simulation. After authorized service import, select objects separately, edit a literal label, move a shape while watching its connectors, and undo probes. Exported labels may become paths; compare visual label presence independently from extractability.

Add independent fixtures for metadata conflicts, multi-primitive node selection, invalid IDs, inherited versus overridden paint, `none` paints, alpha, stroke width/dash, marker mismatch, root meet/slice/none viewport transforms, nested scale/translation order, rotation refusal, text spans/whitespace, outline-only labels, definitions/uses, hidden objects, and negative geometry. Define expected values from SVG rules or measured renders rather than copying the extractor. Repeat isolated skill runs on both supported and refused inputs after the root chooses the contract.

No skill sources were changed for this audit. The project probe and report are separate evidence that can support a subsequent scoped implementation.

# Saved Lucid editor fidelity evidence

Reviewed on 2026-10-07. This is an independent read-only review of saved source material and actual editor screenshots. No browser session, account action, upload, export, or skill modification was performed for this review.

The D3 flowchart evidence supports complete preservation of this small fixture's logical graph and readable labels, with individually editable native objects. It does **not** support preservation of the original SVG's detailed appearance or coordinates. The tested route was semantic source data to Mermaid markup to Lucid native shapes. Direct SVG asset import and the prepared Standard Import package remained untested in the saved account record.

## Reviewed source and captures

- Canonical [D3 flowchart source recipe](../../../skills/d3/references/patterns/flowchart-dag.md): seven explicitly positioned nodes, seven directed links, three branch labels, SVG geometry, text styling, and reveal animation.
- Saved [Colorset1 source gallery image](../../colorset-priority/artifacts/d3-gallery-final-public/desktop/flowchart-dag-cs1.png), visually inspected at original resolution. This is a separate saved gallery capture that illustrates source layout and styling; it is not the SVG uploaded to Lucid, and its capture-time source bytes were not independently bound to the current recipe in this review.
- Prepared [static SVG derivative](../../lucid-native-compatibility/artifacts/data/d3-flowchart-dag-static.svg), read as XML/source. It already adapts colors, scales source coordinates by two, and replaces source curves with orthogonal polylines. It is not an unchanged original SVG and was not uploaded in the saved live tests.
- The [Mermaid derivative](../../lucid-native-compatibility/artifacts/data/d3-flowchart-dag.mmd) and [mapping manifest](../../lucid-native-compatibility/artifacts/data/d3-flowchart-dag.mapping.json), read directly.
- Actual Lucid [code-rendered diagram](../../lucid-native-compatibility/artifacts/screenshots/d3-mermaid-code.jpg), [final native diagram](../../lucid-native-compatibility/artifacts/screenshots/d3-native-final.jpg), [selected and moved decision](../../lucid-native-compatibility/artifacts/screenshots/d3-native-moved.jpg), and [edited start label](../../lucid-native-compatibility/artifacts/screenshots/d3-native-label-edit.jpg), each visually inspected at original resolution.
- The [live acceptance ledger](../../lucid-native-compatibility/reviews/acceptance.md) and [later account results](../../lucid-native-compatibility/reviews/free-expanded-results.md), used to distinguish executed operations from prepared candidates.

## Defensible fidelity result

| Detail | Source contract | Actual saved Lucid result |
| --- | --- | --- |
| Logical nodes | 7: start, collect, validate, persist, repair, notify, done | All 7 recognizable nodes are visible in both code and native-final captures. This is a logical-node count, not a verified serialized Lucid object count. |
| Directed links | 7: start→collect; collect→validate; validate→persist; validate→repair; repair→collect; persist→notify; notify→done | All 7 directed relationships and their arrowheads are visibly traceable in the final capture. The retry loop returns to Collect request. |
| Object labels | Start; Collect request; Valid payload?; Store event; Repair input; Notify subscriber; Done | All 7 are readable with the same words and ordering. Multi-line object labels remain recognizable. The label-edit capture temporarily shows Begin; the final capture restores Start. |
| Edge labels | yes, no, retry | All 3 are present and readable on the corresponding branch/loop. Thus 10 logical text labels survive: 7 object labels and 3 edge labels. |
| Broad shape semantics | Start circle; input parallelogram; decision diamond; 3 rounded process boxes; double-circle end | These broad forms remain recognizable. The native end has a clearly visible white inner ring. The source recipe encodes a second circle, but that ring is not visually distinguishable in the saved gallery image; exact ring styling is not a fidelity pass. |
| Independent editing | Desired native object behavior | The moved-decision capture shows only the diamond selected, and its three incident connections change route relative to the native-final capture. The edited-label capture shows the independently selected circle labeled Begin. The ledger records Undo restoring these probes. |
| Static legibility | Complete selected graph | All 7 objects and 10 logical labels are readable in the native-final capture without visible clipping. This does not establish print-scale readability or all other diagram families. |

The test preserves 7/7 logical nodes, 7/7 directed relationships, and 10/10 logical labels. These bounded counts are meaningful; a single numerical percentage for overall SVG fidelity would conceal the substantial visual changes below.

## Visible changes and explicit losses

1. **Positions and layout change.** The source recipe places Done at center `(522,250)`, below Notify at `(486,140)`. The source gallery capture shows that downward success edge. In the Lucid native-final capture, Store event, Notify subscriber, and Done share the upper success row. Lucid also spreads the graph horizontally and changes its vertical spacing. The Mermaid derivative has no source coordinates, so this is expected automatic layout, not coordinate-preserving SVG conversion.
2. **Dimensions and shape proportions change.** Source centers, widths/heights, corner radii, input slant, and diamond proportions do not survive as exact SVG geometry. The broad shape categories remain, but the native process boxes have visibly different proportions and corner treatment.
3. **Paths, ports, and label positions change.** The original recipe computes cubic Bézier curves and a fixed retry path; the static derivative separately uses orthogonal polylines. The live Mermaid/native route uses Lucid/Mermaid routes, then reroutes attached connectors after native conversion or movement. It preserves the endpoint graph, not the original `d` strings, control points, attachment positions, or text-anchor coordinates. Code-rendered and native-final captures already differ in connector curvature while retaining the same graph.
4. **Colors are adapted.** The submitted Mermaid explicitly uses a crimson/grayscale Colorset1 adaptation. In the saved source gallery capture Collect request and Repair input are crimson; the native capture makes them black and light gray, respectively. Store event and the decision also use different grays. Start and Done remain approximately crimson. Screenshot pixel values cannot prove exact color equality because the Lucid captures are JPEG; the submitted style declarations are the reliable intended-color contract.
5. **Typography changes.** Source text is compact and bold; the native result uses larger, lighter text and different spacing. Literal words survive, but font family, weight, exact metrics, baselines, and native label positioning are not a match. Source screenshot scale and native editor zoom differ, so no pixel-to-pixel typography score is justified.
6. **Behavior and SVG metadata do not transfer.** The source recipe's path-drawing/node-fade animation and D3 data-join/runtime behavior are not retained. Preservation of source SVG groups, classes, element IDs, accessibility title/description, and arbitrary attributes was not verified. A still editor screenshot cannot establish any such behavior or metadata transfer.

The mapping manifest's statements about source geometry at scale two and eight primitive shapes belong to the **locally prepared Standard Import/static-derivative route**. They must not be applied to the live Mermaid conversion, which uses automatic layout and has no accepted Standard Import serialization in this evidence.

## SVG import/export boundary

The later account report explicitly leaves `d3-flowchart-dag-static.svg` image insertion pending and says no file upload occurred. It records ordinary and transparent SVG export attempts that each timed out without a verified SVG file. A saved export-options screenshot shows SVG choices, but it is not a delivered SVG. Verified PNG/JPEG/transparent-PNG/PDF exports of a different native ER fixture do not establish this D3 flowchart's SVG export or vector fidelity.

The separately inspected [Mermaid native-editable screenshot](../../lucid-native-compatibility/artifacts/screenshots/mermaid-native-editable.jpg) confirms independent selection and explicit styling for Flow role 01. Its rightmost graph portion is outside the visible viewport; this review does not independently recount all nine original Mermaid nodes from that screenshot. This remains a separate Mermaid test rather than SVG-file-import evidence.

The supported conclusion is therefore: **this seven-node SVG-producing source can be reconstructed into a readable, editable Lucid flowchart with complete logical content, while substantial drawing details are adapted. Direct SVG-file import, exact SVG appearance, and SVG export remain unqualified by the saved live evidence.**

## Evidence identity

SHA256 values computed from the files reviewed here:

| File | SHA256 |
| --- | --- |
| Canonical D3 source recipe | `d02ee12bf2bea120a578a21fd17ae1f560f1e8a33dc43b6be36284984d73f257` |
| Source gallery PNG | `7815bdf1712fa454f34b0b6a35de9d7f82ab4afc1513ae9361bc878f45a17e31` |
| D3 Mermaid code capture | `f9aed39b24b1023114274d4daa59b3ef7d7c193469933e896fee60cca1c25cf9` |
| D3 native final capture | `a4a83b629dcb605a0516ef117045d949aee52dc60ed0b9735d1c68709fda2d95` |
| D3 native moved capture | `2af9e9a61edc6337481ebdf93980550893e919032a431d1f847be4be8302b2b7` |
| D3 native label-edit capture | `577e6277b502c0054683046ffe67df5dc654803abab5f9d6b3938be3ccd85374` |
| Prepared static SVG derivative | `0b8ece1d8a3c5c6e94698ade84fa43ec3a12ff8accc7f0e98f5057fddb62e517` |
| Mermaid derivative | `82a72d8772851c68c268b3ed290559fbf6f54ca964b82a30f2bbe6f2aae2684c` |

The canonical recipe hash matches the mapping manifest's source hash. A separate XML count confirms seven node groups, seven directed polylines, and ten logical text labels in the prepared static SVG. All twelve local Markdown links in this report resolve. These checks supplement the visual review; they do not demonstrate a service import.

All conclusions describe these saved artifacts and the dated live ledger. Current account capabilities were not rechecked, and this review makes no generic promise about other SVGs, shapes, styles, or Lucid plans.

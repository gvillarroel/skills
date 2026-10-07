# Select native diagram families and routes

Preserve the source notation when converting. The compiler consumes explicit types, properties, and connections; it does not classify arbitrary SVG shapes. Query [native_catalog.py](../scripts/native_catalog.py) for required fields.

## Flowcharts and responsibility lanes

Choose `process` for an established action, `terminator` for start/end, `decision` for branching, `data` for input/output, `document` for a report/document, and `predefinedProcess` for a separately defined subprocess. `predefinedProcess` requires `properties.sideWidth` from 0 to 0.33. `connector` is an on-page *shape*; relationships remain line objects. `offPageLink` is a flowchart continuation symbol, not an automatic page-link action. Preserve branch labels and direction. [Flowchart type contract](https://developer.lucid.co/docs/flowchart-library-si), [symbol meanings](https://lucid.co/diagram/flowchart/symbols)

For multi-owner processes, `swimLanes` requires `vertical`, `titleBar:{height,verticalText}`, and `lanes:[{title,width,headerFill,laneFill},...]`. With vertical columns, widths sum to the bounding-box width; with horizontal rows, they sum to its height. Place each step in its explicitly assigned lane. A colored box is not evidence of ownership. Reuse the source direction and lane order; when designing a new flowchart, consistent top-to-bottom or left-to-right flow aids reading. [Lane contract](https://developer.lucid.co/docs/container-library-si), [orientation example](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/swimlane.py), [flowchart guidance](https://lucid.co/diagram/flowchart/how-to-make-a-flowchart)

## BPMN

Use the exact BPMN types and unique properties:

- `bpmnActivity` requires `activityType`; `taskType` and two activity markers refine established behavior.
- `bpmnEvent` requires `eventGroup`; preserve event subtype, interrupting behavior, and catching/throwing meaning when known.
- `bpmnGateway` exposes exclusive, parallel, inclusive, event-based, and complex variants. Select the subtype from process semantics.
- `bpmnPool` requires title and 1–50 lanes; `bpmnBlackBoxPool` represents an explicitly opaque participant. Pools communicate participants and lanes communicate responsibility.
- Data objects/stores, conversations, choreographies, annotations, and groups have distinct roles. A group does not create a participant or change control flow.

Use `properties` for all these type-specific fields. Query exact enums through `--type bpmnActivity`, `--type bpmnEvent`, and `--type bpmnPool`. BPMN lanes have numeric width despite a Boolean typo in the vendor table; the helper follows its numeric example and dimension explanation. Do not copy the malformed activity JSON example. [BPMN contract](https://developer.lucid.co/docs/bpmn-20-library-si), [visual property reference](https://developer.lucid.co/docs/bpmn-shapes-reference-si)

Keep sequence flow, message flow, and association distinct. Sequence flow orders activities; message flow crosses participant/pool boundaries; association relates explanatory artifacts. Lucid documents dashed message flow with a source circle and dotted associations. The line catalog supports `openCircle`, `bpmnConditional`, and `bpmnDefault`; select markers only from explicit relation meaning. The official BPMN converter's generic arrows do not establish message-flow marker fidelity. No renderer or schema check certifies executable BPMN behavior or every possible marker combination. [notation](https://lucid.co/diagram/bpmn/tutorial), [endpoint contract](https://developer.lucid.co/docs/lines-si), [converter example](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/bpmn-converter/converter/utils/line_utils.py)

## ER diagrams

For an explicit entity/field/cardinality graph at fixed positions, compose native `table` objects and relationship lines. A table requires `rowCount`, `colCount`, and `cells`; cells use zero-based x/y positions, literal text, optional merges and color fill. Preserve entity names, key markers, field order/types, and original notation. Use `one`, `exactlyOne`, `many`, `zeroOrOne`, `oneOrMore`, or `zeroOrMore` only from supplied cardinality. Do not replace every relationship with a default one-to-many connection. [table contract](https://developer.lucid.co/docs/table-library-si), [official ER composition](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/erdiagram.py)

This produces editable tables and lines, without establishing the UI ER entity's field tracking, collapse, SQL export, or schema-update behavior. For those capabilities, use the UI Entity Relationship library or its database metadata import: CSV/TSV/TXT query output identifies keys and creates real ER entries. Use supplied metadata and the selected DBMS's documented route. [ER UI workflow](https://help.lucid.co/hc/en-us/articles/16471565238292-Create-an-Entity-Relationship-Diagram-in-Lucidchart)

## UML class diagrams

For fixed layout, use editable tables with explicit name/attribute/method compartments and native relationship markers. Preserve member visibility `+|-|#|~`, multiplicities, stereotypes, source compartment labels, and navigation direction. The official class example uses `generalization` at a parent, `aggregation` or `composition` at the whole, and dashed strokes for realization/dependency. An association need not be directed: do not add an arrow merely because the example defaults to one. Keep parent/whole roles explicit rather than tying them to left/right placement. [official class composition](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/umlclassdiagram.py), [native markers](https://developer.lucid.co/docs/lines-si)

Tables and relationship markers do not imply a dedicated SI class/entity type or semantic model validation. The example's assisted layout is an optional redesign; omit it for source-coordinate preservation.

## Sequence diagrams, organizations, and mind maps

Use [build_generated.py](../scripts/build_generated.py) for `orgChart`, `mindMap`, `umlSequence`, and `assistedLayout` when reflow is acceptable. These belong in `pages[].dataBackedShapes` and are excluded from the fixed-layout builder. Read [generated-layouts.md](generated-layouts.md) for exact inputs, limits, and CLI examples. The generated helper supports inline collections and explicit native graph integration; it rejects external data, `imageUrlField`, and resource directives as a local profile. It validates identity/parent references and cycles, requires one mind-map root locally, and reports unmeasured geometry. Org charts and mind maps each have a documented 4,000-item document limit; sequence markup is nonempty and at most 50,000 characters. [vendor contract](https://developer.lucid.co/docs/data-backed-shapes-si), [collections](https://developer.lucid.co/docs/data-si)

For UI sequence creation, activate UML Sequence and select Use Markup. Supported groupings include `alt|opt|par|loop|critical`; the UI does not support styling syntax. Ungrouping allows individual styling but ends markup editing. Do not assume full PlantUML support or route a class diagram through sequence markup. Mermaid is another route only when the current supported family and editing mode suit the request; use the verified editor workflow rather than assuming every family pastes into independent shapes. [UML markup](https://help.lucid.co/hc/en-us/articles/16262874090900-Create-a-sequence-diagram-with-UML-markup-in-Lucidchart), [editor workflows](editor-workflows.md)

## Cloud and general network diagrams

Use `namedShape` with a documented literal `className` for AWS 2024, Azure 2021/2024, or GCP 2021 service icons. Use `namedContainer` for their exact boundary classes. Examples: EC2 icon `ArchAmazonEC2AWS2024` differs from VPC boundary `VirtualPrivateCloudVPCAWS2024`; Azure 2024 Resource Group is `ResourceGroupContainerAzure2024`; GCP region is `GCP2021ContainerRegion`. Provider/version and shape/container kind are explicit inputs. Preserve native library styles unless source/user styling is explicit; GCP icons default to Google Blue `#4285F4` without a fill. Omitted text size uses native auto-scaling, so inspect readability after rendering. [AWS](https://developer.lucid.co/docs/aws-2024-library), [Azure 2021](https://developer.lucid.co/docs/azure-2021-library), [Azure 2024](https://developer.lucid.co/docs/azure-2024-library), [GCP](https://developer.lucid.co/docs/gcp-2021-library), [text defaults](https://developer.lucid.co/docs/reference-si)

The catalog blocks unresolved Azure 2021 VM spellings and Private Endpoint kind. Do not synthesize class names or assume other UI libraries work through `namedShape`. Use labeled primitives for generic network nodes and verified artwork for unsupported brand symbols. Preserve explicit link direction and boundaries; color does not establish traffic or trust.

## Artwork fallback

Keep complex icons and illustrations as SVG custom shapes through [editor-workflows.md](editor-workflows.md). Imported artwork is not an editable semantic graph. SI `image` requires a stroke and an ImageFill with a verified resource reference; packaged SVG images are converted to PNG. The fixed-layout builder rejects `image` until a resource-bearing contract is provided rather than emitting a broken reference. [custom libraries](https://help.lucid.co/hc/en-us/articles/14931750819476-Shape-libraries-in-Lucidchart), [image type](https://developer.lucid.co/docs/standard-library-si), [image conversion](https://developer.lucid.co/docs/images-si)

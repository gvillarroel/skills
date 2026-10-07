# Lucid diagram element selection evidence

Observed on 2026-10-07. This report records current official Lucid contracts and implementation recommendations for SVG/Lucid transformations. It is a project research record, not a claim that the service rendered the examples successfully. No account, UI, import request, or remote document was changed during this research.

Use the distinction throughout this report:

- **Documented contract:** a property/type appears in current Lucid Standard Import documentation.
- **Official example:** Lucid-owned code composes documented objects into a diagram. Its defaults and layout algorithm are examples, not a preservation guarantee.
- **Recommended compiler rule:** a conservative local transformation justified by the contract. This still needs local validation and, where possible, a service render.
- **Unknown:** service behavior, semantic validation, or fidelity has not been established.

## Selection matrix

| Source evidence and intent | Preferred representation | Why this is defensible | Boundary and fallback |
| --- | --- | --- | --- |
| An explicit flowchart role such as action, branch, start/end, input/output, document, or subprocess | The matching native Flowchart type | SI documents these symbols; Lucid's symbol guide assigns their meanings. | Do not infer a decision from every diamond or a terminator from every ellipse. Without a role, use a geometry primitive. [SI Flowchart](https://developer.lucid.co/docs/flowchart-library-si), [symbol meanings](https://lucid.co/diagram/flowchart/symbols) |
| Explicit BPMN activity/event/gateway subtype and participants | A `bpmn*` shape with exact enum properties, plus documented line endpoints and strokes | Native properties expose markers and event/gateway variants. | A visually similar circle/diamond cannot establish BPMN meaning. Do not claim an executable BPMN model or valid combinations merely because JSON validates. [SI BPMN](https://developer.lucid.co/docs/bpmn-20-library-si), [visual reference](https://developer.lucid.co/docs/bpmn-shapes-reference-si) |
| A process step is assigned to a named owner or team | Native `swimLanes`; for explicitly BPMN participants, `bpmnPool` | The native lane schema preserves title, orientation, widths, and fills; lanes communicate responsibility. | A colored rectangle is not enough evidence of a lane. Geometric membership alone does not establish responsibility. [SI containers](https://developer.lucid.co/docs/container-library-si), [BPMN participant meaning](https://lucid.co/diagram/bpmn/tutorial) |
| Entity names, ordered fields, keys, and cardinalities are explicitly supplied | Native `table` plus cardinality endpoints | Lucid's ER generator uses this composition. | It is an editable table composition, not proof of the UI ER entity's field attachment, schema import, collapse, update, or SQL export capabilities. Preserve notation; do not replace Chen diamonds with Crow's Foot without instruction. [official ER generator](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/erdiagram.py), [ER UI capabilities](https://help.lucid.co/hc/en-us/articles/16471565238292-Create-an-Entity-Relationship-Diagram-in-Lucidchart) |
| Class names, compartments, member visibility, relationship types, and multiplicities are explicitly supplied | Native `table` plus UML endpoint styles | Lucid's class generator uses tables, `generalization`, `aggregation`, and `composition`. | Do not label an arbitrary table as a class; do not assume a diamond points to the whole without evidence. Preserve source compartment labels rather than inserting example labels. [official UML generator](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/umlclassdiagram.py) |
| Participant/message order is supplied as supported UML sequence markup; generated layout is acceptable | `dataBackedShapes[].type="umlSequence"` | SI accepts nonempty PlantUML-style sequence markup, at most 50,000 characters. | It generates its own size/layout. Full PlantUML syntax and styling are not guaranteed. Markup editing and individual element editing have different UI behavior. [data-backed contract](https://developer.lucid.co/docs/data-backed-shapes-si), [supported UI markup](https://help.lucid.co/hc/en-us/articles/16262874090900-Create-a-sequence-diagram-with-UML-markup-in-Lucidchart) |
| Person IDs and supervisor IDs form an explicit organization dataset; reflow is acceptable | `dataBackedShapes[].type="orgChart"` with a referenced collection | Native data-backed org chart represents the hierarchy, rather than a drawing of boxes. | It is not a fixed-coordinate reconstruction. Preserve names and relationships; verify duplicates, missing supervisors, roots, and cycles locally. Dataset limit is 4,000 users across the document. [data-backed contract](https://developer.lucid.co/docs/data-backed-shapes-si) |
| Explicit cloud service and provider/library version | `namedShape` with an exact verified `className`; use `namedContainer` for cloud boundaries | SI exposes AWS 2024, Azure 2021/2024, and GCP 2021. | Never create a class name by concatenating a label and suffix. A generic cloud shape does not imply AWS. Native icons may differ from the source icon revision. [supported libraries](https://developer.lucid.co/docs/shapes-si) |
| Generic node/edge diagram with no formal notation | Simple primitive plus native text and attached lines | Preserves editable geometry without assigning a formal role. | Preserve explicit topology. A line crossing is not a junction and nearby shapes are not automatically connected. [shape primitives](https://developer.lucid.co/docs/shape-library-si), [lines](https://developer.lucid.co/docs/lines-si) |
| Closed polygon with an explicit editable outline, simple paint, and 3–100 vertices | `flexiblePolygon` with normalized vertices | The SI shape supports arbitrary polygon borders relative to a bounding box. | It does not accept SVG path curves, holes, `fill-rule`, masks, or gradients. Do not reduce a curved icon to a polygon silently. [shape primitives](https://developer.lucid.co/docs/shape-library-si) |
| Complex branded artwork, text outlines, filters, gradients, clipping, or ambiguous symbols; appearance is the priority | SVG custom shape through the documented UI, or image in an SI package with an explicit loss report | SVG custom libraries provide an artwork route; SI explicitly converts packaged SVG images to PNG. | Imported SVG artwork is not a native semantic diagram. Choose native text overlay for independently editable labels. A mixed native/artwork result must disclose which objects remain artwork. [custom libraries](https://help.lucid.co/hc/en-us/articles/14931750819476-Shape-libraries-in-Lucidchart), [SI images](https://developer.lucid.co/docs/images-si) |

## Common implementation contract

The Standard Import shape contract requires `id`, `type`, and `boundingBox`. Common optional fields are `style`, `text`, `actions`, `customData`, `linkedData`, `opacity`, `note`, and `zIndex`; specific types can prohibit them. `boundingBox` has numeric `x,y,w,h` and optional clockwise `rotation` in degrees from 0 to 360. IDs are 1–36 characters in the alphabet `A-Z a-z 0-9 - _ . ~` and must be unique across the document. Colors use RGB/RGBA hexadecimal strings. `opacity` is an integer from 0 to 100. A compiler should require finite coordinates and positive dimensions as its conservative policy, without claiming all such constraints are vendor-enforced. [Shapes](https://developer.lucid.co/docs/shapes-si), [reference types and geometry](https://developer.lucid.co/docs/reference-si)

`style.fill` supports `color` or `image`, not an arbitrary SVG paint server. `style.stroke` uses an integer pixel `width` and `solid|dashed|dotted`; `style.rounding` is twice the corner radius in pixels. `text` can use HTML, and omission of a font size triggers auto-scaling. There is no comprehensive documented HTML/CSS text whitelist, font embedding contract, or SVG glyph metric preservation guarantee. Escape plain source labels as text before inserting them into HTML. Do not equate a numeric font size with exact SVG typography. [style and text reference](https://developer.lucid.co/docs/reference-si)

Default to a fixed layout for SVG reconstruction. Make every reflow feature explicit: `assistedLayout:true` on a supported container rearranges children on the first document open, and the data-backed `assistedLayout` generator can wrap a subset of shapes or all shapes. Retain the original source as evidence before reflow. The overview warns that unchanged SI input can produce different results over time. [containers](https://developer.lucid.co/docs/container-library-si), [data-backed layouts](https://developer.lucid.co/docs/data-backed-shapes-si), [SI overview](https://developer.lucid.co/docs/overview-si)

## Primitive and Standard Library contracts

Use these types when shape identity is geometric rather than semantic. The following table is the complete documented Shape Library type list observed in this review, plus the Standard Library types. [Shape Library](https://developer.lucid.co/docs/shape-library-si), [Standard Library](https://developer.lucid.co/docs/standard-library-si)

| Type | Additional properties or restrictions | Appropriate compiler behavior |
| --- | --- | --- |
| `rectangle` | Common shape fields | Axis-aligned rectangle; permit supported rounding only when effective corner radii match the native representation. |
| `circle` | Common shape fields; no `ellipse` type documented | Exact candidate for a circle. A non-square box as an ellipse remains an unverified approximation; do not report it as exact solely because the schema accepts a box. |
| `cloud`, `diamond`, `doubleArrow`, `hexagon`, `isoscelesTriangle`, `octagon`, `pentagon`, `rightTriangle` | Common shape fields | Use when the source explicitly declares the symbol or verified outline, not from a rough bounding box match. |
| `cross` | Optional `indent:{x,y}`; both supplied members numeric 0–0.5 | Preserve explicit arm indentation. |
| `singleArrow` | Optional `orientation:right|left|up|down`, default `right` | A filled arrow shape is not an attached connector. |
| `flexiblePolygon` | Required `vertices:[{x,y},...]`, 3–100 relative positions | Normalize verified simple closed polygon vertices to the final bounding box; preserve order. |
| `polyStar` | Required `shape:{numPoints,innerRadius}`; points 3–25, inner radius 0–1 | Use only when a regular parametric star is established; do not use for arbitrary spiky polygons. |
| `text` | Does not accept `style` | Use `text` HTML for supported text formatting; preserve standalone labels rather than fusing labels into decorative artwork. |
| `hotspot` | Does not accept `text` | Use only for explicit interactive areas, not a generic invisible semantic node. |
| `image` | Required top-level `stroke` and `image` | `image` is an ImageFill; use `imageScale:"fit"` to preserve aspect ratio. `stretch` can distort. Packaged SVG is rasterized. |
| `stickyNote` | Common fields in example | Use only for an explicit note-card role; do not assign operational meaning. |

General image scaling enums are `fit|fill|stretch|original|tile`; `fit` preserves the complete image and aspect ratio, `fill` can crop, and the default `stretch` can distort. [ImageFill contract](https://developer.lucid.co/docs/reference-si)

## Flowchart contracts and role mapping

Native semantic substitution needs an explicit role from user intent, source metadata, or supplied graph. The symbol guide identifies `process` as an action, `terminator` as start/end, `decision` as branching, `data` as input/output, `document` as a report/document, and `predefinedProcess` as a separately defined subprocess. `connector` is an on-page flowchart symbol, not the SI line object. `offPageLink` continues flow across pages. [meaning](https://lucid.co/diagram/flowchart/symbols), [SI contract](https://developer.lucid.co/docs/flowchart-library-si)

| Contract class | Exact types and properties |
| --- | --- |
| No additional required properties beyond common fields | `connector`, `database`, `data`, `decision`, `delay`, `directAccessStorage`, `display`, `document`, `internalStorage`, `manualInput`, `manualOperation`, `merge`, `multipleDocuments`, `note`, `offPageLink`, `paperTape`, `preparation`, `process`, `storedData`, `terminator` |
| Required shape-specific properties | `braceNote`: `rightFacing:boolean`, `braceWidth:number`; `predefinedProcess`: `sideWidth:number` between 0 and 0.33 |
| Text forbidden | `or`, `summingJunction` |

For diagram redesign, a consistent top-to-bottom or left-to-right direction, concise labels, and swimlanes for responsibility are supported Lucid recommendations. For conversion, preserve the existing reading direction and branching labels unless the user requests redesign. Treat color guidance as an interpretive recommendation, not a reason to change source meaning; preserve supplied palettes and add a key for ambiguous category colors. [flowchart design](https://lucid.co/diagram/flowchart/how-to-make-a-flowchart), [diagram key recommendation](https://help.lucid.co/hc/en-us/articles/31745848620308-Flowcharts-A-guide-from-start-to-finish)

## BPMN exact contracts

Every type below is a normal `pages[].shapes[]` entry using common shape fields. Required/optional refer to the vendor tables. Marker combinations are not certified as BPMN-valid by this documentation. [BPMN 2.0 Library](https://developer.lucid.co/docs/bpmn-20-library-si)

| Type | Required extra properties | Optional extra properties and enums |
| --- | --- | --- |
| `bpmnActivity` | `activityType:task|transaction|eventSubProcess|callActivity` | `taskType:none|send|receive|user|manual|businessRule|service|script`; `activityMarker1` and `activityMarker2`: `none|subProcess|loop|parallelMI|sequentialMI|adHoc|compensation`; each defaults to `none` |
| `bpmnEvent` | `eventGroup:start|intermediate|end` | `eventType:none|message|timer|escalation|conditional|link|error|cancel|compensation|signal|multiple|parallelMultiple|terminate` default `none`; `nonInterrupting` and `throwing` booleans default `false` |
| `bpmnGateway` | None | `gatewayType:none|exclusive|eventBased|parallel|inclusive|exclusiveEventBased|complex|parallelEventBased`, default `none` |
| `bpmnDataObject` | None | `dataType:none|collection|input|output`, default `none` |
| `bpmnDataStore`, `bpmnBlackBoxPool`, `bpmnTextAnnotation` | None | No unique extra properties documented |
| `bpmnConversation` | None | `isCall`, `isSubConversation` booleans, default `false` |
| `bpmnChoreography` | `choreographyType:task|subchoreography|call`; `participants` array of 1–100 objects `{text:string,multipleParticipants:boolean}` | `name`, `taskName` strings; `initiatingMessage`, `responseMessage` booleans default `false` |
| `bpmnGroup` | None | `magnetize:boolean` default `true`; rotation unsupported |
| `bpmnPool` | `title:string`; `lanes` array of 1–50 objects `{title:string,width:number,laneFill:hex}` | `vertical:boolean` default `true`, `verticalLaneText:boolean` default `false`, `magnetize:boolean` default `true`; rotation unsupported |

For `bpmnPool`, lane widths sum to the appropriate total dimension for the orientation. The lane property table calls `width` a Boolean, while the explanation and example use a numeric width (300). Treat numeric finite positive width as the implementation candidate and record this documentation inconsistency; do not emit a Boolean. The activity example also contains a missing colon after `"taskType"`; follow the property contract and emit valid JSON. [BPMN pool and activity tables](https://developer.lucid.co/docs/bpmn-20-library-si)

BPMN role interpretation belongs in a reference, not geometric inference:

- Events distinguish start/intermediate/end and catching/throwing; a generic circle does not encode that distinction.
- `user` and `manual` tasks are distinct; a human task label alone may not specify whether an application participates.
- A subprocess marker, loop marker, and multi-instance marker express different behavior; do not infer a loop from a returning line alone.
- Pools represent participants; lanes assign responsibility. A BPMN group is an organizational artifact, not a new participant or control-flow boundary.
- Sequence flow, message flow, and association must retain distinct meaning. Lucid's tutorial describes message flow across pools, with a dashed line and source circle; associations use dotted lines. Apply a compatible endpoint/stroke only after the relation is explicit. Validate the source/target pool relationship rather than converting every dashed arrow to message flow.

These are interpretive constraints from [Lucid's BPMN tutorial](https://lucid.co/diagram/bpmn/tutorial). SI exposes rendering objects and endpoints; it does not promise executable BPMN XML, behavioral validation, or lossless conversion of arbitrary BPMN features.

## Containers, lanes, and grouping

Containers are shapes. Groups are `pages[].groups[]` objects with `id` and optional `items:[ID,...]` containing shapes, lines, or groups; they cannot contain layers. Use groups for collective editing, and use containers for a visible boundary or semantic region. Do not invent a `parent` property for normal SI shapes. [Container Library](https://developer.lucid.co/docs/container-library-si), [Groups](https://developer.lucid.co/docs/groups-si)

| Type | Exact extra contract |
| --- | --- |
| `braceContainer`, `bracketContainer` | Optional `magnetize:boolean`, default `true` |
| `circleContainer`, `pillContainer`, `rectangleContainer`, `roundedRectangleContainer` | Optional `magnetize`, `containerTitle:{text:string}`, `assistedLayout:boolean` |
| `diamondContainer` | Optional `magnetize`, `assistedLayout`; no `containerTitle` listed |
| `swimLanes` | Required `vertical:boolean`, `titleBar:{height:number,verticalText:boolean}`, and `lanes:[{title:string,width:number,headerFill:hex,laneFill:hex},...]`; optional `magnetize` |

All Container Library types reject bounding-box rotation. Lane widths must sum to the dimension applicable to orientation. Avoid applying group scaling to rotated lane/table structures and reporting it as exact. Disable assisted layout for fixed-coordinate preservation; explicitly supplied memberships and containment bounds should be validated independently. [Container Library](https://developer.lucid.co/docs/container-library-si)

The Groups property table has a duplicated `linkedData` row for the z-order description; the example names that field `zIndex`. Use `zIndex` and record the documentation inconsistency. Do not copy duplicate IDs in vendor examples. [Groups](https://developer.lucid.co/docs/groups-si), [Flowchart examples](https://developer.lucid.co/docs/flowchart-library-si)

## Table, ER, and UML composition

The native `table` contract requires `rowCount`, `colCount`, and `cells`. Each cell requires zero-based `xPosition,yPosition`; optional `mergeCellsRight`, `mergeCellsDown` default to zero, and optional `text` is a string. A provided cell `style` requires a `fill` ColorFill. Optional `userSpecifiedRows` and `userSpecifiedCols` are arrays of `{index:number,size:number}` in pixels; unspecified rows/columns divide the remaining box dimension. `verticalBorder` and `horizontalBorder` default true. Rotation is unsupported. A compiler should validate cell bounds, merge overlap, and positive available size rather than let the importer silently resolve an invalid grid. [Table Library](https://developer.lucid.co/docs/table-library-si)

The official ER generator composes a two-column table with a merged entity header, field/type rows, and key labels, then uses cardinality styles on shape-attached smart lines. Its supported cardinalities are `one|many|zeroOrOne|zeroOrMore|oneOrMore|exactlyOne`, with input aliases such as `0..1` and `1..*`. Keep the distinction between `one` and `exactlyOne` because both are separate documented endpoint styles. A field-level attachment to a native ER entity cannot be assumed for a generic table; use an explicit relative table attachment or identify the limitation. [official ER code](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/erdiagram.py), [endpoint catalog](https://developer.lucid.co/docs/lines-si)

The official UML class generator uses one-column tables and formats members with visibility symbols `+|-|#|~`. Its relationship recipe provides this implementation evidence:

| Explicit relationship | Endpoint at the semantic target | Stroke | Important choice |
| --- | --- | --- | --- |
| Inheritance/generalization | `generalization` at the parent | `solid` | Do not reverse parent/child based on left/right position. |
| Realization/implementation | `generalization` at the implemented interface/contract | `dashed` | Preserve distinction from inheritance. |
| Aggregation | `aggregation` at the whole | `solid` | The whole is a semantic role, not necessarily the `to` node in arbitrary source metadata. |
| Composition | `composition` at the whole | `solid` | Preserve the filled/hollow diamond distinction. |
| Dependency | `arrow` at target in the official sample | `dashed` | Treat the sample mapping as an example; preserve source arrow type when explicit. |
| Association | `arrow` at target in the official sample | `solid` | A generic UML association can be non-directed; never add navigation when source data does not supply it. |

The example always places these markers at its `to` endpoint and uses `none` at `from`. Adapt the recipe to source semantics; do not hard-code every UML association as directional merely because an example defaults that way. Preserve multiplicities as native line text. The sample enables an invisible assisted-layout container; omit that for source-coordinate preservation. [official UML class code](https://github.com/lucidsoftware/sample-lucid-rest-applications/blob/main/standard-import/generic-diagrams/implementations/umlclassdiagram.py)

## Exact line marker catalog

The current documented SI `EndpointStyle` enum has 22 values:

`none`, `aggregation`, `arrow`, `hollowArrow`, `openArrow`, `async1`, `async2`, `closedSquare`, `openSquare`, `bpmnConditional`, `bpmnDefault`, `closedCircle`, `openCircle`, `composition`, `exactlyOne`, `generalization`, `many`, `nesting`, `one`, `oneOrMore`, `zeroOrMore`, `zeroOrOne`.

Endpoint `style` is required for every endpoint type. A `shapeEndpoint` requires `shapeId` and optionally relative `{x,y}` from 0 to 1; omission on both attached endpoints creates a smart line. `positionEndpoint` uses absolute `{x,y}` and is independent of shapes. `lineEndpoint` requires `lineId` and scalar position 0–1. `lineType` is `straight|elbow|curved`. `joints` are for straight lines and `elbowControlPoints` must make right angles. Curved-line Bézier control points are not documented here; do not claim arbitrary SVG cubic routes survive through `curved`. Line text is an array with `text`, scalar position 0–1, and `side:top|middle|bottom`. [Lines](https://developer.lucid.co/docs/lines-si)

Smart lines improve future movement but can change source routing. Fixed relative anchors and explicit supported joints are preferable when route preservation is required. A filled `singleArrow`/`doubleArrow` shape is appropriate decorative geometry; a native line is appropriate when the graph says the object connects nodes. These are recommended policies, not automatic meaning detection.

## Cloud named shape contracts

`namedShape` and `namedContainer` both require an exact `className` in addition to common fields. Documented container nesting is geometric: place the contents inside the container bounding box. Preserve the provider and library revision explicitly. GCP icons default to `#4285F4` without a fill; avoid forcing a color when retaining provider defaults is intended. [AWS 2024](https://developer.lucid.co/docs/aws-2024-library), [Azure 2021](https://developer.lucid.co/docs/azure-2021-library), [Azure 2024](https://developer.lucid.co/docs/azure-2024-library), [GCP 2021](https://developer.lucid.co/docs/gcp-2021-library)

| Version | Verified sample `namedShape` values | Verified sample `namedContainer` values | Literal lookup boundary |
| --- | --- | --- | --- |
| AWS 2024 | `ArchAmazonEC2AWS2024`, `ArchAWSLambdaAWS2024`, `ArchAmazonSimpleStorageServiceAWS2024`, `ArchAmazonRDSAWS2024`, `ArchAmazonAPIGatewayAWS2024` | `AWSAccountAWS2024`, `RegionAWS2024`, `AvailabilityZoneAWS2024`, `VirtualPrivateCloudVPCAWS2024`, `PrivateSubnetAWS2024`, `PublicSubnetAWS2024` | Classes end with `AWS2024`; icon `ArchAmazonVirtualPrivateCloudAWS2024` is distinct from VPC container. |
| Azure 2021 | `VirtualMachineAzure2021`, `FunctionAppsAzure2021`, `StorageAccountsAzure2021`, `AzureSQLAzure2021`, `AzureActiveDirectoryAzure2021` | `ResourceGroupAzure2021`, `SubnetAzure2021`, `SubscriptionAzure2021`, `VirtualNetworkAzure2021` | The sample uses `VirtualMachinesAzure2021` while the Common Shapes table uses singular `VirtualMachineAzure2021`; do not resolve this inconsistency through guessing. |
| Azure 2024 | `VirtualMachineAzure2024`, `FunctionAppsAzure2024`, `StorageAccountsAzure2024`, `AzureSQLAzure2024`, `EntraIDProtectionAzure2024`, `AzureOpenAIAzure2024` | `ResourceGroupContainerAzure2024`, `SubnetContainerAzure2024`, `SubscriptionContainerAzure2024`, `VirtualNetworkContainerAzure2024` | 2024 container names do not follow the 2021 spelling scheme. |
| GCP 2021 | `GCP2021ComputeEngineIcon`, `GCP2021CloudRunIcon`, `GCP2021CloudStorageIcon`, `GCP2021CloudSQLIcon`, `GCP2021PubsubIcon` | `GCP2021ContainerProjectZoneCloudServiceProvider`, `GCP2021ContainerRegion`, `GCP2021ContainerZone`, `GCP2021ContainerSubNetwork`, `GCP2021ContainerKubernetesCluster`, `GCP2021ContainerPod` | Classes start with `GCP2021`; exact capitalization, such as `SubNetwork`, matters. |

The provider pages call their category lists a full catalog but display category *example* class names. A deterministic bundled allowlist must use exact names that were actually documented, not every plausible spelling. Add an explicitly requested new service only after verifying its exact class and shape/container type from current primary evidence. Do not imply arbitrary UI library classes work through `namedShape`.

For implementation, the following complete container lists are explicitly documented on the provider pages:

- AWS 2024: `AWSAccountAWS2024`, `AWSCloudAWS2024`, `AWSCloudAltAWS2024`, `AWSCloudAltDarkAWS2024`, `AWSCloudDarkAWS2024`, `AWSIoTGreengrassAWS2024`, `AWSIoTGreengrassDeploymentAWS2024`, `AWSStepFunctionsWorkflowAWS2024`, `AutoScalingGroupAWS2024`, `AvailabilityZoneAWS2024`, `CorporateDataCenterAWS2024`, `EC2InstanceContentsAWS2024`, `EcsClusterContainerAWS2024`, `EcsEc2ContainerAWS2024`, `EcsFargateContainerAWS2024`, `ElasticBeanstalkContainerAWS2024`, `GenericGroupAWS2024`, `PrivateSubnetAWS2024`, `PublicSubnetAWS2024`, `RegionAWS2024`, `SecurityGroupAWS2024`, `ServerContentsAWS2024`, `SpotFleetAWS2024`, `VirtualPrivateCloudVPCAWS2024`. [AWS catalog](https://developer.lucid.co/docs/aws-2024-library)
- Azure 2021: `AppServicePlanAzure2021`, `LogoContainerAzure2021`, `ResourceGroupAzure2021`, `SubnetAzure2021`, `SubnetWithNetworkSecurityGroupAzure2021`, `SubscriptionAzure2021`, `VirtualNetworkAzure2021`. [Azure 2021 catalog](https://developer.lucid.co/docs/azure-2021-library)
- Azure 2024: `AppServicePlanContainerAzure2024`, `ApplicationSecurityGroupContainerAzure2024`, `EventHubNamespaceContainerAzure2024`, `NetworkSecurityGroupContainerAzure2024`, `ResourceGroupContainerAzure2024`, `SubnetContainerAzure2024`, `SubnetWithNsgContainerAzure2024`, `SubscriptionContainerAzure2024`, `VirtualNetworkContainerAzure2024`. [Azure 2024 catalog](https://developer.lucid.co/docs/azure-2024-library)
- GCP 2021: `GCP2021ContainerUser1`, `GCP2021ContainerInfrastructureSystem2`, `GCP2021ContainerColoDCOnPremises`, `GCP2021ContainerSystem1`, `GCP2021ContainerExternalSaaSProviders`, `GCP2021ContainerExternalDataSources`, `GCP2021ContainerExternalInfrastructure3rdParty`, `GCP2021ContainerExternalInfrastructure1stParty`, `GCP2021ContainerProjectZoneCloudServiceProvider`, `GCP2021ContainerLogicalGroupingOfServicesInstances`, `GCP2021ContainerZone`, `GCP2021ContainerSubNetwork`, `GCP2021ContainerKubernetesCluster`, `GCP2021ContainerPod`, `GCP2021ContainerAccount`, `GCP2021ContainerRegion`, `GCP2021ContainerFirewall`, `GCP2021ContainerInstanceGroup`, `GCP2021ContainerReplicaPool`, `GCP2021ContainerOptionalComponent`, `GCP2021GoogleCloudLogoContainer`. [GCP catalog](https://developer.lucid.co/docs/gcp-2021-library)

## Data-backed diagram contracts

These objects belong in `pages[].dataBackedShapes`, not `pages[].shapes`. Their common fields are `id` and `type`; generated content size follows the dataset/markup rather than a fixed bounding box. [Pages](https://developer.lucid.co/docs/pages-si), [Data Backed Shapes](https://developer.lucid.co/docs/data-backed-shapes-si)

| Type | Required additional fields | Optional fields and limits |
| --- | --- | --- |
| `orgChart` | `position:{x,y}`, `collectionId`, `idField`, `foreignKeyField`, `nameField` | `roleField`, `imageUrlField`, `extraFields:[string]`; maximum 4,000 users across all document pages |
| `mindMap` | `position:{x,y}`, `collectionId`, `idField`, `parentIdField`, `textField` | Root parent field empty/absent; maximum 4,000 items across all document pages |
| `umlSequence` | `position:{x,y}`, `markup:string` | Markup nonempty, maximum 50,000 characters; PlantUML-style sequence markup |
| `assistedLayout` | No extra required fields | `shapeIds:[string]`; omission includes all page shapes |

A root `collections` entry requires `id` and exactly one of `dataSource` (CSV/TXT basename inside package `/data`) or inline `values:[object,...]`. Reject both/neither. The `/data` contents limit is 1 MB; `document.json` limit is 2 MB. Prefer inline values for a small self-contained graph. Images referenced by external URLs remain dependent on those resources and are not made self-contained by an org chart field. [Data](https://developer.lucid.co/docs/data-si), [package limits](https://developer.lucid.co/docs/overview-si)

The UML markup Help page documents arrows, participant activation, messages, notes, aliases, comments, and `alt|opt|par|loop|critical` groupings. It states that styling syntax is unsupported; individual element styling requires ungrouping, which ends markup editing. This is a meaningful workflow choice to disclose. Do not route a UML class diagram through sequence markup or assume the entire PlantUML language is available. [UML sequence Help](https://help.lucid.co/hc/en-us/articles/16262874090900-Create-a-sequence-diagram-with-UML-markup-in-Lucidchart)

## Implementation split

### Proposed self-contained catalog schema

Use a small factual catalog that a compiler can load without opening this project report. Keep compatibility facts separate from semantic recommendations and service-test status. This is a proposed local data format, not a vendor schema:

```json
{
  "schemaVersion": 1,
  "observedAt": "2026-10-07",
  "commonDefinitions": {
    "shape": {"required": ["id", "type", "boundingBox"]},
    "dataBackedShape": {"required": ["id", "type"]}
  },
  "nativeTypes": {
    "bpmnActivity": {
      "library": "bpmn-2.0",
      "placement": "shapes",
      "common": "shape",
      "required": ["activityType"],
      "properties": {
        "activityType": {"jsonType": "string", "enum": ["task", "transaction", "eventSubProcess", "callActivity"]},
        "taskType": {"jsonType": "string", "enum": ["none", "send", "receive", "user", "manual", "businessRule", "service", "script"], "default": "none"},
        "activityMarker1": {"definition": "bpmnActivityMarker", "default": "none"},
        "activityMarker2": {"definition": "bpmnActivityMarker", "default": "none"}
      },
      "rotation": "common-contract",
      "sourceUrls": ["https://developer.lucid.co/docs/bpmn-20-library-si"]
    },
    "table": {
      "library": "table",
      "placement": "shapes",
      "common": "shape",
      "required": ["rowCount", "colCount", "cells"],
      "properties": {
        "rowCount": {"jsonType": "number"},
        "colCount": {"jsonType": "number"},
        "cells": {"jsonType": "array", "itemsDefinition": "tableCell"},
        "userSpecifiedRows": {"jsonType": "array", "itemsDefinition": "tableDimension"},
        "userSpecifiedCols": {"jsonType": "array", "itemsDefinition": "tableDimension"},
        "verticalBorder": {"jsonType": "boolean", "default": true},
        "horizontalBorder": {"jsonType": "boolean", "default": true}
      },
      "rotation": "prohibited",
      "sourceUrls": ["https://developer.lucid.co/docs/table-library-si"]
    }
  },
  "definitions": {
    "bpmnActivityMarker": {"jsonType": "string", "enum": ["none", "subProcess", "loop", "parallelMI", "sequentialMI", "adHoc", "compensation"]},
    "tableCell": {
      "jsonType": "object",
      "required": ["xPosition", "yPosition"],
      "properties": {
        "xPosition": {"jsonType": "number"},
        "yPosition": {"jsonType": "number"},
        "mergeCellsRight": {"jsonType": "number", "default": 0},
        "mergeCellsDown": {"jsonType": "number", "default": 0},
        "text": {"jsonType": "string"},
        "style": {"jsonType": "object", "required": ["fill"], "properties": {"fill": {"definition": "colorFill"}}}
      }
    },
    "tableDimension": {"jsonType": "object", "required": ["index", "size"], "properties": {"index": {"jsonType": "number"}, "size": {"jsonType": "number"}}},
    "colorFill": {"jsonType": "object", "required": ["type", "color"], "properties": {"type": {"jsonType": "string", "enum": ["color"]}, "color": {"jsonType": "string", "format": "rgb-or-rgba-hex"}}}
  },
  "semanticRoleMappings": {
    "flowchart:action": {"type": "process"},
    "flowchart:decision": {"type": "decision"},
    "flowchart:start": {"type": "terminator"},
    "flowchart:end": {"type": "terminator"}
  },
  "relationshipRecipes": {
    "uml:composition": {"markerAt": "whole", "marker": "composition", "stroke": "solid"},
    "uml:generalization": {"markerAt": "parent", "marker": "generalization", "stroke": "solid"}
  },
  "cloudClasses": {
    "ArchAmazonEC2AWS2024": {"type": "namedShape", "provider": "aws", "revision": "2024", "sourceUrl": "https://developer.lucid.co/docs/aws-2024-library"},
    "VirtualPrivateCloudVPCAWS2024": {"type": "namedContainer", "provider": "aws", "revision": "2024", "sourceUrl": "https://developer.lucid.co/docs/aws-2024-library"}
  },
  "compilerPolicies": [
    {"id": "integer-positive-table-dimensions", "origin": "local-policy"},
    {"id": "non-overlapping-table-merges", "origin": "local-policy"},
    {"id": "explicit-semantic-role-only", "origin": "local-policy"},
    {"id": "fixed-layout-default", "origin": "local-policy"}
  ],
  "serviceVerification": {"status": "not-tested"}
}
```

Expand the catalog from the exact tables above. Add `forbiddenFields:["style"]` for `text`, `forbiddenFields:["text"]` for `hotspot`, `or`, and `summingJunction`; use `rotation:"prohibited"` for tables and documented containers. Keep generated types under `placement:"dataBackedShapes"` with `layout:"generated"` and their own required fields and limits. Use a literal cloud class allowlist whose stored `type` must match the submitted object's type. Store enums as arrays, numeric bounds as numbers, defaults only where documented, and nested object requirements explicitly. For contradictory documentation such as BPMN lane width, include a `documentationIssue` and mark numeric validation as a local policy rather than quietly rewriting the claimed vendor contract.

The `semanticRoleMappings` and `relationshipRecipes` are operative only after the agent or source graph supplies the exact role. They must not be a classifier based on shape appearance. Leave family inference and notation selection in prose references.

Encode the following choices in deterministic scripts:

1. Validate a requested exact type against a documented allowlist, its unique properties, and field exclusions. Keep native family types distinct from geometric aliases.
2. Preserve source labels, node IDs, explicit edge endpoints, direction, marker styles, and ordering. Attach source provenance and semantic role as custom data when appropriate.
3. Normalize coordinates into a shared viewport and preserve page geometry. Set fixed page/layout settings intentionally; do not automatically enable reflow.
4. Validate lanes, table grids, group membership, reference IDs, marker enums, and library class/type combinations. Reject contradictory inputs with an actionable English message.
5. Emit a representation/loss manifest that identifies native semantic shapes, generic editable shapes, approximated outlines, text overlays, image artwork, omitted objects, and unverified service behavior.
6. Compile exact simple primitives only after effective transforms, paints, and geometry have been established. Unsupported SVG features require a preservation choice or explicit approximation; unsupported properties cannot be declared exact merely because they were ignored.
7. Make a native symbol from a supplied semantic role. A diagram-family label alone must not assign every node its role or every edge its meaning.
8. Preserve explicit marker geometry/meaning, including cardinalities, composition versus aggregation, and BPMN conditional/default flow. Never infer edge semantics from stroke color or dashed appearance alone.

Keep the following in concise in-skill references for agent judgment:

- Which diagram family fits the user question; preserve source notation unless redesign is requested.
- What evidence is enough to assign a semantic role; use user intent, structured data, explicit source metadata, or inspected source symbol definitions, with ambiguity recorded.
- Whether automatic layout improves the requested result enough to justify changing source geometry.
- When generic native objects communicate the content adequately and when a dedicated symbol, custom SVG artwork, or mixed representation is necessary.
- Which simplifications preserve meaning versus remove relevant structure; retain labels and relationship semantics before optimizing appearance.
- What a reviewer must inspect after remote import: text readability, marker direction, row/field connections, nesting, lane assignment, overlaps, clipping, and the loss manifest.

## Guarantees, gaps, and follow-up coverage

| Area | What this research establishes | What remains unknown or must be verified |
| --- | --- | --- |
| Type/property support | Exact native SI type/property names and enums documented above | Successful service rendering of this skill's payloads; library subscription/tenant behavior; future renderer changes |
| Flowchart/BPMN semantics | Official type catalog and Lucid's notation explanations | Arbitrary SVG semantics, valid BPMN enum combinations, executable models, universal diagram correctness |
| ER/UML class | Official table/line composition examples and real UI ER features | Dedicated ER/class SI types outside the listed catalog; equivalence to UI entity capabilities; preservation of field-level anchors and interactive collapse |
| Organization/sequence/mind map | Native generators and input contracts | Exact SVG positions, full PlantUML support, role/image fidelity, hierarchy validation behavior by the server |
| Cloud | Four SI library revisions and verified literal class names | Unlisted Cisco/other provider `namedShape` classes, all vendor asset revisions, service-specific icon colors/rounding/text anchors |
| SVG paint/text | SI supports a limited explicit style/text contract and SVG image rasterization | Font embedding, exact glyph metrics, SVG paint/filter/mask preservation, complete raw HTML/CSS support |
| Native layout/editability | Supported objects are imported as Lucid objects; groups/containers/data-backed layouts are described | Exact after-import editing behavior for every composition; arbitrary SVG decomposition; pixel-perfect correspondence |
| Routing | Attached/smart endpoints, 22 endpoint styles, straight/elbow/curved line modes | Exact arbitrary cubic SVG routes, crossing/junction intent, marker scaling, layout changes from smart routing |
| Exhaustive coverage scope | All observed SI library families relevant to the requested flowchart, ER, UML, BPMN, swimlane, org, and cloud/network tasks were reviewed | No claim to exhaustive coverage of every Lucid UI library or every SVG feature. Lucidspark-only library was excluded from Lucidchart family selection. |

Recommended acceptance cases: exact role-based flowchart; unknown-role primitive graph; simple polygon; explicit BPMN event/gateway/task/pool including conditional/default/message relations; ER cardinalities with field labels; UML composition/aggregation/inheritance; lanes with uneven widths; table merges; cloud icon plus boundary using each library revision; org dataset; UML sequence subset; unsupported SVG artwork; a fixed-layout and explicitly reflowed version of the same graph. Include negative cases for invented types/class names, ambiguous association direction, duplicate IDs, cyclic group membership, invalid grid merges, lane width mismatch, unsupported rotation, and source curves incorrectly marked exact.

Local output validation proves structural choices, not Lucid visual fidelity. A remote import/export round trip is required before promoting any new representation as visually verified.

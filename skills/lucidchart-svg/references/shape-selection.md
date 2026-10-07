# Choose compatible diagram elements

Use this reference when deciding how a supplied SVG or semantic graph should be represented in Lucidchart. Decide representation from the user's purpose and explicit source evidence before choosing native types. Geometry alone is not a semantic role.

## Preserve meaning before assigning symbols

1. Determine whether the user prioritizes artwork appearance, independently editable objects, formal notation, fixed coordinates, or generated layout. Follow their existing instructions; resolve routine implementation choices without extra confirmation.
2. Identify explicit source information: node/edge IDs, labels, direction, ownership, cardinality, relationship roles, source diagram code, metadata, and named symbol definitions. Keep unknown meanings unknown. A family label does not assign every node or edge its role.
3. Choose a documented semantic symbol only when its role is established. Otherwise choose a generic primitive, native text, and graph-attached line where their geometry/connection is explicit.
4. Keep artwork for unsupported curved outlines, branded symbols, text paths, gradients, filters, masks, and ambiguous graphical notation. Use native text overlays only when independently editable labels are requested and their content/placement is known. Explain mixed representations in the loss report.
5. Preserve the source notation, reading direction, labels, color categories, and graph topology. Redesign only when requested. A crossing is not a junction; proximity is not a connection; dashed lines do not establish message flow or optional relationships.

Lucid documents native semantic flowchart/BPMN libraries, geometric primitives, containers, tables, and four cloud library revisions. Its Standard Import contract does not infer arbitrary SVG semantics. [Supported libraries](https://developer.lucid.co/docs/shapes-si), [primitive shapes](https://developer.lucid.co/docs/shape-library-si)

## Use the offline catalog

Query the bundled helper for the specific type instead of reading the full catalog during ordinary use:

```text
uv run --script <skill>/scripts/native_catalog.py --type predefinedProcess
uv run --script <skill>/scripts/native_catalog.py --type table
uv run --script <skill>/scripts/native_catalog.py --cloud-class ArchAmazonEC2AWS2024
uv run --script <skill>/scripts/native_catalog.py --list
```

The source catalog is [native-shapes.json](native-shapes.json), observed 2026-10-07. The helper validates required fields, enums, nested arrays, normalized polygon coordinates, table grids and merges, lane dimensions, and literal cloud class names. Put type-specific vendor camelCase fields in a node's `properties` object. Common geometry, styling, labels, and rotation remain outside that object under the builder's input contract. Unsupported extra properties are rejected.

The catalog is a bounded local profile, not a full upstream schema or a remote-render guarantee. It rejects non-finite numbers, booleans used as numbers, unsupported resources/generators, invalid grids, lane widths that do not sum to the orientation's dimension, unresolved cloud classes, and undocumented extra fields. Polygon outlines must be simple and enclose nonzero area. Known literal nested labels are escaped before vendor emission. It does not assign roles, add defaults that imply meaning, or certify BPMN validity.

## Choose geometry or a semantic symbol

| Explicit source evidence | Compatible choice | Avoid |
| --- | --- | --- |
| A plain box with no established role | `rectangle` | Assigning `process` merely because it is a rectangle |
| A verified circular outline | `circle` | Treating every circle as an event or on-page connector |
| Elliptical outline | Explicit `ellipse` alias emits `circle`, reported as an approximation | Calling non-square circle rendering exact without a service check |
| Plain diamond or explicit branching role | `diamond` for geometry; `decision` for a flowchart branch; `bpmnGateway` only with BPMN meaning | Inferring gateway subtype from shape or labels alone |
| Explicit filled direction arrow artwork | `singleArrow` or `doubleArrow` | Treating a filled arrow shape as an attached graph connection |
| Explicit node-to-node relationship | Native line with supplied endpoints and markers | Inferring endpoints from proximity or adding navigation direction |
| Simple closed polygon with normalized outline | `flexiblePolygon`, 3–100 vertices | Silently flattening curves, holes, masks, or paint rules |
| Established action/start/end/input/document/subprocess | Corresponding Flowchart type | Applying formal roles to unrelated decorative shapes |
| Established ownership or participant region | `swimLanes`, `bpmnPool`, or documented cloud container as appropriate | Replacing an organizational boundary with a generic editing group |

The documented `text` shape prohibits `style`; `hotspot`, `or`, and `summingJunction` prohibit `text`. A text label may be a separate native object. Do not silently discard a source label to satisfy a selected shape. [Standard Library](https://developer.lucid.co/docs/standard-library-si), [Flowchart Library](https://developer.lucid.co/docs/flowchart-library-si)

## Preserve layout and editing intent

Default to fixed coordinates for reconstruction. Smart lines adjust their attachments when shapes move and can change routing; use explicit anchors and supported control points when source routing matters. Generic curved lines do not provide a documented arbitrary SVG Bézier-path contract. [Lines](https://developer.lucid.co/docs/lines-si)

Groups provide collective editing; containers supply visible boundaries and enclosure behavior. `assistedLayout:true` is an explicit reflow choice for supported container types. Data-backed org/mind-map/sequence/layout generators derive their dimensions from input, and cannot preserve SVG positions exactly. Tables and documented container types prohibit rotation; the compiler also rejects cloud-container rotation conservatively. [Groups](https://developer.lucid.co/docs/groups-si), [containers](https://developer.lucid.co/docs/container-library-si), [generated layouts](https://developer.lucid.co/docs/data-backed-shapes-si)

Do not add an assisted-layout field to `swimLanes`: an official example uses it, but its type-specific contract does not list it. Use a supported layout route and document the intended reflow. Cloud class names require literal verification and correct `namedShape`/`namedContainer` kind; do not synthesize names or substitute an icon for a boundary. Azure 2021's singular/plural VM names and its ambiguous Private Endpoint kind are deliberately blocked pending verification.

## Validate and report the representation

Run the native builder and inspect the resulting package and manifest. Verify labels, endpoints, marker direction, table row order/merges, region containment, lane ownership, overlaps, clipping, and text readability. Report generic editable shapes, formal semantic shapes, approximations, artwork, omissions, and unresolved meaning separately. Offline contract success establishes package structure; a live import/render/export establishes what the service actually preserved.

Use [diagram-families.md](diagram-families.md) for notation choices and routes, [native-reconstruction.md](native-reconstruction.md) for the graph workflow, and [fidelity.md](fidelity.md) for SVG fidelity limits. An unchanged SI package may render differently as Lucid evolves. [SI overview](https://developer.lucid.co/docs/overview-si)

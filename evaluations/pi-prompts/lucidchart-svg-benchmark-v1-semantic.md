# Quality gate and laboratory records

Prepare an editable local Lucid Standard Import package for a laboratory review handoff. This is a public development benchmark. Choose formal diagram elements from the supplied roles and preserve the complete meaning, literal text, IDs, bounds and relationships. A screenshot or imported SVG image will not satisfy the request.

Use one finite 1300 by 800 pixel page titled `Laboratory review & records`, with background `#FFFFFF`, no tiling, and fixed object positions. Bounds below are `(x, y, width, height)` in pixels. Use white fill, a solid 2 pixel `#334155` outline and `#0F172A` text in Arial at 14 pixels for every object. Use that same stroke and text style for connectors and their labels. Keep the two diagram regions distinct; their proximity does not create a relationship.

The upper region is BPMN. All events have no trigger subtype. Each listed task is an ordinary task; there is no subprocess or loop.

| ID | Literal label | Established role | Bounds |
| --- | --- | --- | --- |
| intake | Sample received | Start event | 50, 90, 60, 60 |
| review | Review <assay> & sign | User task performed by a reviewer | 200, 80, 180, 80 |
| outcome | Result acceptable? | Exclusive gateway: exactly one outgoing branch is chosen | 480, 90, 100, 100 |
| publish | Publish certificate | Service task performed automatically | 700, 40, 180, 80 |
| repeat | Repeat measurement | Manual task performed without a software task application | 700, 230, 180, 80 |
| closed | Review closed | End event | 1050, 100, 60, 60 |

These are directed sequence flows, with an ordinary arrow at the destination and no source marker. Keep every relationship ID; only the two branch flows have labels.

| ID | From | To | Literal branch label |
| --- | --- | --- | --- |
| arrive-review | intake | review | |
| review-outcome | review | outcome | |
| acceptable | outcome | publish | pass |
| unacceptable | outcome | repeat | rework |
| publish-close | publish | closed | |
| repeat-close | repeat | closed | |

The lower region is an ER view using two editable tables. Each entity has a name header spanning its two columns, followed by the fields in the exact listed order; column one contains the literal field/key text and column two contains its type. There is no SQL import or hidden schema metadata. Use plain, fully opaque objects with no added text decoration or rounded corners.

| ID | Entity header | Bounds | Ordered field/type rows |
| --- | --- | --- | --- |
| batch | Batch <lab> | 120, 500, 300, 180 | `batch_id PK` / `uuid`; `collected_at` / `timestamp`; `lot_code` / `text` |
| measurement | Measurement & result | 720, 500, 320, 180 | `measurement_id PK` / `uuid`; `batch_id FK` / `uuid`; `value` / `decimal` |

The single ER relationship has ID `batch-measurement`. Every Measurement belongs to exactly one Batch, while a Batch can have zero or many Measurements. Attach the relationship to the two entity objects, put the correct cardinality marker at each respective entity, and display literal multiplicity labels `1` near Batch and `0..*` near Measurement. This relationship has no navigation arrow. Do not add a link between a BPMN task and an entity.

Deliver exactly:

- `out/semantic/graph.json`: the explicit editable graph used for preparation.
- `out/semantic/diagram.lucid`: the local Standard Import package.
- `out/semantic/document.json`: the package's document JSON.
- `out/semantic/native-report.json`: the local preparation report.
- `out/semantic/notes.md`: concise factual English explanation of selected notation, preserved meaning, editing capability, adaptations and unverified live/rendered behavior.

Check the package, fixed bounds, labels, formal roles, field order, endpoint cardinalities and all seven relationships locally. The notes will be reviewed directly rather than scored by keywords. Treat `skills/lucidchart-svg/` as read-only and keep generated files outside it in this workspace. Do not consult repository examples or other skills, access the network, authenticate, upload, or create a live document. No authenticated Lucid connection is available; report the actual local deliverable.

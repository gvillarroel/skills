# Delivery organization, topics and sequence

Prepare an editable local Lucid Standard Import package containing an organization chart, a mind map, a UML sequence view and assisted arrangement of the indicated cards. This is a public development benchmark. I explicitly accept Lucid reflow for all four layouts; supplied origins do not constrain their final dimensions. Use one infinite canvas titled `Delivery planning <R2>` with background `#F1F5F9`.

Preserve the entire two distinct inline datasets below, including field names, JSON scalar types, literal text, row order and parent links. Keep them separate. The collection IDs are `staff-roster` and `delivery-topics`.

```json
{
  "staff-roster":[
    {"person_id":"o-north","reports_to":"","display_name":"Nora & operations","job_title":"North director","office":"North","fte":1.0},
    {"person_id":"o-triage","reports_to":"o-north","display_name":"Mina <triage>","job_title":"Coordinator","office":"North","fte":0.8},
    {"person_id":"o-courier","reports_to":"o-triage","display_name":"Jules","job_title":"Courier","office":"North","fte":0.6},
    {"person_id":"o-south","reports_to":null,"display_name":"Theo","job_title":"South director","office":"South","fte":1.0},
    {"person_id":"o-route","reports_to":"o-south","display_name":"Rae","job_title":"Route planner","office":"South","fte":0.9},
    {"person_id":"o-store","reports_to":"o-south","display_name":"Emery","job_title":"Stores lead","office":"South","fte":1.0}
  ],
  "delivery-topics":[
    {"topic_id":"m-delivery","parent_topic":null,"caption":"Delivery <R2>","priority":1},
    {"topic_id":"m-intake","parent_topic":"m-delivery","caption":"Intake & evidence","priority":2},
    {"topic_id":"m-proof","parent_topic":"m-intake","caption":"Proof of custody","priority":3},
    {"topic_id":"m-pack","parent_topic":"m-intake","caption":"Packing","priority":3},
    {"topic_id":"m-dispatch","parent_topic":"m-delivery","caption":"Dispatch","priority":2},
    {"topic_id":"m-route","parent_topic":"m-dispatch","caption":"Route checks","priority":3},
    {"topic_id":"m-confirm","parent_topic":"m-dispatch","caption":"Arrival confirmed","priority":3}
  ]
}
```

Use layout ID `org-panel` for the organization chart, origin `(40, 100)`: identities are `person_id`, managers are `reports_to`, names are `display_name`, and roles are `job_title`. Preserve `office` and `fte` as extra fields. The two roots are deliberate; neither director reports to the other.

Use layout ID `topics-panel` for the mind map, origin `(40, 900)`: identities are `topic_id`, parents are `parent_topic`, and visible text is `caption`. This dataset has one root and is independent of the organization dataset.

Use layout ID `sequence-panel` for the UML sequence view, origin `(1100, 100)`. Preserve this literal markup with LF line breaks and no additional leading or trailing whitespace:

```text
@startuml
participant Analyst
participant Registry
participant Queue
Analyst -> Registry : submit <lot>
Registry -> Queue : enqueue & audit
alt accepted
Queue --> Registry : receipt
Registry --> Analyst : confirmed
else declined
Queue --> Registry : reason
Registry --> Analyst : revise
end
@enduml
```

Also create three generic editable rectangular cards at these initial bounds `(x, y, width, height)`. Their fill is `#FFFFFF`, outline is solid `#475569` at 1 pixel, and literal labels use Arial at 14 pixels in `#0F172A`.

| ID | Literal label | Initial bounds |
| --- | --- | --- |
| inspect-card | Inspect <lot> | 1100, 650, 180, 70 |
| release-card | Release & record | 1420, 650, 180, 70 |
| archive-card | Reference archive | 1800, 650, 180, 70 |

Connect `inspect-card` to `release-card` with relationship ID `eligible-link`, a destination arrow, no source marker, a solid `#475569` 1 pixel line and the literal label `eligible`. Use assisted layout ID `cards-reflow` to rearrange only `inspect-card` and `release-card`; the archive card is excluded. No relationship involves the archive card. The three other generated views and their collections are outside this assisted selection. Keep the cards plain and fully opaque with no rounded corners or text decoration.

Deliver exactly:

- `out/generated/layout.json`: the explicit preparation input preserving these records, markup, origins, graph and selections.
- `out/generated/diagram.lucid`: the local Standard Import package.
- `out/generated/document.json`: the package's document JSON.
- `out/generated/layout-report.json`: the local preparation report.
- `out/generated/notes.md`: concise factual English account of data/markup preservation, intended reflow, who computes geometry, editing tradeoffs and unverified live/rendered behavior.

Check the actual package, the two separate hierarchies, all four layouts and the assisted selection locally. The notes will be reviewed directly rather than scored by keywords. Treat `skills/lucidchart-svg/` as read-only and keep all generated files in this workspace outside the bundle. Do not discover repository examples or other skills, access the network, authenticate, upload, or create a live document. No authenticated Lucid connection is available. Do not claim final geometry or live parser/render acceptance from local packaging.

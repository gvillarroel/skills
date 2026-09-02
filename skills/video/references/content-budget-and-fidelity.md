# Content Budget and Fidelity

Use this reference for diagram-like scenes, source-dense visual explanations, or any adaptation that may merge, omit, or move source content. Preserve exact scene count and required source anchors from the prompt; this contract governs what appears inside each scene, not whether supplied scenes may disappear.

## Contents

- Choose meaning before geometry
- Set a scene budget and explicit count basis
- Reduce in a stable order
- Account for every source item once
- Separate audience from detail
- Apply the review gate

## Choose meaning before geometry

Before selecting an armature, write the scene's one viewer question and identify the relationship that carries the answer: order, interaction, state, hierarchy, quantity, capacity, boundary, comparison, or causality. Choose one primary behavioral contract for a diagram-like scene, then choose the layout family. A secondary contract may contribute one cue; if two contracts both need full treatment, use separate supplied scenes or an overview/detail route only when the source contract permits it.

Do not let color, motion, or narration carry a state that the settled frame omits. Capacity needs a count or threshold. A policy trace needs literal statuses and outcomes. A trust route needs a named boundary and a blocked path that visibly stops. Residual risk needs a visible handoff between layers.

## Set a scene budget

Use one of three modes:

| Mode | Use | Max nodes | Max relations | Max annotations | Max total visible items | Max focal elements |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `editorial-overview` | One projected or quickly scanned explanation | 9 | 12 | 4 | 12 | 2 |
| `faithful-zoned` | The prompt explicitly requires more source detail | 24 | 32 | 8 | 32 | 2 |
| `non-diagram` | Footage, product UI, portrait, title card, or another scene without diagram nodes | 0 | 0 | 12 | 12 | 2 |

These are editorial limits, not renderer limits. A truthful data chart, real UI capture, or supplied artifact may have more internal marks than the node count. Count semantic diagram entities and explicit relations, not pixels, table cells, or decorative marks.

Record this object in each gated JSON scene:

```json
{
  "contentBudget": {
    "mode": "editorial-overview",
    "nodeItems": ["Web", "Mobile", "Gateway", "Queue", "Workers x2", "Approved", "Deferred"],
    "edgeItems": [
      {"from": "Web", "to": "Gateway"},
      {"from": "Mobile", "to": "Gateway"},
      {"from": "Gateway", "to": "Queue"},
      {"from": "Queue", "to": "Workers x2"},
      {"from": "Workers x2", "to": "Approved"},
      {"from": "Queue", "to": "Deferred", "label": "overflow"}
    ],
    "focalItems": ["Queue"],
    "annotationItems": [
      {"item": "capacity 2", "attachedTo": "Queue", "kind": "constraint"},
      {"item": "1 item per hour", "attachedTo": "Workers x2", "kind": "quantity"}
    ],
    "plannedNodeCount": 7,
    "plannedEdgeCount": 6,
    "focalElementCount": 1,
    "overflowStrategy": "Merge replicated workers; move audit internals to scene-03."
  }
}
```

The count fields are derived claims, not estimates:

- `plannedNodeCount` equals the number of unique strings in `nodeItems`.
- `plannedEdgeCount` equals the number of structured `edgeItems`; every `from` and `to` names a `nodeItems` entry.
- `focalElementCount` equals the number of unique `focalItems`; every focal item names a visible node or annotation.
- `annotationItems` accounts only for visible kept constraints, facts, quantities, states, or units that label a carrier rather than becoming entities. Set `kind` to `constraint`, `fact`, `quantity`, `state`, or `unit`. Actors, services, systems, artifacts, and outcomes belong in `nodeItems`. The validator rejects common entity-noun endings and enforces the declared kind, carrier, and caps, but it cannot prove every natural-language classification; manually challenge ambiguous `fact` entries during review. In diagram modes, `attachedTo` names a `nodeItems` entry. In `non-diagram` mode, use a concrete carrier such as the source UI panel, footage region, or caption band.
- Every kept source item and every visible `merged.into` output appears exactly once in `nodeItems` or `annotationItems`. Never hide retained entities in annotations merely to satisfy the node cap.
- The validator caps both `annotationItems` and the combined `nodeItems` plus `annotationItems` total. Counts therefore cannot hide an unbounded visible list outside the node budget, while the lexical guard and manual semantic review prevent the bounded annotation allowance from becoming an entity escape hatch.

For `faithful-zoned`, name the zones or the overview/detail mechanism in `overflowStrategy`. For `non-diagram`, keep `nodeItems` and `edgeItems` empty and account for visible supplied content through typed `annotationItems`. A true transition with no enumerated source content may use empty `sourceItems`, disposition lists, and annotation lists. Never solve overflow by shrinking labels below the delivery context's legibility threshold.

## Reduce in a stable order

When simplification is authorized, reduce in this order:

1. Remove decorative chrome and repeated legends.
2. Merge exact replicas into one labeled cohort.
3. Collapse leaf-only groups into a named parent when the parent retains the reader's question.
4. Move secondary instrumentation or cross-cutting detail to a named later scene or detail view.
5. Omit a semantic item only when it does not change the promised claim and the prompt permits omission.
6. Split or zoom before compressing an unreadable scene.

Do not use this ladder to evade required anchors, exact facts, scene IDs, or validator literals. Keep every required item in at least one relevant scene. An overview may classify it as moved to detail only when the named target scene keeps the same literal item.

## Account for every source item once

Create a stable list of semantic source items before composing. Use literal prompt wording where practical. Then partition the list exactly once:

```json
{
  "contentAccounting": {
    "sourceItems": [
      "Web client",
      "Mobile client",
      "Gateway",
      "Worker A",
      "Worker B",
      "Audit stream"
    ],
    "kept": ["Web client", "Mobile client", "Gateway"],
    "merged": [
      {
        "sourceItems": ["Worker A", "Worker B"],
        "into": "Workers x2",
        "reason": "The replicas have the same role and route."
      }
    ],
    "omitted": [],
    "movedToDetail": [
      {
        "item": "Audit stream",
        "target": {"kind": "scene", "id": "scene-03"},
        "reason": "Operations detail would compete with the request path in the overview."
      }
    ]
  }
}
```

Rules:

- Keep `sourceItems` unique and non-empty, except for a true `non-diagram` scene with no enumerated source content.
- Scope each ledger to the facts supplied for that scene. Do not copy unrelated items from other scenes into `sourceItems`. Repeat an item across two ledgers only when it is explicitly moved from the source scene and then kept by the named target scene.
- Put every source item in exactly one disposition.
- Merge at least two source items and name the resulting visible group.
- Give every merge, omission, and move a concrete reason.
- Give every moved item a structured target with `kind` equal to `scene`, `detail-view`, or `artifact`, plus a non-empty `id`. A scene target must be later in plan order, match an exact scene ID, and keep the same literal item. Declare every external target in root `contentTargets`: a detail view names an existing `ownerScene`; an artifact names an exact `path`; both enumerate exactly the literal source items delivered to them in `receives`—no missing or speculative entries.
- Never list a new item in a disposition that is absent from `sourceItems`.
- Preserve required source anchors as kept in their final visible scene. A source overview may move an anchor to a named detail scene only when that target keeps the same item. If an anchor is a fact rather than a visual entity, keep it in the relevant `scene.sourceAnchors` and attach it to the visible object or narration cue that carries it.
- Treat `videoDirection.sourceAnchors` as the global literal checklist and each `scene.sourceAnchors` as a local visibility claim. Every CLI-required anchor belongs in the global list; every local anchor belongs in the global list; every global anchor appears in at least one local list and is kept there. A moved anchor belongs in the source scene's `sourceItems` and `movedToDetail`, then in the target scene's `sourceAnchors` and `kept`; do not also claim that it is a visible anchor in the source scene.
- Use `movedToDetail` only for a real move to a target that keeps the same literal item. Do not use it to point backward to the scene where an unrelated item already appears; leave unrelated items out of the local ledger.
- Keep every omitted or moved literal out of visible-bearing scene fields, including functional, editorial, and on-screen text policies. Match the complete Unicode literal after case and whitespace normalization; do not infer a match from one generic token. Discuss the move only in source accounting, overflow rationale, rejected alternatives, risks, or other non-visible planning rationale.

Use the same accounting in Markdown with short `Kept`, `Merged`, `Omitted`, and `Moved to detail` lists.

## Separate audience from detail

Audience changes vocabulary and emphasis, not the number of source items. An engineering scene may retain protocols and ports; a mixed-audience scene may use plain verbs; an executive scene may name capabilities and outcomes. Do not silently remove nodes when changing audience, invent a business label, or substitute one product for another.

Delivery context changes type scale, safe areas, and aspect pressure. If slide or mobile framing makes the current detail illegible, lower the authorized detail level, move content to a named detail scene, or change the camera route. Do not preserve count by making the diagram unreadable.

## Review gate

Before accepting a gated scene:

- the viewer question and primary semantic contract are explicit;
- planned nodes, relations, and focal elements fit the selected mode;
- every enumerated source item is accounted for exactly once;
- required anchors remain kept and visible in at least one relevant scene or attached to a declared narration cue;
- the scene has one dominant reading path and no competing focal cluster;
- states, counts, boundaries, outcomes, and uncertainty survive in a settled frame;
- any moved item names an exact scene or a declared external target that lists the item in `receives`;
- simplification changes neither facts nor audience-independent topology without authorization.

Validate the JSON plan with `--require-content-accounting`.

## Source

This contract distills transferable editorial budgeting, behavior-before-layout, and fidelity-ledger ideas from [Cathryn Lavery's Diagram Design repository](https://github.com/cathrynlavery/diagram-design) at commit `f3622cf66a3c557cb2ead57b687a3c1ff63f5a2b` (MIT), adapted to scene-based planning and this skill's existing source-preservation rules.

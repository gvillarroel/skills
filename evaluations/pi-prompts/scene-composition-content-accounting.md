Use the provided scene-composition-director skill to create a renderer-neutral JSON composition plan for two diagram-led scenes.

Create exactly:

- `projects/review-queue-composition/composition-plan.json`

Preserve these exact scene IDs and facts:

1. `scene-01-overview`: Web and Mobile enter through Gateway, then a queue with `capacity 2`; Reviewer A and Reviewer B are identical replicas with combined service rate `1 item per hour`; terminal outcomes are Approved and Deferred; Audit stream is real but belongs in the detail scene.
2. `scene-02-audit-detail`: Audit stream contains Event schema, Retention policy, Alert route, and Archive.

Requirements:

- Keep the plan renderer-neutral and preserve the literal anchors `Gateway`, `Audit stream`, `capacity 2`, and `1 item per hour`.
- Put all four literal validator anchors in `videoDirection.sourceAnchors`. In each scene's own `sourceAnchors`, include only the literal anchors kept and visible in that scene: scene 1 has `Gateway`, `capacity 2`, and `1 item per hour`; scene 2 has `Audit stream`.
- Add root `contentTargets` as an empty array because the only move targets an existing scene.
- Use an editorial overview budget for scene 1 and a truthful bounded budget for scene 2.
- Set `focalElementCount` to no more than 2 in each scene.
- Give both scenes a complete `contentBudget` and exhaustive `contentAccounting` ledger.
- Use these exact scene-1 `sourceItems`: `Web`, `Mobile`, `Gateway`, `queue`, `capacity 2`, `Reviewer A`, `Reviewer B`, `1 item per hour`, `Approved`, `Deferred`, and `Audit stream`. Keep all except the two reviewers and Audit stream; merge the reviewers; move Audit stream.
- Use these exact scene-2 `sourceItems`: `Audit stream`, `Event schema`, `Retention policy`, `Alert route`, and `Archive`. Keep all five; use empty arrays for its `merged`, `omitted`, and `movedToDetail` fields. Do not copy scene-1 items into the scene-2 ledger.
- In scene 1, use exact `nodeItems` `Web`, `Mobile`, `Gateway`, `queue`, `Reviewer cohort`, `Approved`, and `Deferred`; exact edges `Web -> Gateway`, `Mobile -> Gateway`, `Gateway -> queue`, `queue -> Reviewer cohort`, `Reviewer cohort -> Approved`, and `queue -> Deferred`; `focalItems` containing only `queue`; and `annotationItems` for `capacity 2` attached to `queue` with kind `constraint` and `1 item per hour` attached to `Reviewer cohort` with kind `quantity`. Name `Reviewer cohort` as the exact `merged.into` output. Therefore set counts to 7 nodes, 6 edges, and 1 focal element.
- In scene 2, use all five source items as `nodeItems`; four edges from `Audit stream` to each detail node; `focalItems` containing only `Audit stream`; and empty `annotationItems`. Therefore set counts to 5 nodes, 4 edges, and 1 focal element.
- In scene 1, merge the two reviewer replicas into one visible cohort and move Audit stream with the exact structured target `{"kind":"scene","id":"scene-02-audit-detail"}`.
- Do not mention Audit or audit in scene 1's focal, roles, armature, anchors, object bounds, layout, hierarchy, camera path, depth layers, motion phases, or caption plan. It may appear only in source accounting, overflow rationale, rejected alternatives, risks, or other non-visible planning rationale for that scene.
- In scene 2, keep Audit stream and all four supplied audit-detail items. Treat `Audit stream` as a kept scene anchor in scene 2; do not classify it as a kept scene-1 item when its scene-1 disposition is moved to detail.
- `Reviewer A`, `Reviewer B`, and the four audit-detail items are ledger source items, not additional required `sourceAnchors`.
- Every `sourceItems` entry must have exactly one disposition. Do not add source items or omit required anchors.
- Do not write disallowed runtime-library names anywhere in the JSON, including in a negative list. A visual negative list is optional for this task.
- Include normal scene fields, at least three depth layers, meaningful motion phases, and at least two structured validation checks per scene.
- Any validation check that states a number must match the structured lists. Scene 1 has exactly 11 `sourceItems`, 7 nodes, 6 edges, and 1 focal item; scene 2 has exactly 5 `sourceItems`, 5 nodes, 4 edges, and 1 focal item.
- Read only `skills/scene-composition-director/SKILL.md`, `references/content-budget-and-fidelity.md`, and `references/composition-brief-contract.md` unless one of them explicitly routes you elsewhere. Do not read the output path before creating it and do not inspect validator source. Write the complete plan once as strict JSON with double-quoted keys and values and no trailing commas; check every object and array delimiter before saving. Then run the exact validation command below once; the first validator call must pass, so do not shorten or reconstruct it.
- Validate the result with:

```bash
uv run --script skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan projects/review-queue-composition/composition-plan.json --expect-scenes 2 --require-anchor "Gateway" --require-anchor "Audit stream" --require-anchor "capacity 2" --require-anchor "1 item per hour" --require-content-accounting
```

- Keep every generated artifact outside the copied skill directory.

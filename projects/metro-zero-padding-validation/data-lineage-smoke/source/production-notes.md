# Production Notes

## Source Facts

- Lineage boxes use grayscale level fills.
- Inactive boxes do not use internal padded decoration.

## Visual Metaphor Decision

- Visual pattern: data-lineage.
- Concept claim: a good Lineage boxes without internal decoration explainer should show source provenance, transform ownership, quality gates, drift monitoring, consumer readiness, and rollback separately.
- Mechanic: data moves from source through lineage nodes while transform rules, quality checks, drift monitoring, consumer contract, and rollback route appear as distinct mechanisms.
- Candidate metaphors: data-lineage map, systems flow, and dependency map.
- Rejected alternative: a systems-flow map would show work movement but hide provenance, derived-data trust checks, and downstream consumer contracts.
- Chosen metaphor: data-lineage map with source-to-consumer path, transform rule, quality gate, drift monitor, consumer contract, and rollback route.
- Visual vocabulary: brand red means source lineage; dark gray means trusted transform; dark red means transform rule; status red means drift or rollback risk; mid gray means consumer readiness; black marks moving data packets.
- Narration split: exact datasets, owners, freshness targets, schema versions, and drift thresholds should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- zero internal padding
- gray lineage levels

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-zero-padding-validation/data-lineage-smoke --title "Data Lineage Zero Padding" --output-id data-lineage-zero-padding --pattern data-lineage
```

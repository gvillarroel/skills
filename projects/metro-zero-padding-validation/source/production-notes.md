# Production Notes

## Source Facts

- Boxes must have zero internal padding.
- Hierarchy levels must use different gray values.

## Visual Metaphor Decision

- Visual pattern: layered-architecture.
- Concept claim: a good Metro box hierarchy explainer should show layer ownership, request movement, cross-cutting policy, failure routing, observability, and rollout separately.
- Mechanic: a request descends through owned layers while cross-cutting policy, failure, observability, and rollout mechanisms appear outside the happy path.
- Candidate metaphors: layered architecture stack, systems flow, and dependency map.
- Rejected alternative: a systems-flow map would show work movement but blur stable layer boundaries and cross-cutting concerns.
- Chosen metaphor: layered-architecture stack with request path, layer activation, policy band, failure route, observability panel, and rollout gate.
- Visual vocabulary: brand red means request path; dark gray means active layers; dark red means cross-cutting policy; status red means failure route; mid gray means observability and rollout readiness.
- Narration split: exact owners, protocols, SLOs, and deployment policy should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- zero internal padding
- grayscale hierarchy levels

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-zero-padding-validation --title "Zero Padding Gray Levels" --output-id zero-padding-gray-levels --pattern layered-architecture
```

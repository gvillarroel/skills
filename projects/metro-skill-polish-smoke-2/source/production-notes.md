# Production Notes

## Source Facts

- Square borders are required.
- Panels should align to a visible grid.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good alignment and square borders explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system.
- Mechanic: a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers.
- Candidate metaphors: pipeline map, state machine, and incident timeline.
- Rejected alternative: a plain timeline would show order but hide pressure, branching, and capacity constraints.
- Chosen metaphor: systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle.
- Visual vocabulary: brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity.
- Narration split: implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts.

## Strategy Anchors

- straight panel borders
- shared baselines

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-skill-polish-smoke-2 --title "Metro Square Composition Smoke" --output-id metro-square-smoke --pattern systems-flow
```

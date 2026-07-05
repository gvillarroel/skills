# Production Notes

## Source Facts

- The design must be a navigable modular megacanvas, not a title-and-cards slide.
- Colorset1 is sufficient for the validation draft.
- Square edges and zero internal padding are required for every box-like module.
- Grayscale levels must carry hierarchy across visible surfaces.
- Render-state validation must prove the late queue, retry, dead-letter, and feedback mechanisms.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good strict Metro design adherence for video-generation skill validation explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system.
- Mechanic: a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers.
- Candidate metaphors: pipeline map, state machine, and incident timeline.
- Rejected alternative: a plain timeline would show order but hide pressure, branching, and capacity constraints.
- Chosen metaphor: systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle.
- Visual vocabulary: brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity.
- Narration split: implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts.

## Strategy Anchors

- modular megacanvas
- queue fill
- worker activation
- retry branch
- dead-letter branch
- feedback throttle
- gray hierarchy levels
- square-edge modules

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-contract-video --title "Metro Design Contract Validation" --output-id metro-design-contract --pattern systems-flow
```

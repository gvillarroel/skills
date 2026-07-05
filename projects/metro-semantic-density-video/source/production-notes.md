# Production Notes

## Source Facts

- The video must show a navigable modular megacanvas rather than labeled slides.
- Camera movement must be visible through render-state diversity.
- Camera movement must show meaningful travel and zoom depth, not tiny decorative nudges.
- Queue fill, retry, dead-letter, and feedback throttle must all appear as late mechanisms.
- Contact-sheet frames must change enough to prove visual progression.
- Hiding all SVG text must still leave enough visible mark motion, zones, gray hierarchy, and nonbackground area for the mute test to pass.
- The semantic-density audit must show a continuity path through zones, not only distinct state-summary values.
- The semantic-density audit must prove every visual anchor is bound through source package, rendered DOM, and render-state evidence.
- The semantic-density audit must pass after the wrapper, state check, contact sheet, Metro audit suite, mute-test audit, and encoded-MP4 composition audit.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good semantic-density proof for Metro video-generation skill validation explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system.
- Mechanic: a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers.
- Candidate metaphors: pipeline map, state machine, and incident timeline.
- Rejected alternative: a plain timeline would show order but hide pressure, branching, and capacity constraints.
- Chosen metaphor: systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle.
- Visual vocabulary: brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity.
- Narration split: implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts.

## Strategy Anchors

- modular megacanvas
- semantic density
- queue fill
- retry branch
- dead-letter branch
- feedback throttle
- camera exploration
- contact-sheet progression

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-semantic-density-video --title "Metro Semantic Density Validation" --output-id metro-semantic-density --pattern systems-flow
```

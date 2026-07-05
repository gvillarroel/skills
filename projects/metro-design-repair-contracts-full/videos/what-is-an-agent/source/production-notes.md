# Production Notes

## Source Facts

- An agent is not just “an LLM with tools.” In current official platform guidance, an agentic system combines a model with tools, state or memory, and orchestration.
- For teaching, the cleanest minimal decomposition is: **context** the agent sees, **environment** it can observe or affect, **actions** it can take, and a **loop or policy** that decides what to do next.
- The crucial distinction is between a short, explicit workflow and an agent that can iteratively plan, act, read results, and continue.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is an Agent explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system.
- Mechanic: a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers.
- Candidate metaphors: pipeline map, state machine, and incident timeline.
- Rejected alternative: a plain timeline would show order but hide pressure, branching, and capacity constraints.
- Chosen metaphor: systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle.
- Visual vocabulary: brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity.
- Narration split: implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts.

## Strategy Anchors

- agent_loop_ring
- context_window_box
- Model + Tools + State + Loop
- agent_loop_ring as the visual identity for every agent-related module
- Represent context as stacked translucent panes rather than text walls
- Animate environment changes: repo
- Use one "fixed workflow" lane and one "adaptive agent" lane for contrast
- Add approval checkpoint icon near the end to foreshadow guardrails and permissions
- the final **Model + Tools + State + Loop** badge in harness and MCP videos
- flow-tokens
- swimlane-handoff
- layered-architecture
- masonry-wall
- risk-bowtie
- critical-bowtie-barrier
- masonry wall
- megacanvas zones
- camera reframe

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-an-agent --title "What is an Agent" --output-id what-is-an-agent --pattern systems-flow
```

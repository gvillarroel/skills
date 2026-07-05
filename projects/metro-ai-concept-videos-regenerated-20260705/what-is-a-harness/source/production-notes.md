# Production Notes

## Source Facts

- A harness is the runtime wrapper that turns a raw model into a usable assistant or agent.
- A harness defines instruction layers, default tools, permissions, model picker, execution loop, approvals, memory behavior, logging, and extensibility surface.
- The model is like the engine; the harness provides steering, brakes, dashboard, and controls.
- Different harnesses feel different even when they can call the same model.
- GitHub Copilot emphasizes GitHub-native workflows and explicit AI-credit accounting.
- Claude Code emphasizes skills, hooks, MCP, and coding autonomy.
- OpenCode emphasizes openness and provider choice.
- Harness defaults affect quality, latency, cost, and risk because they change tools, context, retries, and autonomous loops.

## Visual Metaphor Decision

- Visual pattern: layered-architecture.
- Concept claim: a good What is a Harness explainer should show layer ownership, request movement, cross-cutting policy, failure routing, observability, and rollout separately.
- Mechanic: a request descends through owned layers while cross-cutting policy, failure, observability, and rollout mechanisms appear outside the happy path.
- Candidate metaphors: layered architecture stack, systems flow, and dependency map.
- Rejected alternative: a systems-flow map would show work movement but blur stable layer boundaries and cross-cutting concerns.
- Chosen metaphor: layered-architecture stack with request path, layer activation, policy band, failure route, observability panel, and rollout gate.
- Visual vocabulary: brand red means request path; dark gray means active layers; dark red means cross-cutting policy; status red means failure route; mid gray means observability and rollout readiness.
- Narration split: exact owners, protocols, SLOs, and deployment policy should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- comparison grid
- runtime stack
- model engine
- steering controls
- instruction layers
- default tools
- permission gate
- approval control
- logging surface
- cost meter
- use-case matrix

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-a-harness --title "What is a Harness" --output-id what-is-a-harness --pattern layered-architecture
```

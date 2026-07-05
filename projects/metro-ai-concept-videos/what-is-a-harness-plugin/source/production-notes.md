# Production Notes

## Source Facts

- A harness plugin is a distribution mechanism for reusable harness customization.
- The exact packaging differs by product, but the common pattern is to bundle runtime capabilities for install, sharing, versioning, and governance.
- GitHub Copilot CLI plugins can bundle agents, skills, hooks, and MCP configuration.
- Claude Code plugins can bundle skills, agents, hooks, and MCP servers from marketplaces.
- OpenCode plugins are JavaScript or TypeScript modules loaded locally or from npm to add hooks, tools, and integrations.
- Plugins package multiple runtime behaviors into one installable unit.
- Distribution is governance: plugins standardize the approved way to work across a team.
- Plugins can lower cost with efficient defaults or raise cost by injecting noisy context and expensive tool calls everywhere.

## Visual Metaphor Decision

- Visual pattern: layered-architecture.
- Concept claim: a good What is a Harness Plugin explainer should show layer ownership, request movement, cross-cutting policy, failure routing, observability, and rollout separately.
- Mechanic: a request descends through owned layers while cross-cutting policy, failure, observability, and rollout mechanisms appear outside the happy path.
- Candidate metaphors: layered architecture stack, systems flow, and dependency map.
- Rejected alternative: a systems-flow map would show work movement but blur stable layer boundaries and cross-cutting concerns.
- Chosen metaphor: layered-architecture stack with request path, layer activation, policy band, failure route, observability panel, and rollout gate.
- Visual vocabulary: brand red means request path; dark gray means active layers; dark red means cross-cutting policy; status red means failure route; mid gray means observability and rollout readiness.
- Narration split: exact owners, protocols, SLOs, and deployment policy should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- plugin bundle cube
- detachable module blocks
- GitHub plugin manifest card
- Claude marketplace allowlist gate
- OpenCode npm module
- versioning and upgrade arrows
- good plugin versus noisy plugin split
- team-wide install lane

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-a-harness-plugin --title "What is a Harness Plugin" --output-id what-is-a-harness-plugin --pattern layered-architecture
```

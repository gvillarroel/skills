# Production Notes

## Source Facts

- MCP stands for Model Context Protocol.
- MCP is an open standard for connecting AI clients to external systems such as tools, resources, and prompts.
- MCP gives clients and servers a shared protocol instead of requiring one custom integration per assistant.
- An MCP server can expose tools, resources, and prompts.
- MCP is supported across major clients including Claude, ChatGPT-related ecosystems, VS Code, and GitHub Copilot.
- Authentication and authorization matter because MCP can expose real systems.
- Registries, allowlists, and approval policies help govern MCP access.
- MCP can affect cost because tool discovery, tool descriptions, tool calls, and downstream APIs add context or external spend.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is an MCP explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system.
- Mechanic: a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers.
- Candidate metaphors: pipeline map, state machine, and incident timeline.
- Rejected alternative: a plain timeline would show order but hide pressure, branching, and capacity constraints.
- Chosen metaphor: systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle.
- Visual vocabulary: brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity.
- Narration split: implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts.

## Strategy Anchors

- MCP bus
- messy point-to-point integrations becoming one protocol bus
- tools resources prompts lanes
- neutral client cards
- lock icons on bus
- registry gate
- approval shield
- context meter and external billing icons

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-an-mcp --title "What is an MCP" --output-id what-is-an-mcp --pattern systems-flow
```

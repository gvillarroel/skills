# Production Notes

## Source Facts

- An agentic system combines a model with tools, state or memory, and orchestration.
- An agent does more than answer once: it can observe context, take actions, inspect results, and continue in a loop.
- A minimal teaching decomposition is context, environment, actions, and a loop or policy.
- Context can include chat history, files, instructions, memory, and tool outputs.
- Environment is the system the agent can inspect or affect, such as a repo, terminal, browser, ticket system, docs, or database.
- Actions can include reading files, running tests, searching docs, calling APIs, or asking for approval.
- The loop or policy decides whether to keep exploring, execute a tool, or stop.
- A workflow follows predefined steps, while an agent adapts based on what it finds.

## Visual Metaphor Decision

- Visual pattern: state-machine.
- Concept claim: a good What is an Agent explainer should show states, transition guards, rollback, compensation, and terminal outcomes as separate mechanisms.
- Mechanic: one work item advances through state cards while guard panels validate transitions and an explicit recovery lane handles rollback and compensation.
- Candidate metaphors: state-machine diagram, sequence diagram, and checklist timeline.
- Rejected alternative: a checklist timeline would show progress but hide invalid transitions, recovery routes, and terminal-state separation.
- Chosen metaphor: state-machine map with guarded transitions, success path, recovery lane, and terminal-state panel.
- Visual vocabulary: brand red means lifecycle progress; dark red means transition guards; dark gray means successful execution; status red means rollback or compensation; mid gray means terminal states.
- Narration split: implementation-specific state names and exact retry limits are omitted unless supplied as source facts.

## Strategy Anchors

- agent loop ring
- Observe / Act / Check / Continue loop
- four labeled component cards
- stacked context panes
- environment blocks for repo, terminal, browser, tickets, docs, and database
- tool icons around the loop
- policy decision fork
- fixed workflow lane
- adaptive agent lane
- final Model + Tools + State + Loop badge

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-an-agent --title "What is an Agent" --output-id what-is-an-agent --pattern state-machine
```

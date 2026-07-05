# Production Notes

## Source Facts

- A harness hook is an active interception point in the runtime lifecycle.
- Hooks run custom logic when an important runtime event occurs.
- Hooks are active guardrails because they run during execution, not only before a session begins.
- GitHub Copilot hooks can execute external commands at lifecycle points like session start, prompt submit, tool calls, and agent stop.
- Claude Code hooks can be shell commands, HTTP endpoints, or LLM prompts.
- OpenCode exposes comparable event-driven control through plugin events.
- Typical hook jobs include formatting, validation, secret protection, audit logging, notifications, and narrowing huge data before the model sees it.
- Hooks can lower cost by preprocessing and shrinking context, but they can raise latency or cost if they trigger slow services too often.

## Visual Metaphor Decision

- Visual pattern: state-machine.
- Concept claim: a good What is a Harness Hook explainer should show states, transition guards, rollback, compensation, and terminal outcomes as separate mechanisms.
- Mechanic: one work item advances through state cards while guard panels validate transitions and an explicit recovery lane handles rollback and compensation.
- Candidate metaphors: state-machine diagram, sequence diagram, and checklist timeline.
- Rejected alternative: a checklist timeline would show progress but hide invalid transitions, recovery routes, and terminal-state separation.
- Chosen metaphor: state-machine map with guarded transitions, success path, recovery lane, and terminal-state panel.
- Visual vocabulary: brand red means lifecycle progress; dark red means transition guards; dark gray means successful execution; status red means rollback or compensation; mid gray means terminal states.
- Narration split: implementation-specific state names and exact retry limits are omitted unless supplied as source facts.

## Strategy Anchors

- event timeline
- lifecycle pulse
- shield gate overlay
- pre-tool checkpoint
- post-tool checkpoint
- permission request
- session start
- agent stop
- command block
- context shrinking counter
- cost versus latency slider

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-a-harness-hook --title "What is a Harness Hook" --output-id what-is-a-harness-hook --pattern state-machine
```

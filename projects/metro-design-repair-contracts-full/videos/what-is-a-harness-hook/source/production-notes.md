# Production Notes

## Source Facts

- A harness hook is an active interception point in the runtime lifecycle.
- Hooks are where policy becomes executable: before or after tool use, at session start or stop, on permission requests, during compaction, or when notifications fire.
- GitHub Copilot and Claude Code both expose first-class hook systems, while OpenCode exposes comparable event-driven interception through plugin events.
- Good hooks can reduce cost by preprocessing data and avoiding bad runs; poor hooks can increase latency or produce unnecessary extra work.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is a Harness Hook explainer should show hooks as lifecycle interception points where runtime events become enforceable policy, preprocessing, and cost tradeoffs.
- Mechanic: a lifecycle event pulse moves through timeline nodes, a shield gate overlays execution, provider event surfaces expose comparable hook systems, one Bash path is blocked while another log path is filtered, and savings versus latency meters settle into a lifecycle-control boundary.
- Candidate metaphors: hook lifecycle megacanvas, generic systems-flow pipeline, and provider feature comparison table.
- Rejected alternative: a generic systems-flow pipeline would show work movement but hide the hook-specific timing: session, prompt, tool, permission, compaction, notification, stop, blocking, filtering, and cost/latency boundaries.
- Chosen metaphor: hook lifecycle megacanvas with event_timeline, shield_gate overlay, GitHub hook badges, Claude event cloud, OpenCode event list, PreToolUse command block, log-filter path, hook-job cascade, token-savings counter, speed-vs-cost slider, and lifecycle-controls stamp.
- Visual vocabulary: brand red marks active event and safe preprocessing flow; status red marks blocked dangerous command and latency risk; dark red marks executable policy and filter gates; gray levels separate timeline, policy, provider surfaces, preprocessing jobs, and cost boundary. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates all Hook roles.
- Narration split: vendor event names, code details, and exact hook job labels stay in narration or source facts; the frame carries lifecycle interception and cost mechanics without explanatory text.

## Strategy Anchors

- bash # Pseudocode hook: block dangerous commands before tool use event = read_json() if event.type == "PreToolUse" and event.tool == "Bash": if matches(event.command, ["rm -rf", "kubectl delete", "terraform destroy"]): deny("Blocked by repository hook policy") else: allow()
- That pattern is directly aligned with GitHub and Claude hook use cases: validation, audit, and execution control around tool calls. citeturn10view1turn10view0turn9view3 #### Timed narration and visuals | Time | Spoken narration | On-screen text and visual cues | |---|---|---| | 0:00-0:15 | "A harness hook is an event-driven interception point. Something important happens in the runtime, and your custom logic gets a chance to react." |
- lights up event nodes | | 0:15-0:30 | "Hooks are active guardrails because they run during execution, not just before a session begins." | Timeline overlays the
- | | 0:30-0:45 | "GitHub Copilot hooks execute external commands at lifecycle points like session start, prompt submit, tool calls, and agent stop." | GitHub hook events appear as badges | | 0:45-1:00 | "Claude Code hooks go even wider. They can be shell commands, HTTP endpoints, or LLM prompts, and they cover session, turn, tool, compaction, and more." | Claude event cloud expands around the loop | | 1:00-1:15 | "OpenCode expresses similar control through plugin events such as tool execute before and after, shell environment injection, and session idle." | OpenCode event list animates vertically | | 1:15-1:30 | "Typical hook jobs are formatting, validation, secret protection, audit logging, notifications, and narrowing huge data before the model sees it." | Examples cascade across the screen | | 1:30-1:45 | "Hooks can lower cost by shrinking context. But they can raise cost or delay work if they call slow services or trigger too often." | Speed-vs-cost slider | | 1:45-2:00 | "So use hooks for enforcement and preprocessing at clear lifecycle boundaries, not as a place to hide random business logic." | Final rule card: **hooks = lifecycle controls** | Reference basis for narration: GitHub hooks docs and reference, Claude Code hooks reference, OpenCode event system. citeturn10view0turn10view1turn9view3turn8search13turn12view4turn12view5 #### Shot and animation plan - Reuse
- and
- hooks = lifecycle controls
- event_timeline and shield_gate
- Show a bright pulse moving through lifecycle events
- Visualize one hook blocking a command and another filtering log output
- Animate GitHub
- Add a token-savings counter when preprocessing reduces context
- End with a "hooks are for lifecycle boundaries" stamp
- flow-tokens
- attention-matrix-tiles
- swimlane-handoff
- masonry-wall
- risk-bowtie
- circuit-signal-traces

## Render Command

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-a-harness-hook --title "What is a Harness Hook" --output-id what-is-a-harness-hook --pattern systems-flow
```

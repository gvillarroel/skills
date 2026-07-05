# Production Notes

## Source Facts

- A harness is the runtime wrapper that turns a raw model into a usable assistant or agent.
- It usually defines the instruction layers, default tools, permissions, model picker, execution loop, approvals, memory behavior, logging, and extensibility surface.
- In practice, choosing GitHub Copilot, Claude Code, OpenCode, or VS Code agents means choosing a harness with defaults that materially affect quality, latency, cost, and risk.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is a Harness explainer should show hooks as lifecycle interception points where runtime events become enforceable policy, preprocessing, and cost tradeoffs.
- Mechanic: a lifecycle event pulse moves through timeline nodes, a shield gate overlays execution, provider event surfaces expose comparable hook systems, one Bash path is blocked while another log path is filtered, and savings versus latency meters settle into a lifecycle-control boundary.
- Candidate metaphors: hook lifecycle megacanvas, generic systems-flow pipeline, and provider feature comparison table.
- Rejected alternative: a generic systems-flow pipeline would show work movement but hide the hook-specific timing: session, prompt, tool, permission, compaction, notification, stop, blocking, filtering, and cost/latency boundaries.
- Chosen metaphor: hook lifecycle megacanvas with event_timeline, shield_gate overlay, GitHub hook badges, Claude event cloud, OpenCode event list, PreToolUse command block, log-filter path, hook-job cascade, token-savings counter, speed-vs-cost slider, and lifecycle-controls stamp.
- Visual vocabulary: brand red marks active event and safe preprocessing flow; status red marks blocked dangerous command and latency risk; dark red marks executable policy and filter gates; gray levels separate timeline, policy, provider surfaces, preprocessing jobs, and cost boundary. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates all Hook roles.
- Narration split: vendor event names, code details, and exact hook job labels stay in narration or source facts; the frame carries lifecycle interception and cost mechanics without explanatory text.

## Strategy Anchors

- comparison_grid
- credit_meter
- agent_loop_ring
- comparison_grid and agent_loop_ring
- Stack runtime layers: prompt
- Show same model icon in different harness shells
- Use a simple "engine vs car" motion metaphor to make the abstraction sticky
- credit_meter to show how harness defaults change spend
- Close with a pointer back to the harness comparison matrix
- flow-tokens
- swimlane-handoff
- layered-architecture
- masonry-wall
- circuit-signal-traces
- attention-matrix-tiles
- masonry wall
- megacanvas zones
- camera reframe

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-a-harness --title "What is a Harness" --output-id what-is-a-harness --pattern systems-flow
```

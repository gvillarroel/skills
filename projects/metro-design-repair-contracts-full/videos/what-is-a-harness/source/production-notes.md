# Production Notes

## Source Facts

- A harness is the runtime wrapper that turns a raw model into a usable assistant or agent.
- It usually defines the instruction layers, default tools, permissions, model picker, execution loop, approvals, memory behavior, logging, and extensibility surface.
- In practice, choosing GitHub Copilot, Claude Code, OpenCode, or VS Code agents means choosing a harness with defaults that materially affect quality, latency, cost, and risk.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is a Harness explainer should show the harness as the runtime shell that changes controls, defaults, cost, and behavior around the same model.
- Mechanic: a comparison grid selects one runtime cell, layers assemble around the model, the engine core becomes dashboard controls, the same model enters three different harness shells, and cost rises as defaults add tools, context, retries, and loop depth.
- Candidate metaphors: harness runtime megacanvas, generic systems-flow pipeline, and feature comparison table.
- Rejected alternative: a generic systems-flow pipeline would show work movement but hide the model-versus-harness distinction, the same-model-different-shell mechanic, and cost/control defaults.
- Chosen metaphor: harness runtime megacanvas with comparison_grid, runtime stack, engine-to-dashboard morph, same model badge in Copilot/Claude Code/OpenCode shells, credit_meter, muted feature grid, active use-case matrix, and highlighted selection path.
- Visual vocabulary: brand red marks selected runtime paths and shared model identity; dark red marks control/default emphasis; status red marks rising cost pressure; gray levels separate comparison surface, runtime layers, shell boundaries, controls, inactive defaults, and active selection. Colorset2 is not used because colorset1 gray hierarchy plus red state marks separates the required roles.
- Narration split: vendor names, exact plan features, and detailed selection criteria stay in narration or source facts; the frame carries runtime structure and selection mechanics without explanatory text.

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
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-a-harness --title "What is a Harness" --output-id what-is-a-harness --pattern systems-flow
```

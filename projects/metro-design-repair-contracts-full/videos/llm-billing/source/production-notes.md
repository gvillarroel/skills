# Production Notes

## Source Facts

- LLM billing is best understood as “tokens in, tokens out, model selected, extras enabled.” GitHub Copilot now meters usage in AI credits where 1 credit equals $0.01 and actual spend depends on token counts and model rates; Anthropic’s API prices Claude models directly per million input, cached-input, and output tokens, while Claude subscriptions bundle or cap usage in different ways.
- Even “local” models are not free: they consume electricity, hardware life, and developer time, so local inference should be compared against API cost, latency, and opportunity cost instead of being treated as zero-cost.

## Visual Metaphor Decision

- Visual pattern: sankey-flow.
- Concept claim: a good LLM Billing explainer should show how value splits, where loss exits, where streams transform, where they merge, and what bottleneck limits final output.
- Mechanic: one input band splits into retained and loss branches, parallel transforms recombine through a bottleneck, and final output appears after loss and merge states are visible.
- Candidate metaphors: sankey flow, funnel chart, and systems-flow map.
- Rejected alternative: a funnel chart would show dropoff but hide parallel transformations, recombination, and bottleneck ownership.
- Chosen metaphor: sankey-flow map with split branch, loss branch, parallel transform lanes, merge point, bottleneck, and final output readiness.
- Visual vocabulary: brand red means input value; dark gray means retained value; status red means explicit loss or bottleneck; dark red means transform; mid gray means output; black marks moving flow packets.
- Narration split: exact proportions and measured losses should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- (0.12 3) + (0.02 15)
- (0.12 5) + (0.02 25)
- (0.12 2.5) + (0.02 15)
- 1500 / 60
- 0.45 2 0.1883
- 0.17 22
- 1600 / 24
- (10/60) 80 22
- credit_meter
- gpu_rack
- token_stream
- power_curve
- 1 AI credit = $0.01
- $ / latency / retries / human time
- credit_meter and token_stream
- Use a split panel for **API**
- Animate one costly "retry spiral" to show how bad prompting turns into real spend
- gpu_rack and power_curve for local cost

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/llm-billing --title "LLM Billing" --output-id llm-billing --pattern sankey-flow
```

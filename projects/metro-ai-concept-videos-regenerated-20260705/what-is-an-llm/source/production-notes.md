# Production Notes

## Source Facts

- A large language model is a transformer-based neural network trained to predict text autoregressively.
- Tokens are chunks of text rather than full words.
- Newly generated tokens become part of the context for the next prediction.
- Parameters are learned numeric weights inside the network.
- Larger models often improve average capability, but size alone does not guarantee truth, reasoning quality, or cost efficiency.
- Modern LLM inference usually depends on GPUs because transformers map well to parallel matrix operations.

## Visual Metaphor Decision

- Visual pattern: systems-flow.
- Concept claim: a good What is an LLM explainer should show how work moves, where pressure accumulates, where failures branch, and how feedback protects the system.
- Mechanic: a job packet moves through intake, bus, queue, workers, storage, retry, dead-letter, metrics, and feedback-control layers.
- Candidate metaphors: pipeline map, state machine, and incident timeline.
- Rejected alternative: a plain timeline would show order but hide pressure, branching, and capacity constraints.
- Chosen metaphor: systems-flow map with explicit queue pressure, worker capacity, failure branches, and feedback throttle.
- Visual vocabulary: brand red means accepted work; status red means retry or failed work; dark red means feedback control; dark gray means active transformation; stacked gray slots mean bounded capacity.
- Narration split: implementation details, exact vendor names, and operational thresholds are omitted unless supplied as source facts.

## Strategy Anchors

- token stream
- context window box
- attention arcs
- autoregressive loop
- parameter counter
- capability versus truth warning
- GPU rack
- recap stack

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/what-is-an-llm --title "What is an LLM" --output-id what-is-an-llm --pattern systems-flow
```

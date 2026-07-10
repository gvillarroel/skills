# Production Notes

## Source Facts

- A large language model is a transformer-based neural network trained to predict text autoregressively: given prior tokens, it estimates the next token and repeats that process until it reaches a stopping condition.
- Tokens are chunks of text rather than full words, and the model’s size usually refers to its number of learned parameters, not its context window or factual correctness.
- Modern LLM training and inference depend heavily on GPUs because transformers map well to parallel matrix operations, and larger models often improve capability on average, although scaling laws describe trends rather than guarantees.

## Visual Metaphor Decision

- Visual pattern: metric-dashboard.
- Concept claim: a good What is an LLM explainer should show the metric owner, threshold rule, anomaly, forecast, and decision window as separate visual mechanisms.
- Mechanic: a primary trend line reveals first, threshold bands convert the trend into an operating rule, an anomaly highlights risk, and a forecast cone opens the decision window.
- Candidate metaphors: metric dashboard, comparison matrix, and phase timeline.
- Rejected alternative: a comparison matrix would rank choices but hide when a metric crosses an operational threshold.
- Chosen metaphor: metric dashboard with trend, threshold bands, anomaly marker, forecast cone, and late decision panel.
- Visual vocabulary: brand red means primary metric trend; dark gray means healthy range; dark red means warning; status red means action risk; mid gray means forecast; black means quality context.
- Narration split: exact metric values, statistical confidence, and alert thresholds should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- token_stream
- context_window_box
- gpu_rack
- parameter_counter
- Context -> Next token -> Repeat
- Tokens != words
- Parameters = learned weights
- Not equal to truth
- Tokens / Transformer / Parameters / GPUs / Context
- Morph token bars into an attention graph to introduce transformers
- End with a four-tile summary card that can be reused as a chapter bumper in later videos
- matmul-tile-accumulation
- attention-matrix-tiles
- token-boxes-to-context-window
- masonry-wall
- qkv-projection-flow
- kv-cache-growth
- masonry wall

## Render Command

```powershell
uv run --script .agents/skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/what-is-an-llm --title "What is an LLM" --output-id what-is-an-llm --pattern metric-dashboard
```

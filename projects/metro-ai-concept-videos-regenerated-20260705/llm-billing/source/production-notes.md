# Production Notes

## Source Facts

- LLM billing reduces to model selected, input tokens, output tokens, and whether usage is wrapped in a subscription.
- GitHub Copilot meters usage in AI credits, where 1 AI credit equals $0.01.
- Token usage converts into credits based on the selected model.
- Copilot Pro includes 1,500 AI credits per month, and Business includes 1,900 credits per seat in a pooled organization bucket.
- Claude API pricing is direct per million input, cached-input, and output tokens.
- Claude subscriptions package the underlying usage instead of removing the usage cost.
- Local models are not free because electricity, hardware life, and developer time still have costs.
- Better prompts, smaller sufficient models, hooks, and skills usually reduce wasted retries and cost.

## Visual Metaphor Decision

- Visual pattern: metric-dashboard.
- Concept claim: a good LLM Billing explainer should show the metric owner, threshold rule, anomaly, forecast, and decision window as separate visual mechanisms.
- Mechanic: a primary trend line reveals first, threshold bands convert the trend into an operating rule, an anomaly highlights risk, and a forecast cone opens the decision window.
- Candidate metaphors: metric dashboard, comparison matrix, and phase timeline.
- Rejected alternative: a comparison matrix would rank choices but hide when a metric crosses an operational threshold.
- Chosen metaphor: metric dashboard with trend, threshold bands, anomaly marker, forecast cone, and late decision panel.
- Visual vocabulary: brand red means primary metric trend; dark gray means healthy range; dark red means warning; status red means action risk; mid gray means forecast; black means quality context.
- Narration split: exact metric values, statistical confidence, and alert thresholds should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- credit meter
- token stream converting into dollars or credits
- individual versus pooled bucket split
- Claude pricing table cards
- subscription layers over raw token meter
- GPU rack with power meter and clock
- retry spiral
- optimized cost waterfall
- final cost scorecard

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/llm-billing --title "LLM Billing" --output-id llm-billing --pattern metric-dashboard
```

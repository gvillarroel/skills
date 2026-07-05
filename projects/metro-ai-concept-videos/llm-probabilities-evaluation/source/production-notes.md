# Production Notes

## Source Facts

- LLMs assign probabilities over candidate next tokens rather than looking up one true answer during generation.
- The selected token is appended back into context, creating a repeated generation loop.
- Better context reshapes the probability distribution toward better tokens, but the output remains probabilistic.
- Log probabilities let you inspect token confidence after generation.
- Logit bias can nudge specified tokens up or down before selection.
- pass@N asks whether at least one of N sampled candidates is correct.
- Programmatic verification is strongest when available, including unit tests, schema checks, exact match, parsers, and tool-execution success.
- LLM-as-judge evaluation can help when objective checks are hard, but it needs a clear rubric and calibration against human review.

## Visual Metaphor Decision

- Visual pattern: scenario-tree.
- Concept claim: a good LLM Probabilities and Evaluation explainer should show how a decision branches into plausible scenarios, where probability or evidence belongs, and when fallback changes the selected outcome.
- Mechanic: one decision point branches into base, upside, and downside routes; probabilities and evidence appear before the decision gate, then fallback and outcome are revealed late.
- Candidate metaphors: scenario tree, comparison matrix, and phase timeline.
- Rejected alternative: a comparison matrix would rank options but hide downstream branches, fallback route, and conditional outcomes.
- Chosen metaphor: scenario-tree map with decision root, scenario branches, probability labels, evidence weight, upside/risk branches, fallback route, and selected outcome.
- Visual vocabulary: brand red means main scenario evidence; dark gray means upside; status red means downside risk; dark red means fallback; mid gray means selected outcome.
- Narration split: exact probabilities, payoff values, and confidence intervals should come from source facts when available; otherwise the scaffold stays schematic.

## Strategy Anchors

- probability bars
- blinking cursor
- poor versus rich context comparison
- confidence thermometer
- boosted and suppressed token cards
- passN grid
- test runner panel
- programmatic verification checklist
- judge rubric cards
- final evaluation loop recap

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-ai-concept-videos/llm-probabilities-evaluation --title "LLM Probabilities and Evaluation" --output-id llm-probabilities-evaluation --pattern scenario-tree
```

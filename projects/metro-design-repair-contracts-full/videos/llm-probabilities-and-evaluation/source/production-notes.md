# Production Notes

## Source Facts

- LLMs do not “look up the one true answer” during generation; they assign probabilities over candidate next tokens and then select or sample from that distribution.
- Better context helps because it reshapes the distribution toward better tokens, but the output remains probabilistic.
- In coding and agentic systems, this is why **pass@N** matters: if you sample multiple candidates, you often get a higher chance that at least one is correct; practical evaluation then uses programmatic checks where possible and model-based judging where automation is harder.
- mermaid flowchart LR A[Prompt + context] --> B[Model computes token distribution] B --> C{Select token} C -->|greedy / sampled| D[Append token to context] D --> B D --> E[Candidate answer] E --> F{Evaluation} F -->|unit tests/schema/rules| G[Programmatic verdict] F -->|rubric or judge model| H[LLM-as-judge verdict] G --> I[pass@1 / pass@N / score] H --> I ``` The diagram highlights the main teaching point: generation and evaluation are separate loops.
- Token probabilities describe **how** text is produced; pass@N and verification describe **how** you decide whether the produced answer is good enough.

## Visual Metaphor Decision

- Visual pattern: comparison-matrix.
- Concept claim: a good LLM Probabilities and Evaluation explainer should compare options against shared criteria, expose tradeoffs, and delay recommendation until evidence is visible.
- Mechanic: option columns stay fixed while criteria rows fill, score-shift markers explain changing preference, and recommendation plus guardrail panels appear after the comparison is legible.
- Candidate metaphors: decision matrix, ranking podium, and pros/cons ledger.
- Rejected alternative: a ranking podium would show a winner but hide which criteria changed the decision.
- Chosen metaphor: comparison matrix with shared criteria rows, per-option score bars, tradeoff lens, recommendation, and guardrail.
- Visual vocabulary: brand red means the selected option or score movement; dark gray means quality balance; status red means cost or risk; dark red means guardrail; black marks the decision cursor.
- Narration split: exact scores and weighting can be explained in narration or source notes unless the prompt supplies them.

## Strategy Anchors

- mermaid flowchart LR A[Prompt + context] --> B[Model computes token distribution] B --> C{Select token} C -->|greedy / sampled| D[Append token to context] D --> B D --> E[Candidate answer] E --> F{Evaluation} F -->|unit tests/schema/rules| G[Programmatic verdict] F -->|rubric or judge model| H[LLM-as-judge verdict] G --> I[pass@1 / pass@N / score] H --> I
- The diagram highlights the main teaching point: generation and evaluation are separate loops. Token probabilities describe **how** text is produced; pass@N and verification describe **how** you decide whether the produced answer is good enough. citeturn33search4turn20search9turn20search3 #### Timed narration and visuals | Time | Spoken narration | On-screen text and visual cues | |---|---|---| | 0:00-0:15 | "Every token an LLM produces comes from a probability distribution. The model scores many possible next tokens, then one gets selected." |
- animate above a blinking cursor | | 0:15-0:30 | "That means two things. First, outputs can vary across runs. Second, better context usually improves results because it changes the distribution." | Same prompt with poor vs rich context, bars shift visibly | | 0:30-0:45 | "Tools like log probabilities let you inspect confidence after generation, and logit bias can nudge certain tokens up or down." | Confidence thermometer and boosted/suppressed token cards | | 0:45-1:00 | "In coding, one answer is often not enough. So teams use pass at N: generate multiple candidates and ask whether at least one of them is correct." |
- fills with green and red boxes | | 1:00-1:15 | "The classic example is HumanEval, where generated code is executed against tests. If any of N samples pass, that improves pass at N even if pass at one stays lower." | Test runner panel; one out of five turns green | | 1:15-1:30 | "Programmatic verification is the gold standard when you can use it: unit tests, schema checks, exact match, parsers, or tool-execution success." | Checklist icons: tests, JSON schema, parser, sandbox | | 1:30-1:45 | "When you cannot write objective checks, you can still use an LLM as judge, but only with a clear rubric and calibration against human review." | Judge panel with rubric cards and agreement gauge | | 1:45-2:00 | "So the big lesson is simple: treat LLM outputs like samples from a distribution, then build evaluation loops that make correctness measurable." | Full-screen recap: **Distribution -> Samples -> Verification -> Metrics** | Reference basis for narration and evaluation framing: OpenAI logprobs/logit bias docs, HumanEval/Codex evaluation work, OpenAI eval best practices, and Anthropic evaluation guidance. citeturn33search4turn33search1turn20search0turn32view0turn20search9turn20search6turn20search3 #### Shot and animation plan - Reuse
- ; show top three candidate tokens changing with richer context. - Reuse
- ; animate a better prompt narrowing uncertainty. - Show a compact
- with one correct answer emerging only on sample four. - Reuse
- Distribution -> Samples -> Verification -> Metrics
- probability_bars
- context_window_box
- Show a compact passN_grid with one correct answer emerging only on sample four
- test_runner asset from any existing code-verification scene
- Animate a judge model rubric as cards scoring correctness
- End with the same summary formula card every later evaluation-focused video can reuse
- attention-matrix-tiles
- token-boxes-to-context-window
- evidence-ladder
- masonry-wall

## Render Command

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/metro-design-repair-contracts-full/videos/llm-probabilities-and-evaluation --title "LLM Probabilities and Evaluation" --output-id llm-probabilities-and-evaluation --pattern comparison-matrix
```

First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root, in order. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/llm-probabilities-evaluation/src/index.html --source-package projects/metro-ai-concept-videos/llm-probabilities-evaluation/source/source-package.json --output projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `scenario-tree` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: LLM Probabilities and Evaluation.
Video title: LLM Probabilities and Evaluation.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, branch labels, probability labels, metrics, or rubric cards.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the production notes justify why the red, neutral, white, black, and gray palette cannot distinguish the required states.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/source/source-package.json`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/source/production-notes.md`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/src/index.html`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/src/render.mjs`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/video-renders/draft/videos/llm-probabilities-evaluation.mp4`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/video-renders/draft/review/llm-probabilities-evaluation-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/video-renders/draft/review/llm-probabilities-evaluation-contact-sheet.json`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/llm-probabilities-evaluation/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- LLMs assign probabilities over candidate next tokens rather than looking up one true answer during generation.
- The selected token is appended back into context, creating a repeated generation loop.
- Better context reshapes the probability distribution toward better tokens, but the output remains probabilistic.
- Log probabilities let you inspect token confidence after generation.
- Logit bias can nudge specified tokens up or down before selection.
- pass@N asks whether at least one of N sampled candidates is correct.
- Programmatic verification is strongest when available, including unit tests, schema checks, exact match, parsers, and tool-execution success.
- LLM-as-judge evaluation can help when objective checks are hard, but it needs a clear rubric and calibration against human review.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: Show a model scoring many candidate next tokens as a probability distribution before one token is selected.
- 0:15-0:30: Compare poor context and rich context while probability bars visibly shift.
- 0:30-0:45: Reveal log probabilities and logit bias as inspection and nudging controls.
- 0:45-1:00: Branch from one prompt into multiple candidate answers to introduce pass@N.
- 1:00-1:15: Show a HumanEval-like test runner where one out of five candidates passes.
- 1:15-1:30: Route candidates through programmatic verification: unit tests, schema checks, parser, and sandbox.
- 1:30-1:45: Route hard-to-automate cases through a judge panel with rubric cards and calibration gauge.
- 1:45-2:00: End on the loop: distribution, samples, verification, and metrics.

Preserve these visual anchors:

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

Preserve these scenario labels:

- prompt plus context
- token distribution
- greedy selection
- sampled selection
- appended token
- candidate answer
- programmatic verdict
- judge verdict
- pass at one
- pass at N

Preserve these probability labels:

- top token 42 percent
- alternative token 28 percent
- long tail 30 percent
- richer context shifts distribution
- sample 1 fails
- sample 4 passes
- pass@N success
- calibrated judge

The scenario-tree render-state check must prove `visualPattern=scenario-tree`, preserved scenario labels, preserved probability labels, nondecreasing scenario progression, probability, risk or uncertainty, decision, fallback or alternative, and outcome states transitioning from hidden to visible, and visible mechanism progression across the full 120 seconds.

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/llm-probabilities-evaluation/`; do not write into the copied skill directory.

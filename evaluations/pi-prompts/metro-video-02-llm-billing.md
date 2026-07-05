First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root, in order. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/llm-billing/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/llm-billing/src/index.html --source-package projects/metro-ai-concept-videos/llm-billing/source/source-package.json --output projects/metro-ai-concept-videos/llm-billing/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `metric-dashboard` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: LLM Billing.
Video title: LLM Billing.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, data objects, metric cards, threshold markers, or table cells.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the production notes justify why the red, neutral, white, black, and gray palette cannot distinguish the required states.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/llm-billing/source/source-package.json`
- `projects/metro-ai-concept-videos/llm-billing/source/production-notes.md`
- `projects/metro-ai-concept-videos/llm-billing/src/index.html`
- `projects/metro-ai-concept-videos/llm-billing/src/render.mjs`
- `projects/metro-ai-concept-videos/llm-billing/artifacts/video-renders/draft/videos/llm-billing.mp4`
- `projects/metro-ai-concept-videos/llm-billing/artifacts/video-renders/draft/review/llm-billing-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/llm-billing/artifacts/video-renders/draft/review/llm-billing-contact-sheet.json`
- `projects/metro-ai-concept-videos/llm-billing/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/llm-billing/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/llm-billing/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/llm-billing/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- LLM billing reduces to model selected, input tokens, output tokens, and whether usage is wrapped in a subscription.
- GitHub Copilot meters usage in AI credits, where 1 AI credit equals $0.01.
- Token usage converts into credits based on the selected model.
- Copilot Pro includes 1,500 AI credits per month, and Business includes 1,900 credits per seat in a pooled organization bucket.
- Claude API pricing is direct per million input, cached-input, and output tokens.
- Claude subscriptions package the underlying usage instead of removing the usage cost.
- Local models are not free because electricity, hardware life, and developer time still have costs.
- Better prompts, smaller sufficient models, hooks, and skills usually reduce wasted retries and cost.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: Reduce LLM billing to four drivers: model, input tokens, output tokens, and subscription wrapper.
- 0:15-0:30: Show GitHub Copilot AI credits, with 1 AI credit equal to $0.01 and token bars converting into credits.
- 0:30-0:45: Compare Copilot Pro's 1,500 monthly credits with Business's 1,900 pooled credits per seat.
- 0:45-1:00: Show Claude API pricing as per-million input, cached-input, and output token meters.
- 1:00-1:15: Show subscription layers packaging raw token usage rather than deleting the underlying cost.
- 1:15-1:30: Reveal local model costs through GPU power, hardware aging, and developer waiting time.
- 1:30-1:45: Show a retry spiral and then an optimized path using smaller models, tighter prompts, hooks, and skills.
- 1:45-2:00: End on a scorecard comparing dollars, latency, retries, and human time.

Preserve these visual anchors:

- credit meter
- token stream converting into dollars or credits
- individual versus pooled bucket split
- Claude pricing table cards
- subscription layers over raw token meter
- GPU rack with power meter and clock
- retry spiral
- optimized cost waterfall
- final cost scorecard

Preserve these metric labels:

- selected model
- input tokens
- output tokens
- AI credits
- cached input
- subscription allowance
- local electricity
- hardware amortization
- developer time
- retry waste

Preserve these threshold labels:

- 1 AI credit = $0.01
- Pro 1,500 credits/month
- Business 1,900 credits/seat
- 60 AI credits example
- Claude per million tokens
- local is not free
- fewer wasted loops

The metric-dashboard render-state check must prove `visualPattern=metric-dashboard`, preserved metric labels, preserved threshold labels, nondecreasing metric or mechanism reveal, and visible mechanism progression across the full 120 seconds.

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/llm-billing/`; do not write into the copied skill directory.

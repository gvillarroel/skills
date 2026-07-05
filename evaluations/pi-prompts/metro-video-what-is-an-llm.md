First action: read this prompt at `../prompt.md`. Then run the exact commands below from the isolated workspace root. Do not list directories, do not read helper source, do not ask questions, and do not stop before verifying the exact outputs.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-ai-concept-videos/what-is-an-llm/artifacts/reviews/prompt-contract-build.json
```

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_tonal_style.py --html projects/metro-ai-concept-videos/what-is-an-llm/src/index.html --source-package projects/metro-ai-concept-videos/what-is-an-llm/source/source-package.json --output projects/metro-ai-concept-videos/what-is-an-llm/artifacts/reviews/metro-style-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer video scaffold for the video module described below.

Use the `systems-flow` scaffold. Use 120 seconds, 30 fps, and 1280x720.

Topic: What is an LLM.
Video title: What is an LLM.
Checked date: 2026-07-04.

Style contract:

- Use Metro Minimal Tonal Motion: one large navigable megacanvas, flat modular surfaces, Metro blocks, Masonry-like section blocks, camera zoom/pan/reframe movement, and block expansion transitions.
- Do not reserve space for titles, subtitles, captions, or editorial text. Use only functional labels inside diagrams, charts, process nodes, state labels, or data objects.
- Use color set 1 whenever possible: primary red `#9e1b32`, dark red `#6d1222`, status red `#e8002a`, red highlight `#ffccd5`, neutral text/surface `#333e48`, black `#000000`, white `#ffffff`, and grays `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c`, `#828282`, `#696969`, `#4f4f4f`, `#363636`, `#1c1c1c`.
- Do not use the full-color palette unless the concept cannot be distinguished with red, neutral, white, black, and gray.

Required exact scaffold outputs:

- `projects/metro-ai-concept-videos/what-is-an-llm/source/source-package.json`
- `projects/metro-ai-concept-videos/what-is-an-llm/source/production-notes.md`
- `projects/metro-ai-concept-videos/what-is-an-llm/src/index.html`
- `projects/metro-ai-concept-videos/what-is-an-llm/src/render.mjs`
- `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/video-renders/draft/videos/what-is-an-llm.mp4`
- `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/video-renders/draft/review/what-is-an-llm-contact-sheet.jpg`
- `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/video-renders/draft/review/what-is-an-llm-contact-sheet.json`
- `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/reviews/self-review.md`
- `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/reviews/prompt-contract-build.json`

Also write the browser render-state report to `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/reviews/render-state-check.json`.

Also write the Metro tonal style audit to `projects/metro-ai-concept-videos/what-is-an-llm/artifacts/reviews/metro-style-audit.json`.

Preserve these source facts:

- A large language model is a transformer-based neural network trained to predict text autoregressively.
- Tokens are chunks of text rather than full words.
- Newly generated tokens become part of the context for the next prediction.
- Parameters are learned numeric weights inside the network.
- Larger models often improve average capability, but size alone does not guarantee truth, reasoning quality, or cost efficiency.
- Modern LLM inference usually depends on GPUs because transformers map well to parallel matrix operations.

Preserve these timed narration beats as the production timing contract:

- 0:00-0:15: Context enters the model, and the model predicts one next token, then repeats.
- 0:15-0:30: The word "token" matters because a token is not always a whole word.
- 0:30-0:45: Transformer attention connects context tokens and scales better than older sequence models.
- 0:45-1:00: Autoregressive generation folds each new token back into the next prediction step.
- 1:00-1:15: Parameter count means learned numeric weights inside the network.
- 1:15-1:30: More parameters often improve average performance but do not equal truth.
- 1:30-1:45: GPUs execute the parallel tensor work behind transformer inference.
- 1:45-2:00: Recap the system as tokens, transformer, parameters, GPUs, and context.

Preserve these visual anchors:

- token stream
- context window box
- attention arcs
- autoregressive loop
- parameter counter
- capability versus truth warning
- GPU rack
- recap stack

Preserve these system labels:

- Prompt context
- Tokenizer
- Context window
- Transformer attention
- Parameter weights
- GPU compute
- Next token
- Feedback loop
- Capability trend
- Truth warning
- Recap stack

After the commands finish, verify the exact output paths, wrapper report, contact-sheet manifest, media properties, source preservation, derived render-state check, and Metro tonal style audit. Keep generated task files under `projects/metro-ai-concept-videos/what-is-an-llm/`; do not write into the copied skill directory.

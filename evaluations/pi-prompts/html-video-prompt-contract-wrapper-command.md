# Isolated HTML Video Prompt Contract Wrapper Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

First action: read `../prompt.md` directly. Then run this command exactly:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/wrapper-saga-video/artifacts/reviews/prompt-contract-build.json
```

Do not ask for clarification. Do not derive a title-based project name. Do not open `build_standalone_explainer.py` manually; the wrapper is responsible for deriving and running the helper.

Required exact video package outputs:

- `projects/wrapper-saga-video/source/source-package.json`
- `projects/wrapper-saga-video/source/production-notes.md`
- `projects/wrapper-saga-video/src/index.html`
- `projects/wrapper-saga-video/src/render.mjs`
- `projects/wrapper-saga-video/artifacts/video-renders/draft/videos/wrapper-saga-explainer.mp4`
- `projects/wrapper-saga-video/artifacts/video-renders/draft/review/wrapper-saga-explainer-contact-sheet.jpg`
- `projects/wrapper-saga-video/artifacts/video-renders/draft/review/wrapper-saga-explainer-contact-sheet.json`
- `projects/wrapper-saga-video/artifacts/reviews/self-review.md`

The wrapper report must be written at projects/wrapper-saga-video/artifacts/reviews/prompt-contract-build.json.

Topic: event-driven saga architecture.

Video title: Wrapper Saga Exact Path Explainer.

Checked date: July 4, 2026.

Use the `systems-flow` scaffold. The final MP4 basename must be `wrapper-saga-explainer`, and the shared project root must be `projects/wrapper-saga-video`.

Preserve these source facts in `source-package.json`:

- Saga workflows coordinate multi-step business processes through events and compensating actions.
- A bounded queue makes pressure visible before workers saturate.
- Retries need caps and backoff so failures do not become infinite invisible loops.
- Dead-letter paths separate failed work for inspection instead of hiding it in the main flow.
- Feedback control can slow intake when downstream capacity is exceeded.

Preserve these visual anchors:

- intake sources
- event bus
- bounded queue
- worker pool
- retry branch
- dead-letter path
- throughput metric
- feedback limit

Use 12 seconds, 12 fps, and 1280x720. Before final response, inspect the wrapper report, contact-sheet JSON manifest, source package, and self-review. Both JSON reports must have `"passed": true`, and `source-package.json` must contain `bounded queue` and `Feedback control`.

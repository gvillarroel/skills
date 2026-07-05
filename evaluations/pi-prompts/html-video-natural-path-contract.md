# Isolated HTML Video Natural Path Contract Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

First action: read `../prompt.md` directly. Do not run directory listings or shell probes before reading it.

Create a standalone systems-flow explainer video package from this prompt. This prompt intentionally does not provide the final helper command; derive the helper arguments from the exact required paths below.

Do not ask for clarification. Do not use title-derived project names. Do not write into the copied skill directory. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash.

Required exact outputs:

- `projects/natural-saga-video/source/source-package.json`
- `projects/natural-saga-video/source/production-notes.md`
- `projects/natural-saga-video/src/index.html`
- `projects/natural-saga-video/src/render.mjs`
- `projects/natural-saga-video/artifacts/video-renders/draft/videos/natural-saga-explainer.mp4`
- `projects/natural-saga-video/artifacts/video-renders/draft/review/natural-saga-explainer-contact-sheet.jpg`
- `projects/natural-saga-video/artifacts/video-renders/draft/review/natural-saga-explainer-contact-sheet.json`
- `projects/natural-saga-video/artifacts/reviews/self-review.md`

Topic: event-driven saga architecture.

Video title: Natural Saga Exact Path Explainer.

Checked date: July 4, 2026.

Use the `systems-flow` scaffold. The final MP4 basename must be `natural-saga-explainer`, and the shared project root must be `projects/natural-saga-video`.

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

Use 12 seconds, 12 fps, and 1280x720. Before final response, inspect the contact-sheet JSON manifest and self-review. The contact-sheet JSON must have `"passed": true`, and `source-package.json` must contain `bounded queue` and `Feedback control`.

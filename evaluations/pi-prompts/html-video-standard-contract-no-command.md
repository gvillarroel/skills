Create a complete standalone HTML video package for a systems-flow explainer. First action: read `../prompt.md` directly with the file-reading tool, not a shell command. No full command is supplied; derive the runnable workflow from the skill's standard exact-output workflow.

Do not ask clarifying questions, do not run directory listings or shell probes before reading the prompt, and do not write into the copied skill directory. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash.

Required exact video package outputs:

- `projects/standard-contract-video/source/source-package.json`
- `projects/standard-contract-video/source/production-notes.md`
- `projects/standard-contract-video/src/index.html`
- `projects/standard-contract-video/src/render.mjs`
- `projects/standard-contract-video/artifacts/video-renders/draft/videos/standard-contract-explainer.mp4`
- `projects/standard-contract-video/artifacts/video-renders/draft/review/standard-contract-explainer-contact-sheet.jpg`
- `projects/standard-contract-video/artifacts/video-renders/draft/review/standard-contract-explainer-contact-sheet.json`
- `projects/standard-contract-video/artifacts/reviews/self-review.md`

Write the prompt-contract build report to `projects/standard-contract-video/artifacts/reviews/prompt-contract-build.json`.

Topic: event-driven order processing reliability.

Video title: Standard Contract Reliability Explainer.

Checked date: July 4, 2026.

Use the `systems-flow` scaffold.

Preserve these source facts:

- Orders enter through three intake sources: storefront, API, and scheduled import.
- Every order is normalized onto one event contract before it reaches workers.
- The bounded queue is the visible pressure gauge before workers saturate.
- Retry policy must branch separately from dead-letter inspection.
- Feedback should visibly throttle intake when queue pressure and retries rise.

Preserve these visual anchors:

- intake sources
- event bus
- bounded queue
- worker pool
- retry branch
- dead-letter branch
- feedback throttle gate
- throughput metric

Use 12 seconds, 12 fps, and 1280x720.

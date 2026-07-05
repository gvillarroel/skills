First action: read the exact file ../prompt.md with the file-reading tool; do not run any shell command before that. After reading it, run the exact wrapper command below immediately; do not list directories, probe the workspace, or use PowerShell-style commands in bash.

Use the bundled html-d3-anime-video-workflow skill to build a deterministic standalone HTML video scaffold.

Run this exact wrapper command from the evaluation workspace:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/systems-flow-labeled-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/systems-flow-labeled-video/source/source-package.json`
- `projects/systems-flow-labeled-video/source/production-notes.md`
- `projects/systems-flow-labeled-video/src/index.html`
- `projects/systems-flow-labeled-video/src/render.mjs`
- `projects/systems-flow-labeled-video/artifacts/video-renders/draft/videos/labeled-systems-flow.mp4`
- `projects/systems-flow-labeled-video/artifacts/video-renders/draft/review/labeled-systems-flow-contact-sheet.jpg`
- `projects/systems-flow-labeled-video/artifacts/video-renders/draft/review/labeled-systems-flow-contact-sheet.json`
- `projects/systems-flow-labeled-video/artifacts/reviews/self-review.md`
- `projects/systems-flow-labeled-video/artifacts/reviews/prompt-contract-build.json`

The browser render-state report must be written to:

- `projects/systems-flow-labeled-video/artifacts/reviews/render-state-check.json`

The wrapper should derive this state check from the prompt. It must prove `visualPattern=systems-flow`, final `queueSlots=8`, final `visibleMechanismCount=6`, monotonic queue fill, retry, dead-letter, and feedback transitions, preserved system labels, and mechanism-count progression.

Topic: explaining the validation pipeline for advanced video skill updates.

Video title: Skill Video Validation Systems Flow

Checked date: July 4, 2026

Use the `systems-flow` scaffold.

Preserve these source facts:

- A skill patch enters the pipeline only after the prompt and expected artifact paths are known.
- The evidence bus carries source facts, anchors, exact output paths, and media format constraints.
- A bounded validation queue makes backlog pressure visible before work reaches the validator pool.
- Retry and dead-letter paths separate recoverable render issues from artifacts that need manual critique.
- The feedback throttle slows new changes until source preservation, media metrics, and payload checks pass.

Preserve these visual anchors:

- Three intake sources must feed one shared evidence bus.
- The validation queue must visibly fill before worker nodes pulse.
- The validator pool must branch failed work into retry and dead-letter controls.
- A throughput trend must move separately from the main packet path.
- The feedback throttle must loop back toward intake late in the video.
- A moving job token must traverse the success path.
- Retry and failed-work packets must use different branch colors.
- The final caption must explain that feedback limits intake before failure.

Preserve these system components exactly:

- change request
- review event
- risk signal
- evidence bus
- validation queue
- validator pool
- release store
- retry policy
- review dead-letter
- throughput trend
- feedback throttle

Format requirements:

- Duration: 12 seconds.
- Frame rate: 12 fps.
- Resolution: 1280x720.

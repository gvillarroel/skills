Use $source-to-video-director to create exactly `source-package.json`, `storyboard.md`, and `shot-contract.json` in the workspace root for a code-change video titled `Retry Budget for Stream Ingestion`; route is `code-change`; change size is `4 files, +126/-38`; behavior is `Workers retry transient stream disconnects up to a per-job retry budget, then write a terminal failure event.`; files are `worker.ts`, `events.ts`, `config.ts`, and `worker.test.ts`; constant is `STREAM_RETRY_BUDGET`; event is `stream_retry_exhausted`; audience is `Backend engineers reviewing release notes`; duration is `24 seconds`; aspect is `16:9`; style is `Quiet technical diagram`; audio is `silent, no music, no voiceover, no captions`; do not write renderer code and do not include any GSAP dependency, import, timeline snippet, or implementation instruction.

Requirements:

- source-package.json must preserve the exact title, files, constant, event, behavior, audience, duration, aspect, style, and audio constraints.
- storyboard.md must start with a Source Facts table containing the exact supplied literals.
- shot-contract.json must contain exactly 4 shots, semantic motionIntent entries, `seekDeterministic: true`, and `forbiddenDependencies: ["gsap"]`.
- All three artifacts must include the anchors STREAM_RETRY_BUDGET, stream_retry_exhausted, worker.ts, events.ts, config.ts, and worker.test.ts.

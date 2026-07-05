First action: read the exact file ../prompt.md with the file-reading tool; do not run any shell command before that. After reading it, run the exact wrapper command below immediately; do not list directories, probe the workspace, or use PowerShell-style commands in bash.

Use the bundled html-d3-anime-video-workflow skill to build a deterministic standalone HTML video scaffold.

Run this exact wrapper command from the evaluation workspace:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/phase-timeline-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/phase-timeline-video/source/source-package.json`
- `projects/phase-timeline-video/source/production-notes.md`
- `projects/phase-timeline-video/src/index.html`
- `projects/phase-timeline-video/src/render.mjs`
- `projects/phase-timeline-video/artifacts/video-renders/draft/videos/phase-timeline-explainer.mp4`
- `projects/phase-timeline-video/artifacts/video-renders/draft/review/phase-timeline-explainer-contact-sheet.jpg`
- `projects/phase-timeline-video/artifacts/video-renders/draft/review/phase-timeline-explainer-contact-sheet.json`
- `projects/phase-timeline-video/artifacts/reviews/self-review.md`
- `projects/phase-timeline-video/artifacts/reviews/prompt-contract-build.json`

The browser render-state report must be written to:

- `projects/phase-timeline-video/artifacts/reviews/render-state-check.json`

The wrapper should derive this state check from the prompt. It must prove `visualPattern=phase-timeline`, risk, gate, handoff, and final milestone transitions, final `activePhase=5`, monotonic active-phase progress, preserved phase labels, and `visibleMechanismCount` progression.

Topic: produce, critique, improve, and publish loop for advanced skill video scaffolds.

Video title: Advanced Video Skill Iteration Timeline

Checked date: July 4, 2026

Use the `phase-timeline` scaffold.

Preserve these source facts:

- The loop starts by locking the prompt, source facts, exact artifact paths, and expected media format.
- A draft build should produce source package, notes, HTML, render script, MP4, contact sheet, and self-review.
- Critique must inspect both media metrics and visible composition, not only whether files exist.
- Improvements should patch the reusable skill before rerunning the isolated validation.
- Publication happens only after exact outputs, source preservation, render state, and payload checks pass.

Preserve these visual anchors:

- Six phase cards must appear in chronological order from left to right.
- A moving phase token must travel across the main timeline.
- A risk scan lane must appear below the main sequence before the decision gate.
- A decision gate must appear above the main timeline before validation.
- A handoff route must carry constraints into the validation phase.
- A release milestone must appear only near the end.
- Source lock and quality gate meters must be distinct from the phase cards.
- The final caption must state that release happens only after gates pass.

Preserve these timeline phases exactly:

- source lock
- draft build
- visual critique
- skill patch
- pi validation
- publish

Format requirements:

- Duration: 12 seconds.
- Frame rate: 12 fps.
- Resolution: 1280x720.

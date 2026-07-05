First action: read the exact file ../prompt.md with the file-reading tool; do not run any shell command before that.

Use the bundled html-d3-anime-video-workflow skill to build a deterministic standalone HTML video scaffold.

Run this exact wrapper command from the evaluation workspace:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/state-machine-labeled-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/state-machine-labeled-video/source/source-package.json`
- `projects/state-machine-labeled-video/source/production-notes.md`
- `projects/state-machine-labeled-video/src/index.html`
- `projects/state-machine-labeled-video/src/render.mjs`
- `projects/state-machine-labeled-video/artifacts/video-renders/draft/videos/labeled-state-machine.mp4`
- `projects/state-machine-labeled-video/artifacts/video-renders/draft/review/labeled-state-machine-contact-sheet.jpg`
- `projects/state-machine-labeled-video/artifacts/video-renders/draft/review/labeled-state-machine-contact-sheet.json`
- `projects/state-machine-labeled-video/artifacts/reviews/self-review.md`
- `projects/state-machine-labeled-video/artifacts/reviews/prompt-contract-build.json`

The browser render-state report must be written to:

- `projects/state-machine-labeled-video/artifacts/reviews/render-state-check.json`

The wrapper should derive this state check from the prompt. It must prove `visualPattern=state-machine`, final `activeState=5`, monotonic active-state progress, rollback, compensation, and terminal transitions, preserved state and guard labels, and `visibleMechanismCount` progression.

Topic: modeling a review-to-publish workflow for advanced video skill updates.

Video title: Skill Update Review State Machine

Checked date: July 4, 2026

Use the `state-machine` scaffold.

Preserve these source facts:

- The workflow begins with a drafted skill patch that has not yet been validated.
- Review separates prompt interpretation, rendered media quality, and repository payload risk.
- Validation must include an isolated pi run before a skill is treated as done.
- Failed visual critiques feed back into a patch step instead of being hidden in notes.
- Publication is allowed only after source preservation, media metrics, and payload checks pass.

Preserve these visual anchors:

- Six lifecycle states must be visible from left to right.
- Three transition guards must appear above the main lifecycle path.
- A rollback path must return from execution toward review.
- A compensation path must restore the invariant before republishing.
- Terminal states must be separated from the main execution state.
- A moving token must traverse the lifecycle path.
- Recovery motion must be distinct from the success path.
- The review caption must state why guards are separate from states.

Preserve these lifecycle states exactly:

- drafted
- reviewed
- validated
- patched
- promoted
- published

Preserve these transition guards exactly:

- source guard
- quality gate
- payload check

Format requirements:

- Duration: 12 seconds.
- Frame rate: 12 fps.
- Resolution: 1280x720.

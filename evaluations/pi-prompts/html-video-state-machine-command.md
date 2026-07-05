# Isolated HTML Video State-Machine Scaffold Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

First action: read `../prompt.md` directly. Then run this command exactly:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/state-machine-video/artifacts/reviews/prompt-contract-build.json
```

Do not ask for clarification. Do not open `build_standalone_explainer.py` manually; the wrapper is responsible for deriving and running the helper.

Required exact video package outputs:

- `projects/state-machine-video/source/source-package.json`
- `projects/state-machine-video/source/production-notes.md`
- `projects/state-machine-video/src/index.html`
- `projects/state-machine-video/src/render.mjs`
- `projects/state-machine-video/artifacts/video-renders/draft/videos/state-machine-lifecycle.mp4`
- `projects/state-machine-video/artifacts/video-renders/draft/review/state-machine-lifecycle-contact-sheet.jpg`
- `projects/state-machine-video/artifacts/video-renders/draft/review/state-machine-lifecycle-contact-sheet.json`
- `projects/state-machine-video/artifacts/reviews/self-review.md`

The wrapper report must be written at `projects/state-machine-video/artifacts/reviews/prompt-contract-build.json`.

Topic: payment workflow lifecycle state machine.

Video title: Payment Lifecycle State Machine.

Checked date: July 4, 2026.

Use the `state-machine` scaffold. The final MP4 basename must be `state-machine-lifecycle`, and the shared project root must be `projects/state-machine-video`.

Preserve these source facts in `source-package.json`:

- Payment workflow states should be explicit rather than hidden inside one processor step.
- Schema and policy guards must run before execution commits side effects.
- Execution can fail after authorization and should not jump straight to success.
- Rollback and compensation paths restore invariants after a partial failure.
- Terminal states separate completed work from parked or failed work.

Preserve these visual anchors:

- lifecycle states
- guarded transition
- schema guard
- policy guard
- execution state
- rollback path
- compensation path
- terminal state

Use 12 seconds, 12 fps, and 1280x720. Before final response, inspect the wrapper report, contact-sheet JSON manifest, source package, and self-review. Both JSON reports must have `"passed": true`, and the wrapper report must show no missing facts or anchors plus matching media values.

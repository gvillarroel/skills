# Isolated HTML Video Comparison-Matrix Scaffold Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

First action: read `../prompt.md` directly. Then run this command exactly:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/comparison-matrix-video/artifacts/reviews/prompt-contract-build.json
```

Do not ask for clarification. Do not open `build_standalone_explainer.py` manually; the wrapper is responsible for deriving and running the helper.

Required exact video package outputs:

- `projects/comparison-matrix-video/source/source-package.json`
- `projects/comparison-matrix-video/source/production-notes.md`
- `projects/comparison-matrix-video/src/index.html`
- `projects/comparison-matrix-video/src/render.mjs`
- `projects/comparison-matrix-video/artifacts/video-renders/draft/videos/comparison-matrix-decision.mp4`
- `projects/comparison-matrix-video/artifacts/video-renders/draft/review/comparison-matrix-decision-contact-sheet.jpg`
- `projects/comparison-matrix-video/artifacts/video-renders/draft/review/comparison-matrix-decision-contact-sheet.json`
- `projects/comparison-matrix-video/artifacts/reviews/self-review.md`

The wrapper report must be written at `projects/comparison-matrix-video/artifacts/reviews/prompt-contract-build.json`.

Topic: choosing between three AI video production approaches.

Video title: AI Video Approach Decision Matrix.

Checked date: July 4, 2026.

Use the `comparison-matrix` scaffold. The final MP4 basename must be `comparison-matrix-decision`, and the shared project root must be `projects/comparison-matrix-video`.

Preserve these source facts in `source-package.json`:

- A useful comparison must judge every option against the same criteria.
- The fastest option is not automatically best if quality or risk suffers.
- Score changes should be visible before the recommendation appears.
- A recommendation should explain the tradeoff rather than hide it.
- Guardrails prevent the final choice from becoming a blind ranking.

Preserve these visual anchors:

- option set
- shared criteria
- score bars
- score shift
- tradeoff lens
- recommended option
- risk guardrail
- decision rationale

Use 12 seconds, 12 fps, and 1280x720. Before final response, inspect the wrapper report, contact-sheet JSON manifest, source package, and self-review. Both JSON reports must have `"passed": true`, and the wrapper report must show no missing facts or anchors plus matching media values.

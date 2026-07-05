First action: read the exact file `../prompt.md` with the file-reading tool; do not run any shell command before that.

This is a required artifact-production task, not a reading-only task.

In the isolated workspace, first read the exact file `../prompt.md` with the file-reading tool. Do not read `README.md` as a substitute. Reading `skills/html-d3-anime-video-workflow/SKILL.md` does not satisfy this requirement, and you must not stop after reading the skill file.

The shell in this validation workspace is bash. Do not run PowerShell commands such as `Get-ChildItem`, `Get-Location`, or `Test-Path`; the exact wrapper command below does not require a directory probe.

Use only the copied `skills/html-d3-anime-video-workflow` skill bundle and normal local tools.

After reading `../prompt.md`, run this exact scaffold command from the workspace root:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/comparison-matrix-labeled-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/comparison-matrix-labeled-video/source/source-package.json`
- `projects/comparison-matrix-labeled-video/source/production-notes.md`
- `projects/comparison-matrix-labeled-video/src/index.html`
- `projects/comparison-matrix-labeled-video/src/render.mjs`
- `projects/comparison-matrix-labeled-video/artifacts/video-renders/draft/videos/labeled-comparison-matrix.mp4`
- `projects/comparison-matrix-labeled-video/artifacts/video-renders/draft/review/labeled-comparison-matrix-contact-sheet.jpg`
- `projects/comparison-matrix-labeled-video/artifacts/video-renders/draft/review/labeled-comparison-matrix-contact-sheet.json`
- `projects/comparison-matrix-labeled-video/artifacts/reviews/self-review.md`

The wrapper report must be written to:

- `projects/comparison-matrix-labeled-video/artifacts/reviews/prompt-contract-build.json`

The browser render-state report must be written to:

- `projects/comparison-matrix-labeled-video/artifacts/reviews/render-state-check.json`

The wrapper should derive this state check from the prompt. It must prove `visualPattern=comparison-matrix`, final `criteriaRevealed=4`, monotonic criteria reveal, score-shift, tradeoff, recommendation, and guardrail transitions, preserved option and criterion labels, and `visibleMechanismCount` progression.

Topic: choosing the next video-production skill improvement from three candidate investments.

Video title: Skill Improvement Decision Matrix

Checked date: July 4, 2026

Use the `comparison-matrix` scaffold.

Preserve these source facts exactly in the source package:

- A useful comparison must keep all candidates on the same criteria.
- Generic scorecards hide why one improvement is safer than another.
- Labeling the real options makes the recommendation auditable in the video itself.
- Guardrails prevent a high-scoring automation path from skipping semantic review.
- The recommendation should name the chosen improvement only after evidence is visible.

Preserve these visual anchors exactly in the source package:

- option set
- shared criteria
- score bars
- score shift
- tradeoff lens
- recommended option
- risk guardrail
- decision rationale

Preserve these decision options exactly in the source package and use them as rendered option labels in order:

- new scaffold
- label support
- review gates

Preserve these decision criteria exactly in the source package and use them as rendered criterion labels in order:

- speed
- visual fidelity
- risk control
- reuse value

Use 12 seconds, 12 fps, and 1280x720.

After the command finishes, inspect the wrapper report, the contact-sheet JSON, the source package, and the self-review. Do not overwrite a passing wrapper-generated contact sheet.

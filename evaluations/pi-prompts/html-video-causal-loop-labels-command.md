First action: read the exact file `../prompt.md` with the file-reading tool; do not run any shell command before that.

This is a required artifact-production task, not a reading-only task.

In the isolated workspace, first read the exact file `../prompt.md` with the file-reading tool. Do not read `README.md` as a substitute. Reading `skills/html-d3-anime-video-workflow/SKILL.md` does not satisfy this requirement, and you must not stop after reading the skill file.

The shell in this validation workspace is bash. Do not run PowerShell commands such as `Get-ChildItem` or `Test-Path`; the exact wrapper command below does not require a directory probe.

Use only the copied `skills/html-d3-anime-video-workflow` skill bundle and normal local tools.

After reading `../prompt.md`, run this exact scaffold command from the workspace root:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/causal-loop-labeled-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/causal-loop-labeled-video/source/source-package.json`
- `projects/causal-loop-labeled-video/source/production-notes.md`
- `projects/causal-loop-labeled-video/src/index.html`
- `projects/causal-loop-labeled-video/src/render.mjs`
- `projects/causal-loop-labeled-video/artifacts/video-renders/draft/videos/labeled-causal-loop.mp4`
- `projects/causal-loop-labeled-video/artifacts/video-renders/draft/review/labeled-causal-loop-contact-sheet.jpg`
- `projects/causal-loop-labeled-video/artifacts/video-renders/draft/review/labeled-causal-loop-contact-sheet.json`
- `projects/causal-loop-labeled-video/artifacts/reviews/self-review.md`

The wrapper report must be written to:

- `projects/causal-loop-labeled-video/artifacts/reviews/prompt-contract-build.json`

The browser render-state report must be written to:

- `projects/causal-loop-labeled-video/artifacts/reviews/render-state-check.json`

The wrapper should derive this state check from the prompt. It must prove `visualPattern=causal-loop`, loop, delay, amplifier, damping, side-effect, and intervention transitions, final `visibleMechanismCount=6`, preserved causal labels, and mechanism-count progression.

Topic: mapping a video production improvement loop from critique to reusable skill guidance.

Video title: Critique To Skill Feedback Loop

Checked date: July 4, 2026

Use the `causal-loop` scaffold.

Preserve these source facts exactly in the source package:

- Draft defects become useful only when the critique identifies the underlying mechanism.
- Repeated isolated validation turns one-off fixes into reusable skill guidance.
- A delayed review loop lets weak patterns survive longer than the video itself.
- Motion checks can amplify confidence while still missing causal meaning.
- The leverage point is the moment critique is promoted into the owning skill.

Preserve these visual anchors exactly in the source package:

- cause chain
- reinforcing loop
- delayed effect
- balancing loop
- side effect
- pressure metric
- leverage point
- intervention

Preserve these causal variables exactly in the source package and use them as rendered causal labels in order:

- draft defects
- delayed review
- validation confidence
- reusable guidance
- missed meaning
- skill update

Use 12 seconds, 12 fps, and 1280x720.

After the command finishes, inspect the wrapper report, the contact-sheet JSON, the source package, and the self-review. Do not overwrite a passing wrapper-generated contact sheet.

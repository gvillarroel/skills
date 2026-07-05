First action: read the exact file `../prompt.md` with the file-reading tool; do not run any shell command before that.

This is a required artifact-production task, not a reading-only task.

In the isolated workspace, first read the exact file `../prompt.md` with the file-reading tool. Do not read `README.md` as a substitute. Reading `skills/html-d3-anime-video-workflow/SKILL.md` does not satisfy this requirement, and you must not stop after reading the skill file.

The shell in this validation workspace is bash. Do not run PowerShell commands such as `Get-ChildItem` or `Test-Path`; the exact wrapper command below does not require a directory probe.

Use only the copied `skills/html-d3-anime-video-workflow` skill bundle and normal local tools.

After reading `../prompt.md`, run this exact scaffold command from the workspace root:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/causal-loop-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/causal-loop-video/source/source-package.json`
- `projects/causal-loop-video/source/production-notes.md`
- `projects/causal-loop-video/src/index.html`
- `projects/causal-loop-video/src/render.mjs`
- `projects/causal-loop-video/artifacts/video-renders/draft/videos/causal-loop-intervention.mp4`
- `projects/causal-loop-video/artifacts/video-renders/draft/review/causal-loop-intervention-contact-sheet.jpg`
- `projects/causal-loop-video/artifacts/video-renders/draft/review/causal-loop-intervention-contact-sheet.json`
- `projects/causal-loop-video/artifacts/reviews/self-review.md`

The wrapper report must be written to:

- `projects/causal-loop-video/artifacts/reviews/prompt-contract-build.json`

Topic: explaining why a team keeps shipping brittle AI video drafts and where to intervene.

Video title: AI Video Quality Causal Loop

Checked date: July 4, 2026

Use the `causal-loop` scaffold.

Preserve these source facts exactly in the source package:

- Rushed first drafts create visible defects that should feed back into the next skill update.
- Delayed review makes defects look like isolated mistakes instead of a reinforcing process.
- More automation can amplify quality only if review gates catch the right mechanisms.
- Side effects appear when validation checks motion but misses causal meaning.
- A useful intervention targets the leverage point where critique becomes reusable skill guidance.

Preserve these visual anchors exactly in the source package:

- cause chain
- reinforcing loop
- delayed effect
- balancing loop
- side effect
- pressure metric
- leverage point
- intervention

Use 12 seconds, 12 fps, and 1280x720.

After the command finishes, inspect the wrapper report, the contact-sheet JSON, and the self-review. Do not overwrite a passing wrapper-generated contact sheet.

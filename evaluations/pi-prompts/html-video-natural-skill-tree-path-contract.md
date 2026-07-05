# Isolated HTML Video Natural Skill-Tree Path Contract Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

First action: read `../prompt.md` directly. Do not run directory listings or shell probes before reading it.

Create a standalone skill-tree explainer video package from this prompt. This prompt intentionally does not provide the final helper command; derive the helper arguments from the exact required paths below.

Do not ask for clarification. Do not use title-derived project names. Do not write into the copied skill directory. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash. If you read the standalone helper contract, use the relative path `skills/html-d3-anime-video-workflow/references/standalone-helper-contract.md`, not a constructed absolute path.

Required exact outputs:

- `projects/natural-poe2-skill-tree-video/source/source-package.json`
- `projects/natural-poe2-skill-tree-video/source/production-notes.md`
- `projects/natural-poe2-skill-tree-video/src/index.html`
- `projects/natural-poe2-skill-tree-video/src/render.mjs`
- `projects/natural-poe2-skill-tree-video/artifacts/video-renders/draft/videos/natural-poe2-tree.mp4`
- `projects/natural-poe2-skill-tree-video/artifacts/video-renders/draft/review/natural-poe2-tree-contact-sheet.jpg`
- `projects/natural-poe2-skill-tree-video/artifacts/video-renders/draft/review/natural-poe2-tree-contact-sheet.json`
- `projects/natural-poe2-skill-tree-video/artifacts/reviews/self-review.md`

Topic: Path of Exile 2 passive tree strategy.

Video title: Natural Path of Exile 2 Tree Route.

Checked date: July 4, 2026.

Use the `skill-tree` scaffold. The final MP4 basename must be `natural-poe2-tree`, and the shared project root must be `projects/natural-poe2-skill-tree-video`.

Preserve these source facts in `source-package.json`:

- A Path of Exile 2 passive plan should start from the active skill, playstyle, and class direction instead of chasing isolated nodes.
- Damage and defense checkpoints should both be visible before a route is treated as stable.
- Attribute travel should justify gem or gear requirements rather than consume points as filler.
- Keystones are rule-changing tradeoffs and should be reviewed as costs as well as power.
- Atlas or endgame specialization should stay visually separate from the character build path.

Preserve these visual anchors:

- start location
- travel path
- damage checkpoint
- defense checkpoint
- attribute highway
- keystone tradeoff
- gear requirement
- Atlas layer

Use 12 seconds, 12 fps, and 1280x720. Before final response, inspect the contact-sheet JSON manifest and self-review. The contact-sheet JSON must have `"passed": true`, and `source-package.json` must contain `Keystones` and `Atlas layer`.

Do not run `check_video_outputs.py` with helper arguments such as `--project-root` or `--output-id`; those belong only to `build_standalone_explainer.py`. The evaluation harness verifies the required exact output paths.

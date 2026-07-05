Create a complete standalone HTML video package for a Path of Exile 2 skill-tree strategy explainer. First action: read `../prompt.md` directly with the file-reading tool, not a shell command. No full command is supplied; derive the runnable workflow from the skill's standard exact-output workflow.

Do not ask clarifying questions, do not run directory listings or shell probes before reading the prompt, and do not write into the copied skill directory. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash.

Required exact video package outputs:

- `projects/standard-poe2-tree-video/source/source-package.json`
- `projects/standard-poe2-tree-video/source/production-notes.md`
- `projects/standard-poe2-tree-video/src/index.html`
- `projects/standard-poe2-tree-video/src/render.mjs`
- `projects/standard-poe2-tree-video/artifacts/video-renders/draft/videos/standard-poe2-tree.mp4`
- `projects/standard-poe2-tree-video/artifacts/video-renders/draft/review/standard-poe2-tree-contact-sheet.jpg`
- `projects/standard-poe2-tree-video/artifacts/video-renders/draft/review/standard-poe2-tree-contact-sheet.json`
- `projects/standard-poe2-tree-video/artifacts/reviews/self-review.md`

Write the prompt-contract build report to `projects/standard-poe2-tree-video/artifacts/reviews/prompt-contract-build.json`.

Topic: Path of Exile 2 skill tree route planning.

Video title: Standard POE2 Skill Tree Strategy.

Checked date: July 4, 2026.

Use the `skill-tree` scaffold.

Preserve these source facts:

- Pick the active skill and weapon plan before spending passive points.
- Passive routes should support both damage scaling and survival.
- Attribute travel nodes are useful only when they unlock gear, gems, or nearby clusters.
- Keystones are tradeoffs and should not be treated as free power.
- Atlas passives are a separate late-game layer, not the same route as the character tree.

Preserve these visual anchors:

- active skill start
- notable route
- damage branch
- defense branch
- attribute highway
- keystone tradeoff
- gear requirement checkpoint
- separate Atlas layer

Use 12 seconds, 12 fps, and 1280x720.

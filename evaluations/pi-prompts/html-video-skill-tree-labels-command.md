First action: read the exact file ../prompt.md with the file-reading tool; do not run any shell command before that. After reading it, run the exact wrapper command below immediately; do not list directories, probe the workspace, or use PowerShell-style commands in bash.

Use the bundled html-d3-anime-video-workflow skill to build a deterministic standalone HTML video scaffold.

Run this exact wrapper command from the evaluation workspace:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/skill-tree-labeled-video/artifacts/reviews/prompt-contract-build.json
```

Required exact outputs:

- `projects/skill-tree-labeled-video/source/source-package.json`
- `projects/skill-tree-labeled-video/source/production-notes.md`
- `projects/skill-tree-labeled-video/src/index.html`
- `projects/skill-tree-labeled-video/src/render.mjs`
- `projects/skill-tree-labeled-video/artifacts/video-renders/draft/videos/labeled-skill-tree.mp4`
- `projects/skill-tree-labeled-video/artifacts/video-renders/draft/review/labeled-skill-tree-contact-sheet.jpg`
- `projects/skill-tree-labeled-video/artifacts/video-renders/draft/review/labeled-skill-tree-contact-sheet.json`
- `projects/skill-tree-labeled-video/artifacts/reviews/self-review.md`
- `projects/skill-tree-labeled-video/artifacts/reviews/prompt-contract-build.json`

Additional exact browser-state output:

- `projects/skill-tree-labeled-video/artifacts/reviews/render-state-check.json`

Topic: Path of Exile 2 passive skill tree strategy for early build planning.

Video title: Path of Exile 2 Skill Tree Label Strategy

Checked date: July 4, 2026

Use the `skill-tree` scaffold.

Preserve these source facts:

- The passive route should start from the active skill and playstyle rather than from isolated stat clusters.
- Early support nodes should connect the start to a notable cluster before branch specialization.
- Damage and defense branches should both be visible so the route does not overfit one axis.
- Attribute and gear-fit checks should happen before treating a keystone as free power.
- Atlas passives belong in a separate endgame layer rather than the character build route.

Preserve these visual anchors:

- The main route must grow from the start through early support, notable, attribute, gear, and keystone nodes.
- Damage and defense branches must split from the same notable checkpoint.
- Three bottom meters must track damage, defense, and gear readiness.
- The keystone must appear as a tradeoff node after gear fit.
- Atlas nodes must remain in a separated right-side layer.
- A moving token must travel along the main character route.
- Branch colors must distinguish damage, defense, attributes, tradeoff, and Atlas.
- The closing caption must keep Atlas passives separate from the character build path.

Preserve these tree nodes exactly:

- skill plan
- support
- notable
- damage
- defense
- attrs
- gear fit
- keystone
- bossing
- atlas pts
- maps

Preserve these strategy meters exactly:

- damage plan
- defense check
- gear unlocks

Format requirements:

- Duration: 12 seconds.
- Frame rate: 12 fps.
- Resolution: 1280x720.

After the command finishes, verify the wrapper report. It must show `passed: true`, no findings, no missing source facts, anchors, tree labels, or meter labels, 12.0 seconds, 12 fps, 1280x720 media, and a passing derived `stateCheck` that includes final-state checks including `routeCount=5`, `false->true` transition checks, label containment, monotonic `visibleMechanismCount`, monotonic `routeCount`, at least three distinct route-count values, and `visualPattern=skill-tree`.

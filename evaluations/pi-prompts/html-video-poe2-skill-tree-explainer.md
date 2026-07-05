# Isolated HTML Video Skill Evaluation: Path of Exile 2 Skill Tree Strategy

Use the loaded `html-d3-anime-video-workflow` skill to create a short standalone explainer video.

Task: build a concise visual explanation of the Path of Exile 2 passive skill tree and beginner strategy. The output should teach the viewer how to think about the tree, not prescribe a patch-fragile exact build.

Do not ask for clarification or confirmation. This prompt intentionally supplies enough source facts, duration, format, audience, and exact paths for a draft. If the loaded skill includes an executable standalone explainer helper, use it as the starter path and pass the supplied source facts and anchors into it.

If using a helper command, infer these values from the exact required paths:

- `--project-root projects/poe2-skill-tree-video`
- `--output-id poe2-skill-tree-strategy`

Writing to `projects/poe2-skill-tree-strategy` or any other title-derived directory is a validation failure.

Run this exact scaffold command before final response, then verify the exact required paths:

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/poe2-skill-tree-video --title "Path of Exile 2 Skill Tree Strategy" --topic "Path of Exile 2" --output-id poe2-skill-tree-strategy --checked-date "July 4, 2026" --duration 20 --fps 12 --width 1280 --height 720 --source-url "https://pathofexile2.com/game/passive-skill-tree" --source-url "https://www.pathofexile.com/forum/view-thread/3975218" --source-url "https://www.pathofexile.com/forum/view-thread/3932540" --fact "Checked date: July 4, 2026." --fact "Game/topic: Path of Exile 2." --fact "Official Path of Exile 2 passive tree page exists at https://pathofexile2.com/game/passive-skill-tree, but the page requires JavaScript in a non-browser fetch." --fact "Official Path of Exile 2 0.5.4 patch notes state that the patch adds an Expedition Atlas Passive Skill Tree for Runes of Aldur, and that players earn its Atlas Passive Points by defeating each boss in The Grand Expedition questline." --fact "Official Path of Exile 2 0.5.0 notes state that the Atlas Tree was significantly expanded with over 300 nodes and that completing the fortress maps gives enough passive points to fully allocate the Atlas Tree." --fact "Keep the character passive tree concept distinct from endgame Atlas passive trees. Explain Atlas passives only as a separate late-game specialization layer." --fact "Beginner strategy anchor: choose the active skill/playstyle first, then spend passives to support its damage type, defenses, attributes, and pathing efficiency." --anchor "start location" --anchor "travel path" --anchor "attribute highway" --anchor "small passive cluster" --anchor "notable node" --anchor "keystone tradeoff" --anchor "defensive checkpoint" --anchor "optional specialization layer"
```

Write all generated task files outside the copied skill directory. Use these exact required output paths relative to the workspace:

- `projects/poe2-skill-tree-video/source/source-package.json`
- `projects/poe2-skill-tree-video/source/production-notes.md`
- `projects/poe2-skill-tree-video/src/index.html`
- `projects/poe2-skill-tree-video/src/render.mjs`
- `projects/poe2-skill-tree-video/artifacts/video-renders/draft/videos/poe2-skill-tree-strategy.mp4`
- `projects/poe2-skill-tree-video/artifacts/reviews/self-review.md`

Source facts to preserve:

- Checked date: July 4, 2026.
- Game/topic: Path of Exile 2.
- Official Path of Exile 2 passive tree page exists at `https://pathofexile2.com/game/passive-skill-tree`, but the page requires JavaScript in a non-browser fetch.
- Official Path of Exile 2 0.5.4 patch notes state that the patch adds an Expedition Atlas Passive Skill Tree for Runes of Aldur, and that players earn its Atlas Passive Points by defeating each boss in The Grand Expedition questline.
- Official Path of Exile 2 0.5.0 notes state that the Atlas Tree was significantly expanded with over 300 nodes and that completing the fortress maps gives enough passive points to fully allocate the Atlas Tree.
- Keep the character passive tree concept distinct from endgame Atlas passive trees. Explain Atlas passives only as a separate late-game specialization layer.
- Beginner strategy anchor: choose the active skill/playstyle first, then spend passives to support its damage type, defenses, attributes, and pathing efficiency.
- Strategy anchors to show visually: start location, travel path, attribute highway, small passive cluster, notable node, keystone tradeoff, defensive checkpoint, and optional specialization layer.
- Avoid exact node names, class balance claims, numeric build breakpoints, or "best build" recommendations unless they are explicitly in the supplied facts.

Video requirements:

- Duration: 18 to 24 seconds.
- Format: 1280x720 MP4.
- Draft quality is acceptable, but the video must be nonblank, have meaningful motion, and include at least four visibly different key states.
- Use a deterministic timestamp render function, such as `window.renderConceptFrame(videoId, seconds, options)`, in the HTML.
- Serve or load the HTML in a way that works for frame capture. Avoid external network dependencies during rendering.
- Use visuals as the main explanation. Keep visible explanatory text minimal; short data labels are allowed when needed for a silent draft.
- Use at least three coordinated visual mechanisms, for example route growth, cluster highlighting, defensive meter filling, keystone tradeoff flipping, or Atlas layer separation.
- The MP4 must be created, not only planned.

Review requirements:

- In `self-review.md`, critique the generated video against the skill guidance. Mention at least five concrete strengths or defects.
- Include the exact MP4 path, duration, resolution, and the commands or tools used for rendering/validation.
- Note anything that would need improvement in the skill if this were a first-pass validation run.

Before final response, verify that all required output paths exist and that the MP4 is non-empty.

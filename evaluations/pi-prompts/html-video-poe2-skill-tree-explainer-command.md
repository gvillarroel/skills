# Isolated HTML Video Command Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

Run this command exactly. Do not change `--project-root`, `--output-id`, filenames, or paths.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/poe2-skill-tree-video --title "Path of Exile 2 Skill Tree Strategy" --topic "Path of Exile 2" --output-id poe2-skill-tree-strategy --checked-date "July 4, 2026" --duration 20 --fps 12 --width 1280 --height 720 --source-url "https://pathofexile2.com/game/passive-skill-tree" --source-url "https://www.pathofexile.com/forum/view-thread/3975218" --source-url "https://www.pathofexile.com/forum/view-thread/3932540" --fact "Checked date: July 4, 2026." --fact "Game/topic: Path of Exile 2." --fact "Official Path of Exile 2 passive tree page exists at https://pathofexile2.com/game/passive-skill-tree, but the page requires JavaScript in a non-browser fetch." --fact "Official Path of Exile 2 0.5.4 patch notes state that the patch adds an Expedition Atlas Passive Skill Tree for Runes of Aldur, and that players earn its Atlas Passive Points by defeating each boss in The Grand Expedition questline." --fact "Official Path of Exile 2 0.5.0 notes state that the Atlas Tree was significantly expanded with over 300 nodes and that completing the fortress maps gives enough passive points to fully allocate the Atlas Tree." --fact "Keep the character passive tree concept distinct from endgame Atlas passive trees. Explain Atlas passives only as a separate late-game specialization layer." --fact "Beginner strategy anchor: choose the active skill/playstyle first, then spend passives to support its damage type, defenses, attributes, and pathing efficiency." --anchor "start location" --anchor "travel path" --anchor "attribute highway" --anchor "small passive cluster" --anchor "notable node" --anchor "keystone tradeoff" --anchor "defensive checkpoint" --anchor "optional specialization layer"
```

Before final response, verify these exact paths exist and the MP4 is non-empty:

- `projects/poe2-skill-tree-video/source/source-package.json`
- `projects/poe2-skill-tree-video/source/production-notes.md`
- `projects/poe2-skill-tree-video/src/index.html`
- `projects/poe2-skill-tree-video/src/render.mjs`
- `projects/poe2-skill-tree-video/artifacts/video-renders/draft/videos/poe2-skill-tree-strategy.mp4`
- `projects/poe2-skill-tree-video/artifacts/reviews/self-review.md`

If any exact path is missing, rerun the same command exactly. Do not ask for clarification.

# Isolated HTML Video Skill-Tree Mechanism-State Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

First action: read `../prompt.md` directly. Do not run directory listings or shell probes before reading it.

Read `../prompt.md` directly, then run these commands exactly in order. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash. Do not change paths, filenames, `--output-id`, `--video-id`, or `--pattern`.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/poe2-skill-tree-mechanism-video --title "Path of Exile 2 Skill Tree Mechanism State" --topic "Path of Exile 2 passive tree strategy" --output-id poe2-skill-tree-mechanism --pattern skill-tree --checked-date "July 4, 2026" --duration 12 --fps 12 --width 1280 --height 720 --source-url "local prompt facts" --fact "A Path of Exile 2 passive plan should start from the active skill, playstyle, and class direction instead of chasing isolated nodes." --fact "Damage and defense checkpoints should both be visible before a route is treated as stable." --fact "Attribute travel should justify gem or gear requirements rather than consume points as filler." --fact "Keystones are rule-changing tradeoffs and should be reviewed as costs as well as power." --fact "Atlas or endgame specialization should stay visually separate from the character build path." --anchor "start location" --anchor "travel path" --anchor "damage checkpoint" --anchor "defense checkpoint" --anchor "attribute highway" --anchor "keystone tradeoff" --anchor "gear requirement" --anchor "Atlas layer"
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/capture_html_video.py --html projects/poe2-skill-tree-mechanism-video/src/index.html --output projects/poe2-skill-tree-mechanism-video/artifacts/video-renders/draft/videos/poe2-skill-tree-mechanism-browser.mp4 --video-id poe2-skill-tree-mechanism --duration 12 --fps 4 --width 1280 --height 720 --manifest projects/poe2-skill-tree-mechanism-video/artifacts/reviews/skill-tree-capture-manifest.json --expect-state visualPattern=skill-tree --expect-state sourceFacts=5 --expect-state damageBranchVisible=true --expect-state defenseBranchVisible=true --expect-state keystoneVisible=true --expect-state atlasVisible=true --expect-state visibleMechanismCount=5 --min-distinct-state routeCount=4 --min-distinct-state visibleMechanismCount=3
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/make_video_contact_sheet.py --video projects/poe2-skill-tree-mechanism-video/artifacts/video-renders/draft/videos/poe2-skill-tree-mechanism-browser.mp4 --output projects/poe2-skill-tree-mechanism-video/artifacts/reviews/skill-tree-contact-sheet.jpg --manifest projects/poe2-skill-tree-mechanism-video/artifacts/reviews/skill-tree-contact-sheet.json --samples 8 --columns 4 --thumb-width 320 --label-times --min-tile-color-buckets 12 --min-tile-nonbackground-ratio 0.015 --min-consecutive-change-ratio 0.002 --min-changing-pairs 4 --max-low-change-pairs 3
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_video_outputs.py --require projects/poe2-skill-tree-mechanism-video/source/source-package.json --require projects/poe2-skill-tree-mechanism-video/src/index.html --require projects/poe2-skill-tree-mechanism-video/artifacts/video-renders/draft/videos/poe2-skill-tree-mechanism.mp4 --require projects/poe2-skill-tree-mechanism-video/artifacts/video-renders/draft/review/poe2-skill-tree-mechanism-contact-sheet.jpg --require projects/poe2-skill-tree-mechanism-video/artifacts/video-renders/draft/videos/poe2-skill-tree-mechanism-browser.mp4 --require projects/poe2-skill-tree-mechanism-video/artifacts/reviews/skill-tree-contact-sheet.jpg --require-json-passed projects/poe2-skill-tree-mechanism-video/artifacts/video-renders/draft/review/poe2-skill-tree-mechanism-contact-sheet.json --require-json-passed projects/poe2-skill-tree-mechanism-video/artifacts/reviews/skill-tree-capture-manifest.json --require-json-passed projects/poe2-skill-tree-mechanism-video/artifacts/reviews/skill-tree-contact-sheet.json --require-text projects/poe2-skill-tree-mechanism-video/source/source-package.json::Keystones --report projects/poe2-skill-tree-mechanism-video/artifacts/reviews/output-contract-report.json
```

Before final response, inspect the capture manifest, both contact-sheet manifests, and output contract report. All JSON reports must have `"passed": true`. The capture manifest must prove `damageBranchVisible`, `defenseBranchVisible`, `keystoneVisible`, and `atlasVisible` each reached `true`; `visibleMechanismCount` must reach `5`; `routeCount` must have at least four distinct values. If any exact path is missing, rerun the commands exactly. Do not ask for clarification.

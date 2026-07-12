# Production Notes — Holiday 2026: Geek, Tech, Anime, Games, Comics & Vinyl

## Concept Claim

The ranked source evidence should let a family choose a child-permitted, culture-first option without reading all candidates first.

## Chosen Visual Metaphor

A route marker travels from the Brassfield home reference through ranked evidence and returns to the complete Excel planner.

## Production Files

- Final MP4: `artifacts/videos/06-geek-tech-anime-games-comics-vinyl.mp4`
- Contact sheet: `artifacts/reviews/contact-sheet.jpg`
- Motion report: `artifacts/reviews/motion-report.json`
- Audio report: `artifacts/reviews/audio-report.json`
- Pattern blueprint: `source/pattern-blueprint.json`
- Source, renderer and review contracts live under `source/`, `src/`, and `artifacts/`.

Source images: 8 acquired through the image-first Playwright workflow; 0 source-bound fallback cards were required. Every image, method, URL and fallback is recorded in `artifacts/reviews/source-capture-log.json`.

Audio: VoxCPM2 neural narration from a project-generated synthetic voice anchor, plus a procedural harmonic bed, sidechain ducking and gentle seam ticks, normalized to a 48-second 48 kHz stereo master.

## Render State Contract

`renderConceptFrame` exposes `activeBeat`, `sceneId`, `activeCompositionId`, `activeAssetIds`, `sourceProofAssetIds`, `visibleMechanismCount`, transition visibility, output visibility and the final callback state. Visible DOM media carries matching asset paths and SHA-256 digests.

## Command Working Directory

Command working directory: project root. Package-relative paths use `source/`, `src/`, and `artifacts/`.

## Validation Commands

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/select_video_patterns.py --title "Holiday 2026" --promise "Family planning" --format "compressed explainer" --runtime "0:48" --output source/pattern-blueprint.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py source/brief.md --min-beats 8 --require-voiceover --min-voiceover-lines 8 --require-source-links --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/06-geek-tech-anime-games-comics-vinyl.mp4 --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output artifacts/reviews/asset-composition-validation.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 48 --require-all-brief-beats --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --require-visual-ids --output artifacts/reviews/renderer-contract.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/render_concept_video.py src/index.html artifacts/videos/06-geek-tech-anime-games-comics-vinyl.mp4 --brief source/brief.md --require-all-brief-beats --duration 48 --fps 30 --capture-fps 6 --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --audio-file artifacts/audio/final-audio.m4a --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_artifact.py artifacts/videos/06-geek-tech-anime-games-comics-vinyl.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 48 --duration-tolerance 0.7 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --brief source/brief.md --video artifacts/videos/06-geek-tech-anime-games-comics-vinyl.mp4 --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --require-source-links --output artifacts/reviews/readiness-score.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output artifacts/reviews/style-fidelity.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_production_package.py --brief source/brief.md --video artifacts/videos/06-geek-tech-anime-games-comics-vinyl.mp4 --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --require-voiceover --require-source-links --require-production-notes --require-package-manifest --require-pattern-blueprint --require-style-fidelity-report --require-renderer-beat-coverage --require-contact-sheet --require-motion-report --min-readiness-score 18 --min-style-fidelity-score 12 --expect-duration 48 --duration-tolerance 0.7 --require-final-review-notes --json
```

## Visual Review

- Renderer contract passed: yes; 14 sampled states in ../artifacts/reviews/renderer-contract.json
- Readiness score: 22/24 ready; no weak categories; report ../artifacts/reviews/readiness-score.json
- Contact sheet inspected: ../artifacts/reviews/contact-sheet.jpg generated (140059 bytes); approved visual review ../artifacts/reviews/visual-review.json.
- Asset quality check: 8/8 declared assets are ready; producer skills ['d3-animated-svg', 'playwright']; hash-bound report ../artifacts/reviews/asset-composition-validation.json.
- Composition check: 8 scenes use 8 composition families and 8 armatures; report ../artifacts/reviews/asset-composition-validation.json.
- Renderer asset-binding check: visible asset coverage=True, manifest binding=True, composition coverage=True, observed assets=8; report ../artifacts/reviews/renderer-contract.json.
- Legibility check: contact sheet and sampled frames passed nonblank quality review in ../artifacts/reviews/quality-report.json.
- Beat coverage check: all sampled brief beats covered by renderer state in ../artifacts/reviews/renderer-contract.json.
- Visual mechanism check: reported visual pattern; final visibleMechanismCount=8; output/final callback visible=true/true.
- Pacing/transition check: yes; motion changing pairs 38, subtle pairs 48; quality samples 6; reports ../artifacts/reviews/motion-report.json and ../artifacts/reviews/quality-report.json.
- Source-binding check: declared asset IDs, scene uses, visible DOM IDs, and reviewed frames agree in ../artifacts/reviews/asset-composition-validation.json.
- Motion/quality checks passed: yes; motion changing pairs 38, subtle pairs 48; quality samples 6; reports ../artifacts/reviews/motion-report.json and ../artifacts/reviews/quality-report.json
- Audio sync check: final audio ready; duration coverage True; report ../artifacts/reviews/audio-report.json
- Final audio duration checked: final audio ready; duration coverage True; report ../artifacts/reviews/audio-report.json
- Known caveats: final audio is listed; review any project-specific footage, source, or rights limitations separately.

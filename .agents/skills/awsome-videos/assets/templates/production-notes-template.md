# <Project Title> Production Notes

## Design Note

Concept claim:

Chosen visual metaphor:

Rejected metaphors:

Visual vocabulary:

Timing contract:

## Production Files

- Brief:
- Pattern blueprint:
- Source package:
- Shot contract:
- Asset manifest:
- Composition plan:
- Transition plan:
- Renderer/storyboard:
- Audio:
- Voiceover cues:
- Final MP4:
- Silent preview:
- Contact sheet:
- Motion report:
- Audio report:
- Renderer contract report:
- Readiness score:
- Review reports:
- Visual review:
- Visual contract report:

## Render State Contract

Required states:

- `activeBeat`
- `visualPattern`
- `visibleMechanismCount`
- `hookVisible`
- `sourceProofVisible`
- `transitionVisible`
- `warningVisible`
- `outputVisible`

Final state expectations:

- Core mechanism visible:
- Final callback visible:
- Audio present:
- Final audio duration covered:

## Validation Commands

Command working directory: project root, the folder that contains `source/`, `src/`, and `artifacts/`.

Brief:

```powershell
uv run --script {{SKILL_PATH}}/scripts/select_video_patterns.py --title "What Is X?" --runtime 1:10 --output source/pattern-blueprint.json --json
uv run --script {{SKILL_PATH}}/scripts/check_video_brief.py source/brief.md --require-voiceover --require-source-links --json
uv run --script {{SKILL_PATH}}/scripts/extract_voiceover_cues.py source/brief.md --format json --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.json
uv run --script {{SKILL_PATH}}/scripts/extract_voiceover_cues.py source/brief.md --format srt --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.srt
uv run --script {{SKILL_PATH}}/scripts/extract_voiceover_cues.py source/brief.md --format csv --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.csv
uv run --script {{SKILL_PATH}}/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output artifacts/reviews/style-fidelity.json --json
```

Replace source placeholders with concrete URLs or domains before running source-backed validation commands.
For publishable audio, add `--audio-file` to the render command, add `--require-final-audio` to video, readiness, and package commands, and add `paths.finalAudio` to `source/package-manifest.json`; the audio report must show `finalAudioReady: true`, `placeholderAudio: false`, and `finalAudioDurationOk: true`.

Visual contract:

```powershell
uv run --script {{SKILL_PATH}}/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/final.mp4 --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output artifacts/reviews/asset-composition-validation.json --json
uv run --script {{SKILL_PATH}}/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 70 --require-all-brief-beats --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --require-visual-ids --screenshot-dir artifacts/reviews/renderer-frames --output artifacts/reviews/renderer-contract.json --json
```

Video:

```powershell
uv run --script {{SKILL_PATH}}/scripts/render_concept_video.py src/index.html artifacts/videos/final.mp4 --brief source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --json
uv run --script {{SKILL_PATH}}/scripts/check_video_artifact.py artifacts/videos/final.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
```

Package:

```powershell
uv run --script {{SKILL_PATH}}/scripts/score_video_readiness.py --require-source-links --brief source/brief.md --video artifacts/videos/final.mp4 --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --require-visual-contract-report --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --output artifacts/reviews/readiness-score.json --json
uv run --script {{SKILL_PATH}}/scripts/finalize_production_notes.py source/production-notes.md --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --audio-report artifacts/reviews/audio-report.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --json
uv run --script {{SKILL_PATH}}/scripts/check_production_package.py --require-source-links --brief source/brief.md --video artifacts/videos/final.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer --forbid-scaffold-renderer --require-renderer-report --require-renderer-beat-coverage --require-renderer-visual-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet --require-motion-report --output artifacts/reviews/package-validation.json --json
```

Visual review:

- Renderer contract passed:
- Readiness score:
- Contact sheet inspected:
- Asset quality check:
- Composition check:
- Renderer asset-binding check:
- Legibility check:
- Beat coverage check:
- Visual mechanism check:
- Pacing/transition check:
- Source-binding check:
- Audio sync check:
- Motion/quality checks passed:
- Final audio duration checked:
- Known caveats:

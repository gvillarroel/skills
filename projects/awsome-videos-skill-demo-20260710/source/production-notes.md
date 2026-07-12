# Una skill convierte a Codex en especialista — Production Notes

## Design Note

Concept claim: A reusable Codex skill turns repeated prompt baggage into an on-demand operational package with scoped instructions, specialist assets, and validation.

Chosen visual metaphor: Eight fixed-frame semantic workbenches transform repeated instruction sheets into a recognizable red SKILL packet, open only the required reference, coordinate resource roles, route a visual need, block a defective artifact, compare active context, and reactivate across projects.

Rejected metaphors: An abstract systems canvas, detached proof windows, anonymous moving boxes, text-only slides, generic stock footage, decorative logo storms, soft-corner dashboard cards, and invented token-savings percentages.

Visual vocabulary: Tonal grayscale work surfaces, one persistent red SKILL packet with a folded white corner and SKILL label, eight original semantic SVGs, eight named composition families, recognizable technical objects, causal motion verbs, and local Spanish functional labels.

Timing contract: Eight source-bound beats cover exactly 70 seconds; each scene has a recognizable input, causal action, visible result, readable hold, mechanism emphasis, and semantic seam handoff.

## Production Files

- Brief: `source/brief.md`
- Pattern blueprint: `source/pattern-blueprint.json`
- Source package: `source/source-package.json`
- Shot contract: `source/shot-contract.json`
- Asset manifest: `source/asset-manifest.json`
- Composition plan: `source/composition-plan.json`
- Transition plan: `source/transition-plan.json`
- Renderer/storyboard: `src/index.html` and `src/storyboard.md`
- Audio: `artifacts/audio/final-mix.wav`
- Voiceover cues: `artifacts/audio/voiceover-cues.json`
- Final MP4: `artifacts/videos/skill-convierte-codex-especialista.mp4`
- Contact sheet: `artifacts/reviews/contact-sheet.jpg`
- Motion report: `artifacts/reviews/motion-report.json`
- Audio report: `artifacts/reviews/audio-report.json`
- Renderer contract report: `artifacts/reviews/renderer-contract.json`
- Readiness score: `artifacts/reviews/readiness-score.json`
- Style fidelity score: `artifacts/reviews/style-fidelity.json`
- Visual review: `artifacts/reviews/visual-review.json`
- Visual contract report: `artifacts/reviews/asset-composition-validation.json`
- Final package report: `artifacts/reviews/package-validation.json`

## Render State Contract

Required states returned by `window.renderConceptFrame`:

- `activeBeat`
- `sceneId`
- `activeCompositionId`
- `activeAssetIds`
- `visualPattern`
- `visibleMechanismCount`
- `hookVisible`
- `sourceProofVisible`
- `transitionVisible`
- `warningVisible`
- `outputVisible`

Final state expectations:

- Core mechanism visible: `visibleMechanismCount` remains above zero in every sampled scene.
- Final callback visible: the final sampled state reports the reusable-workflow output and callback.
- Asset binding visible: each scene exposes the exact manifest asset ID, source path, and SHA-256 on a loaded visual element.
- Audio present: the final MP4 contains the rights-safe Spanish narration mix.
- Final audio duration covered: `audio-report.json` reports `finalAudioReady=true`, `placeholderAudio=false`, and `finalAudioDurationOk=true` for 70 seconds.

## Validation Commands

Command working directory: project root, the folder that contains `source/`, `src/`, and `artifacts/`.

Brief and style:

```powershell
uv run --script ../../.agents/skills/awsome-videos/scripts/select_video_patterns.py --title "Una skill convierte a Codex en especialista" --promise "Show how a reusable Codex skill turns repeated prompt baggage into an on-demand, validated workflow." --format "compressed explainer" --runtime "70 seconds" --output source/pattern-blueprint.json --json
uv run --script ../../.agents/skills/awsome-videos/scripts/check_video_brief.py source/brief.md --require-voiceover --require-source-links --json
uv run --script ../../.agents/skills/awsome-videos/scripts/extract_voiceover_cues.py source/brief.md --format json --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.json
uv run --script ../../.agents/skills/awsome-videos/scripts/extract_voiceover_cues.py source/brief.md --format srt --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.srt
uv run --script ../../.agents/skills/awsome-videos/scripts/extract_voiceover_cues.py source/brief.md --format csv --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.csv
uv run --script ../../.agents/skills/awsome-videos/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output artifacts/reviews/style-fidelity.json --json
```

Visual contract and renderer:

```powershell
uv run --script ../../.agents/skills/awsome-videos/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/skill-convierte-codex-especialista.mp4 --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output artifacts/reviews/asset-composition-validation.json --json
uv run --script ../../.agents/skills/awsome-videos/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 70 --require-all-brief-beats --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --require-visual-ids --output artifacts/reviews/renderer-contract.json --json
```

Video and audio:

```powershell
uv run --script ../../.agents/skills/awsome-videos/scripts/render_concept_video.py src/index.html artifacts/videos/skill-convierte-codex-especialista.mp4 --brief source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --audio-file artifacts/audio/final-mix.wav --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --json
uv run --script ../../.agents/skills/awsome-videos/scripts/check_video_artifact.py artifacts/videos/skill-convierte-codex-especialista.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
```

Readiness and package:

```powershell
uv run --script ../../.agents/skills/awsome-videos/scripts/score_video_readiness.py --require-source-links --brief source/brief.md --video artifacts/videos/skill-convierte-codex-especialista.mp4 --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --require-visual-contract-report --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --require-final-audio --output artifacts/reviews/readiness-score.json --json
uv run --script ../../.agents/skills/awsome-videos/scripts/check_production_package.py --require-source-links --brief source/brief.md --video artifacts/videos/skill-convierte-codex-especialista.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-final-audio --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer --forbid-scaffold-renderer --require-renderer-report --require-renderer-beat-coverage --require-renderer-visual-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet --require-motion-report --output artifacts/reviews/package-validation.json --json
```

## Visual Review

- Renderer contract passed: yes; 14 sampled states in artifacts\reviews\renderer-contract.json
- Readiness score: 24/24 ready; no weak categories; report artifacts\reviews\readiness-score.json
- Contact sheet inspected: artifacts\reviews\contact-sheet.jpg generated (115437 bytes); approved visual review artifacts\reviews\visual-review.json.
- Asset quality check: 8/8 declared assets are ready; producer skills ['d3-animated-svg']; hash-bound report artifacts\reviews\asset-composition-validation.json.
- Composition check: 8 scenes use 8 composition families and 8 armatures; report artifacts\reviews\asset-composition-validation.json.
- Renderer asset-binding check: visible asset coverage=True, manifest binding=True, composition coverage=True, observed assets=8; report artifacts\reviews\renderer-contract.json.
- Legibility check: contact sheet and sampled frames passed nonblank quality review in artifacts\reviews\quality-report.json.
- Beat coverage check: all sampled brief beats covered by renderer state in artifacts\reviews\renderer-contract.json.
- Visual mechanism check: `semantic-skill-workflow` is visible across all eight scenes; 8/8 three-second muted tests identify a familiar object, causal action, and result, and the final hold shows the ready-state callback across four project surfaces.
- Pacing/transition check: yes; motion changing pairs 55, subtle pairs 68; quality samples 6; reports artifacts\reviews\motion-report.json and artifacts\reviews\quality-report.json.
- Source-binding check: declared asset IDs, scene uses, visible DOM IDs, and reviewed frames agree in artifacts\reviews\asset-composition-validation.json.
- Motion/quality checks passed: yes; motion changing pairs 55, subtle pairs 68; quality samples 6; reports artifacts\reviews\motion-report.json and artifacts\reviews\quality-report.json
- Audio sync check: final audio ready; duration coverage True; report artifacts\reviews\audio-report.json
- Final audio duration checked: final audio ready; duration coverage True; report artifacts\reviews\audio-report.json
- Known caveats: no third-party footage or stock media is present; the Spanish neural narration and procedural audio are project-generated, and the visuals are explanatory rather than quantitative measurements.

# Una skill convierte a Codex en especialista — Production Notes

## Design Note

Concept claim: A reusable Codex skill turns repeated prompt baggage into an on-demand operational package with scoped instructions, specialist assets, and validation.

Chosen visual metaphor: A continuous hard-edge megacanvas transforms a prompt wall into a compact SKILL.md package, opens only the required resource, routes work to specialists, crosses a validation gate, and returns as a reusable hub.

Rejected metaphors: Text-only slides, generic stock footage, decorative logo storms, rounded dashboard cards, invented token-savings percentages, and one repeated picture-in-picture placement.

Visual vocabulary: Tonal grayscale system geometry, a persistent red handoff edge, eight original SVG mechanism proofs, four materially distinct proof layouts, square modules, camera reframes, and local Spanish functional labels.

Timing contract: Eight source-bound beats cover exactly 70 seconds; each scene has an entrance, readable hold, mechanism emphasis, and seam handoff.

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
uv run --script ../../.agents/skills/awsome-videos/scripts/check_production_package.py --require-source-links --brief source/brief.md --video artifacts/videos/skill-convierte-codex-especialista.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-final-audio --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer --forbid-scaffold-renderer --require-renderer-report --require-renderer-beat-coverage --require-renderer-visual-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet --require-motion-report --json
```

## Visual Review

- Renderer contract passed: 14 sampled states cover all eight beats, assets, and compositions; the browser report is current for the final renderer and composition-plan hashes.
- Readiness score: 24/24 ready with no weak categories.
- Contact sheet inspected: the final six-frame sheet and the eight-scene review sheet are nonblank, balanced, and free of cross-tile label overflow.
- Asset quality check: 8/8 original SVG assets are ready, structurally valid, source-bound, rights-declared, SHA-256 verified, and backed by producer reports.
- Composition check: eight scene-specific armatures and four materially distinct evidence layouts passed safe-area, hierarchy, square-edge, and zero-padding contracts.
- Renderer asset-binding check: visible asset coverage, exact manifest-resource loading, composition coverage, and all eight observed asset IDs passed.
- Legibility check: 53 full-resolution scene and seam frames were reviewed against the final MP4; functional labels remain inside the safe area with no outline, overlap, or clipping.
- Beat coverage check: all eight narration beats and all eight declared scene, composition, and asset IDs cover the full 70-second runtime.
- Visual mechanism check: prompt pressure, SKILL.md packaging, progressive disclosure, resource roles, specialist routing, validation, context-on-demand, and the reusable callback each have a distinct proof asset and state change.
- Pacing/transition check: motion review passed with 67 changing pairs and 70 subtle-changing pairs; all seven seams have unique before, midpoint, and after evidence while preserving the red handoff edge.
- Source-binding check: manifest IDs, asset paths, SHA-256 values, producer reports, scene uses, visible DOM bindings, and reviewed frames agree in the final visual-contract report.
- Audio sync check: the final 70-second rights-safe mix is muxed as 48 kHz stereo AAC and aligns with the eight narration cue windows.
- Motion/quality checks passed: motion and quality reports both pass with no findings; the final MP4 is 1280x720 H.264 at 30 fps.
- Final audio duration checked: source duration is 70.0 seconds, `finalAudioReady=true`, `placeholderAudio=false`, and `finalAudioDurationOk=true`.
- Known caveats: narration is synthetic Spanish speech; all visuals, music-bed synthesis, and sound effects are project-generated, with no third-party footage or copyrighted music.

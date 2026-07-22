# What is an LLM? Production Notes

## Design Note

Concept claim: Explain a large language model as a prediction engine that turns text into tokens, scores the next token, and repeats that loop until an answer appears.

Chosen visual metaphor: LLM as visible state movement through large, language, model, prediction.

Rejected metaphors: decorative logo storm, generic magic imagery, and text-only slides.

Visual vocabulary: source/input surface, LLM state surface, proof/output surface, warning path, final callback.

Timing contract: 8 beats over 70s, one visible change every 6-10 seconds, final callback visible.

## Production Files

- Brief: source/brief.md
- Pattern blueprint: source/pattern-blueprint.json and source/pattern-blueprint.md
- Renderer/storyboard: src/index.html and src/storyboard.md
- Audio: artifacts/audio/final-narration-70s.wav
- Voiceover cues: artifacts/audio/voiceover-cues.json, artifacts/audio/voiceover-cues.srt, artifacts/audio/voiceover-cues.csv
- Final MP4: artifacts/videos/what-is-a-llm.mp4
- Silent preview: artifacts/videos/what-is-a-llm-silent-preview.mp4 optional
- Contact sheet: artifacts/reviews/contact-sheet.jpg
- Motion report: artifacts/reviews/motion-report.json
- Audio report: artifacts/reviews/audio-report.json
- Renderer contract report: artifacts/reviews/render-state.json
- Readiness score: artifacts/reviews/readiness-score.json
- Style fidelity score: artifacts/reviews/style-fidelity.json
- Review reports: artifacts/reviews/

## Render State Contract

Required states: `window.renderConceptFrame` must return the fields below.

- `activeBeat`
- `visualPattern`
- `visibleMechanismCount`
- `hookVisible`
- `sourceProofVisible`
- `transitionVisible`
- `warningVisible`
- `outputVisible`

Final state expectations:

- Core mechanism visible: `visibleMechanismCount` stays above zero in sampled states.
- Final callback visible: final sampled state reports `finalCallbackVisible=true`.
- Audio present: final MP4 contains the final narration track.
- Final audio duration covered: `audio-report.json` has `finalAudioReady=true`, `placeholderAudio=false`, and `finalAudioDurationOk=true`.

## Validation Commands

Command working directory: project root, the folder that contains `source/`, `src/`, and `artifacts/`.

Brief: source/brief.md

```powershell
uv run --script ../../skills/awsome-videos/scripts/select_video_patterns.py --title "What is an LLM?" --promise "Explain a large language model as a prediction engine that turns text into tokens, scores the next token, and repeats that loop until an answer appears." --format "compressed explainer" --runtime "1:10" --output source/pattern-blueprint.json --json
uv run --script ../../skills/awsome-videos/scripts/check_video_brief.py source/brief.md --require-voiceover --require-source-links --json
uv run --script ../../skills/awsome-videos/scripts/extract_voiceover_cues.py source/brief.md --format json --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.json
```

Video:

```powershell
uv run --script ../../skills/awsome-videos/scripts/render_concept_video.py src/index.html artifacts/videos/what-is-a-llm.mp4 --brief source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --force --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --audio-file artifacts/audio/final-narration-70s.wav --final-audio-duration-tolerance 1 --json
uv run --script ../../skills/awsome-videos/scripts/check_video_artifact.py artifacts/videos/what-is-a-llm.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
```

Package:

```powershell
uv run --script ../../skills/awsome-videos/scripts/score_video_readiness.py --require-source-links --brief source/brief.md --video artifacts/videos/what-is-a-llm.mp4 --renderer-report artifacts/reviews/render-state.json --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --require-final-audio --output artifacts/reviews/readiness-score.json --json
uv run --script ../../skills/awsome-videos/scripts/score_style_fidelity.py --require-source-links --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --output artifacts/reviews/style-fidelity.json --json
uv run --script ../../skills/awsome-videos/scripts/check_production_package.py --require-source-links --brief source/brief.md --video artifacts/videos/what-is-a-llm.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --renderer src/index.html --renderer-report artifacts/reviews/render-state.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-final-audio --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-renderer --require-renderer-report --require-renderer-beat-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet --require-motion-report --json
```

Visual review:

- Renderer contract passed: render-state report passed, sampled frames were nonblank, and all 10 brief beats were covered.
- Readiness score: artifacts/reviews/readiness-score.json
- Style fidelity score: 16/16 with no penalties; source proof is backed by Google ML Crash Course and AWS LLM references while the visuals remain generated diagrams.
- Contact sheet inspected: automated nonblank contact-sheet validation passed.
- Legibility check: title, terminal prompt, token bars, warning overlay, and final mechanism labels are readable in the sampled contact sheet.
- Beat coverage check: render-state report has `briefBeatCoverageOk=true` and sampled beats 1-10.
- Visual mechanism check: prompt/context, model layers, token probability bars, and repeat loop stay visible as the definition advances.
- Pacing/transition check: hard cuts, panel builds, warning overlay, and final callback change the visual state every 6-10 seconds.
- Source-binding check: generated diagrams map to the brief's Google ML Crash Course and AWS LLM source links; no external footage is implied.
- Audio sync check: final narration covers the full 70s runtime and the renderer capture manifest uses 840 sampled frames at `captureFps=12`.
- Motion/quality checks passed: motion and quality reports passed.
- Final audio duration checked: `sourceDurationSeconds=70.0`, `finalAudioDurationOk=true`.
- Known caveats: source visuals are generated for this concept demo; no external footage was used.

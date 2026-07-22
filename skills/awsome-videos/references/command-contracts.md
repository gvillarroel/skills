# Command Contracts

Set $env:AWSOME_VIDEOS_SKILL; run from project root.

## Preflight And Scaffold

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_runtime_tools.py --require-render-tools --json
~~~

Passing text starts with `PASS awsome-videos runtime preflight`; omit render tools for plan-only work.

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/scaffold_production_package.py projects/my-video --title "What Is X?" --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/select_video_patterns.py --title "What Is X?" --promise "Explain X with one mechanism, proof, and limitation." --runtime 1:10 --output projects/my-video/source/pattern-blueprint.json --json
~~~

The scaffold creates the visual-contract files but remains a wireframe.

## Brief, Voiceover, And Style

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py projects/my-video/source/brief.md --require-voiceover --require-source-links --json
~~~

`PASS awsome-videos brief` requires concrete source links and no missing/generic/thin/duplicate fields.

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/extract_voiceover_cues.py projects/my-video/source/brief.md --format json --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output projects/my-video/artifacts/audio/voiceover-cues.json
~~~

Passing JSON has "ok": true, enough cueCount, and beatCueMismatches: [].

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief projects/my-video/source/brief.md --pattern-blueprint projects/my-video/source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output projects/my-video/artifacts/reviews/style-fidelity.json --json
~~~

Passing text starts with PASS awsome-videos style fidelity; JSON has no penalties or weak categories and scores at least 12/16.

## Asset And Composition Gate

Create assets, apply scene-composition-director, inspect frames, correct issues, then run:

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest projects/my-video/source/asset-manifest.json --composition-plan projects/my-video/source/composition-plan.json --visual-review projects/my-video/artifacts/reviews/visual-review.json --video projects/my-video/artifacts/videos/final.mp4 --brief projects/my-video/source/brief.md --project-root projects/my-video --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output projects/my-video/artifacts/reviews/asset-composition-validation.json --json
~~~

Require current hashes, ready assets, complete seams, approved evidence, and zero blockers.

## Renderer Binding And Render

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/create_concept_renderer.py projects/my-video/source/brief.md projects/my-video/src/index.html --force --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_renderer_contract.py projects/my-video/src/index.html --brief projects/my-video/source/brief.md --duration 70 --require-all-brief-beats --asset-manifest projects/my-video/source/asset-manifest.json --composition-plan projects/my-video/source/composition-plan.json --require-visual-ids --screenshot-dir projects/my-video/artifacts/reviews/renderer-frames --output projects/my-video/artifacts/reviews/renderer-contract.json --json
~~~

Passing output proves briefBeatCoverageOk, visualAssetCoverageOk, and compositionCoverageOk through DOM and renderer-state IDs.

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/render_concept_video.py projects/my-video/src/index.html projects/my-video/artifacts/videos/final.mp4 --brief projects/my-video/source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --force --contact-sheet projects/my-video/artifacts/reviews/contact-sheet.jpg --quality-report projects/my-video/artifacts/reviews/quality-report.json --motion-report projects/my-video/artifacts/reviews/motion-report.json --capture-manifest projects/my-video/artifacts/reviews/capture-manifest.json --render-state-report projects/my-video/artifacts/reviews/render-state.json --audio-report projects/my-video/artifacts/reviews/audio-report.json --json
~~~

Passing render JSON has a 30 fps MP4, captureFps: 12, reports, and briefBeatCoverageOk: true.

## MP4, Readiness, And Notes

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_artifact.py projects/my-video/artifacts/videos/final.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --require-audio --audio-report projects/my-video/artifacts/reviews/audio-report.json --require-audio-report --contact-sheet projects/my-video/artifacts/reviews/contact-sheet.jpg --quality-report projects/my-video/artifacts/reviews/quality-report.json --motion-report projects/my-video/artifacts/reviews/motion-report.json --capture-manifest projects/my-video/artifacts/reviews/capture-manifest.json --json
~~~

Passing text starts with PASS awsome-videos video. Add --require-final-audio for publishable delivery; finalAudioDurationOk must be true.

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --require-source-links --brief projects/my-video/source/brief.md --video projects/my-video/artifacts/videos/final.mp4 --renderer projects/my-video/src/index.html --renderer-report projects/my-video/artifacts/reviews/renderer-contract.json --asset-manifest projects/my-video/source/asset-manifest.json --composition-plan projects/my-video/source/composition-plan.json --visual-review projects/my-video/artifacts/reviews/visual-review.json --visual-contract-report projects/my-video/artifacts/reviews/asset-composition-validation.json --require-visual-contract-report --quality-report projects/my-video/artifacts/reviews/quality-report.json --motion-report projects/my-video/artifacts/reviews/motion-report.json --capture-manifest projects/my-video/artifacts/reviews/capture-manifest.json --audio-report projects/my-video/artifacts/reviews/audio-report.json --contact-sheet projects/my-video/artifacts/reviews/contact-sheet.jpg --require-voiceover --output projects/my-video/artifacts/reviews/readiness-score.json --json
~~~

Finished-video visual/source scores are capped without this evidence. Passing JSON has at least 18/24 and no weakCategories.

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/finalize_production_notes.py projects/my-video/source/production-notes.md --renderer-report projects/my-video/artifacts/reviews/renderer-contract.json --readiness-report projects/my-video/artifacts/reviews/readiness-score.json --contact-sheet projects/my-video/artifacts/reviews/contact-sheet.jpg --quality-report projects/my-video/artifacts/reviews/quality-report.json --motion-report projects/my-video/artifacts/reviews/motion-report.json --audio-report projects/my-video/artifacts/reviews/audio-report.json --visual-review projects/my-video/artifacts/reviews/visual-review.json --visual-contract-report projects/my-video/artifacts/reviews/asset-composition-validation.json --json
~~~

Final notes need substantive structured visual and audio checks.

## Final Package

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_production_package.py --require-source-links --brief projects/my-video/source/brief.md --video projects/my-video/artifacts/videos/final.mp4 --design-note projects/my-video/source/design-note.md --production-notes projects/my-video/source/production-notes.md --package-manifest projects/my-video/source/package-manifest.json --pattern-blueprint projects/my-video/source/pattern-blueprint.json --asset-manifest projects/my-video/source/asset-manifest.json --composition-plan projects/my-video/source/composition-plan.json --visual-review projects/my-video/artifacts/reviews/visual-review.json --visual-contract-report projects/my-video/artifacts/reviews/asset-composition-validation.json --renderer projects/my-video/src/index.html --renderer-report projects/my-video/artifacts/reviews/renderer-contract.json --readiness-report projects/my-video/artifacts/reviews/readiness-score.json --style-fidelity-report projects/my-video/artifacts/reviews/style-fidelity.json --contact-sheet projects/my-video/artifacts/reviews/contact-sheet.jpg --quality-report projects/my-video/artifacts/reviews/quality-report.json --motion-report projects/my-video/artifacts/reviews/motion-report.json --capture-manifest projects/my-video/artifacts/reviews/capture-manifest.json --audio-report projects/my-video/artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer --forbid-scaffold-renderer --require-renderer-report --require-renderer-beat-coverage --require-renderer-visual-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet --require-motion-report --output projects/my-video/artifacts/reviews/package-validation.json --json
~~~

PASS awsome-videos package reruns browser renderer/readiness and binds loaded assets plus fresh frames to the MP4.

## Maintenance

~~~powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/test_validators.py --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_reference_completeness.py --json
~~~

Both return "ok": true. Maintenance proves positive and negative visual-contract fixtures, runtime/package behavior, corpus provenance, compact references, and command coverage.

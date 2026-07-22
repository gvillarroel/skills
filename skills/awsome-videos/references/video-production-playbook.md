# Video Production Playbook

Use this for actual video, production package, renderer, contact sheet, or MP4 validation. Keep work source-bound: the visual mechanism must explain the technical claim, not decorate it. Follow this ownership chain: source freeze -> specialist asset routing -> asset acquisition/generation -> per-scene composition -> semantic transitions -> one renderer owner -> frame review -> correction/rerender -> final validation.

Before running command examples, set `$env:AWSOME_VIDEOS_SKILL` to this skill directory in the current workspace.

## Production Sequence

1. Before browser rendering or MP4 validation, run the runtime preflight:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_runtime_tools.py --require-render-tools --json
   ```

   Passing JSON includes `"ok": true`, `checks.uv.ok: true`, `checks.requiredFiles.ok: true`, `checks.ffmpeg.ok: true`, and `checks.ffprobe.ok: true`. For plan-only work, omit `--require-render-tools`.
2. For a new package, create the standard layout with:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/scaffold_production_package.py projects/<project-id> --title "What Is X?" --json
   ```

   Use `--force` only when intentionally overwriting scaffolded text files.
3. Use `source/pattern-blueprint.json` from the scaffolder, or regenerate it with `scripts/select_video_patterns.py`, before writing the brief.
4. Create or update a brief from `assets/templates/brief-template.md` when useful. Replace starter voiceover lines; `--require-voiceover` rejects placeholders and repeated filler. For source-backed work, replace generic source notes with concrete URLs/domains and validate with `--require-source-links`.
5. Validate the brief before building:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py path/to/brief.md --require-voiceover --json
   ```

   Add `--require-source-links` when the source plan must be auditable. Passing JSON should include `source_link_count` above zero and empty `source_link_failures`.

6. Extract voiceover cues when the brief is ready for recording, subtitles, or audio-mix timing:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/extract_voiceover_cues.py path/to/brief.md --format json --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output path/to/artifacts/audio/voiceover-cues.json
   ```

   Passing JSON includes `"ok": true`, enough `cueCount`, `beatCueMismatches: []`, and `finalCueEndSeconds` within tolerance. Generate `--format srt` and `--format csv` too whenever the package manifest declares those handoff paths.

7. Read `references/visual-asset-composition-workflow.md` and finish the visual preflight before coding final visuals:
   - Use `source-to-video-director` to freeze facts and stable shot IDs for source-backed or finished work.
   - Record every real or generated asset in `source/asset-manifest.json`; route raster work to `imagegen`, conventional diagrams to Mermaid, custom mechanisms/data geometry to D3, charts to ECharts, and meaningful depth to Three.js.
   - Use `scene-composition-director` for every multi-scene final video and `scene-transition-director` for adjacent cuts. Preserve `bNN`, `sNN`, asset IDs, and composition IDs end to end.
   - Run `scripts/check_visual_contract.py` without final-review flags as a structural preflight. Do not implement the final renderer while seams, asset ownership, or scene composition are unresolved.
   Write a short design note with:
   - Concept claim.
   - Chosen visual metaphor.
   - Rejected metaphors and why.
   - Visual vocabulary.
   - Timing contract.
8. If using a browser renderer, create a deterministic starter from the brief only as a wireframe:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/create_concept_renderer.py `
     projects/<project-id>/source/brief.md `
     projects/<project-id>/src/index.html `
     --force `
     --json
   ```

   `create_concept_renderer.py` and its template contain `AWSOME_SCAFFOLD_WIREFRAME`; they cannot pass a finished package unchanged.
9. Choose exactly one renderer owner and implement the video. Prefer `html-d3-anime-video-workflow` for complex browser explainers; use Slidev or Manim only when their delivery surface fits better. Prefer deterministic frame rendering:
   - A browser renderer should expose `window.renderConceptFrame(videoId, seconds, options)` and return state values.
   - A frame/video renderer should sample exact timestamps, not depend on wall-clock animation timing.
   - A storyboard-only package should still specify exact shot timing, assets, and validation gates.
10. Validate the renderer contract before encoding. Final renderers must expose visible DOM markers plus state fields for active asset and composition IDs:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_renderer_contract.py `
     projects/<project-id>/src/index.html `
      --brief projects/<project-id>/source/brief.md `
      --asset-manifest projects/<project-id>/source/asset-manifest.json `
      --composition-plan projects/<project-id>/source/composition-plan.json `
      --duration 70 `
      --require-all-brief-beats `
      --require-visual-ids `
      --screenshot-dir projects/<project-id>/artifacts/reviews/renderer-frames `
      --output projects/<project-id>/artifacts/reviews/renderer-contract.json `
     --json
   ```

   Passing proves every brief beat has renderer state coverage plus pixel evidence; screenshots need enough luminance variation and color diversity to avoid blank-frame false positives.

11. For a deterministic HTML renderer, render MP4, contact sheet, audio report, motion report, capture manifest, quality report, and render-state report with:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/render_concept_video.py `
     projects/<project-id>/src/index.html `
     projects/<project-id>/artifacts/videos/final.mp4 `
     --brief projects/<project-id>/source/brief.md `
     --require-all-brief-beats `
     --duration 70 `
     --fps 30 `
     --capture-fps 12 `
     --force `
     --contact-sheet projects/<project-id>/artifacts/reviews/contact-sheet.jpg `
     --quality-report projects/<project-id>/artifacts/reviews/quality-report.json `
     --motion-report projects/<project-id>/artifacts/reviews/motion-report.json `
     --capture-manifest projects/<project-id>/artifacts/reviews/capture-manifest.json `
     --render-state-report projects/<project-id>/artifacts/reviews/render-state.json `
     --audio-report projects/<project-id>/artifacts/reviews/audio-report.json `
     --json
   ```

   Keep `--fps` as the final encoded MP4 frame rate. Use `--capture-fps 12` for faster deterministic screenshot capture unless the motion genuinely needs per-frame 30 fps capture.
12. Add audio as production roles: voiceover, bed, ducking, hits, ticks, risers, whooshes, dropout, final tail. Synthetic validation audio is only for previews. Publishable work passes `--require-final-audio`; `audio-report.json` needs `sourceDurationSeconds` and `finalAudioDurationOk: true`, and `package-manifest.json` needs project-root-relative `paths.finalAudio`.
13. Inspect the contact sheet, first/hold/emphasis/final scene frames, before/midpoint/after seam frames, and full-speed playback. Write `artifacts/reviews/visual-review.json`, correct every failed scene, rerender, and run `check_visual_contract.py` with `--require-ready-assets --require-specialist-routing --require-reviewed-scenes`; it re-extracts representative MP4 frames for pixel comparison. Final review needs concrete asset-quality, composition, and renderer-binding findings.
14. Validate the final MP4 with `scripts/check_video_artifact.py` and available visual/motion checks.
15. Score style fidelity/readiness and finalize production notes. Add `--require-source-links` to both scoring commands for source-backed or publishable briefs:

   ```powershell
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py `
     --brief projects/<project-id>/source/brief.md `
     --pattern-blueprint projects/<project-id>/source/pattern-blueprint.json `
     --require-voiceover `
     --require-pattern-blueprint `
     --output projects/<project-id>/artifacts/reviews/style-fidelity.json `
     --json
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py `
     --brief projects/<project-id>/source/brief.md `
     --video projects/<project-id>/artifacts/videos/final.mp4 `
     --renderer projects/<project-id>/src/index.html `
     --renderer-report projects/<project-id>/artifacts/reviews/renderer-contract.json `
     --asset-manifest projects/<project-id>/source/asset-manifest.json `
     --composition-plan projects/<project-id>/source/composition-plan.json `
     --visual-review projects/<project-id>/artifacts/reviews/visual-review.json `
     --visual-contract-report projects/<project-id>/artifacts/reviews/asset-composition-validation.json `
     --require-visual-contract-report `
     --quality-report projects/<project-id>/artifacts/reviews/quality-report.json `
     --motion-report projects/<project-id>/artifacts/reviews/motion-report.json `
     --capture-manifest projects/<project-id>/artifacts/reviews/capture-manifest.json `
     --audio-report projects/<project-id>/artifacts/reviews/audio-report.json `
     --contact-sheet projects/<project-id>/artifacts/reviews/contact-sheet.jpg `
     --require-voiceover `
     --output projects/<project-id>/artifacts/reviews/readiness-score.json `
     --json
   uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/finalize_production_notes.py `
     projects/<project-id>/source/production-notes.md `
     --renderer-report projects/<project-id>/artifacts/reviews/renderer-contract.json `
     --readiness-report projects/<project-id>/artifacts/reviews/readiness-score.json `
     --contact-sheet projects/<project-id>/artifacts/reviews/contact-sheet.jpg `
     --quality-report projects/<project-id>/artifacts/reviews/quality-report.json `
     --motion-report projects/<project-id>/artifacts/reviews/motion-report.json `
     --audio-report projects/<project-id>/artifacts/reviews/audio-report.json `
     --json
   ```

16. Validate the full handoff with `scripts/check_production_package.py` when source plus MP4 are present. Finished work must add the asset manifest, composition plan, visual review, visual-contract report, `--require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer-visual-coverage --forbid-scaffold-renderer`. Add `--require-source-links` for source-backed publishable videos.

## Project Layout

Use a project folder when creating artifacts:

```text
projects/<project-id>/
├── source/
│   ├── brief.md
│   ├── design-note.md
│   ├── asset-manifest.json
│   ├── composition-plan.json
│   ├── production-notes.md
│   └── package-manifest.json
├── src/
│   ├── index.html
│   └── storyboard.md
└── artifacts/
    ├── videos/
    ├── audio/
    ├── reviews/              # visual-review.json, renderer/visual contract reports, frames
    └── images/
```

Keep generated media and frame dumps under `artifacts/`.

The scaffolder creates `source/package-manifest.json` with relative paths and validation commands. Update it if final filenames change.
The scaffolded `src/index.html` is deterministic. Replace generic visuals with source-bound code, UI, docs, diagrams, or captures, but preserve `window.renderConceptFrame`.
The scaffolded source-link text is a placeholder. Replace it with concrete URLs or domains before using `--require-source-links`.

## Deterministic Renderer Contract

For browser/SVG/Canvas renderers, return state that can prove coverage:

```js
return {
  videoId,
  activeBeat: beatIndex + 1,
  sceneId: "s01",
  activeCompositionId: "s01",
  activeAssetIds: ["a01-source-proof"],
  sourceProofAssetIds: ["a01-source-proof"],
  visualPattern: "mechanism-name",
  visibleMechanismCount,
  hookVisible,
  sourceProofVisible,
  transitionVisible,
  warningVisible,
  outputVisible
};
```

Use monotonic counters for coverage checks. Final state should show the core mechanism and final callback.
`check_renderer_contract.py` samples screenshots in addition to state. If a renderer returns valid state but paints blank or nearly blank frames, fix the visual layer before encoding.

## Short Explainer Timing

Use a visible change every 6-10 seconds:

- 0:00-0:05: cold claim and first proof visual.
- 0:05-0:20: compressed definition.
- 0:20-0:45: core mechanism.
- 0:45-1:05: practical example or contrast.
- 1:05-end: limitation, warning, or callback.

For a 60-90 second demo, use 8-10 timed beats and keep every beat visually distinct.

## MP4 Validation

Validate stream properties and optional reports:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_artifact.py `
  projects/<project-id>/artifacts/videos/final.mp4 `
  --expect-width 1280 `
  --expect-height 720 `
  --expect-fps 30 `
  --expect-duration 70 `
  --duration-tolerance 1 `
  --require-audio `
  --audio-report projects/<project-id>/artifacts/reviews/audio-report.json `
  --require-audio-report `
  --contact-sheet projects/<project-id>/artifacts/reviews/contact-sheet.jpg `
  --quality-report projects/<project-id>/artifacts/reviews/quality-report.json `
  --motion-report projects/<project-id>/artifacts/reviews/motion-report.json `
  --capture-manifest projects/<project-id>/artifacts/reviews/capture-manifest.json
```

Passing validation proves container basics only. Inspect the contact sheet for legibility, pacing, source binding, audio sync evidence, and whether visuals explain the claim.
With `--require-audio`, ffmpeg `volumedetect` runs; silent AAC streams fail. Use `--skip-audio-level-check` only for intentionally silent previews.
With `--require-final-audio`, the validator also requires `audio-report.json` to show `finalAudioReady=true`, `placeholderAudio=false`, and `finalAudioDurationOk=true`.
For a complete handoff, include final audio as `paths.finalAudio`; package validation checks the file and command flags.
When `--contact-sheet` is supplied, `check_video_artifact.py` also opens the image and fails tiny or nearly blank sheets using width, height, luminance-variation, and color-diversity checks.

For a tiny smoke MP4, encode with visible bitrate or pass `--min-size-bytes 1`. Do not relax size for final deliverables.

## Package Validation

Use one command when the handoff includes source notes and a video:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_production_package.py `
  --brief projects/<project-id>/source/brief.md `
  --video projects/<project-id>/artifacts/videos/final.mp4 `
  --design-note projects/<project-id>/source/design-note.md `
  --production-notes projects/<project-id>/source/production-notes.md `
  --package-manifest projects/<project-id>/source/package-manifest.json `
  --pattern-blueprint projects/<project-id>/source/pattern-blueprint.json `
  --asset-manifest projects/<project-id>/source/asset-manifest.json `
  --composition-plan projects/<project-id>/source/composition-plan.json `
  --visual-review projects/<project-id>/artifacts/reviews/visual-review.json `
  --visual-contract-report projects/<project-id>/artifacts/reviews/asset-composition-validation.json `
  --renderer projects/<project-id>/src/index.html `
  --renderer-report projects/<project-id>/artifacts/reviews/renderer-contract.json `
  --readiness-report projects/<project-id>/artifacts/reviews/readiness-score.json `
  --style-fidelity-report projects/<project-id>/artifacts/reviews/style-fidelity.json `
  --contact-sheet projects/<project-id>/artifacts/reviews/contact-sheet.jpg `
  --quality-report projects/<project-id>/artifacts/reviews/quality-report.json `
  --motion-report projects/<project-id>/artifacts/reviews/motion-report.json `
  --capture-manifest projects/<project-id>/artifacts/reviews/capture-manifest.json `
  --audio-report projects/<project-id>/artifacts/reviews/audio-report.json `
  --expect-width 1280 `
  --expect-height 720 `
  --expect-fps 30 `
  --expect-duration 70 `
  --duration-tolerance 1 `
  --min-style-fidelity-score 12 `
  --require-audio `
  --require-audio-report `
  --require-voiceover `
  --require-design-note `
  --require-production-notes `
  --require-package-manifest `
  --require-pattern-blueprint `
  --require-visual-contract `
  --require-ready-assets `
  --require-specialist-routing `
  --require-source-routing `
  --require-reviewed-scenes `
  --require-renderer `
  --forbid-scaffold-renderer `
  --require-renderer-report `
  --require-renderer-beat-coverage `
  --require-renderer-visual-coverage `
  --require-readiness-report `
  --require-style-fidelity-report `
  --require-final-review-notes `
  --require-contact-sheet `
  --require-motion-report `
  --output projects/<project-id>/artifacts/reviews/package-validation.json
```

Expected passing output starts with `PASS awsome-videos package`; JSON requires `"ok": true`.
Readiness reports must meet `--min-readiness-score`, report `readiness: "ready"`, and have no `weakCategories` unless `--allow-weak-readiness` is deliberate. Style reports must meet `--min-style-fidelity-score` and have empty `penalties`.
Renderer reports need `briefBeatCoverageOk: true` with `--require-renderer-beat-coverage`.
For completed handoffs, run `scripts/finalize_production_notes.py` and use `--require-final-review-notes` so production notes cannot still say pending, TBD, not run, or unfinished.
The final review gate also requires non-thin structured `Legibility check`, `Beat coverage check`, `Visual mechanism check`, `Pacing/transition check`, `Source-binding check`, `Audio sync check`, and `Known caveats` lines.
For scaffolded handoffs, use `--require-pattern-blueprint` so selected taxonomy has visual, animation, transition, audio, script, and beat guidance.
For source-backed packages, add `--require-source-links`; nested brief JSON must report concrete links and no failures.
For publishable audio, add `--require-final-audio`; manifest JSON must report `finalAudioExists: true` and empty `missingFinalAudioCommandTerms`.

## Finished Handoff

Report:

- Final MP4 path.
- Pattern blueprint, source brief, design note, asset manifest, composition plan, production notes, and package manifest paths.
- Renderer or storyboard path.
- Audio report path and whether it proves final audio, duration coverage, or only placeholder validation audio.
- Final audio source path from `paths.finalAudio` when the package uses `--require-final-audio`.
- Contact sheet path.
- Approved visual review and hash-bound asset/composition validation report paths.
- Motion report path.
- Readiness score and weakest categories.
- Commands run and pass/fail results.
- Package validation result when source and video are both present.
- Any known caveat, such as synthetic voiceover or missing live footage.

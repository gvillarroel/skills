# Holiday 2026 Video Package Validation Requirements

This checklist applies to `projects/holiday2026/video-packages/10-sports-live-games`. Run every command from that package root. The target is a source-backed, 70-second, 1280×720, 30 fps package with final narration/music/SFX—not validation-tone audio.

## Current scaffold blockers

- `source/brief.md` still contains angle-bracket placeholders and generic narration. The current brief validator fails on zero concrete source links; its other checks are not proof that the placeholder prose is publishable.
- `source/source-package.json` has an empty promise, `status: "planned"`, null source URLs, unverified rights, and planned verification. All eight shots are also planned.
- All eight assets are planned, missing on disk, and have null hashes. `a01` still uses a `replace.invalid` URL. All seven `skillRouting` entries are planned and their proof reports are absent.
- `src/index.html` is the starter: it contains `AWSOME_SCAFFOLD_WIREFRAME`, sets `window.AWSOME_SCAFFOLD_WIREFRAME = true`, returns `activeCompositionId: null`, and returns empty `activeAssetIds` and `sourceProofAssetIds`. Removing the marker alone is insufficient; package validation also detects structural similarity to the starter.
- `artifacts/reviews/visual-review.json` is pending, has no evidence frames or transition reviews, has a null candidate-video hash, and has an unresolved blocker.
- `source/package-manifest.json` has no `paths.finalAudio`. Its render, video-validation, readiness, and package-validation commands lack the final-audio flags.
- `source/production-notes.md` still contains `pending` review lines and commands without final-audio flags. These words are rejected by the final-review gate.

## Required files

All paths must be project-root-relative. Every path declared in `source/package-manifest.json` must exist before the final package gate, except the `packageValidation` report being written by that command.

- Source and renderer:
  - `source/brief.md`
  - `source/source-package.json`
  - `source/shot-contract.json`
  - `source/design-note.md`
  - `source/production-notes.md`
  - `source/pattern-blueprint.json`
  - `source/pattern-blueprint.md`
  - `source/asset-manifest.json`
  - `source/composition-plan.json`
  - `source/transition-plan.json`
  - `source/package-manifest.json`
  - `src/index.html`
  - `src/storyboard.md`
- Declared visual assets:
  - `artifacts/images/a01-source-proof.png`
  - `artifacts/images/a02-definition-diagram.svg`
  - `artifacts/images/a03-mechanism-input.svg`
  - `artifacts/images/a04-state-mechanism.svg`
  - `artifacts/images/a05-output-proof.png`
  - `artifacts/images/a06-contrast-mechanism.svg`
  - `artifacts/images/a07-rule-summary.svg`
  - `artifacts/images/a08-callback-system.svg`
- Audio, captions, and video:
  - `artifacts/audio/final-mix.wav` (recommended `paths.finalAudio`)
  - `artifacts/audio/voiceover-cues.json`
  - `artifacts/audio/voiceover-cues.srt`
  - `artifacts/audio/voiceover-cues.csv`
  - `artifacts/videos/holiday-2026-sports-live-games.mp4`
- Render and final-validation evidence:
  - `artifacts/reviews/contact-sheet.jpg`
  - `artifacts/reviews/renderer-contract.json`
  - `artifacts/reviews/render-state.json`
  - `artifacts/reviews/quality-report.json`
  - `artifacts/reviews/motion-report.json`
  - `artifacts/reviews/capture-manifest.json`
  - `artifacts/reviews/audio-report.json`
  - `artifacts/reviews/visual-review.json`
  - `artifacts/reviews/asset-composition-validation.json`
  - `artifacts/reviews/style-fidelity.json`
  - `artifacts/reviews/readiness-score.json`
  - `artifacts/reviews/package-validation.json`
  - Every scene and seam evidence image named in `visual-review.json`.
- Asset producer reports:
  - `artifacts/reviews/a01-source-proof-validation.json`
  - `artifacts/reviews/a02-definition-diagram-validation.json`
  - `artifacts/reviews/a03-mechanism-input-validation.json`
  - `artifacts/reviews/a04-state-mechanism-validation.json`
  - `artifacts/reviews/a05-output-proof-validation.json`
  - `artifacts/reviews/a06-contrast-mechanism-validation.json`
  - `artifacts/reviews/a07-rule-summary-validation.json`
  - `artifacts/reviews/a08-callback-system-validation.json`
- Route proof reports:
  - `artifacts/reviews/source-contract-validation.json`
  - `artifacts/reviews/composition-plan-specialist-validation.json`
  - `artifacts/reviews/transition-plan-specialist-validation.json`
  - `artifacts/reviews/asset-generation-validation.json`
  - `artifacts/reviews/mermaid-assets-validation.json`
  - `artifacts/reviews/asset-capture-validation.json`
  - `artifacts/reviews/renderer-route-validation.json`

## Required fields and markers

- Brief:
  - Keep populated values on the same line as `Promise:`, `Audience:`, `Format:`, `Runtime:`, `Cold-open line:`, `First visual:`, and `Audio cue:`; remove every angle-bracket placeholder.
  - Keep at least eight `bNN`/`sNN` timed rows with `Time | Beat ID | Scene ID | Script purpose | Visual | Animation | Transition | Audio`.
  - Keep one concrete utterance per line as `- M:SS-M:SS: narration`; no template filler or duplicate narration.
  - Include concrete source URLs/domains plus the hook, visual source plan, animation/transitions, music/SFX, voiceover, and evaluation sections.
- Source contracts:
  - `source-package.json`: schema version 1; nonempty promise/audience; frozen/ready/verified status; exactly eight `fNN` facts with matching beat/time, substantive claim, concrete non-placeholder `sourceUrl`, accepted `rightsStatus`, and complete/frozen/verified `verificationStatus`.
  - `shot-contract.json`: version 1; exactly eight `sNN` shots with matching `beatId`, time, substantive `job` and `viewerTask`, nonempty `assetIds` and `sourceFactIds`, and approved/complete/frozen/ready/verified status. Every fact must be covered exactly by the matching shot.
- Assets and routing:
  - Each asset requires stable `id`, `kind`, concrete `claim`, project-relative `output`, current 64-character SHA-256, `origin {type, uri, rightsStatus, attribution}`, `producer {skill, method, report}`, technical crop/size fields, one or more `uses {sceneId, beatId, role, fit}`, at least three substantive `qualityChecks`, and `status` of `ready`, `verified`, or `approved`.
  - Accepted rights values are `fair-use`, `licensed`, `official-source`, `owned`, `project-generated`, `public-domain`, or `user-provided`. Captured/external assets need a real HTTP(S) URL and attribution where required.
  - Each producer report requires schema version 1, `ok: true` or `passed: true`, matching `assetId`, `skill`, `output`, and `sha256`, plus at least three structured checks with `name`, `method`, and `finding`.
  - Each completed `skillRouting` proof requires schema version 1, passing status, matching `stage`, `skill`, and `output`, and an `artifacts` list whose project-relative paths and hashes exactly match `outputPaths`. Use `fallbackReason` for a skipped route. Source, composition, transitions, and exactly one renderer owner must be complete.
- Composition and transitions:
  - Keep exactly one composition scene per rendered `sNN`, with matching beat/asset IDs, safe zones, text bounds, focal hierarchy, two rejected alternatives, two anchors, normalized `objectBounds` with a meaningful focal object, entrance/hold/emphasis/exit phases, reduced-motion intent, validation checks/contracts, and outgoing seam data.
  - Use materially different geometry across scenes. Eight scenes require seven adjacent transitions `s01__s02` through `s07__s08`, with matching times, persistent element, semantic state change, attention handoff, and before/midpoint/after proof.
- Renderer:
  - Replace the scaffold composition, not merely its marker. Keep `window.renderConceptFrame(videoId, seconds, options)`.
  - Visible media must carry matching `data-asset-id`, `data-asset-src`, and `data-asset-sha256` and must load the declared file. Composition objects need `data-object-id`.
  - Returned state must truthfully provide `activeBeat`, `sceneId`, `activeCompositionId`, `activeAssetIds`, and `sourceProofAssetIds`. It must agree with the visible DOM and current manifests.
- Visual review:
  - Bind current manifest/composition digests and `candidateVideo {path, sha256}`; set full-speed playback reviewed.
  - Each of eight scenes needs exactly four unique, hash-bound, in-scene frames in increasing `first < hold < emphasis < final` order; all eight checks—`focalClarity`, `safeAreas`, `clipping`, `overlap`, `contrast`, `typography`, `silentComprehension`, and `sourceProof`—must be `pass`.
  - Each scene needs a substantive three-second-or-less `silentTest {object, action, result}`, finding/correction text, and `status: "approved"`.
  - Each adjacent transition needs exactly `before`, `midpoint`, and `after` frames, substantive finding, and `status: "pass"`. Finish with `unresolvedBlockers: []` and `overallStatus: "approved"`.
- Final audio and reports:
  - Add `"finalAudio": "artifacts/audio/final-mix.wav"` to `package-manifest.json.paths`. The file must exist and cover at least 69 seconds for the 70-second target with a one-second tolerance.
  - Render with `--audio-file`. `audio-report.json` must show `finalAudioReady: true`, `placeholderAudio: false`, `finalAudioDurationOk: true`, a real source path/hash, and the final video hash.
  - Renderer validation must report `ok`, `briefBeatCoverageOk`, `visualAssetCoverageOk`, and `compositionCoverageOk` as true.
  - Visual-contract, style, readiness, and package reports must be current and passing. Readiness must be at least 18/24, `readiness: "ready"`, with no weak categories; style fidelity must be at least 12/16 with no penalties.
  - Final production notes must contain substantive lines for `Asset quality check`, `Composition check`, `Renderer asset-binding check`, `Legibility check`, `Beat coverage check`, `Visual mechanism check`, `Pacing/transition check`, `Source-binding check`, `Audio sync check`, and `Known caveats`. Do not leave `pending`, `TBD`, `TODO`, `not run`, `unfinished`, or thin values such as “ok.”

## Recommended command order

Set the skill path once:

```powershell
$env:AWSOME_VIDEOS_SKILL = (Resolve-Path '../../../../skills/awsome-videos').Path
```

1. Preflight, then finish source contracts and replace all scaffold prose:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_runtime_tools.py --require-render-tools --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/select_video_patterns.py --title "Holiday 2026: Sports & Live Games" --promise "Compare family-friendly Georgia sports and live-game options by distance, cost, timing, and child fit." --format "compressed explainer" --runtime "1:10" --output source/pattern-blueprint.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/select_video_patterns.py --title "Holiday 2026: Sports & Live Games" --promise "Compare family-friendly Georgia sports and live-game options by distance, cost, timing, and child fit." --format "compressed explainer" --runtime "1:10" --output source/pattern-blueprint.md --markdown
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_brief.py source/brief.md --require-voiceover --require-source-links --json
```

2. Export every declared cue format and score the final brief:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/extract_voiceover_cues.py source/brief.md --format json --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/extract_voiceover_cues.py source/brief.md --format srt --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.srt
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/extract_voiceover_cues.py source/brief.md --format csv --min-cues 8 --expect-duration 70 --duration-tolerance 1 --require-beat-match --output artifacts/audio/voiceover-cues.csv
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_style_fidelity.py --brief source/brief.md --pattern-blueprint source/pattern-blueprint.json --require-voiceover --require-pattern-blueprint --require-source-links --output artifacts/reviews/style-fidelity.json --json
```

3. Produce and hash real assets, route proofs, composition, and transitions. Run structural visual preflight before implementing final visuals:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --json
```

4. Replace the wireframe renderer and validate renderer/DOM binding:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_renderer_contract.py src/index.html --brief source/brief.md --duration 70 --require-all-brief-beats --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --require-visual-ids --screenshot-dir artifacts/reviews/renderer-frames --output artifacts/reviews/renderer-contract.json --json
```

5. Create `artifacts/audio/final-mix.wav`, add it to the manifest, update the four command strings that require final-audio terms, then render:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/render_concept_video.py src/index.html artifacts/videos/holiday-2026-sports-live-games.mp4 --brief source/brief.md --require-all-brief-beats --duration 70 --fps 30 --capture-fps 12 --force --audio-file artifacts/audio/final-mix.wav --final-audio-duration-tolerance 1 --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --render-state-report artifacts/reviews/render-state.json --audio-report artifacts/reviews/audio-report.json --json
```

6. Inspect full-resolution scene holds, transition midpoints, the contact sheet, muted playback, and full-speed playback. Correct failures and rerender. Only then write approved evidence and run the hash-bound visual gate:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_visual_contract.py --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --video artifacts/videos/holiday-2026-sports-live-games.mp4 --brief source/brief.md --project-root . --min-assets 8 --min-scenes 8 --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --output artifacts/reviews/asset-composition-validation.json --json
```

7. Validate the MP4 and final audio, then compute readiness:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_video_artifact.py artifacts/videos/holiday-2026-sports-live-games.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --require-audio --audio-report artifacts/reviews/audio-report.json --require-audio-report --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --json
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/score_video_readiness.py --require-source-links --brief source/brief.md --video artifacts/videos/holiday-2026-sports-live-games.mp4 --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --require-visual-contract-report --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --require-final-audio --contact-sheet artifacts/reviews/contact-sheet.jpg --require-voiceover --output artifacts/reviews/readiness-score.json --json
```

8. Replace all pending review prose, keep each `uv run --script` command on one line in production notes, and finalize the notes:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/finalize_production_notes.py source/production-notes.md --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --audio-report artifacts/reviews/audio-report.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --json
```

9. Run the package gate last:

```powershell
uv run --script $env:AWSOME_VIDEOS_SKILL/scripts/check_production_package.py --require-source-links --brief source/brief.md --video artifacts/videos/holiday-2026-sports-live-games.mp4 --design-note source/design-note.md --production-notes source/production-notes.md --package-manifest source/package-manifest.json --pattern-blueprint source/pattern-blueprint.json --asset-manifest source/asset-manifest.json --composition-plan source/composition-plan.json --visual-review artifacts/reviews/visual-review.json --visual-contract-report artifacts/reviews/asset-composition-validation.json --renderer src/index.html --renderer-report artifacts/reviews/renderer-contract.json --readiness-report artifacts/reviews/readiness-score.json --style-fidelity-report artifacts/reviews/style-fidelity.json --contact-sheet artifacts/reviews/contact-sheet.jpg --quality-report artifacts/reviews/quality-report.json --motion-report artifacts/reviews/motion-report.json --capture-manifest artifacts/reviews/capture-manifest.json --audio-report artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 70 --duration-tolerance 1 --min-readiness-score 18 --min-style-fidelity-score 12 --require-audio --require-audio-report --require-final-audio --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-visual-contract --require-ready-assets --require-specialist-routing --require-source-routing --require-reviewed-scenes --require-renderer --forbid-scaffold-renderer --require-renderer-report --require-renderer-beat-coverage --require-renderer-visual-coverage --require-readiness-report --require-style-fidelity-report --require-final-review-notes --require-contact-sheet --require-motion-report --output artifacts/reviews/package-validation.json --json
```

A passing final report starts with `PASS awsome-videos package` or has `"ok": true`; it must also show `finalAudioExists: true`, empty `missingFinalAudioCommandTerms`, fresh renderer/visual hashes, and no failures.

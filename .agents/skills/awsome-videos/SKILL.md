---
name: awsome-videos
description: Plan, write, direct, produce, critique, or validate fast technical explainer videos using distilled patterns from the 2025-07-06 to 2026-07-06 public Awesome (@awesome-coding) and Fireship YouTube corpus. Orchestrate source, asset-generation, scene-composition, transition, renderer, audio, and visual-review skills for finished work. Use when Codex needs a video brief, script, shot plan, asset plan, composition plan, production package, MP4, or quality gate for high-density programming, AI, web-dev, software-news, or "100 seconds" style explainers.
---

# Awsome Videos

Use this skill to produce a complete fast-tech-explainer plan or production package, not just prose. The expected output is usually a brief with a timed beat table that covers script intent, visuals, animation, transition, audio, and validation. When the user asks for a finished video, carry the brief into a production artifact and validate the MP4.

Before copying command examples, set `$env:AWSOME_VIDEOS_SKILL` to this skill directory in the current workspace.

## Finished-Video Ownership

Keep this skill as the showrunner: own format, script cadence, audio direction, and final acceptance. For finished work, execute the full chain `source freeze -> specialist routing -> real assets -> scene composition -> semantic transitions -> one renderer -> frame review -> correction/rerender -> final package gate`.

- Prefer `source-to-video-director` for frozen facts, storyboards, and shot IDs.
- Require `scene-composition-director` for a multi-scene final video and `scene-transition-director` for its cuts.
- Route each visual to one owner: `imagegen` for raster imagery; Mermaid for conventional diagrams; D3 for bespoke mechanisms/data geometry; ECharts for charts; Three.js only for meaningful depth.
- Choose exactly one renderer owner. Prefer `html-d3-anime-video-workflow` for complex browser explainers; treat Slidev and Manim as alternative render surfaces.
- Keep external skills preferred rather than sibling-file dependencies. In an isolated skill-only workspace, implement the same artifact contracts with a documented fallback reason.
- Treat `create_concept_renderer.py` as a wireframe generator. Never deliver its `AWSOME_SCAFFOLD_WIREFRAME` unchanged as a finished video.

## Workflow

1. Read `references/awesome-fireship-patterns.md` when the task asks for style fidelity, examples, evaluation criteria, or detailed motion/audio guidance.
2. Read `references/visual-asset-composition-workflow.md` for every finished video, asset plan, composition pass, renderer handoff, or visual-quality repair.
3. Read `references/video-production-playbook.md` when creating an actual video, renderer, production package, audio plan, contact sheet, frame capture, or MP4.
4. Read `references/evaluation-rubric.md` when critiquing, scoring, deciding readiness, or writing acceptance criteria. Read `references/command-contracts.md` for exact commands.
5. For finished-video work, run `scripts/check_runtime_tools.py`; add `--require-render-tools` before browser rendering or MP4 validation.
6. For a new finished-video or production-package project, scaffold the standard folders and starter files with `scripts/scaffold_production_package.py` unless the user supplied an existing package.
7. Pick the format before writing:
   - `compressed explainer`: 60-160 seconds, one concept, high compression, simple visual grammar; use 60-90 seconds for demos and 90-160 seconds for fuller standalone explainers.
   - `trend/news commentary`: 3-6 minutes, claim-driven hook, fast context, implications, final take.
   - `tutorial/overview`: 5-12 minutes, concept stack, code/UI examples, recurrent recap beats.
   - `deep walkthrough`: 20+ minutes, slower screen/code segments with occasional montage resets.
   Use `scripts/select_video_patterns.py` when a topic needs a quick style blueprint before the brief.
8. Build a timed beat table. Include columns for `time`, `script purpose`, `visual`, `animation`, `transition`, and `audio`.
9. Keep visuals source-bound. Freeze URL-backed facts in `source-package.json` and map them into `shot-contract.json`; then create the asset, composition, and transition contracts with stable `bNN`/`sNN` IDs. Every asset needs provenance/rights, a producer report, output path/hash, target crop, uses, and checks. Every scene needs deliberate hierarchy, anchors, safe zones, motion phases, screenshot checks, and materially varied `objectBounds` geometry.
10. Make each timed beat concrete. Avoid placeholder cells such as `Text`, `Fade`, `Cut`, or `Music`; name the actual visual proof, motion, transition type, and audio cue for that beat.
11. Use rapid movement sparingly but constantly: hard cuts, punch-in zooms, UI pans, meme/image inserts, code scrolls, match cuts, and fast overlays should mark a new idea or joke.
12. Specify music and sound as production roles, not song names: background bed, ducking under voiceover, transition hits, short risers, glitch ticks, whooshes, and low impacts.
13. Before validating, make sure the brief explicitly contains these validator-visible sections or terms: title/promise, audience, hook, script/voiceover, visuals, animation, transitions, audio/music/SFX, assets/sources, and evaluation/validation.
14. Implement the chosen renderer only after visual preflight. Require `window.renderConceptFrame`; the visible media element must carry manifest-matching asset metadata and actually load the declared file, compositions/objects need stable IDs, and renderer state must return matching active IDs. Hard-coded `sourceProofVisible=true` is not proof.
15. Render, inspect full-resolution frames, transition midpoints, the contact sheet, and full-speed playback. Write `artifacts/reviews/visual-review.json`, correct every failed scene, rerender, and run `scripts/check_visual_contract.py`. Then run brief, style, renderer, MP4, readiness, final-notes, and package gates.

## Output Contract

For a production-ready plan, include:

- Title and one-sentence promise.
- Audience and prerequisite assumptions.
- Runtime target and format choice.
- Pattern blueprint or equivalent selected format, visual, animation, transition, audio, and script vocabulary.
- Hook/cold-open line.
- Timed beat table with at least 8 beats for short videos, more for longer work.
- Visual source plan: what assets, screenshots, code, diagrams, generated images, and source links are needed.
- Stable beat/scene IDs plus `source/asset-manifest.json` and `source/composition-plan.json` for any production handoff.
- Selected skill routes and ownership boundaries. Every completed route points to a passing JSON proof report; record a concrete fallback reason when a preferred specialist is unavailable.
- Animation and transition vocabulary per beat.
- Music/SFX plan with where and when each audio role appears.
- Voiceover or narration draft with one spoken line per timed beat.
- Voiceover cues JSON/SRT/CSV when narration timing is needed for recording, subtitles, or mix review.
- Concrete, non-repeated voiceover lines; replace template placeholders such as "Define the concept" before validation.
- Script style notes: density, joke/claim cadence, setup-payoff, and final callback.
- Evaluation checklist plus concrete `check_video_brief.py`, `score_style_fidelity.py`, and `score_video_readiness.py` commands when the plan should be production-ready.

For a finished-video request, also include:

- Project scaffold or package manifest path when a new package was created.
- Pattern blueprint path, usually `source/pattern-blueprint.json`.
- Source brief and production notes.
- Renderer, storyboard, or shot implementation files.
- Ready asset manifest with actual project files, producer reports, provenance/rights, and complete beat/scene usage.
- Composition plan with varied scene armatures and exact asset IDs; transition plan for multi-scene work.
- Renderer contract validation result when an HTML renderer is included.
- Renderer report with `visualAssetCoverageOk=true` and `compositionCoverageOk=true`.
- Final MP4 path and optional silent preview path.
- Audio report path; for publishable work, note whether final narration/music/SFX replaced synthetic validation audio and whether `finalAudioDurationOk` proves the source audio covers the requested runtime.
- Final audio source path in `package-manifest.json` as `paths.finalAudio` when `--require-final-audio` is used.
- Voiceover cue artifact paths when generated from the brief.
- Contact sheet or frame review path when available.
- Approved `visual-review.json` and hash-bound asset/composition validation report after a correction/rerender loop.
- Motion report path when rendered from HTML frames.
- Capture manifest and quality report when the MP4 was rendered from HTML.
- Readiness score path and score label.
- Style fidelity report path and score.
- Finalized production notes with renderer, readiness, contact-sheet, motion/quality, and audio evidence.
- Non-thin final review lines for asset quality, composition, renderer asset binding, legibility, beat coverage, visual mechanism, pacing/transition, source binding, audio sync, and caveats.
- Brief validation and MP4 validation commands with pass/fail results.
- Package validation command when the handoff includes both source files and an MP4.

Do not copy exact channel branding, scripts, jokes, thumbnails, or proprietary footage. Use the distilled structural patterns to create original work.

## Validation

Use `references/command-contracts.md` for exact commands and expected JSON/text fields. Minimum gates:

- Runtime preflight passes `scripts/check_runtime_tools.py --require-render-tools` before browser rendering or MP4 validation.
- Briefs pass `scripts/check_video_brief.py --require-voiceover`; source-backed work also passes `--require-source-links`.
- Voiceover cue exports pass `scripts/extract_voiceover_cues.py --require-beat-match` when timing is needed.
- Style fidelity passes `scripts/score_style_fidelity.py --require-voiceover`; scaffolded work should include `--pattern-blueprint source/pattern-blueprint.json --require-pattern-blueprint`.
- Visual preflight passes `scripts/check_visual_contract.py` structurally before renderer implementation. Finished work also passes `--require-ready-assets --require-specialist-routing --require-reviewed-scenes` with current input hashes and approved evidence.
- Browser renderers pass `scripts/check_renderer_contract.py --brief ... --require-all-brief-beats --asset-manifest ... --composition-plan ... --require-visual-ids` before encoding.
- MP4s pass `scripts/check_video_artifact.py` with expected dimensions, fps, duration, audio report, contact sheet, quality report, motion report, and capture manifest when those artifacts exist.
- Finished handoffs pass readiness with `--require-visual-contract-report`, then package validation with all visual/source/review/renderer/scaffold gates. That final gate reruns the browser renderer, binds fresh frames to the MP4, and recomputes readiness instead of trusting stored reports.
- Source-backed handoffs carry `--require-source-links` through brief validation, style fidelity, readiness scoring, and package validation.
- Publishable audio passes `--require-final-audio`, with `audio-report.json` proving `finalAudioReady=true`, `placeholderAudio=false`, and `finalAudioDurationOk=true`.
- Maintenance passes `scripts/test_validators.py --json` and `scripts/check_reference_completeness.py --json`.

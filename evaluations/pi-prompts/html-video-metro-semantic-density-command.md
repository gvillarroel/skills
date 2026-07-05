First action: read this prompt at `../prompt.md`. Then run the exact command block below once from the current workspace root, without prepending `cd /mnt/data`, `pwd`, `ls`, or any other directory/probe command, and without adding, removing, or reordering flags. Use a shell timeout of at least 600 seconds for the command block. After both commands exit successfully, read only `projects/metro-semantic-density-video/artifacts/reviews/metro-semantic-density-audit.json`, report whether `passed` is true, and stop. Do not list directories, do not run manual file-existence checks, do not read helper source, do not read audit source, do not rerun or regenerate after a passing command, do not ask questions, and do not stop before both commands finish. Do not add `--state-min-distinct visibleZoneCount`; `visibleZoneCount` is expected to remain at 5 while `activeZoneId` changes.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-semantic-density-video/artifacts/reviews/prompt-contract-build.json --state-manifest projects/metro-semantic-density-video/artifacts/reviews/render-state-check.json --state-expect visualPattern=systems-flow --state-expect-final retryVisible=true --state-expect-final deadLetterVisible=true --state-expect-final feedbackVisible=true --state-expect-final queueSlots=8 --state-expect-final visibleMechanismCount=6 --state-expect-final visibleZoneCount=5 --state-expect-contains systemLabels=Gateway --state-expect-contains systemLabels=Throttle --state-expect-transition 'retryVisible=false->true' --state-expect-transition 'deadLetterVisible=false->true' --state-expect-transition 'feedbackVisible=false->true' --state-expect-monotonic visibleMechanismCount=nondecreasing --state-expect-monotonic queueSlots=nondecreasing --state-min-distinct visibleMechanismCount=5 --state-min-distinct queueSlots=3 --state-min-distinct activeZoneId=3 --state-min-distinct cameraX=3 --state-min-distinct cameraMoving=2 --metro-style-manifest projects/metro-semantic-density-video/artifacts/reviews/metro-style-audit.json --metro-composition-manifest projects/metro-semantic-density-video/artifacts/reviews/metro-composition-audit.json --metro-rendered-frame-manifest projects/metro-semantic-density-video/artifacts/reviews/metro-rendered-frame-audit.json --metro-mute-test-manifest projects/metro-semantic-density-video/artifacts/reviews/metro-mute-test-audit.json --metro-video-composition-manifest projects/metro-semantic-density-video/artifacts/reviews/metro-video-composition-audit.json --metro-audit-suite-manifest projects/metro-semantic-density-video/artifacts/reviews/metro-audit-suite.json
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_metro_semantic_density.py --wrapper-report projects/metro-semantic-density-video/artifacts/reviews/prompt-contract-build.json --state-manifest projects/metro-semantic-density-video/artifacts/reviews/render-state-check.json --contact-sheet-manifest projects/metro-semantic-density-video/artifacts/video-renders/draft/review/metro-semantic-density-contact-sheet.json --metro-audit-suite projects/metro-semantic-density-video/artifacts/reviews/metro-audit-suite.json --metro-mute-test-audit projects/metro-semantic-density-video/artifacts/reviews/metro-mute-test-audit.json --metro-video-composition-audit projects/metro-semantic-density-video/artifacts/reviews/metro-video-composition-audit.json --output projects/metro-semantic-density-video/artifacts/reviews/metro-semantic-density-audit.json
```

Task: create a deterministic standalone HTML+D3/Anime.js validation video that proves Metro design is not just color and geometry. It must also prove semantic density: source-anchor semantic binding, visible mechanism progression, multiple dynamic state keys, camera exploration with meaningful travel and zoom depth, visible functional zones, ordered active-zone progression, camera-coupled zone transitions, contact-sheet change, encoded-MP4 composition, and no weak opening tile.

Design contract:

- Build a navigable modular megacanvas with several functional zones.
- Expose source `visualZones` and `semanticBindings`, rendered SVG `data-zone-id`/`data-zone-role`/`data-source-anchor` markers, and render-state `visibleZoneCount` plus changing `activeZoneId` and `activeSourceAnchors`.
- Ensure `metro-semantic-density-audit.json` reports `sourceAnchorVisualBindingCoverage` as `1.0`.
- Ensure ordered `statesSample` evidence shows adjacent `activeZoneId` changes coupled to camera pan, zoom, or reframe deltas.
- Ensure camera evidence shows meaningful travel and zoom depth, not decorative nudge-scale changes.
- Do not reserve any visible title, subtitle, caption, date, draft, or editorial band inside the frame.
- Use only functional labels that belong to the visual object itself.
- Use colorset1: red, dark red, status red, neutral text, white, black, and multiple grayscale levels.
- Use hard 0-radius rectangles, snapped 4 px grid edges, shared baselines, external gutters, and zero internal box padding.
- Use grayscale levels to separate hierarchy; do not simulate hierarchy with inset panels, padded chips, or nested boxes.
- Show continuity through camera-style zoom/pan/reframing or block expansion rather than disconnected slide cuts.

Use the `systems-flow` scaffold.

Required exact scaffold outputs:

- `projects/metro-semantic-density-video/source/source-package.json`
- `projects/metro-semantic-density-video/source/production-notes.md`
- `projects/metro-semantic-density-video/src/index.html`
- `projects/metro-semantic-density-video/src/render.mjs`
- `projects/metro-semantic-density-video/artifacts/video-renders/draft/videos/metro-semantic-density.mp4`
- `projects/metro-semantic-density-video/artifacts/video-renders/draft/review/metro-semantic-density-contact-sheet.jpg`
- `projects/metro-semantic-density-video/artifacts/video-renders/draft/review/metro-semantic-density-contact-sheet.json`
- `projects/metro-semantic-density-video/artifacts/reviews/self-review.md`
- `projects/metro-semantic-density-video/artifacts/reviews/prompt-contract-build.json`
- `projects/metro-semantic-density-video/artifacts/reviews/render-state-check.json`
- `projects/metro-semantic-density-video/artifacts/reviews/metro-style-audit.json`
- `projects/metro-semantic-density-video/artifacts/reviews/metro-composition-audit.json`
- `projects/metro-semantic-density-video/artifacts/reviews/metro-rendered-frame-audit.json`
- `projects/metro-semantic-density-video/artifacts/reviews/metro-mute-test-audit.json`
- `projects/metro-semantic-density-video/artifacts/reviews/metro-video-composition-audit.json`
- `projects/metro-semantic-density-video/artifacts/reviews/metro-audit-suite.json`

Semantic-density output after the scaffold:

- `projects/metro-semantic-density-video/artifacts/reviews/metro-semantic-density-audit.json`

Topic: semantic-density proof for Metro video-generation skill validation.

Video title: Metro Semantic Density Validation

Checked date: 2026-07-04

Use 6 seconds, 30 fps, and 1280x720.

Preserve these source facts:

- The video must show a navigable modular megacanvas rather than labeled slides.
- Camera movement must be visible through render-state diversity.
- Camera movement must show meaningful travel and zoom depth, not tiny decorative nudges.
- Queue fill, retry, dead-letter, and feedback throttle must all appear as late mechanisms.
- Contact-sheet frames must change enough to prove visual progression.
- Hiding all SVG text must still leave enough visible mark motion, zones, gray hierarchy, and nonbackground area for the mute test to pass.
- The semantic-density audit must show a continuity path through zones, not only distinct state-summary values.
- The semantic-density audit must prove every visual anchor is bound through source package, rendered DOM, and render-state evidence.
- The semantic-density audit must pass after the wrapper, state check, contact sheet, Metro audit suite, mute-test audit, and encoded-MP4 composition audit.

Preserve these visual anchors:

- modular megacanvas
- semantic density
- queue fill
- retry branch
- dead-letter branch
- feedback throttle
- camera exploration
- contact-sheet progression

Preserve these system components:

- Gateway
- Event bus
- Queue
- Worker pool
- Retry policy
- Dead letter
- Metrics
- Throttle

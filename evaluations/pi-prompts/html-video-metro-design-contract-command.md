First action: read this prompt at `../prompt.md`. Then run the exact command below. Do not list directories, do not read helper source, do not ask questions, and do not stop before the command finishes.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metro-design-contract-video/artifacts/reviews/prompt-contract-build.json --state-manifest projects/metro-design-contract-video/artifacts/reviews/render-state-check.json --state-expect visualPattern=systems-flow --state-expect-final retryVisible=true --state-expect-final deadLetterVisible=true --state-expect-final feedbackVisible=true --state-expect-final queueSlots=8 --state-expect-final visibleMechanismCount=6 --state-expect-contains systemLabels=Intake --state-expect-contains systemLabels=Throttle --state-expect-transition 'retryVisible=false->true' --state-expect-transition 'deadLetterVisible=false->true' --state-expect-transition 'feedbackVisible=false->true' --state-expect-monotonic visibleMechanismCount=nondecreasing --state-expect-monotonic queueSlots=nondecreasing --state-min-distinct visibleMechanismCount=5 --state-min-distinct queueSlots=3 --state-min-distinct cameraX=3 --state-min-distinct cameraMoving=2 --metro-style-manifest projects/metro-design-contract-video/artifacts/reviews/metro-style-audit.json --metro-composition-manifest projects/metro-design-contract-video/artifacts/reviews/metro-composition-audit.json --metro-rendered-frame-manifest projects/metro-design-contract-video/artifacts/reviews/metro-rendered-frame-audit.json --metro-audit-suite-manifest projects/metro-design-contract-video/artifacts/reviews/metro-audit-suite.json
```

Task: create a deterministic standalone HTML+D3/Anime.js validation video that follows Metro Minimal Tonal Motion as a design contract, not just as a palette.

Design contract:

- Build a large modular map or megacanvas with several functional zones.
- Do not reserve any visible title, subtitle, caption, date, draft, or editorial band inside the frame.
- Use only functional labels that belong to the visual object itself.
- Use colorset1: red, dark red, status red, neutral text, white, black, and multiple grayscale levels.
- Use hard 0-radius rectangles, snapped 4 px grid edges, shared baselines, external gutters, and zero internal box padding.
- Use grayscale levels to separate hierarchy; do not simulate hierarchy with inset panels, padded chips, or nested boxes.
- Show continuity through camera-style zoom/pan/reframing or block expansion rather than disconnected slide cuts.

Use the `systems-flow` scaffold.

Required exact scaffold outputs:

- `projects/metro-design-contract-video/source/source-package.json`
- `projects/metro-design-contract-video/source/production-notes.md`
- `projects/metro-design-contract-video/src/index.html`
- `projects/metro-design-contract-video/src/render.mjs`
- `projects/metro-design-contract-video/artifacts/video-renders/draft/videos/metro-design-contract.mp4`
- `projects/metro-design-contract-video/artifacts/video-renders/draft/review/metro-design-contract-contact-sheet.jpg`
- `projects/metro-design-contract-video/artifacts/video-renders/draft/review/metro-design-contract-contact-sheet.json`
- `projects/metro-design-contract-video/artifacts/reviews/self-review.md`
- `projects/metro-design-contract-video/artifacts/reviews/prompt-contract-build.json`
- `projects/metro-design-contract-video/artifacts/reviews/render-state-check.json`
- `projects/metro-design-contract-video/artifacts/reviews/metro-style-audit.json`
- `projects/metro-design-contract-video/artifacts/reviews/metro-composition-audit.json`
- `projects/metro-design-contract-video/artifacts/reviews/metro-rendered-frame-audit.json`
- `projects/metro-design-contract-video/artifacts/reviews/metro-audit-suite.json`

Topic: strict Metro design adherence for video-generation skill validation.

Video title: Metro Design Contract Validation

Checked date: 2026-07-04

Use 6 seconds, 30 fps, and 1280x720.

Preserve these source facts:

- The design must be a navigable modular megacanvas, not a title-and-cards slide.
- Colorset1 is sufficient for the validation draft.
- Square edges and zero internal padding are required for every box-like module.
- Grayscale levels must carry hierarchy across visible surfaces.
- Render-state validation must prove the late queue, retry, dead-letter, and feedback mechanisms.

Preserve these visual anchors:

- modular megacanvas
- queue fill
- worker activation
- retry branch
- dead-letter branch
- feedback throttle
- gray hierarchy levels
- square-edge modules

Preserve these system components:

- Intake
- Event bus
- Signal
- Broker
- Queue
- Worker pool
- Store
- Retry policy
- Dead letter
- Throughput
- Throttle

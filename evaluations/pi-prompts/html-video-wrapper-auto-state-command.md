First action: read this prompt at `../prompt.md`. Then run the exact command below. Do not list directories, do not read helper source, do not ask questions, and do not add state flags manually.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/wrapper-auto-state-video/artifacts/reviews/prompt-contract-build.json
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer scaffold and let the wrapper derive the browser render-state check from this prompt.

Use the `metric-dashboard` scaffold.

Required exact scaffold outputs:

- `projects/wrapper-auto-state-video/source/source-package.json`
- `projects/wrapper-auto-state-video/source/production-notes.md`
- `projects/wrapper-auto-state-video/src/index.html`
- `projects/wrapper-auto-state-video/src/render.mjs`
- `projects/wrapper-auto-state-video/artifacts/video-renders/draft/videos/auto-state-dashboard.mp4`
- `projects/wrapper-auto-state-video/artifacts/video-renders/draft/review/auto-state-dashboard-contact-sheet.jpg`
- `projects/wrapper-auto-state-video/artifacts/video-renders/draft/review/auto-state-dashboard-contact-sheet.json`
- `projects/wrapper-auto-state-video/artifacts/reviews/self-review.md`
- `projects/wrapper-auto-state-video/artifacts/reviews/prompt-contract-build.json`

Additional exact browser-state output:

- `projects/wrapper-auto-state-video/artifacts/reviews/render-state-check.json`

Topic: automatic wrapper state-check derivation for metric dashboards.

Video title: Auto State Wrapper

Checked date: 2026-07-04

Use 12 seconds, 12 fps, and 1280x720.

Preserve these source facts:

- The wrapper should detect the render-state report path from the prompt.
- Default metric-dashboard state checks should include trend, threshold, anomaly, forecast, and decision visibility.
- Default label containment checks should include the first and last metric labels.
- Default threshold containment checks should include the first and last threshold labels.
- The wrapper should fail if the derived browser state check fails.

Preserve these visual anchors:

- auto state manifest
- default state expectations
- metric-dashboard route
- trend visible
- threshold visible
- anomaly visible
- forecast visible
- decision visible
- label containment
- wrapper pass

Preserve these metric labels:

- readiness score
- detection lag
- recovery rate
- evidence quality
- escalation risk

Preserve these threshold labels:

- healthy zone
- warning line
- action line

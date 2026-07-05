First action: read this prompt at `../prompt.md`. Then run the exact command below. Do not list directories, do not read helper source, do not ask questions, and do not stop before the command finishes.

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/wrapper-integrated-state-video/artifacts/reviews/prompt-contract-build.json --state-manifest projects/wrapper-integrated-state-video/artifacts/reviews/render-state-check.json --state-expect visualPattern=metric-dashboard --state-expect anomalyVisible=true --state-expect forecastVisible=true --state-expect decisionVisible=true --state-expect-contains "metricLabels=readiness score" --state-expect-contains "metricLabels=escalation risk" --state-expect-contains "thresholdLabels=warning line" --state-min-distinct activeMetric=4 --state-min-distinct visibleMechanismCount=4
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer scaffold and validate browser render state through the prompt-contract wrapper itself.

Use the `metric-dashboard` scaffold.

Required exact scaffold outputs:

- `projects/wrapper-integrated-state-video/source/source-package.json`
- `projects/wrapper-integrated-state-video/source/production-notes.md`
- `projects/wrapper-integrated-state-video/src/index.html`
- `projects/wrapper-integrated-state-video/src/render.mjs`
- `projects/wrapper-integrated-state-video/artifacts/video-renders/draft/videos/integrated-state-dashboard.mp4`
- `projects/wrapper-integrated-state-video/artifacts/video-renders/draft/review/integrated-state-dashboard-contact-sheet.jpg`
- `projects/wrapper-integrated-state-video/artifacts/video-renders/draft/review/integrated-state-dashboard-contact-sheet.json`
- `projects/wrapper-integrated-state-video/artifacts/reviews/self-review.md`
- `projects/wrapper-integrated-state-video/artifacts/reviews/prompt-contract-build.json`

Additional exact wrapper-state output:

- `projects/wrapper-integrated-state-video/artifacts/reviews/render-state-check.json`

Topic: integrated wrapper validation for metric dashboards.

Video title: Integrated State Wrapper

Checked date: 2026-07-04

Use 12 seconds, 12 fps, and 1280x720.

Preserve these source facts:

- The wrapper should derive the output id from the requested MP4 path.
- Browser render-state validation should run after scaffold generation.
- The state report should be written by the wrapper-integrated checker.
- Exact label containment should be validated for metric and threshold arrays.
- Top-level wrapper success should depend on the state check passing.

Preserve these visual anchors:

- wrapper command
- metric-dashboard scaffold
- render state checker
- exact labels
- anomaly proof
- forecast proof
- decision window
- stateCheck report

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

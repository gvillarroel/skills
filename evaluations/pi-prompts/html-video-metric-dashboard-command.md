First action: read this prompt at `../prompt.md`. Then run the two exact commands below, in order. Do not list directories, do not read helper source, do not ask questions, and do not stop after the first command.

Command 1:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/build_from_prompt_contract.py --prompt ../prompt.md --manifest projects/metric-dashboard-video/artifacts/reviews/prompt-contract-build.json
```

Command 2:

```bash
uv run --script skills/html-d3-anime-video-workflow/scripts/check_html_render_state.py --html projects/metric-dashboard-video/src/index.html --video-id metric-dashboard --duration 12 --samples 6 --width 1280 --height 720 --manifest projects/metric-dashboard-video/artifacts/reviews/render-state-check.json --expect-state visualPattern=metric-dashboard --expect-state anomalyVisible=true --expect-state forecastVisible=true --expect-state decisionVisible=true --expect-state-contains "metricLabels=readiness score" --expect-state-contains "metricLabels=escalation risk" --expect-state-contains "thresholdLabels=warning line" --min-distinct-state activeMetric=4 --min-distinct-state visibleMechanismCount=4
```

Task: create a deterministic standalone HTML+D3/Anime.js explainer scaffold for a metric-dashboard video.

Use the `metric-dashboard` scaffold.

Required exact outputs:

- `projects/metric-dashboard-video/source/source-package.json`
- `projects/metric-dashboard-video/source/production-notes.md`
- `projects/metric-dashboard-video/src/index.html`
- `projects/metric-dashboard-video/src/render.mjs`
- `projects/metric-dashboard-video/artifacts/video-renders/draft/videos/metric-dashboard.mp4`
- `projects/metric-dashboard-video/artifacts/video-renders/draft/review/metric-dashboard-contact-sheet.jpg`
- `projects/metric-dashboard-video/artifacts/video-renders/draft/review/metric-dashboard-contact-sheet.json`
- `projects/metric-dashboard-video/artifacts/reviews/self-review.md`
- `projects/metric-dashboard-video/artifacts/reviews/prompt-contract-build.json`

Additional exact browser-state output after Command 2:

- `projects/metric-dashboard-video/artifacts/reviews/render-state-check.json`

Topic: incident readiness metric dashboard.

Video title: Incident Readiness Metrics

Checked date: 2026-07-04

Use 12 seconds, 12 fps, and 1280x720.

Preserve these source facts:

- The dashboard starts with one primary readiness metric before supporting metrics appear.
- Thresholds define healthy, warning, and action zones.
- An anomaly should be connected to a named risk metric.
- A forecast cone should appear only after the historical trend is visible.
- The decision window should open after threshold and forecast context exists.

Preserve these visual anchors:

- primary readiness metric
- trend line
- healthy band
- warning threshold
- action threshold
- anomaly marker
- forecast cone
- decision window

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

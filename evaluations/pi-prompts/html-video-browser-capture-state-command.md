# Isolated HTML Video Browser Capture State Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

Read `../prompt.md`, then run these commands exactly in order. Do not change paths, filenames, `--output-id`, `--video-id`, or `--pattern`.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/event-driven-saga-state-video --title "Event-Driven Saga State Capture" --topic "event-driven saga architecture" --output-id event-driven-saga-state --pattern systems-flow --checked-date "July 4, 2026" --duration 12 --fps 12 --width 1280 --height 720 --source-url "local prompt facts" --fact "Saga workflows coordinate multi-step business processes through events and compensating actions." --fact "A bounded queue makes pressure visible before workers saturate." --fact "Retries need caps and backoff so failures do not become infinite invisible loops." --fact "Dead-letter paths separate failed work for inspection instead of hiding it in the main flow." --fact "Feedback control can slow intake when downstream capacity is exceeded." --anchor "intake sources" --anchor "event bus" --anchor "bounded queue" --anchor "worker pool" --anchor "retry branch" --anchor "dead-letter path" --anchor "throughput metric" --anchor "feedback limit"
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/capture_html_video.py --html projects/event-driven-saga-state-video/src/index.html --output projects/event-driven-saga-state-video/artifacts/video-renders/draft/videos/event-driven-saga-state-browser.mp4 --video-id event-driven-saga-state --duration 6 --fps 6 --width 1280 --height 720 --manifest projects/event-driven-saga-state-video/artifacts/reviews/state-capture-manifest.json --expect-state visualPattern=systems-flow --expect-state sourceFacts=5 --min-distinct-state beat=2
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_video_outputs.py --require projects/event-driven-saga-state-video/src/index.html --require projects/event-driven-saga-state-video/artifacts/video-renders/draft/videos/event-driven-saga-state-browser.mp4 --require-json-passed projects/event-driven-saga-state-video/artifacts/reviews/state-capture-manifest.json --require-text "projects/event-driven-saga-state-video/source/source-package.json::bounded queue" --report projects/event-driven-saga-state-video/artifacts/reviews/output-contract-report.json
```

Before final response, verify these exact paths exist and are non-empty:

- `projects/event-driven-saga-state-video/source/source-package.json`
- `projects/event-driven-saga-state-video/src/index.html`
- `projects/event-driven-saga-state-video/artifacts/video-renders/draft/videos/event-driven-saga-state-browser.mp4`
- `projects/event-driven-saga-state-video/artifacts/reviews/state-capture-manifest.json`
- `projects/event-driven-saga-state-video/artifacts/reviews/output-contract-report.json`

Both JSON reports must have `"passed": true`. The state capture manifest must show `visualPattern` as `systems-flow`, `sourceFacts` as `5`, and at least two distinct `beat` values. If any exact path is missing, rerun the commands exactly. Do not ask for clarification.

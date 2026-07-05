# Isolated HTML Video Browser Capture Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

Read `../prompt.md`, then run these commands exactly in order. Do not change paths, filenames, `--output-id`, `--video-id`, or `--pattern`.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/event-driven-saga-browser-video --title "Event-Driven Saga Browser Capture" --topic "event-driven saga architecture" --output-id event-driven-saga-browser --pattern systems-flow --checked-date "July 4, 2026" --duration 12 --fps 12 --width 1280 --height 720 --source-url "local prompt facts" --fact "Saga workflows coordinate multi-step business processes through events and compensating actions." --fact "A bounded queue makes pressure visible before workers saturate." --fact "Retries need caps and backoff so failures do not become infinite invisible loops." --fact "Dead-letter paths separate failed work for inspection instead of hiding it in the main flow." --fact "Feedback control can slow intake when downstream capacity is exceeded." --anchor "intake sources" --anchor "event bus" --anchor "bounded queue" --anchor "worker pool" --anchor "retry branch" --anchor "dead-letter path" --anchor "throughput metric" --anchor "feedback limit"
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/capture_html_video.py --html projects/event-driven-saga-browser-video/src/index.html --output projects/event-driven-saga-browser-video/artifacts/video-renders/draft/videos/event-driven-saga-browser-browser.mp4 --video-id event-driven-saga-browser --duration 6 --fps 6 --width 1280 --height 720 --manifest projects/event-driven-saga-browser-video/artifacts/reviews/browser-capture-manifest.json
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/review_video_quality.py --video projects/event-driven-saga-browser-video/artifacts/video-renders/draft/videos/event-driven-saga-browser-browser.mp4 --report projects/event-driven-saga-browser-video/artifacts/reviews/browser-quality-report.json --expect-width 1280 --expect-height 720 --expect-duration 6 --expect-fps 6
```

Before final response, verify these exact paths exist and are non-empty:

- `projects/event-driven-saga-browser-video/source/source-package.json`
- `projects/event-driven-saga-browser-video/src/index.html`
- `projects/event-driven-saga-browser-video/artifacts/video-renders/draft/videos/event-driven-saga-browser.mp4`
- `projects/event-driven-saga-browser-video/artifacts/video-renders/draft/videos/event-driven-saga-browser-browser.mp4`
- `projects/event-driven-saga-browser-video/artifacts/reviews/browser-capture-manifest.json`
- `projects/event-driven-saga-browser-video/artifacts/reviews/browser-quality-report.json`

The browser quality report must have `"passed": true`. If any exact path is missing, rerun the commands exactly. Do not ask for clarification.

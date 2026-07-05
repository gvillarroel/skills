# Isolated HTML Video Browser Capture Motion Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

Read `../prompt.md`, then run these commands exactly in order. Do not change paths, filenames, `--output-id`, `--video-id`, or `--pattern`.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/event-driven-saga-motion-video --title "Event-Driven Saga Motion Audit" --topic "event-driven saga architecture" --output-id event-driven-saga-motion --pattern systems-flow --checked-date "July 4, 2026" --duration 12 --fps 12 --width 1280 --height 720 --source-url "local prompt facts" --fact "Saga workflows coordinate multi-step business processes through events and compensating actions." --fact "A bounded queue makes pressure visible before workers saturate." --fact "Retries need caps and backoff so failures do not become infinite invisible loops." --fact "Dead-letter paths separate failed work for inspection instead of hiding it in the main flow." --fact "Feedback control can slow intake when downstream capacity is exceeded." --anchor "intake sources" --anchor "event bus" --anchor "bounded queue" --anchor "worker pool" --anchor "retry branch" --anchor "dead-letter path" --anchor "throughput metric" --anchor "feedback limit"
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/capture_html_video.py --html projects/event-driven-saga-motion-video/src/index.html --output projects/event-driven-saga-motion-video/artifacts/video-renders/draft/videos/event-driven-saga-motion-browser.mp4 --video-id event-driven-saga-motion --duration 6 --fps 6 --width 1280 --height 720 --manifest projects/event-driven-saga-motion-video/artifacts/reviews/browser-capture-manifest.json
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/review_video_quality.py --video projects/event-driven-saga-motion-video/artifacts/video-renders/draft/videos/event-driven-saga-motion-browser.mp4 --report projects/event-driven-saga-motion-video/artifacts/reviews/browser-quality-report.json --expect-width 1280 --expect-height 720 --expect-duration 6 --expect-fps 6
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/audit_video_motion.py --video projects/event-driven-saga-motion-video/artifacts/video-renders/draft/videos/event-driven-saga-motion-browser.mp4 --report projects/event-driven-saga-motion-video/artifacts/reviews/motion-audit-report.json --sample-fps 1 --min-samples 4 --min-color-buckets 12 --min-nonbackground-ratio 0.015 --min-changing-pairs 2
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_video_outputs.py --require projects/event-driven-saga-motion-video/src/index.html --require projects/event-driven-saga-motion-video/artifacts/video-renders/draft/videos/event-driven-saga-motion-browser.mp4 --require-json-passed projects/event-driven-saga-motion-video/artifacts/reviews/browser-quality-report.json --require-json-passed projects/event-driven-saga-motion-video/artifacts/reviews/motion-audit-report.json --require-text "projects/event-driven-saga-motion-video/source/source-package.json::bounded queue" --report projects/event-driven-saga-motion-video/artifacts/reviews/output-contract-report.json
```

Before final response, verify these exact paths exist and are non-empty:

- `projects/event-driven-saga-motion-video/source/source-package.json`
- `projects/event-driven-saga-motion-video/src/index.html`
- `projects/event-driven-saga-motion-video/artifacts/video-renders/draft/videos/event-driven-saga-motion-browser.mp4`
- `projects/event-driven-saga-motion-video/artifacts/reviews/browser-capture-manifest.json`
- `projects/event-driven-saga-motion-video/artifacts/reviews/browser-quality-report.json`
- `projects/event-driven-saga-motion-video/artifacts/reviews/motion-audit-report.json`
- `projects/event-driven-saga-motion-video/artifacts/reviews/output-contract-report.json`

All JSON reports must have `"passed": true`. If any exact path is missing, rerun the commands exactly. Do not ask for clarification.

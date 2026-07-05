# Isolated HTML Video Systems-Flow Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

Run this command exactly. Do not change `--project-root`, `--output-id`, filenames, paths, or `--pattern`.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/event-driven-saga-video --title "Event-Driven Saga Failure Recovery" --topic "event-driven saga architecture" --output-id event-driven-saga-flow --pattern systems-flow --checked-date "July 4, 2026" --duration 18 --fps 12 --width 1280 --height 720 --source-url "local prompt facts" --fact "Saga workflows coordinate multi-step business processes through events and compensating actions." --fact "A bounded queue makes pressure visible before workers saturate." --fact "Retries need caps and backoff so failures do not become infinite invisible loops." --fact "Dead-letter paths separate failed work for inspection instead of hiding it in the main flow." --fact "Feedback control can slow intake when downstream capacity is exceeded." --anchor "intake sources" --anchor "event bus" --anchor "bounded queue" --anchor "worker pool" --anchor "retry branch" --anchor "dead-letter path" --anchor "throughput metric" --anchor "feedback limit"
```

Before final response, verify these exact paths exist and the MP4 is non-empty:

- `projects/event-driven-saga-video/source/source-package.json`
- `projects/event-driven-saga-video/source/production-notes.md`
- `projects/event-driven-saga-video/src/index.html`
- `projects/event-driven-saga-video/src/render.mjs`
- `projects/event-driven-saga-video/artifacts/video-renders/draft/videos/event-driven-saga-flow.mp4`
- `projects/event-driven-saga-video/artifacts/reviews/self-review.md`

The self-review must mention `systems-flow` and at least three semantic motion systems. If any exact path is missing, rerun the same command exactly. Do not ask for clarification.

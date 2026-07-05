# Isolated HTML Video Mechanism-State Evaluation

Use the loaded `html-d3-anime-video-workflow` skill.

Read `../prompt.md` directly, then run these commands exactly in order. Do not run `Get-ChildItem`, `Test-Path`, or other PowerShell probes; the isolated shell may be bash. If inspecting a file with the read tool, pass a `path`, not a shell command. Do not change paths, filenames, `--output-id`, `--video-id`, or `--pattern`.

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/build_standalone_explainer.py --project-root projects/event-driven-saga-mechanism-video --title "Event-Driven Saga Mechanism State" --topic "event-driven saga architecture" --output-id event-driven-saga-mechanism --pattern systems-flow --checked-date "July 4, 2026" --duration 12 --fps 12 --width 1280 --height 720 --source-url "local prompt facts" --fact "Saga workflows coordinate multi-step business processes through events and compensating actions." --fact "A bounded queue makes pressure visible before workers saturate." --fact "Retries need caps and backoff so failures do not become infinite invisible loops." --fact "Dead-letter paths separate failed work for inspection instead of hiding it in the main flow." --fact "Feedback control can slow intake when downstream capacity is exceeded." --anchor "intake sources" --anchor "event bus" --anchor "bounded queue" --anchor "worker pool" --anchor "retry branch" --anchor "dead-letter path" --anchor "throughput metric" --anchor "feedback limit"
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/capture_html_video.py --html projects/event-driven-saga-mechanism-video/src/index.html --output projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/videos/event-driven-saga-mechanism-browser.mp4 --video-id event-driven-saga-mechanism --duration 12 --fps 4 --width 1280 --height 720 --manifest projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-capture-manifest.json --expect-state visualPattern=systems-flow --expect-state sourceFacts=5 --expect-state retryVisible=true --expect-state deadLetterVisible=true --expect-state feedbackVisible=true --expect-state visibleMechanismCount=6 --min-distinct-state visibleMechanismCount=4 --min-distinct-state queueSlots=5
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/make_video_contact_sheet.py --video projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/videos/event-driven-saga-mechanism-browser.mp4 --output projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-contact-sheet.jpg --manifest projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-contact-sheet.json --samples 8 --columns 4 --thumb-width 320 --label-times --min-tile-color-buckets 12 --min-tile-nonbackground-ratio 0.015 --min-consecutive-change-ratio 0.002 --min-changing-pairs 5 --max-low-change-pairs 2
```

```powershell
uv run --script skills/html-d3-anime-video-workflow/scripts/check_video_outputs.py --require projects/event-driven-saga-mechanism-video/source/source-package.json --require projects/event-driven-saga-mechanism-video/src/index.html --require projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/videos/event-driven-saga-mechanism.mp4 --require projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/review/event-driven-saga-mechanism-contact-sheet.jpg --require projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/videos/event-driven-saga-mechanism-browser.mp4 --require projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-contact-sheet.jpg --require-json-passed projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/review/event-driven-saga-mechanism-contact-sheet.json --require-json-passed projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-capture-manifest.json --require-json-passed projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-contact-sheet.json --require-text projects/event-driven-saga-mechanism-video/source/source-package.json::Feedback control --report projects/event-driven-saga-mechanism-video/artifacts/reviews/output-contract-report.json
```

The exact required outputs are:

- `projects/event-driven-saga-mechanism-video/source/source-package.json`
- `projects/event-driven-saga-mechanism-video/src/index.html`
- `projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/videos/event-driven-saga-mechanism.mp4`
- `projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/review/event-driven-saga-mechanism-contact-sheet.jpg`
- `projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/review/event-driven-saga-mechanism-contact-sheet.json`
- `projects/event-driven-saga-mechanism-video/artifacts/video-renders/draft/videos/event-driven-saga-mechanism-browser.mp4`
- `projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-capture-manifest.json`
- `projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-contact-sheet.jpg`
- `projects/event-driven-saga-mechanism-video/artifacts/reviews/mechanism-contact-sheet.json`
- `projects/event-driven-saga-mechanism-video/artifacts/reviews/output-contract-report.json`

All JSON reports must have `"passed": true`, including the helper-generated contact-sheet manifest under `artifacts/video-renders/draft/review/`. The capture manifest must prove `retryVisible`, `deadLetterVisible`, and `feedbackVisible` were each `true`, `visibleMechanismCount` reached `6`, and `queueSlots` had at least five distinct values. The browser-capture contact sheet must contain exactly eight real tiles, four columns, at least five changing consecutive tile pairs, and at most two low-change consecutive pairs. If any exact path is missing, rerun the commands exactly. Do not ask for clarification.

Do not run a separate `ls` command over the backticked paths above; the `check_video_outputs.py` command and evaluation harness verify file existence. Inspect the JSON reports instead.

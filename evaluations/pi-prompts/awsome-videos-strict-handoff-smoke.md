Use $awsome-videos.

Create and validate a strict finished-video handoff for a short deterministic explainer titled "What Is RAG?". Work only in `outputs/`.

Run this exact shell command first:

```shell
mkdir -p outputs; uv run --script skills/awsome-videos/scripts/scaffold_production_package.py outputs/rag-video --title "What Is RAG?" --promise "Explain retrieval augmented generation as a search-then-generate loop that grounds an answer in retrieved context." --project-id rag-video --runtime 0:12 --json > outputs/scaffold-result.json
```

Then run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/check_video_brief.py outputs/rag-video/source/brief.md --require-voiceover --json > outputs/brief-validation.json
```

Then run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/extract_voiceover_cues.py outputs/rag-video/source/brief.md --format json --min-cues 8 --expect-duration 12 --duration-tolerance 1 --require-beat-match --output outputs/rag-video/artifacts/audio/voiceover-cues.json
```

Then run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/render_concept_video.py outputs/rag-video/src/index.html outputs/rag-video/artifacts/videos/rag-video.mp4 --duration 12 --fps 30 --force --contact-sheet outputs/rag-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/rag-video/artifacts/reviews/quality-report.json --motion-report outputs/rag-video/artifacts/reviews/motion-report.json --capture-manifest outputs/rag-video/artifacts/reviews/capture-manifest.json --render-state-report outputs/rag-video/artifacts/reviews/render-state.json --audio-report outputs/rag-video/artifacts/reviews/audio-report.json --install-browser --json > outputs/render-result.json
```

Then run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/check_video_artifact.py outputs/rag-video/artifacts/videos/rag-video.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 12 --duration-tolerance 1 --min-size-bytes 1 --require-audio --audio-report outputs/rag-video/artifacts/reviews/audio-report.json --require-audio-report --contact-sheet outputs/rag-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/rag-video/artifacts/reviews/quality-report.json --motion-report outputs/rag-video/artifacts/reviews/motion-report.json --capture-manifest outputs/rag-video/artifacts/reviews/capture-manifest.json --json > outputs/video-validation.json
```

Then run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/score_video_readiness.py --brief outputs/rag-video/source/brief.md --video outputs/rag-video/artifacts/videos/rag-video.mp4 --renderer-report outputs/rag-video/artifacts/reviews/render-state.json --quality-report outputs/rag-video/artifacts/reviews/quality-report.json --motion-report outputs/rag-video/artifacts/reviews/motion-report.json --capture-manifest outputs/rag-video/artifacts/reviews/capture-manifest.json --audio-report outputs/rag-video/artifacts/reviews/audio-report.json --contact-sheet outputs/rag-video/artifacts/reviews/contact-sheet.jpg --require-voiceover --output outputs/rag-video/artifacts/reviews/readiness-score.json --json > outputs/readiness-result.json
```

Then run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/finalize_production_notes.py outputs/rag-video/source/production-notes.md --renderer-report outputs/rag-video/artifacts/reviews/render-state.json --readiness-report outputs/rag-video/artifacts/reviews/readiness-score.json --contact-sheet outputs/rag-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/rag-video/artifacts/reviews/quality-report.json --motion-report outputs/rag-video/artifacts/reviews/motion-report.json --audio-report outputs/rag-video/artifacts/reviews/audio-report.json --video-validation outputs/video-validation.json --json > outputs/finalize-notes-result.json
```

Finally run this exact shell command:

```shell
uv run --script skills/awsome-videos/scripts/check_production_package.py --brief outputs/rag-video/source/brief.md --video outputs/rag-video/artifacts/videos/rag-video.mp4 --design-note outputs/rag-video/source/design-note.md --production-notes outputs/rag-video/source/production-notes.md --package-manifest outputs/rag-video/source/package-manifest.json --pattern-blueprint outputs/rag-video/source/pattern-blueprint.json --renderer outputs/rag-video/src/index.html --renderer-report outputs/rag-video/artifacts/reviews/render-state.json --readiness-report outputs/rag-video/artifacts/reviews/readiness-score.json --contact-sheet outputs/rag-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/rag-video/artifacts/reviews/quality-report.json --motion-report outputs/rag-video/artifacts/reviews/motion-report.json --capture-manifest outputs/rag-video/artifacts/reviews/capture-manifest.json --audio-report outputs/rag-video/artifacts/reviews/audio-report.json --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 12 --duration-tolerance 1 --min-size-bytes 1 --min-readiness-score 18 --require-audio --require-audio-report --require-voiceover --require-design-note --require-production-notes --require-package-manifest --require-pattern-blueprint --require-renderer --require-renderer-report --require-readiness-report --require-final-review-notes --require-contact-sheet --require-motion-report --json > outputs/package-validation.json
```

Required outputs:

- `outputs\scaffold-result.json`
- `outputs\brief-validation.json`
- `outputs\render-result.json`
- `outputs\video-validation.json`
- `outputs\readiness-result.json`
- `outputs\finalize-notes-result.json`
- `outputs\package-validation.json`
- `outputs\rag-video\source\brief.md`
- `outputs\rag-video\source\pattern-blueprint.json`
- `outputs\rag-video\source\package-manifest.json`
- `outputs\rag-video\source\production-notes.md`
- `outputs\rag-video\src\index.html`
- `outputs\rag-video\artifacts\audio\voiceover-cues.json`
- `outputs\rag-video\artifacts\videos\rag-video.mp4`
- `outputs\rag-video\artifacts\reviews\contact-sheet.jpg`
- `outputs\rag-video\artifacts\reviews\render-state.json`
- `outputs\rag-video\artifacts\reviews\quality-report.json`
- `outputs\rag-video\artifacts\reviews\motion-report.json`
- `outputs\rag-video\artifacts\reviews\capture-manifest.json`
- `outputs\rag-video\artifacts\reviews\audio-report.json`
- `outputs\rag-video\artifacts\reviews\readiness-score.json`

The final answer must report whether `render-result.json`, `video-validation.json`, `readiness-result.json`, `finalize-notes-result.json`, and `package-validation.json` all have `"ok": true`; include the readiness score, MP4 duration, fps, audio stream count, and whether final review notes have stale lines.

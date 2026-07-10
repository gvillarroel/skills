Use $awsome-videos.

Create and validate a short deterministic MP4 from a scaffolded HTML renderer. Work only in `outputs/`.

Run this exact scaffold command first:

```bash
bash -lc 'mkdir -p outputs && uv run --script skills/awsome-videos/scripts/scaffold_production_package.py outputs/breaker-video --title "What Is A Circuit Breaker?" --promise "Explain a circuit breaker as a fail-fast state machine around unreliable dependencies." --project-id circuit-breaker --skill-path skills/awsome-videos --json > outputs/scaffold-result.json'
```

Then run this exact render command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/render_concept_video.py outputs/breaker-video/src/index.html outputs/breaker-video/artifacts/videos/circuit-breaker.mp4 --duration 8 --fps 2 --force --contact-sheet outputs/breaker-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/breaker-video/artifacts/reviews/quality-report.json --capture-manifest outputs/breaker-video/artifacts/reviews/capture-manifest.json --render-state-report outputs/breaker-video/artifacts/reviews/render-state.json --install-browser --json > outputs/render-result.json'
```

Then validate the MP4 with this exact command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/check_video_artifact.py outputs/breaker-video/artifacts/videos/circuit-breaker.mp4 --expect-width 1280 --expect-height 720 --expect-fps 2 --expect-duration 8 --duration-tolerance 0.5 --min-size-bytes 1 --require-audio --contact-sheet outputs/breaker-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/breaker-video/artifacts/reviews/quality-report.json --capture-manifest outputs/breaker-video/artifacts/reviews/capture-manifest.json --json > outputs/video-validation.json'
```

Finally validate the production package with this exact command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/check_production_package.py --brief outputs/breaker-video/source/brief.md --video outputs/breaker-video/artifacts/videos/circuit-breaker.mp4 --design-note outputs/breaker-video/source/design-note.md --renderer outputs/breaker-video/src/index.html --renderer-report outputs/breaker-video/artifacts/reviews/render-state.json --contact-sheet outputs/breaker-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/breaker-video/artifacts/reviews/quality-report.json --capture-manifest outputs/breaker-video/artifacts/reviews/capture-manifest.json --expect-width 1280 --expect-height 720 --expect-fps 2 --expect-duration 8 --duration-tolerance 0.5 --min-size-bytes 1 --require-audio --require-design-note --require-renderer --require-renderer-report --require-contact-sheet --json > outputs/package-validation.json'
```

Required outputs:

- `outputs/scaffold-result.json`
- `outputs/render-result.json`
- `outputs/video-validation.json`
- `outputs/package-validation.json`
- `outputs/breaker-video/src/index.html`
- `outputs/breaker-video/artifacts/videos/circuit-breaker.mp4`
- `outputs/breaker-video/artifacts/reviews/contact-sheet.jpg`
- `outputs/breaker-video/artifacts/reviews/quality-report.json`
- `outputs/breaker-video/artifacts/reviews/capture-manifest.json`
- `outputs/breaker-video/artifacts/reviews/render-state.json`

The final answer must report whether `render-result.json`, `video-validation.json`, and `package-validation.json` all have `"ok": true`, and include the MP4 duration, fps, and audio stream count from `video-validation.json`.

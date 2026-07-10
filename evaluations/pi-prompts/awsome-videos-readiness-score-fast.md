Use $awsome-videos.

Create a short readiness-scored production package without using repository context outside the copied skill. Work only in `outputs/`.

Run this exact scaffold command first:

```bash
bash -lc 'mkdir -p outputs && uv run --script skills/awsome-videos/scripts/scaffold_production_package.py outputs/rate-limit-video --title "What Is A Rate Limit?" --promise "Explain a rate limit as a token budget that protects a service and gives clients retry timing." --project-id rate-limit --skill-path skills/awsome-videos --json > outputs/scaffold-result.json'
```

Then run this exact renderer contract command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/check_renderer_contract.py outputs/rate-limit-video/src/index.html --duration 70 --output outputs/rate-limit-video/artifacts/reviews/render-state.json --install-browser --json > outputs/renderer-validation.json'
```

Then run this exact synthetic MP4 command:

```bash
bash -lc 'ffmpeg -y -f lavfi -i testsrc2=size=1280x720:rate=2:duration=4 -f lavfi -i sine=frequency=330:duration=4 -c:v libx264 -b:v 2M -pix_fmt yuv420p -c:a aac -shortest outputs/rate-limit-video/artifacts/videos/rate-limit.mp4 >/dev/null 2>&1 && cp outputs/rate-limit-video/artifacts/reviews/renderer-frames/renderer-00-000000ms.png outputs/rate-limit-video/artifacts/reviews/contact-sheet.jpg 2>/dev/null || ffmpeg -y -i outputs/rate-limit-video/artifacts/videos/rate-limit.mp4 -frames:v 1 outputs/rate-limit-video/artifacts/reviews/contact-sheet.jpg >/dev/null 2>&1 && printf "{\"ok\":true,\"passed\":true,\"findings\":[]}\n" > outputs/rate-limit-video/artifacts/reviews/quality-report.json && printf "{\"ok\":true,\"findings\":[]}\n" > outputs/rate-limit-video/artifacts/reviews/capture-manifest.json'
```

Then run this exact readiness score command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/score_video_readiness.py --brief outputs/rate-limit-video/source/brief.md --video outputs/rate-limit-video/artifacts/videos/rate-limit.mp4 --renderer-report outputs/rate-limit-video/artifacts/reviews/render-state.json --quality-report outputs/rate-limit-video/artifacts/reviews/quality-report.json --capture-manifest outputs/rate-limit-video/artifacts/reviews/capture-manifest.json --contact-sheet outputs/rate-limit-video/artifacts/reviews/contact-sheet.jpg --output outputs/rate-limit-video/artifacts/reviews/readiness-score.json --json > outputs/readiness-result.json'
```

Finally run this exact package validation command:

```bash
bash -lc 'uv run --script skills/awsome-videos/scripts/check_production_package.py --brief outputs/rate-limit-video/source/brief.md --video outputs/rate-limit-video/artifacts/videos/rate-limit.mp4 --design-note outputs/rate-limit-video/source/design-note.md --renderer outputs/rate-limit-video/src/index.html --renderer-report outputs/rate-limit-video/artifacts/reviews/render-state.json --readiness-report outputs/rate-limit-video/artifacts/reviews/readiness-score.json --contact-sheet outputs/rate-limit-video/artifacts/reviews/contact-sheet.jpg --quality-report outputs/rate-limit-video/artifacts/reviews/quality-report.json --capture-manifest outputs/rate-limit-video/artifacts/reviews/capture-manifest.json --expect-width 1280 --expect-height 720 --expect-fps 2 --expect-duration 4 --duration-tolerance 0.5 --min-size-bytes 1 --require-audio --require-design-note --require-renderer --require-renderer-report --require-readiness-report --require-contact-sheet --json > outputs/package-validation.json'
```

Required outputs:

- `outputs/scaffold-result.json`
- `outputs/renderer-validation.json`
- `outputs/readiness-result.json`
- `outputs/package-validation.json`
- `outputs/rate-limit-video/artifacts/videos/rate-limit.mp4`
- `outputs/rate-limit-video/artifacts/reviews/readiness-score.json`

The final answer must report whether `readiness-result.json` and `package-validation.json` have `"ok": true`, and include the package readiness score and label from `outputs/package-validation.json`.

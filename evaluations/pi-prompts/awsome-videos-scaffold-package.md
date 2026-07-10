Use $awsome-videos to scaffold and validate a production package for a 70-second explainer titled "What Is A Retry Queue?".

Read `skills/awsome-videos/SKILL.md` after reading this prompt.

First run this exact shell command:

```
bash -lc 'mkdir -p outputs && uv run --script skills/awsome-videos/scripts/scaffold_production_package.py outputs/retry-queue --title "What Is A Retry Queue?" --promise "Explain a retry queue as controlled failure recovery with delay, limits, and dead-letter handling." --project-id retry-queue --skill-path skills/awsome-videos --json > outputs/scaffold-result.json'
```

Then create a 70-second 1280x720 30 fps MP4 with audio at `outputs/retry-queue/artifacts/videos/retry-queue.mp4`. Use a visible test pattern and enough bitrate, for example `testsrc` plus `-b:v 700k`, so the package validator duration, resolution, audio, and size checks pass on the first try.

Then validate the package and write JSON to `outputs/retry-queue/artifacts/reviews/package-validation.json`. The validation command must include `--expect-duration 70 --duration-tolerance 1`, `--require-audio`, `--design-note outputs/retry-queue/source/design-note.md`, `--require-design-note`, `--production-notes outputs/retry-queue/source/production-notes.md`, `--package-manifest outputs/retry-queue/source/package-manifest.json`, `--require-production-notes`, and `--require-package-manifest`.

Required outputs:

- `outputs/scaffold-result.json`
- `outputs/retry-queue/source/brief.md`
- `outputs/retry-queue/source/design-note.md`
- `outputs/retry-queue/source/production-notes.md`
- `outputs/retry-queue/source/package-manifest.json`
- `outputs/retry-queue/src/storyboard.md`
- `outputs/retry-queue/artifacts/videos/retry-queue.mp4`
- `outputs/retry-queue/artifacts/reviews/package-validation.json`

The final package validation JSON must have `"ok": true`. Do not run a knowingly failing package validation command before the final validation.

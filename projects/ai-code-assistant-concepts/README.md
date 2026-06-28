# AI Code Assistant Concepts

This project generates a coherent set of fifteen compact instructional videos about AI code assistant concepts.

## Outputs

- Per-video planning folders: `videos/<video-id>/`
- Rendered MP4s: `artifacts/videos/<video-id>/<video-id>.mp4`
- Review reports: `artifacts/review/<video-id>/`
- Smoke screenshots: `artifacts/screenshots/smoke/<video-id>/`

## Commands

- `npm run plans`: regenerate briefs, contracts, composition plans, and transition plans.
- `npm run validate`: validate data shape and generated planning files.
- `npm run smoke`: render representative browser frames for every module.
- `npm run render:quick`: create low-frame-rate MP4s for critique.
- `npm run render:final`: create final MP4s.
- `npm run review`: run ffprobe, black/freeze scans, keyframe extraction, and review reports.

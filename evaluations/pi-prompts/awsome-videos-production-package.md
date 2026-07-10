Use $awsome-videos to create a compact production package for a 70-second video titled "What Is A Queue?".

The skill bundle is available at `skills/awsome-videos`; read `skills/awsome-videos/SKILL.md` after reading this prompt.

Create these exact files:

- `outputs/queue-brief.md`
- `outputs/queue-evaluation.md`
- `outputs/smoke.mp4`
- `outputs/queue-brief-validation.json`
- `outputs/smoke-video-validation.json`

Requirements:

- The brief must use a timed beat table with at least 8 beats and include script purpose, visual, animation, transition, and audio columns.
- The brief must explicitly include the terms or headings for title/promise, audience, hook, script or voiceover, visuals, animation, transitions, audio/music/SFX, assets/sources, and evaluation/validation before running the validator.
- The evaluation must use the skill's rubric and include a category score table plus the total score.
- Create `outputs/smoke.mp4` as a 2-second 1280x720 30 fps MP4 with an audio stream. It is only a validator smoke artifact, not the finished video.
- Validate the brief with:

```powershell
uv run --script skills/awsome-videos/scripts/check_video_brief.py outputs/queue-brief.md --json > outputs/queue-brief-validation.json
```

- Validate the smoke MP4 with:

```powershell
uv run --script skills/awsome-videos/scripts/check_video_artifact.py outputs/smoke.mp4 --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 2 --duration-tolerance 0.5 --require-audio --min-size-bytes 1 --json > outputs/smoke-video-validation.json
```

Use $awsome-videos to create and validate a small production package for a 45-second explainer titled "What Is A Retry Queue?".

Read `skills/awsome-videos/SKILL.md` after reading this prompt. Use the production package validator from the skill.
Create the `outputs` directory before listing or writing anything under it, and avoid exploratory commands that are expected to fail.

Create these exact files:

- `outputs/retry-brief.md`
- `outputs/design-note.md`
- `outputs/storyboard.md`
- `outputs/smoke.mp4`
- `outputs/package-validation.json`

Requirements:

- `outputs/retry-brief.md` must include a timed beat table with at least 8 beats and all required validation-visible coverage: title/promise, audience, hook, script/voiceover, visuals, animation, transitions, audio/music/SFX, assets/sources, and evaluation/validation.
- `outputs/design-note.md` must include concept claim, chosen visual metaphor, visual vocabulary, and timing contract.
- `outputs/storyboard.md` must include storyboard or shot timing details.
- `outputs/smoke.mp4` must be a 2-second 1280x720 30 fps MP4 with an audio stream. It is only a validator smoke artifact.
- Validate the package with this exact shell command, including the `bash -lc` wrapper:

```
bash -lc 'uv run --script skills/awsome-videos/scripts/check_production_package.py --brief outputs/retry-brief.md --video outputs/smoke.mp4 --design-note outputs/design-note.md --renderer outputs/storyboard.md --expect-width 1280 --expect-height 720 --expect-fps 30 --expect-duration 2 --duration-tolerance 0.5 --require-audio --require-design-note --require-renderer --min-size-bytes 1 --json > outputs/package-validation.json'
```

Convert a small animated SVG into a GIF.

Requirements:

- Use the `animated-svg-to-gif` skill.
- Read `../prompt.md` first, then work only from the copied skill and this prompt. Do not look elsewhere outside the workspace.
- Create exactly `pulse.animated.svg` in the workspace root. It should be a self-contained SVG with a white background, a labeled circle, and a simple CSS or SMIL pulse animation that lasts about 2 seconds.
- Use the skill script to convert it to exactly `pulse.gif` at 12 fps, white background, width 360, duration 2 seconds, and scale 1.
- Keep the converter-generated item manifest at exactly `pulse.manifest.json` and the run manifest at exactly `conversion-manifest.json`, beside `pulse.gif`.
- Verify the exact file `pulse.gif` with `ffprobe` if available. If `ffprobe` is unavailable, verify the file exists and has nonzero size.
- Keep outputs in the workspace root. Apart from the required first read of `../prompt.md`, do not read any other path outside the workspace root.
- At the end, print a concise summary of files created and validation checks.

Convert a small animated SVG into a GIF.

Requirements:

- Use the `animated-svg-to-gif` skill.
- Work only from the copied skill and the prompt. Do not look outside the workspace.
- Create exactly `pulse.animated.svg` in the workspace root. It should be a self-contained SVG with a white background, a labeled circle, and a simple CSS or SMIL pulse animation that lasts about 2 seconds.
- Use the skill script to convert it to exactly `pulse.gif` at 12 fps, white background, width 360, duration 2 seconds, and scale 1.
- Verify the exact file `pulse.gif` with `ffprobe` if available. If `ffprobe` is unavailable, verify the file exists and has nonzero size.
- Keep outputs in the workspace root. Do not read files outside the workspace root, including `../command.txt` or `../prompt.md`.
- At the end, print a concise summary of files created and validation checks.

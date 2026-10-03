Use the copied `pixel-art-image-video` skill to demonstrate exact source-color pixel art in this isolated workspace. Do not edit the copied skill bundle.

Use the skill's `uv run --script` commands for conversion and validation. Bare `python` may not have Pillow installed; use `uv` for Python dependencies or use `ffmpeg` for source generation.

Create an opaque `source.png` with a recognizable geometric composition and more than 64 distinct RGB colors. Convert it to `exact.png` at 160 × 96 with a 4-pixel logical block using the skill's exact source-color option. Write `exact.json` and run the bundled validator into `exact-validation.json`. The output must use original sampled RGB values, not a fitted palette.

Also create a one-second `source.mp4` with visible motion and an audio track using local tools. Convert it to a 160 × 96, 8 fps, 4-pixel-block lossless video at `exact.mkv`, preserving decoded source RGB colors and audio. Write `exact-video.json`, a contact sheet at `exact-contact.png`, and the validator result at `exact-video-validation.json`.

Inspect the still and contact sheet. In your final response, state the still and video logical grids, whether the exact source-color checks passed, and any format limitation relevant to MP4 or GIF. Create every requested file at its exact workspace-root path.

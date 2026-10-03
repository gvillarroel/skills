# Video and animated-image workflow

Use a local video or animated raster as input and `.mp4`, `.gif`, or `.mkv` as output. The converter uses `ffprobe` to inspect dimensions, duration, codec, and audio; `ffmpeg` samples the selected interval at a constant rate and reduces it to the logical grid. In palette-limited modes it fits one palette from uniformly spaced samples and quantizes every frame with identical settings. In `--palette preserve` mode it samples decoded RGB pixels with nearest-neighbor instead, without quantization or color adjustment. Every frame is enlarged with nearest-neighbor sampling and encoded in the requested format.

`--start` selects a nonnegative source offset. `--duration` defaults to the remaining source duration, but each invocation is capped at 120 seconds and 600 frames by default. `--fps` defaults to 12 and may be 1–60. The script also rejects jobs above a 300-million output-pixel-frame budget; lower dimensions, frame rate, or duration rather than bypassing that guard blindly.

For a color-preserving HD source:

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py input.mp4 -o output.mp4 --quality-profile detailed --width 1280 --height 720 --fps 15 --start 0 --duration 4 --palette adaptive --colors 32 --contact-sheet contact.png --json-report output.json
```

For an exact four-color animated GIF:

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py input.gif -o output.gif --quality-profile balanced --fps 12 --palette forest4 --loop 0 --contact-sheet contact.png --json-report output.json
```

For exact decoded source RGB colors in a lossless video container:

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py input.mp4 -o output.mkv --quality-profile detailed --fps 12 --palette preserve --contact-sheet contact.png --json-report output.json
uv run --script skills/pixel-art-image-video/scripts/validate_pixel_art.py output.mkv --manifest output.json --expect-palette-mode preserve
```

MP4 uses H.264/YUV 4:2:0 for broad playback compatibility and re-encodes selected source audio to AAC unless `--audio drop` is set. MKV uses lossless FFV1 with RGB-family `bgr0` pixels and lossless FLAC for decoded source audio; it is larger and less universally playable. The manifest records `sourceAudio` and `audioKept`; the validator checks the actual stream and compares every decoded MKV frame to the corresponding source RGB sample in `preserve` mode. GIF cannot carry audio and may quantize timing to 10 ms increments. GIF preserves its *resulting* palette and block grid, but it cannot guarantee arbitrary original RGB values; MP4 may show nearby colors or softened chroma at block edges.

Inspect a contact sheet and the actual animation. A contact sheet proves broad motion progression but cannot reveal a bad loop seam, occasional blank frame, sound sync, or compression artifacts. Use the independent validator for frame count, distinct decoded frames, dimensions, approximate rate/duration, palette contract for GIF, and audio presence for MP4. If sound timing or an especially tight loop is important, also inspect playback manually and use `ffprobe` to compare audio/video stream durations.

This skill does not directly execute JavaScript-driven SVG animation, Canvas, WebGL, or browser interaction. Capture those to a local video or animated raster first. Static SVG images are supported directly through the still-image path; authored JavaScript is disabled and external resources are blocked there.

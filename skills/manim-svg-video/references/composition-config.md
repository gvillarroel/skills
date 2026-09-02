# Composition Configuration

Use `scripts/compose_svg_video.py` as the stable entrypoint for Manim SVG video composition.

Set `$env:MANIM_SVG_VIDEO_SKILL` to the skill directory, then invoke the script through
`$env:MANIM_SVG_VIDEO_SKILL/scripts/compose_svg_video.py`. Keep outputs in the current
project rather than in the skill bundle.

## Commands

Generate the manifest and Manim scene without rendering:

```powershell
uv run --script $env:MANIM_SVG_VIDEO_SKILL/scripts/compose_svg_video.py --discover-root path/to/animated-svgs --out projects/<project-id>/artifacts/videos/svg-sequence --duration 12 --max-assets 6 --dry-run
```

Render a low-cost smoke MP4 before a long render:

```powershell
uv run --script $env:MANIM_SVG_VIDEO_SKILL/scripts/compose_svg_video.py --discover-root path/to/animated-svgs --out projects/<project-id>/artifacts/videos/svg-sequence-smoke --duration 12 --max-assets 6 --layout replace --active-slots 1 --render --quality l --fps 5 --resolution 640,360
```

After the smoke passes, keep the same source and layout contract while increasing duration,
fps, resolution, or Manim quality for the requested deliverable.

## Timing

- `--duration`: total target video length in seconds. Use `600` for 10 minutes.
- `--active-slots`: number of SVGs introduced in the same wave. Higher values make more animations coexist; lower values give each SVG more screen time.
- `--enter-seconds`: duration of each wave entrance animation.
- `--pulse-every-seconds`: cadence for subtle active-wave movement during long dwell periods.
- `--pulse-seconds`: duration of each active-wave pulse.
- `--no-exact-duration`: disable the default ffmpeg pad/trim pass that makes the final MP4 match `--duration`.

The script divides the total duration across waves, tracks elapsed time in the generated scene, and waits at the end if needed so the output reaches the configured duration.
Manim can still round long multi-segment renders by a few frames, so exact-duration post-processing is enabled by default.

## Layout

The default layout is `replace`: every wave occupies fixed slots, plays for its share of the timeline, fades out, and is replaced by the next wave.

Use:

- `--layout replace --active-slots 1` for one full-screen SVG at a time.
- `--layout replace --active-slots 2` for two half-screen SVGs at a time.
- `--layout replace --active-slots 4` for four quarter-screen SVGs at a time.

Use `--layout mosaic` only when every SVG should keep a final grid cell after its entrance. In mosaic mode, a larger `--active-slots` value creates denser simultaneous entrances; for dozens of SVGs, start with `12` at 16:9.

## Palette

The default palette uses a white scene background with light tiles:

- `--background #ffffff`
- `--title-color #111827`
- `--tile-fill #f8fafc`
- `--tile-stroke #cbd5e1`
- `--label-color #334155`

When changing the background, adjust the title, tile, and placeholder colors together so the title, empty regions, and conversion placeholders stay readable.

## Discovery

Default discovery searches for `**/*.animated.svg` below each `--discover-root`, excluding `node_modules`, `.git`, and generated Manim media internals. Use repeated `--include` flags to add patterns, or `--from-list` with one SVG path per line for exact ordering.

For an input named `name.animated.svg`, the script tries to render from static companions in this order:

1. Same directory: `name.static.svg`.
2. Sibling static directory: `../static/name.static.svg` when the animated file is under an `animated/` folder.
3. The original animated SVG when no static companion exists.

The manifest keeps both `source` and `render_source` so it is clear which animated SVG was selected and which file was used for visual import.

## Outputs

Each run writes:

- `composition-manifest.json`: selected assets, render sources, conversion errors, scene path, and render settings.
- `manim_svg_video_scene.py`: generated Manim scene.
- `assets/*.png`: rasterized SVGs when `--import-mode image` is used and a local rasterizer is available.
- `media/`: Manim output, including MP4 after `--render`.
- `rendered_video_raw` in the manifest when the raw Manim MP4 required duration repair.

Keep all of these under `projects/<project-id>/artifacts/videos/` for project-scoped validation hygiene.

## Validation

Before delivery:

1. Confirm `asset_count` and source ordering in `composition-manifest.json`.
2. Resolve or report every non-null `conversion_error`.
3. Inspect at least the first, middle, and final rendered states at full resolution.
4. Probe the MP4 with `ffprobe`; verify exact width, height, fps, codec, and duration against the request.
5. Confirm the manifest's `rendered_video` exists and that exact-duration repair did not silently replace the requested visual settings.

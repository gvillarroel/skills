---
name: pixel-art-image-video
description: "Converts local raster or SVG images and local videos or animated rasters into crisp pixel art with adaptive, custom, or exact source colors. Use for retro game-style PNG/WebP stills, MP4/GIF motion, lossless MKV video, and image-dependent pixel-density tuning; do not use when the source must remain editable vector art or JavaScript-driven SVG motion needs direct capture."
---

# Pixel Art Image and Video

Turn source imagery into a low-resolution logical color grid, then enlarge it with nearest-neighbor sampling. The shipped converter supports still PNG/lossless WebP output from raster, self-contained SVG, or one video frame, and animated MP4/GIF or lossless MKV output from local video or animated raster input. The output format follows `--output`. Keep generated files outside this skill directory and honor exact user-provided paths.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. Prefer saturated/base colors, then dark, bright and neutral solids, with soft fills late. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

## Choose the look

Use `--palette colorset1` by default or `--palette colorset2` for extended semantic categories. The bundled [colorsets.json](assets/palettes/colorsets.json) defines exact allowed paints. Adaptive fitting maps source medoids to `--colorset` tokens; custom colors and backgrounds must belong to that active set. `forest4` and `sunset8` are compact colorset2 subsets. Use `preserve` only when exact source RGB is explicitly required; its manifest declares `paintScope: source-fidelity` and no colorset claim. Review sheets use colorset1 chrome. Decoded lossy video and antialiased edges can contain derived tones; test authored palette membership before encoding and use lossless PNG/WebP/GIF/MKV for an exact pixel-color deliverable.

Start with the smallest feature that must remain recognizable:

- `chunky`: large silhouettes, icons, bold portraits, or an intentionally coarse 8-pixel block.
- `balanced`: ordinary illustrations or footage; a 5-pixel block and 24 adaptive colors.
- `detailed`: thin contours, faces, charts, or small labels; a 3-pixel block and 32 adaptive colors. If text remains unreadable, use `--pixel-size 2` or preserve a non-pixelated text layer outside this conversion.
- `manual`: the neutral baseline when all meaningful values will be overridden.

Profiles set pixel size and adaptive palette count. Explicit `--pixel-size` and `--colors` override those fields independently. Read [references/quality-and-palettes.md](references/quality-and-palettes.md) when selecting a palette, tuning dither, handling alpha, or judging whether the result still communicates the source.

`--palette adaptive` fits a limited palette from the source. For animation, it fits one palette from frames spread across the selected timeline and reuses it throughout. `forest4` and `sunset8` are fixed palettes; `custom` requires two or more repeated `--color` arguments. `--palette preserve` keeps the exact RGB values of selected source pixels, without a color-count limit; it uses nearest-neighbor source sampling, disables color enhancement and dither, and requires PNG/lossless WebP for stills or FFV1 MKV for motion. Read [references/quality-and-palettes.md](references/quality-and-palettes.md) for the exact-color contract and transparency boundary. For reduced palettes, prefer `--dither none` for clean clusters or `bayer4` for deliberate texture; Floyd–Steinberg may shimmer in motion.

## Convert a still

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py source.png -o result.png --quality-profile balanced --palette colorset1 --json-report result.json
```

To pixelate while keeping the sampled source RGB values exactly, including sources with more than 64 colors:

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py source.png -o exact-pixel.png --quality-profile detailed --palette preserve --json-report exact-pixel.json
uv run --script skills/pixel-art-image-video/scripts/validate_pixel_art.py exact-pixel.png --manifest exact-pixel.json --expect-palette-mode preserve
```

For a small labeled illustration, increase the final canvas while retaining a fine logical grid:

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py source.svg -o result.webp --quality-profile detailed --width 1280 --height 720 --pixel-size 2 --palette custom --color "#333e48" --color "#9e1b32" --color "#828282" --color "#ffffff" --json-report result.json
```

Raster input honors EXIF orientation. Transparent static input is converted to a hard alpha grid by default; use `--alpha flatten --background "#ffffff"` when the deliverable must be opaque. SVG rendering disables authored JavaScript and blocks external or local sidecar resources; data-embed required images/fonts. `--start` selects a still from a video source.

## Convert motion

Read [references/video.md](references/video.md) before a long or high-resolution render. `ffmpeg` and `ffprobe` must be available for motion conversion.

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py source.mp4 -o result.mp4 --quality-profile detailed --width 1280 --height 720 --fps 12 --palette colorset1 --contact-sheet result-contact.png --json-report result.json
```

For exact source colors in video, select MKV/FFV1 rather than MP4 or GIF:

```powershell
uv run --script skills/pixel-art-image-video/scripts/pixel_art.py source.mp4 -o exact-pixel.mkv --quality-profile detailed --fps 12 --palette preserve --json-report exact-pixel-video.json
uv run --script skills/pixel-art-image-video/scripts/validate_pixel_art.py exact-pixel.mkv --manifest exact-pixel-video.json --expect-palette-mode preserve --expect-audio keep
```

MP4 and MKV keep source audio by default; pass `--audio drop` to remove it. GIF has no audio and uses `--loop 0` for infinite repetition. Use `--start` and `--duration` to select a bounded interval. The converter caps frame count and output pixels so an accidental long 4K job cannot exhaust temporary storage. MP4/H.264 is broadly playable but lossy; MKV/FFV1 preserves decoded RGB values but is larger and less universally playable. GIF/PNG/WebP preserve their resulting palette and blocks, but GIF cannot keep arbitrary source RGB colors.

## Review and validate

Inspect the still at native size and at 2–4× nearest-neighbor zoom. For animation, inspect the GIF/MP4 and its contact sheet: movement, loop seam, static-region stability, faces, small symbols, and labels matter more than nominal resolution. If the feature is lost, reduce `--pixel-size` first; if the palette muddies color regions, adjust `--colors` or supply a custom palette. Do not claim an exact pixel-art recreation of proprietary game assets.

Run the independent validator with the manifest:

```powershell
uv run --script skills/pixel-art-image-video/scripts/validate_pixel_art.py result.png --manifest result.json --expect-pixel-size 5 --expect-palette-mode colorset1 --expect-colorset colorset1 --max-colors 17
```

For motion, pin dimensions, rate, duration, real frame changes, and audio:

```powershell
uv run --script skills/pixel-art-image-video/scripts/validate_pixel_art.py result.mp4 --manifest result.json --expect-width 1280 --expect-height 720 --expect-pixel-size 3 --expect-fps 12 --min-frames 12 --min-distinct-frames 3 --expect-audio keep
```

The validator checks palette membership and a reversible nearest-neighbor grid for palette-limited stills/GIFs; in `preserve` mode it compares every visible output RGB value to the corresponding nearest-neighbor source sample, including all decoded MKV frames. It also checks output/source checksums, motion, timing, and audio streams. For MP4 it checks the declared palette size rather than exact decoded colors because H.264 compression introduces nearby tones. Report the source format, profile, logical grid, palette mode or exact-color contract, output size, frame rate/duration, whether audio survived, and any intentional label loss.

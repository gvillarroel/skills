# Animated SVG or raster to GIF guide

## Runtime contract

Use `scripts/stylize_animated_image.py` when motion must survive. For SVG input, Chromium samples self-contained CSS and SMIL animation at explicit timeline positions. For raster input, Pillow decodes and composites GIF, animated WebP, APNG, and other supported multi-frame formats. The script flattens each sampled frame onto an opaque background, uses a constant output rate, applies the same ordered-dither phase throughout, and runs a two-pass ffmpeg palette workflow over the complete timeline.

Animated SVG input requires `--duration-seconds`; it defines the capture window and therefore the delivered loop. Authored JavaScript and event handlers remain disabled, external requests are blocked, and only declarative SVG/CSS/SMIL motion is sampled. Inline or data-embed fonts and images. Raster input defaults to one decoded source cycle and uses `--duration-seconds` only to trim or repeat it.

Do not use this path for a static source merely to manufacture motion. Do not claim that variable frame durations are preserved exactly: GIF timing is quantized to centiseconds and the script approximates the source timeline at `--fps`. For a static rendition of one animated frame, use `stylize_svg.py --frame N` instead.

## Quality routing

Start with the smallest meaningful moving feature, not the source canvas size alone:

| Target | Starting profile | Playback | Notes |
| --- | --- | ---: | --- |
| Small chat preview | `compact` | 8–10 fps | Prioritize silhouettes and file size. |
| General illustration | `balanced` | 10–12 fps | Good default for moderate motion. |
| 1280×720 showcase | `detailed` | 12–15 fps | Keeps a 640×360 effective grid at cell size 2. |
| Fine or fast motion | `detailed` | 18–24 fps | Verify file size and motion cadence; GIF is inefficient at video-like rates. |

Prefer this reduction order when the file is too large:

1. Shorten the duration or trim a redundant loop.
2. Lower `--fps` while checking that motion still reads.
3. Reduce render dimensions while preserving aspect ratio.
4. Increase `--cell-size` only after the first three, because it discards spatial detail.

For 1-bit `original` and `custom` output, pass `--colors 2`; both modes already contain exactly two visible tones. Regional mode may use more colors, so leave `--colors 256` unless a tighter palette is intentional.

## Stable animation rules

- Keep the same `--matrix-size`, grid origin, cell size, contrast, and dimensions across every frame. Per-frame random noise creates shimmer; the supplied engine uses a fixed ordered Bayer phase.
- Regional mode selects medoids from an animation-wide histogram and reuses them for every frame. Do not quantize each frame independently because close hues can swap cluster identities and flicker.
- Use an opaque `--background`; GIF transparency is one-bit and can produce jagged halos around antialiased edges. White is the default and matches the two-tone modes.
- For raster input, let the source define one cycle by default. `--duration-seconds` samples cyclically, so a longer duration repeats the source rather than inventing in-between motion.
- For SVG input, pass the actual declarative loop duration. The sampler evaluates timestamps from zero through the last frame before the endpoint; an indefinite SVG animation therefore loops cleanly when its declared cycle and `--duration-seconds` agree.
- Keep `--loop 0` for an infinite loop. Use a positive integer only when the consuming platform honors finite GIF loop metadata.
- The script limits output frames with `--max-frames`; raise that cap only after estimating `duration × fps` and accepting the memory and encoding cost.

## Mode recipes

Direct animated SVG capture, classic black and white, high-definition:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_animated_image.py chart.animated.svg -o result.gif --mode original --quality-profile detailed --render-width 1280 --render-height 720 --fps 15 --duration-seconds 3 --colors 2 --contact-sheet result-contact.png --json-report result.json
```

Animated raster, classic black and white, high-definition:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_animated_image.py source.gif -o result.gif --mode original --quality-profile detailed --render-width 1280 --render-height 720 --fps 12 --colors 2 --contact-sheet result-contact.png --json-report result.json
```

Custom ink plus white:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_animated_image.py source.webp -o result.gif --mode custom --color "#283845" --quality-profile detailed --fps 12 --colors 2 --contact-sheet result-contact.png --json-report result.json
```

Animation-wide source-color regions:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_animated_image.py source.png -o result.gif --mode regional --quality-profile balanced --region-colors 8 --fps 12 --contact-sheet result-contact.png --json-report result.json
```

## Validation and review

Run the independent validator with the requested dimensions, approximate frame rate, loop, mode, and palette limit. The validator inspects every decoded frame, requires positive timing, checks the union of visible colors, and cross-checks the manifest when supplied.

```powershell
uv run --script skills/one-bit-dither-svg/scripts/validate_animated_gif.py result.gif --manifest result.json --expect-mode custom --expect-custom-color "#283845" --expect-source-kind raster --expect-source-format WEBP --expect-width 1280 --expect-height 720 --expect-fps 12 --expect-loop 0 --min-frames 2 --min-distinct-frames 2 --max-colors 2
```

Then review the actual loop and the contact sheet:

- Confirm at least one meaningful object changes between frames; a multi-frame container with duplicate frames is not a useful animation.
- Check the last-to-first transition as carefully as adjacent frames.
- Look for a stationary ordered-dither texture on static objects and coherent movement on moving objects.
- In regional mode, verify that a source hue keeps the same representative color throughout the cycle.
- Inspect the first, middle, and final frames at native size. Also zoom 2× with nearest-neighbor scaling to catch accidental resampling blur.
- Use `ffprobe` when delivery requires an independent codec, dimension, duration, or frame-count record.

## Boundaries

- Self-contained CSS and SMIL SVG are direct inputs. JavaScript-driven SVG, HTML canvas, video, remote URLs, and browser interaction are not; capture those into a local raster animation before using this skill.
- The SVG sampler blocks external URLs and local sidecar files. Data-embed every required font and image so the source is portable and deterministic.
- GIF stores frame delays in 10 ms units. An exact requested rate such as 12 fps becomes an alternating 80/90 ms cadence, so validate with a tolerance instead of expecting identical per-frame delays.
- GIF is limited to 256 palette entries. The three one-bit modes are intentionally compatible with that limit, but dense regional palettes and long high-definition timelines can still produce large files.

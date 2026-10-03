---
name: one-bit-dither-svg
description: "Transforms local SVGs and raster images into self-contained pixel SVGs, or restyles declarative animated SVGs and animated raster images as palette-optimized GIFs, with a one-bit dithered engraving aesthetic. Includes Obra Dinn-inspired black-and-white, custom-color-and-white, and region-aware source-color modes. Use for retro 1-bit, stippled, or high-contrast treatment of illustrations, photos, screenshots, logos, diagrams, SVG/CSS/SMIL animation, and animated GIF/WebP/APNG files; not when source editability, JavaScript-driven motion, or interaction must remain intact."
---

# One-Bit Dither Image and Animation

Load a local image, reduce it to a controlled ordered-dither grid, and emit either a static SVG or an animated GIF. For static output, accept a self-contained SVG or any raster format Pillow can read and rebuild the grid as run-length-compressed SVG rectangles. For animated output, either sample a self-contained CSS/SMIL SVG at explicit browser timeline positions or decode every composited raster frame, then keep one stable grid and regional palette across the timeline and encode a GIF with a whole-animation ffmpeg palette. Source pixels, paths, text objects, and interaction are intentionally flattened.

## Solid-fill presentation

For authored filled marks and preview chrome, start with one opaque colorset fill and no decorative border. Prefer saturated/base colors, then dark, bright and neutral solids, with soft fills late. Assign unique usable fills before introducing border variants; exclude the actual canvas color. Choose exact black or white text on each fill by maximum relative-luminance contrast. Keep semantic mappings stable across previews, legends and exports. Only after the usable solid colors are exhausted, expand with contrasting palette border colors, dash patterns and widths. Preserve meaningful line art, connectors, keyboard focus indicators, original source media and explicitly requested conversion aesthetics. Apply this preference to newly authored visuals and framing; preserve required source identity and fidelity.

Keep zoom previews and verification helpers in the active workspace, for example `regional-zoom.png`. Read the same workspace-relative path with the image tool; do not use `/tmp` or an external temporary directory. If a new Python verification helper needs Pillow, declare `pillow` in its own uv script metadata and run it with `uv run --script` so it has the dependency independently of the converter.

## Choose one mode

Use `--colorset colorset1` by default or `--colorset colorset2` for extended paint. The bundled [colorsets.json](assets/palettes/colorsets.json) defines exact allowed tokens. Original black/white already fits colorset1; custom ink must belong to the selected set. Regional source medoids retain region geometry but map their authored ink to the nearest active token before pairing it with black or white. Both static SVG and GIF validators reject off-palette paints. Describe regional results as palette restyling, not preservation of original RGB values.

- `original`: use only black and white. Choose this for the closest general 1-bit terminal/engraving treatment.
- `custom`: use one user-selected color plus white. Require a `#RGB` or `#RRGGBB` color.
- `regional`: quantize the rendered source into local color regions. Pair every dark region with white and every light region with black according to the stronger WCAG contrast ratio.

Do not claim an exact reproduction of proprietary game assets, fonts, interfaces, or palettes. The reusable mechanism is ordered 1-bit dithering inspired by the broad visual grammar of *Return of the Obra Dinn*.

## Transform

Keep generated artifacts outside the skill directory. Use exact requested paths when the user supplied them.

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py input.png -o output.svg --mode original --quality-profile balanced --preview-png output.png --json-report output.json
```

For a custom color:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py input.jpg -o output.svg --mode custom --color "#9e1b32" --quality-profile balanced --preview-png output.png --json-report output.json
```

For source-color regions:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py input.webp -o output.svg --mode regional --quality-profile balanced --preview-png output.png --json-report output.json
```

Raster inputs honor EXIF orientation, preserve alpha, and use high-quality Lanczos resizing. GIF, animated WebP, and multipage TIFF inputs use frame zero unless `--frame N` selects another frame. SVG inputs still use browser-accurate rendering while blocking external resources and disabling source JavaScript; inline or embed required SVG images and fonts before conversion.

## Preserve SVG or raster animation as GIF

Use the animated script when motion, timing, and looping must survive. It directly accepts self-contained SVGs animated with CSS or SMIL, plus any multi-frame raster Pillow can decode, including GIF, animated WebP, and APNG. `ffmpeg` must be on `PATH`.

For animated SVG, define the capture window explicitly. The browser sampler disables authored JavaScript, blocks external resources, freezes SMIL and CSS animation at each frame timestamp, and feeds those frames directly into the one-bit renderer:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_animated_image.py chart.animated.svg -o chart-one-bit.gif --mode original --quality-profile detailed --render-width 1280 --render-height 720 --fps 15 --duration-seconds 3 --colors 2 --contact-sheet chart-contact.png --json-report chart.json
```

For an animated raster, omit `--duration-seconds` to preserve one decoded source cycle:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_animated_image.py input.gif -o output.gif --mode original --quality-profile detailed --render-width 1280 --render-height 720 --fps 12 --colors 2 --contact-sheet output-contact.png --json-report output.json
```

Use the same `--mode`, `--color`, `--region-colors`, cell, matrix, and contrast controls as the static path. The script samples or decodes the source, shares one animation-wide regional palette to prevent color flicker, flattens transparency onto `--background`, and defaults to infinite looping. For SVG, `--duration-seconds` is required because declarative animations do not expose one reliable universal cycle duration. For raster input, use it only when intentionally trimming or repeating the decoded source cycle. Read [references/animation-guide.md](references/animation-guide.md) before increasing frame rate, duration, or dimensions.

## Route quality, then inspect

Inspect the source structure and choose one baseline before rendering:

- `compact`: broad silhouettes, large flat shapes, disposable previews, or strict file-size limits.
- `balanced`: ordinary illustrations, logos, and charts whose identity does not depend on small type.
- `detailed`: labels, thin strokes, small symbols, dense diagrams, or any source where losing a narrow feature changes meaning.
- `manual`: legacy baseline for fully explicit tuning.

Named profiles set render width, cell size, matrix size, contrast, and regional color count together. Any explicit tuning flag overrides only that profile field. Escalate from `balanced` to `detailed` when native-size inspection loses text or a semantically important line; do not use `detailed` reflexively because it materially increases output size. Read [references/mode-guide.md](references/mode-guide.md) for the exact presets, override order, regional color guidance, and rendering failures.

Always inspect the PNG preview at native size and at 2–4× nearest-neighbor zoom. Check recognizable silhouettes, important internal edges, balanced light/dark mass, stable color regions, and the absence of accidental moiré or illegible text. Prefer changing `--cell-size`, then `--contrast`, then `--matrix-size`; do not compensate for lost semantic detail by merely increasing the final SVG display size.

For GIF output, inspect the contact sheet and the animation itself. Confirm actual motion, a clean loop seam, stable dither texture, stable regional colors, and readable silhouettes at playback size. A nominally high-resolution canvas is not high quality when the dither grid is too coarse; for 1280×720, start with `detailed` (`--cell-size 2`) and reduce frame rate before reducing spatial detail when file size is excessive.

## Validate

Run the structural validator after the visual review:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/validate_stylized_svg.py output.svg --expect-mode original
```

For custom mode, also pass the requested color:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/validate_stylized_svg.py output.svg --expect-mode custom --expect-custom-color "#9e1b32"
```

For raster input, also pin provenance when the input contract matters:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/validate_stylized_svg.py output.svg --expect-mode regional --expect-source-kind raster --expect-source-format PNG --expect-source-frame 0
```

Validate an animated GIF independently from its conversion manifest:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/validate_animated_gif.py output.gif --manifest output.json --expect-mode original --expect-source-kind svg --expect-source-format SVG --expect-width 1280 --expect-height 720 --expect-fps 15 --expect-loop 0 --min-frames 2 --min-distinct-frames 2 --max-colors 2
```

The final static SVG must contain only local vector rectangles and metadata—no raster `<image>`, script, `foreignObject`, or external reference, even when the input was raster. The final GIF must have multiple positively timed and visually distinct frames, the requested dimensions and loop behavior, and no colors outside its mode contract. Report the source kind and format, browser capture or decoded-raster path, selected frame or animated frame count, mode, quality profile, custom color or regional count, render size, cell size, matrix size, playback rate, duration, palette size, and any intentional flattening limitation in the handoff.

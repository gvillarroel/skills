# Mode and tuning guide

## Contents

- [Visual contract](#visual-contract)
- [Modes](#modes)
- [Tuning order](#tuning-order)
- [Common recipes](#common-recipes)
- [Input and rendering boundaries](#input-and-rendering-boundaries)
- [Visual review checklist](#visual-review-checklist)

## Visual contract

This skill implements a general one-bit engraved/pixel treatment through browser-accurate SVG rendering or Pillow-based raster loading, ordered Bayer thresholding, and reconstruction as crisp SVG rectangles. Its animated path reuses the same grid logic for each composited raster frame and encodes the results as a GIF. It does not copy game artwork, fonts, UI, code, or an extracted proprietary palette.

Every mode uses the source's rendered luminance to decide the ordered-dither pattern. Transparent cells remain transparent. Semi-transparent cells below `--alpha-threshold` are omitted; other cells become fully opaque marks.

## Modes

### `original`

- Output colors: `#000000` and `#ffffff` only.
- Best for silhouettes, line art, engraving, stark scenes, and the most recognizable 1-bit result.
- If the image becomes too dark, reduce `--contrast` slightly or choose a smaller Bayer matrix. If it becomes washed out, raise `--contrast`.

### `custom`

- Output colors: the exact normalized `--color` value and `#ffffff` only.
- The custom color replaces black; white remains the light tone.
- Prefer colors with visible contrast against white. Deep red, blue, green, violet, or brown usually read better than pale colors.
- The script rejects white as the custom color because it would collapse both tones.

### `regional`

- The renderer clusters visible source cells into `--region-colors` source medoids with deterministic OKLab clustering, then maps each region's authored ink to the nearest token in `--colorset colorset1` (default) or `colorset2`. Frequency, perceptual distance, and chroma preserve small source zones in the clustering; output RGB values intentionally follow the active colorset. Regions can share a paint after mapping, so inspect boundaries before delivery.
- Each cell keeps its assigned representative region color.
- Each dark representative color is paired with white. Each light representative color is paired with black. The choice is whichever companion has the higher WCAG contrast ratio.
- Within a region, ordered dithering alternates only between that region color and its chosen companion. This preserves the source's color geography without reverting to unrestricted full color.
- Start with 6–10 regions. Use 3–5 for poster-like blocks and 12–16 for artwork whose identity depends on several distinct hues. More regions do not restore vector editability or fine geometry.

## Tuning order

Choose a named baseline from the source's smallest meaningful feature:

| Profile | Render width | Cell | Matrix | Contrast | Regional colors | Route when |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `compact` | 768 | 5 | 4 | 1.25 | 6 | Broad silhouettes and large flat shapes; size matters more than detail. |
| `balanced` | 960 | 3 | 4 | 1.15 | 8 | General illustrations, logos, and charts with comfortably sized marks. |
| `detailed` | 1280 | 2 | 4 | 1.05 | 12 | Small text, thin strokes, dense symbols, or narrow semantic edges. |
| `manual` | 768 | 4 | 4 | 1.15 | 8 | Compatibility baseline or a fully hand-tuned run. |

Pass the selection with `--quality-profile`. Explicit `--render-width`, `--cell-size`, `--matrix-size`, `--contrast`, or `--region-colors` values override just their matching preset values. Compare the preview at native size before accepting an escalation: `detailed` samples about eleven times as many cells as `compact` at the same aspect ratio and can produce much larger SVGs.

Then override fields in this order:

1. `--cell-size`: controls information density. Lower values preserve detail but create larger SVGs. Typical range: 2–6.
2. `--contrast`: expands or compresses luminance around the midpoint before thresholding. Typical range: 0.9–1.5.
3. `--matrix-size`: selects a 2×2, 4×4, or 8×8 Bayer texture. Use 2 for coarse checker texture, 4 for the default balance, and 8 for finer tonal steps that can look more obviously patterned.
4. `--render-width` and optional `--render-height`: define the settled raster frame before cells are sampled. Increasing render size helps only when paired with an appropriate cell size.
5. `--region-colors`: regional mode only. Raise it only when distinct source hues are being merged incorrectly.

Keep the product of the render dimensions reasonable. The script caps each dimension at 4096 pixels and rebuilds the sampled grid as run-length-compressed rectangles.

## Common recipes

Fine line art or compact labels from SVG or raster input:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py source.png -o result.svg --mode original --quality-profile detailed --preview-png result.png --json-report result.json
```

Bold custom ink:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py source.jpg -o result.svg --mode custom --color "#274690" --quality-profile compact --preview-png result.png --json-report result.json
```

Regional poster treatment:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py source.webp -o result.svg --mode regional --quality-profile balanced --region-colors 6 --contrast 1.1 --preview-png result.png --json-report result.json
```

Animated-image frame selection:

```powershell
uv run --script skills/one-bit-dither-svg/scripts/stylize_svg.py source.gif -o result.svg --mode original --frame 3 --quality-profile balanced --preview-png result.png --json-report result.json
```

To preserve motion rather than select one frame, use `stylize_animated_image.py` and follow [animation-guide.md](animation-guide.md).

## Input and rendering boundaries

- Supply a local SVG or a raster image Pillow can decode. Common supported formats include PNG, JPEG, WebP, GIF, TIFF, and BMP; additional formats depend on the installed Pillow build. HTML pages, remote URLs, PDF pages, canvas state, and video are outside this skill's direct input contract.
- Raster inputs are oriented from EXIF before their aspect ratio is calculated, converted to RGBA, resized with Lanczos, and kept transparent where their alpha is below `--alpha-threshold`.
- With `stylize_svg.py`, animated GIF/WebP and multipage TIFF inputs are flattened to one zero-based `--frame`; frame zero is the default. Use `stylize_animated_image.py` when timing, composited disposal behavior, and motion must be preserved as a GIF.
- For SVG, make the source self-contained. HTTP(S) images, web fonts, stylesheets, and other external resources are blocked and cause conversion to fail closed. Source JavaScript is disabled, and the document's root SVG is rendered at an explicit size.
- A Chromium-compatible browser is required only for SVG inputs. Raster conversion uses Pillow and does not launch a browser.
- The static script always emits a static SVG made of rectangle runs. The animated script accepts only a multi-frame raster source and emits an animated GIF.

## Visual review checklist

- Compare the preview with the source at the same aspect ratio.
- For photos and screenshots, verify faces, text, thin UI borders, and high-frequency textures; choose `detailed` when any of those carry meaning, and avoid treating photographic noise as required detail.
- Verify focal silhouettes and at least the few internal edges needed for recognition.
- Check that transparent negative space remains transparent.
- In `custom`, confirm that no third color appears.
- In `regional`, confirm that source hues stay in their expected spatial zones and that each zone uses only its representative color plus black or white.
- Inspect diagonal edges and gradients for distracting repeating bands. Try a different matrix size or cell size when the Bayer texture dominates the subject.
- Re-render text separately or keep it outside the converted layer when readability matters; flattened small type rarely survives coarse dithering.

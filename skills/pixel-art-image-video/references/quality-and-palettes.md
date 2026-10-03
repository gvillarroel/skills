# Quality, palettes, and pixel structure

## Route by source content

Pixel art is a deliberate reduction, not just a small image scaled up. Choose the largest block that preserves the smallest *important* source feature. At 1280×720, the profiles begin near these logical grids:

| Profile | Block | Logical grid | Palette | Appropriate source |
| --- | ---: | ---: | ---: | --- |
| `chunky` | 8 | 160×90 | 16 | silhouette, sprite, bold landscape |
| `balanced` | 5 | 256×144 | 24 | illustration, portrait, ordinary footage |
| `detailed` | 3 | 427×240 | 32 | fine contours, faces, chart labels |

These are starting points, not quality rankings. A portrait may benefit from 5-pixel blocks because clusters become intentional; a chart with small numbers may need 2-pixel blocks or a separately typeset overlay. Do not treat an upscaled 1280×720 canvas as evidence of HD detail when its logical grid is only 160×90.

Inspect at native size first. Check silhouette and key regions, then eyes/facial expression, distinctive object details, and text if they carry meaning. Zoom 2–4× with nearest-neighbor only to inspect block consistency. Escalate the logical grid if important information disappears, or lower the color count if the result resembles a blurred photo more than clustered pixel art.

## Palette decisions

- `colorset1`: default exact red/neutral paints from the bundled contract.
- `colorset2`: exact extended paints from that contract.
- `adaptive`: fit medoids from the static image or a uniform sample across the timeline, then map them to nearest `--colorset` tokens. The color count is an upper bound; duplicate mapped medoids are merged. The palette is stable across video frames.
- `forest4`: fixed four-color green ramp for high-contrast monochrome scenes.
- `sunset8`: fixed eight-color warm/cool ramp for graphic scenes and atmospheric footage.
- `custom`: repeat `--color` for distinct entries from the selected colorset. Arbitrary custom swatches fail rather than silently escaping the declared paint contract.
- `preserve`: do not quantize to a palette. Select existing decoded source RGB pixels with nearest-neighbor sampling, then enlarge them with nearest-neighbor blocks. This can retain thousands of distinct source colors; a source pixel's exact RGB values remain unchanged in the output. Use lossless PNG/WebP for a still or FFV1 MKV for motion.

Fixed palettes can distort the source's original hue relationships. When preserving source colors matters, start with `adaptive`, not a preset. Inspect the chosen palette in the JSON report; several near-duplicate colors indicate that the palette budget may be too high for that scene.

`--contrast` and `--saturation` are applied at the logical grid before palette mapping. Their defaults are mild (1.08 and 1.10). Large values can erase shadow structure or clip skin tones. Reduce them toward 1 when the source already has strong contrast or stylized colors.

In `preserve` mode, both defaults become 1. The converter rejects non-neutral contrast/saturation, dither, alpha flattening, and lossy MP4/GIF output because those would violate exact source colors. Pixelation still discards spatial detail: only the selected original pixel colors remain, not every source pixel. For SVG, "source RGB" means the browser-rendered pixel values at the requested output size, including edge antialiasing; it does not mean only the authored SVG fill/stroke swatches. For video, it means the decoded RGB frames sampled from the input, not colors prior to the input codec. Transparent pixels have no visible RGB contract; hard-alpha thresholding keeps the sampled RGB of visible pixels but changes their opacity.

## Dither and transparency

- `none`: cleanest contiguous color clusters and most temporally stable video.
- `bayer4`: fixed 4×4 logical-grid pattern. The grid phase never changes between frames, so texture remains attached to the canvas. `--dither-strength` controls how strongly it perturbs the nearest-color decision.
- `floyd`: diffusion at the logical grid. It can add useful ramps in still images but may shimmer during motion.

The converter never smooths enlarged logical pixels. PNG and lossless WebP retain their exact output RGB values; MKV/FFV1 does the same for motion, while MP4 is lossy. Static alpha is quantized to either fully transparent or fully opaque logical cells using `--alpha-threshold`; this intentionally sacrifices soft antialiasing for sprite-like edges. Use `--alpha flatten` and a chosen `--background` when transparency is not wanted outside `preserve` mode. MP4, MKV, and GIF outputs are opaque.

## Known failure modes

- Fine text becomes speckled or illegible. Use `detailed`, then `--pixel-size 2`, or overlay text separately after conversion.
- Gradients turn into banding. Add palette colors, try `bayer4`, or accept the banding as part of the style.
- Video colors fluctuate. Keep one timeline-wide palette; the shipped converter does this automatically. Avoid per-frame palette fitting.
- Movement stutters. Raise `--fps` only after ensuring each logical pixel carries enough spatial information; 12–18 fps often works well for game-like motion.
- File size rises quickly. Shorten the clip or lower fps before reducing the logical grid enough to lose semantic detail.

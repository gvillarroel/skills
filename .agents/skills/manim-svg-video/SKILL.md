---
name: manim-svg-video
description: Compose many SVG or animated-SVG assets into one configurable Manim-rendered video. Use when Codex needs to discover `.animated.svg` files, place multiple SVG animations in a shared timeline, keep completed SVGs occupying their final mosaic positions, generate a timed MP4 such as a 10-minute showcase, tune Manim layout/timing/import options, or validate SVG-to-video rendering.
---

# Manim SVG Video

## Core Workflow

1. Discover source SVGs first, normally with `**/*.animated.svg`, and keep generated artifacts outside skill directories under `projects/<project-id>/artifacts/videos/`.
2. Prefer `scripts/compose_svg_video.py` for video generation. It writes a manifest, rasterizes SVGs when needed, generates a Manim scene, and optionally renders MP4.
3. Use `--duration 600` for a 10-minute video. Use `--layout replace --active-slots 1` for one full-screen SVG at a time, `--active-slots 2` for two half-screen SVGs, or `--active-slots 4` for four quarter-screen SVGs.
4. Use `replace` when each completed SVG animation should leave and be replaced by the next source. Use `mosaic` only when completed SVGs should accumulate and remain visible in their final positions.
5. Keep exact-duration post-processing enabled unless debugging; the script pads or trims the rendered MP4 with ffmpeg when Manim frame rounding misses the target duration.
6. Start with `--dry-run` or a short `--duration` smoke render, then render the full video after the manifest lists the expected assets.
7. Inspect the manifest and at least one rendered frame/video. Treat missing or failed assets as findings to resolve or explicitly report.

## Resource Routing

- Read `references/composition-config.md` when tuning duration, wave size, layout, import mode, source discovery, or manifest fields.
- Read `references/manim-svg-import.md` when deciding between raster image import and vector `SVGMobject`, when text disappears, or when intrinsic SVG animation behavior matters.
- Run `scripts/compose_svg_video.py` directly. Read or patch the script only when changing compositor behavior.

## Common Commands

Generate a manifest and Manim scene without rendering:

```powershell
uv run --script .agents/skills/manim-svg-video/scripts/compose_svg_video.py --discover-root . --out projects/<project-id>/artifacts/videos/repo-animated-svg-10min --duration 600 --dry-run
```

Render a 10-minute MP4 from repository animated SVGs:

```powershell
uv run --script .agents/skills/manim-svg-video/scripts/compose_svg_video.py --discover-root . --out projects/<project-id>/artifacts/videos/repo-animated-svg-10min-replace-white --duration 600 --layout replace --active-slots 4 --import-mode svg --render --quality l --fps 5 --resolution 854,480
```

Render a faster smoke test with only a few assets:

```powershell
uv run --script .agents/skills/manim-svg-video/scripts/compose_svg_video.py --discover-root .agents/skills/mermaid-animated-svg/assets/examples/mermaid-svg-animated/animated --out projects/<project-id>/artifacts/videos/smoke --duration 12 --max-assets 6 --render --quality l --fps 5 --resolution 640,360
```

## Operating Notes

- Manim controls the timeline and coexistence choreography. Browser-native CSS or SMIL animation inside an SVG is not executed by `SVGMobject`; use Manim animations for video motion.
- Prefer static companion SVGs such as `.static.svg` for final-frame fidelity when composing from `.animated.svg`; the script resolves companions automatically when possible.
- Use the default white background and light tile palette unless the user asks for another style. Tune `--background`, `--tile-fill`, `--tile-stroke`, and `--title-color` together so titles and frames remain visible.
- Read `../ANIMATED_VISUAL_TOKENS.md` before changing default video palettes or title styling. Use the documented brand neutral for text, page/video background defaults where appropriate, and the brand palette for editable tile, highlight, and title colors.
- Use `--layout replace --active-slots 1|2|4` for full-screen, half-screen, or quarter-screen replacement videos.
- Use the default vector import for portability. Use image import only when ImageMagick, `rsvg-convert`, or Inkscape is available and raster fidelity matters more than vector editability.
- Keep long renders low resolution and low fps during validation, then increase quality only when the scene is correct.
- Treat `SVGMobject` text warnings as expected for SVGs with text nodes; switch to `--import-mode image` only when a rasterizer is installed and text fidelity is more important than vector import.

## Pattern Promotion

When a composition layout, source discovery rule, SVG import workaround, duration repair, or mosaic/replacement behavior proves reusable, update the owning reference before finishing. Use `references/composition-config.md` for layout and manifest patterns, and `references/manim-svg-import.md` for import/text/rasterization patterns. Include trigger, command, source contract, layout contract, validation checks, and any renderer limitation.

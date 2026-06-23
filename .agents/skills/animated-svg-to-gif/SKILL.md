---
name: animated-svg-to-gif
description: Convert animated SVG files into high-quality GIFs by rendering browser-accurate frames and encoding them with an optimized ffmpeg palette. Use when Codex needs to turn CSS, SMIL, Mermaid, D3, ECharts, Slidev, or other animated SVG assets into shareable GIF files, batch-convert SVG folders, tune GIF dimensions, frame rate, duration, loop behavior, or verify conversion quality.
---

# Animated SVG to GIF

## Core Workflow

1. Use `scripts/convert_animated_svg_to_gif.py` for conversion instead of static SVG rasterizers. Browser capture preserves CSS keyframes, SMIL timing, foreignObject labels, filters, markers, and SVG text rendering.
2. Prefer explicit output settings for deliverables: set `--fps`, `--width` or `--max-width`, `--scale`, and `--duration` when the target channel has size or timing constraints.
3. Let the script infer duration for generated animated SVGs that use `--am-delay` and `--am-duration`; override with `--duration` when animations are JavaScript-driven, looped, or intentionally longer.
4. Keep generated GIFs and manifests under `output/animated-svg-to-gif/` unless the user names another destination.
5. Verify every important GIF with `ffprobe` and a visual preview or contact sheet before delivery.

## Quick Commands

Convert one SVG:

```powershell
uv run --script .agents/skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py input.animated.svg --output-dir output/animated-svg-to-gif --fps 24 --scale 2
```

Convert a folder of animated SVGs:

```powershell
uv run --script .agents/skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py .agents/skills/mermaid-animated-svg/assets/examples/mermaid-svg-animated/animated --output-dir output/animated-svg-to-gif/mermaid --fps 24 --max-width 1280 --scale 2
```

Force timing and dimensions for a delivery target:

```powershell
uv run --script .agents/skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py chart.animated.svg -o chart.gif --duration 5 --fps 30 --width 960 --scale 2 --background "#ffffff"
```

Install Playwright's Chromium browser if the local cache is missing:

```powershell
uv run --script .agents/skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py diagram.animated.svg --install-browser
```

## Quality Guidance

- Use `--fps 24` for most diagrams and UI animations; use `--fps 30` for fast motion or social/video contexts.
- Use `--scale 2` by default. It multiplies the final GIF pixel dimensions from the CSS capture size; lower it only when file size is more important than crisp edges and text.
- Use `--background "#ffffff"` unless transparency is explicitly required; GIF transparency is one-bit and often causes jagged edges.
- Keep `--colors 256`, `--dither sierra2_4a`, and `--stats-mode full` for polished output. Change these only for file-size experiments.
- Use `--duration` when the source uses infinite loaders, JavaScript timelines, or CSS animations that do not expose useful timing metadata.
- Pass `--include-static` only when the user intentionally wants a GIF wrapper around a static SVG.

## Pattern Promotion

When a source family or conversion preset proves reusable, update this skill before finishing. Capture the source pattern, trigger context, recommended flags, output constraints, verification commands, and pitfalls such as static SVG skipping or duration inference. If the pattern grows beyond this file, create `references/pattern-recipes.md` and link it here.

## Validation

After changing the skill or script, run:

```powershell
uv run --script .agents/skills/animated-svg-to-gif/scripts/convert_animated_svg_to_gif.py --help
uv run --script scripts/validate-skills.py
```

For converted assets, run `ffprobe` on representative GIFs and inspect at least one generated preview frame or contact sheet. Confirm that dimensions, duration, frame rate, background, labels, and final animation state match the source intent.

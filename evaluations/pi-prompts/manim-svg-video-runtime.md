Use the loaded Manim SVG Video skill to prepare a standalone SVG-only video render.

First read `../prompt.md`. Create `inputs/pulse.animated.svg` as a small, valid, self-contained SVG with a `viewBox`, at least two visible geometric elements, and one embedded CSS or SMIL animation. Do not read repository files, sibling skills, or files outside the isolated workspace.

Then run this exact command once:

```bash
uv run --script skills/manim-svg-video/scripts/compose_svg_video.py --discover-root inputs --out outputs/svg-video --duration 4 --layout replace --active-slots 1 --max-assets 1 --dry-run
```

Inspect the generated manifest without modifying the copied skill. The required outputs are exactly:

- `outputs/svg-video/composition-manifest.json`
- `outputs/svg-video/manim_svg_video_scene.py`

Report the discovered asset count, source path, render source, import mode, duration, layout, and whether rendering was intentionally skipped.

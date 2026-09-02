---
name: manim-svg-video
description: Render one or many SVG or animated-SVG source assets into a configurable Manim-authored MP4 with SVG-only sequencing, vector or raster import, exact-duration repair, and a composition manifest. Use for standalone SVG-to-video work, animated-SVG showcases, replacement or mosaic timelines, and Manim SVG render troubleshooting that does not need mixed-media composition, cross-producer interactions, narration, or a broader video production workflow.
---

# Manim SVG Video

Set `$env:MANIM_SVG_VIDEO_SKILL` to this skill directory before invoking bundled commands.

## Ownership boundary

- Own SVG discovery, final-state companion selection, Manim import, SVG-only layout and timing, scene generation, MP4 rendering, exact-duration repair, and the composition manifest.
- Preserve source SVGs. Treat their authoring, semantics, geometry, accessibility, and native animation as producer-owned.
- Do not claim that Manim executes CSS or SMIL embedded in an SVG. Read `references/manim-svg-import.md` before choosing a source or import mode.
- Hand off the finished MP4 and manifest to `video` only when a later task needs mixed media, cross-asset interactions, narration/audio, storyboarding, or final-program composition.

## Workflow

1. Confirm that the requested deliverable is an SVG-only MP4 or SVG sequence. Route broader production work to `video` instead of recreating its contracts here.
2. Read `references/composition-config.md`; select exact duration, dimensions, fps, source order, layout, active slots, and output path.
3. Read `references/manim-svg-import.md`; choose the source state and vector or raster import deliberately.
4. Run `scripts/compose_svg_video.py` in dry-run mode. Inspect `composition-manifest.json` for the expected assets, ordering, `render_source`, and conversion failures.
5. Render a short, low-resolution smoke. Inspect visible content and timing before increasing quality or duration.
6. Render the requested MP4, keep exact-duration repair enabled, then complete the validation checklist in `references/composition-config.md`.
7. Return the MP4, manifest, generated scene, source/import warnings, and exact validation results. For downstream `video` composition, also report dimensions, fps, duration, background behavior, and the final artifact path.

## Resource routing

- `references/composition-config.md`: commands, discovery, timing, layouts, output fields, and validation.
- `references/manim-svg-import.md`: CSS/SMIL limitations, static companions, vector-versus-raster selection, and fallback behavior.
- `references/visual-tokens.md`: optional palette and typography tokens when the user asks to restyle the Manim wrapper.
- `scripts/compose_svg_video.py`: deterministic discovery, manifest generation, Manim scene generation, rendering, and duration repair.

## Maintenance

Keep reusable Manim timing or layout rules in `references/composition-config.md` and import workarounds in `references/manim-svg-import.md`. Test the script with a dry run and a real short MP4, then run repository and isolated-skill validation before marking behavior done.

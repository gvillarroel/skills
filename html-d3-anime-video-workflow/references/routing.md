# Routing

Use this reference to avoid duplicating guidance already owned by another skill.

## Owns The Cross-Stack Workflow

Use `html-d3-anime-video-workflow` for:

- research-backed multi-video planning
- deciding between Slidev recording and standalone timestamp rendering
- coordinating HTML layout, D3 SVG redraws, Anime.js preview cues, Playwright capture, ffmpeg encoding, and contact-sheet review
- production manifests and review notes
- repeated improvement passes across many videos

## Route To Existing Skills

Use `d3-animated-svg` when the question is mainly:

- which D3 visualization form to use
- how to construct deterministic SVG geometry
- how to animate D3-generated SVG marks
- how to build or validate D3 replayable galleries

Use `slidev-animejs` when the question is mainly:

- Anime.js APIs or Vue component lifecycle
- scoped selectors, cleanup, `$clicks`, or Slidev mount behavior
- SVG helper, text, layout, WAAPI, draggable, scroll, timer, or engine demos inside Slidev

Use `slidev-video` when the source is a Slidev deck and the need is:

- MP4/WebM recording
- native slide transitions
- click-state traversal
- slide screenshots, contact sheets, or `recording-manifest.json`

Use `slidev-quality-audit` before delivering complex Slidev visuals.

Use `animated-svg-to-gif` when the requested artifact is a GIF from an animated SVG.

Use `manim-svg-video` when the requested artifact is a Manim video composed from many existing SVG files.

## Boundary Decisions

- If the output is a Slidev deck, start with the Slidev skills.
- If the output is a standalone HTML animation video, start here, then load D3 or Anime.js skills only for component-specific detail.
- If the user asks to improve the video production process after a completed run, store the cross-stack lesson here and update the owning component skill only for component-local lessons.
- If a pipeline needs exact per-frame reproducibility, prefer timestamp rendering over real-time browser recording.
- If the video value depends on native Slidev transitions, prefer `slidev-video` recording rather than rebuilding the deck as standalone HTML.

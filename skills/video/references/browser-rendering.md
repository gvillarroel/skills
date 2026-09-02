# Browser Rendering and Validation

## Deterministic contract

The renderer must expose:

```js
window.renderConceptFrame(videoId, seconds, { duration })
```

It must render solely from the supplied time and return the active scene, elements, interactions, semantic states, and manifest-bound asset IDs. Do not rely on wall-clock progress during frame capture.

## Sequence

1. Validate `source/scene-contract.json` with `validate_scene_contract.py`.
2. Build `src/index.html` with `build_composite_scene.py`.
3. Inspect sampled states with `check_renderer_contract.py` or `check_html_render_state.py`.
4. Render MP4 with `render_concept_video.py` using exact width, height, fps, and duration.
5. Generate a contact sheet and motion/quality reports.
6. Review muted playback and interaction midpoints; repair the contract or producer artifact, then rebuild and rerender.
7. Validate the final stream with `check_video_artifact.py`.

Use Slidev recording only for a deck-first source. Route SVG-only Manim rendering to `manim-svg-video` and consume its MP4 plus manifest only if broader composition follows. A mixed SVG/GIF/HTML scene should normally use the browser compositor.

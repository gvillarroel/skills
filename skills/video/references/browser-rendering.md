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

## Planning-only scene review

For a planning-only request, validate and build the scene, then capture native
states without encoding an MP4. Use the declared dimensions and sample each
interaction at its start, midpoint, just before arrival, after arrival, and
the held final state. Keep captures under the task workspace:

```text
uv run --script <skill-root>/scripts/check_renderer_contract.py src/index.html --video-id compact-scene --duration 8 --width 960 --height 540 --times 0 0.8 1.59 1.7 3.1 4.7 6.3 7.8 --screenshot-dir deliverables/states --output deliverables/renderer-review.json --json
```

Replace the example ID, dimensions, duration and times with actual contract
values. A single scene needs the default one semantic beat; do not impose a
multi-scene minimum. `--require-visual-ids` additionally requires both a
validated asset manifest and a composition plan. Use it only when those
contracts are present. Inspect the screenshot paths actually reported by the
checker, then report full labels, head/shaft visibility, unambiguous endpoints,
route separation and moving-token clearance. A passing render-state report
alone does not prove compactness or visual quality.

Audit the whole compositor stage after choosing an actual readable timestamp,
so all sibling asset and connector SVGs participate in the paint check:

```text
uv run --script <skill-root>/scripts/arrow_quality.py src/index.html --selector "#stage" --width 960 --height 540 --time 7.8 --video-id compact-scene --report deliverables/arrow-review.json
```

The auditor infers the stage's CSS backing through its ancestors. If an
explicit uniform canvas is needed, pass its actual paint with `--canvas`.
Do not mistake an initial unrevealed head for the final held state, or inspect
only one asset SVG while ignoring sibling connectors. Inspect the reported
head count as well as issues and retain native screenshot evidence.

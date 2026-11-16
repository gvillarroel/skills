Create a small offline acceptance video for a calmer original-paper walkthrough.
Use only the copied `skills/line-world-video/` bundle and normal local tools.
Keep that bundle read-only. Do not use the network, live browser sessions,
sibling skills, repository docs or acceptance galleries. A local headless
browser for your authored preview is allowed.

Generate a synthetic one-page PDF with two well-separated diagram components,
one on the left and one on the right. Include readable embedded text in both
components and a connector between them. Identify this explicitly as synthetic
fixture content with a local source and reuse declaration. Use it as the actual
page image, not a redraw in the video.

Make one 12-second scene with stable ID `method`, 30 fps and 1920x1080 output.
The simulated narration references the left component at second 4 and the
right component at second 9. Keep the original text and complete active component
visible at those reading stops. Use the skill's pan-first camera defaults:
one gradual initial zoom, followed by a lateral pan while keeping the same scale.
Do not zoom back out between the components. Use short clear margin emphasis
and the primary-red adjacent guide. Emphasis must not cross source words or
the connector. There should be no closed highlight rectangle or added title.
No audio track is required for this camera fixture.

Produce these exact artifacts:

- `film/story.json`: editable source, scene, region and cue contract.
- `film/index.html` and `film/paper-motion.js`: the self-contained preview and reusable motion runtime.
- `clips/01-method.mp4`: rendered complete scene, 360 frames.
- `review/audit.json`: actual browser trajectory and motion audit, with no findings.
- `review/hero.png`: exact full-resolution reading frame at second 9.
- `review/checks.json`: actual verification of duration, dimensions, frames,
  source identity, repeat seeking, no per-cue zoom-out, lateral camera travel,
  fixed reading scale and unobscuring emphasis. Use explicit booleans and a
  top-level `ok` only after checking the preview and actual movie.

Use the bundled utilities to reduce custom work. Keep any task files outside
the skill. State honestly that this is a synthetic local fixture, not a native
editor export or a real research claim.

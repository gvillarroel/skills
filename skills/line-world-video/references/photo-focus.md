# Original photographic color during focus

## Contents

- [Build the pair once](#build-the-pair-once)
- [Bind semantic focus](#bind-semantic-focus)
- [Inspect and revise](#inspect-and-revise)

Show secondary component photographs in a neutral grayscale treatment. While
the explanation gives a component focus, restore that photograph's original
colors; return to the same neutral treatment when focus leaves. Preserve the
red adjacent guide. Keep inactive photographs quiet and preserve original color
when color itself is evidence. This direction concerns photographic components;
do not desaturate an original paper's chart, a quantitative color scale or a
brand asset without an explicit reason.

## Build the pair once

Use the reviewed source and `documentary_assets.py prepare` from
[documentary images](documentary-images.md). It already caches
`<asset-id>.prepared.png` in the source's original colors, with the identical
crop, orientation, resize, background mask and flip used for its gray variants.
Never attempt to recover color from a one-bit, edge-only or grayscale export.
Keep both prepared files and the provenance/rights record. Do not recolor a
photograph with the red/gray palette or invent color for a monochrome original.

Keep a project-owned binding request, for example `bindings.json`:

```json
{"bindings":[{"id":"gpu-left","target":"#gpu-photo",
"asset":"documented-card","variant":"gray","transition":0.35,
"windows":[{"start":2.4,"end":6.8}]}]}
```

Use measured semantic focus intervals from the existing narration/cue plan,
not pointer hover or proximity to a photograph. Multiple images may share a
window when the spoken subject is their group. Keep intentionally transformed
evidence, such as an augmentation example, paired with its correspondingly
cropped/flipped prepared original.

```text
uv run --script <skill-root>/scripts/photo_focus.py plan --manifest film/media/manifest.json --bindings film/bindings.json --html-root film --output film/photo-focus.json
```

This verifies both prepared digests, neutral RGB channels and matching image
dimensions, then derives relative `neutral` and `color` paths. Store all media
inside the HTML root. It reuses the existing prepared original without another
download, filter pass or model call. The generated JSON has a `bindings` array;
embed it as `window.PHOTO_FOCUS_PLAN` when building an offline composition.

## Bind semantic focus

Copy `assets/runtime/photo-focus.js` into the project, load it before scene code,
and bind one actual SVG `<image>` per entry. Use inline SVG inside HTML as well.
Give the image a stable ID, explicit geometry, the neutral `href` and
`preserveAspectRatio="xMidYMid meet"`. Put shared fades on its parent group.

```js
const photos = LineWorldPhotoFocus.attach(
  document.querySelector('#stage'), PHOTO_FOCUS_PLAN.bindings);
// Include photos.ready in the composition's existing readiness promise.
window.ready = Promise.all([document.fonts.ready, photos.ready]);
// In the existing parent-clock renderer, after camera/figure layout:
photos.render(seconds);
```

Retain the composition's existing renderer and readiness work when integrating
these calls. Await both image decodes before capture. The runtime overlays the
prepared original at identical image bounds and fit, preserves the neutral
image's source/binding attributes, and crossfades only within the declared
window. Geometry, labels, crop and the camera remain fixed. It uses no timers,
CSS autoplay, hover listeners or asynchronous source swaps during playback.
Use explicit image attributes for geometry; avoid ID-only CSS transforms on
the original image. Do not attach two controllers to one image.
Prefer a stable image ID or a selector retaining its documentary attribute.
The inspector excludes its own original-color clone when resolving a broad
image selector; the clone must not be mistaken for a second source photograph.
For scene-local clocks and frame-cache integration, use the bridge described in
[long focus holds](focus-motion.md#integrate-an-existing-scene-local-renderer).

`transition` is the fade duration at each edge, default **0.35 seconds**. Change
`start`/`end` or `transition` in project JSON and rerender the affected scene.
The fade finishes at the window boundary so no color remains after focus.
Short windows clamp each fade to half their length. Overlapping or adjacent
windows on one photograph merge without a gray flash. Repeated/backward seeks
produce the same appearance. Call `destroy()` when replacing the controller.
The unchanged source image is restored on teardown.

## Inspect and revise

```text
uv run --script <skill-root>/scripts/photo_focus.py inspect --html film/scene.html --output film/photo-review.json --screenshot film/photo-focus.png
```

Use `--plan film/photo-focus.json` instead of the embedded plan when needed.
With this option the helper also compares the file's bindings with the actual
`window.PHOTO_FOCUS_PLAN` in the browser, including windows and transition. Use
that built-in check rather than extracting JSON from HTML by string/delimiter
splits: data URIs contain semicolons, so that extra parsing is unreliable.
The browser helper hides the guide for proof, checks the actual paired source
URLs, samples neutral entry/exit, full original color, an intermediate fade,
fixed bounds and repeated seeking. A monochrome original stays monochrome;
the report records whether the pair has a visible difference. An omitted focus
window or wrong spoken cue is outside this check: inventory every relevant
photograph and inspect the measured narration separately.

Add `--video film/photo-preview.mp4 --duration 9 --fps 30` for a silent 1080p
preview of at most 60 seconds. Inspect encoded reading frames, the return to
gray and neighboring joins. Preserve approved speech and its measured timing
for this visual change. Use the existing complete-film renderer and assembly
for final narrated delivery.

# HyperFrames Runtime and Extension

Verified baseline: HyperFrames 0.8.111, GSAP 3.14.2, Node.js 24, Chromium/Chrome
and FFmpeg. Review the official [core contract](https://github.com/heygen-com/hyperframes/blob/main/skills/hyperframes-core/SKILL.md)
when upgrading; do not silently replace the pinned package during a release test.

The builder copies only its own templates, palette, font and vendor resources.
Generated `package.json` pins HyperFrames. There is no global skill installation,
account login or hosted renderer. The generated runner, built from
[hf.ts](../assets/templates/hf.ts), confines framework home/temp
caches to the output project through a Node preload. Supply
`HYPERFRAMES_BROWSER_PATH` when automatic Chrome/Chromium discovery fails.

## Native contract

- One standalone root in `<body>`, never inside `<template>`.
- Root `data-composition-id`, exact `data-width`, `data-height`, `data-duration`
  and `data-fps`; root CSS `width:100%; height:100%`.
- One paused GSAP timeline registered under the identical composition ID.
- A clock proxy triggers a pure `renderAt(seconds)` update. DOM state is derived
  again on every seek; no accumulating trails, incremental counters or mutable
  physics simulation state.
- Bundled local font and GSAP; optional local audio with a unique `id` and
  `data-start`, `data-duration`, `data-track-index`. HyperFrames owns playback.
- No wall-clock callbacks, autonomous animations, unseeded randomness, network
  assets, negative/infinite repeats or render-critical input listeners.

The index contains one continuous scene. The supplied interactive preview is a
separate HTML surface and does not add controls, prose or metadata to the video.
Serve the output project over local HTTP before opening `preview.html`; browsers
restrict cross-file iframe access. For example, run `uv run --no-project python
-m http.server 3210 --bind 127.0.0.1 --directory <project>` in a terminal and visit
`http://127.0.0.1:3210/preview.html`. The browser audit serves it automatically.

## Custom extensions

Extend the generated project when a real mechanism needs richer shape semantics.
Keep its brief and pure state function as the semantic source; consume new local
assets by explicit file path. Register new marks in `snapshot` so their bindings,
bounds and paints remain auditable. Preserve units, direct labels, canonical
entity paint and the same clock. Avoid replacing the mechanism with a sequence
of marketing cards just because a bundled primitive is insufficient.

A specialist may supply a diagram/3D/media artifact if available. Do not make a
sibling skill a required dependency or import its private renderer source. If an
extension exceeds the bundled audit's coverage, state that limit and add an
appropriate project-owned check before claiming completion.

Render only to the exact requested artifact path. The CLI's root `data-duration`
sets the movie length; padding the GSAP timeline does not change it. Inspect the
render summary's capture/GPU route and verify the MP4 with FFprobe after success.

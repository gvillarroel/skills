# Rendering and review

Prerequisites: Python/uv, Node.js 24+, local Chrome/Edge/Chromium, FFmpeg and
FFprobe. The browser helper declares Playwright and Pillow through uv. It uses
an installed browser without downloading one. Set `LINE_WORLD_BROWSER` to an
explicit browser executable when needed. Keep outputs in the task workspace.

The generated project contains `index.html` for capture and `preview.html` for
inspection. Serve it over HTTP, for example:

```text
uv run --no-project python -m http.server 3277 --bind 127.0.0.1 --directory film
```

Visit `http://127.0.0.1:3277/preview.html`. Controls provide exact-time seek,
beat selection, speed, playback and drag-to-pan. The rendered stage excludes
all controls and user camera offsets. The template uses one paused GSAP clock
proxy registered as `window.__timelines['line-world']`; `renderAt` computes each
frame from that clock.

For native HyperFrames, the generated package pins **0.8.111**, the verified
single-scene runtime contract used by the companion explainer. Install with
`npm install --cache .cache/npm --ignore-scripts --no-audit --no-fund`, from the
generated project. The bundled launcher confines framework home/temp/font
caches to that project. Run `node scripts/hf.ts lint`, `validate`, `inspect`,
and `render --output <absolute-final.mp4>`. Consult the actual CLI's `--help`
for render flags. Record CLI findings; intentional off-canvas world geometry
is marked explicitly. Native CLI validation does not replace custom SVG checks.

The bundled Playwright fallback uses the same root and pure state function.
Its default `--capture browser` uses direct browser screenshots and avoids
per-frame computed-style export. The explicit `--capture svg` route exports
computed SVG styles and uses resvg 0.5.0 with the bundled font; use it when a
computed-SVG raster route is specifically needed. That route supports the SVG
template rather than general HTML/canvas/WebGL. Windows browser cache
discovery prefers an existing Playwright headless shell before Chrome/Edge.
The fallback captures frame `i` at `i/fps`, pipes PNGs to FFmpeg and writes H.264/yuv420p.
It verifies exact dimensions, frame count and duration, samples transition
midpoints, checks off-canvas geometry only when it should be on camera, and
records palette paints and all selected row/value pairs. `--audit-only` omits
encoding. A contact sheet is inspection evidence, not a finished video.

Use `--benchmark-capture --benchmark-frames 6 --report benchmark.json` to compare
the two capture methods on a few representative times before committing to a
long export. It writes both sample PNGs and measured per-frame medians. Treat
this as a local microbenchmark, not an end-to-end speed guarantee. Do not keep
rerendering the entire film just to select a capture backend.

Inspect the reported PNGs at full resolution. Reading states must be unclipped,
nonblank and legible; pointer endpoints must correspond to the selected datum.
The dot must not cover values. Red/neutral paint must dominate; extended hues
belong only to documented simultaneous categories. Make red primary and gray
secondary. Reserve black for the last contrast need in text or fine notation;
reject large dark neutral fills. Preserve readable contrast in filled marks
and enough contrast for thin arrows and small labels.

This first template is a silent visual explainer. Add locally sourced audio
only when requested or justified by the brief, recording provenance and sync.
Never represent a missing audio stream as an audio validation pass.

Use Playwright's public `browser.close()` and runtime context cleanup. Do not
terminate processes from a CDP system inventory or depend on private transport
attributes. A runtime failure requires a fresh process-level smoke test before
retrying a long render. Renderer documentation:
[resvg Python API](https://resvg-py.readthedocs.io/en/latest/api.html).

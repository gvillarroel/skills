# Minimal linked explanatory video

Create an 8-second HyperFrames video, 960 by 540 pixels at 12 fps, showing a
conserved allocation between two stores, A and B. They contain 40 units in total.
Initially A has 32 and B has 8. At 2 seconds, an initiating allocation control
starts moving; over 3 seconds A changes linearly to 12 and B to 28. Hold that state
through the end. The allocation control can explore A between 0 and 40 in the
interactive preview. The mechanism should dominate the scene; its linked history
should explain the opposite changes. Preserve the total at every sampled time.
State outside the film that this is an illustrative, lossless allocation model.

Use colorset1. Keep the filmed explanation sparse: direct A/B labels, necessary
values/units and axes, no introductory headline, cards, decorative title or ending
slogan. The same input must update the visible stores and their histories. The
preview must have working transport and parameter controls outside the filmed area.

Deliver exactly `out/video.mp4`, the editable project at `out/project/index.html`,
`out/project/preview.html`, `out/project/manifest.json`, `out/project/brief.json`,
`out/audit.json`, `out/media.json` and a movie-derived `out/contact.jpg`.
Check actual browser behavior, seek reproducibility, input propagation and the
rendered MP4. Inspect reports and correct findings before finishing.

`skills/hyperframes-explainer/` is read-only. Keep generated files and caches in
this workspace. Normal local Node.js, Chrome/Chromium, FFmpeg and uv are available;
network package installation for the local project is permitted. No credentials,
hosted renderer, sibling skills, external repository context or acceptance fixture
reads are needed. Use only this bundle and these task inputs.


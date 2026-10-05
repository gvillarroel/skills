# Static scene compositor contract

Use the loaded video skill's scene contract and compositor to make a
planning-only offline 640×360 scene with two editable SVG assets: a white
background source box labelled Input and a target box labelled Result.
Give each box readable 18px text and ports at its left/right edges. Connect
Input → Result with a clear directional signal route. Create the small SVGs
in the workspace when no specialist producer is available and record that
fallback. Preserve asset semantics and source dimensions.

Write exactly `source/scene-contract.json`, `src/index.html` and
`deliverables/layout-review.md`. Run the native contract validator and
compositor, render the scene at its output dimensions, and record actual
findings. MP4 rendering is outside this planning-only smoke.

Treat `skills/video/` as read-only. Generated files belong outside it. Do
not read acceptance examples or other skills and do not publish anything.
Use normal local tools; install dependencies in this workspace if needed.

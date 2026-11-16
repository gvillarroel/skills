Read ../prompt.md first. Use only the read-only skills/line-world-video bundle
and ordinary local tools. Keep generated files outside the skill directory.

Prepare a small offline media handoff for a 1080p educational video and a D3
graph. This is an asset workflow contract, not a finished video or historical
research task. Create an authored fixture logo for the fictional company
Orbit Tools, using SVG vector paths with a wide 800 by 100 viewBox. Also create
a 200 by 400 PNG test pattern explicitly labeled as a portrait-layout fixture,
not a photograph of a person. Use local files only; no web search is required.

Create media-request.json with two reviewed fixture entries and explicit test
provenance/rights. Use the skill's reusable helper to prepare circular assets in
media/, including SVG and transparent PNG variants, credits and graph nodes.
The wide logo must remain completely visible and preserve its aspect ratio.
The portrait layout should use a chosen focal point and zoom; identify it as
raster artwork. Run the same build again and save its compact JSON output as
reuse.json. Do not modify the helper or hand-author substitute circular outputs.

Write handoff.md explaining the relative image paths to use in D3, where to
place a spoken-name focus dot, how to obtain real documentary portraits for a
future production, and where the source/rights information is stored. Do not
claim that the test pattern depicts a real contributor or that fixture rights
apply to photographs from the web.

Required outputs: media-request.json, media/manifest.json,
media/graph-nodes.json, media/credits.md, media/orbit-tools.circle.svg,
media/orbit-tools.circle.png, media/portrait-fixture.circle.svg,
media/portrait-fixture.circle.png, reuse.json and handoff.md.

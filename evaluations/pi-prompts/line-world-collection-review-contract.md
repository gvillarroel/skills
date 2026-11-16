# Collection review contract

Create a small local fixture to demonstrate reviewing a current movie alongside
an older export. Work only in this task workspace; keep the loaded skill read-only.

Create `artifacts/film.mp4`: a two-second, 30 fps, 640 by 360 silent video with a
white field and a visible primary-red solid geometric mark. This is an explicit
synthetic utility fixture, not a narrated production. Use local FFmpeg.

Create `artifacts/collection.json` with one current entry and one reference entry
for the same production. Both may point to the fixture movie; distinguish their
identities and roles. Use the skill's bundled collection reviewer to generate
`artifacts/reviews/summary.json` and `artifacts/reviews/index.html`, including
the reference. Run it again to exercise verified reuse.

Preserve missing operator observations as pending. Do not fabricate a visual
attestation or call a local movie a native editor export. The summary must show
successful machine checks, one current video and one historical reference, and
must not say the delivery is approved without actual observations. Briefly state
what was generated and the actual scope of validation.

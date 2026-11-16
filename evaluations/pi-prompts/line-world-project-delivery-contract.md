Validate the loaded skill's portable local-assembly workflow with a small
synthetic fixture. Keep the copied skill read-only; put all files in this
workspace. Do not operate Google Vids, generate speech or access an account.

Create two one-second 640x360 H.264/yuv420p clips at 30 fps, with a visible gray
or primary-red geometric mark on white. Create a two-second synthetic tone WAV,
explicitly identified as a fixture rather than actual narration. The ordered
scene IDs are `data` and `model`; each measured fixture audio partition is one
second. Story and observed JSON should declare those same IDs and extents.

Use the bundled delivery utility to prepare `assembly.json`, assemble
`complete.mp4` with `assembly-report.json`, and package `sources.zip` with
`bundle-report.json`. Repeat assembly and packaging to verify actual cache
reuse. Include the story and observed fixture JSON in the bundle. Extract the
ZIP into `clean/`, verify its file digests, and use its self-contained tool to
produce exactly `clean/rebuilt.mp4`. Capture and inspect a frame at
`preview.png` and inspect the final frame count/audio streams. Write `review.md`
describing checks, synthetic provenance, any frame padding and the distinction
between local assembly and native/cloud export. Do not count metadata alone as
visual inspection or claim speech alignment from this tone fixture.

Required exact outputs: `assembly.json`, `complete.mp4`, `assembly-report.json`,
`sources.zip`, `bundle-report.json`, `clean/rebuilt.mp4`, `preview.png`, `review.md`.

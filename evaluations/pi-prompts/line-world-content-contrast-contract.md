# Content-presence review contract

Use only the loaded read-only skill and normal local tools. Do not inspect
acceptance examples, sibling skills, repository docs or existing projects.
Read only the compact references needed for this diagnostic; execute helpers
without reading their implementation unless an actual failure requires it.
Write the artifacts below at their exact workspace-relative paths.

Create `film/baseline.mp4`, a 640×360, 30 fps, three-second silent diagnostic.
Show one outlined rectangular process object in seconds 0–1 and 2–3, but hide
it completely during seconds 1–2. A small primary-red guide remains visible
throughout, positioned outside the object. Use FFmpeg or an equivalent local
renderer. This is a diagnostic fixture, not a production or Google Vids video.

Create matching `film/story.json`, `film/cues.json` and `film/source/index.html`.
Use one scene `process` with clipSeconds 3, authored cues at 0.5 and 2.5, and an
SVG stage/guide with pure renderAt(seconds) and snapshot(). The source must hide
the complete object over the same middle interval, with no other object left
except the guide. Do not hide a defect from the review with ignore attributes.

Run the bundled review helper with the baseline movie, story, cues and source,
writing `film/review/`. Use a driver to accept diagnostic exit 2 only after
asserting both the encoded insufficient-content interval and source empty
interval. Retain its compact summary as `film/before.json`. An expected failing
diagnostic is test data; do not produce a harness tool error.
Use the report-field paths documented in the review reference when writing
assertions; counts and detailed interval arrays have different paths.

Correct the source and produce `film/final.mp4` with the process object present
throughout all three seconds. Keep the same guide, scene budget and cues. Use
the style's primary red and stronger neutral contours; keep its face white with a primary-red edge; do not use pink backgrounds. Preserve quantities and
photographic/brand colors if applicable. Run the same review against this new
movie, then repeat it unchanged. Save the last summary as `film/after.json`.
Verify all 90 decoded/content frames, zero insufficient-content frames, zero
empty source intervals, and reuse of both the unchanged source/content scans
and movie thumbnails on the last run. Inspect the generated diagnostic images.

Write `film/notes.md` with the actual defect interval, correction, cache counts,
color choices and source/encoded evidence limits. Cues are authored test times,
not measured speech. Leave manualReview pending because no finished production
has been inspected; do not fabricate a delivery attestation.

Required outputs: film/baseline.mp4, film/final.mp4, film/story.json,
film/cues.json, film/source/index.html, film/before.json, film/after.json,
film/notes.md, film/review/report.json, film/review/findings.json,
film/review/index.html.

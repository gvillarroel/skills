Read ../prompt.md first. Use only the read-only skills/line-world-video bundle
and normal local tools. Keep generated files outside that bundle. This is a
diagnostic fixture task, not a historical production or native Google Vids task.

Create film/fixture.mp4 as a three-second 640 by 360, 30 fps silent MP4 using
FFmpeg's white color source with a small solid colored box so it is never a
blank frame. Create film/story.json with one scene, id fixture, clipSeconds 3.
Create film/cues.json with scene fixture and two cue references near the start
and end. These are authored test times, not measured speech.

Create film/source/index.html with a 640 by 360 SVG #stage, a red circle #guide,
a readable label inside an outlined rectangle near the center, and a pure
renderAt(seconds) plus snapshot(). Initially make the guide travel through the
rectangle/label between clear endpoint ports. Endpoints must be safe. Do not
add an independent timer. The movie is only a decoding fixture; its pixels are
not claimed equivalent to this separately authored source diagnostic.

Use the skill's review_video.py to review both the movie and this source,
writing film/review/. Retain the compact failing diagnostic as film/before.json.
An expected diagnostic nonzero exit is test data: handle it through a driver
that exits successfully only when the intended transit finding is detected,
instead of producing a harness tool error.

Then fix the source guide route while preserving its endpoint ports and the
readable geometry. Use the bundled focus runtime or a clear piecewise route.
Run the same review command again into film/review/ and save the new summary
as film/after.json. Confirm zero guide events, a clean reading audit, 90 decoded
frames, and reuse of all previously extracted movie thumbnails. Inspect the
generated images. Leave manualReview pending because no finished production
has been reviewed; do not fabricate an attestation. Write film/notes.md with the
observed defect/fix, actual cache results, and source/encoded evidence limits.

Required outputs: film/fixture.mp4, film/story.json, film/cues.json,
film/source/index.html, film/before.json, film/after.json, film/notes.md,
film/review/report.json, film/review/findings.json, film/review/index.html.

Read ../prompt.md first. Use only the read-only skills/line-world-video bundle
and normal local tools. Keep generated files outside that bundle.

Run a local command-contract exercise of the incremental editor, without a
video export or external account. Create film/story.json with voice Nyla,
language en, and three ordered scenes a,b,c, each with clipSeconds 8,
essentialAnimationSeconds 4 and script "Explain a", "Explain b", "Explain c".
Create film/cues.json with scenes a,b,c, each containing one cue with id focus,
target a-mark/b-mark/c-mark, at 2 and travelSeconds 0.25.

Use scripts/video_edit.py setup to register the files. Inspect only scene b's
focus cue. Save the compact output as film/inspection.json. Before rendering,
use a theme patch to change fontScale from 1 to 1.05; generate theme.css through
the helper. Use the cache planner and seed three LOCAL TEST receipts, with
artifacts clips/a.bin, clips/b.bin, clips/c.bin containing the corresponding
ASCII scene letter. These are cache fixtures, not video evidence. Poses are
firstPose {"x":0}/lastPose {"x":1} for a, then 1/2 for b and 2/3 for c.
Use actual current input fingerprints in each receipt.

Create film/changes.json to change only cue b/focus at from 2 to 2.8 using a
stable-ID path and an expected old value. Plan then apply it. Save the apply
receipt as film/edit-report.json and the detailed pending cache status as
film/pending.json. Re-record b against its current fingerprint, preserving its
actual fixture endpoints 1/2. Save the final cache status as film/reused.json.

Required artifacts: film/story.json, film/cues.json, film/theme.json,
film/theme.css, film/inspection.json, film/changes.json, film/edit-report.json,
film/pending.json and film/reused.json. Preserve all scripts and other cues.
Do not claim actual speech timing, a native upload or a finished video.

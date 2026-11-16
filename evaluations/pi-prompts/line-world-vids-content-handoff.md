# Visual-gap repair handoff

Use only the loaded Google Vids adapter and normal tools, with no live account
access for this diagnostic. Write `handoff.md`, `repair-plan.json`, `story.json`,
`inventory-before.json`, `inventory-after.json`, `before-check.json` and
`after-check.json`.

An existing three-scene Vids film has approved native Nyla speech, measured
scene extents of 12.4, 17.2 and 14.1 seconds and matching prepared visual clips.
The second clip sometimes shows only the guide and a divider during a camera
transition. Speech text, word timing and all scene extents must stay unchanged.
The stronger-red visual revision uses primary #9e1b32 and secondary #696969.

Prepare a bounded operator handoff to replace only the repaired second visual,
verify the selected scene, object/voice counts and unchanged timing, then export
and inspect the actual downloaded movie for empty intervals and continuity.
Explain why a minimum/maximum white/black detector alone is insufficient.
Use the optional Line World content checker only if actually available; keep a
standalone inspection fallback. Do not claim account actions, regenerated speech,
native export or audio listening occurred during this diagnostic.

Also exercise the bundled native inventory helper with explicit supplied mock
observations. Use three expected clip IDs and the durations above; the initial
inventory has four current scene buttons because an extra five-second scene
with zero objects is inserted in position two. Use fresh English announcement
strings for each ordinal and total. Retain that input and its failing check.
Handle expected exit 2 through a driver only after asserting the empty scene and
count mismatch. Produce a corrected three-scene observation and passing check,
preserving the three clip IDs, voice starts and extents. These are diagnostic
observations; do not claim any actual editor action occurred.

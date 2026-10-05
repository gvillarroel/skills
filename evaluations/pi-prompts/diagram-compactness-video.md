# Editable scene planning

Produce a planning-only, editable 960×540 scene explaining a sensor control
loop: Sensor → Controller → Motor → Sensor. The controller also reports to
an Alarm. Keep every directed relationship, distinguish feedback from
forward control, and plan a moving signal that remains traceable throughout
the loop. This is an offline scene; no external publication is needed.

Write exactly `source/scene-contract.json`, `src/index.html` and
`deliverables/layout-review.md`. Use the skill's native contract validator
and compositor. Create the small required source assets in the workspace
when a specialist producer is unavailable, recording the fallback reason.
Inspect the scene at delivery size and report actual placement and motion
findings plus verification commands. MP4 rendering is outside this
planning-only request.

Treat `skills/video/` as read-only. Generated files belong outside it. Do
not inspect acceptance examples or other skills. Use only the task inputs
and normal local tools; install dependencies in this workspace if needed.

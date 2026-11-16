# Existing renderer with a frozen reading hold

Build a small portable HTML demonstration of fixing this integration problem:
an existing scene-local renderer returns only its camera and guide state, so a
PNG hold cache freezes a newly added chart animation while the camera is still.

Keep an authored `renderClip(index, localSeconds)` function that renders the
scene/camera/guide. Use the skill's scene-effects bridge to extend that renderer
with parent-clock focus motion, rather than replacing it. Use two five-second
scenes, a real SVG curve in the second scene, a stable reading label `42`, and
a calm meaningful trace during a second-scene local focus interval from one to
4.8 seconds. Keep numerical geometry, the reading label and the camera fixed
during that interval. Treat this as a declared synthetic utility fixture.

Create exactly `artifacts/scene.html`, its required local runtime assets,
`artifacts/motion-review.json` and `artifacts/reading.png`. Expose the standard
global seek function and an embedded focus plan. Run the bundled actual-target
pixel inspector; demonstrate that moving phases change the returned cache
identity, inactive effects permit stable hold reuse and repeated seeking is
deterministic. Keep the loaded skill directory unchanged and keep outputs in
the requested artifact paths. State any limits of the checks you ran.

# Speech-linked focus and clear reading space

Use `line-world-speech-focus` for a narrated figure whose guide identifies the
object currently being explained. A decorative orbit or margin sweep does not
fulfil this contract.

## Cue and geometry contract

Keep project-owned cues with `target`, `phrase`, `at` in scene-local seconds,
`travelSeconds` and an evidence source. Resolve `target` from stable
`data-focus-id` attributes after `document.fonts.ready`. Distinguish repeated
values by entity ID and occurrence: `split-train`, `split-validation` and
`split-test` remain three different targets even when two labels both say 20%.

Obtain word timestamps from the actual recorded audio or a reviewed native
caption/word timeline. The optional Google Vids companion includes an exact
phrase/occurrence aligner. Keep ASR timing approximate and inspect the short
spoken passage. Script position and word counts are draft estimates only.
Re-align when narration, scene starts or voice speed changes.

Use `assets/runtime/focus.js` in authored HTML. It exposes pure
`LineWorldFocus.port`, `route`, `pose`, `along`, `overlap` and `audit` functions.
For a moving camera, `visibleAlong` keeps a point on its already clear world
route inside the current camera bounds; it does not clamp the point off that
route. Build pan obstacles from both neighboring scenes in world coordinates.
The builder and dedicated plugin producers ship it. Copy the file into the
project and load it before scene code; keep the skill payload read-only.

1. Reserve clear space beside each label, value or meaningful mark. Include
   other labels and important mark envelopes in the port obstacles. For a
   node, reserve space outside its whole shape rather than placing the guide
   inside its label. Pass the maximum focus radius, keyline and breathing room.
2. Call `port(targetBox, frameBounds, obstacles, {radius: 14, gap: 18})` once.
   Boxes use `{x0,y0,x1,y1}` in the same logical coordinate system. A missing
   safe port must trigger recomposition; do not accept a least-bad overlap.
3. Resolve short travel paths once with `route(previous, next, textObstacles,
   frameBounds)`. It returns clear waypoints or fails. It checks straight paths,
   simple lanes and a corner visibility graph. Keep travel agile, usually
   0.18–0.35 seconds; longer distances may need a reserved lane or a camera move.
4. Attach each path to its cue as `path`, with resolved `x` and `y`. Call
   `pose(cues, seconds, initialPose)` from the parent audio clock. Travel starts
   before `at` so arrival coincides with the spoken reference. It shrinks during
   travel, grows briefly on arrival and settles; it does not pulse while idle.
5. Carry the actual last pose into the next scene. Make targets visible before
   their reference. If a cut requires a short arrival pan, record any earliest
   feasible cue delay rather than claiming exact alignment. Keep late cues
   active throughout the voice; never freeze a whole scene after a fixed twelve
   seconds if narration still points to new objects.

For an overview, transform both target boxes and all obstacles into the final
screen coordinates. End the zoom before referring to miniature panels, or
update the ports with the same camera transform. A screen-space guide must not
point at a target using stale world coordinates.

## Text and mark clearance

Reserve text envelopes before routing connectors. Measure actual loaded fonts,
including numeric values above tall bars and the first/last labels near axes.
Keep full-frame dividers intact; fit each section's labels inside its own area.
Move a connector into an empty lane when it crosses a row label. Grid rules may
be split around a measured value envelope. Do not move measured data to clear
labels or hide the conflict by shrinking all text.

At settled reading frames call `LineWorldFocus.audit(stageSvg)`. It reports
clipped labels, pairwise text overlap and actual stroked geometry passing through
text; it samples the path rather than treating its whole bounding box as ink.
Basic user-space clip paths are respected. Complex clip masks, glyph shapes and
all transit camera states still need visual inspection. Run at output size after
fonts load. Intentional container outlines may enclose text but must not cut it.

Inspect each cue arrival and its travel samples with the full dot/keyline
envelope against labels and essential marks. Verify the 60 → first 20 → second
20 sequence against the audio when applicable. Repeat an arbitrary backward
seek and compare its state. Inspect a short encoded excerpt with sound and
the final output's joins; a total-duration match alone does not prove sync.
Use the [whole-film review](visual-review.md) when testing every guide state,
not only its arrivals. Treat figure interiors and portraits as obstacles too.

For a standalone HTML with `#stage`, `#guide`, `window.renderAt(seconds)` and
optional `window.ready`, run `scripts/inspect_focus.py --html figure.html
--times 2.2,4.1,5 --output focus-review.json --screenshot preview.png`.
It injects this bundle's diagnostic runtime, waits for fonts/readiness, records
returned states and real guide bounds, checks label/stroke clearance and repeats
a seek. Use `--guide` for another selector. Supply cue arrivals and travel
midpoints; this sampled helper does not claim every-frame or audio verification.

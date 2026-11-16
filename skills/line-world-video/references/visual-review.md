# Whole-film visual review

## Contents

- [One review command](#one-review-command)
- [Content presence](#content-presence)
- [Fix the actual cause](#fix-the-actual-cause)
- [Reuse and record decisions](#reuse-and-record-decisions)

Use this procedure for a requested visual audit or polish pass. It combines the
encoded movie, optional SVG source and explicit operator judgments. Keep the
tool in this read-only skill; put review artifacts in the task workspace.
For filled semantic objects, also follow [icon contrast and centering](icons-and-alignment.md).
Run `inspect_items.py` once across authored states; check white icon strokes on
red, inactive-state contrast and both horizontal and vertical content centers.

## One review command

```text
uv run --script <skill-root>/scripts/review_video.py --video final.mp4 --story story.json --timing observed.json --cues cues.json --html composition/index.html --clock scene-local --output review
```

The story needs ordered `scenes` with unique lowercase hyphen-case `id` and
positive `clipSeconds`. Optional measured timing supplies matching scene IDs,
`sceneSeconds` or `duration`, and optional global `start`. Optional cues use
`scenes: [{id, cues: [{target, at, travelSeconds}]}]` with local seconds. Preserve
their actual audio evidence. Omit timing for a source-budget review; that does
not establish measured narration timing.

The local SVG source must expose `#stage`, `#guide`, optional `window.ready`
and either `renderAt(globalSeconds)` or, with `--clock scene-local`,
`renderClip(sceneIndex, localSeconds)`. A pure `snapshot()` enables repeat-seek
checks. Canvas/WebGL productions can use encoded galleries without `--html`;
this helper does not infer their internal geometry.
Use `--guide-selector '#guide-dot'` for a differently named SVG guide. Composite
guides exclude their own child circles from obstacle checks. For paper, website,
starter or mixed collections, use [collection review](collection-review.md) to
run the matching source audit rather than treating a full-page capture as an
obstructing photograph.

Read `summary.json` first, then `findings.json` for the affected scene/time.
Open `index.html` to inspect the encoded frames and seek the original movie.
Use the per-scene JPEG sheets for compact inspection. Do not load the full
report, galleries or vendor sources into model context unless a finding needs
that detail. The report distinguishes actual encoded frames from source geometry.

The helper decodes the entire movie and counts decoded frame statistics,
reports detected white/black frames, and samples reading states, scene openings,
cue arrivals and travel midpoints. With source HTML it tests the guide at 30 fps
by default, including text, image, rectangle and circle interiors. `--trajectory-fps`
changes source sampling only; state the actual coverage. These are sampled
geometry checks, not pixel proof for every point or independent speech alignment.

## Content presence

The helper scans every encoded frame for insufficient content, beyond pure-white
or pure-black screens. The white-field profile uses a 640×360 decode, a minimum
RGB difference of 18, at least 0.1% non-background ink and 5% extent in both
dimensions. Uniform fills, a lone guide or a single divider fail. This is a
conservative content-presence gate, not a quota for filling intentional whitespace.
The actual thresholds and exact failing frame/time intervals remain in the report.
The gallery automatically includes offending intervals and the least-ink frame.

For a scripted diagnostic, use the actual machine paths: `summary.json` exposes
`insufficientContentFrames` and `emptySourceIntervals` as counts.
`report.json["content"]["intervals"]` contains encoded time/frame intervals;
`report.json["source"]["scenes"][i]["content"]["emptyIntervals"]` contains source
intervals. The per-scene `findings.json` entries use `emptyEncodedIntervals` and
`emptySourceIntervals`. Read those documented fields instead of guessing a
`coverage` key. Diagnostic exit 2 is expected when a gate fails; distinguish
that finding from an unexpected helper failure before accepting it in a driver.

Source checks exclude guide elements, dividers, background surfaces and hidden
objects. At least one useful shape, image or readable label must remain mostly
visible throughout the camera route. `visibleAnchors` is capped at one: it is a
presence lower bound, not an inventory. Use `data-content-anchor` for a meaningful
aggregate such as a field of observations; its descendants must actually be
visible. Do not annotate an empty background as content. Source anchors and
encoded pixels are independent gates; each can fail when the other passes.

The default linked and atlas renderers run these checks automatically. With a
custom renderer or Google Vids, use this review command on the downloaded film.
The standalone `content_scan.py --video film.mp4 --output content.json` runs just
the cached encoded gate. The supplied profile is for this style's white field
and constant-frame-rate movies; adapt its declared policy for a requested different
background instead of relaxing thresholds to conceal a real gap.

It also checks settled label/stroke clearance, small text, media near an edge,
figures too close to dividers, and equal-font groups. Add the same
`data-review-font-group` to text elements that should share a screen font size;
do not use that grouping for intentional heading/value hierarchies. Preserve
the default no-title policy. Large full-frame background rectangles and defs
are excluded from guide obstacles. Use `data-review-ignore="true"` only for a
documented intentional construction; never hide a defect to pass the review.

## Fix the actual cause

- Resolve label/connector conflicts by recomposition or clear travel lanes.
  Keep the full dot, keyline and breathing room away from text and faces.
- Include all meaningful filled/outlined figures in routing, not only labels.
  Remove contained obstacle boxes when an outer box already protects them.
  Inspect computed paint after applying the theme; a white SVG fill attribute
  can still produce a solid gray body through CSS. Protect that complete body.
- During a pan, translate both scenes' obstacles and guide ports into one world
  system. Route once through that combined geometry. Use
  `LineWorldFocus.visibleAlong(path, progress, currentCameraBounds)` to remain
  on the safe route as the camera moves. Reserve an inset for the dot radius;
  fail and recompose if the camera contains no point of that route. Inspect
  velocity and bends; geometric clearance alone does not establish good motion.
- Interpolate the actual affine screen transform during a zoom. Independently
  interpolating scale and camera translation can push a previously visible
  guide outside the frame. Track its world anchor during the zoom and verify
  every intermediate frame. Finish a summary zoom before its first spoken cue.
- At an overview scale, fade miniature copy before it becomes unreadable and
  use concise concept labels when needed to identify the summarized figures.
  Keep the original full-size reading states intact. Do not audit a summary
  map as if its tiny internal text were meant to be read.
- Compare related Mermaid/D3 diagrams at a shared scale or measured text size.
  Independent fit-to-box scaling can produce mismatched typography.
- Give portraits headroom, keep external names clear and leave space between
  a section divider and a nearby figure. Keep primary red semantic; use dark
  gray for the secondary comparison, including its value label when appropriate.
- Keep an outgoing or incoming explanatory object visible during a camera handoff.
  Move islands closer or overlap their reveals if the route crosses empty space.
  Show a real observation field on frame zero, retain an atlas panel's geometry,
  and overlap outgoing/incoming chart fades. Do not delay every object until the
  camera settles or add decorative marks merely to pass the content gate.

Use the semantic editor and shared theme for supported field/style revisions.
Regenerate only affected outputs and verified dependent joins. A source pass
does not update an old movie. Render, replace changed native clips while
preserving unchanged narration, export again and review that actual file.

## Reuse and record decisions

Repeated runs verify cached thumbnail hashes and reuse them by actual movie
digest. The source cache covers local HTML, scripts, styles, data, media and
fonts plus both diagnostic runtimes and clock parameters. Declare extra external
file dependencies with repeated `--input path`. Corrupt thumbnails are rebuilt.
Use a separate review directory; the helper rejects one containing the authored
source. No model call is required for extraction, scanning or cache reuse.
`encodedSamples` counts gallery entries; cache counts refer to unique frame
files. Two entries can reference the same final frame. Compare unique frame
indices when validating reuse rather than assuming those counts are identical.

Inspect every scene's contact sheet, full-resolution reading/defect frames,
transitions, guide paths and the relevant passages with audio. Record actual
visual notes, fixes, accepted intentional details and remaining limits. To bind
that record to the current artifacts, create a project-owned JSON file:

```json
{"videoSha256":"digest from report.json","sourceSha256":"source digest from report.json",
"scenes":[{"id":"scene-id","reviewed":true,"notes":"Observed result and disposition."}]}
```

Include every current scene exactly once. Use null for the source digest only
when no source was reviewed. Add `--manual-review notes.json` on the repeated
command. A stale hash or incomplete scene list is rejected. `ok` describes the
machine checks; `manualReview` remains pending until a matching record is
supplied, and `deliveryReady` requires both. That record is an operator
attestation, not automatic proof of listening or looking at the images.

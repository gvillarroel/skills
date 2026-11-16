# Motion during long focus holds

## Contents

- [Choose meaningful motion](#choose-meaningful-motion)
- [Use the parent clock](#use-the-parent-clock)
- [Check the actual target](#check-the-actual-target)

For a chart or diagram kept in focus **longer than two seconds**, program calm
motion through that reading interval. Count the actual visual focus window,
not merely a guide's visit to one small node. Carry the explanation while the
viewer reads. A moving guide alone does not animate the focused figure.
Exactly two seconds or less does not require this additional motion.

## Choose meaningful motion

Prefer a trace on an existing chart curve, a flow along actual diagram edges,
an ordered reveal of related parts, or restrained emphasis on the active mark.
Keep numerical endpoints, axis domains, areas, labels and the camera stable
when the data itself is unchanged. Never oscillate bar heights, invent new
observations or jitter labels merely to add activity. A genuine changing-data
simulation needs its own truthful state/units; do not apply a fixed-data
stability check to that different case.

Use a single explanatory motion in the active figure and quiet inactive views.
For linked views of the same selected row, measure its complete reading hold
across those views. Do not divide it by the guide's visits to individual panes;
doing so can disable every interval while the same datum is explained for
several seconds. Keep corresponding representations synchronized.
Prefer a 3.2-second cycle, gentle entry/exit and no flicker, shaking or repeated
zooming. Shorter eligible holds can use part of one pass. Keep the motion
running through the hold instead of finishing a quick reveal and leaving a
long static tail. Native D3/Mermaid/HyperFrames motion can supply this behavior;
do not add a second effect when the existing figure already does the job.

Original-paper captures and photographs retain their source pixels. Animate a
separate unobscuring relation/emphasis overlay when useful; never morph a
documentary object, move paper text or retrace an unverified source connection.
Keep the primary guide beside the target, with readable contrast and clear ports.

## Use the parent clock

The bundled `assets/runtime/focus-motion.js` supplies two fixed-data options:
`trace` moves a short red emphasis segment along real SVG geometry; `pulse`
changes a restrained contour's opacity without changing its size. Both leave
the source element untouched. An emphasis trace is not an additional datum.
On a thick primary-red stroke, a thin white inset trace keeps motion visible
without changing the mark's quantitative width or endpoints.
Emphasis layers must keep computed `fill: none`. The runtime gives its own
transparent fill and stroke priority over imported producer CSS. A Mermaid
`.node rect` rule can otherwise fill an animation clone, cover reading text and
blend a red node into pink. The pixel inspector rejects opaque emphasis even
when that layer moves. Apply this protection to the overlay alone.
Copy the runtime into project assets, load it before scene code and declare
all focus windows in project-owned JSON or `window.FOCUS_PLAN`:

```js
window.FOCUS_PLAN = {windows: [
  {id: 'flow', source: '#actual-edge', scope: '#diagram', kind: 'diagram',
   start: .4, end: 4.2, mode: 'trace'},
  {id: 'history', source: '#actual-curve', scope: '#chart', kind: 'chart',
   start: 4.5, end: 9, mode: 'trace', period: 3.2}
]};
const motion = LineWorldFocusMotion.attach(
  document.querySelector('#stage'), FOCUS_PLAN.windows);
window.renderAt = seconds => {
  // Render the existing camera, source figure and semantic guide first.
  return {seconds, motion: motion.render(seconds)};
};
```

Keep the actual scene renderer when integrating this call; do not replace it
with the small illustration above. Finish font/layout/centering work before
attaching motion. `source` resolves to one actual SVG path, line, polyline,
circle or rect, including its transform and clipping. Use unique IDs, finite
parent-clock `start`/`end`, `kind: chart|diagram`, and `mode: trace|pulse`.
Trace one continuous path; bind disconnected diagram edges separately or use
`pulse` for a geometry with multiple subpaths. SVG dash patterns restart at
each subpath and can otherwise create unintended static gaps.
Periods below 2.4 seconds are rejected. Motion stops outside the window and
is disabled for intervals of at most two seconds. It never starts a timer,
autoplay loop or random simulation. Forward, backward and repeated seeking
must give the same image. Use `destroy()` when replacing a controller.

For quantitative bars, keep their geometry fixed and prefer an adjacent
explanatory relationship or restrained contour emphasis. Do not create an
extra border for every small solid object. For a native Mermaid figure, bind
its actual rendered edge rather than drawing a substitute graph.

## Check the actual target

```text
uv run --script <skill-root>/scripts/inspect_focus_motion.py --html film/scene.html --output film/motion-review.json --screenshot film/reading.png
```

Use `--plan film/focus.json` for an external `{windows:[...]}` record. This
also works with custom parent-clock animation that does not use the runtime.
The helper samples five actual browser images inside each eligible hold,
measures changed pixels inside the declared target, rejects moving fixed-data
geometry/reading labels and checks backward/repeated seek. The guide is hidden
only for this motion proof, then restored for the screenshot. Changes elsewhere
or guide movement do not satisfy the target's motion check.

The plan must inventory every relevant chart/diagram hold; this audit cannot
infer omitted spoken focus windows. Samples are not an all-frame or semantic
certificate. Inspect whether the effect explains the subject, stays within the
target, preserves contrast and does not compete with reading. Run the existing
focus/label and whole-film review for routes, collisions and continuity.

For a short standalone preview, add `--video film/preview.mp4 --duration 9`.
It produces a silent 1080p preview at the parent clock, capped at 60 seconds;
`--fps` accepts 24, 25, 30 or 60. Keep complete narrated-film rendering and
measured speech in their existing workflow. Changing this emphasis does not
justify regenerating an approved voice or changing the scene budget.
The repeat-pixel check reports exact equality separately and requires identical
geometry and computed source/overlay paint. It permits 8/255 of Chromium
antialiasing variation. A sparse edge allowance additionally permits up to
64/255 on at most 0.05% of target pixels (minimum budget eight), only beside a
local contrast edge of at least 32/255. Solid-interior changes, larger changes,
or changed geometry/paint fail. These reported bounds do not replace inspecting
the motion. Run the source inspector before a long final capture.

## Integrate an existing scene-local renderer

For narrated projects with `renderClip(index, localSeconds)`, copy
`focus-motion.js`, optional `photo-focus.js`, and `scene-effects.js` from
`assets/runtime/`. Declare ordered scenes plus scene-local effect windows:

```js
const authored = window.renderClip;
const effects = LineWorldSceneEffects.attach(stage, {
  scenes: story.scenes,
  motion: [{id:'flow', sceneId:'prepare', source:'#actual-edge',
    kind:'diagram', start:1, end:8}],
  photos: [{id:'gpu', sceneId:'compute', target:'#gpu-photo',
    neutral:'gpu-gray.png', color:'gpu.prepared.png',
    windows:[{start:2, end:7}]}]
});
window.FOCUS_PLAN = {windows:effects.windows};
window.PHOTO_FOCUS_PLAN = {bindings:effects.photos};
await effects.ready; // Inside the existing layout/image readiness promise.
window.renderClip = (i,t) => effects.frame(i,t,authored(i,t));
window.renderAt = t => {
  const p=effects.locate(t); return renderClip(p.index,p.seconds);
};
window.snapshot = effects.snapshot;
```

Attach after font, geometry and centering work. Preserve the original readiness
promise and await the combined one in the capture helper. The bridge validates
local bounds, converts windows to the parent clock and includes active motion
phases/photo fades in the returned frame-cache identity. A camera/guide-only
cache otherwise freezes these effects during a reading hold. Inactive effects
keep the same identity so static PNGs can still be reused. Do not add absolute
time to every cache key when no rendered property changes. Never replace the
authored camera or semantic guide with this bridge.

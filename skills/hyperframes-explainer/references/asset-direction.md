# Asset Direction

Choose the visual means before the renderer. An event needs a visible cause,
a recognizable subject, and complementary consequences. Minimal typography does
not justify an anonymous rectangle in place of a mechanism.

## Contents

- [Select by explanatory job](#select-by-explanatory-job)
- [Plan moments and shared state](#plan-moments-and-shared-state)
- [Construct an informative vector fallback](#construct-an-informative-vector-fallback)
- [Quality gate before encoding](#quality-gate-before-encoding)

## Select by explanatory job

Inspect installed skill descriptions using the current session catalog or local
skill inventory. Read only the selected skills. Names below describe optional
capabilities, not required installations or hard-coded filesystem paths.

| Explanatory job | Preferred available skill | What to request | Standalone fallback |
| --- | --- | --- | --- |
| Recognize an object and its moving part | `svg-brief-design` | Original vector silhouette, cutaway, editable moving parts, exact palette and ports | Draw subject-specific SVG with the construction recipe below |
| Follow matter, packets, motion, waves or a field | `procedural-svg-animation` | Deterministic paths/geometry and a pure time/state evaluator, with causal parameter bindings | Use sampled paths and expressions driven by canonical accumulated state |
| Read magnitude, history, distributions or spatial data | `d3` or `echarts-animated-svg` | Truthful scales, geometry, direct labels, fixed domains, editable SVG | Use bundled plots plus authored axes, ticks and direct units |
| Arrange distinct views and object-to-object connectors | `diagram-composition` | Compact layout, meaningful panel forms, named ports and obstacle-safe routes | Assign nonoverlapping view regions and route through actual object ports |
| Connect many related representations or zoom levels | `compose-synchronized-svg` | Shared entity/state contract, semantic groups and synchronized geometry | Reduce the scope to one dominant mechanism and one or two consequences |
| Explain depth, perspective, rotation or an occluded spatial relationship | `threejs-animated-3d` | Seekable scene or renderable frames, fixed camera logic, named object/state hooks | Use an honest vector cutaway or orthographic view; disclose lost depth |
| Explain flows, sequences, states or dependencies | `mermaid` | Native notation, preserved relationship semantics and editable vector hooks | Author the same topology in SVG |
| Explain UML, components or structured architecture | `plantuml-colorset-renderer` | Appropriate diagram family, explicit colorset1 and meaningful nodes/ports | Author the same typed relationships in SVG |
| Identify a real technical entity | `iconify-icon-search` or `technical-logo-assets` | Verified consistent-family SVG and license/source metadata | Use a direct name and a custom silhouette; do not invent a brand mark |
| Show appearance that the viewer must recognize | `pexels-media-search`, `destockd-video-search`, `polyhaven-asset-search`, `ambientcg-material-search`, `kenney-asset-search` or `imagegen` | Relevant image, shot or 3D asset with provenance and usable format | Use an explanatory illustration when appearance is not essential |
| Assemble several media types, soundtrack or scene sequence | `video` | Mixed-media composition contract and appropriate specialist artifacts | Use a single local HyperFrames composition and the bundled validation path |

Choose one suitable producer per asset. Prefer SVG for editable explanatory
geometry, 3D for a spatial claim, and real imagery for appearance. Do not select
3D, stock footage, generative textures, logos or decorative particles merely to
make a scene look expensive. A conventional chart may need only the plot builder.
Reuse an existing correct asset before generating another.

For the matching inlet/vehicle models, the bundled
[calibrated composer](calibrated-mechanisms.md) is a reusable original vector
producer. Use it when no companion is needed or installed. Mermaid defaults to
colorset1; PlantUML defaults to colorset2, so pass colorset1 explicitly for this
workflow. Normalize renderer SVG into the supported import subset or use the
documented custom route; notation selection alone does not prove integration.

## Plan moments and shared state

Write an asset plan beside the project brief. For each asset, record:

- The viewer question, its visual encoding, and the event IDs where it matters.
- The actual producer and why its capability suits this question.
- Native bounds, intended view/placement, input/output ports and named shape hooks.
- Source quantities, derived quantities, units, domains and the meaning of motion.
- Source path, ownership/license where applicable, and whether the asset is
  static context, a driven mechanism, a quantitative view or a rendered sequence.

For a variable inlet, the explanatory chain is aperture → transport speed → stored
amount → history slope. An opening alone cannot explain accumulation. Use a
recognizable valve and reservoir, moving tracers on the connected inlet, a level
with capacity ticks, and a time curve. Make their geometry respond to the same
source and its integral. Keep identifiers, colors and ports stable through the
event. A paused still must already show how the system is connected.

The plan format and SVG import command are in [asset-contract.md](asset-contract.md).
Use exact state bindings; an autonomous SVG/CSS animation with a similar duration
does not synchronize with HyperFrames. Bake or disable a specialist's independent
clock and drive its hooks from `stateAt(t)` and the master timeline.

## Construct an informative vector fallback

1. Establish the subject's silhouette and scale before details. Pick the features
   that make it recognizable: a valve body and wheel, a reservoir's inlet and
   level, a vehicle's wheels and road, a queue's ordered slots, or a circuit's
   terminals. Use original geometry rather than stacking generic titled cards.
2. Separate stationary structure, the causal actuator, the moving substance, and
   measurement marks into stable shape IDs. Put mechanical housings in neutral
   tones; reserve red for the active quantity. Keep open channels visibly open.
3. Use a deliberate stroke hierarchy at 1080p: approximately 4–6 px for principal
   contours, 2–3 px for quieter structure, and readable direct labels at least
   24 px. Scale these with the output size. Avoid shadows, arbitrary gradients,
   oversized arrowheads and tiny decorative fasteners.
4. Author at the target view size, with a `0 0 width height` viewBox. Draw curves,
   joins and ports intentionally. Flatten transforms before import. Keep editable
   SVG source and label the modeled quantity with units, not explanatory prose.
5. Use motion only where the model supplies its meaning. For flow, advance tracers
   with `mod(k * integrate(rate,time) + phase, 1)`, not `rate * time`; this remains
   continuous through a rate ramp and stops at zero rate. Tracers indicate motion
   qualitatively unless calibrated as discrete measured quanta.
   Calibrate a constant-area fill as `usableHeight * amount / capacity`, with its
   zero baseline and capacity edge aligned to the actual ruler. A capacity label
   alone does not replace a requested graduated ruler. For rightward rolling in
   SVG's downward-y coordinates, positive rotation is clockwise; use
   `distance * pixelsPerUnit / wheelRadius * 180 / pi`, and place the road at the
   wheel's actual contact point. Keep neutral housings distinct from quantity paint.
6. Inspect a composed still and event frames. Improve shape, separation, route or
   scale until the moving part and its effect can be identified without a title.

## Quality gate before encoding

Check recognition, truthful encoding, useful density and causal continuity.
Inspect the initial state, event onset, ramp midpoint, settled change, and final
hold. Each visible detail should identify the subject, expose an interaction,
quantify a consequence, or provide spatial context. Remove the rest.

A richer drawing can still fail when its movement is ornamental, its route misses
the inlet, its fill contradicts the units, or its plot shows a different history.
Repair these relationships before adding labels. Record specialist validators
and manual review separately from HyperFrames' mechanical checks.

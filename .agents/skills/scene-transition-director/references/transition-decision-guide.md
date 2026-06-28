# Transition Decision Guide

Use this guide to make cuts feel intentional, surprising, and coherent across a video.

## Source Preservation Rules

- Keep supplied scene IDs exactly. Do not shorten `s01-intake` to `s01`, and do not replace user-provided scenes with a generic example.
- Count adjacent boundaries before writing. Three scenes normally mean two transitions; five scenes normally mean four transitions.
- Copy a named persistent element exactly. If the source says `work packet`, do not rename it to `request packet`.
- Preserve required color/object phrases such as `yellow task card`, `blue tool packet`, and `green proof card`.
- Use examples in this reference only as pattern guidance, never as source material.

Mechanical chain rule:

```text
scene IDs: A, B, C
transitions: A -> B, B -> C
```

Do not replace the supplied scene IDs with `s01`, `s02`, or newly invented names.

## Decision Order

1. **Narrative handoff**: what idea must survive the cut?
2. **Persistent element**: what visible thing carries that idea?
3. **State evolution**: what did it mean before, what does it become, and what changes because of the cut?
4. **Viewer attention**: where is the eye at the final frame of the source scene, and where must it land in the target scene?
5. **Transition family**: match cut, persistent object, camera move, color handoff, spatial portal, morph, interrupt, or hard cut.
6. **Composition shift**: centered hero, loop, flow spine, split screen, grid, depth space, or other armature.
7. **Color shift**: preserve color by semantic role, shift color only when state changes, and avoid using color as decoration.
8. **Camera/space shift**: zoom, pan, parallax, depth reveal, compression, expansion, or portal when scale or abstraction changes.
9. **Rhythm**: cut on completion, anticipation, interruption, or delayed reveal.
10. **Validation**: define a visual check for both sides of the cut.

## Transition Families

### Match Cut

Use when two scenes share shape, location, orientation, or role. The outgoing object should land near the incoming focal point, or the viewer will miss the match.

Best for:
- formula to diagram
- chart mark to process node
- product surface to schematic equivalent

Reject when the two objects only look similar but mean different things.

### Persistent Object

Use when one object carries story state across scenes. Preserve identity with at least two of: color, size, shape, label, motion path, trail, or timing.

Best for:
- request packet
- cursor
- token
- trace line
- work item
- camera target

Avoid adding a persistent object after the fact if it does not affect the concept.

### Camera Move

Use when the scene changes abstraction level. Zoom into a detail, pull out to show system context, pan to reveal consequence, or rotate only when depth is meaningful.

Best for:
- detail to system
- local proof to global summary
- inside model to outside harness

Validate that text remains readable during the move.

### Color Handoff

Use when a semantic role becomes the next focal system. Preserve color meaning. A blue route can become a blue trace; a green test gate can become a green validation result.

Reject when the color shift is only mood.

### Spatial Portal

Use when the viewer crosses from one conceptual space into another: code space to runtime space, harness exterior to loop interior, evaluation dashboard to final formula.

Make the portal a cause/effect action, not a decorative wipe.

### Morph

Use when a role transforms: task card becomes packet, trace line becomes evidence card, failed action becomes blocked gate. Keep enough geometry continuity that the viewer sees the transformation.

### Interrupt

Use sparingly when surprise is the point. Interrupt with a blocking gate, sudden pause, red stop mark, or snap zoom only when the narrative needs contrast.

## Persistent Element Checklist

For each recurring element, record:

- name
- semantic role
- shape and color identity
- state in each scene
- first appearance and last appearance
- what changes at each transition
- what validates continuity

If the element does not change state or guide attention, remove it.

## Cut Quality Checks

Flag a transition when:

- the outgoing focal point and incoming focal point are unrelated
- the persistent object changes color or shape without a state reason
- the camera moves but the abstraction level does not change
- a wipe hides a weak composition rather than carrying meaning
- the cut relies on reading text instead of visible state change
- all transitions use the same family
- the transition completes in the first few frames and then the scene holds static
- the implementation shows only a generic persistent-object pulse when the plan promised a camera move, portal, morph, color wash, or other scene-level transition family

## Renderer Handoff Notes

- For deterministic HTML/SVG video, encode transition behavior from absolute timestamps rather than wall-clock animation state.
- For hard scene boundaries, make the outgoing scene visibly hand off the persistent element before the cut and make the incoming scene receive it after the cut.
- For each planned transition, capture at least one midpoint frame inside the transition window and compare it with the planned `family`, `bridgeAction`, and `incomingState`. A contact sheet alone often skips these short windows.
- Add contact-sheet checks and full-speed playback checks. A contact sheet can show composition, but it often cannot show whether a handoff feels continuous.

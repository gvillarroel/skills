# Transition Plan Contract

Use this file before writing `transition-plan.md`, `transition-plan.json`, or a renderer handoff.

## Output Shape

For planning or renderer handoff, create one of:

- `transition-plan.md`: readable transition direction and per-cut briefs.
- `transition-plan.json`: machine-readable transition plan.
- An added `Transitions` section in an existing storyboard or production notes.

For `transition-plan.json`, use this shape:

```json
{
  "version": 1,
  "videoId": "stable-video-id",
  "persistentElement": {
    "name": "<exact persistent element name from prompt>",
    "role": "viewer-tracked work item",
    "states": ["task", "loop packet", "tool request", "blocked action", "final proof"]
  },
  "transitions": [
    {
      "id": "t01",
      "fromScene": "s01",
      "toScene": "s02",
      "start": 8.2,
      "duration": 1.1,
      "family": "persistent object",
      "semanticPurpose": "Carry the viewer from task intake to loop execution without resetting attention.",
      "stateChange": "The packet changes from queued patch work to active loop packet.",
      "attentionHandoff": "The outgoing packet exits on the same baseline where the observe node appears.",
      "styleContinuity": "Grid-locked hard-edge panels, unchanged stroke width, and square apertures persist through the midpoint.",
      "alignmentRule": "Outgoing packet center and incoming observe node share the same row baseline.",
      "edgeRule": "All masks and panels remain square, rectangular, and 0-radius through the transition.",
      "boxPaddingRule": "All masks, panels, cards, and apertures keep internalPaddingPx 0; content remains flush to bounds.",
      "grayscaleHierarchyRule": "Outgoing, bridge, and incoming hierarchy use distinct grayscale levels #333333, #696969, and #9c9c9c; hue only marks semantic state.",
      "grayscaleHierarchy": [
        { "level": 0, "role": "primary focal", "grayHex": "#333333" },
        { "level": 1, "role": "secondary support", "grayHex": "#696969" },
        { "level": 2, "role": "tertiary structure", "grayHex": "#9c9c9c" }
      ],
      "genericMotionRejected": "A generic pan or pulse would not show the packet changing role from queued work to active loop execution.",
      "surprise": "The task packet exits the harness frame and becomes the loop packet.",
      "outgoingState": "Patch packet is visible at the right edge.",
      "bridgeAction": "Packet pulls a teal trace line across the cut.",
      "incomingState": "Packet lands on the observe node.",
      "compositionShift": "Centered enclosure becomes radial loop.",
      "colorShift": "Teal harness boundary becomes active loop path.",
      "cameraShift": "Subtle zoom-in then settle.",
      "spaceShift": "Runtime chassis changes into process loop space.",
      "validationFrames": [
        {
          "time": "transition midpoint",
          "target": "packet, rectangular mask, and observe node baseline",
          "passCriterion": "The packet remains visible, the mask has square corners, and the landing target is already aligned."
        }
      ],
      "validationChecks": [
        {
          "method": "midpoint-frame-review",
          "target": "transition midpoint",
          "passCriterion": "Persistent element appears on both sides and attention lands on the observe node."
        }
      ]
    }
  ]
}
```

Replace every example name and scene ID with the user's exact source facts. If the prompt names the persistent element, `persistentElement.name` must be byte-for-byte the supplied phrase. Put semantic interpretation in `persistentElement.role` or transition fields, not in `persistentElement.name`.

Every transition should include:

- `semanticPurpose`: why this cut exists in the story.
- `stateChange`: what changes in object state, attention, abstraction, space, rhythm, or role.
- `attentionHandoff`: where the eye starts and where it lands.
- `styleContinuity`: palette, typography, stroke, mask, edge, and geometry rules that persist.
- `alignmentRule`: grid, axis, baseline, orthogonal path, or landing rule.
- `edgeRule`: corner radius, mask shape, aperture shape, and whether square/rectangular geometry is required.
- `boxPaddingRule`: whether boxes, masks, panels, cards, and apertures preserve zero internal padding and flush-to-bounds content.
- `grayscaleHierarchyRule`: how hierarchy levels remain visible with distinct grayscale values through outgoing, bridge, and incoming states.
- `grayscaleHierarchy`: structured scale with at least three `{ level, role, grayHex }` entries where each `grayHex` is a distinct monotonic grayscale value. It is required when `--require-grayscale-hierarchy` is used; prose-only gray hex lists are not enough.
- `genericMotionRejected`: why a generic slide, pan, wipe, pulse, or glide would be wrong.
- `validationFrames`: midpoint, pre-cut, post-cut, or landing frames that prove the transition, with `time` or `timestamp`, `target`, and `passCriterion`.

Use structured `validationChecks` objects with `method`, `target`, and `passCriterion` when the plan will feed an implementation or automated review.

## Validation

Run the bundled validator for JSON transition plans:

```powershell
uv run --script skills/scene-transition-director/scripts/validate_transition_plan.py --plan transition-plan.json --expect-transitions 4 --require-anchor "task packet" --forbid gsap
```

When the prompt gives an exact transition count, pass `--expect-transitions`. When it names a persistent element, pass `--expect-persistent-name`. When it lists exact scene IDs, pass `--expect-chain` with those IDs joined by commas.

For semantic hard-edge plans, add:

```powershell
--require-semantic-fields --require-square-edge-style
```

For no-padding or grayscale-level plans, add:

```powershell
--require-zero-box-padding --require-grayscale-hierarchy
```

Under those flags, do not include any positive `padding`, `paddingPx`, `boxPaddingPx`, or `internalPaddingPx` value. Under square-edge flags, do not include soft-corner cards, pills, soft edges, blobs, or positive radius language unless explicitly marked as a source-native exception.

If validation fails, fix the exact failed fields in the existing JSON. Do not ignore a failed validator, weaken supplied validator arguments, or replace the user's source scenario with a generic transition sequence.

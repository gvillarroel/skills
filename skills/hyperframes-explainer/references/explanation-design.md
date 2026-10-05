# Explanation Through Linked Motion

Name the sentence that the mechanism must demonstrate: **when X changes, Y and Z
respond through this relationship**. Keep the sentence in the source manifest;
it does not need to become a title in the video.

## Select complementary views

Choose representations by their questions, not by visual variety. A moving body
can answer where it is; a vector can show direction and magnitude; a trace can
show how a quantity changes; a reservoir can reveal accumulation; a partition can
show conservation. Two views of the same numerical value are useful only when
their encodings answer different questions.

Use one dominant mechanism with subordinate representations attached spatially
to it. Two to four linked views often fit a short explanation, but use the number
the subject needs. A common flat canvas, shared baselines and open whitespace are
usually clearer than equal-size framed cards. Stable positions let the viewer
compare states without relearning the scene.

## Compact connected mechanisms

For conceptual node/link diagrams, size nodes to their labels and group related
objects closely. Remove surplus outer padding and shorten routes through the
nearest clear corridor. Keep arrowheads and a direction-bearing shaft visible,
attach endpoints to their intended objects and reserve distinct lanes and space
for relation labels. Crossings must not imply an extra junction; do not merge
unrelated paths or move an endpoint away from its object to save room.

After a readable composed still, try up to two focused compaction revisions and
retain the tightest passing result. Check delivery-size stills at stable states,
event midpoints, arrivals and full-motion extrema, including changing-value labels.
Revert reductions that introduce text overlap, clipping, hidden heads, ambiguous
routes or lost mechanism recognition. Preserve stable anchors and the complete
travel/rotation envelope; compact unused gaps rather than the space an object
actually needs to move. Physical distance, magnitude, timing and conservation
remain faithful. Supporting charts retain readable axes and useful data dimensions
instead of being squeezed to meet a diagram packing target.

## Give the event a visible consequence

1. Establish the initial state briefly.
2. Show the initiating action where it actually occurs: a source moves, a gate
   opens, a load changes, an object hits a boundary, or a parameter changes.
3. Propagate the input through the declared relationships. Related geometry,
   values, traces and markings sample the same state at the same time.
4. Hold the changed state long enough to compare. Preserve a small baseline,
   trail or reference line when it makes the difference visible.

Do not animate every quantity merely because an event occurred. If a conservation
law holds, keep the conserved total unchanged while parts exchange. If a physical
or computational delay matters, model that delay explicitly; synchronization means
one consistent clock, not erasing the mechanism's latency.

## Minimal text without minimal information

Default to no on-stage title. Put labels beside the relevant marks and values next
to their units. Prefer `Speed`, `Distance`, `Input`, `Output` or a supplied domain
label to a sentence explaining what the viewer can already see. Avoid an opening
card, chapter names, a legend when direct labels suffice, resolution/fps stamps,
promotional slogans and an ornamental footer.

A single short context label or event note is useful when the action is otherwise
ambiguous. A visible assumption note is required if its omission would falsely
present an illustrative model as observed evidence. Put fuller source, mathematical
and validation explanations in the accompanying project manifest or review.

At 1080p, start with essential labels around 28–36 px and direct values around
32–44 px. Check the actual delivery size. Do not satisfy a text budget by shrinking
labels, hiding units, removing uncertainty or merging unrelated mechanisms.

## Causal fidelity

Preserve entities, units, direction, dependencies and supplied facts. Match travel
direction to the sign of the represented quantity. Use honest zero-based scales
for amounts and consistent scales across compared marks. Keep axes/domain limits
stable across events. A progress bar must not silently clamp a quantity that can
exceed its scale.

Record the model's scope and unsupported mechanisms in the manifest. A smooth
animation of a formula is conditional mathematical output; it does not prove a
real system behaves that way.

## Pattern recipes

- **Mechanism + rate + accumulation:** use one changing rate source; derive
  cumulative amount through `integrate`; move the mechanism and trace the amount
  from the same state. Inspect event ramp midpoints and the post-event slope.
- **Exchange + conservation:** derive complementary parts from one source and
  show both amounts plus one total reference. Validate `partA + partB = total` at
  every sampled time; the total must remain unchanged when allocation changes.
  Check displayed values as well as model values: independent rounding must not
  suggest that a conserved total changed. Increase precision or show approximation
  explicitly when exact displayed parts cannot add to the displayed total.
- **Position + direction + history:** use one phase/time source to derive position
  and a direction vector; generate the trail from `stateAt(sampleTime)`, never from
  previously visited frames. Reverse seeking must reconstruct the same path.

Recreate these with the scene contract and builder. They are mechanisms, not fixed
layouts or subject-specific facts; use supplied quantities and truthful labels.

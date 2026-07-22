# Timeline Sequencing

## Use When

Use timelines for choreographed Slidev scenes where multiple targets must enter, align, overlap, or call back in a controlled order.

## Anime.js Pattern

Use `createTimeline({ defaults })`, then chain `.add(target, parameters, position)`, labels, relative offsets, timers, or callbacks. Keep default duration and easing in the timeline unless a target needs a deliberate exception.

## Slidev Pattern

Use a timeline for slide-level story beats, not for unrelated decoration. Rebuild or seek the timeline on `$clicks` if the presenter needs deterministic states.

## Tested Fixture

The `timeline-sequencing` slide coordinates square, circle, and triangle marks with overlapping offsets.

## Pitfalls

- Dispose timelines through `scope.revert()` or explicit `revert()` on unmount.
- Do not mix hidden Slidev slide targets into one timeline.
- Use labels for maintenance when more than two offsets are involved.

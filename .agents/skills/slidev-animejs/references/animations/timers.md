# Timers

## Use When

Use timers for counters, clocks, progress callbacks, and non-DOM sequencing that needs Anime.js timing but not a direct animated target.

## Anime.js Pattern

Use `createTimer({ duration, loop, frameRate, onUpdate })` and render timer state into DOM, SVG, or component refs.

## Slidev Pattern

Use timers to coordinate annotations, live counters, or callback-driven progress in a deck. Keep timer output deterministic enough for screenshot checks.

## Tested Fixture

The `timers` slide renders timer progress into a numeric label and rotating dial.

## Pitfalls

- A timer has no visible output unless `onUpdate` writes one.
- Revert timers on unmount.
- Avoid high frame rates for simple counters in presentation mode.

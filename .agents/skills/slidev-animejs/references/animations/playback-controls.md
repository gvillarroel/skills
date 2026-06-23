# Playback Controls

## Use When

Use playback controls when a Slidev click or presenter action must seek, pause, reverse, restart, cancel, complete, reset, or revert an animation deterministically.

## Anime.js Pattern

Store the returned animation or timeline instance and call methods such as `play()`, `pause()`, `seek()`, `restart()`, `reverse()`, `complete()`, `cancel()`, `reset()`, or `revert()`.

## Slidev Pattern

Map `$clicks` to explicit states. For example, click zero pauses at the start, click one seeks to the middle, and click two restarts or reverses.

## Tested Fixture

The `playback-controls` slide uses click state to pause, seek, reverse, and restart a controlled marker animation.

## Pitfalls

- Keep one authoritative animation instance per component run.
- Do not leave cancelled animations without resetting inline styles if the slide will be revisited.
- Prefer `revert()` on component cleanup when the target should return to authored CSS.

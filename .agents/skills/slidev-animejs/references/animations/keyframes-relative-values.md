# Keyframes And Relative Values

## Use When

Use keyframes when one target needs a named motion arc: bounce, overshoot, settle, color-shift, relative movement, or a staged explanatory path.

## Anime.js Pattern

Define property keyframes directly on animated properties. Use per-keyframe `to`, `from`, `duration`, and `ease` values when timing differs by segment. Use relative values such as `+=24` for concise adjustments from the current state.

## Slidev Pattern

Tie the keyframe direction, distance, or ending emphasis to `$clicks` when the slide has multiple explanatory states. Recreate the animation after click changes if the keyframe path changes.

## Tested Fixture

The `keyframes-relative-values` slide animates a marker through a multi-stop path and a relative final nudge.

## Pitfalls

- Keep the keyframe path within the stage at all viewport sizes.
- Avoid changing the number of target elements during the keyframe animation.
- Use shorter loop delays in validation decks so browser checks catch active motion quickly.

# Animatable Live Input

## Use When

Use animatables for frequent value changes from pointer movement, scroll, sensor-like inputs, or repeated click-controlled targets.

## Anime.js Pattern

Use `createAnimatable(targets, parameters)` and call generated property functions such as `animatable.x(value)` or `animatable.y(value)`.

## Slidev Pattern

Bind pointer or click handlers to a bounded stage. Use animatables when a normal `animate()` call would be recreated too often.

## Tested Fixture

The `animatable-live-input` slide moves a marker through setter calls generated from click state and pointer movement.

## Pitfalls

- For performance reasons, animatable property setters accept numeric values or numeric arrays.
- Refresh bounds if the slide resizes.
- Remove pointer listeners on unmount.

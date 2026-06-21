# SVG Motion Path

## Use When

Use motion paths for moving markers along routes, showing flow across a diagram, following a process loop, or explaining spatial sequencing.

## Anime.js Pattern

Use `svg.createMotionPath(path)` and spread the returned `translateX`, `translateY`, and `rotate` tween parameters into `animate()`.

## Slidev Pattern

Render the path and the moving target in the same SVG coordinate system or in a positioned stage whose coordinates match the path. Optionally combine with `svg.createDrawable(path)` to draw the route as the marker moves.

## Tested Fixture

The `svg-motion-path` slide moves a marker along a curved path while the path is drawn.

## Pitfalls

- Keep the path element in the DOM before calling `createMotionPath`.
- Verify the target's transform origin so rotation follows the route naturally.
- Do not let the moving target leave the slide crop.

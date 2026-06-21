# Three.js Scene Patterns

Use these patterns when implementing Three.js scenes or galleries for this repository.

## Scene Selection

- Use primitive meshes for fast explanatory scenes: boxes, spheres, torus knots, planes, tubes, cylinders, and instanced meshes.
- Use `BufferGeometry` for particle fields, wave surfaces, point clouds, and generated scientific or data-driven shapes.
- Use `InstancedMesh` when repeating many similar objects with different transforms or token colors.
- Use local generated data unless the request requires a specific model or dataset. Avoid large remote assets in acceptance fixtures.

## Renderer Structure

Create one scene module per example. Return a small API:

```js
{
  update(seconds) {},
  reset() {},
  dispose() {}
}
```

Use a shared renderer harness for canvas setup, resizing, camera aspect updates, replay state, pointer drag, and the animation loop. Keep the scene factory responsible only for geometry, materials, lights, and per-frame transforms.

## Camera And Layout

- Use `PerspectiveCamera` for depth-forward examples and keep the field of view moderate, usually 34 to 50 degrees.
- Place the camera high enough to reveal depth without hiding labels or page UI.
- Call `camera.updateProjectionMatrix()` after every resize.
- Keep fixed-format scene frames stable with `aspect-ratio`, `min-height`, and `overflow: hidden`.

## Materials And Color

- Use token colors from `ANIMATED_VISUAL_TOKENS.md`: red `#9e1b32`, orange `#e77204`, yellow `#f1c319`, green `#45842a`, blue `#007298`, purple `#652f6c`, black, white, and grays.
- Use `MeshStandardMaterial` with ambient and directional lights for most scenes.
- Use `PointsMaterial` with vertex colors for particles.
- Keep clear colors white or light neutral unless the scene requires a dark inspection environment.

## Interaction

- Add pointer drag for galleries so every canvas is demonstrably interactive.
- Keep replay controls outside the canvas and expose `aria-label` text.
- Reset animation time and scene transforms on replay. Do not create duplicate render loops, listeners, or meshes on repeated replay.

## Performance

- Cap renderer pixel ratio with `Math.min(window.devicePixelRatio, 2)`.
- Prefer shared geometries/materials where many meshes repeat.
- Dispose geometries, materials, and renderers if a component can unmount.
- Avoid postprocessing in baseline fixtures unless the effect is the point of the example.

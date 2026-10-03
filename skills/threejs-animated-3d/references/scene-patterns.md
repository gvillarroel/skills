# Three.js Scene Patterns

Use these patterns when implementing Three.js scenes or galleries for this repository.

## Scene Selection

- Use primitive meshes for fast explanatory scenes: boxes, spheres, torus knots, planes, tubes, cylinders, and instanced meshes.
- Use `BufferGeometry` for particle fields, wave surfaces, point clouds, and generated scientific or data-driven shapes.
- Use `InstancedMesh` when repeating many similar objects with different transforms or token colors.
- Use local generated data unless the request requires a specific model or dataset. Avoid large remote assets in acceptance fixtures.
- For the bundled orbit, `--token-count` accepts 1–24 objects within the same motion envelope. Reuse fills for the same semantic role. For unique roles use the complete
  bundled `solidSequence` before any optional outline variant; exclude the actual
  canvas and any color already reserved for another distinct role. Increase the scene size or simplify trajectories when overlap obscures identity.

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
- Keep fixed-format scene frames stable with `aspect-ratio`; default to a 200 px minimum stage height and compact spacing from `visual-tokens.md`. An explicit requested size takes precedence.
- Fit camera distance to the complete animation envelope and the current horizontal/vertical field of view. Refit after aspect changes or orbit input. `overflow: hidden` is not evidence that moving objects fit; inspect their projected bounds through the cycle. The bundled orbit template samples a cylindrical motion envelope with a 12% projection margin, leaving decorative floor rings free to extend beyond the frame.

## Materials And Color

- Follow `visual-tokens.md`: colorset1 uses red `#9e1b32`, black, white, and grays first. Pink is a last resort; colorset2's extended hues require an explicit request.
- Use `MeshStandardMaterial` with ambient and directional lights for most scenes.
- Keep filled meshes free of decorative edge geometry and default wireframes.
  Relationship lines, trajectories and scientific line geometry remain visible.
- Keep lights neutral white, enable normal sRGB input/output conversion, and inspect final shading so red does not become a broad pink wash. Validate material colors separately from naturally shaded pixels.
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

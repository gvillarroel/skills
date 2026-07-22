# Three.js Validation

Use browser verification for Three.js because static DOM checks cannot prove WebGL scenes rendered.

## Required Checks

1. Open the page through an HTTP server, not `file://`, when using modules or Vite.
2. Listen for console errors, console warnings, and page errors.
3. Wait for an explicit ready flag such as `window.__threeGalleryReady === true`.
4. Verify the expected number of scene cards, canvases, and replay controls.
5. Sample canvas pixels after rendering:
   - Nonwhite pixel count proves the canvas is not blank.
   - Color diversity proves token-colored objects rendered instead of a flat clear color.
   - Canvas bounds prove responsive sizing is usable.
6. Sample canvas hashes before and after a delay to confirm animation changes frames.
7. Click replay controls and confirm replay state changes without duplicating canvases or listeners.
8. Perform a pointer drag on at least one canvas and confirm interaction state changes.
9. Capture desktop and mobile screenshots and inspect them for framing, overlap, and text fit.

## Canvas Pixel Probe

Use `preserveDrawingBuffer: true` in verification fixtures so Playwright can read `canvas.toDataURL()` reliably. Draw that data URL into a temporary 2D canvas and sample pixels from the image. Avoid `canvas.getContext("2d")` on a WebGL canvas; a canvas cannot switch context types after WebGL is created.

## Movement Probe

Hash a downsampled image from each canvas, wait 500 to 800 milliseconds, then hash again. Require most or all hashes to change. Keep animations deterministic enough that a failed movement check signals a real render loop or visibility problem.

## Screenshot Output

Store verification screenshots in `projects/<project-id>/artifacts/screenshots/`, or in `projects/threejs-animated-3d-validation/artifacts/screenshots/` for this repository's validation fixture. Keep generated screenshots and build artifacts out of the skill directory.

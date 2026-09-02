Create exactly `scene.html` as a portable browser 3D scene.

Requirements:

- Use the `threejs-animated-3d` skill.
- Work only from the copied skill and the prompt. Do not look outside the workspace and do not use external network resources.
- Create exactly `scene.html` in the workspace root.
- Create the bundled validator report at exactly `scene-validation.json` in the workspace root.
- The page must be self-contained or use only files inside `skills/threejs-animated-3d/`.
- Do not create `portable-3d-scene.html`, `index.html`, or any other HTML filename.
- Do not copy vendor files such as `three.module.min.js` into the workspace root; if a local Three.js module is needed, reference the copy inside `skills/threejs-animated-3d/`.
- Render a nonblank animated 3D token-orbit scene in a `<canvas>` with at least five colored objects, camera perspective, lighting/depth cues, and a replay button.
- Include no CDN, remote import, remote script, remote stylesheet, image URL, or package install dependency.
- Verify with the skill's bundled standalone validator. It must pass static source checks, desktop/mobile browser rendering, nonblank/color-diverse canvas checks, frame movement, replay, pointer drag, horizontal overflow, and browser errors. Do not replace it with Playwright API probes or an unguarded expected-negative `grep`.
- At the end, print a concise summary of files created and validation checks.

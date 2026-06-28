Create exactly `scene.html` as a portable browser 3D scene.

Requirements:

- Use the `threejs-animated-3d` skill.
- Work only from the copied skill and the prompt. Do not look outside the workspace and do not use external network resources.
- Create exactly `scene.html` in the workspace root.
- The page must be self-contained or use only files inside `skills/threejs-animated-3d/`.
- Do not create `portable-3d-scene.html`, `index.html`, or any other HTML filename.
- Do not copy vendor files such as `three.module.min.js` into the workspace root; if a local Three.js module is needed, reference the copy inside `skills/threejs-animated-3d/`.
- Render a nonblank animated 3D token-orbit scene in a `<canvas>` with at least five colored objects, camera perspective, lighting/depth cues, and a replay button.
- Include no CDN, remote import, remote script, remote stylesheet, image URL, or package install dependency.
- Verify with a browser if available, or with direct source checks if browser automation is unavailable: `scene.html` exists, contains a canvas setup, contains animation logic, contains a replay control, and contains no external network references.
- At the end, print a concise summary of files created and validation checks.

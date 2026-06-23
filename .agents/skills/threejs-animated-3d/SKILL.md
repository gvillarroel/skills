---
name: threejs-animated-3d
description: "Build, animate, troubleshoot, and validate Three.js/WebGL 3D scenes and galleries. Use when Codex needs browser-rendered 3D visuals, animated camera or object motion, particle fields, 3D data views, material and lighting studies, interactive canvas scenes, or a Three.js example page that should be verified with Playwright canvas-pixel checks."
---

# Three.js Animated 3D

## Core Workflow

1. Decide whether the request needs real 3D. Use Mermaid for notation-first diagrams, D3 for bespoke SVG geometry, ECharts for standard chart dashboards, and Three.js when depth, perspective, lighting, camera motion, meshes, materials, particles, or WebGL interaction are central to the result.
2. Choose the output contract before coding:
   - For live artifacts, deliver a responsive HTML/Vite page or framework component with modular scene factories.
   - For capture workflows, render deterministic frames from time-based animation state rather than relying on wall-clock side effects.
   - For reusable examples, expose a replay/reset function for every scene.
3. Build each scene with a stable renderer lifecycle: fixed container aspect ratio, device-pixel-ratio cap, resize handling, camera update on resize, animation cleanup, and explicit disposal when scenes are removed.
4. Use the repository visual tokens before capture. Keep page UI neutral, use the known primary palette for categorical materials, and reserve red for brand, risk, or emphasis.
5. Prefer simple, inspectable geometry for examples. Use generated primitives, instanced meshes, buffer geometry, and local data before adding heavy external model assets.
6. Verify the result in a browser. Check desktop and mobile viewports, canvas nonblank pixels, color diversity, animation movement, pointer interaction, replay controls, text fit, and console/page errors.

## Progressive Disclosure Map

- `references/scene-patterns.md`: read when choosing scene types, structuring a Three.js gallery, or implementing cameras, lights, materials, particles, and resize-safe renderers.
- `references/validation.md`: read when writing Playwright checks, canvas pixel probes, movement checks, replay checks, or screenshot verification for Three.js output.

## Common Commands

Install and verify the included Three.js gallery fixture:

```powershell
npm install --prefix .agents/skills/threejs-animated-3d/assets/examples/threejs-animated-3d
npm run build --prefix .agents/skills/threejs-animated-3d/assets/examples/threejs-animated-3d
npm run verify --prefix .agents/skills/threejs-animated-3d/assets/examples/threejs-animated-3d
```

Run the example page locally:

```powershell
npm run dev --prefix .agents/skills/threejs-animated-3d/assets/examples/threejs-animated-3d
```

## Complementarity Rules

- Prefer Mermaid when the notation or Mermaid-rendered layout is the source of truth.
- Prefer D3 when the final artifact should be portable SVG or needs custom 2D data geometry.
- Prefer ECharts when the request is a standard chart family with existing ECharts interaction and layout.
- Prefer Three.js when the viewer must perceive objects in 3D space, inspect lighting/materials, orbit or pan a camera, watch particles or meshes move through depth, or compare generated 3D scene patterns.
- Do not force Three.js for flat diagrams or charts unless 3D depth materially improves the explanation.

## Visual Tokens

Read `../ANIMATED_VISUAL_TOKENS.md` before creating or updating examples, galleries, captures, or user-facing controls. Use Open Sans for page text, Material Symbols Rounded for replay/reset icons, and the documented brand palette for editable scene materials, page chrome, controls, highlights, and replay states.

## Pattern Promotion

When a Three.js scene, material setup, camera move, interaction, or replay behavior proves reusable, update `references/scene-patterns.md` before finishing. Capture the scene pattern name, trigger, geometry/data contract, camera and lighting setup, animation clock, replay/reset API, responsive sizing rules, and validation checks. Put browser and canvas-pixel verification lessons in `references/validation.md`.

## Validation

After changing this skill, its references, or examples, run:

```powershell
uv run --script scripts/validate-skills.py
```

When changing the example gallery, also run the `Common Commands` build and verify steps. Inspect generated screenshots under `projects/threejs-animated-3d-validation/artifacts/screenshots/` and confirm all canvases are nonblank, animated, color-tokened, responsive, and interactive.

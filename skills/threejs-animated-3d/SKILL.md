---
name: threejs-animated-3d
description: "Builds, animates, troubleshoots, and validates Three.js/WebGL 3D scenes and galleries. Use when Codex needs browser-rendered 3D visuals, animated camera or object motion, particle fields, 3D data views, material and lighting studies, interactive canvas scenes, or a Three.js example page that should be verified with Playwright canvas-pixel checks."
---

# Three.js Animated 3D

## Exact Output Contract

When a task names a specific output file, treat that path as fixed. Before coding, capture it:

```powershell
$OutputHtml = "scene.html"
```

Replace the example value with the exact requested path. Do not substitute descriptive names such as `portable-3d-scene.html`, `three-scene.html`, or `index.html`, even if the task description says "portable" or "3D scene". When the task forbids network access or package installation, run `scripts/build_standalone_threejs.py` with the exact output path. The builder inlines the bundled Three.js module and core into the HTML, so the artifact remains portable from nested output directories without CDN scripts, remote fonts, package installation, or copied vendor files.

## Core Workflow

1. Decide whether the request needs real 3D. Use Mermaid for notation-first diagrams, D3 for bespoke SVG geometry, ECharts for standard chart dashboards, and Three.js when depth, perspective, lighting, camera motion, meshes, materials, particles, or WebGL interaction are central to the result.
2. Choose the output contract before coding:
   - For live artifacts, deliver a responsive HTML/Vite page or framework component with modular scene factories.
   - For capture workflows, render deterministic frames from time-based animation state rather than relying on wall-clock side effects.
   - For reusable examples, expose a replay/reset function for every scene.
3. Build each scene with a stable renderer lifecycle: fixed container aspect ratio, device-pixel-ratio cap, resize handling, camera update on resize, animation cleanup, and explicit disposal when scenes are removed.
4. Read `references/visual-tokens.md` before styling. Default to colorset1: neutral materials and surfaces with deliberate red emphasis. Pink is a last-resort category after usable red/neutrals, never an automatic secondary color. Use colorset2 only for explicit extended color. Use white lights so neutral objects retain their hue.
5. Default to compact panels: 12 px padding, 8 px gaps, 4 px vertical button padding, and a 200 px stage minimum. Preserve readable fonts and touch targets; fit the full animation envelope after resizing rather than shrinking meaningful scene geometry.
6. Prefer simple, inspectable geometry for examples. Use generated primitives, instanced meshes, buffer geometry, and local data before adding heavy external model assets.
7. Verify the result in a browser. Check desktop and mobile viewports, canvas nonblank pixels, tonal variation, material/light palette, animation movement, pointer interaction, replay controls, text fit, and console/page errors. Grayscale shading counts as variation; do not add hues to satisfy a diversity check.

## Progressive Disclosure Map

- `references/scene-patterns.md`: read when choosing scene types, structuring a Three.js gallery, or implementing cameras, lights, materials, particles, and resize-safe renderers.
- `references/validation.md`: read when writing Playwright checks, canvas pixel probes, movement checks, replay checks, or screenshot verification for Three.js output.
- `scripts/build_standalone_threejs.py`: run for isolated runtime smoke tests or any task that needs a portable no-network HTML scene at an exact path.
- `scripts/validate_standalone_threejs.py`: run after the standalone builder; it performs static, desktop/mobile canvas, animation, replay, pointer, overflow, and browser-error checks in one fail-closed command.
- `assets/templates/self-contained-token-orbit.html`: builder source template; do not copy it directly because its runtime marker must be expanded.
- `assets/vendor/three.module.min.js` and `assets/vendor/three.core.min.js`: bundled inputs that the builder embeds into the standalone HTML.

## Common Commands

Create a no-network runtime scene with an exact output path:

The builder uses colorset1 and compact spacing by default. Pass `--colorset
colorset2` only for an explicit extended palette; `--density comfortable` is
available for requested larger spacing. Use `--title "Scene heading"` for the
visible heading and `--token-count 12` for a different orbit count (1–24), reusing
role colors as the count grows. Keep generated files outside the skill directory.

```powershell
$OutputHtml = "scene.html"
uv run --script skills/threejs-animated-3d/scripts/build_standalone_threejs.py $OutputHtml
if (!(Test-Path -LiteralPath $OutputHtml)) { throw "Missing requested Three.js HTML output path." }
if (Test-Path -LiteralPath "portable-3d-scene.html") { throw "Wrong output filename: use the exact requested path." }
if (Test-Path -LiteralPath "three.module.min.js") { throw "Standalone build must not copy vendor files to the workspace root." }
Select-String -Path $OutputHtml -Pattern "https?://|//cdn|unpkg|jsdelivr|esm.sh" -Quiet | ForEach-Object { if ($_) { throw "External network reference found." } }
uv run --script skills/threejs-animated-3d/scripts/validate_standalone_threejs.py $OutputHtml --report scene-validation.json --screenshot scene.png
```

The validator declares Playwright dependencies: always run it with
`uv run --script`, never bare `python`. It can reuse installed Edge/Chrome on
Windows when managed Chromium is absent. Use the bundled validator instead of probing Playwright object internals or
issuing an unguarded `grep` whose expected no-match exit code becomes a tool
error. Treat its nonzero exit as the validation failure and fix the artifact.

For repository acceptance-fixture maintenance only, set `<skill-root>` to the full `threejs-animated-3d` source directory. The commands below require `assets/examples/`, which is intentionally excluded from the normal runtime payload.

Install and verify the included Three.js gallery fixture:

```powershell
npm install --prefix <skill-root>/assets/examples/threejs-animated-3d
npm run build --prefix <skill-root>/assets/examples/threejs-animated-3d
npm run verify --prefix <skill-root>/assets/examples/threejs-animated-3d
```

Run the example page locally:

```powershell
npm run dev --prefix <skill-root>/assets/examples/threejs-animated-3d
```

## Complementarity Rules

- Prefer Mermaid when the notation or Mermaid-rendered layout is the source of truth.
- Prefer D3 when the final artifact should be portable SVG or needs custom 2D data geometry.
- Prefer ECharts when the request is a standard chart family with existing ECharts interaction and layout.
- Prefer Three.js when the viewer must perceive objects in 3D space, inspect lighting/materials, orbit or pan a camera, watch particles or meshes move through depth, or compare generated 3D scene patterns.
- Do not force Three.js for flat diagrams or charts unless 3D depth materially improves the explanation.

## Visual Tokens

Read `references/visual-tokens.md` before creating or updating examples, galleries, captures, or user-facing controls. Use Open Sans for page text, Material Symbols Rounded for replay/reset icons, and the documented brand palette for editable scene materials, page chrome, controls, highlights, and replay states.

## Pattern Promotion

When a Three.js scene, material setup, camera move, interaction, or replay behavior proves reusable, update `references/scene-patterns.md` before finishing. Capture the scene pattern name, trigger, geometry/data contract, camera and lighting setup, animation clock, replay/reset API, responsive sizing rules, and validation checks. Put browser and canvas-pixel verification lessons in `references/validation.md`.

## Validation

After changing this skill, its references, or examples, run:

```powershell
uv run --script scripts/validate-skills.py
uv run --script skills/threejs-animated-3d/scripts/validate_standalone_threejs.py <artifact.html> --report <report.json> --screenshot <preview.png>
```

When changing the example gallery, also run the `Common Commands` build and verify steps. Inspect generated screenshots under `projects/threejs-animated-3d-validation/artifacts/screenshots/` and confirm all canvases are nonblank, animated, color-tokened, responsive, and interactive.

## Solid fill priority

Use opaque, single-token filled marks without decorative borders first. Read
`solidSequence` and `textOnFill` from `assets/palettes/colorsets.json`. Reuse a
fill for the same semantic role; when roles must be distinct, exhaust every
usable distinct token in the preferred sequence, excluding the actual canvas,
before creating outline or tint combinations. Soft tokens occur late. For text
on a fill, use exactly black or white with the larger WCAG contrast computed
from the actual background; composite opacity before evaluating translucent
backgrounds. Do not infer text color from a hue name.

Keep connectors, axes, signal traces, open line art, physical geometry and
explicit source-fidelity modes. A stroke that depicts a relationship or is the
geometry itself is meaningful. Reserve decorative outlines for a documented
palette overflow or an explicit requested style; mark SVG overflow treatments
with `data-outline-tier="overflow"`. A transient keyboard focus ring remains an
interaction affordance. Use position, whitespace and direct labels for ordinary
selection and grouping.

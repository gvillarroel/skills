---
name: video
description: Orchestrate, compose, render, and validate mixed-media videos from artifacts produced by specialist skills. Use for storyboard-to-MP4, multi-scene, audio, or heterogeneous composition work that must route D3, ECharts, PlantUML, Mermaid, Three.js, raster images, GIFs, SVGs, Slidev, or other visual producers without reimplementing their tools; define exact dimensions and aspect ratio, place multiple elements in one scene, synchronize them to one master clock, specify semantic interactions between ports and states, capture deterministic frames, encode audio/video, and verify the final artifact. Route standalone SVG-only Manim rendering to `manim-svg-video`.
---

# Video

Treat this as the mixed-media video orchestrator. Own the source contract, output format, scene composition, cross-asset interaction, master timeline, final renderer, audio mux, review loop, and delivery gate. Do not recreate diagrams, charts, illustrations, 3D scenes, or standalone SVG-only video rendering that an available specialist skill owns.

Set `$env:VIDEO_SKILL` to this skill directory before copying bundled commands.

## Ownership boundary

- Route each source visual to one producer. The producer owns its internal semantics, geometry, styling, animation hooks, and validation report.
- Keep D3, ECharts, PlantUML, Mermaid, Three.js, image generation, animated-SVG/GIF conversion, standalone SVG-to-video rendering, and Slidev authoring inside their specialist skills.
- Keep video-level placement, crop, scale, z-order, camera, timing, transitions, shared state, connectors, audio, capture, and encoding here.
- Exchange files and contracts, never sibling-skill source imports. If a preferred skill is unavailable in an isolated workspace, preserve the same artifact contract and record a concrete fallback reason.

## Workflow

1. Freeze source facts, exact output paths, scene IDs, duration, audience, and requested deliverables. Read `references/source-package.md` and `references/storyboard-contract.md` for source-backed work.
2. Declare the output before laying out a scene: exact pixel width and height, derived aspect ratio, fps, duration, background, safe areas, and resize policy. Do not substitute a nearby social or broadcast preset.
3. Read `references/tool-routing.md`, select only the required producers, and request one validated artifact per visual role. Require stable asset IDs, output paths, hashes, intrinsic dimensions or `viewBox`, transparency/background behavior, semantic ports, controllable states, provenance, and a producer report.
4. Plan composition after producer contracts exist. Read `references/composition-selection-guide.md`, `references/content-budget-and-fidelity.md`, and `references/composition-brief-contract.md` when the scene is dense, diagram-like, or source-bound.
5. For a mixed scene, read `references/scene-interaction-contract.md`, start from the complete `assets/templates/scene-contract.json` example, and create `source/scene-contract.json`. Use one normalized stage, explicit element bounds, layer order, named ports, shared events, property tracks, and interactions. Keep producer internals isolated. Do not inspect validator source to infer the schema; write the complete contract, run the validator, and use only its report for corrections.
6. Validate the scene contract before renderer work:

   ```powershell
   uv run --script $env:VIDEO_SKILL/scripts/validate_scene_contract.py source/scene-contract.json --project-root . --require-files --json
   ```

7. Build the deterministic browser compositor for SVG, raster, GIF, and HTML assets:

   ```powershell
   uv run --script $env:VIDEO_SKILL/scripts/build_composite_scene.py source/scene-contract.json src/index.html --project-root . --json
   ```

   The compositor exposes `window.renderConceptFrame(videoId, seconds, options)` and returns active element, interaction, and state IDs. It embeds SVGs without redrawing them and decodes GIF frames against the master clock.
8. Use the bundled browser renderer for heterogeneous scenes and the bundled Slidev recorder only for a deck-first source. Route a standalone SVG/Manim-native sequence to `manim-svg-video`; if broader composition follows, consume its MP4 and manifest as producer outputs.
9. Read `references/transition-decision-guide.md` and `references/transition-plan-contract.md` for multi-scene work. Plan attention handoff and persistent semantic state before choosing an effect.
10. Render exact timestamps, inspect full-resolution frames and transition midpoints, create a contact sheet, review muted playback, correct failed scenes, rerender, and validate the MP4 dimensions, fps, duration, motion, and audio.

## Cross-element interaction rules

- Connect elements through named ports and scene events. Never make a Mermaid artifact call PlantUML code or a GIF query D3 state.
- Use the video scene bus for `signal`, `highlight`, `reveal`, `handoff`, `camera-follow`, and `data-state` interactions.
- Keep a single master clock. Pause autonomous CSS, SVG, GIF, canvas, iframe, and video timing during deterministic capture unless an adapter maps it to `seconds`.
- Inline SVG when an interaction targets an internal selector. Use element-local normalized ports when internals are opaque.
- Treat GIF internals as opaque. Animate the GIF container, or decode it to master-clock-controlled frames; do not claim internal-node interaction.
- Define geometry and semantic state separately: a connector may travel from one port to another while source and target state tracks control emphasis, visibility, or data state.
- Resolve ID collisions when several SVGs share a document. Preserve each producer's original artifact and apply namespacing only in the composed renderer.

## Routing map

- D3: bespoke SVG/data geometry, joins, simulations, linked views, or custom interaction.
- ECharts: conventional chart grammar and chart-specific SVG animation.
- PlantUML: UML, architecture, deployment, cloud, and notation-led technical diagrams.
- Mermaid: flow, sequence, state, relationship, schedule, and other Mermaid-native diagrams.
- Three.js: meaningful depth, camera motion, particles, materials, or WebGL interaction.
- Image generation: raster illustration, texture, cutout, or visual plate.
- Manim SVG video: standalone SVG-only sequencing and rendering; return an MP4 and composition manifest for optional downstream use here.
- Animated SVG to GIF: GIF conversion only; the video skill owns placement and synchronization afterward.
- Slidev/Anime.js or Slidev/ECharts: deck component authoring; the video skill owns recording and final media validation.

## Progressive disclosure

- `references/tool-routing.md`: producer selection, handoff fields, and ownership boundaries.
- `references/scene-interaction-contract.md`: mixed-media scene schema, ports, state bus, GIF behavior, and interaction patterns.
- `references/output-format-contract.md`: dimensions, ratios, safe areas, scaling, and variant rules.
- `references/source-package.md` and `references/storyboard-contract.md`: source freeze and shot planning.
- `references/composition-selection-guide.md`, `references/content-budget-and-fidelity.md`, and `references/composition-brief-contract.md`: spatial composition and fidelity accounting.
- `references/transition-decision-guide.md`, `references/transition-pattern-catalog.md`, and `references/transition-plan-contract.md`: multi-scene transitions.
- `references/browser-rendering.md`: deterministic browser capture, MP4 encoding, and review.
- `references/slidev-recording-workflow.md` and `references/slidev-recorder-options.md`: Slidev backend.

## Required delivery evidence

For a finished mixed-media video, provide the scene contract, specialist outputs and reports, built renderer, final MP4, render-state report, contact sheet, motion/quality reports, and the exact validation commands and results. A planning-only request may stop at validated source, composition, interaction, and transition contracts.

## Maintenance

After changing this skill, run its contract tests plus the repository validators. Use an isolated `pi` run before marking behavior done.

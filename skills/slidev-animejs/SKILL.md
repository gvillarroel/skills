---
name: slidev-animejs
description: "Builds, choreographs, troubleshoots, and validates Anime.js animations and embedded HyperFrames scenes inside Slidev presentations. Use when Codex needs to add reusable Vue animation components to a Slidev deck, wire Anime.js lifecycle cleanup with Slidev clicks and slide mounts, create CSS, keyframe, JavaScript object, stagger, timeline, playback, timer, animatable, easing, SVG, text, layout, draggable, scroll, scope, WAAPI, or engine-control demos, or verify animated Slidev decks in browser and export workflows."
---

# Slidev Anime.js

Read [the colorset output contract](references/colorset-contract.md) before authoring or auditing visual output. Apply one exact bundled palette to every authored output path and inspect rendered paint. Default to colorset1; declare colorset2 when its category distinctions are needed. Start category marks with opaque solid fills and no decorative borders; exhaust the selected palette's usable unique solids before outlined overflow variants. Choose black or white inside text by actual fill contrast.

For connected explanatory diagrams, use the smallest readable layout by
default. Follow [diagram compaction](references/integration-patterns.md#diagram-compaction)
to reduce idle gaps and route length while protecting labels, full arrowheads,
endpoint identity and motion clearance. Keep chart scales and useful data
dimensions intact; do not apply packing to unrelated animation studies.

For an ordered main row with an optional reciprocal check branch and backward
return, start with [the measured connected-flow scaffold](references/connected-flows.md)
instead of hand-sizing the diagram. It creates a native readable Vue stage,
separated ports, visible base routes and a parcel following the actual paths.

For configurable column counts, regular grids, or masonry collections, read [dynamic composition templates](references/dynamic-layouts.md) and copy `assets/templates/slidev-layouts/` into the deck. Keep the three copied runtime files unchanged; customize wrapper data/props and use its display-title prefix for visible order. Prefer the copy-ready collection parent for fixed readable cards, actual-width column limits and capacity-driven pagination; use the engine directly for custom control. Declare CLI/theme/Vue dependencies, retain complete category identities, and run the bundled static checker before native build/capture. Inspect capacity, all pages and real inner-width changes; preserve readable fixed typography and every component. Keep literal three-row masonry distinct from vertical column masonry.

For HyperFrames scenes inside a slide or a dynamic collection cell, read [HyperFrames integration](references/hyperframes-integration.md). Generate new starter decks with the bundled scaffold; merge its player resources manually into existing decks. Use the reusable preview component for Play/Pause controls, map Slidev clicks to explicit seek times, and pause inactive scenes. Use colorset1 and local Open Sans inside authored starter scenes because iframe styles are isolated; preserve explicit styling in supplied custom compositions. Validate backward seeks, slide reentry, actual cell dimensions and a deterministic static-export state.

For native Mermaid fences, install [the bundled diagram defaults](references/mermaid-defaults.md) once in the deck. Plain Mermaid source then inherits colorset1 automatically, with the same red/neutral palette and solid body treatment used by the Mermaid and PlantUML skills. Preserve existing setup hooks and explicit user styling.

Use [the static deck checker](scripts/check_mermaid_deck.py) before building: `uv run --script <skill-root>/scripts/check_mermaid_deck.py --deck deck --plain-mermaid --expect-blocks 3` for a requested three-block deck. It checks Mermaid fences and runtime inputs without modifying files. Slidev headmatter such as `theme: default` is separate from diagram source and is legal. Use native build/capture metadata for slide count and rendered geometry; do not count global `---` separators or opening/closing fence lines as slides or Mermaid blocks.

## Core Workflow

1. Put animation behavior in Vue components under the Slidev `components/` directory. Keep `slides.md` focused on slide composition and small props such as `$clicks`.
2. Install `animejs` next to the Slidev deck and import only the APIs needed by the component.
3. Run Anime.js code only after Vue mount. Query DOM nodes from a component root ref instead of using global selectors that can hit hidden Slidev slides.
4. Use `createScope({ root })` for component-local selectors, shared defaults, media query handling, and batch `revert()` on unmount or slide reruns.
5. Drive deterministic demo states from `$clicks`. Clamp click counts, keep target names and DOM structure stable, and restart, seek, or update animations intentionally when the slide step changes.
6. Give animated stages fixed slide-relative dimensions. Avoid animation that changes the outer slide layout unless testing Anime.js layout animation itself.
7. Prefer transform and opacity for frequent motion. Use SVG and text helpers when they express the story better than manual DOM mutation.
8. Validate with `npm --prefix <deck-root> run build`, then capture the built deck using `uv run --script <skill-root>/scripts/capture_deck.py --deck <deck-root> --output-dir <workspace-captures>`. Run bundled Python helpers through `uv run --script` so their declared dependencies are available. Inspect every animation slide, the screenshots and `capture.json`; the helper records native click, replay and reduced motion states and owns server cleanup. Confirm visible motion, complete labels/heads and actual click transitions; a captured image alone is not a quality pass.

## Reference

Read `references/integration-patterns.md` before implementing or debugging an Anime.js Slidev deck. It covers project shape, Vue lifecycle, scoped cleanup, `$clicks`, export, and verification.

For a named Anime.js capability, select its directly linked recipe below. Read `references/animation-type-index.md` for broad coverage or API lookup. Each animation pattern has one dedicated reference.

Read `references/assets/animated-svg-assets.md` when the task asks for SVGs that Anime.js can animate. It documents the generated SVG asset pack, stable selectors, and the copy-ready runtime template under `assets/templates/slidev-svg-asset-pack/`.

For normal work, copy only `assets/templates/slidev-svg-asset-pack/` into the target deck; it contains `components/SvgAssetSlide.vue`, `lib/svg-assets.js`, and the six SVG files under `assets/templates/slidev-svg-asset-pack/assets/animated-svg/`. Do not read or copy `assets/examples/` during normal skill use.

In an isolated workspace, copy the complete pack without enumerating the bundle: run `cp -R skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/. <deck-root>/` in bash or `Copy-Item skills/slidev-animejs/assets/templates/slidev-svg-asset-pack/* <deck-root> -Recurse -Force` in PowerShell. Replace `<deck-root>` with the exact requested deck path.

The runnable validation fixture under `assets/examples/slidev-animejs/` is maintenance-only. It consumes the runtime template through a thin wrapper so fixture validation exercises the same files shipped in the isolated runtime payload.

## Visual Tokens

Read `references/visual-tokens.md` before creating or updating animated Slidev examples, generated SVG assets, controls, or export fixtures. Use Open Sans for slide and SVG text, Material Symbols Rounded for system icons, and the documented brand palette for editable marks, stages, controls, highlight states, and generated assets.

## Pattern Promotion

When an Anime.js animation pattern, SVG asset hook, or Slidev lifecycle pattern proves reusable, update the owning reference before finishing. Use `references/animation-type-index.md` and the dedicated animation files for API-specific patterns, `references/integration-patterns.md` for Vue/Slidev lifecycle and `$clicks`, and `references/assets/animated-svg-assets.md` for SVG selector contracts. Include trigger, DOM contract, Anime.js API, cleanup/replay behavior, and validation command.

## Additional reference routes

Read only the resource matching the task.

## Direct recipe links

Select the matching recipe and read it in full.

- [animatable live input](references/animations/animatable-live-input.md).
- [css properties colors](references/animations/css-properties-colors.md).
- [css transforms](references/animations/css-transforms.md).
- [draggable interactions](references/animations/draggable-interactions.md).
- [easings springs](references/animations/easings-springs.md).
- [engine controls](references/animations/engine-controls.md).
- [js object values](references/animations/js-object-values.md).
- [keyframes relative values](references/animations/keyframes-relative-values.md).
- [layout transitions](references/animations/layout-transitions.md).
- [playback controls](references/animations/playback-controls.md).
- [scope media cleanup](references/animations/scope-media-cleanup.md).
- [scroll observer](references/animations/scroll-observer.md).
- [stagger sequences](references/animations/stagger-sequences.md).
- [svg drawable](references/animations/svg-drawable.md).
- [svg morph](references/animations/svg-morph.md).
- [svg motion path](references/animations/svg-motion-path.md).
- [text scramble](references/animations/text-scramble.md).
- [text split](references/animations/text-split.md).
- [timeline sequencing](references/animations/timeline-sequencing.md).
- [timers](references/animations/timers.md).
- [waapi animations](references/animations/waapi-animations.md).

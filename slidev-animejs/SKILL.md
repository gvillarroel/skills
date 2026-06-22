---
name: slidev-animejs
description: Build, choreograph, troubleshoot, and validate Anime.js animations inside Slidev presentations. Use when Codex needs to add reusable Vue animation components to a Slidev deck, wire Anime.js lifecycle cleanup with Slidev clicks and slide mounts, create CSS, keyframe, JavaScript object, stagger, timeline, playback, timer, animatable, easing, SVG, text, layout, draggable, scroll, scope, WAAPI, or engine-control demos, or verify animated Slidev decks in browser and export workflows.
---

# Slidev Anime.js

## Core Workflow

1. Put animation behavior in Vue components under the Slidev `components/` directory. Keep `slides.md` focused on slide composition and small props such as `$clicks`.
2. Install `animejs` next to the Slidev deck and import only the APIs needed by the component.
3. Run Anime.js code only after Vue mount. Query DOM nodes from a component root ref instead of using global selectors that can hit hidden Slidev slides.
4. Use `createScope({ root })` for component-local selectors, shared defaults, media query handling, and batch `revert()` on unmount or slide reruns.
5. Drive deterministic demo states from `$clicks`. Clamp click counts, keep target names and DOM structure stable, and restart, seek, or update animations intentionally when the slide step changes.
6. Give animated stages fixed slide-relative dimensions. Avoid animation that changes the outer slide layout unless testing Anime.js layout animation itself.
7. Prefer transform and opacity for frequent motion. Use SVG and text helpers when they express the story better than manual DOM mutation.
8. Validate with `npm run build`, then open the deck in a browser and inspect every animation slide. Confirm that each stage is nonblank, animations run, interactions work, and console errors are absent.

## Reference

Read `references/integration-patterns.md` before implementing or debugging an Anime.js Slidev deck. It covers project shape, Vue lifecycle, scoped cleanup, `$clicks`, export, and verification.

Read `references/animation-type-index.md` when the task names a specific Anime.js capability or asks for broad animation coverage. It routes to one dedicated reference file per animation pattern demonstrated in the acceptance deck.

Read `references/assets/animated-svg-assets.md` when the task asks for SVGs that Anime.js can animate. It documents the generated SVG asset pack, stable selectors, and the Slidev fixture component that exercises each asset.

The runnable validation fixture lives in `slidev-animejs/assets/examples/slidev-animejs/`. Keep one slide per tested animation type and keep the matching reference file updated whenever the fixture behavior changes.

## Visual Tokens

Read `../ANIMATED_VISUAL_TOKENS.md` before creating or updating animated Slidev examples, generated SVG assets, controls, or export fixtures. Use Open Sans for slide and SVG text, Material Symbols Rounded for system icons, and the documented brand palette for editable marks, stages, controls, highlight states, and generated assets.

## Pattern Promotion

When an Anime.js animation pattern, SVG asset hook, or Slidev lifecycle pattern proves reusable, update the owning reference before finishing. Use `references/animation-type-index.md` and the dedicated animation files for API-specific patterns, `references/integration-patterns.md` for Vue/Slidev lifecycle and `$clicks`, and `references/assets/animated-svg-assets.md` for SVG selector contracts. Include trigger, DOM contract, Anime.js API, cleanup/replay behavior, and validation command.

# Slidev Anime.js Integration Patterns

## Contents

- [Project Shape](#project-shape)
- [Dependencies](#dependencies)
- [Vue Lifecycle Contract](#vue-lifecycle-contract)
- [Slidev Click Stories](#slidev-click-stories)
- [Scope And Cleanup](#scope-and-cleanup)
- [Slide And Export Constraints](#slide-and-export-constraints)
- [Verification Checklist](#verification-checklist)
- [Diagram Compaction](#diagram-compaction)

## Project Shape

Use this structure for a local Slidev animation lab:

```text
slides.md
assets/
  animated-svg/
components/
  AnimeFeatureSlide.vue
  SvgAssetSlide.vue
lib/
  anime-demos.js
  svg-assets.js
styles/
  index.css
package.json
```

Slidev auto-loads Vue components from `components/`. Keep shared animation metadata in `lib/` so the same taxonomy can drive slides, references, and browser verification.

When the task needs the generated SVG pack, copy the contents of `assets/templates/slidev-svg-asset-pack/` from the loaded skill into the deck root. The template already matches the project shape above; its source SVGs live under `assets/templates/slidev-svg-asset-pack/assets/animated-svg/` and it does not depend on the acceptance fixture.

## Dependencies

Install and run npm in the deck directory, or use `--prefix <deck-root>`;
the current workspace may be its parent. Declare the selected Slidev theme
as a dependency, including `@slidev/theme-default` for the default theme,
before noninteractive builds. Keep capture scripts and screenshots in the
task workspace and read those exact paths; avoid `/tmp` paths when using
native Windows tools. Wait for a successful server readiness probe before
browser capture, and scope SVG locators to the visible slide component.
For a built deck, prefer `uv run --script <skill-root>/scripts/capture_deck.py --deck <deck-root>
--output-dir <workspace-captures>` over ad hoc server launch/capture code.
It owns a random localhost SPA server, awaits screenshots and shuts down its
browser and server. Review the actual state images and JSON; use `clicks: 2`
or matching `v-click` content when two native click transitions are required.

Install Anime.js next to the Slidev project:

```powershell
npm install animejs
```

Use Anime.js v4 module imports:

```js
import { animate, createScope, createTimeline, stagger, svg } from 'animejs'
```

Import specialized APIs only when needed: `createTimer`, `createAnimatable`, `createDraggable`, `createLayout`, `onScroll`, `splitText`, `scrambleText`, `waapi`, and `engine`.

## Vue Lifecycle Contract

A reusable Slidev animation component should:

- Render a fixed-size stage before Anime.js initializes.
- Store a root element with `ref`.
- Create animations in `onMounted` or after `nextTick`.
- Query descendants from the root element, not from `document`.
- Use `createScope({ root })` when selectors are convenient.
- Call `scope.revert()` and any explicit cleanup handlers in `onBeforeUnmount`.
- Restart, seek, or update animations when `$clicks` changes.

Use a clamped Slidev click step:

```js
const activeStep = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), 2))
```

## Slidev Click Stories

Pass `$clicks` from `slides.md` into the animation component:

```md
<AnimeFeatureSlide feature="timeline-sequencing" :step="$clicks" />
```

Inside the component, use click steps for deterministic states: a different stagger origin, a longer path, a changed SVG morph target, a reordered layout, or a different text target. Avoid random values in validation decks.

## Scope And Cleanup

Use `createScope` around Anime.js selectors so hidden slides do not animate by accident:

```js
scope = createScope({ root: root.value, defaults: { duration: 800, ease: 'outExpo' } })
scope.add(() => {
  animate('.mark', { x: 120, loop: true, alternate: true })
})
```

When a helper mutates the DOM outside normal animation instances, add explicit cleanup. `splitText()` should be reverted before recreating the animation, `createDraggable()` observers should be reverted, and WAAPI animations created outside scope should be cancelled.

## Slide And Export Constraints

- Keep animated stages inside fixed grid tracks or fixed-height containers.
- Prefer `x`, `y`, `scale`, `rotate`, and `opacity` for frequent motion.
- Keep looped animations short enough to be readable in presenter mode.
- Avoid relying on external assets or uncached network data for export.
- For animated SVG assets, import trusted local SVG files as raw strings and inline them before running Anime.js. Do not load them with `<img>` when internal paths, groups, or attributes need to be animated.
- Respect reduced motion when the deck is meant for broad presentation use; at minimum, keep motion purposeful and not full-screen flashing.

## Diagram Compaction

For concepts joined by lines, size nodes from rendered labels and use the
shortest clear routes between explicit endpoint ports. Reduce surplus node
padding, rank gaps, stage wrappers and edge detours before changing visual
scale. Keep the requested slide/stage dimensions and preserve minimum readable
text, strokes and head sizes at their final scale.

Reserve distinct lanes for unrelated edges and the complete painted envelopes
of labels, heads and moving objects, including spring overshoot. Heads must
remain outside opaque target shapes, and every line must visibly leave the
intended source. Never let packing turn crossings into apparent junctions.

After a first browser render, compare a tighter local arrangement with the
baseline at the same scale. Inspect initial, settled click, replay and reduced
motion states plus closest motion approaches. Reject overlap, clipping,
occlusion, ambiguous routes or unreadable paint; restore the local clearance
that failed. Keep the smallest passing candidate and stop when another local
reduction harms reading or motion. Record the changed gaps and protected
clearances in verification notes. A smaller font or deleted fact is not a
compaction improvement. For charts, improve useful information density while
preserving axes, scale, legends and mark separation.

## Verification Checklist

Run these checks before considering a Slidev Anime.js deck ready:

1. `npm run build` succeeds from the Slidev project directory.
2. Every animation slide mounts without console errors.
3. Every stage contains visible animated output, not just static labels.
4. `$clicks` changes the animation state without stale DOM wrappers or duplicated split-text spans.
5. SVG helper slides render visible paths, movers, or morph targets.
6. Generated SVG asset slides expose stable internal hooks such as `.svg-drawable`, `#orbit-path`, or `.machine-signal` and animate those hooks through scoped selectors.
7. Interactive slides keep pointer targets inside the slide frame.
8. The skill has a dedicated reference file for every animation type demonstrated in the deck.

# Slidev Anime.js Integration Patterns

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

## Dependencies

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

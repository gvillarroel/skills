# Anime.js Animation-Type Index For Slidev

Use this index when choosing a motion pattern for a Slidev story. Load only the specific reference needed after reading the core workflow.

## Animation References

- `animations/css-transforms.md`: transform and opacity animation for DOM marks.
- `animations/css-properties-colors.md`: CSS dimensions, colors, border radius, and variables.
- `animations/keyframes-relative-values.md`: keyframes, from values, relative values, and multi-step tweens.
- `animations/js-object-values.md`: counters, meters, and animated non-DOM state.
- `animations/stagger-sequences.md`: delayed list or grid waves across many targets.
- `animations/timeline-sequencing.md`: coordinated sequences, labels, offsets, timers, and callbacks.
- `animations/playback-controls.md`: play, pause, seek, reverse, restart, complete, cancel, reset, and revert.
- `animations/timers.md`: `createTimer` for callbacks, counters, loops, and synchronization.
- `animations/animatable-live-input.md`: efficient property setters for frequent pointer or click updates.
- `animations/easings-springs.md`: built-in eases, cubic Bezier, steps, irregular, and spring motion.
- `animations/svg-drawable.md`: SVG stroke draw-on and erase effects.
- `animations/svg-motion-path.md`: moving targets along an SVG path.
- `animations/svg-morph.md`: morphing SVG path, polygon, or polyline shapes.
- `animations/text-split.md`: character, word, or line reveal with `splitText`.
- `animations/text-scramble.md`: character scramble and reveal with `scrambleText`.
- `animations/layout-transitions.md`: FLIP-style layout transitions after DOM order, parent, or display changes.
- `animations/draggable-interactions.md`: pointer-driven draggable elements with release physics.
- `animations/scroll-observer.md`: `onScroll` triggers and scroll-synchronized progress.
- `animations/scope-media-cleanup.md`: root scoping, media queries, defaults, and batch cleanup.
- `animations/waapi-animations.md`: WAAPI-powered transform and opacity animation.
- `animations/engine-controls.md`: engine speed, fps, pause, resume, and global defaults.

## Shared Example Fixture

The validation deck in `.agents/skills/slidev-animejs/assets/examples/slidev-animejs/` uses one component, `components/AnimeFeatureSlide.vue`, and one metadata file, `lib/anime-demos.js`.

Keep the animation keys stable because `slides.md`, browser verification, and reference routing depend on them:

```text
css-transforms
css-properties-colors
keyframes-relative-values
js-object-values
stagger-sequences
timeline-sequencing
playback-controls
timers
animatable-live-input
easings-springs
svg-drawable
svg-motion-path
svg-morph
text-split
text-scramble
layout-transitions
draggable-interactions
scroll-observer
scope-media-cleanup
waapi-animations
engine-controls
```

Use deterministic shapes, text, positions, and click states. Animation randomness is acceptable only when seeded or when the final visual state is not part of validation.

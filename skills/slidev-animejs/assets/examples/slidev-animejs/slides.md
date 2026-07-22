---
theme: default
title: Slidev Anime.js Animation Lab
info: |
  A validation deck for mastering Anime.js animation patterns inside Slidev through reusable Vue components, scoped lifecycle cleanup, one slide per tested animation type, and generated SVG assets with animation hooks.
transition: slide-left
mdc: true
drawings:
  persist: false
---

# Slidev + Anime.js

<div class="hero-motion-grid">
  <div class="hero-copy">
    <p class="eyebrow">Animation lab</p>
    <h2>One scoped Vue pattern across the Anime.js motion surface used in Slidev.</h2>
    <p>
      This deck validates component lifecycle, click-driven state, CSS, object values,
      timelines, playback, timers, SVG helpers, generated SVG assets, text helpers, layout, interactions, WAAPI, and engine controls.
    </p>
    <div class="hero-facts">
      <span>21 animation types</span>
      <span>6 SVG assets</span>
      <span>Scoped cleanup</span>
    </div>
  </div>
  <div class="hero-stage">
    <div class="motion-chip">CSS</div>
    <div class="motion-chip">Timeline</div>
    <div class="motion-chip">Timer</div>
    <div class="motion-chip">SVG</div>
    <div class="motion-chip">Text</div>
    <div class="motion-chip">Interaction</div>
  </div>
</div>

---

# Component Contract

<div class="two-column">
  <div class="checklist">
    <p class="eyebrow">Reusable Slidev component</p>
    <h2>Mount, scope, animate, revert.</h2>
    <ul>
      <li>Query targets from a component root, not from global document selectors.</li>
      <li>Wrap selectors with <code>createScope({ root })</code> and call <code>revert()</code> on rerun or unmount.</li>
      <li>Drive deterministic variants from <code>$clicks</code>.</li>
      <li>Keep stage dimensions stable so animation does not resize the slide.</li>
    </ul>
  </div>
  <pre class="code-panel"><code>&lt;AnimeFeatureSlide
  feature="timeline-sequencing"
  :step="$clicks"
/&gt;</code></pre>
</div>

---

# CSS Transforms

<AnimeFeatureSlide feature="css-transforms" :step="$clicks" />

<v-clicks class="chart-clicks">

- Animate transform and opacity inside a fixed stage.
- Confirm scoped selectors only touch the current slide component.
- Keep outer slide layout stable while marks move.

</v-clicks>

---

# CSS Properties, Colors, And Variables

<AnimeFeatureSlide feature="css-properties-colors" :step="$clicks" />

<v-clicks class="chart-clicks">

- Animate width, radius, and color without resizing the slide.
- Drive an accent through a local CSS variable.
- Keep contrast readable through the tween.

</v-clicks>

---

# Keyframes And Relative Values

<AnimeFeatureSlide feature="keyframes-relative-values" :step="$clicks" />

<v-clicks class="chart-clicks">

- Move through a multi-stop keyframe path.
- Use per-stop easing for overshoot and settle.
- Apply relative movement without creating new DOM.

</v-clicks>

---

# JavaScript Object Values

<AnimeFeatureSlide feature="js-object-values" :step="$clicks" />

<v-clicks class="chart-clicks">

- Animate a plain object that drives visible DOM.
- Render a counter and meter in <code>onUpdate</code>.
- Keep computed values deterministic for screenshots.

</v-clicks>

---

# Stagger Sequences

<AnimeFeatureSlide feature="stagger-sequences" :step="$clicks" />

<v-clicks class="chart-clicks">

- Distribute delay through a fixed grid.
- Compare first, center, and last origins with clicks.
- Keep grid dimensions stable while cells scale.

</v-clicks>

---

# Timeline Sequencing

<AnimeFeatureSlide feature="timeline-sequencing" :step="$clicks" />

<v-clicks class="chart-clicks">

- Coordinate multiple targets with shared defaults.
- Use labels and relative offsets for maintainable timing.
- Include callbacks without leaking global side effects.

</v-clicks>

---

# Playback Controls

<AnimeFeatureSlide feature="playback-controls" :step="$clicks" />

<v-clicks class="chart-clicks">

- Pause at the authored start state.
- Seek to a deterministic midpoint.
- Reverse and restart from click state.

</v-clicks>

---

# Timers

<AnimeFeatureSlide feature="timers" :step="$clicks" />

<v-clicks class="chart-clicks">

- Use Anime.js timing without an animated target.
- Render timer progress into a numeric label.
- Revert the timer when leaving the component.

</v-clicks>

---

# Animatable Live Input

<AnimeFeatureSlide feature="animatable-live-input" :step="$clicks" />

<v-clicks class="chart-clicks">

- Use generated property setters for frequent updates.
- Move the marker from pointer movement or click state.
- Keep pointer bounds local to the slide stage.

</v-clicks>

---

# Easings And Springs

<AnimeFeatureSlide feature="easings-springs" :step="$clicks" />

<v-clicks class="chart-clicks">

- Compare easing families from identical start and end positions.
- Include cubic Bezier, stepped, and spring motion.
- Keep spring settlement inside the stage.

</v-clicks>

---

# SVG Drawable

<AnimeFeatureSlide feature="svg-drawable" :step="$clicks" />

<v-clicks class="chart-clicks">

- Convert SVG paths into drawable proxies.
- Stagger line draw-on timing across segments.
- Verify strokes remain visible inside the Slidev frame.

</v-clicks>

---

# SVG Motion Path

<AnimeFeatureSlide feature="svg-motion-path" :step="$clicks" />

<v-clicks class="chart-clicks">

- Map a marker to SVG path coordinates.
- Rotate the marker along path inclination.
- Draw the route while the marker moves.

</v-clicks>

---

# SVG Morph

<AnimeFeatureSlide feature="svg-morph" :step="$clicks" />

<v-clicks class="chart-clicks">

- Morph a source path into a hidden target path.
- Keep fill, stroke, and viewBox deterministic.
- Browser-check the interpolated shape, not only build success.

</v-clicks>

---

# Generated SVG: Drawable Circuit

<SvgAssetSlide asset="drawable-circuit" :step="$clicks" />

---

# Generated SVG: Motion Orbit

<SvgAssetSlide asset="motion-orbit" :step="$clicks" />

---

# Generated SVG: Morphing Badge

<SvgAssetSlide asset="morphing-badge" :step="$clicks" />

---

# Generated SVG: Stagger Dashboard

<SvgAssetSlide asset="stagger-dashboard" :step="$clicks" />

---

# Generated SVG: Timeline Machine

<SvgAssetSlide asset="timeline-machine" :step="$clicks" />

---

# Generated SVG: Interactive Hotspots

<SvgAssetSlide asset="interactive-hotspots" :step="$clicks" />

---

# Split Text Reveal

<AnimeFeatureSlide feature="text-split" :step="$clicks" />

<v-clicks class="chart-clicks">

- Split a short heading into character targets.
- Stagger reveal without nesting repeated wrappers.
- Revert split text before rerunning.

</v-clicks>

---

# Scramble Text

<AnimeFeatureSlide feature="text-scramble" :step="$clicks" />

<v-clicks class="chart-clicks">

- Reveal a short phrase with deterministic scramble.
- Use <code>innerHTML</code> as the animated property.
- Change target phrase from click state.

</v-clicks>

---

# Layout Transitions

<AnimeFeatureSlide feature="layout-transitions" :step="$clicks" />

<v-clicks class="chart-clicks">

- Record and animate CSS layout changes.
- Keep the layout root fixed in size.
- Change arrangement and order from click state.

</v-clicks>

---

# Draggable Interactions

<AnimeFeatureSlide feature="draggable-interactions" :step="$clicks" />

<v-clicks class="chart-clicks">

- Create a bounded draggable target.
- Keep pointer interaction inside the slide stage.
- Add an automated nudge for browser validation.

</v-clicks>

---

# Scroll Observer

<AnimeFeatureSlide feature="scroll-observer" :step="$clicks" />

<v-clicks class="chart-clicks">

- Use an internal scroll container.
- Drive animation with <code>onScroll</code>.
- Avoid fighting Slidev page navigation.

</v-clicks>

---

# Scope, Media Queries, And Cleanup

<AnimeFeatureSlide feature="scope-media-cleanup" :step="$clicks" />

<v-clicks class="chart-clicks">

- Scope selectors to the current component root.
- Use media query matches for reduced-motion handling.
- Revert all scoped animations on rerun or unmount.

</v-clicks>

---

# WAAPI Animations

<AnimeFeatureSlide feature="waapi-animations" :step="$clicks" />

<v-clicks class="chart-clicks">

- Use Anime.js WAAPI mode for simple transform motion.
- Keep JavaScript-engine features for SVG, text, and layout.
- Clean up WAAPI animations on unmount.

</v-clicks>

---

# Engine Controls

<AnimeFeatureSlide feature="engine-controls" :step="$clicks" />

<v-clicks class="chart-clicks">

- Change engine speed from click state.
- Demonstrate pause and resume without leaving the engine paused.
- Restore global engine state during cleanup.

</v-clicks>

---

# Validation Targets

<div class="validation-grid">
  <div>
    <p class="eyebrow">Build</p>
    <h2>The production deck must compile with Anime.js v4 module imports.</h2>
    <p><code>npm run build</code> catches missing exports, invalid Vue syntax, and bundling problems.</p>
  </div>
  <div>
    <p class="eyebrow">Browser</p>
    <h2>Every animation slide must render visible motion without console errors.</h2>
    <p>Playwright should visit each animation and SVG asset slide, advance clicks, and verify that the stage is nonblank.</p>
  </div>
  <div>
    <p class="eyebrow">Reference</p>
    <h2>Every animation type has a dedicated skill reference.</h2>
    <p>The reference files document use cases, Anime.js APIs, Slidev patterns, fixture coverage, generated SVG hooks, and pitfalls.</p>
  </div>
</div>

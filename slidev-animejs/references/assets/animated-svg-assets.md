# Animated SVG Asset Pack

Use these generated SVG files when a Slidev Anime.js deck needs vector artwork that can be animated without redrawing the asset in JavaScript. The assets live in `examples/slidev-animejs/assets/animated-svg/` and are imported with Vite `?raw` so their internal SVG nodes are available to Anime.js selectors.

## Integration Pattern

1. Keep SVGs as standalone files with a stable `viewBox`, semantic `title`, and `desc`.
2. Add animation hooks as explicit `id`, `class`, and `data-anime-*` attributes.
3. Inline the SVG in a Vue component with a trusted local raw import or with `v-html` from a bundled string.
4. Create Anime.js animations after `nextTick()` so the injected SVG nodes exist.
5. Scope selectors to the component root with `createScope({ root })`.
6. Prefer `svg.createDrawable()`, `svg.createMotionPath()`, `svg.morphTo()`, `stagger()`, and `createTimeline()` for SVG-specific motion.

## Assets

| Asset | Source file | Primary hooks | Anime.js use |
| --- | --- | --- | --- |
| Drawable Circuit | `drawable-circuit.svg` | `.svg-drawable`, `.svg-node`, `[data-anime-group="drawables"]` | Draw independent circuit paths, then pulse signal nodes with staggered timing. |
| Motion Orbit | `motion-orbit.svg` | `#orbit-path`, `#orbit-traveler`, `.orbit-ring`, `.orbit-pulse` | Move a grouped traveler along a route while drawing the path and rotating rings. |
| Morphing Badge | `morphing-badge.svg` | `#badge-source`, `#badge-target-star`, `#badge-target-wave`, `#badge-target-diamond`, `.badge-spark` | Morph a visible source path into hidden targets selected by Slidev click state. |
| Stagger Dashboard | `stagger-dashboard.svg` | `.dashboard-card`, `.dashboard-bar`, `.dashboard-dot` | Stagger dashboard cards and scale metric bars from a fixed left origin. |
| Timeline Machine | `timeline-machine.svg` | `.machine-cable`, `.machine-gear`, `.machine-block`, `.machine-signal` | Sequence cable draw-on, gear rotation, conveyor movement, and signal pulses in one timeline. |
| Interactive Hotspots | `interactive-hotspots.svg` | `.map-route`, `.map-hotspot`, `.map-callout`, `[data-region]` | Draw a route and rotate active emphasis across hotspots from click or pointer state. |

## Slidev Fixture

The fixture component is `examples/slidev-animejs/components/SvgAssetSlide.vue`. It imports each asset as raw SVG from `examples/slidev-animejs/lib/svg-assets.js`, injects it into a fixed stage, and runs one Anime.js animation recipe per asset.

Use it in `slides.md` with a clamped click state:

```md
<SvgAssetSlide asset="motion-orbit" :step="$clicks" />
```

## SVG Authoring Rules

- Keep the outer `svg` dimensions independent from Slidev layout; use `viewBox` for scaling.
- Do not rely on CSS files outside the SVG for the initial static appearance.
- Avoid randomly generated IDs. Use readable, stable names such as `#orbit-path` or `.machine-signal`.
- Put hidden morph targets inside the same SVG as the visible source path.
- Use grouped elements for motion path travelers so Anime.js can move the full icon as one target.
- Keep decorative background shapes separate from animation hooks so broad selectors do not animate them by accident.

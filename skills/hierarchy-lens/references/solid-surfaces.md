# Solid surfaces and category capacity

Use this recipe for authored diagram nodes, labels, categorical marks, frames,
controls and video chrome in either colorset. Preserve an explicit requested
style, source photographs/video/artwork, meaningful connectors, axes, paths and
physical line geometry. A technical wire or an open vessel wall is meaningful
geometry; a dark outline around an otherwise filled card is decoration.

1. Assign a semantic identity once and reuse it across views. Read the selected
   `assets/palettes/colorsets.json` entry's `solidSequence`. Filter only the actual
   canvas color. Use every remaining distinct solid before repeating a fill.
   Begin with base and saturated colors, then dark, bright and neutral solids;
   soft colors are late alternatives. Do not restrict capacity to the six base
   hues, skip neutral colors, or begin with pale fills carrying dark outlines.
2. Paint each category surface with one opaque fill and `stroke="none"` / zero
   border width. Put gaps between adjoining objects where separation helps.
   Keep direct labels and semantic shapes. Use weight, position, scale or a
   separate marker for ordinary emphasis before adding an outline.
3. Pair each inside label with the actual solid behind the letters. Use the
   selected palette's `textOnFill[fill]`: it selects exact `#000000` or `#ffffff`
   by the higher WCAG sRGB relative-luminance contrast. Do not use a brightness
   guess, near-black, an unconditional white label or a color that merely passes
   on the outer canvas. Keep text outside a mark on the actual canvas pairing.
4. Only after exhausting all usable solids, begin an explicit overflow cycle.
   Reuse fills with border color, then dash, then width variants; keep direct
   labels and show this composite identity consistently in legends and views.
   A border alone cannot justify repeating a color while another usable solid
   remains. For producers with a bundled palette helper, that helper
   exposes `solid_colors`, `text_on_fill` and `category_style`; the latter reports
   `overflow` and keeps stroke width zero throughout the first solid cycle.
5. Regenerate from the owning source. Inspect initial, changed and export states.
   Check first-cycle border width, uniqueness before overflow, and the actual
   text/fill pairs. Preserve interaction focus cues and semantic line marks.
   Alpha used for motion/focus is a compositing state, not a new category color;
   keep inside labels opaque or review their composited background separately.

Do not recolor an imported producer asset implicitly. Restyle it at its owning
producer when the request includes that source, and identify source-preserved
pixels separately from authored wrapper paint.

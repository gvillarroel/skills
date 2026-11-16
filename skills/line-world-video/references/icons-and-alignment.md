# Icon contrast and centered content

Apply these rules to authored semantic objects and their states. Preserve the
original colors and geometry of paper captures, portraits and real brand marks.

## Foreground follows the visible face

Use white `#ffffff` text and monochrome icons inside a solid primary-red
`#9e1b32` face. Use dark ink on light gray or white. On secondary dark gray,
choose a readable foreground; the theme selects white. Recompute both the
new active object and the previous inactive object whenever focus changes.
Do not leave hard-coded gray icon strokes inside a red face.

Mark a semantic monochrome SVG wrapper, `<use>` or external SVG `<image>` with
`data-lw-icon="monochrome"`. Keep holes transparent and retain the original
stroke geometry. The bundled theme maps the rendered alpha to the selected
foreground; it handles hard-coded child paint, symbol references and external
SVGs without fetching or rewriting their sources. Do not mark a photograph or
multicolor logo as monochrome. Give a real logo a white backing or use an
approved monochrome source variant when its colors lack contrast.

Call `LineWorldTheme.finish(svg)` after fonts and image assets load. Use
`LineWorldTheme.focus(svg,target,'primary')` for reversible emphasis, or call
`LineWorldTheme.contrast(svg)` after custom fill changes. The helpers adapt
icons and internal text together. A target can be a glyph or its containing
semantic object. Keep attention ports outside the visible content bounds.

## Center the complete content block

Center the combined icon and label block horizontally **and** vertically using
its actual rendered bounds. Do not equate a text baseline, an SVG viewBox center
or a font's nominal height with its visible center. Keep the intended gap
between icon and label; move the complete block together. Preserve external
labels, axes, chart coordinates and data geometry.

For a simple item, put its face and internal content in their own parent group.
`finish` adopts direct internal text and marked icons into one centered wrapper.
For deliberate layouts, mark the wrapper explicitly:

```html
<g>
  <rect id="training-face" data-lw-surface="item"
        x="100" y="100" width="240" height="160" fill="#9e1b32"/>
  <g data-lw-content data-lw-for="training-face">
    <g data-lw-icon="monochrome"><!-- Real provider paths. --></g>
    <text x="170" y="180">Training</text>
  </g>
</g>
```

Use `LineWorldTheme.center(svg)` after changing content or container geometry.
Repeated calls are idempotent and account for transformed/scaled parents. Add
new children to the existing content wrapper. The helper centers; it does not
shrink or reflow oversized text. Enlarge the face, shorten a label with meaning
preserved, or change the layout if the audit reports overflow.

For nested bubbles or several cards, give **each face its own parent**. Do not
let an enclosing face adopt the labels of smaller objects. Use
`data-lw-align="preserve"` for deliberate data alignment. Quantitative/category
faces already marked `data-encoding`, `data-color-role` or
`data-lw-preserve="paint"` retain their deliberate geometry. White grouping
shells do not automatically center their entire contents; use an explicit
content wrapper only when that group truly represents one centered object.
For HTML containers, `data-lw-layout="center"` provides flex centering in both
axes. Do not use that CSS marker as a substitute for SVG geometry.

## Verify the actual states

```text
uv run --script <skill-root>/scripts/inspect_items.py --html film/index.html --all-states --output review/items.json --screenshot review/items.png
```

The helper uses the authored scene cues or beat reading poses in one local
browser run. For custom clocks, supply `--times 2,5,8` and optionally
`--scene-index 0`. Load the real theme in the source first; the inspector never
injects a repair. It reports visible icon counts, white-foreground counts,
centered content and exact findings. No icon count means this pose has no
marked icon inside a face; it does not certify unmarked assets.

`LineWorldTheme.audit(svg)` fails for incorrect or unverified marked icon ink,
content displaced by more than two CSS pixels in either axis, and content that
overflows its face. `LineWorldFocus.audit` includes those findings when the theme
is loaded. Inspect active, inactive and return-seek states visually at playback
size. Check actual white pixels for symbol/external SVGs; a correct CSS `color`
alone does not prove their strokes changed. Geometric centering is measurable;
optical balance still needs a visual check, especially for asymmetric glyphs.

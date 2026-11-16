# Red first, gray second, black last

## Contents

- [Composition hierarchy](#composition-hierarchy)
- [Semantic priority](#semantic-priority)
- [Vivid emphasis](#vivid-semantic-emphasis)

## Composition hierarchy

Make the overall composition predominantly white. Use grayscale to organize
structure, context, readable information and secondary comparisons. Use primary
red selectively to direct attention to the current object, value or relation.
This is a flexible visual direction, not a fixed percentage, pixel budget or
prescribed background split. Judge shapes, negative space, contrast and visual
weight together. A large empty white background alone does not establish a good
composition; meaningful objects must remain visible during camera travel.

Use borderless solid gray for small individual objects. Use solid primary red
with white internal labels and monochrome icons for their active emphasis. Keep group/container
interiors white with a discreet outline so nested content does not become a
large saturated panel. Keep neutral
structure legible rather than fading it merely to make the frame look whiter.
Review representative reading frames and transitions by eye; preserve the
hierarchy without a numerical pass/fail quota.

After custom body recoloring, call `LineWorldTheme.contrast(root)` to recompute
internal label contrast. It handles nested SVG text/tspans and HTML labels in
foreignObject; HTML uses `color`, while SVG uses `fill`. Recompute inactive labels
too, including unbound numeric values, so a previous white label returns to dark
ink on a gray face. Mark monochrome glyphs `data-lw-icon="monochrome"` so their
actual strokes follow the face too. Center each combined icon/label block in
both axes after fonts load. Read [icon contrast and centering](icons-and-alignment.md)
for the markers, geometry helper and actual-state audit. Check both the selected
state and the state after focus moves.

Use colorset2 exceptionally when a graph or chart needs additional distinct
colors for several entities, categories or independent data lines. Record the
entity-to-color mapping and maintain it across representations. Extra colors
should explain identity rather than add decoration. Keep the composition light
and the main attention cue red. Preserve photographic and brand colors; real
portraits or logos do not by themselves require a diagram palette change.

The shared `assets/palettes/video-color-direction.json` stores this qualitative
direction for every dedicated visual producer. The canonical base tokens stay
unchanged.

## Semantic priority

Apply this priority to both palettes and every producer in the video plugin:

1. Use primary red `#9e1b32` for the main series, active relation, selected edge
   and guide. Use borderless red fill for a small active object; keep large group panels white.
2. Use dark gray `#696969` for a second highlighted series or comparison bar.
   Its semantic role is `secondaryHighlight`; red remains the primary emphasis.
   Use light and medium grays for inactive geometry and quiet quantitative areas:
   `#e7e7e7`, `#cfcfcf`, `#b5b5b5`, `#9c9c9c` and `#828282`.
3. Use charcoal `#333e48` for readable text, icons and fine structural outlines.
   Use very dark neutrals `#363636`, `#1c1c1c` and black `#000000` only after
   the lighter options fail a concrete contrast or notation requirement.
   Do not assign a large category block black as the second default color.

White remains the canvas and normal diagram surface. Keep the primary guide
red in either palette. Introduce colorset2 hues only for documented simultaneous
identities; explicit category mappings remain stable across views. Do not
replace their semantics merely to reorder a decorative palette.

The private `assets/palettes/video-colors.json` preserves exact allowed tokens
but changes their ordered sequences for this video style. Keep the baseline
`assets/palettes/colorsets.json` unchanged. All five packaged skills receive
both files; their video palette readers use the style file. The builder exports
`colorSequence` to `story.js`;
the linked starter uses it for proportional category fills. Do not import the
general producer's black-second sequence into the film. Keep the general
canonical skills unchanged.

## Vivid, semantic emphasis

Use `#828282` for essential neutral contours on white; keep `#cfcfcf` and
`#e7e7e7` for supporting separators, inactive surfaces and quiet context. Fine
mechanism strokes still need to survive the final delivery scale. Do not fade
all useful objects until a reveal completes.

Keep the guide exactly `#9e1b32`. Small ordinary objects use solid light or
medium gray, with no border; the active object uses solid primary red and
readable white internal labels. Outside labels may stay red. Groups/containers
keep white interiors, with a discreet gray outline or a red focus outline.
Do not use pink object backgrounds or translucent red surfaces that composite
to pink. The secondary comparison stays dark gray `#696969`. Preserve actual
quantities, category mappings, matrix pixels, portraits and complete logos.

Mark surface shapes `data-lw-surface="item"` or `"group"`. Use semantic roles,
not a pixel-size cutoff, to distinguish an object from a container. Call
`LineWorldTheme.finish(stageSvg)` once after constructing the figure and loading
fonts. It supplies gray borderless item faces, white group shells and readable
internal text. It leaves encoded fills intact. Mark quantitative/category fills
with `data-encoding` or `data-lw-preserve="paint"`; do not reinterpret data as
an ordinary decorative surface.

Call `LineWorldTheme.focus(stageSvg, target, 'primary')` or `'secondary'` from
the parent-clock render function. The target may be one element or an array of
related elements. A text target can resolve to its containing small item face.
Focus chooses readable internal text, uses solid emphasis for ordinary items,
and preserves nested gray contents when a group shell is selected. Pass null
to clear. Exact original inline values and priorities are restored on a later
seek; no geometry, autonomous timer or data quantity changes. Copy both
`theme.js` and `theme.css` into custom compositions. Existing project themes
need an explicit `colors.line` change to adopt the stronger contour default.

Use `data-lw-focus-mode="group"` on a logical grouping without an explicit
shell. The optional `data-focus-fill="outline"` requests a white outlined
surface; `"solid"` remains compatible with an earlier authored ordinary item.
`data-focus-on-fill` is available for explicit internal text, although automatic
containment handles normal boxes. Keep labels outside the object unmarked.
The bundled palette omits pink from generated category sequences; canonical
base tokens remain unchanged.

The standalone `inspect_focus.py` also checks marked surfaces: ordinary item
borders and filled group shells are reported as style defects. Add
`--scene-index N` for a scene-local composition; the helper supports `renderClip`
or a two-argument `renderAt` without a custom browser driver. This lets repeated
example reviews share one inspection command.

Use charcoal on pale gray and white text on red when contrast permits. Small
black text on a mid-gray is an acceptable last contrast choice; a black panel
is not the default workaround. Keep quantitative area, length and units intact.
Sankey bands and secondary stacked areas use pale grays without altering width.

Run the actual browser audit. It rejects pink geometric surfaces, including
translucent red composited over white, without inspecting photographic pixels.
It also rejects neutral dark filled marks occupying
more than two percent of the reading frame, and broad dark strokes with the
same footprint. Text, fine outlines and tiny notation marks are outside that
large-block rule. A genuine quantitative comparison bar may use `#696969` with
`data-color-role="secondary-highlight"`, `data-encoding="quantity"` and a finite
positive `data-value`; the narrowly scoped exception covers at most 12% of the
frame, not dark panels, black blocks or broad dark strokes.
Inspect a category frame, wide quantitative bands, native
diagrams, the overview and a repeated seek. Keep explicit user-requested dark
styles as a separate adapted brief rather than silently weakening this default.

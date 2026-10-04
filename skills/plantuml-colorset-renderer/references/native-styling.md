# Native PlantUML Style Delivery

## Contents

- [Editable style resources](#editable-style-resources)
- [Finished delivery](#finished-delivery)
- [Raster-only Ditaa](#raster-only-ditaa)
- [Refreshing embedded themes](#refreshing-embedded-themes)
- [Maintenance checks](#maintenance-checks)

Use this reference when styling a family, debugging missing theme effects, or
changing the renderer. Deliver through `scripts/render_plantuml_directory.py`;
loading a theme directly into PlantUML covers only the native part of the style
contract. Some upstream primitives hardcode their outline or paint.

## Editable style resources

Edit `assets/themes/cs1.puml` or `assets/themes/cs2.puml` for native defaults.
Edit `assets/themes/native-style-rules.json` for the exact fallback paints of
ArchiMate layers and Salt buttons, the grammar canvas, and semantic detail
thickness. The finisher validates those paints against the selected palette.
For Colorset1, start each family's primary body with `#9e1b32`. Allocate
secondary kinds from the gray group before near-black, black, white, and the
remaining red hues or pink. Read the exact priority in `solidSequence` rather
than selecting a dark red as the second category. A white canvas excludes only
that exact token from categorical capacity; text and semantic strokes use their
actual contrast instead of consuming category slots.

The seven ArchiMate layers (Technology, Application, Business, Motivation,
Strategy, Physical, Implementation) retain their native semantic names. Colorset1
uses `archimateRoleOrder` to rank Business, Application, Technology, Motivation,
Strategy, Physical, and Implementation. Read the editable `archimate` colors in
that rank as an ordered pool and compress absent layers: the first active layer
uses primary red, the second gray1, and so on. A one-layer Technology or
Application diagram therefore starts red. The finished report records
`archimateLayers`; SVG records `data-native-layer-map` and each body's native
layer. Colorset2 keeps its fixed layer map. Explicit authored presentation
remains authoritative.

Native Colorset1 charts likewise compress active bar, line, and scatter mark
kinds onto primary red, gray1, and gray2 in that rank. A line-only or
scatter-only chart starts primary red. The report records `chartMarks` and SVG
records `data-native-mark-map`; preserve coordinates, values, axes and explicit
source paint. Repeated series of the same native mark kind share its default
role; distinct independent categories use explicit `solid_style` allocation.
These editable files form one delivery configuration; do not duplicate their
values in an ad hoc gallery stylesheet.
Keep family selectors scoped: `objectDiagram object`, `componentDiagram
usecase`, `activityDiagram diamond`, `sequenceDiagram participant`,
`jsonDiagram node`, `wbsDiagram node`, `chenEerDiagram chenEntity`,
`nwdiagDiagram server`, and `ganttDiagram task` have different native paths.
Generic `root` properties can override legacy `skinparam` behavior in families
without a matching selector. A global `title` selector also matches some actor
style signatures. Scope document titles to `document title`.

Use an opaque categorical fill, exact black/white font paint, and zero
decorative line thickness for each body. A repeated object kind reuses its
assigned role; allocate additional semantic categories with `solid_style` from
the palette helper. Use a neutral container surface distinct from its children
so nested deployment nodes remain visible without adding outlines.

Preserve semantic strokes explicitly: actors, class compartments, component
symbols, cylinders, queue curves, packet field boundaries, timing traces,
grammar rails, Chen weak/multivalued/derived/identifying notation, axes,
lifelines, and link glyphs. A zero-width outline must not erase those details.

The official [PlantUML style documentation](https://plantuml.com/style) explains
family scopes and selector precedence. Validate each change against actual
native output; accepting a style property is not proof that a primitive uses it.

## Finished delivery

`scripts/native_styles.py` runs on newly rendered native SVG before palette
normalization. It restores the grammar viewport's separate white canvas,
maps native ArchiMate layer fills to exact solid role colors,
removes hardcoded filled railroad-token and Salt-button outlines, and removes
default Gantt task contours. It restores missing internal geometry separately
from body contours and selects black or white from the actual painted backing
of each native text label. Exterior participant labels use the canvas; they do
not inherit the dark cylinder's text color.

A native timing state label can extend beyond its filled terminal shape.
When its text crosses incompatible backings, add a small opaque surface in the
same assigned body color immediately behind that whole label, with no outline.
Tag it `label-surface` and report `labelSurfaceCount`. Keep the label coordinates,
state polygon, trace, event times, and timeline endpoints unchanged. This is
label backing, not an extension of a measured duration. Pad only the outer
display frame if it ends before that label surface; keep the measured time axis
and every event/state endpoint unchanged. Fail if it cannot fit the existing
viewport; preserve explicit source styling.

The finisher keeps geometry, native labels, source relationships, and explicit
authored presentation. Source styling is recorded as `explicit-source`; its
outlines remain authoritative. Explicit source `FontColor` is also preserved.
Do not label such a deliberate source override as a default solid-body pass.
Comments, quoted labels, title text, and layout-only properties do not disable
the default style finish. Media preservation recognizes image/sprite syntax,
including scaled sprite references; an ordinary word such as Sprite in a title
still uses the finished SVG-to-PNG path.

`scripts/arrow_contrast.py` then checks native link groups, sequence messages,
activity and grammar tracks, JSON/YAML ports, mindmap/WBS branches, and Gantt
dependencies. Require at least 3:1 on each crossed painted surface for shafts
and complete heads. Keep hollow symbols hollow. If no allowed paint contrasts
with every backing, move the route or label into a clear gutter in the source
and rerender. Do not hide the failure by removing a semantic symbol.

For SVG-capable diagrams, PNG derives from this finished SVG, including
PNG-only requests. Source-media preservation and native mathematical notation
keep their narrower delivery paths. Never claim that raster palette
quantization alone establishes native style correctness.

The report records `native_style` version, delivery mode, and checked body/text
counts. SVG exposes `data-native-style`, `data-source-style`, and diagnostic
role attributes. The report validator requires the current version and
recomputes tagged body outlines, text backings, and native connector contrast.
Supplement those checks with rendered inspection of all meaningful primitives;
an annotation is diagnostic evidence, not an independent visual review.

## Raster-only Ditaa

For Ditaa PNG, `scripts/ditaa_styles.py` adds temporary native `cRGB` seed tags
only in free interior whitespace and disables shadows. It maps source-backed
fill regions to exact palette roles, removes their external decorative
contours, and selects black/white labels and internal glyph strokes. Connector
portions inside a dark node use its readable foreground; external shafts and
heads keep their native drawing. The original ASCII source is unchanged.

Automatic Ditaa styling supports disjoint `+---+` / `| |` boxes with an optional
`{io}`, `{s}`, or `{d}` glyph, four free interior cells for a color tag, and
native `scale=` from 0.1 through 10. Keep native colors as uppercase three-digit
`cRGB`; six-digit tags corrupt native labels. Nested/divided/shared boxes,
sloped borders, tabs, unsupported glyphs, unmatched raster geometry, and
category overflow fail explicitly before a style pass. Add space or simplify
the ASCII drawing according to the error, preserving labels and links.

The Kroki Ditaa route receives `no-shadows` and scale through HTTP query options
because it strips PlantUML wrappers. The [Kroki option
contract](https://docs.kroki.io/kroki/setup/diagram-options/) and [HTTP
usage](https://docs.kroki.io/kroki/setup/usage/) document this separate mechanism.

## Refreshing embedded themes

`--write-themed` writes source copies with bounded renderer-owned theme blocks.
Rerendering those copies replaces that block with the selected current theme,
including a change from Colorset 1 to Colorset 2. Later authored overrides stay
after the block. The renderer also recognizes the earlier bundled theme block
format. It never uses an arbitrary comment containing the skill name as a
reason to skip theme application.

## Maintenance checks

Run the native-style, arrow, raster, and coverage test scripts. Include negative
controls that corrupt an actual body outline, text paint, or connector paint.
Render all available frozen families in both palettes, inspect native and
finished geometry, and validate exact coverage reports. Inspect SVG and PNG at
readable size before publishing the gallery. Keep fixtures out of normal
isolated runtime payloads.

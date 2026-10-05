---
name: svg-brief-design
description: "Creates original editable SVG illustrations, ornaments, emblems, and decorative diagrams from short text briefs, with deliberate composition, line hierarchy, and negative space. Use for designing new vector artwork; not for tracing images, converting raster assets, or building interactive visualizations."
---

# SVG Brief Design

Create an original editable drawing from the user's short brief. Preserve its
subject, relationships, palette, proportions, background and exact output path.
Use procedural scaffolds for repeated geometry, then make the drawing specific
through its silhouette and details. The bundled scripts contain original
mathematical constructions, not stored artwork or recovered reference paths.

First make a compact checklist of the brief's subject, occupied proportions,
required features and regions that must stay empty. Preserve those relationships
before adding style or detail. An opening divided by lines is not an empty
opening; a decorative title does not replace a requested identifier or code.
For flowing frames, open mechanical forms, printed diagrams or compact labels,
read [purpose and construction](references/construction-decisions.md) before
choosing geometry. Use its original orbit base when an annular construction fits.

## Build a useful base

Choose the proportions of the occupied drawing before its surrounding canvas.
Identify what must be recognizable, which parts connect, and any exact text.
Leave unspecified details open; do not silently treat a reference's count,
layout or ornament as a requirement.

Use [the scaffold recipe guide](references/scaffold-recipes.md) when a regular
construction fits: radial blades, wireframe spheres, oscillations, connected
flows, text panels or pinnate foliage. Generate a small JSON recipe and SVG:

```text
python <skill-root>/scripts/scaffold.py init <kind> --recipe design.json --output artwork.svg
```

For a simple ordered stage flow with consecutive arrows, use `init flow` as
the first construction step. Edit its recipe with the exact labels, direction
and requested canvas, then `build` again; its content-sized nodes and attached
arrows prevent spacious default cards or hidden tips. Use custom geometry for
branching or other relationships the ordered scaffold does not represent.

Edit the recipe for the actual brief before treating the base as a deliverable.
Replace example labels, choose appropriate counts and proportions, and remove
unrequested content. For several bases, use `composition` with separate boxes
and inspect their clearance. Regenerate after parameter or detail changes:

```text
python <skill-root>/scripts/scaffold.py build design.json --output artwork.svg
```

For an irregular subject, create your own geometry directly or use `blank` with
original detail primitives. Do not force a face, vehicle or scientific optical
diagram into a radial badge, generic flow or sine wave. A base is useful only
when its construction matches the requested object. Keep generated files
outside the read-only skill directory and honor the requested delivery path.

## Decide the visual grammar

Use `colorset1` by default. Select `colorset2` for an explicit multicolor
request or necessary semantic color distinctions. Read exact allowed tokens
from `assets/palettes/colorsets.json`; apply one selected contract to every
stroke, fill, text color, background, annotation and exported preview. Record
`data-colorset` on the SVG root. Keep transparency as transparency and use
opacity separately from exact lowercase six-digit paint tokens. The scaffold
stores `style.colorset` in its editable recipe and rejects off-palette main,
underlay and nested detail paint. Use `init --colorset colorset2` when needed;
for an existing recipe change `style.colorset` and every affected paint together.

- Identify the subject, its recognizable features, the intended mood, and the
  dominant arrangement. Keep those decisions compact; do not expand a short
  request into an elaborate fictional specification.
- Choose a suitable aspect ratio before drawing. A long strip should remain
  long, a radial symbol should read as radial, and a portrait should not become
  a generic badge merely because a border is easy to construct.
- Start with a solid silhouette with cutouts. Choose open line drawing when
  requested or when the line itself conveys the subject, or use a deliberate
  mixture. Use the same curve character, corner
  language, and weight hierarchy throughout.
- Treat empty areas as designed shapes. Leave breathing room around the focal
  feature and between neighboring parts; added detail must improve recognition.

## Construct the drawing

Build the outer proportions and the largest internal divisions first. Add the
features that identify the subject, then secondary detail. Keep the dominant
shape readable at a small size before spending effort on decoration.

For line art, use a clear principal stroke and a quieter detail stroke. Avoid
stacking almost identical outlines: they create accidental dark seams and make
otherwise simple artwork look nervous. Keep intersections intentional and
curves smooth across joined segments.

For filled artwork, design separated masses and real interior openings. Several
overlapping black polygons can erase the very facial features, joints, facets,
or channels that should make the subject legible. Check which areas remain
connected after overlap. Use compound paths or masks for transparent cutouts;
white paint is not transparency.

Use symmetry when the request supports it, but keep meaningful asymmetry.
Generate repeated geometry from one consistent construction rather than
independently guessing every matching part. Match visual rhythm, not an
arbitrary target number of elements.

For decorative diagrams, make the intended relationships readable: connected
axes, coherent curves, distinct annotations, and unambiguous endpoints. Keep
letters and symbols subordinate to the drawing. Do not invent numerical claims
or label decorative codes as machine-readable without implementing them.

For connected explanatory diagrams, use the smallest readable occupied layout
by default. Size nodes from their labels, shorten routes and remove unused
canvas space while preserving visible arrowheads, identifiable source/target
ports, separated edges and text clearance. Start with 6 px vertical and 10 px
horizontal inset around final measured text; do not stretch nodes to fill a
fixed canvas. Read the connected-diagram procedure
in [purpose and construction](references/construction-decisions.md). Preserve
an explicit canvas and the negative space that describes an illustration;
do not compress quantitative graphs or shrink labels to make a layout fit.

## Check the artifact

Honor the exact requested path and delivery format. Keep an SVG self-contained
with a meaningful viewBox and editable vector elements. Include only the
requested background and resources, with authored paint inside the selected
colorset. Match requested color roles to its exact tokens.

With execution tools, render the generated SVG and open the preview. Use the
bundled renderer as the documented entry point; do not guess a rendering
library's function names or keyword arguments. Use `uv` to provision the pinned
dependencies and invoke the helper directly; avoid a bare-Python dependency
probe that can fail in a clean workspace:

```text
uv run --script <skill-root>/scripts/render_svg.py artwork.svg --output preview.png
```

Use bare `python` only when the helper's declared dependencies are already
known to be installed and `uv` is unavailable.

Inspect at intended size and as a thumbnail: subject identity, negative space,
stroke hierarchy, annotation clearance and arrow attachment. Check every exact
label and requested relationship. A valid render or an edge warning is not a
semantic verdict. Correct the largest visible issue and render again after
editing. The renderer reports its font limitation; use `--font-dir` when exact
repeatability matters. With writing-only tools, reason about geometry and
stacking without claiming a rendered review.

Keep the deliverable focused. Do not add a title, border, texture, caption,
shadow, or extra object unless it serves the brief. Prefer removing a weak
decoration over covering a compositional problem with complexity.

For adapting a base, consult [detail editing](references/detail-editing.md).
For path and fill questions, consult [SVG mechanics](references/svg-mechanics.md).
When reference SVGs are supplied, extract general construction principles and
invent fresh geometry for the current brief. Do not import their paths, trace
their contours, encode the source artwork, or store distinctive designs in this
bundle. Deliver the requested SVG; include its recipe or preview only when
useful or requested.

## Solid fill priority

Use opaque, single-token filled marks without decorative borders first. Read
`solidSequence` and `textOnFill` from `assets/palettes/colorsets.json`. Reuse a
fill for the same semantic role; when roles must be distinct, exhaust every
usable distinct token in the preferred sequence, excluding the actual canvas,
before creating outline or tint combinations. Soft tokens occur late. For text
on a fill, use exactly black or white with the larger WCAG contrast computed
from the actual background; composite opacity before evaluating translucent
backgrounds. Do not infer text color from a hue name.

Keep connectors, axes, signal traces, open line art, physical geometry and
explicit source-fidelity modes. A stroke that depicts a relationship or is the
geometry itself is meaningful. Reserve decorative outlines for a documented
palette overflow or an explicit requested style; mark SVG overflow treatments
with `data-outline-tier="overflow"`. A transient keyboard focus ring remains an
interaction affordance. Use position, whitespace and direct labels for ordinary
selection and grouping.

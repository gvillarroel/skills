# Scaffold recipes

`scripts/scaffold.py` runs on Python 3.11+ without dependencies. It builds SVG
from a small recipe instead of requiring the agent to calculate every repeated
coordinate. It never reads a reference SVG. The defaults are construction
examples, not answers to the user's brief.

## Commands and shared fields

```text
python <skill-root>/scripts/scaffold.py init globe --recipe design.json --output artwork.svg
python <skill-root>/scripts/scaffold.py build design.json --output artwork.svg
```

`init` requires new paths. `build` replaces the specified SVG while keeping the
recipe. Always edit the recipe for the brief before delivery. `blank` begins
empty and needs original detail primitives before it can render visibly.
`composition` also begins empty; add its items before rendering.

Every recipe has `version: 1`, `kind`, `canvas`, `style`, `parameters`, `underlay`
and `details`. Coordinates are SVG user units. `canvas` supplies `width`,
`height` and `margin`; `style` supplies `stroke` and a hex `color`. The output is
transparent and uses editable SVG elements with stable IDs. It does not embed
images, fonts or remote resources. Keep margins larger than stroke width.

## Choose and adapt a construction

| Kind | Appropriate base | Parameters and editing decisions |
| --- | --- | --- |
| `radial` | Angular rotary symbol or open segmented disk | `count` (3–48), `inner_ratio` (.08–.8), `twist` (-.85–.85 of one angular pitch), `gap` (.02–.5 of a pitch), `rotation` in degrees. Select a count from the brief or a deliberate open choice. A larger inner ratio increases the opening. Twist controls handedness. Each blade is an independent original quadrilateral. |
| `globe` | Wireframe sphere without geographic features | `meridians` (1–24), `parallels` (0–24), `tilt` (-70–70 degrees). Curves are projected spherical circles, including back-facing wireframe portions. It is not a geographic map. |
| `wave` | Illustrative oscillation with shared axes | `cycles` (.1–30), `amplitude` (.05–.9 of available half-height), `phase` in degrees, `damping` (0–10), optional `x_label`, `y_label`. Zero lies on the horizontal axis. The function is a sampled sine with an optional exponential envelope; do not use it for a different mathematical relationship. |
| `flow` | Ordered stages with attached arrows | `labels` (2–12 strings), `direction` (`horizontal` or `vertical`), `rounding`, optional `font_size` (14–36, default 18). Nodes use conservative text bounds and 10/6-unit padding instead of stretching across the canvas. Adjacent box ports and arrow endpoints are computed together; change direction or enlarge the canvas if content cannot fit at the chosen font. |
| `panel` | Label or information block with stable text hierarchy | `title`, `header`, `rows` (up to 12 strings), optional `border`. Replace `Heading` and `Detail`. It does not invent serials, codes, icons, barcodes or a black header strip. Add such elements only when the brief supports them. |
| `frond` | A curved pinnate botanical stem | `pairs` (3–32), `bend` (-.65–.65), `spread` (.1–.48), `rotation` in degrees. The rotated curve control hull fits inside its box. This is a generic botanical construction, not a species identification. |
| `composition` | Several related bases in one drawing | `items` is a list of `id`, `kind`, `box: [x, y, width, height]`, and optional `parameters`. Each box stays inside canvas margins. Nested compositions are unsupported. IDs are namespaced automatically. Choose boxes from the brief's layout, not a reference's coordinates. |
| `blank` | A subject needing its own geometry | Start with an appropriate canvas and supply original `underlay` and `details` primitives, or author SVG directly. |

The script rejects nonfinite values, invalid ranges, undersized text and duplicate
IDs. This catches mechanical problems, not all overlaps, scientific errors or
poor proportions. A legal parameter choice can still look wrong.

## Original detail primitives

`underlay` draws before the generated structure; `details` draws after it. Each
entry has `tag`, `attrs`, optional `text`, and optional `children`. Supported
tags are `g`, `path`, `rect`, `circle`, `ellipse`, `line`, `polyline`, `polygon`,
and `text`. Attribute names use normal SVG spelling, such as `stroke-width`.
Groups can apply a shared `transform`. Text must use `fill` and `stroke: none`
when the inherited outline style is inappropriate.

For instance, a caller may add a newly designed circular feature using its own
center and radius, or a text element containing an exact requested caption.
For complex contours, construct fresh paths from semantic parts. Do not paste
a path from a purchased reference into the recipe. Attribute URLs and embedded
resources are rejected. Create more advanced self-contained masks directly in
the generated SVG when needed, following the mechanics reference.

## Revision choices

Edit parameters for global proportions, rhythm and density. Edit `details` for
subject-specific parts. Directly edit generated SVG for advanced path shaping,
compound cutouts or masks. If editing SVG directly, preserve it as the source
of those edits: a later recipe build replaces the SVG and does not merge hand
changes. Never discard a finished contour by blindly regenerating.

Do not keep a base merely because it was cheap to generate. If its dominant
silhouette is wrong, change the construction before polishing small marks.

For multiple fronds or other bases, use `composition` instead of copying SVG
source and guessing transform offsets. Leave clearance between their boxes
unless overlap is intentional. The fit keeps each supported construction in
its box, but it cannot judge whether two boxes should overlap or whether their
combination reads as the requested ornament. Detail primitives can still cross
the canvas; inspect the final preview.

## Orbit: tapered bands with a reserved opening

Use `orbit` for an annular frame, not a central emblem. Parameters: `count`
(3–24), `inner_ratio` (.2–.9), `coverage` (.25–1.8 times the angular spacing),
`taper` (.5–3), `rotation` in degrees and `direction` (1 or -1). Each closed
band uses an original polar construction; the declared inner disk stays empty.
The radius drifts sinusoidally and the width rises from and returns to zero.
No stored path or artwork is used. Inspect overlaps after changing coverage: a
protected center does not guarantee resolved junctions or a finished ornament.
Keep the recipe for proportion edits; edit original vector paths for local
finishing, and do not regenerate over those direct edits.

## Direction and actual backings

Flow tips and shafts leave a 4-unit gutter at both box ports. Their open chevron geometry remains editable line art and uses independent opaque direction ink; light node colors never determine arrow paint. The builder chooses black or white against the canvas, then checks sampled shafts and head vertices against ordinary local rect/circle/ellipse fills including ancestor opacity. `canvas.background` optionally emits an exact palette fill; `style.arrow_color` requests an allowed direction token and fails below 3:1 against the checked backings.

Complex filled paths and transformed underlays require browser inspection and are marked `data-arrow-audit="inspect-custom-underlay-in-browser"`. Inspect actual alpha composites and any foreground details crossing a shaft or tip. Reposition the gutter or scope direction paint to the local backing when one paint cannot reach 3:1; avoid decorative rims, halos or node borders. Transparent SVGs assume white presentation unless an explicit canvas backing is supplied.

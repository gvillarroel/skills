# Editable Asset Contract

## Contents

- [Importable SVG](#importable-svg)
- [Plan and assembly](#plan-and-assembly)
- [Custom scene, 3D and raster media](#custom-scene-3d-and-raster-media)

Use `scripts/import_assets.py` to assemble compatible specialist SVGs into the
bundled scene. This preserves per-shape dependency, geometry, palette and seek
audits. It does not import an opaque image and assume that image is synchronized.

## Importable SVG

- Author at native target dimensions with a positive `viewBox="0 0 width height"`.
  Placement is a translation in the assigned view's coordinates. The asset's
  viewBox must fit that view. Flatten scale, rotation, skew and matrices into
  geometry; nested translations are supported.
- Include a nonempty direct SVG `<title>` for source accessibility. This metadata
  does not become a visible film headline.
- Use `g`, `path`, `circle`, `ellipse`, `rect`, `line`, `polygon`, `polyline` and
  single-line `text`. Give every rendered shape a unique lowercase hyphen-case ID.
  IDs become `<asset-id>-<shape-id>` in the assembled brief.
- Use exact active-palette hex tokens for fill/stroke, or `none`. Optional
  `data-fill-role`/`data-stroke-role` must agree with visible paint. Inherited
  presentation attributes and translated groups are resolved during import.
  Use numeric geometry/font sizes/stroke widths; no CSS or percentage units.
- Flatten tspans, CSS, symbols/use, clipping, masks, gradients and filters before
  this route. Scripts, images, animation elements, external references, DTDs and
  event handlers are rejected. Use the custom route below when they are essential.
- Bind literal vector geometry through numeric attributes. Use path-local geometry
  centered at its pivot plus `translateX`, `translateY`, `rotation` for rotating
  parts. The imported file has a visible representative state.

For a travelling object, keep its parts inside one named SVG `g`, draw it fully
inside the view at its initial pose, and bind a **relative** group offset:

```json
{"car":{"offset":[{"mul":["distance",6]},0]}}
```

This preserves each shape's authored coordinates and initial translation while
adding the same motion to body, windows, wheels and labels. Give the road/ruler
the same zero position and pixels-per-unit scale. Budget room for the entire
object at both domain extremes. Do not replace a path's initial `translateX`
with distance alone: that discards its initial pose and can clip the rear of the
object. Group bindings accept `offset` only; bind wheel rotation/fills individually.

Compute the travel scale before binding: `pixelsPerUnit = availableTravel /
maximumAccumulatedQuantity`. For a view 600 px wide, an object whose initial
right edge is 220 px, and 20 px right padding, available travel is 360 px.
A maximum accumulated distance of 48 m permits 7.5 px/m. Derive that maximum
from the control domain and duration (6 m/s × 8 s), rather than the nominal
movie's final distance. Match the ruler to the same scale and the object's
chosen measurement anchor. Check the entire moving silhouette at zero and max.

Browser bounds findings identify the sampled time, actual input override,
measured edges and allowed view region. Fix that reported counterfactual, not
only the nominal last frame. Preserve the declared control domain; correct scale,
pose or layout rather than hiding evidence with a clamp.

Write JSON/SVG as UTF-8. On Windows use an explicit UTF-8 writer and plain ASCII
unit separators if shell encoding is uncertain. Correct any replacement
characters or mangled sequences reported by preflight before rendering.

## Plan and assembly

For a standalone hand-authored asset, start with the bundled scaffold command.
It derives native dimensions from the chosen view and writes a correctly
plan-relative source path. Then edit the SVG and its bindings; the empty scaffold
cannot pass import. If a plan already names this exact missing SVG in the selected
view, it preserves that plan and creates only the SVG. Existing SVGs are never
replaced. Inspect the scaffold report's `ok` and `svg` before reading the file.

```text
uv run --script <skill-root>/scripts/import_assets.py --scaffold --brief scene.json --view mechanism --output assets/mechanism.svg --plan asset-plan.json --report scaffold.json
```

Replace `mechanism` with the actual view ID. Use view-local geometry, without
adding the view's canvas offset. The importer/renderer applies that offset once.
Serialize nested JSON expressions with a structured writer such as Python
`json.dumps`, rather than manually balancing a long inline object. Validate the
plan with the importer; its authoring report explains malformed JSON without a
failed raw parser command. Use parsed JSON edits for bindings, not substring edits.

A rotating wheel should use a path whose local origin is its pivot. For example,
place a stationary rim and translated spoke path in the SVG, then bind only the
path's `rotation` (degrees):

```xml
<circle id="wheel-rim" cx="180" cy="100" r="34" fill="none" stroke="#9e1b32" stroke-width="4"/>
<path id="wheel" d="M-34 0 H34 M0 -34 V34 M-24 -24 L24 24 M-24 24 L24 -24" transform="translate(180 100)" fill="none" stroke="#9e1b32" stroke-width="3"/>
```

The path retains `translateX:180, translateY:100` after import. A binding such as
`{"attrs":{"rotation":{"mul":["rate",18]}}}` rotates about that actual hub.
Lines accept endpoint bindings, not `rotation`; use sine/cosine endpoints for a
rotating line, or author a path at its known pivot. Do not guess a pivot from a
bounding box. Put nonnumeric text `anchor` on the mark, outside numeric `attrs`.

Example plan; replace the paths and IDs with the actual authored SVG:

Asset `path` is relative to the plan JSON's directory. If the plan is
`deliverables/asset-plan.json`, set path to the relative filename assets/mechanism.svg, not
`deliverables/assets/mechanism.svg`. CLI input/output paths remain relative to
the command workspace. This distinction prevents duplicated directory prefixes.

```json
{
  "schemaVersion": 1,
  "assets": [{
    "id": "inlet",
    "path": "assets/inlet.svg",
    "producer": "svg-brief-design",
    "purpose": "Make the valve opening and connected flow path recognizable.",
    "view": "mechanism",
    "placement": [0, 0],
    "moments": ["establish", "open-valve", "hold"],
    "ports": {"supply": [40, 180], "outlet": [480, 180]},
    "bindings": {
      "wheel": {"attrs": {"rotation": {"mul": ["rate", 18]}}},
      "readout": {"value": "rate", "digits": 1, "unit": "L/s"}
    }
  }]
}
```

`moments` names declared event IDs or `establish`/`hold`. `ports` records native
SVG coordinates inside its viewBox; check actual connected geometry against
these anchors. `bindings` names local SVG shape/group IDs and may override `attrs`,
`entity`, `value`, `digits`, `unit`, `text` or `textRole`, or add a relative
`offset:[dx-expression,dy-expression]`. Bound numeric attributes
replace imported coordinates; provide final view-local expressions including
placement when needed. Other geometry remains literal and editable. For a
readout, use a `text` shape. Do not bind a chart curve by changing an unrelated
box: use a plot or an explicitly audited custom path evaluator.

Assets are inserted in plan order behind the base brief's marks. Put an asset's
structure, fill and outline in the correct internal drawing order, then put
additional dynamic overlays in the base brief. Reassemble from that unexpanded
brief after any asset edit; do not import into an already assembled brief.

When the mechanism has a moving part or changing amount, bind that actual imported
shape's numeric geometry. Do not draw the actuator in a static SVG and animate
an unrelated native box. At least one mechanism hook should change geometry
between event states; charts remain a complementary quantitative representation.

Run from the task workspace, not from the skill directory, one gate at a time:

```text
uv run --script <skill-root>/scripts/import_assets.py --brief scene.json --plan asset-plan.json --output assembled.json --report import.json
uv run --script <skill-root>/scripts/explainer.py build --brief assembled.json --project project --report build.json
```

Inspect the import report's `ok`. Expected unsupported-shape, palette, hook,
collision and model findings exit zero without replacing the output brief.
A missing SVG named in the plan is an authoring finding with a path-resolution
diagnosis; unreadable input files are infrastructure failures. The assembled brief records
producer, purpose, moments, ports, hooks, source SHA-256 and each imported mark ID.
Build copies the original SVGs into `<project>/assets/source/` and the manifest keeps their
project-relative paths. A source changed after assembly requires reimport.

The expansion is deterministic. All imported animated attributes enter the same
state evaluator and browser audit as native marks. Audit the assembled scene at
source-domain extremes, including zero and reverse seeks; a correct static SVG
does not establish correctness of its bindings.

## Custom scene, 3D and raster media

Preserve local specialist source, licensing, source hashes, native bounds and
state contract. Keep one HyperFrames root and one paused registered GSAP clock.
Expose deterministic `renderAt(t)`/`seek(t)` that reconstructs every asset from
canonical state and the absolute clock. Drive animation clips, particles and
camera motion explicitly; do not accumulate frame-to-frame state or start a
second autonomous loop.

Extend validation to the actual graphics: projected ports, mesh positions,
numerical values, canvas bounds, sampled frames, repeatability, reverse seek and
real preview controls. The bundled SVG audit covers only registered SVG marks;
report custom coverage accurately. Retain the native HyperFrames and full media
checks. Prefer the import route when unsupported effects have no explanatory job.

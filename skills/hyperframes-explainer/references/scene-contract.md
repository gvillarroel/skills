# Scene Contract, Version 1

Use the bundled `assets/templates/brief.json` for the file shape. It is an
illustrative starting mechanism, not a source of subject facts. All coordinates
are authored in the exact output canvas; view regions give local coordinates.

## Contents

- [Root](#root)
- [Initialize a rate/accumulation scene](#initialize-a-rateaccumulation-scene)
- [Expressions](#expressions)
- [Primitive vocabulary](#primitive-vocabulary)
- [Edit a generated brief](#edit-a-generated-brief)
- [Public runtime](#public-runtime)

## Root

- `schemaVersion`: 1; `id`: lowercase hyphen-case, at most 64 characters.
- `claim`: the causal relationship; `evidence`: supplied sources or an explicit
  illustrative/model statement. These stay in the manifest, outside the film.
- `output`: `width`, `height`, `fps`, `duration`, optional `audio` local file path.
- `palette`: `mode` (`colorset1` default or `colorset2`), `decision`, `reason`.
- `sources`: numeric source variables keyed by ID. Each has `value`, `domain`
  `[minimum, maximum]`, and `unit`. Reserve `time` for the sampled second.
- `derived`: quantities keyed by ID, each with `expr` and `unit`.
- `events`: `{id, at, duration, changes, cause}`. Change only declared sources.
  Ramps are linear; zero duration is a discrete change. Do not overlap event
  windows that write the same source. One event may update several inputs atomically.
- `views`: `{id, question, region:[x,y,width,height], importance}`. Use one `main`
  mechanism and supporting views. Regions must fit the output. Distinct panels
  must not overlap; for a continuous scene, semantic groups may each use the
  exact full canvas `[0,0,width,height]`, with all geometry in canvas coordinates.
  This is a shared coordinate frame, not permission for colliding graphics:
  inspect actual marks, labels and object contacts in the browser and native audit.
- `marks`: primitive marks belonging to one view; each has `id`, `view`, `kind`,
  `attrs`, `fill`, optional `stroke`, and optional `entity`.
- `entities`: optional ID-to-role mapping. A repeated entity gets its paint from
  this mapping; avoid assigning a new color to the same subject in a second view.
- `invariants`: optional `{id, lhs, rhs, tolerance}` equalities checked over time.

## Initialize a rate/accumulation scene

For a controlled nonnegative input and an integral from zero, create the brief
before asking for an SVG scaffold. Run one command and inspect its `ok`:

```text
uv run --script <skill-root>/scripts/explainer.py init --brief scene.json --report init.json --width 960 --height 540 --fps 12 --duration 8 --initial 2 --maximum 5 --target 5 --at 2 --ramp 2 --source rate --source-unit L/s --quantity volume --quantity-unit L
```

Substitute the requested paths and facts. The flags name the output canvas,
initial input, legal maximum, new target and linear event's start/duration.
For speed/distance, change source/quantity names and units to `speed`, `m/s`,
`distance`, `m`. Add `--palette colorset2` only for an explicit second-palette
request; otherwise use colorset1. Do not silently retain illustrative values.

The initializer writes a valid landscape scene with `mechanism` and `history`
views, one `change-input` event, exact analytic accumulation, input/quantity
readouts and fixed-domain history axes. It derives the maximum history quantity
from maximum input × duration, fitting legal counterfactuals. It never replaces
an existing brief or edits the copied skill. Use the patch command or a structured
JSON writer for subsequent changes.

It leaves the mechanism empty: create the SVG scaffold next, draw recognizable
assets and bind their moving parts. This numerical layout is not a finished film.
Its model assumes no losses/output and starts accumulation at zero. Use a custom
brief for negative rates, reservoirs with outflow, balances, oscillations, other
models or portrait/small layouts. Preserve source facts and inspect assumptions.

## Expressions

A number is literal; a string names `time`, a source or a derived variable.
A one-key object applies one operation to an array of expressions:

`add`, `sub`, `mul`, `div`, `min`, `max`, `pow`, `clamp`, `abs`, `sqrt`, `sin`, `cos`, `mod`.

`sub` and `div` take two operands; `clamp` takes value/min/max; trigonometric inputs
are radians. Division by zero, negative square roots and non-finite results are
findings. Model the legal domain honestly; do not add an arbitrary denominator
epsilon to hide an undefined quantity.

`mod(value, positive-period)` takes two operands and returns a nonnegative phase.
Its period must stay positive throughout the legal domain. Use accumulated state
for a transport phase so changing a source rate cannot reset particle positions.

`{"integrate": ["rate", "time"]}` integrates a **source** rate from time zero
through its declared linear event ramps. It is analytic, deterministic and seek-safe.
Use it for actual accumulation; multiplying the current rate by total elapsed time
is incorrect when the rate changed.

Derived references are topologically resolved. Unknown names, cycles and arbitrary
code strings are rejected. Mark geometry can use the same expressions, but keep
physical quantities in their real units and perform pixel mapping in `attrs`.

## Primitive vocabulary

- `circle`: `cx`, `cy`, `r`.
- `ellipse`: `cx`, `cy`, `rx`, `ry` (nonnegative radii).
- `rect`: `x`, `y`, `width`, `height`; optional `rx`.
- `line`: `x1`, `y1`, `x2`, `y2`; optional `arrow: true` on the mark.
- `path`: literal SVG `d`; animate `translateX`, `translateY`, `rotation` in
  `attrs` or use circles/lines for variable geometry. No arbitrary HTML/SVG injection.
- `text`: `x`, `y`, optional `fontSize`, `anchor` (`start`, `middle`, `end`);
  `text` is a short direct label, optional `value` expression, `digits`, `unit`,
  `textRole` (`label`, `annotation`, `context`). `anchor` is on the mark, not in
  `attrs`. A valid legacy `attrs.anchor` is normalized to the mark-level field
  when no mark-level anchor exists. Other attributes stay numeric. Values and
  units stay attached.
- `plot`: `attrs` gives `x`, `y`, `width`, `height`; `xValue`, `yValue` expressions;
  `xDomain`, `yDomain` fixed numerical bounds. Optional `samples` (default 100).
  Shows only the sampled history up to the current second and a current point.
  Add concise axis/unit labels as separate text marks; no automatic legend/title.

`fill`/`stroke` name roles from the active palette; `none` is permitted. An `entity`
overrides the semantic mark fill (or the stroke of a line/path/plot) using the
registry. `strokeWidth`, `dash` and `opacity` are optional mark-level properties.
`linecap` and `linejoin` default to `round`. Imported assets use the same marks;
see [asset-contract.md](asset-contract.md) for asset plans and provenance.
Use the exact role keys: `background`, `surface`, `ink`, `inkDark`, `primary`,
`primaryDark`, `accent`, `accentSoft`, `muted`, `line`, `quiet`. Colorset2 also
provides `secondary`, `secondaryDark`, `tertiary`, `positive`, `attention`, `special`.
For example, structural outlines use `line`, essential text uses `ink`, red
quantities use `primary`, and colorset2 blue quantities use `secondary`.
Choose these keys before writing the first brief; do not invent a `structure` role.

Every numerical source must affect a visible encoding. At least one event must
affect marks in two distinct views. The preflight checks this dependency closure;
also inspect whether the chosen encodings answer genuinely different questions.

Keep default text labels short. One optional context label is enough for this
style. The preflight flags long labels/prose but never rewrites supplied text.

## Edit a generated brief

Write a small patch JSON with group objects keyed by existing IDs or quantity
names. Example: `{"marks":{"rate-label":{"attrs":{"y":190}}},"sources":{"rate":{"value":3}}}`.
Run `uv run --script <skill-root>/scripts/explainer.py patch --brief <project-owned-brief.json>
--patch <patch.json> --report <patch-report.json>`. Inspect `ok` and `applied`.
The patcher preserves untouched fields, replaces expression operators atomically,
rejects unknown/renamed IDs and leaves the brief unchanged on validation findings.
Then regenerate the owned project with `build --refresh` and rerun its audit.
Write a fresh brief for adding/removing marks or changing the schema; no textual
replacement of repeated `x`, `y`, `fontSize` or serialized JSON fragments is needed.

## Public runtime

The generated `window.explainer` exposes:

- `stateAt(seconds, overrides={})`: pure canonical source/derived state.
- `snapshot(seconds, overrides={})`: state plus resolved visible mark attributes.
- `seek(seconds)`: seek the paused GSAP clock and return a plain snapshot.
- `setInputs(values)`: preview-only input changes, propagated through every view.
- `clearInputs()`: restore the scripted input events.
- `renderAt(seconds)`: deterministic frame rendering.

Preview parameter overrides apply a constant replacement input across the sampled
history; they compare an alternative trajectory rather than splice an unrecorded
pointer gesture into the scripted movie. Restore the scripted inputs before capture.

The interactive preview puts transport/parameter controls outside the filmed
stage. New capture sessions start with no preview overrides. Do not couple
rendered state to pointer position, page-load timing or previous frames.

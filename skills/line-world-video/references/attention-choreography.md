# Attention and data points

Use `line-world-attention` when one guide hands attention between related
figures and releases points carrying a quantity or category. Keep the guide
primary red `#9e1b32` in either palette. Its size expresses emphasis, while
the other marks represent data. Never imply that a larger guide is a larger
measurement.

## Editable input

The builder fills these defaults in `story.json`:

```json
{
  "attention": {
    "guideColor": "#9e1b32",
    "baseRadius": 9,
    "travelRadius": 6,
    "focusRadius": 22,
    "emitRadius": 32,
    "pointRadius": 4.5,
    "emissionSeconds": 0.34,
    "flightSeconds": 0.55,
    "unitPerPoint": null,
    "categoryColors": {},
    "emissionViews": ["network", "circle-pack", "donut"]
  }
}
```

Require travel ≤ base ≤ focus ≤ emission radius ≤ 64 logical pixels. The guide
contracts in travel, grows on arrival, expands during emission and returns to
its base size. Radii remain readable at the 1920×1080 logical frame. For a
different composition, tune them against labels rather than scaling blindly.

In the atlas, quantity points transfer each entity's `after` value from its
first figure to its linked network, circle pack or donut. Automatic units use
a 1/2/5 step with at most about sixteen full points per entity. An explicit
`unitPerPoint` may produce at most 64. Show `1 dot = …` with the correct unit.
A partial final point has proportional area, so the encoded quantities sum
exactly to the source. Zero emits no points. Do not turn an arbitrary transfer
matrix into a claim of conserved mass.

For simultaneous category identities, select `palette: "colorset2"`, record
`paletteReason`, and supply `attention.categoryColors` using existing row IDs:
for example, `intake: #007298`, `review: #45842a`, `build: #652f6c`,
`release: #e77204`. Use distinct exact colors. The guide stays primary red.
The mapping also applies to the atlas's observation marks. A spatial sample
is one observation, not one day; state that separate unit in its legend.
Keep object names or shapes available alongside color. With no mapping,
quantity points are neutral and the film remains colorset1.

## Implementation and verification

The builder copies `assets/runtime/attention.js` into generated projects.
Every dedicated plugin producer also ships this standalone runtime. Load it
before scene code and use `LineWorldAttention.settings`, `radius`, `tokens`,
`sample` and `clearPort` as needed. All are pure state functions; pass seconds
from the parent clock. Cache measured focus ports after local fonts load.
Reserve enough clearance for the maximum guide radius and its white keyline.

Run `build`, then the bundled browser audit. Inspect emission midpoints,
landed quantities, arrival and travel, a repeated backward seek, and the
final overview. Confirm primary red, visible size variation, stable colors,
exact per-entity quantity sums and safe label clearance. Do not animate with
independent timers. The linked starter varies guide size but leaves quantity
emissions to its adapted data views; the atlas implements all three receivers.

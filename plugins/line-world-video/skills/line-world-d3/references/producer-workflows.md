# D3 video operations

Use real D3 for the geometry that needs it. The copied runtime includes original
builders/exporters and their assets, but a synchronized SVG group is the normal
video output. Do not invoke a full dashboard or logo studio to get a simple mark.

## Bounded table/comparison starter

Provide JSON with `records: [{"id":"alpha","label":"Alpha","value":12}, ...]`,
`unit:"items"` and `duration:8`. The starter supports 2–8 nonnegative values,
fixed 1920×1080 logical dimensions, complete column divisions and pure seeking.
Use its supported builder for this form; keep generated files outside the skill.

```text
uv run --script <skill-root>/scripts/video_chart.py build --data data.json --project film
uv run --script <skill-root>/scripts/video_chart.py export --project film --svg film/asset.svg --screenshot review/frame.png --receipt review/receipt.json
```

The export checks real browser bounds, pairwise labels, values, a common zero
scale and repeated seeking. Adapt the generated project for other forms rather
than asking the source bundle to hold task files.

## Data and geometry

Use `d3.select(...).selectAll(...).data(records, d => d.id).join(...)` with stable
IDs. Use `scaleLinear` for measured positions and lengths, `scaleBand` for
discrete slots, `line`/`area` for ordered observations, `hierarchy` plus `tree`,
`pack`, `treemap` or `partition` for nested records. Use `Delaunay.from` for
neighbor/cell views and `geoPath` with a declared projection for geographic data.

Seed `randomLcg`; stop and pre-tick force simulations. Preserve one canonical
dataset, equal units and shared domains across linked representations. Keep
source record IDs on marks and expose sensible focus ports above labels.

The runtime inventory is available in `assets/vendor/` and the exact palette
in `assets/palettes/colorsets.json`. Locate actual filenames before wiring the
project; copy only the runtime files needed by the output. Keep all output
outside the copied skill bundle.

## Time contract

Build settled geometry once. Let `renderAt(t)` update reveal, selected paint,
markers or camera state from project timing. Use the parent's pure clock when
embedded. Keep controls in a separate preview. Export an SVG from the rendered
state after flattening computed presentation and local font dependencies.

## Useful pairings

Use table + bars/dumbbells for precise comparison, timeline + lines for events
and change, hierarchy + treemap/pack for membership and magnitude, Sankey +
matrix for direction and exact transfers. Do not add all possible chart types
to a production scene merely because the library supports them.

## Checks

Measure text and native bounds after fitting. Check zero values, shared scales,
missing data, direct labels, focus linkage, meaningful transitions and repeated
seeking. Check exact palette on actual computed paint, not source declarations.

Primary API references: [D3 API](https://d3js.org/api),
[hierarchy](https://d3js.org/d3-hierarchy),
[Delaunay](https://d3js.org/d3-delaunay).

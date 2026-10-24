# Chart recipes

## Contents

- [Named columns and scatter](#named-columns-and-continuous-or-categorical-scatter)
- [Time series and gaps](#time-series-gaps-and-mixed-marks)
- [Categories and a matrix](#categories-and-a-matrix)
- [Facets](#facets)
- [Visible notes](#visible-notes)
- [Style and layout](#style-and-layout-decisions)

These examples target XY 0.0.8. Use `inspect.signature(xy.<factory>)` in the
project's environment for an unfamiliar option. All examples construct `Chart`
objects; export or display the resulting variable with the host workflow.

## Named columns and continuous or categorical scatter

```python
import xy

rows = {
    "distance_km": [2, 4, 7, 11, 15, 18],
    "minutes": [8, 15, 22, 37, 44, 58],
    "route": ["urban", "urban", "rural", "urban", "rural", "rural"],
    "deliveries": [12, 20, 9, 25, 11, 16],
}
chart = xy.scatter_chart(
    xy.scatter("distance_km", "minutes", color="route", size="deliveries",
               size_range=(6, 16), opacity=0.8),
    xy.x_axis(label="Distance (km)"),
    xy.y_axis(label="Travel time (min)"),
    xy.legend(title="Route"),
    xy.tooltip(fields=["distance_km", "minutes", "route", "deliveries"]),
    data=rows, title="Delivery routes", width=960, height=500,
)
```

A numeric `color=` channel uses a continuous map (`colormap="viridis"`);
a categorical channel uses discrete colors. A CSS color such as `"red"`
means a constant. If a column's name is itself a valid CSS color, bind the
actual column array to avoid that ambiguity. Geometry columns must align;
boolean and complex coordinates are rejected. NumPy arrays, sequences, dict
tables, and pandas column lookup work without a special conversion to JSON.
For JSON-style row records, retain the original records and build a column
mapping first: `columns = {key: [row[key] for row in records] for key in records[0]}`.
Pass `data=columns`; a list of dictionaries does not implement named column lookup.

## Time series, gaps, and mixed marks

```python
from datetime import date, timedelta
import numpy as np
import xy

days = [date(2026, 1, 1) + timedelta(days=i) for i in range(6)]
measured = [18.2, 19.1, np.nan, 17.8, 20.4, 21.0]
target = [19.0] * len(days)
chart = xy.chart(
    xy.line(days, measured, name="Measured", color="#2563eb", width=2.5),
    xy.scatter(days, measured, name="Observations", color="#2563eb", size=7),
    xy.line(days, target, name="Target", color="#525252", dash="dashed"),
    xy.x_axis(label="Date", format="%b %d"),
    xy.y_axis(label="Temperature (°C)"),
    xy.legend(), title="Daily temperature", width=960, height=480,
)
```

Keep missing values in their original positions. XY breaks line runs at NaN;
points with missing geometry are omitted without renumbering canonical rows.
Sort genuinely ordered line data together with every associated channel when
necessary; do not independently sort x and y. Multiple line series are separate
marks with constant colors and names, rather than one scatter-style color column.

## Categories and a matrix

```python
bars = xy.bar_chart(
    xy.bar(["North", "South", "West"], [42, 58, 35], color="#2563eb"),
    xy.x_axis(label="Region"), xy.y_axis(label="Orders"),
    title="Orders by region", width=800, height=420,
)

matrix = xy.heatmap_chart(
    xy.heatmap([[1, 4, 2], [3, 2, 5]], colormap="viridis"),
    xy.x_axis(label="Column"), xy.y_axis(label="Row"),
    xy.colorbar(title="Count"), title="Counts", width=800, height=420,
)
```

Use a rectangular z matrix for a heatmap. When supplying explicit x/y grid
coordinates, verify the release's grid shape/center contract before exporting.
Use a bar series' documented `mode`/`series` options only after checking the
installed signature; do not infer stacking from several unrelated marks.

## Facets

```python
panels = xy.facet_chart(
    xy.scatter("distance_km", "minutes", color="#2563eb"),
    xy.x_axis(label="Distance (km)"), xy.y_axis(label="Travel time (min)"),
    data=rows, by="route", cols=2,
    width=900, height=320, share_x=True, share_y=True,
)
panels.to_html("routes.html")
```

`width` is the total grid width; `height` is per-panel height. Both are
positive pixel integers. Use compatible
row-aligned channels so subsetting by facet remains valid. `FacetChart` has
display/export/memory methods but no `append`, `pick`, or `select_range` methods.

## Visible notes

Use `xy.text(x, y, value, ...)` as a chart child for a short data-coordinate
annotation. Include its location in the authored axis domains and inspect the
export so the note does not overlap data or disappear outside the plot:

```python
note = xy.text(10, 60, "Synthetic observations", anchor="middle",
               color="#525252")
```

For a note outside the plot, place ordinary text in the host page or a small
HTML wrapper around the exported chart. Keep the chart's self-contained assets
and CSP intact. Preserve arbitrary source identifiers in the editable source;
do not bind them to `symbol` or `key` merely to force them into a tooltip. Verify
which extra fields the installed renderer actually retains before promising
per-row metadata in hover output.

## Style and layout decisions

Use [the colorset workflow](colorsets.md), defaulting to colorset1 and selecting
colorset2 for an explicit multicolor request. The examples above illustrate API
shape; replace their literal colors with the selected helper's semantic roles
and replace interpolated numeric maps with exact bins for palette-controlled
deliverables. Preserve explicit user style and meaningful units. Give interactive containers an
explicit height; `height="100%"` needs a parent height. XY's DOM chrome can use
CSS, while WebGL/canvas marks support a smaller validated style surface. Prefer
the public mark, axis, theme, legend, and tooltip arguments before injecting
CSS. Use explicit export dimensions to avoid responsive fallback sizes.

For other chart families (polar, Sankey, uncertainty, violin, contours), inspect
the installed public signature and the matching release's official chart guide.
Do not treat a roadmap entry as an implemented API.

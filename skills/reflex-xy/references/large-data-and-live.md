# Large data and live charts

## Representation and exactness

XY keeps canonical numeric columns as float64 in Python, then sends typed binary
representations to its client. Long ordered lines can use M4 decimation; dense
Cartesian scatters can use native-computed density grids. The browser renders
these with WebGL. Ingest, validation, and binning still depend on source size;
do not repeat an upstream benchmark as a measurement of the user's machine.

```python
import numpy as np
import xy

rng = np.random.default_rng(17)
x = rng.normal(size=300_000)
y = 0.6 * x + rng.normal(scale=0.5, size=x.size)
chart = xy.scatter_chart(
    xy.scatter(x, y, color=np.hypot(x, y), colormap="viridis", density=None),
    xy.x_axis(label="x"), xy.y_axis(label="y"),
    title="Correlated sample", width=1000, height=560,
)
report = chart.memory_report()  # builds/validates canonical data
```

`density=None` selects automatically; `True` requests aggregation and `False`
forces markers. Keep the automatic mode unless the task needs otherwise. Avoid
creating a huge dataset just to demonstrate a small task. Thresholds are policy,
not a stable API contract. A density bin or sampled marker does not represent
every exact input row. Live hosts can request refined source windows; standalone
HTML has only the representation/sample that was embedded at export time.

`memory_report()` includes `backend`, `canonical_bytes`, column lengths, null
counts, and ingest copies. Use it to explain actual allocations. A null-free
float64 Arrow array can be zero-copy, but conversions, multiple chunks, and
missing materialization may copy. Arrow is an optional separately installed input
dependency; it is not universally zero-copy.

Polar geometry has a different contract: no Cartesian density/M4 shortcut,
restricted interactions, and a point-count ceiling. Check the release-specific
polar guide before promising large polar traces or box selection. Grid inputs
and point traces have different limits.

## Selection and canonical rows

```python
small = xy.scatter_chart(xy.scatter([0, 1, 2, 3], [1, 3, 2, 4]))
row = small.pick(0, 1)
selection = small.select_range(0.5, 2.5, 0, 5, trace_id=0)
```

`pick(trace_id, index)` maps a shipped vertex index to a source row when such a
mapping exists. Invalid indices return `None`; do not assume a density-cell
index is a row ID. Core notebook callbacks are `on_hover`, `on_click`,
`on_brush`, `on_select`, and `on_view_change`. `on_select` receives an
`xy.Selection`, while Reflex exposes a separate JSON-safe event envelope.
Use the host's documented selection resolver for bounded/truncated projections.

Range selection targets scatter source rows; a line-only chart returns an empty
selection. `chart.select(range={"x0": 0, "x1": 2, "y0": 1, "y1": 5})`
uses scalar rectangle bounds, while `set_view()` uses per-axis ranges. Widget
construction or queuing a view/selection command does not establish that its
frontend has delivered callbacks; test that separately in a running host.

## Append and streaming

```python
live = xy.line_chart(xy.line([0.0, 1.0], [10.0, 12.0]))
live.append(0, [2.0, 3.0], [11.0, 14.0])
live.to_html("latest-snapshot.html")
```

Append targets existing scatter/line traces, not chart structure. Batches must
have equal nonzero coordinate lengths. Ordered line x values must continue
ascending; per-point color/size channels need matching tails. Keep a sensible
retention strategy for an indefinitely growing process and inspect memory.
An already-written HTML file remains unchanged. To send future updates, keep
the widget/kernel or Reflex backend alive and use its documented adapter path.

## Linked views

Set a common `link_group="measurements"` and `link_axes=("x",)` on related
charts mounted in the same live page. This coordinates viewports. Cross-filtering
data still requires a callback or application state; shared link names alone
do not filter rows or connect separate standalone browser documents.

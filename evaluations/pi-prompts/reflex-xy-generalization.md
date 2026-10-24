Make a small daily trend chart with Python `xy==0.0.8` for fictional reservoir
measurements. These records are the full source data; keep the dates, order, and
missing value exactly as supplied:

```json
[
  {"day": "2026-03-01", "level_m": 17.3},
  {"day": "2026-03-02", "level_m": 17.5},
  {"day": "2026-03-03", "level_m": 17.1},
  {"day": "2026-03-04", "level_m": null},
  {"day": "2026-03-05", "level_m": 16.9},
  {"day": "2026-03-06", "level_m": 17.2},
  {"day": "2026-03-07", "level_m": 17.7},
  {"day": "2026-03-08", "level_m": 17.6},
  {"day": "2026-03-09", "level_m": 18.0}
]
```

Use a date-aware x axis, a line and visible point marks. Title the chart
`Reservoir level in March`, label the axes `Observation date` and `Level (m)`,
and visibly explain that this is synthetic data and March 4 has no measurement.
Do not invent or impute a point for that day. Preserve the original records in
the reproducible source even if the plot requires a separate filtered view.

Deliver exact paths `app.py`, `results/trend.html`, and `results/trend.png`.
The HTML must be an interactive local export that opens offline without a
server. The PNG must be a readable native xy export. `app.py` must have PEP 723
metadata declaring `xy==0.0.8`, contain the exact source records, and recreate
both exports with `uv run --script app.py` from the workspace root. Use xy for
the chart and its exports. Verify the exports and briefly explain how you handled
the missing observation in your final response.

Treat `skills/reflex-xy/` as read-only and write generated files elsewhere in
this workspace. Do not inspect other skills, parent directories, acceptance
examples, or repository documentation. Registry access for declared dependencies
is allowed; the HTML must work offline. Do not publish or deploy anything.

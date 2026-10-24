Create a Python xy scatter chart for a fictional air-sensor experiment. I need a
portable interactive HTML file that opens locally without a server or network
connection, plus an SVG for a report. Use `xy==0.0.8` from reflex-dev/xy.

Use these exact observations, keeping all column names, row order, identifiers,
and values in the reproducible source:

```json
[
  {"sample": "A-01", "humidity_pct": 31, "response_ms": 128, "room": "Atrium", "signal": 7},
  {"sample": "A-02", "humidity_pct": 44, "response_ms": 116, "room": "Atrium", "signal": 11},
  {"sample": "A-03", "humidity_pct": 58, "response_ms": 105, "room": "Atrium", "signal": 9},
  {"sample": "A-04", "humidity_pct": 69, "response_ms": 94, "room": "Atrium", "signal": 14},
  {"sample": "L-01", "humidity_pct": 34, "response_ms": 144, "room": "Lab", "signal": 8},
  {"sample": "L-02", "humidity_pct": 47, "response_ms": 137, "room": "Lab", "signal": 13},
  {"sample": "L-03", "humidity_pct": 61, "response_ms": 122, "room": "Lab", "signal": 10},
  {"sample": "L-04", "humidity_pct": 73, "response_ms": 113, "room": "Lab", "signal": 16},
  {"sample": "S-01", "humidity_pct": 29, "response_ms": 157, "room": "Store", "signal": 6},
  {"sample": "S-02", "humidity_pct": 43, "response_ms": 148, "room": "Store", "signal": 12},
  {"sample": "S-03", "humidity_pct": 57, "response_ms": 132, "room": "Store", "signal": 15},
  {"sample": "S-04", "humidity_pct": 68, "response_ms": 121, "room": "Store", "signal": 9}
]
```

Use named columns for humidity on x, response time on y, and a consistent category
color for each room. Label the chart `Sensor response by humidity`, the x axis
`Humidity (%)`, and the y axis `Response (ms)`. Show the three room names in a
legend. If the installed API supports a straightforward size channel, use signal
strength for point size; otherwise keep a readable constant size. Include a small
visible synthetic-data note. The chart should support xy's native local inspection
interaction, such as tooltips or selection, and export with readable axes.

Deliver exact paths `app.py`, `results/cloud.html`, and `results/cloud.svg`.
`app.py` must be a rerunnable Python script with PEP 723 metadata declaring
`xy==0.0.8`, contain the exact source observations, and regenerate both exports
when run from the workspace root with `uv run --script app.py`. Use xy for the
chart and its exports. Check both generated files and report actual limitations
briefly in your final response.

Treat all of `skills/reflex-xy/` as read-only. Keep generated files outside that
directory. Do not inspect other skills, parent directories, acceptance examples,
or repository documentation. Registry access for declared dependencies is allowed;
the delivered HTML itself must work offline. Do not publish or deploy anything.

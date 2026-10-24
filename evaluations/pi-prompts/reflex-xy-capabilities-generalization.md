Build a pair of Python XY charts for a fictional sensor calibration review.
Use `xy==0.0.8` from reflex-dev/xy. Show the central estimate and its supplied
lower/upper measurement range at each actual observation time. Keep all six
observations in their original order and preserve every identifier and value
in the editable source:

```json
[
  {"sample": "C-01", "elapsed_h": 0, "center": 12.0, "lower": 10.5, "upper": 13.7},
  {"sample": "C-02", "elapsed_h": 2, "center": 13.2, "lower": 11.8, "upper": 14.0},
  {"sample": "C-03", "elapsed_h": 5, "center": 11.4, "lower": 9.2, "upper": 13.1},
  {"sample": "C-04", "elapsed_h": 8, "center": 15.0, "lower": 13.9, "upper": 16.8},
  {"sample": "C-05", "elapsed_h": 12, "center": 14.1, "lower": 12.3, "upper": 15.2},
  {"sample": "C-06", "elapsed_h": 18, "center": 16.3, "lower": 14.4, "upper": 18.5}
]
```

Use canonical colorset1 for the first treatment and colorset2 for the second.
Make the treatments visibly distinct while preserving the same observations,
scales, dimensions, and interval meaning. Use opaque canonical fills and
meaningful line colors. Avoid unnecessary legends; if a legend is useful,
place it in empty space so it covers no data.

Title each chart `Sensor interval estimates`, label x `Elapsed time (h)` and
y `Response (units)`, and include a small visible `Fictional observations` note.
These ranges are supplied measurement boundaries, not estimated statistical
confidence intervals. Use a truthful supported XY representation of them.

Deliver exact paths `app.py`, `notes.md`, `results/cs1/interval.html`,
`results/cs1/interval.svg`, `results/cs2/interval.html`, and
`results/cs2/interval.svg`. The HTML files must open locally without a network,
server, or Python installation and preserve useful native local inspection.
Use XY for the charts and exports. The SVGs must be valid native exports with
readable axes and all supplied interval boundaries. `app.py` must contain PEP
723 metadata declaring `xy==0.0.8` and regenerate all four chart exports when
run from the workspace root with `uv run --script app.py`.

Briefly explain the visual encoding, the fact that these are fictional supplied
ranges, and the actual checks and offline interaction limits in `notes.md`.
Do not claim that an emailed HTML snapshot can execute Python callbacks.

Treat `skills/reflex-xy/` as read-only. Keep generated files outside that
directory. Do not inspect other skills, parent directories, acceptance examples,
or repository documentation. Registry access for declared dependencies is
allowed; the delivered HTML itself must work offline. Do not publish or deploy.

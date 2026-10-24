Create two readable Python XY charts of fictional supplied measurement ranges.
Use `xy==0.0.8` from reflex-dev/xy and its native vertical error-bar mark with
visible horizontal end caps and a central point at each observation. Preserve
every record in this order in the editable source:

```json
[
  {"sample": "E-01", "position": 1, "center": 12.0, "lower": 10.5, "upper": 13.7},
  {"sample": "E-02", "position": 2, "center": 13.2, "lower": 11.8, "upper": 14.0},
  {"sample": "E-03", "position": 3, "center": 11.4, "lower": 9.2, "upper": 13.1},
  {"sample": "E-04", "position": 4, "center": 15.0, "lower": 13.9, "upper": 16.8},
  {"sample": "E-05", "position": 5, "center": 14.1, "lower": 12.3, "upper": 15.2},
  {"sample": "E-06", "position": 6, "center": 16.3, "lower": 14.4, "upper": 18.5}
]
```

Show each range at its actual position, from its lower to its upper value.
These are supplied boundaries, not statistical confidence intervals. Make the
caps compact and clearly shorter than the gap between neighboring observations
so each range remains visually distinct. Choose the cap size using the actual
units of the native API. All centers, range ends, and caps must fit inside the
plot with comfortable margins. Avoid an unnecessary legend.

Use canonical colorset1 for one chart and colorset2 for the other. Make their
measurement ink visibly different while preserving identical geometry, axis
domains, labels, and dimensions. Use opaque canonical paints and readable
chart chrome. Title both charts `Capped measurement ranges`, label x
`Observation position` and y `Response (units)`, and include the visible note
`Fictional supplied ranges`.

Deliver these exact paths: `app.py`, `notes.md`,
`results/cs1/errorbars.html`, `results/cs1/errorbars.svg`,
`results/cs2/errorbars.html`, and `results/cs2/errorbars.svg`.
Use XY's native chart exports. The SVG files must be valid XML with readable
axes, six centers, and six correctly capped ranges. The HTML files must open
locally without a network, server, or Python installation. `app.py` must include
PEP 723 metadata declaring `xy==0.0.8` and recreate all four chart exports when
run from the workspace root with `uv run --script app.py`.

In `notes.md`, briefly explain the encoding, the cap-size units and chosen
value, the fictional nature of the supplied ranges, and only checks actually
performed. State offline interaction limits honestly; do not claim that a
saved HTML snapshot can execute Python callbacks. No added callbacks or custom
interactions are required.

Treat `skills/reflex-xy/` as read-only. Keep generated files outside that
directory. Do not inspect other skills, parent directories, acceptance examples,
or repository documentation. Registry access for declared dependencies is
allowed; the delivered HTML itself must work offline. Do not publish or deploy.

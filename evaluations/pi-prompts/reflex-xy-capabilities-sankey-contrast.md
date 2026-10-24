Create two Python XY Sankey charts for a fictional review process using
`xy==0.0.8` from reflex-dev/xy. Preserve these five node identities and five
weighted links exactly, including their order, in the editable source:

```json
{
  "nodes": ["Intake", "Review", "Direct", "Accepted", "Returned"],
  "links": [
    {"source": "Intake", "target": "Review", "value": 70},
    {"source": "Intake", "target": "Direct", "value": 30},
    {"source": "Review", "target": "Accepted", "value": 55},
    {"source": "Review", "target": "Returned", "value": 15},
    {"source": "Direct", "target": "Accepted", "value": 30}
  ]
}
```

Use the native XY Sankey family. Make link widths proportional to their supplied
values. Keep all five native node-name labels visible and readable over the
actual node and ribbon fills beneath them, with no clipping or overlap that
hides a label. Use dark canonical fills for the nodes and ribbons in each
treatment and choose supported label styling that maintains clear contrast.
Do not remove the labels to avoid the contrast problem. Keep the fixed diagram
framed when opened; no callbacks or custom interactions are required.

Use canonical colorset1 for the first chart and canonical colorset2 for the
second. Make the treatments visibly distinct while keeping identical data,
layout, node order, labels, and dimensions. Opaque authored fills must come from
the chosen set. Title both charts `Fictional review flow` and show a visible
`Synthetic flow totals` note. Do not add an unnecessary legend.

Deliver exact paths `app.py`, `notes.md`, `results/cs1/flows.html`,
`results/cs1/flows.svg`, `results/cs2/flows.html`, and
`results/cs2/flows.svg`. Use XY's native HTML and SVG exports. The SVGs must be
valid XML with all five native labels readable. The HTML files must open locally
without a network, server, or Python installation. Include PEP 723 metadata
declaring `xy==0.0.8` in `app.py`; running `uv run --script app.py` from the
workspace root must recreate all four chart exports.

In `notes.md`, briefly explain the flow totals and fictional data, the actual
label contrast strategy, whether interpolated ribbon shades remain exact
palette entries, checks actually performed, and offline interaction limits.
Do not claim a saved HTML snapshot can execute Python callbacks. Responsive
width is welcome but is not required for this focused contrast task.

Treat `skills/reflex-xy/` as read-only. Keep generated files outside that
directory. Do not inspect other skills, parent directories, acceptance examples,
or repository documentation. Registry access for declared dependencies is
allowed; the delivered HTML itself must work offline. Do not publish or deploy.

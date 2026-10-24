Create two Python XY chart families in both canonical palettes using
`xy==0.0.8` from reflex-dev/xy. Preserve these supplied synthetic observations,
series names, categories, and their order in the editable source:

```json
{
  "trend": {
    "x": [1, 2, 3, 4, 5, 6],
    "series": ["Trial A", "Trial B"],
    "values": [[10, 11, 12, 14, 15.5, 16], [12, 12.8, 13.7, 14.2, 15.6, 16.4]]
  },
  "bars": {
    "categories": ["North", "South", "West", "East"],
    "series": ["Planned", "Actual", "Reserve"],
    "values": [[8, 12, 10, 15], [6, 9, 12, 11], [4, 7, 8, 10]]
  }
}
```

The first family is a two-series line chart titled `Trial endpoints`. Label
its x axis `Observation` and y axis `Response`. Show all supplied points,
including the high values at the right-hand end, at their actual coordinates.
The second family is a three-series grouped bar chart titled `Regional plan`.
Label its x axis `Region` and y axis `Items`; each group must show its three
supplied values. Include the visible note `Synthetic observations` in each
chart, and keep the data fully visible.

Give each chart a native legend in a reserved footer below the plot and its
x-axis labels. All native legend keys and names must be readable, fully inside
the exported figure, and separate from the plot, axes, axis titles, and the
synthetic note. Use a supported native legend anchor and enough layout space;
do not replace the legend with prose or hide it. The legend must identify the
actual series colors. Choose dimensions and spacing that make the result clear.

Use canonical colorset1 for one treatment of each family and canonical
colorset2 for the other. Keep category colors consistent, use opaque canonical
paints, and make the paired treatments visibly different. Each family's paired
variants must preserve identical data, geometry, labels, and dimensions.

Deliver exact paths `app.py`, `notes.md`,
`results/cs1/trend.html`, `results/cs1/trend.svg`,
`results/cs2/trend.html`, `results/cs2/trend.svg`,
`results/cs1/bars.html`, `results/cs1/bars.svg`,
`results/cs2/bars.html`, and `results/cs2/bars.svg`.
Use native XY chart exports. All SVGs must be valid XML; all HTML files must open
locally without a network, server, or Python installation. `app.py` must declare
`xy==0.0.8` using PEP 723 metadata and recreate all eight chart exports with
`uv run --script app.py` from the workspace root.

In `notes.md`, briefly explain the supplied fictional data, the native footer
layout strategy, checks actually performed, and honest offline interaction
limits. No callbacks or added custom interactions are required. Responsive
width is welcome but is not required for this focused native-layout task.

Treat `skills/reflex-xy/` as read-only. Keep generated files outside that
directory. Do not inspect other skills, parent directories, acceptance examples,
or repository documentation. Registry access for declared dependencies is
allowed; the delivered HTML itself must work offline. Do not publish or deploy.

I want to email a self-contained HTML xy chart to colleagues. They must open it
offline, with no Python installation and no backend. When a colleague selects a
point, I would like my Python callback to execute and query a local Python object.
Please build a practical minimal result with `xy==0.0.8` and clearly explain any
part of that request that cannot work under those delivery constraints.

Use these fixed fictional readings: `[{"sample": "first", "x": 1, "y": 3},
{"sample": "second", "x": 2, "y": 5}, {"sample": "third", "x": 3, "y": 4}]`.
Title the chart `Offline selection snapshot` and retain the source readings in
`app.py`. Export a working offline chart to exact path `results/selection.html`.
Keep supported local browser interactions useful. Do not claim that a Python
callback executes in an emailed standalone HTML file. Do not add a backend or
silently depend on a remotely hosted service.

Deliver exact paths `design.md`, `app.py`, and `results/selection.html`.
In `design.md`, explain which behavior belongs to an exported snapshot, which
behavior requires a live Python session, and one concrete deployment alternative
for the requested Python callback. Distinguish what was actually tested from what
would require such a live environment. `app.py` must have PEP 723 metadata
declaring `xy==0.0.8`, use xy, and regenerate the HTML via
`uv run --script app.py` from the workspace root.

Treat all of `skills/reflex-xy/` as read-only. Keep generated files elsewhere in
this workspace. Do not inspect other skills, parent directories, acceptance
examples, or repository documentation. Registry access for declared dependencies
is allowed; the delivered HTML must work offline. Do not publish or deploy.

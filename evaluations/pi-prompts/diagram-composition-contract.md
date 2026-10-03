Use the loaded diagram-composition skill. Its directory skills/diagram-composition/
is read-only. Keep every generated file within this workspace. No network access
or other skills are needed.

Create a small schematic with three regions: a circular neighborhood of three
peers around a shared library at upper left, a two-row comparison of read/write
access at lower left, and a tall synthesis of the shared library inside a service
boundary at right. This is illustrative data, not a claim about any real product.
Use a 1000 by 700 canvas displayed at 1000px, minimum essential text 14px. Each
panel must be an actual diagram, not a paragraph in a rectangle. Link the first
two regions to the relevant object in the synthesis. Keep labels short.

Create out/plan.json, the panel sources under out/panels/, out/figure.svg,
out/report.json, out/audit.json, and out/preview.png. Use this exact command once
the plan and panel SVGs exist:

```sh
uv run --script skills/diagram-composition/scripts/compose_diagram.py compose --spec out/plan.json --output out/figure.svg --report out/report.json
```

Run the bundled browser audit at the intended size. Repair actual readability or
geometry findings, and preserve the exact output paths. Write out/review.md with
the viewer questions, form choices, and what you verified. Do not install tools
or inspect anything outside this workspace; use the available normal runtime.

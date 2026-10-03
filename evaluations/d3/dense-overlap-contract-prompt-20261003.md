Create a self-contained colorset1 D3 visualization of dense task overlap using the bundled saturated task-overlap recipe.

Read `skills/d3/references/patterns/task-overlap-dense.md`. Generate the deterministic input in this workspace with this exact command:

```text
uv run --script skills/d3/scripts/layout_task_overlap_labels.py --output task-overlap-layouts.js
```

Use the generated saturated layout's nine scope circles, 100 task dots, 100 labels, existing geometry, memberships, leader endpoints, and IDs. The scope regions must use their saturated colorset1 tokens with semantic fill opacity 0.28 so overlapping sets remain visible. Keep the task dots and external label faces opaque and borderless. Choose each label's black or white paint by its actual composited backing, including scope labels over transparent intersections. Do not make the entire SVG or ordinary labels translucent.

Deliver exactly `task-overlap-layouts.js`, `dense-overlap.html`, and `dense-overlap.svg` in the workspace root. The HTML must work offline, and the SVG must be a portable, fully rendered export of its settled scene with accessible title and description. Include a Replay control in the HTML; both repeated replay and reduced motion must finish with all nine regions, 100 dots, and 100 labels visible. Inspect the chart and source-over intersections at its native scale.

Follow the skill's applicable colorset finalization, active-palette, self-contained, and rendered output checks. Treat `skills/d3/` as read-only. Keep generated files and verification scratch inside this workspace, outside that bundle. Do not read acceptance fixtures, other skills, repository data, or parent directories.

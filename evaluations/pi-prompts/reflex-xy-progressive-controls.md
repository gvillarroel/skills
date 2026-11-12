Design a compact interface around an XY chart using the loaded skill. The host
shows the existing chart and lets users save an image. Users should find the
initial screen simple, then discover palette choices and other export formats.

Create `interaction-plan.json` and `index.html` in the workspace. No Python
chart rendering or server is needed for this focused interface task. Use this
already-rendered chart as the content; preserve its SVG geometry:

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 220" role="img" aria-label="Measured response rises across three observations"><rect width="400" height="220" fill="#f7f7f7"/><path d="M40 180 L190 110 L350 40" fill="none" stroke="#9e1b32" stroke-width="3"/></svg>
```

The plan JSON must have `default_colorset`, `initial_actions`, `secondary_actions`,
and `data_preservation` fields. In the HTML, show the chart and a working
primary save-SVG action. Keep other display/export choices reachable, and label
unimplemented formats honestly rather than creating dead links. Do not add a
server, external assets or a synthetic application shell. Use semantic controls
with keyboard behavior, retain the chart when options open/close and keep mobile
controls usable at a 390 CSS pixel viewport. Use only the requested workspace
for generated files and verification artifacts. Do not modify the copied skill.

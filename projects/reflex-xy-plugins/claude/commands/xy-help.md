---
description: Explain the XY chart plugin, its chart specification, and host boundaries
---

Explain the plugin's chart workflow using these facts:

- Start with the native chart preview and **Save image**. **More options** is
  collapsed initially and reveals palette, sample charts, rerendering, file
  actions and technical details only when requested. It can be opened and
  closed with the native button using a pointer or keyboard.
- The empty pane offers a clearly labeled sample action. Loading shows progress;
  errors keep a concise explanation visible and retain the last successful
  chart. Palette changes and rerendering use the displayed chart's data.
- **Save image** creates a unique PNG under the current project's
  `.xy-charts/exports/` folder and confirms success inside the pane. It preserves
  the original XY pixels and does not open another application. More options
  contains the saved path, folder action and optional HTML browser export.
- Native pane interactions, sample generation, palette changes, rerendering,
  saving and copying run locally without calling a model or submitting a turn.
  Asking Claude to design or explain a chart still uses the normal model.
- In More options, **Sample chart (replaces current data)** loads demonstration
  data. Use a specification or the model tool to chart real supplied data.
- `/xy-chart` renders a line demo and opens a chart pane. `/xy-chart colorset2 scatter`,
  `/xy-chart colorset1 bar`, and `/xy-chart sankey` choose other demos.
  Every new command, JSON file and `render_chart` call defaults to **Colorset 1**
  when it omits `colorset`, even after an earlier chart used Colorset 2.
  Colorset 2 requires `colorset2`, `"colorset":"colorset2"`, or an explicit
  choice in the pane. Pane controls can retain the palette explicitly selected
  for the chart being edited.
  The sample selector loads every preset listed by the bundled renderer contract;
  those names also work after `/xy-chart`.
- `/xy-chart @charts/request.json` reads a declarative JSON chart request inside
  the current project. A raw JSON object after `/xy-chart` also works.
  The adapter rejects lexical parent and absolute paths; filesystem symlinks
  still follow the host's normal rules. This path check is not an OS sandbox.
- The `render_chart` tool accepts a `spec` object. Use a preset request for a
  common chart or ChartSpec v1 for whitelisted XY marks and components. Read
  `runtime/contract.json` in this plugin for the exact contract and permitted APIs.
- The bundled `reflex-xy` skill supplies the Python API and colorset guidance.
  Use its compact references when a request needs data analysis or a chart family
  beyond the sample presets.
- Artifacts are generated under `.xy-charts/` inside the current project. The
  result includes interactive HTML, SVG, PNG, editable Python, and chart JSON.
- The pane shows an SVG image in Claude Code Desktop and VS Code, or PNG in a
  capable terminal. This is the actual native XY export, not a replacement chart
  drawn in JavaScript. Full XY browser hover and zoom are available through the
  optional HTML export in More options; they are not claimed in the native Mod.
- Exported HTML is a snapshot. Python callbacks and future appended data require
  a live Python host. A Claude web/cloud session may run the skill or Python
  workflow when its environment supports them, but it does not render a native
  Mods pane. Do not claim that the regular claude.ai chat runs this local mod.
- `uv` and Python dependencies must be available where Claude Code executes.
  The first render may install the pinned XY environment. `uvExecutable` in
  plugin configuration can select an existing executable path.

Help the user create a valid specification with their actual data. Preserve its
meaning and label units. Do not fabricate measurements or replace the XY engine
with another chart library.

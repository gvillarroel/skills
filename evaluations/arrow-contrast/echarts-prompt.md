Use the ECharts animated SVG skill to create native directed charts in this
workspace. Read its entry point and arrow reference. Copy the bundled runtime
`assets/templates/echarts-colorsets.mjs` into exact `echarts-colorsets.mjs`.
Use ECharts 6.1.0 through normal npm tools in this workspace; install it if
needed. Do not read acceptance examples or alter the copied skill.
This is a fresh workspace: discover existing files before reading them.
Create your package, copied helper, render script and check outputs; do not
try to read generated files before creating them. For the fixed graph,
omit `coordinateSystem` or use native `view`; `layout: 'none'` does not mean
`coordinateSystem: null` or `coordinateSystem: 'none'`.
Keep the render loop and option assertions small and separate. Inspect solid
node styles on the prepared option, after preparation has run. Apply pixel
insetting only to Cartesian lines, not the fixed-coordinate graph. Compare
saved coordinate variables directly before and after insetting; report field
names must match the fields actually written into the JSON.

Create two static charts per palette, using `prepareColorsetOption`:

- A fixed-coordinate graph with two radius-30 solid nodes, inside labels,
  one native end arrow of size 16, and an initial `#cfcfcf` edge at opacity
  0.25. Include declared low-opacity emphasis and blur edge styles.
- Three two-point continuous Cartesian routes with native arrow heads,
  curveness 0.18, and radius-4 endpoint scatter marks. Start the arrow line
  paint at opacity 0.25. Lay out original coordinates, then use the public
  pixel inset helper with a 3 px gap plus the endpoint radius. Preserve
  original coordinates for resizing and semantic endpoint identity.

Use a white canvas and 640 by 360 output. Render with ECharts SVG SSR;
do not draw replacement chart geometry. Create exact
`graph-cs1.static.svg`, `graph-cs2.static.svg`,
`routes-cs1.static.svg`, `routes-cs2.static.svg`.
Animate each to its corresponding `.animated.svg` with the bundled script,
using graph or lines profiles, and validate each static/animated pair to exact
`graph-cs1.validation.json`, `graph-cs2.validation.json`,
`routes-cs1.validation.json`, `routes-cs2.validation.json`.
Retain native head paths, transforms and static final paint.

Write exact `option-checks.json` with `passed: true` only after assertions
verify: both palettes produce contrast-safe shaft/head line styles against
the white canvas; graph nodes remain solid and borderless; declared edge
focus/blur styles remain readable; input route coordinates are unchanged by
insetting; repeated layout/inset from the original option gives identical
coordinates; and a directed default markLine with pale low-opacity input
gets corrected. Include final prepared styles and original/inset coordinates.
Keep helper behavior and rendered local contrast limitations explicit.

Use only current workspace files, the copied skill, and normal installed
tools. Do not inspect parent harness files, run manifests, ancestor git
state, sibling skills, repository documentation or the original repository.
Write generated artifacts in the workspace root. All requested names are
exact output paths.

The palette API names are `colorset1` and `colorset2`, but file names use
`cs1` and `cs2`. Map them explicitly. Do not emit filenames containing
`colorset1` or `colorset2`. Check every requested filename exists before
finishing the task.

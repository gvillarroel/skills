Use Slidev ECharts to create a reusable directed-route Vue component.
Read the copied skill entry point, its arrow contrast reference and the
relevant integration/lines recipe. Copy the bundled runtime helper to exact
`echarts-colorsets.mjs` in this workspace. Do not read acceptance examples
or modify the copied skill. This targeted task does not require installing
a full deck.

Create exact `ArrowRoutes.vue`. Use ECharts with SVGRenderer, initialize
after mount into a real sized container, and prepare colorset options before
setting them. Accept a stable click/step prop and construct three continuous
two-point Cartesian routes with native arrow heads, radius-4 target scatter
marks, curveness 0.18 and an initial pale arrow line at opacity 0.25. Choose
colorset2. Keep input coordinates as the semantic endpoint data. Lay out
the original option, then use the public pixel-inset helper with radius plus
a 3 px gap; reapply the original layout and recompute after step changes
and ResizeObserver events. Dispose the chart and observer on unmount.
Import the copied helper by its workspace-relative path. Do not hand-draw
replacement arrow geometry or add borders to filled marks.

Create exact `option-checks.json` using only Node built-ins and the public
helper API. Assert `passed: true` only when both palettes correct pale
low-opacity graph/lines/markLine arrows, preserve borderless solid nodes,
and correct declared low-opacity focus/blur states. Include final styles.
Test pixel-inset nonmutation and repeated-call equality with a focused mock
of the initialized chart's public getOption/convertToPixel/convertFromPixel
methods; use continuous axes and an explicit pixel scale. Record original
and inset coordinates. Confirm unsupported categorical geometry is rejected.
Preparation styles its option in place; construct fresh nested state objects
for each palette and inspect each baseline before calling it. Keep that
operation distinct from the nonmutating pixel inset.

Create exact `integration.md` explaining the component lifecycle, semantic
endpoint contract, resize/click recomputation, native target/tangent
inspection, actual local 3:1 shaft/head contrast, reduced-motion/resting
states and the limits of a canvas-only option check. Do not claim that this
targeted JSON task itself measured browser pixels.

Use only current workspace resources and the copied skill. Do not inspect
parent harness files, run manifests, ancestor git state, sibling skills or
repository files. Keep all generated task files at the exact workspace paths
above. Keep the artifact-writing script focused on JSON and write Markdown
separately.

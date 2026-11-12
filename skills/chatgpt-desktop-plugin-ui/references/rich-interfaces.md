# Rich graphs, charts, and complex workspaces

Use this reference before authoring a graph, linked chart, dense table, or
multi-panel plugin view. Treat the recipes below as design decisions to verify,
not universal host capabilities or fixed node-count limits.

## Contents

- [Inspection task](#start-from-an-inspection-task)
- [Graphs](#graphs-without-a-hairball)
- [Charts](#charts-that-preserve-meaning)
- [State and recovery](#linked-state-and-recovery)
- [Pixel review](#review-pixels-and-alternatives)
- [ChatGPT Desktop choices](#chatgpt-desktop-choices)

## Start from an inspection task

Write the question first: for example, "Which dependency explains this service's
latency, and what changed over 24 hours?" Define stable entity/edge IDs, units,
timestamps/timezone, missing-value rules, data revision, and selection state.
Keep one authoritative model. Derive the graph, chart, table and inspector from
that model; an export must contain the same scope and values.

Use a focused workspace as the default: a compact summary, one active analysis
view, and a selected-entity inspector. Offer an overview or comparison when the
task needs simultaneous views. Compare both with the same data and viewport.
Put layout, comparison, display settings, and export behind a named disclosure.
Keep the main task action visible. Do not make every visualization a separate
dashboard card or hide a required recovery action in an overflow menu.

## Graphs without a hairball

1. Choose topology deliberately. Use a layered layout for a directed workflow,
   a tree for hierarchy, an adjacency matrix for dense pairwise relations, and
   a node-link diagram for a bounded neighborhood. Use a Sankey only when
   quantitative flows and their accounting are meaningful. Service call rates
   need not conserve flow: retries, fan-out and unlike units invalidate that
   interpretation.
2. Start with a selected entity and its direct neighborhood when the full
   graph would make labels unreadable. Show visible/total counts, direction,
   edge type, and aggregation rules. Let search reveal another entity and
   provide a clear return to the previous scope.
3. Keep IDs and layout stable across selection, filtering and refresh. Seed or
   precompute layouts; stop a force simulation after settling. Selection must
   not reshuffle an otherwise unchanged graph.
4. Distinguish selected, keyboard-focused, related and filtered-out states.
   Use a border/symbol/text label as well as color. Route edges behind nodes;
   verify arrowheads and labels against real node bounds. Never let a line
   imply a connection to an unrelated node it passes.
5. Provide search, explicit zoom/Fit controls and a relationship list. Keep
   ordinary page scrolling usable. Do not require precise dragging, wheel
   modifiers, hover or edge clicking for the core task. On a small surface,
   prefer a readable neighborhood/list over shrinking an entire map.
6. For a large graph, query a bounded neighborhood and summarize clusters
   with member/edge counts. Add Canvas/WebGL, a worker or virtualization only
   after measuring a bottleneck and checking that the host permits it. Preserve
   an accessible selection/list outside the raster layer. Never send an entire
   sensitive graph merely to make an inspector responsive.

## Charts that preserve meaning

- Use a line for ordered observations, bars/dots for categorical comparisons,
  a heatmap for a matrix, and small multiples for several related series.
  Avoid decorative 3D geometry and dual axes that obscure comparisons.
- Keep x/y data paired and sort only genuinely ordered data. Preserve missing
  values as gaps. State units, timezone, window, aggregation, denominator and
  whether data is synthetic. Distinguish an objective from observed values.
- Use a zero baseline for magnitude bars. Make the domain policy explicit for
  line charts; retain comparable domains across service/series switches unless
  a clearly named rescale action changes them. Mark clipping or log scales.
- Use exact palette roles and distinguish series with labels/dashes as well
  as color. Reduce ticks and reflow legends at narrow widths. Recompute the
  chart's dimensions/ticks instead of scaling readable labels into tiny text.
- Provide a concise finding plus exact values in a table or equivalent text.
  A title, tooltip or screenshot alone does not communicate a complex chart.
  Include source row IDs in exports when needed for traceability.
- Aggregate/downsample only with a stated method, raw count and retained
  extrema/uncertainty appropriate to the task. A smooth line must not invent
  observations. Measure point/label density on the actual surface.

## Linked state and recovery

Store selected ID, filters, active view, sort, comparison and data revision
separately. Keep selection through view changes. If a filter excludes it,
explain that explicitly rather than silently changing the inspector. Distinguish
global KPIs from filtered counts.

Represent loading, empty, error, stale and canceled states. Retain the last
valid snapshot and drafts on failure; offer a nearby retry. Guard asynchronous
updates with an epoch/request ID and revision. Test a canceled request that
actually finishes later: hiding the spinner does not prove stale-result safety.
Commit edits only after validating the current identity, authority and revision.
Read-only selection should remain local and deterministic.

Use real tab/button/select semantics where available; test focus retention after
redraw. A keyboard graph needs a bounded focus path and a list alternative.
Scope Escape to the focused transient surface and return focus to its trigger.
Respect reduced motion and the host's text/theme conventions. Use a real
dialog implementation if a drawer becomes modal; never trap focus in a
nonmodal inspector.

## Review pixels and alternatives

Capture the populated initial state, a meaningful selection, an empty filter,
an error/retry, and the narrow layout. Use the same task and data for alternative
layouts. Record host/build, viewport or terminal cells, device scale, selected
ID, revision and capabilities with each capture.

Critique each finding as observation -> user cost -> specific repair -> recheck.
Separate product behavior, authored prototype behavior, and capture-tool failure.
A blank screenshot with passing DOM assertions requires fixing the capture,
then inspecting actual pixels. A hypothetical concern is not an observed defect.

Check labels, edge crossings, clipping, scroll containment, exact values,
keyboard/focus, contrast, long names, zero/one/empty/large data and canceled late
responses. Test web widths 320/390, 768 and 1280 or wider as appropriate; test
terminal widths 60/80/120 cells. Keep any necessary two-dimensional region
contained so ordinary controls and prose still reflow. A local renderer,
valid stream or native test engine establishes only its own validation layer.

## ChatGPT Desktop choices

Use a local-thread MCP App for a rich local inspector. Keep domain state and
actions in the server and render in the sandboxed resource. Route direct
refresh/page/query actions through the supported bridge, and keep visual
selection/filtering local. Do not rebuild a React/HTML interface through a
sequence of assistant messages.

Bundle a complete initial view and give text-only clients a useful summary.
Negotiate optional extensions/capabilities. A method existing on an SDK or
window.openai does not prove permission to download files, open links or change
display mode. Prefer the standard App SDK; feature-detect host extensions only
for a required enhancement. Respect returned display modes and retained state.
[Official ChatGPT UI contract](https://developers.openai.com/plugins/build/chatgpt-ui).

Use one compact inline task view before expanding a multi-panel workspace.
Keep export honest: static SVG/PNG preserves a snapshot, interactive HTML
preserves supported browser behavior, and a JSON view can work when sandbox
downloads are unavailable. Verify each promised format from the actual resource.
Do not label an exported HTML snapshot a live Python/server application.

Local stdio, remote deployment and stock-host rendering are separate tests.
Check the exact local plugin declaration/working directory and resource bytes,
then the real bridge and host. An iframe in a local browser is a prototype
renderer, and an in-app browser artifact is a browser alternative. Neither
alone establishes native inline plugin acceptance.

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
- [Codex choices](#codex-choices)

## Start from an inspection task

Write the question first: for example, "Which dependency explains this service's
latency, and what changed over 24 hours?" Define stable entity/edge IDs, units,
timestamps/timezone, missing-value rules, data revision, and selection state.
Keep one authoritative model. Derive the graph, chart, table and inspector from
that model; an export must contain the same scope and values.

For an explicitly requested multi-view workspace, use: a compact summary, one active analysis
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

## Codex choices

For a browser prototype, keep grid tracks and their children shrinkable:

```css
.workspace { display:grid; grid-template-columns:minmax(0,1fr) 18rem; }
.analysis, .inspector { min-width:0; }
.table-region { max-width:100%; overflow:auto; }
@media (max-width:760px) { .workspace { grid-template-columns:minmax(0,1fr); } }
```

Use a neighborhood/list or a contained spatial region at 320px. A min-width on
an SVG/panel can otherwise expand the entire document despite a responsive
outer grid. Measure document scrollWidth as well as child bounds. Use explicit
UTF-8 when reading/writing generated HTML in Windows validation scripts.

Use allocated width as the graph-density boundary, including intermediate
side-panel widths. A 14px label in an 840-unit SVG becomes about 7.65px when
the panel gives it 459px. A window-level breakpoint alone can miss this. Keep
the panel shrinkable and query its own inline size; the query styles descendants:

```css
.analysis { container-type:inline-size; container-name:analysis; }
.neighbor-list { display:none; }
@container analysis (max-width:760px) {
  .spatial-map, .map-tools { display:none; }
  .neighbor-list { display:grid; }
}
```

Derive the threshold from the actual label budget, topology and controls; 760px
is an example, not a host limit. Keep selected ID, scope counts and explicit
full-list access in the compact view. Restore keyboard focus by stable record
ID after rebuilding a list; if its relationship trigger no longer exists,
focus the updated inspector heading. Recheck the actual panel's selected
values, exact table and focus, then preserve before/after screenshots.

Choose the executing frontend before the visualization. The desktop may expose
a supported MCP App/plugin UI route; CLI output, IDE behavior and an owned
app-server frontend have different contracts. Do not infer an iframe from
successful MCP tool discovery, and do not claim an owned frontend is always
required. Inspect the current loader, negotiated protocol and frontend source.

For a desktop-capable route, keep a portable MCP tool/resource boundary:
structured data + useful text, bundled HTML/SVG, direct server actions, stable
IDs and optional capabilities. Validate the actual declared command and working
directory. A bundled server can differ from the editable source used in tests.
For the CLI, show a ranked table, direct relationship list and compact trend;
give an explicit browser/SVG artifact for spatial inspection.

Use elicitation for bounded structured input when the negotiated client supports
it; it is not a general-purpose graph canvas. For an owned app-server frontend,
keep selection/filtering in frontend state and map refresh/edit actions to the
actual backend APIs. Keep approval and policy events in the host's supported
flow; do not impersonate them in an authored graph or drawer.

Compare native controls, an MCP App, a browser artifact and an owned frontend
against the task. Record which is installed and which actually painted.
Showing a browser tab inside Codex proves the browser alternative works; it
does not prove the portable package was accepted by the stock plugin loader.

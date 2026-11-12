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
- [Gemini Enterprise alternatives](#gemini-enterprise-alternatives)

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

## Gemini Enterprise alternatives

Pin the Gemini Enterprise composite catalog and its retrieved digest. The
November 12, 2026 catalog provides several distinct rich-view routes:

| Route | Use | Boundary |
| --- | --- | --- |
| MaterialTabs + MaterialTable | Native analysis tabs and exact values | Host styling and catalog props; rows use the declared string/object or binding contract. |
| VegaChart | Declarative quantitative plots | Put the Vega-Lite spec in the surface model and bind spec to its path; validate both wrapper and chart spec. |
| Canvas root | A persistent resizable side-panel workspace | Canvas must be the root; configure a meaningful opener card. |
| IFrameSrcdoc | A self-contained custom graph/chart workspace | Enforced connect-src 'none'; no outbound fetch/CDN dependency. |
| Image/table or text relations | Reviewable snapshot/fallback | Preserve exact values and direction; an image is not interactive topology. |

For a rich Vega spec, use a component such as:

```json
{"id":"latency","component":"VegaChart","spec":{"path":"/chart"},"height":300}
```

Store the actual Vega-Lite object at /chart through updateDataModel. A complex
raw object directly in spec can fail the catalog's DynamicValue contract even
though the description calls it a JSON object. MaterialTable literal cells
follow the schema's string contract; format units deliberately or use a valid
model binding. Validate runtime bound data as well as the wire wrapper.

MaterialTable columns are objects, not an array of header strings:

```json
{"id":"values","component":"MaterialTable","columns":[{"header":"Latency (ms)","field":"latency"}],"rows":[{"latency":"180"}]}
```

Use the bundled chart-and-table template for an exact complete envelope/model
example. Do not infer props from another table framework or a similarly named
catalog component. The bounded message checker cannot detect every catalog error.

Use Canvas autoOpen:false and autoFullscreen:false for a user-opened workspace
when unsolicited expansion would interrupt chat. closePanel:true is a one-shot
panel-close command, distinct from deleting the surface; later omission does
not reopen it. This catalog component is distinct from HTML canvas2D and the
separate Gemini Enterprise Canvas product.

Bundle IFrameSrcdoc scripts/styles/data. Keep refresh/export disabled or honest
when no bridge is implemented. The catalog mentions a2ui_action events, but it
does not by itself establish their full wrapper, backend handling or authority.
Inspect the matching A2A/A2UI implementation before wiring actions. Do not
invent an MCP App bridge inside it.

Bind the official envelope's relative catalog.json to the selected catalog's
component AND function unions; DynamicValue validation can reference
anyFunction even for a chart. Preserve official schema base URIs. Validate
Vega-Lite against its chosen schema/version separately; catalog acceptance
does not validate every internal visualization feature.

[Official composite catalog](https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json),
[component reference](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/a2ui-component-gallery-reference).
Schema success and a local iframe preview do not establish Google Cloud
deployment, A2A streaming/actions, registration, host styling or real host paint.

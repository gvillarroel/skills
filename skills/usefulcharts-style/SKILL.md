---
name: usefulcharts-style
description: Create editable educational posters inspired by UsefulCharts, with compact family trees, branching histories, and parallel timelines. Use for genealogy, dynasties, institutional or idea lineages, and chronological wall charts where spatial hierarchy, relationship routing, semantic color, and print readability matter.
---

# UsefulCharts-style posters

Create an original information poster with a clear reading order, stable family colors, compact labels, and deliberate connector corridors. Use the user's data and wording. Treat UsefulCharts as a design reference; identify the result by its subject and author, without their logo or an implied affiliation.

## Choose and plan the composition

1. Identify the relationship model before drawing. Distinguish parentage, partnership, institutional branching, succession, and influence. A chronological neighbor is not automatically an ancestor. Record uncertain claims and sources; mark invented demonstration data visibly as synthetic.
2. Read [visual grammar](references/visual-grammar.md). Choose a **genealogy** for generations and unions, **lineage** for branching categories or ideas, or **timeline** for comparable dated intervals. Read only the matching recipe in [pattern recipes](references/pattern-recipes.md).
3. Design the page as a poster: a shallow dark title strip, light chart field, compact category key, most space reserved for relationships, and a quiet source/reading footer. Use portrait 2:3 by default; change the aspect ratio when the content benefits. Separate the graph's data model from authored row/column placement.
4. Allocate columns to coherent branches and reserve gaps for long connectors. Align partners, keep siblings near their common junction, and keep branches in a stable left-to-right order. For a timeline, derive every interval position from the same numeric year scale. For schematic rows, explicitly say that vertical spacing does not measure elapsed time.

## Build an editable result

For a deterministic SVG and a local zoomable HTML viewer, read [the input contract](references/data-contract.md), then write a JSON brief outside the skill directory. A small starting brief is available at [assets/templates/starter.json](assets/templates/starter.json); adapt it to the task rather than copying its subject or topology.

For an ordinary branching history, prefer `mode: lineage` with `layout: auto`: supply named/color-coded groups, nodes, and typed edges, and omit node rows/columns and page dimensions unless the user specifies them. The renderer orders stages, allocates branch columns, and budgets width for names. Use manual placement for genealogies or a deliberately composed layout. The report exposes the automatic placements for review.

For a long brief, assemble a native Python/JavaScript object and write it with `json.dumps`/`JSON.stringify`; repeated hand-written JSON arrays are prone to mismatched closing brackets. Keep the source data human-readable with indentation.

Run the bundled renderer without reading its implementation:

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
```

Paths are explicit and relative to the working directory. Create exactly the paths requested by the user. The renderer has no third-party dependencies. It escapes labels, selects contrasting text, checks graph semantics, routes orthogonal lines around nodes, and fails on collisions it cannot repair. It never drops a node or edge to make a layout pass.

Use `columns`, node `col`/`row`, `node_width`, page dimensions, and lane positions to repair crowding. Keep body type at least 16 SVG units on the default 1600-unit width; use enlargement, wrapping, or more space before reducing text. The renderer's metrics are a preflight, not a visual quality verdict.

When a requested composition falls outside the renderer (for example, hundreds of intermarriages, portraits, maps, or a glyph comparison matrix), retain the same data and visual grammar and author an SVG directly or extend a copy of the renderer in the working directory. Do not force that data into a false tree. Keep full text, typed relationships, source notes, and a reproducible source file. The bundled browser audit supports its own SVG metadata; custom SVG requires equivalent geometry and semantic checks.

## Render, inspect, and repair

Run the browser audit for actual font geometry and export:

```sh
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --report browser.json --png poster.png
```

It uses Playwright Chromium (or installed Chrome/Edge); see [evaluation and repair](references/evaluation.md) for browser provisioning and the full rubric. Open the PNG with the available image-reading tool; the browser audit already supplies image rendering and measured geometry without Pillow. Inspect at page scale and zoom into the densest junction, longest label, and uncertain connection. Check the SVG/HTML at 100% zoom. Re-render after repairs and inspect the final output, not an earlier draft.

Compare against a relevant reference family when visual resemblance is requested. Judge page silhouette, hierarchy, branch placement, connector semantics, category color, density, and typography separately. Do not claim a numeric similarity percentage from a screenshot or treat a zero-collision report as proof that the poster looks right.

Deliver the editable SVG, source JSON, a preview, and the viewer when useful. Explain what was verified and any unresolved limitation. A chart needs readable connected information, not just the frame and palette.

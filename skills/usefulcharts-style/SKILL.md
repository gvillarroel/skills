---
name: usefulcharts-style
description: Create editable educational posters inspired by UsefulCharts, with compact family trees, branching histories, and parallel timelines. Use for genealogy, dynasties, institutional or idea lineages, and chronological wall charts where spatial hierarchy, relationship routing, semantic color, and print readability matter.
---

# UsefulCharts-style posters

Create an original information poster with a clear reading order, stable family colors, compact labels, and deliberate connector corridors. Use the user's data and wording. Treat UsefulCharts as a design reference; identify the result by its subject and author, without their logo or an implied affiliation. A cream background, colored boxes, and a condensed title do not establish a convincing resemblance.

## Choose and plan the composition

1. Identify the relationship model before drawing. Distinguish parentage, partnership, institutional branching, succession, and influence. A chronological neighbor is not automatically an ancestor. Record uncertain claims and sources; mark invented demonstration data visibly as synthetic.
2. Read [editorial composition](references/editorial-composition.md) when matching this poster family. Choose a **genealogy** for generations and unions, **lineage** for branching categories or ideas, or **timeline** for comparable dated intervals. Read only the matching recipe in [pattern recipes](references/pattern-recipes.md).
3. Design the page as a poster: a shallow dark title strip, continuous light chart field, most space reserved for relationships, and a quiet source footer. Use portrait 2:3 for a dense wall chart. Let source complexity determine the format; a short 20-record tree needs a compact composition, not a nearly empty giant canvas. Separate data from placement.
4. Allocate columns to coherent branches and reserve gaps for long connectors. Align partners, keep siblings near their common junction, and keep branches in a stable left-to-right order. For a timeline, derive every interval position from the same numeric year scale. For schematic rows, explicitly say that vertical spacing does not measure elapsed time.

## Build an editable result

For a deterministic SVG and a local zoomable HTML viewer, read [the input contract](references/data-contract.md), then write a JSON brief outside the skill directory. A small starting brief is available at [assets/templates/starter.json](assets/templates/starter.json); adapt it to the task rather than copying its subject or topology.

For the poster aesthetic, set **`design: editorial`** and read [the editorial renderer contract](references/editorial-contract.md). This profile provides compact typography, plain labels, colored cards, family pills, emblems, rounded routes, map/count insets, and annotated temporal ribbons. The older default renderer remains a simple schematic compatibility mode; it is not the aesthetic acceptance target.

For an ordinary branching history, combine `design: editorial`, `mode: lineage`, and `layout: auto`: supply groups, nodes, and typed edges, and omit page dimensions and coordinates unless requested. The renderer infers stages and branch positions without inventing records. Use authored `x`/`y` placements for a dense genealogy or an intentionally asymmetric composition. Vary emphasis by meaning rather than random decoration. Keep important entities visible among compact unboxed supporting names.

For a long brief, assemble a native Python/JavaScript object and write it with `json.dumps`/`JSON.stringify`; repeated hand-written JSON arrays are prone to mismatched closing brackets. Keep the source data human-readable with indentation.

Run the bundled renderer without reading its implementation:

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
```

Paths are explicit and relative to the working directory. Create exactly the paths requested by the user. The renderer has no third-party dependencies. It escapes labels, selects contrasting text, checks graph semantics, routes orthogonal lines around nodes, and fails on collisions it cannot repair. It never drops a node or edge to make a layout pass.

Use explicit node widths and coordinates, lane positions, or the automatic layout to repair crowding. Editorial posters typically use 10–16-unit body type on an 1800-unit-wide canvas and must be inspected at intended print size; this is deliberately dense wall-chart typography. Do not shrink long labels repeatedly to rescue poor placement. The renderer's metrics are a preflight, not a visual quality verdict.

For unsupported structures, retain the same data and visual grammar and author an SVG directly or extend a copy of the renderer in the working directory. Do not force a cyclic network into a false tree. Keep full text, typed relationships, source notes, and a reproducible source file. The bundled browser audit supports its own SVG metadata; custom SVG requires equivalent geometry and semantic checks.

## Render, inspect, and repair

Run the browser audit for actual font geometry and export:

```sh
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --report browser.json --png poster.png
```

It uses Playwright Chromium (or installed Chrome/Edge); see [evaluation and repair](references/evaluation.md) for browser provisioning and the full rubric. Open the PNG with the available image-reading tool; the browser audit already supplies image rendering and measured geometry without Pillow. Inspect at page scale and zoom into the densest junction, longest label, and uncertain connection. Check the SVG/HTML at 100% zoom. Re-render after repairs and inspect the final output, not an earlier draft.

Compare the final image beside a relevant reference at the same display width, then compare a dense detail at the same relative scale. Judge silhouette, asymmetry, focal hierarchy, supporting annotations, line weight, and texture separately from correctness. Identical chains, equally populated families, continuous uniform bars, and one card treatment everywhere are visible template artifacts. A clean audit cannot override an obvious aesthetic mismatch. Never claim an indistinguishable result or a numeric similarity percentage without the evidence to support it.

Deliver the editable SVG, source JSON, a preview, and the viewer when useful. Explain what was verified and any unresolved limitation. A chart needs readable connected information, not just the frame and palette.

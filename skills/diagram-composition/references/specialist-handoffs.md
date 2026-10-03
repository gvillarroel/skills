# Specialist handoffs and SVG normalization

Discover companions from the current skill catalog; never assume their locations
or require their files in this bundle. Read and follow a companion's own entry
point when invoking it. Select by visual need, not by habit:

| Need | Optional companion | Standalone fallback |
| --- | --- | --- |
| Standard sequence, ER, state, tree, flow, timeline notation | mermaid or plantuml-colorset-renderer | Native SVG with explicitly preserved notation and accessible labels |
| Custom radial, network, matrix, or aligned data geometry | d3 | Deterministic SVG coordinates and native paths |
| Conventional quantitative charts | echarts-animated-svg or slidev-echarts for a requested deck | Plain SVG bars/dots with truthful shared scales |
| Dense hierarchy | hierarchy-lens or usefulcharts-style | Labeled nested groups or a compact tree |
| Bespoke explanatory illustration | svg-brief-design | Simple native SVG schematic |
| Exact technical brands/products | technical-logo-assets | Supplied SVG, or exact short text if unavailable |
| Generic interface/concept pictograms | iconify-icon-search | Simple unbranded shape with a short label |
| Shared live values or navigable megacanvas | compose-synchronized-svg | Keep this task static, or explicitly explain the unavailable interactive scope |

Every handoff should include:

```text
Panel ID / viewer question / one claim:
Exact facts, canonical concept IDs, and relationship meanings:
Chosen family and reason; rejected alternative:
Output SVG path and editable source path:
Body width x height; intended displayed label size:
Canonical concept ID -> exact color map, neutral theme, and SVG color bindings:
Type scale, icon exports, and shared legend policy:
Connection objects/ports; data-node-id, node/container kind, and wire annotations:
Static SVG, native text (no foreignObject), tight viewBox, no remote assets:
```

Return an SVG plus its source and named object-bound ports. Use the browser
`measure` command in [connectors-and-surfaces.md](connectors-and-surfaces.md)
for annotated imported geometry. Have the specialist
apply [shared-colors.md](shared-colors.md), overriding renderer defaults where
needed. Require the same semantic colors and quantitative scales across views;
annotate actual colored marks so the final browser audit can check the result.
Have the specialist
fix unsupported exports at source. Mermaid-like HTML labels must be disabled
before rendering. Snapshot interactive charts to a meaningful static state;
do not carry an entire dashboard runtime into one panel.

## Import contract

The composer accepts self-contained native SVG, local definitions/references,
presentation attributes, and inline styles. It prefixes IDs, `url(#...)`, local
hrefs, and accessibility references. It rejects duplicate/missing IDs, script,
HTML, animation, raster/external images, external resources, and stylesheet
blocks. Embedded `data:image/svg+xml` images are recursively validated and
expanded into native SVG, preserving artwork and local references. This supports
vector-only logo exporters that wrap their artwork in an embedded SVG image.
Other icons must be inlined instead of using external `<image>` paths.

When a trusted static renderer emits CSS, materialize it first:

```text
uv run --script <skill-root>/scripts/audit_diagram.py prepare --input rendered.svg --output prepared.svg --overwrite
```

This browser step copies computed presentation properties into the SVG and
removes stylesheets, with JavaScript disabled and network requests blocked.
Unused renderer animation classes/keyframes are discarded; active animation
requires a meaningful static export before normalization.
Nested viewports retain their clipping behavior. Some renderers intentionally
draw long lifelines beyond the viewBox; the audit reports these as `clippedMarks`
for visual review instead of extending them across neighboring panels. Text
outside its allocated body is still a failure, even when clipped.
It does not convert HTML labels or flatten external assets; fix these at source.
Then compose `prepared.svg`. Preserve original renderer output and source.

For exported icon SVGs, copy their native vector children into a nested SVG at
the desired bounds, preserving the original viewBox and `meet` aspect ratio.
Namespace IDs if using an icon more than once within one panel. Keep accessible
names and provenance/license sidecars. Do not recolor protected brand artwork.

An unavailable asset should produce a visible exact text fallback or a clearly
identified unresolved identity. Do not invent a recognizable-looking logo or
silently exchange GitHub Copilot, Microsoft Copilot, Claude, and generic cloud.

The compositor intentionally does not implement every renderer. Its stable
handoff is geometry plus semantic identity, so a future specialist can be added
without changing the page-planning method.

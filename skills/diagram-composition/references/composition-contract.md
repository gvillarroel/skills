# Composition contract v1

Use UTF-8 JSON. Read the template for an executable small starting plan. Paths
are local and relative to the spec file unless absolute. Layout can run before
the source files exist. Composition requires every source. No output is written
inside the skill bundle; existing outputs require `--overwrite`.

| Field | Meaning |
| --- | --- |
| `version` | Exactly `1` |
| `title`, `thesis` | Visible short page title; accessible explanation |
| `note` | Optional short visible footer/legend line; use a source panel for a longer legend |
| `canvas` | `width`, `height`, `displayWidth`, `minTextPx`, `margin`, `gap`, `titleHeight`, `footerHeight`; positive dimensions and nonnegative reservations |
| `grid` | Positive `columns` and `rows` weight arrays |
| `concepts` | Array of `{id,label,color?}` for repeated semantic identities; optional opaque `#RRGGBB` is a shared categorical accent, never a per-panel choice |
| `panels` | Array in reading order; each panel needs fields below |
| `links` | Optional cross-panel connections; each needs fields below |

Panel fields: unique lowercase hyphen `id`; `title`, `question`, `claim`,
`family`, `reason`, `alternative`; `concepts` list of registry IDs; `source` SVG
path; `span: {row,column,rows,columns}` with one-based starting indices and
positive spans; optional `padding` (default 12), `headerHeight` (default 34),
`frame` (`none`, `line`, or `fill`, default `none`); `objects` mapping semantic IDs
to normalized `box: [x,y,width,height]`, `kind: node|container`, and optional
`shape: rect|ellipse`; `ports` mapping names to `{object,side}`. The side is left,
right, top, or bottom; its point is derived from that object's boundary. Legacy
normalized `[u,v]` values are accepted but cannot certify final endpoint contact.
Read [connectors-and-surfaces.md](connectors-and-surfaces.md) for automatic native
exports and browser measurement of annotated specialist SVGs.
Optional `routingObstacles` contains normalized `[x,y,width,height]` boxes measured
around source text and internal wires. Copy the measurement report's field or
use the complete native pipeline; do not represent those boxes as semantic nodes.

Link fields: unique `id`, `from` and `to` strings `panel-id.port-name`, nonempty
semantic `relation`, optional short visible `label` (defaults to relation),
`directed` boolean (default false), and optional `via` list of `[x,y]` points in
canvas coordinates. The route uses supplied waypoints and rejects intrusion or
wrong-side approach. Without waypoints, it searches short orthogonal routes around
node interiors, measured text/wire obstacles, and reserved panel headers, with
outward terminal segments and separated lanes. Ports reference actual fitted
objects, not arbitrary panel corners.
Containers allow child connections; labels and connector crossings are also
checked after rendering. Complex crowded arrangements may require another port
side or revised grid space.

Keep family names descriptive (for example `comparison-matrix`, `radial-hub`,
`layered-architecture`). A family name does not verify its semantics. `reason`
and `alternative` should explain real tradeoffs, not repeat the field names.
Concept lists describe presence; they do not prove that labels/icons are drawn.
For colored concepts, the browser additionally requires visible bindings in each
listed panel. Follow [shared-colors.md](shared-colors.md) for native `concept`
fields, imported SVG annotations, and the global legend policy.

The layout output reports panel, body, track geometry, and any `semanticColors`.
Layout can defer missing port coordinates with a warning
while sources are being designed, but it still rejects unknown panel IDs. The
final compose command rejects every unresolved port. Composition adds
source viewBoxes, scale, fitted rectangles, mapped ports, routes, source SHA-256,
and warnings for poor aspect fit. The SVG includes accessible title/description,
semantic panel metadata, and a copy of this report. Minimum text size is checked
in the browser after all nested transforms and display scaling.

```text
uv run --script <skill-root>/scripts/compose_diagram.py layout --spec composition.json --output layout.json --overwrite
uv run --script <skill-root>/scripts/compose_diagram.py compose --spec composition.json --output figure.svg --report report.json --overwrite
uv run --script <skill-root>/scripts/audit_diagram.py audit --input figure.svg --report audit.json --screenshot preview.png --overwrite
```

Use `--overwrite` only when replacing your own generated files. Browser audit
requires Python Playwright and installed Chromium, Chrome, or Edge. It prefers
Playwright Chromium and falls back to an installed Chrome/Edge channel only
when that binary is missing. If all browser binaries are missing,
install the normal Playwright Chromium dependency if allowed by the environment,
or state the gap. Reports list findings and exit nonzero for failed checks.
Use `--inspect` during drafting to return expected visual findings without a
command failure; `ok` remains false until they are repaired. Omit `--inspect`
from the final audit. Regeneration of your own outputs uses `--overwrite`.
Screenshots are taken at `canvas.displayWidth`; the SVG remains vector at any
zoom. Geometry and solid-surface checks cannot establish icon recognition,
causality, or perfect connector clearance: review the actual screenshot.

# Renderer input contract

`render_chart.py` reads one UTF-8 JSON object. The default canvas is 1600 × 2400 SVG units. Coordinates are in viewBox units; generated text stays editable. The title font is embedded from the bundle; the SVG makes no network requests and includes no external scripts or images.

## Shared fields

| Field | Meaning |
| --- | --- |
| `id` | Stable lowercase hyphen-case subject ID. |
| `title`, `subtitle` | Required title and optional one-line context. Keep title under about 50 characters; the renderer wraps long titles. |
| `mode` | `genealogy`, `lineage`, or `timeline`. |
| `width`, `height` | Optional canvas dimensions, at least 1000 × 1200. Default 1600 × 2400. |
| `groups` | Array of `{id, label, color}`; 1–8 categories. Color is `#RRGGBB`. Default palette can be copied from the starter. |
| `source_note` | Required concise data provenance, including “Synthetic” for invented data. |
| `reading_note` | Optional interpretation note; wrapping is automatic. |
| `frame_color`, `paper_color` | Optional `#RRGGBB`; defaults are dark oxblood and warm ivory. |
| `pattern_id` | Optional reusable pattern ID from the matching recipe; leave absent for a bespoke diagram. |

Use compact prose in notes. The renderer expands the header/footer as needed; the browser audit catches remaining overflow. Category text and fills must remain distinguishable; duplicate colors are rejected. The default SVG ink is dark charcoal.

## Genealogy and lineage

For `mode: lineage`, prefer `layout: auto` when the task does not prescribe positions. Supply `nodes` with only `id`, `label`, `group`, and optional `detail`/`emphasis`, plus the typed `edges`. Omit node `row`/`col`, `columns`, `node_width`, `width`, and `height` to let the renderer compute a compact layout. Structural links determine topological stages; influence does not change rank. Categories order leaf branches. Optional `rows` can name the inferred stages. Explicit page dimensions are honored and must still fit. The report includes `resolved_layout`; switch to manual placement for a complex merge or an exact composition. This mode does not infer missing relationships.

Internal entity, union, category, and edge IDs may contain letters, numbers, underscores, hyphens, periods, and colons; they are preserved verbatim. Keep the page `id` and published `pattern_id` in lowercase hyphen-case.

- `columns`: integer 2–18, the horizontal grid count. Start near the busiest row's node count; the grid already reserves gutters. Use fractional columns to center parents rather than adding many empty columns that narrow every label.
- `rows`: array of at least two short strings. These are schematic generation/phase labels, ordered top to bottom. The last rank ends near the bottom of the chart field.
- `node_width`: optional; default is 80–88% of a column pitch, expanded to fit the widest name word when that fits the gutter budget. Set about 125–180 units for dense 1600-wide posters. The renderer rejects widths that invade adjacent columns. `font_size` defaults to 18 (minimum 16). For large column counts, widen the page: a useful lower bound is `201 + columns * (widest_word_width + 20) / 0.88` SVG units. Do not shrink all text to fit unnecessary columns.
- `nodes`: array of `{id, label, group, row, col, detail?, emphasis?}`. `row` is an integer index starting at zero; `col` is a number from 0 to `columns-1`, including fractions. `detail` is a short date/role line. `emphasis: true` uses a stronger border. Height is derived from wrapped text; nodes on the same rank align by their vertical center.
- `edges`: array of `{id, source, target, kind, group?}`. Kinds are `descent`, `branch`, `succession`, `influence`, `uncertain`, and `adopted`. Use unique IDs. Descent, branch, succession, adoption, and uncertain links must go to a later row and must be acyclic. Influence may join nodes in either direction but cannot be a self-link. Color defaults to the target category.
- `unions`: genealogy-only array of `{id, partners: [nodeId, nodeId], children: [nodeId, ...]}`. Partners must be in the same row, separated by a gap; they are connected by a double line. Children must occur below their partners. A child's descent starts at the midpoint. For an uncertain or adopted child, leave that child out of `children` and add an edge with the union ID as `source` and the appropriate kind.
- `lanes`: optional array of `{label, group, col, span}` for named branch headings; `col` and `span` use grid columns. Headings must not overlap. They are annotations, not constraints that silently move nodes.

All node and union IDs share one namespace; edge IDs are also unique within their array and cannot collide with generated `<union>-<child>` relation IDs. References must resolve. Relation meaning must follow the input; the renderer does not infer ancestry from dates.

The router uses sparse orthogonal paths, avoids node rectangles, prefers short paths and fewer bends, and reports unrelated crossings. Crossings have a small paper-colored halo and no dot. A circle marks each true union origin. Review crossings visually even when they are technically clear. Crowded graphs can exceed the bundled router; use more space, improved column ordering, or an authored extension instead of accepting an unreadable tangle.

## Timeline

- `time`: `{start: number, end: number, step: positive number, notation?: "numeric" | "historical"}`. End must be greater than start. Tick count is limited to 80; a finer grid needs a larger design, not hundreds of tiny labels.
- `lanes`: array of `{id, label}`; each occupies an equal width. For uneven lane widths, author a custom layout.
- `periods`: array of `{id, label, group, lane, start, end, detail?, track?, tracks?}`. `lane` resolves to a lane ID. `track` starts at 0, `tracks` defaults to 1. Use the same `tracks` count for all periods in a lane. Width is subdivided by tracks; actual time is never stretched to fit text. A narrow colored ribbon records the interval, and a horizontal name/date label sits beside it. Intervals must be long and wide enough for their content; otherwise the renderer returns a repair error.
- `nodes`, `edges`, and `unions` are not accepted in timeline mode. This renderer draws comparable intervals and does not infer transition relationships.

## Output and errors

```sh
uv run --script <skill-dir>/scripts/render_chart.py data.json --svg out/chart.svg --html out/chart.html --report out/layout.json
```

`--svg` is required; `--html` and `--report` are optional. Output parents are created. Files are written only after input and layout checks pass. Input and output paths must be distinct. The report includes source SHA-256, node/edge counts, canvas, geometric checks, crossing count, and a clear statement that visual judgment is still required.

Failures exit with code 2 and a concise English diagnostic. Fix the stated input or layout issue and run again. A diagnostic is not permission to delete labels, change facts, collapse relationships, or move numeric endpoints.

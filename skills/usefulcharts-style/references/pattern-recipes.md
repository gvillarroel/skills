# Pattern recipes

## Genealogy with partnerships

**Pattern ID:** `usefulcharts-dynastic-genealogy`

Trigger: named people, generations, partners, parentage, and dynasty/category membership.

Input: `mode: genealogy`; ordered `rows`; nodes with stable IDs, category, row, and column; `unions` linking two partners with explicit children. A union is a relationship object, not an invented person. Single-parent data may use a `descent` edge.

1. Arrange partners in the same row and reserve an empty gap between them.
2. Put the next generation below. Use half-column positions to center a lone child or a partner pair.
3. Give each branch a stable category; derive connector color from the child's category unless the data explicitly specifies another category.
4. Use `uncertain` or `adopted` only when supported by the supplied data. Use `succession` separately from parentage. Do not invent a missing partner or use a partnership line to imply biological parenthood.
5. Render, audit, and zoom into every partnership junction. Check the child source is the union midpoint, not the closer partner's box.

Validation: run `render_chart.py` and `audit_chart.py`; inspect every edge touching two categories. Pitfalls: repeated names without unique IDs; multiple marriages overlapping on one row; descendants connected to a sibling bar as if it were a spouse; crossing lines mistaken for junctions. Use aliases with an explicit same-person note for a deliberately repeated person; never silently duplicate identity.

## Branching institutional or idea history

**Pattern ID:** `usefulcharts-branching-lineage`

Trigger: splits, inherited methods, institutional families, or an evolutionary classification whose relationship meaning is explicit.

Input: `mode: lineage` with `layout: auto`; named category groups, nodes, and typed `branch`, `influence`, or `uncertain` edges. Let the renderer assign schematic rows and columns unless a deliberate manual composition requires explicit placements. Keep evidence on edges as well as nodes when the connections are factual claims.

1. Center shared precursors above the major branches.
2. Give each branch a named lane and a stable color, widening prolific families.
3. Use solid trunks for declared branch relationships; use dotted arrows for influence so resemblance does not masquerade as descent.
4. Keep cross-branch paths in the inter-rank corridors and review their intersections.
5. Explain schematic vertical spacing; a displayed date in a label does not make the layout a numeric time scale.

Validation: render and browser-audit; count nodes/edges against source, inspect the longest cross-branch route, and check semantic legends. Pitfalls: force-directed placement destroys reading order; a timeline ordered by attractive spacing misrepresents intervals; a hierarchy label does not prove a historical link.

## Parallel historical intervals

**Pattern ID:** `usefulcharts-parallel-history`

Trigger: compare contemporaneous phases, civilizations, institutions, or programs across places/categories.

Input: `mode: timeline`; numeric `time.start`, `time.end`, and `time.step`; named lanes; periods with `start`, `end`, `lane`, `group`, and short labels. Use `time.notation: historical` for BCE/CE, with astronomical year 0 representing 1 BCE; otherwise years are ordinary numeric values. State that convention in the note when used.

1. Assign each parallel lane to one stable domain.
2. Derive all y coordinates and bar lengths from the same time mapping. Keep intervals within the declared bounds; reject reversed intervals.
3. Set `track` and `tracks` for overlapping intervals in the same lane; overlap in time is valid, overlap of printed labels is not.
4. Use narrow duration ribbons with adjacent horizontal labels. Put an opaque paper-colored surface behind labels so grid lines do not run through text. Short intervals may need a larger page or external callouts; do not stretch duration to fit text.
5. Include an explicit date scale, tick labels, legend, and period dates.

Validation: compare at least three interval endpoints with the time mapping and check contemporary periods share their y coordinates. Pitfalls: inventing connecting descent from adjacent periods; hiding long gaps; mixing ordinal generations with metric years; equalizing lengths to improve appearance.

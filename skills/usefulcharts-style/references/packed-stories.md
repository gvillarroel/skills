# Pack an institutional story around its records

Use `design: editorial`, `mode: lineage`, `layout: packed` for a medium history with a deliberate relative arrangement, typically 31–100 records. This route preserves the chosen arrangement while measuring its page. When only records and relationships are supplied, start from [data-first branches](data-first-branches.md) instead of inventing dozens of placement hints.

Read [the small template](../assets/templates/packed-lineage.json) only when a complete input example is useful. It is invented data. Replace every record and relationship with the supplied subject.

## Supply relative positions and exact content

Give each node `id`, `label`, `group`, and relative `x`/`y` hints. The hints describe left/right and earlier/later placement; they are **not final SVG coordinates**. A rough arrangement such as x = 1, 3, 5 and y = 1, 2, 3 is sufficient. Place a successor below each structural predecessor. Keep neighboring source dates in a sensible order, while retaining uncertainty in the printed date. Distances remain schematic.

Use `date_label` for the exact visible date and `detail` for the short historical consequence. Packed nodes default to `detail_position: outside`: date above the name, caption below. Set `emphasis: true` on the major developments named by the user. The renderer gives other mergers stronger treatment and single continuations quieter names while preserving every source category. A relevant optional `icon` can identify a landmark; its presence alone does not justify adding a new event.

Omit page dimensions, node widths, font overrides and absolute route hints for the first preview. The renderer uses measured 18-unit names, adjusts larger landmarks, and packs the content with space for attachments. It preserves relative ordering and all source fields; it does not scale the text down to fit. The separate category key is automatic. Set `legend: false` only when another visible key already explains every category.

## Compose the local stories

- Give a shared precursor a central position above its descendants.
- Place an actual merger near both of its predecessors. Put a short terminating branch beside the continuing story.
- Give a family with more active branches more horizontal positions. Reclaim positions after branches end; do not maintain an empty column for a terminated institution.
- Let a later family begin beside its actual source. Avoid placing a distant new branch at the far edge merely because its color is new.
- Put supporting records closer in the relative arrangement than major changes. The packer removes unnecessary gaps, but it cannot choose the right narrative neighbors for you.

The packer reserves the full date/name/caption envelope. It preserves left/right and vertical order, enforces separation between every pair, and keeps structural successors below their predecessors. It does not provide a numeric time axis or a visual-similarity score.

## Render, inspect and repair

```sh
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

Open the PNG. Compare whole-page readability, the busiest merger and the longest influence path with the reference. Keep a meaningful contrast between landmarks and supporting names. A grid of equal colored boxes remains a weak composition even when it is compact.

Change relative hints to improve neighborhoods, then rerender. For one difficult corridor or a contextual inset, copy the measured centers and widths from `layout.json`'s `resolved_layout.nodes` into an authored brief, remove `layout: packed`, and retain the measured page dimensions. Then add explicit `via` or `corridor_y` routes and audit again. Do not mix absolute route coordinates with relative placement hints.

Node-anchored annotations may be added after reviewing the first preview. Fixed page annotations and insets require the authored route so they receive deliberate space. Honor a user's prescribed coordinates with an authored layout; do not silently reinterpret them as relative hints. Partnerships belong in the genealogy/cohort route.

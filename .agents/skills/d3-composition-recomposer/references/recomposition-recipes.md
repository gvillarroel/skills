# D3/SVG Recomposition Recipes

Use these recipes to convert one source pattern into a composition-specific variant.

## ID and Metadata Contract

Use this ID shape for every named variant:

```text
d3-composition-<composition-id>-<source-id>
```

Expose these fields when the variant appears in a gallery card:

- `data-composition-id`: target composition ID.
- `data-example-id`: source example ID.
- `data-pattern-id`: stable base pattern ID, usually `d3-pattern-<source-id>`.
- `data-composition-pattern-id`: stable variant ID.

When the user gives only a pattern family or source ID, build a small representative structure that preserves the family semantics instead of searching a gallery fixture. For example, a force-network placeholder should remain a node-link graph with at least seven nodes and enough links to show clusters, bridges, and the requested armature.

## Balance and Symmetry

Use for comparison, calm dashboards, mirrored categories, and centered system maps.

- Put the primary shared node, central metric, or comparison baseline on the visual center.
- Distribute visual mass across left/right and top/bottom axes.
- Move bridges, legends, or summary chips near the center instead of leaving them as corner clutter.
- Good sources: networks, mirrored distributions, overlap sets, balanced bars, paired tables.

## Diagonal Armature

Use for change, conflict, escalation, progress, and before/after stories.

- Place source or starting state low-left and outcome or target state high-right.
- Align route endpoints, connectors, or major node centers along the diagonal.
- Use reciprocal diagonals for secondary comparisons or tension.
- Good sources: routes, connected scatter, critical paths, Sankey/alluvial flows, slope charts, attention arcs.

## Golden and Root Divisions

Use when one field is dominant and another field explains, summarizes, or constrains it.

- Give the primary chart the larger field.
- Put legend, notes, totals, or comparison table in the shorter field.
- Align the division line with a visible guide or container edge.
- Good sources: treemaps, document quality views, scorecards, inline bar tables, probability views.

## Thirds and Fifths Grid

Use for repeatable dashboards, reports, matrix views, and sortable modules.

- Snap cards, cells, rows, columns, and labels to modular tracks.
- Keep row and column rhythm stable during sorting or filtering.
- Use consistent gutters and fixed preview aspect ratios so the pattern can join a larger page.
- Good sources: tables, calendars, heat matrices, waffles, Kanban boards, scatterplot matrices.

## Radial and Rosette

Use for cycles, peer categories around one center, weighted wheels, and reciprocal relationships.

- Give the center a real semantic role: hub, selected state, root, pointer, or current phase.
- Use rings for hierarchy or magnitude bands and spokes for peer axes.
- Keep angular slots consistent and reserve outer lanes for labels when needed.
- Good sources: force networks, radial hierarchy, sunburst, chord, radar, circular bars, roulette samplers, phase rings.

## Flow Spine

Use for pipelines, timelines, handoffs, model execution, and source-to-output stories.

- Lay out source, transform, checkpoint, and output on one readable path.
- Keep branches secondary and return them to the spine.
- Use labels as station names or lane headers rather than floating annotations.
- Good sources: Sankey, alluvial, state machines, sequence lifelines, Gantt rollouts, token flows, router capacity views.

## Dense Label Lanes

Use when the data field is dense and labels must remain inspectable.

- Keep points or regions in the central field.
- Move labels into side, top, bottom, or ring lanes with short, unambiguous leaders.
- Reserve enough lane spacing for the longest label at the smallest target viewport.
- Good sources: maps, bubble scatter, point clouds, word fields, scientific scatter, optimized label examples.

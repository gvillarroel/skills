# Radial hierarchy with stable lenses

**Pattern ID:** `hierarchy-radial-lenses`

- **Trigger:** One large rooted hierarchy must be understood through several attributes without moving its entities between views.
- **Input:** The flat JSON contract in [data-contract.md](data-contract.md), with stable identities and individual source measurements.
- **Output:** A self-contained HTML explorer containing one SVG map, accessible controls, a details panel, and static SVG/PNG downloads.
- **Published example set:** `hierarchy-lens`; [live example](https://gvillarroel.github.io/skills/examples/hierarchy-lens/#hierarchy-radial-lenses).

## Implementation

1. Build the parent-child tree once and compute subtree headcount, depth, and optional observed metric sums bottom-up.
2. Assign each child an angular span proportional to its subtree headcount inside its parent. Reserve the parent's own one-entity share at the end. Leave that outer share blank; it has no further reports. Avoid duplicating a manager as a synthetic employee leaf.
3. Draw equal-width rings by relative reporting depth. Angle encodes subtree count; area is not a headcount comparison across rings. An outer node cannot be compared by area with an inner node.
4. Keep spans and sibling order fixed when colors, metric scope, search, or category highlighting change. Rebase geometry only when the user explicitly focuses a branch or changes visible ring count.
5. Define categorical colors from the full dataset. Numeric scales start at zero and use one full-dataset maximum for the selected metric and scope. Focus must not renormalize the scale. The optional log scale uses log1p and explicitly labels its transformation.
6. Treat category selection and search as highlighting, preserving the surrounding context. Count matches separately from all visible nodes. Search the whole hierarchy and let a result focus its parent so a tiny or hidden node remains discoverable.
7. Provide breadcrumbs, an up action, overview reset, ring count, hover/focus detail, keyboard previous/next mark movement, Enter to focus, and Escape to move up. Dense marks do not all need to be tab stops; a roving tab stop plus searchable records is preferable.
8. Keep labels only when they fit their visible arc at the actual screen size. The details panel and search expose exact text. Show how many nodes are outside the visible ring limit. Large maps require branch exploration; no static overview makes thousands of names legible.

The partition model is an adjacency representation: containment and placement replace connectors. See the [official D3 partition documentation](https://d3js.org/d3-hierarchy/partition) for the underlying representation. The bundled implementation uses native SVG and JavaScript, so it ships without a D3 runtime dependency.

## Validation

```text
uv run --script <skill-root>/scripts/audit_explorer.py explorer.html --report audit.json --screenshot overview.png
```

Validate fixed geometry across lenses, category and numeric-domain stability after focusing, node/parent conservation, null versus zero, partial aggregate coverage, export contents, keyboard interaction, and mobile overflow. A synthetic 1200-record example is the default acceptance fixture; measure larger inputs separately.

## Pitfalls

- Sorting by the active metric destroys spatial memory. Keep metric ranking in a separate list if requested.
- Adding all subtree totals double-counts descendants. The total for a branch is the sum of individual known values once, not the sum of rendered ring values.
- A missing token observation is not inactivity. Avoid productivity or performance conclusions from usage alone.
- Multiple managers form a graph. Do not fabricate a tree or clone people without explaining the chosen relationship.
- SVG and PNG exports preserve the current colors, legend, units, period, focus, and missing-data note, but are static. Deliver HTML for interaction.

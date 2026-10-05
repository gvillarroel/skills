# Graph Charts In Slidev

- **Data shape:** Use `data` nodes with stable names and `links` with source/target names plus values.
- **Animation pattern:** Prefer deterministic layouts such as `circular` for validation decks. Animate symbol size and link width, not random force positions.
- **Display guidance:** Use graph charts for topology, not simple flows. Add adjacency emphasis and keep node labels short.
- **Conceptual diagram packing:** Prefer content-sized nodes and short explicit routes. Compare orientation or fixed-coordinate arrangements rather than spreading nodes across all available space. Reduce only surplus gaps; retain complete arrowhead envelopes, label clearance and distinct lanes. Check a tighter candidate at delivery scale and undo any reduction that obscures an endpoint or makes unrelated edges appear joined. Circular/force layouts are choices to evaluate, not inherently compact defaults. Keep quantitative graph encodings intact.
- **Modules:** Register `GraphChart` and `TooltipComponent`.
- **Pitfalls:** Force layout can make screenshots flaky; use fixed coordinates or circular layout when reproducibility matters.
- **Directed edges:** Follow [arrow contrast](../arrow-contrast.md). For fixed `layout: 'none'` graphs with axis-aligned built-in nodes, call `insetGraphArrowRoutes(chart, 3)` after native layout and repeat after resize/click updates. Inspect the complete head at each target; a safe canvas color does not qualify a route crossing another filled node. Circular/force layouts require an explicit resting geometry review.

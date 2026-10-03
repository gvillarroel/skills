# Graph Charts In Slidev

- **Data shape:** Use `data` nodes with stable names and `links` with source/target names plus values.
- **Animation pattern:** Prefer deterministic layouts such as `circular` for validation decks. Animate symbol size and link width, not random force positions.
- **Display guidance:** Use graph charts for topology, not simple flows. Add adjacency emphasis and keep node labels short.
- **Modules:** Register `GraphChart` and `TooltipComponent`.
- **Pitfalls:** Force layout can make screenshots flaky; use fixed coordinates or circular layout when reproducibility matters.
- **Directed edges:** Follow [arrow contrast](../arrow-contrast.md), use native `edgeSymbol` clipping and inspect the actual head at each target; a safe canvas color does not qualify a route crossing another filled node.

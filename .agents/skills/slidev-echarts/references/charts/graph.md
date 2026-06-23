# Graph Charts In Slidev

- **Data shape:** Use `data` nodes with stable names and `links` with source/target names plus values.
- **Animation pattern:** Prefer deterministic layouts such as `circular` for validation decks. Animate symbol size and link width, not random force positions.
- **Display guidance:** Use graph charts for topology, not simple flows. Add adjacency emphasis and keep node labels short.
- **Modules:** Register `GraphChart` and `TooltipComponent`.
- **Pitfalls:** Force layout can make screenshots flaky; use fixed coordinates or circular layout when reproducibility matters.

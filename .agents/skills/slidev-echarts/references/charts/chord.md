# Chord Charts In Slidev

- **Data shape:** Use category nodes and weighted links. Keep the node set small and stable across clicks.
- **Animation pattern:** Update link values while preserving node names. Stable nodes keep arcs anchored as ribbons thicken or shrink.
- **Display guidance:** Use chord when reciprocal overlap is the point. Keep labels short because radial label space is limited.
- **Modules:** Register `ChordChart`, `LegendComponent`, and `TooltipComponent`.
- **Pitfalls:** Chord charts become unreadable with many categories; switch to sankey for directional multi-stage flow.

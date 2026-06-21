# Scatter Charts In Slidev

- **Data shape:** Use tuples such as `[name, x, y, size]` or objects with explicit dimensions. Encode tooltip fields so the visible chart can stay clean.
- **Animation pattern:** Move points by changing x/y values across `$clicks`; keep point names stable. Use `visualMap` for size or color when a third metric matters.
- **Display guidance:** Label only selected points or rely on tooltips. Keep axis ranges fixed through the story.
- **Modules:** Register `ScatterChart`, `GridComponent`, `VisualMapComponent`, and `TooltipComponent`.
- **Pitfalls:** Dense scatter plots need either transparency, jitter, or aggregation; otherwise animation turns into visual noise.

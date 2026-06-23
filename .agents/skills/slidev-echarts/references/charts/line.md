# Line Charts In Slidev

- **Data shape:** Use ordered arrays keyed by time or sequence, such as `{ months, revenue: { baseline, scenario, target } }`. Keep x-axis categories stable across clicks.
- **Animation pattern:** Use stable `series.id` values and update only `data`, `areaStyle`, or labels from `$clicks`. Smooth lines and area fills make value changes legible.
- **Display guidance:** Keep no more than three lines on a slide unless the story is comparison-heavy. Use a dashed baseline and a stronger color for the active scenario.
- **Modules:** Register `LineChart`, `GridComponent`, `TooltipComponent`, and `LegendComponent`.
- **Pitfalls:** Do not reorder time categories during the story; it reads as a new chart instead of an animated trend update.

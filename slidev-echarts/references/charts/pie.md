# Pie Charts In Slidev

- **Data shape:** Use a small array of `{ name, value }` objects. Names must remain stable across updates so ECharts can match slices.
- **Animation pattern:** Animate between pie and donut radius, then update named slice values. Use `universalTransition` for part-to-whole morphs.
- **Display guidance:** Limit to four or five slices, use a legend when labels would collide, and prefer donut form when adding center text or visual breathing room.
- **Modules:** Register `PieChart`, `LegendComponent`, and `TooltipComponent`.
- **Pitfalls:** Do not use pie for precise close comparisons; switch to bar when slice differences are subtle.

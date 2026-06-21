# Heatmap Charts In Slidev

- **Data shape:** Use cells as `[xIndex, yIndex, value]` plus explicit x and y category arrays.
- **Animation pattern:** Update values through `$clicks` under a fixed `visualMap`. Reveal labels only in the final state.
- **Display guidance:** Use heatmaps for repeated categorical intersections such as day/hour activity.
- **Modules:** Register `HeatmapChart`, `GridComponent`, `VisualMapComponent`, and `TooltipComponent`.
- **Pitfalls:** Changing visualMap min/max across clicks makes color changes ambiguous; keep the scale stable.

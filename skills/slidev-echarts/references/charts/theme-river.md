# Theme River Charts In Slidev

- **Data shape:** Use rows `[date, value, streamName]`. Every stream should have entries for the same dates, with zero values when absent.
- **Animation pattern:** Generate deterministic rows from shared data and rebalance values across `$clicks`. Keep stream names stable for legend matching.
- **Display guidance:** Use theme river when topic or channel volume changes over time and relative shape matters.
- **Modules:** Register `ThemeRiverChart`, `SingleAxisComponent`, `LegendComponent`, and `TooltipComponent`.
- **Pitfalls:** Uneven dates or missing stream names cause confusing gaps; normalize rows before passing to ECharts.

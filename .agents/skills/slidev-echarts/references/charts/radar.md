# Radar Charts In Slidev

- **Data shape:** Use an indicator list with shared max values and one value vector per profile.
- **Animation pattern:** Update one profile vector toward a benchmark while keeping indicator order fixed. Area opacity helps viewers see the shape change.
- **Display guidance:** Use five to seven dimensions. Keep labels short and avoid negative values.
- **Modules:** Register `RadarChart`, `RadarComponent`, `LegendComponent`, and `TooltipComponent`.
- **Pitfalls:** Radar charts imply comparable dimensions; normalize metrics before plotting.

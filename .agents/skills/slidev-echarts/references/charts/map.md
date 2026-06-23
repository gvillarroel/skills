# Map Charts In Slidev

- **Data shape:** Use local GeoJSON plus `{ name, value }` rows whose names exactly match feature `properties.name`.
- **Animation pattern:** Call `echarts.registerMap(...)` before `setOption`, then update region values through `$clicks`. Use a stable `visualMap` range.
- **Display guidance:** Use maps only when spatial position matters. For synthetic demos, simple rectangular GeoJSON regions are enough to test rendering and animation.
- **Modules:** Register `MapChart`, `GeoComponent`, `VisualMapComponent`, and `TooltipComponent`.
- **Pitfalls:** Missing name matches render as empty regions; verify GeoJSON names before debugging color scales.

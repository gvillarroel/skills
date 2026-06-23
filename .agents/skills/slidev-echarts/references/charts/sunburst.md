# Sunburst Charts In Slidev

- **Data shape:** Use the same hierarchy shape as treemap: parent nodes with children and leaf values.
- **Animation pattern:** Update leaf values while preserving hierarchy names and level structure. Use `universalTransition` for radial segment morphs.
- **Display guidance:** Use sunburst for radial hierarchy when the top-level grouping is as important as leaf allocation.
- **Modules:** Register `SunburstChart` and `TooltipComponent`.
- **Pitfalls:** Long labels do not fit radial arcs; abbreviate or rely on tooltips for detail.

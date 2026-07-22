# Funnel Charts In Slidev

- **Data shape:** Use ordered stage objects with stable names and values.
- **Animation pattern:** Update stage values across `$clicks` while preserving order and stage names. Use `universalTransition` for width morphs.
- **Display guidance:** Sort descending and label segments inside when there is enough vertical room.
- **Modules:** Register `FunnelChart`, `LegendComponent`, and `TooltipComponent`.
- **Pitfalls:** Do not compare unrelated categories with a funnel; it implies sequential attrition.

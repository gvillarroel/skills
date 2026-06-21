# Treemap Charts In Slidev

- **Data shape:** Use a hierarchy array with values on leaves and group names on parents.
- **Animation pattern:** Update leaf values while preserving hierarchy names. `universalTransition` helps rectangle reflow feel intentional.
- **Display guidance:** Hide breadcrumbs for slide screenshots unless drill-down is required. Use upper labels for group names and simple leaf labels.
- **Modules:** Register `TreemapChart` and `TooltipComponent`.
- **Pitfalls:** Tiny rectangles produce unreadable labels; set label rules or aggregate small values into an "Other" group.

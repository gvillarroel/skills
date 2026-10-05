# Tree Charts In Slidev

- **Data shape:** Use one nested root object with `name`, optional `value`, and `children` arrays.
- **Animation pattern:** Keep branch structure stable across clicks and update leaf values or emphasis. Disable expand/collapse for presentation decks unless interaction is the point.
- **Display guidance:** Use left-to-right orientation for process or system stories when it yields short, traceable branches. Compare top-to-bottom for wide trees. Size spacing from complete labels and branch lanes; reduce surplus rank gaps after rendering while preserving readable type and endpoint identity. Keep all required facts and honor an explicit orientation.
- **Modules:** Register `TreeChart` and `TooltipComponent`.
- **Pitfalls:** Deep trees exceed slide space quickly; first repack and test at final slide scale. Use detail views or authorized grouping when needed, accounting for retained records and relationships. Treemap/sunburst suit allocation stories; they do not preserve the same branch-tracing task. Do not hide required labels or shrink type to force a fit.

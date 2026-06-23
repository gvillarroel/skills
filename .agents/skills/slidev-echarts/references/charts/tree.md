# Tree Charts In Slidev

- **Data shape:** Use one nested root object with `name`, optional `value`, and `children` arrays.
- **Animation pattern:** Keep branch structure stable across clicks and update leaf values or emphasis. Disable expand/collapse for presentation decks unless interaction is the point.
- **Display guidance:** Use left-to-right orientation for process or system stories. Keep labels concise and give the tree enough horizontal space.
- **Modules:** Register `TreeChart` and `TooltipComponent`.
- **Pitfalls:** Deep trees exceed slide space quickly; collapse detail into groups or switch to treemap/sunburst for allocation stories.

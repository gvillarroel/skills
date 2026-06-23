# Sankey Charts In Slidev

- **Data shape:** Use named nodes and directed links with source, target, and value.
- **Animation pattern:** Update link values while node names remain stable. Use gradient line color to reinforce direction.
- **Display guidance:** Use sankey for staged transfer or allocation. Keep node count low and align nodes to make the flow readable.
- **Modules:** Register `SankeyChart` and `TooltipComponent`.
- **Pitfalls:** Cycles and many cross-links reduce clarity; for network topology use graph instead.

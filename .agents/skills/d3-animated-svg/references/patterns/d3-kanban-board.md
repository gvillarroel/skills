# D3 Kanban Board

- **Pattern ID:** `d3-pattern-d3-kanban-board`
- **Gallery source ID:** `d3-kanban-board`
- **Family:** Diagram
- **Use when:** Columns and ticket cards recreated with D3 joins and staged reveal.
- **Renderer:** `renderD3KanbanBoard`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the pattern's core geometry and semantic color roles before changing labels or domain data.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderD3KanbanBoard() {
    const svg = prepareSvg("d3-kanban-board", "D3 kanban board", "Mermaid kanban data rendered as D3 columns and cards.");
    const columns = [
      { id: "Backlog", x: 32, color: palette.blue },
      { id: "In progress", x: 204, color: palette.orange },
      { id: "Done", x: 376, color: palette.green }
    ];
    const cards = [
      { col: "Backlog", title: "Define colors", ticket: "EX-101", owner: "Design", priority: "High" },
      { col: "Backlog", title: "Choose shapes", ticket: "EX-102", owner: "Docs", priority: "High" },
      { col: "In progress", title: "Create wrappers", ticket: "EX-201", owner: "Docs", priority: "Very High" },
      { col: "Done", title: "Allow examples", ticket: "EX-301", owner: "Maintainer", priority: "Low" }
    ];
    const colW = 150;
    const cardH = 70;
    const priorityColor = { "Very High": palette.red, High: palette.orange, Low: palette.green };
    const colById = new Map(columns.map(d => [d.id, d]));
    const colGroups = svg.append("g").selectAll("g.kanban-column").data(columns).join("g")
      .attr("class", "kanban-column")
      .attr("transform", d => `translate(${d.x},54)`);
    colGroups.append("rect").attr("width", colW).attr("height", 310).attr("rx", 10).attr("fill", palette.gray50).attr("stroke", palette.gray200);
    colGroups.append("rect").attr("width", colW).attr("height", 34).attr("rx", 10).attr("fill", d => d.color).attr("fill-opacity", .86);
    colGroups.append("text").attr("class", "reverse-label").attr("x", colW / 2).attr("y", 22).attr("text-anchor", "middle").attr("font-weight", 800).text(d => d.id);
    fadeIn(colGroups, .05, .35);
    const indexed = cards.map(card => {
      const preceding = cards.filter(d => d.col === card.col).indexOf(card);
      return { ...card, x: colById.get(card.col).x + 10, y: 104 + preceding * 92 };
    });
    const cardGroups = svg.append("g").selectAll("g.kanban-card").data(indexed).join("g")
      .attr("class", "kanban-card")
      .attr("transform", d => `translate(${d.x},${d.y})`);
    cardGroups.append("rect").attr("width", colW - 20).attr("height", cardH).attr("rx", 8).attr("fill", palette.surface).attr("stroke", palette.gray300).attr("stroke-width", 1.3);
    cardGroups.append("rect").attr("x", 0).attr("y", 0).attr("width", 6).attr("height", cardH).attr("rx", 3).attr("fill", d => priorityColor[d.priority]);
    cardGroups.append("text").attr("class", "mark-label").attr("x", 16).attr("y", 21).attr("font-weight", 800).text(d => d.title);
    cardGroups.append("text").attr("class", "caption").attr("x", 16).attr("y", 43).text(d => d.ticket);
    cardGroups.append("text").attr("class", "caption").attr("x", 16).attr("y", 61).text(d => `${d.owner} / ${d.priority}`);
    fadeIn(cardGroups, .18, .45);
  }
```

# Kanban Assignee Board

- **Pattern ID:** `d3-pattern-kanban-assignee-board`
- **Gallery source ID:** `kanban-assignee-board`
- **Family:** Diagram
- **Use when:** Five Kanban columns need compact task-title cards with colored two-letter assignee dots and a legend.
- **Renderer:** `renderKanbanAssigneeBoard`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the five-column board geometry, one visible title per task card, top-right assignee dots, and legend mapping each dot color to a person.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

```js
function renderKanbanAssigneeBoard() {
    const svg = prepareSvg("kanban-assignee-board", "Kanban assignee board", "Five Kanban columns with task cards, colored assignee dots, and a compact team legend.");
    const people = [
      { id: "AM", name: "Avery", color: palette.blue },
      { id: "BR", name: "Blair", color: palette.orange },
      { id: "CL", name: "Chen", color: palette.green },
      { id: "DN", name: "Dana", color: palette.purple },
      { id: "ES", name: "Ellis", color: palette.cyan }
    ];
    const personById = new Map(people.map(person => [person.id, person]));
    const columns = [
      { id: "Intake", x: 13, color: palette.blue },
      { id: "Ready", x: 120, color: palette.green },
      { id: "Build", x: 227, color: palette.orange },
      { id: "Review", x: 334, color: palette.purple },
      { id: "Ship", x: 441, color: palette.cyan }
    ];
    const tasks = [
      { col: "Intake", title: "Brief", assignees: ["AM", "BR"] },
      { col: "Intake", title: "Map", assignees: ["CL"] },
      { col: "Intake", title: "Risks", assignees: ["DN", "ES"] },
      { col: "Ready", title: "Spec", assignees: ["AM", "CL"] },
      { col: "Ready", title: "Copy", assignees: ["BR"] },
      { col: "Ready", title: "Flow", assignees: ["DN", "AM"] },
      { col: "Ready", title: "API", assignees: ["ES", "CL"] },
      { col: "Build", title: "Data", assignees: ["CL", "ES"] },
      { col: "Build", title: "UI", assignees: ["AM", "DN"] },
      { col: "Build", title: "Sync", assignees: ["BR", "CL", "ES"] },
      { col: "Build", title: "Tests", assignees: ["DN"] },
      { col: "Build", title: "Fixes", assignees: ["AM", "BR"] },
      { col: "Review", title: "QA", assignees: ["ES", "DN"] },
      { col: "Review", title: "Legal", assignees: ["BR"] },
      { col: "Review", title: "Perf", assignees: ["CL", "AM"] },
      { col: "Review", title: "Docs", assignees: ["DN", "BR"] },
      { col: "Ship", title: "Launch", assignees: ["AM", "ES"] },
      { col: "Ship", title: "Monitor", assignees: ["CL", "DN"] },
      { col: "Ship", title: "Retro", assignees: ["BR", "ES", "AM"] }
    ];
    const colW = 100;
    const colH = 306;
    const cardW = colW - 12;
    const cardH = 43;
    const cardGap = 8;
    const boardY = 72;

    const legend = svg.append("g").attr("class", "kanban-assignee-legend")
      .selectAll("g")
      .data(people)
      .join("g")
      .attr("transform", (_, i) => `translate(${22 + i * 106},30)`);
    legend.append("circle")
      .attr("fill", d => d.color)
      .attr("stroke", palette.surface)
      .attr("stroke-width", 1.7);
    grow(legend.selectAll("circle"), "r", 2, 10.2, .04, .35);
    legend.append("text")
      .attr("class", "reverse-label")
      .attr("x", 0)
      .attr("y", 3.5)
      .attr("text-anchor", "middle")
      .attr("font-size", 7.2)
      .attr("font-weight", 900)
      .text(d => d.id);
    legend.append("text")
      .attr("class", "caption")
      .attr("x", 16)
      .attr("y", 4)
      .attr("font-size", 10.5)
      .attr("font-weight", 800)
      .text(d => d.name);

    const colById = new Map(columns.map(column => [column.id, column]));
    const colGroups = svg.append("g").selectAll("g.kanban-assignee-column").data(columns).join("g")
      .attr("class", "kanban-assignee-column")
      .attr("transform", d => `translate(${d.x},${boardY})`);
    colGroups.append("rect")
      .attr("width", colW)
      .attr("height", colH)
      .attr("rx", 9)
      .attr("fill", palette.gray50)
      .attr("stroke", palette.gray200);
    colGroups.append("rect")
      .attr("width", colW)
      .attr("height", 30)
      .attr("rx", 9)
      .attr("fill", d => d.color)
      .attr("fill-opacity", .88);
    colGroups.append("text")
      .attr("class", "reverse-label")
      .attr("x", colW / 2)
      .attr("y", 20)
      .attr("text-anchor", "middle")
      .attr("font-size", 11)
      .attr("font-weight", 850)
      .text(d => d.id);
    fadeIn(colGroups, .08, .34);

    const counts = new Map();
    const indexed = tasks.map(task => {
      const order = counts.get(task.col) || 0;
      counts.set(task.col, order + 1);
      const column = colById.get(task.col);
      return {
        ...task,
        x: column.x + 6,
        y: boardY + 39 + order * (cardH + cardGap),
        order
      };
    });
    const cardGroups = svg.append("g").selectAll("g.kanban-assignee-card").data(indexed).join("g")
      .attr("class", "kanban-assignee-card")
      .attr("data-column", d => d.col)
      .attr("data-task-title", d => d.title)
      .attr("data-assignees", d => d.assignees.join(","))
      .attr("transform", d => `translate(${d.x},${d.y})`);
    cardGroups.append("rect")
      .attr("width", cardW)
      .attr("height", cardH)
      .attr("rx", 7)
      .attr("fill", palette.surface)
      .attr("stroke", palette.gray300)
      .attr("stroke-width", 1.15);
    cardGroups.append("text")
      .attr("class", "mark-label")
      .attr("x", 8)
      .attr("y", 35)
      .attr("font-size", 10.2)
      .attr("font-weight", 850)
      .text(d => d.title);
    cardGroups.append("line")
      .attr("x1", 8)
      .attr("x2", cardW - 8)
      .attr("y1", 24)
      .attr("y2", 24)
      .attr("stroke", palette.gray100)
      .attr("stroke-width", 1);
    cardGroups.each(function (task) {
      const stack = d3.select(this).append("g").attr("class", "assignee-dots");
      const dots = task.assignees.map((id, index) => ({
        ...personById.get(id),
        x: cardW - 10 - (task.assignees.length - 1 - index) * 18
      }));
      const dotGroups = stack.selectAll("g.assignee-dot").data(dots).join("g")
        .attr("class", "assignee-dot")
        .attr("transform", d => `translate(${d.x},13.5)`);
      dotGroups.append("circle")
        .attr("fill", d => d.color)
        .attr("stroke", palette.surface)
        .attr("stroke-width", 1.6);
      grow(dotGroups.selectAll("circle"), "r", 2, 9.4, .24 + task.order * .035, .34);
      dotGroups.append("text")
        .attr("fill", palette.surface)
        .attr("x", 0)
        .attr("y", 2.9)
        .attr("text-anchor", "middle")
        .attr("font-size", 6.4)
        .attr("font-weight", 900)
        .text(d => d.id);
    });
    fadeIn(cardGroups, .16, .42);
  }
```

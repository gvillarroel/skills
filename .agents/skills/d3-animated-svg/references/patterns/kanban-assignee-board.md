# Kanban Assignee Board

- **Pattern ID:** `d3-pattern-kanban-assignee-board`
- **Gallery source ID:** `kanban-assignee-board`
- **Family:** Diagram
- **Use when:** Five Kanban columns need compact task-title cards with colored two-letter assignee dots and a legend.
- **Renderer:** `renderKanbanAssigneeBoard`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- Keep data deterministic and inline small datasets.
- Preserve the five-column board geometry, one visible title per task card with 1-3 wrapped lines, content-sized card heights, square card and column edges, bottom-right floating assignee dots, and legend mapping each dot color to a person.
- Show the board scaffold first: columns and the assignee legend reveal before task cards.
- Reveal task cards one at a time in left-to-right board order. Expose `data-column-order`, `data-task-order`, `data-reveal-order`, and `data-reveal-begin-ms` on cards so browser checks can audit the sequence.
- Use SVG-native animation for standalone output; do not leave runtime D3 or CDN dependencies in a self-contained deliverable.
- Include an SVG `<title>`, `<desc>`, stable `viewBox`, and final-state geometry.

## Source Excerpt

The excerpt below is the compact renderer source for this pattern. If it references helpers such as `prepareSvg`, `fadeIn`, `revealIn`, `grow`, `drawPath`, `palette`, `ramps`, `axisBottom`, or `axisLeft`, read `references/shared-renderer-helpers.md` and recreate only the needed helper behavior in the final artifact.

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
      { id: "Intake", x: 8, color: palette.blue },
      { id: "Ready", x: 117, color: palette.green },
      { id: "Build", x: 226, color: palette.orange },
      { id: "Review", x: 335, color: palette.purple },
      { id: "Ship", x: 444, color: palette.cyan }
    ];
    const tasks = [
      { col: "Intake", title: "Brief", assignees: ["AM", "BR"] },
      { col: "Intake", title: "Map release\nnotes draft", assignees: ["CL"], expectedLines: 2 },
      { col: "Intake", title: "Risks", assignees: ["DN", "ES"] },
      { col: "Ready", title: "Spec", assignees: ["AM", "CL"] },
      { col: "Ready", title: "Copy", assignees: ["BR"] },
      { col: "Ready", title: "Flow", assignees: ["DN", "AM"] },
      { col: "Ready", title: "API", assignees: ["ES", "CL"] },
      { col: "Build", title: "Data", assignees: ["CL", "ES"] },
      { col: "Build", title: "UI", assignees: ["AM", "DN"] },
      { col: "Build", title: "Reconcile\nmobile check\nstates", assignees: ["BR", "CL", "ES"], expectedLines: 3 },
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
    const colW = 105;
    const headerH = 24;
    const cardW = colW - 8;
    const cardGap = 4;
    const boardY = 48;
    const titleX = 6;
    const titleY = 12.4;
    const titleLineHeight = 10.1;
    const titleFontSize = 9.7;
    const titleFontWeight = 850;
    const titleMaxLines = 3;
    const titleFullWidth = cardW - titleX * 2;
    const titleDotSafeWidth = cardW - 60;
    const cardHeightForLines = lineCount => 34 + Math.min(titleMaxLines, Math.max(1, lineCount)) * 8;

    function fitKanbanTitleLine(probe, value, width) {
      let fitted = value.trim();
      probe.text(fitted);
      if (probe.node().getComputedTextLength() <= width) return fitted;
      while (fitted.length > 1) {
        fitted = fitted.slice(0, -1).trimEnd();
        probe.text(`${fitted}...`);
        if (probe.node().getComputedTextLength() <= width) return `${fitted}...`;
      }
      return "...";
    }

    const titleProbe = svg.append("text")
      .attr("class", "mark-label")
      .attr("x", -999)
      .attr("y", -999)
      .attr("font-size", titleFontSize)
      .attr("font-weight", titleFontWeight)
      .attr("visibility", "hidden");

    function measureKanbanTitle(title) {
      const widthForLine = index => index >= titleMaxLines - 1 ? titleDotSafeWidth : titleFullWidth;
      const raw = String(title);
      let lines;
      if (raw.includes("\n")) {
        const hardLines = raw.split(/\n/).map(line => line.trim()).filter(Boolean);
        lines = hardLines.slice(0, titleMaxLines);
        if (hardLines.length > titleMaxLines) {
          lines[titleMaxLines - 1] = `${lines[titleMaxLines - 1]} ${hardLines.slice(titleMaxLines).join(" ")}`;
        }
        lines = lines.map((line, index) => fitKanbanTitleLine(titleProbe, line, widthForLine(index)));
      } else {
        const words = raw.split(/\s+/).filter(Boolean);
        lines = [];
        let current = "";
        for (let i = 0; i < words.length; i += 1) {
          const candidate = current ? `${current} ${words[i]}` : words[i];
          titleProbe.text(candidate);
          if (!current || titleProbe.node().getComputedTextLength() <= widthForLine(lines.length)) {
            current = candidate;
          } else {
            lines.push(current);
            current = words[i];
            if (lines.length === titleMaxLines - 1) {
              current = [current, ...words.slice(i + 1)].join(" ");
              break;
            }
          }
        }
        if (current && lines.length < titleMaxLines) lines.push(current);
        lines = lines.map((line, index) => fitKanbanTitleLine(titleProbe, line, widthForLine(index)));
      }
      return lines.length ? lines : [""];
    }

    const sizedTasks = tasks.map(task => {
      const lines = measureKanbanTitle(task.title);
      return {
        ...task,
        titleLines: lines,
        lineCount: lines.length,
        cardH: cardHeightForLines(lines.length)
      };
    });
    titleProbe.remove();

    const tasksByColumn = d3.group(sizedTasks, task => task.col);
    const columnHeight = column => {
      const columnTasks = tasksByColumn.get(column.id) || [];
      return headerH + 16 + d3.sum(columnTasks, task => task.cardH) + Math.max(0, columnTasks.length - 1) * cardGap;
    };

    function wrapKanbanTitle(text, lines) {
      text.attr("data-line-count", lines.length)
        .selectAll("tspan")
        .data(lines)
        .join("tspan")
        .attr("x", titleX)
        .attr("y", (_, index) => titleY + index * titleLineHeight)
        .text(d => d);
    }

    const legendGroup = svg.append("g")
      .attr("class", "kanban-assignee-legend")
      .attr("data-legend", "assignee");
    const legend = legendGroup
      .selectAll("g")
      .data(people)
      .join("g")
      .attr("transform", (_, i) => `translate(${22 + i * 106},22)`);
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
    revealIn(legendGroup, .06, .3);

    const colById = new Map(columns.map(column => [column.id, column]));
    const columnOrder = new Map(columns.map((column, index) => [column.id, index]));
    const colGroups = svg.append("g").selectAll("g.kanban-assignee-column").data(columns).join("g")
      .attr("class", "kanban-assignee-column")
      .attr("data-column-order", d => columnOrder.get(d.id))
      .attr("transform", d => `translate(${d.x},${boardY})`);
    colGroups.append("rect")
      .attr("width", colW)
      .attr("height", columnHeight)
      .attr("fill", palette.gray50)
      .attr("stroke", palette.gray200);
    colGroups.append("rect")
      .attr("width", colW)
      .attr("height", headerH)
      .attr("fill", d => d.color)
      .attr("fill-opacity", .88);
    colGroups.append("text")
      .attr("class", "reverse-label")
      .attr("x", colW / 2)
      .attr("y", 16)
      .attr("text-anchor", "middle")
      .attr("font-size", 11)
      .attr("font-weight", 850)
      .text(d => d.id);
    revealIn(colGroups, (_, i) => .08 + i * .035, .34);

    const counts = new Map();
    const offsets = new Map();
    const indexed = sizedTasks.map(task => {
      const order = counts.get(task.col) || 0;
      const offset = offsets.get(task.col) || 0;
      counts.set(task.col, order + 1);
      offsets.set(task.col, offset + task.cardH + cardGap);
      const column = colById.get(task.col);
      return {
        ...task,
        x: column.x + 4,
        y: boardY + headerH + 8 + offset,
        columnOrder: columnOrder.get(task.col),
        order
      };
    });
    [...indexed]
      .sort((a, b) => d3.ascending(a.x, b.x) || d3.ascending(a.y, b.y))
      .forEach((task, revealOrder) => {
        task.revealOrder = revealOrder;
      });
    const cardRevealStart = .66;
    const cardRevealGap = .115;
    const cardGroups = svg.append("g").selectAll("g.kanban-assignee-card").data(indexed).join("g")
      .attr("class", "kanban-assignee-card")
      .attr("data-column", d => d.col)
      .attr("data-column-order", d => d.columnOrder)
      .attr("data-task-order", d => d.order)
      .attr("data-reveal-order", d => d.revealOrder)
      .attr("data-reveal-begin-ms", d => Math.round((cardRevealStart + d.revealOrder * cardRevealGap) * 1000))
      .attr("data-task-title", d => d.title)
      .attr("data-expected-lines", d => d.expectedLines || d.lineCount)
      .attr("data-card-height", d => d.cardH)
      .attr("data-assignees", d => d.assignees.join(","))
      .attr("transform", d => `translate(${d.x},${d.y})`);
    cardGroups.append("rect")
      .attr("width", cardW)
      .attr("height", d => d.cardH)
      .attr("fill", palette.surface)
      .attr("stroke", palette.gray300)
      .attr("stroke-width", 1.15);
    cardGroups.append("text")
      .attr("class", "mark-label")
      .attr("x", titleX)
      .attr("font-size", titleFontSize)
      .attr("font-weight", titleFontWeight)
      .each(function (task) {
        wrapKanbanTitle(d3.select(this), task.titleLines);
      });
    cardGroups.each(function (task) {
      const stack = d3.select(this).append("g").attr("class", "assignee-dots");
      const dots = task.assignees.map((id, index) => ({
        ...personById.get(id),
        x: cardW - 12 - (task.assignees.length - 1 - index) * 18
      }));
      const dotGroups = stack.selectAll("g.assignee-dot").data(dots).join("g")
        .attr("class", "assignee-dot")
        .attr("transform", d => `translate(${d.x},${task.cardH - 11.5})`);
      dotGroups.append("circle")
        .attr("fill", d => d.color)
        .attr("stroke", palette.surface)
        .attr("stroke-width", 1.6);
      grow(dotGroups.selectAll("circle"), "r", 2, 9.4, cardRevealStart + task.revealOrder * cardRevealGap + .2, .32);
      dotGroups.append("text")
        .attr("fill", palette.surface)
        .attr("x", 0)
        .attr("y", 2.9)
        .attr("text-anchor", "middle")
        .attr("font-size", 6.4)
        .attr("font-weight", 900)
        .text(d => d.id);
    });
    revealIn(cardGroups, d => cardRevealStart + d.revealOrder * cardRevealGap, .32);
  }
```

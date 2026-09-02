const specs = {
  billing: {
    core: "$",
    color: "#9e1b32",
    inputs: ["input", "cache", "retry", "ctx"],
    parts: ["prompt", "answer", "tools"],
    outputs: ["credits", "plan"],
    rows: [
      { label: "in", color: "#007298", count: 7 },
      { label: "out", color: "#652f6c", count: 6 },
      { label: "cache", color: "#45842a", count: 4 },
      { label: "retry", color: "#e77204", count: 5 }
    ]
  },
  evaluation: {
    core: "Eval",
    color: "#007298",
    inputs: ["cases", "trace", "rubric"],
    parts: ["model", "grader", "human"],
    outputs: ["score", "regress"],
    rows: [
      { label: "pass", color: "#45842a", count: 8 },
      { label: "fail", color: "#9e1b32", count: 3 },
      { label: "drift", color: "#e77204", count: 5 },
      { label: "ship", color: "#652f6c", count: 6 }
    ]
  },
  agent: {
    core: "Agent",
    color: "#652f6c",
    inputs: ["goal", "state", "memory"],
    parts: ["LLM", "tool", "observe"],
    outputs: ["step", "result"],
    rows: [
      { label: "plan", color: "#007298", count: 5 },
      { label: "call", color: "#652f6c", count: 7 },
      { label: "obs", color: "#e77204", count: 6 },
      { label: "done", color: "#45842a", count: 4 }
    ]
  },
  guardrail: {
    core: "Guard",
    color: "#45842a",
    inputs: ["user", "tool", "data"],
    parts: ["policy", "filter", "log"],
    outputs: ["allow", "block", "redact"],
    rows: [
      { label: "ok", color: "#45842a", count: 8 },
      { label: "risk", color: "#e77204", count: 5 },
      { label: "stop", color: "#9e1b32", count: 4 },
      { label: "audit", color: "#007298", count: 6 }
    ]
  },
  harness: {
    core: "Harness",
    color: "#333e48",
    inputs: ["context", "tools", "policy"],
    parts: ["loop", "state", "eval"],
    outputs: ["trace", "control"],
    rows: [
      { label: "ctx", color: "#007298", count: 7 },
      { label: "tool", color: "#652f6c", count: 5 },
      { label: "env", color: "#e77204", count: 6 },
      { label: "log", color: "#45842a", count: 8 }
    ]
  },
  hook: {
    core: "Hook",
    color: "#e77204",
    inputs: ["event", "cmd", "call"],
    parts: ["pre", "check", "post"],
    outputs: ["allow", "deny", "log"],
    rows: [
      { label: "start", color: "#007298", count: 4 },
      { label: "pre", color: "#e77204", count: 6 },
      { label: "post", color: "#652f6c", count: 5 },
      { label: "log", color: "#45842a", count: 7 }
    ]
  },
  plugin: {
    core: "Plugin",
    color: "#9e1b32",
    inputs: ["skill", "agent", "hook"],
    parts: ["manifest", "assets", "MCP"],
    outputs: ["install", "share"],
    rows: [
      { label: "skill", color: "#007298", count: 5 },
      { label: "agent", color: "#652f6c", count: 5 },
      { label: "hook", color: "#e77204", count: 5 },
      { label: "mcp", color: "#45842a", count: 5 }
    ]
  },
  skill: {
    core: "Skill",
    color: "#007298",
    inputs: ["trigger", "task", "repo"],
    parts: ["SKILL.md", "refs", "scripts"],
    outputs: ["context", "action"],
    rows: [
      { label: "load", color: "#007298", count: 7 },
      { label: "refs", color: "#652f6c", count: 4 },
      { label: "script", color: "#e77204", count: 5 },
      { label: "work", color: "#45842a", count: 6 }
    ]
  },
  mcp: {
    core: "MCP",
    color: "#652f6c",
    inputs: ["host", "client", "auth"],
    parts: ["server", "tools", "resources"],
    outputs: ["data", "action"],
    rows: [
      { label: "tool", color: "#007298", count: 7 },
      { label: "res", color: "#45842a", count: 6 },
      { label: "auth", color: "#e77204", count: 4 },
      { label: "result", color: "#652f6c", count: 8 }
    ]
  },
  alternatives: {
    core: "Choice",
    color: "#333e48",
    inputs: ["task", "risk", "team"],
    parts: ["cost", "fit", "lock"],
    outputs: ["plan", "mix"],
    rows: [
      { label: "cost", color: "#9e1b32", count: 4 },
      { label: "speed", color: "#007298", count: 7 },
      { label: "fit", color: "#45842a", count: 6 },
      { label: "risk", color: "#e77204", count: 5 }
    ]
  }
};

function text(g, label, x, y, ctx, options = {}) {
  ctx.drawHookText(g, label, x, y, {
    size: options.size ?? 18,
    weight: options.weight ?? 800,
    fill: options.fill ?? ctx.palette.brandNeutral,
    opacity: options.opacity ?? 1,
    anchor: options.anchor,
    baseline: options.baseline
  });
}

function arrow(g, from, to, color, opacity, width = 3) {
  g.append("line")
    .attr("x1", from.x)
    .attr("y1", from.y)
    .attr("x2", to.x)
    .attr("y2", to.y)
    .attr("stroke", color)
    .attr("stroke-width", width)
    .attr("stroke-linecap", "round")
    .attr("opacity", opacity);
  const angle = Math.atan2(to.y - from.y, to.x - from.x);
  const size = 12;
  g.append("path")
    .attr("d", [
      `M${to.x},${to.y}`,
      `L${to.x - Math.cos(angle - Math.PI / 6) * size},${to.y - Math.sin(angle - Math.PI / 6) * size}`,
      `L${to.x - Math.cos(angle + Math.PI / 6) * size},${to.y - Math.sin(angle + Math.PI / 6) * size}`,
      "Z"
    ].join(" "))
    .attr("fill", color)
    .attr("opacity", opacity);
}

function node(g, x, y, w, h, label, color, ctx, options = {}) {
  const opacity = options.opacity ?? 1;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", options.rx ?? 8)
    .attr("fill", options.fill ?? "#ffffff")
    .attr("stroke", options.stroke ?? color)
    .attr("stroke-width", options.strokeWidth ?? 2.4)
    .attr("opacity", opacity);
  text(g, label, x + w / 2, y + h / 2 + 1, ctx, {
    size: options.size ?? 18,
    weight: options.weight ?? 850,
    fill: options.textFill ?? color,
    opacity
  });
}

function drawCore(g, spec, t, ctx) {
  const { palette, easeOut } = ctx;
  const box = { x: 505, y: 194, w: 270, h: 270 };
  const active = easeOut((t - 0.6) / 1.4);
  g.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", spec.color)
    .attr("stroke-width", 3.8)
    .attr("opacity", 0.97);
  text(g, spec.core, box.x + box.w / 2, box.y + 115, ctx, {
    size: spec.core.length > 6 ? 34 : 52,
    weight: 900,
    fill: palette.brandNeutral,
    opacity: 0.96
  });
  const layers = [3, 4, 3];
  const nodePositions = layers.map((count, layer) => {
    const x = box.x + 78 + layer * 56;
    const startY = box.y + 177 + (4 - count) * 9;
    return Array.from({ length: count }, (_, index) => ({ x, y: startY + index * 24 }));
  });
  for (let layer = 0; layer < nodePositions.length - 1; layer += 1) {
    nodePositions[layer].forEach((from, fromIndex) => {
      nodePositions[layer + 1].forEach((to, toIndex) => {
        g.append("line")
          .attr("x1", from.x)
          .attr("y1", from.y)
          .attr("x2", to.x)
          .attr("y2", to.y)
          .attr("stroke", (fromIndex + toIndex + layer) % 3 === 0 ? spec.color : palette.gray400)
          .attr("stroke-width", 1.3)
          .attr("opacity", 0.22 + active * 0.28);
      });
    });
  }
  nodePositions.flat().forEach((item, index) => {
    const pulse = (Math.sin((ctx.seconds ?? 0) * 1.9 + index * 0.8) + 1) / 2;
    g.append("circle")
      .attr("cx", item.x)
      .attr("cy", item.y)
      .attr("r", 4.8 + pulse * 1.2)
      .attr("fill", index % 3 === 0 ? spec.color : palette.gray600)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.5)
      .attr("opacity", 0.55 + active * 0.2 + pulse * 0.12);
  });
  return box;
}

function drawAmbientFlow(g, coreBox, spec, ctx) {
  const { palette, seconds, easeInOut } = ctx;
  const colors = spec.rows.map((row) => row.color);
  const lanes = [
    { from: { x: 310, y: 120 }, to: { x: 970, y: 120 }, arc: 0 },
    { from: { x: 970, y: 610 }, to: { x: 310, y: 610 }, arc: 0 },
    { from: { x: coreBox.x - 42, y: coreBox.y + 64 }, to: { x: coreBox.x + coreBox.w + 42, y: coreBox.y + 64 }, arc: -18 },
    { from: { x: coreBox.x + coreBox.w + 42, y: coreBox.y + 204 }, to: { x: coreBox.x - 42, y: coreBox.y + 204 }, arc: 18 }
  ];
  lanes.forEach((lane, laneIndex) => {
    d3.range(3).forEach((index) => {
      const raw = ((seconds * (0.06 + laneIndex * 0.012) + index / 3 + laneIndex * 0.11) % 1);
      const p = easeInOut(raw);
      const x = lane.from.x + (lane.to.x - lane.from.x) * p;
      const y = lane.from.y + (lane.to.y - lane.from.y) * p + Math.sin(p * Math.PI) * lane.arc;
      g.append("rect")
        .attr("x", x - 5)
        .attr("y", y - 5)
        .attr("width", 10)
        .attr("height", 10)
        .attr("rx", 3)
        .attr("fill", colors[(index + laneIndex) % colors.length] ?? palette.blue)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.1)
        .attr("opacity", 0.36);
    });
  });
}

function drawMatrix(g, x, y, cols, rows, progress, colors, ctx) {
  const { palette, easeOut } = ctx;
  const cell = 20;
  const gap = 7;
  const activeCells = Math.floor(cols * rows * easeOut(progress));
  d3.range(cols * rows).forEach((index) => {
    const active = index < activeCells;
    g.append("rect")
      .attr("x", x + (index % cols) * (cell + gap))
      .attr("y", y + Math.floor(index / cols) * (cell + gap))
      .attr("width", cell)
      .attr("height", cell)
      .attr("rx", 4)
      .attr("fill", active ? colors[index % colors.length] : palette.gray100)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.4)
      .attr("opacity", active ? 0.76 : 0.58);
  });
}

function drawMovingSquares(g, from, to, colors, t, ctx, options = {}) {
  const { easeInOut } = ctx;
  const count = options.count ?? 5;
  d3.range(count).forEach((index) => {
    const raw = ((t * (options.speed ?? 0.22) + index / count) % 1);
    const p = easeInOut(raw);
    const x = from.x + (to.x - from.x) * p;
    const y = from.y + (to.y - from.y) * p + Math.sin(p * Math.PI) * (options.arc ?? 0);
    g.append("rect")
      .attr("x", x - 7)
      .attr("y", y - 7)
      .attr("width", 14)
      .attr("height", 14)
      .attr("rx", 4)
      .attr("fill", colors[index % colors.length])
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.4)
      .attr("opacity", options.opacity ?? 0.82);
  });
}

function drawParts(g, spec, t, ctx) {
  const { palette, easeOut } = ctx;
  const reveal = easeOut((t - 2.2) / 4.0);
  if (reveal <= 0.01) return;
  spec.parts.forEach((part, index) => {
    const x = 542 + index * 68;
    const y = 514;
    node(g, x, y, 60, 42, part, [palette.blue, palette.orange, palette.green][index % 3], ctx, {
      opacity: reveal,
      size: part.length > 5 ? 12 : 15,
      fill: "#ffffff",
      strokeWidth: 2
    });
  });
}

function drawSideNodes(g, spec, t, ctx) {
  const { palette, easeOut } = ctx;
  const leftP = easeOut((t - 0.8) / 2.6);
  const rightP = easeOut((t - 5.4) / 3.2);
  spec.inputs.forEach((label, index) => {
    const y = 154 + index * 76;
    node(g, 96, y, 150, 46, label, [palette.blue, palette.green, palette.orange, palette.purple][index % 4], ctx, {
      opacity: leftP,
      fill: "#ffffff",
      size: 17
    });
  });
  spec.outputs.forEach((label, index) => {
    const y = 174 + index * 88;
    node(g, 1040, y, 150, 50, label, [palette.green, palette.red, palette.blue][index % 3], ctx, {
      opacity: rightP,
      fill: "#ffffff",
      size: 17
    });
  });
}

function drawRows(g, spec, t, ctx) {
  const { palette, easeOut } = ctx;
  const rowsP = easeOut((t - 8.5) / 7.0);
  const group = g.append("g").attr("opacity", rowsP);
  spec.rows.forEach((row, rowIndex) => {
    const y = 544 + rowIndex * 34;
    text(group, row.label, 92, y + 10, ctx, {
      anchor: "start",
      size: 15,
      weight: 840,
      fill: palette.gray700,
      opacity: rowsP
    });
    d3.range(12).forEach((index) => {
      const active = index < Math.floor(row.count * rowsP + 0.001);
      group.append("rect")
        .attr("x", 176 + index * 29)
        .attr("y", y)
        .attr("width", 20)
        .attr("height", 20)
        .attr("rx", 4)
        .attr("fill", active ? row.color : palette.gray100)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.4)
        .attr("opacity", active ? 0.86 : 0.62);
    });
  });
}

function drawLoop(g, coreBox, spec, t, ctx) {
  const { palette, easeOut, clamp } = ctx;
  const loopP = easeOut((t - 7.2) / 4.2);
  if (loopP <= 0.01) return;
  const group = g.append("g").attr("opacity", loopP);
  const path = `M${coreBox.x + coreBox.w + 28},${coreBox.y + 82} C${894},${118} ${954},${520} ${coreBox.x + coreBox.w - 10},${coreBox.y + coreBox.h + 18} C${506},${628} ${388},${438} ${coreBox.x - 30},${coreBox.y + 188}`;
  group.append("path")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", spec.color)
    .attr("stroke-width", 3.2)
    .attr("stroke-dasharray", "12 11")
    .attr("opacity", 0.34);
  drawMovingSquares(group, { x: coreBox.x + coreBox.w + 34, y: coreBox.y + 84 }, { x: coreBox.x - 30, y: coreBox.y + 190 }, [spec.color, palette.blue, palette.orange], t, ctx, {
    count: 6,
    speed: 0.13,
    arc: 84,
    opacity: 0.74
  });
  d3.range(3).forEach((index) => {
    const p = clamp((t - 13.4 - index * 0.24) / 1.8, 0, 1);
    if (p <= 0.01 || p >= 1) return;
    group.append("circle")
      .attr("cx", coreBox.x + coreBox.w / 2)
      .attr("cy", coreBox.y + coreBox.h / 2)
      .attr("r", 92 + p * 80)
      .attr("fill", "none")
      .attr("stroke", [palette.blue, palette.green, palette.orange][index])
      .attr("stroke-width", 3)
      .attr("opacity", (1 - p) * 0.22);
  });
}

function drawComparison(g, spec, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeOut((t - 0.5) / 5.8);
  const group = g.append("g").attr("opacity", p);
  const base = { x: 930, y: 516 };
  spec.rows.slice(0, 4).forEach((row, index) => {
    const h = 42 + row.count * 9 * p;
    group.append("rect")
      .attr("x", base.x + index * 58)
      .attr("y", base.y - h)
      .attr("width", 34)
      .attr("height", h)
      .attr("rx", 6)
      .attr("fill", row.color)
      .attr("opacity", 0.72);
  });
  drawMatrix(group, 82, 128, 7, 6, p, spec.rows.map((row) => row.color), ctx);
  drawMovingSquares(group, { x: 320, y: 214 }, { x: 500, y: 320 }, spec.rows.map((row) => row.color), t, ctx, {
    count: 7,
    speed: 0.18,
    arc: -34,
    opacity: 0.62
  });
}

function drawHandoff(g, spec, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeOut((t - 1.0) / 5.5);
  const group = g.append("g").attr("opacity", p);
  const box = { x: 910, y: 166, w: 250, h: 370 };
  group.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 18)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 2)
    .attr("opacity", 0.96);
  spec.rows.forEach((row, rowIndex) => {
    const y = box.y + 46 + rowIndex * 58;
    d3.range(row.count).forEach((index) => {
      const active = index < Math.floor(row.count * easeOut((t - 2.0 - rowIndex * 0.45) / 2.6));
      group.append("rect")
        .attr("x", box.x + 32 + index * 20)
        .attr("y", y)
        .attr("width", 14)
        .attr("height", 14)
        .attr("rx", 4)
        .attr("fill", active ? row.color : palette.gray100)
        .attr("opacity", active ? 0.84 : 0.58);
    });
  });
  text(group, spec.core === "$" ? "$" : "+", box.x + box.w / 2, box.y + box.h - 72, ctx, {
    size: 54,
    weight: 900,
    fill: spec.color,
    opacity: 0.92
  });
}

export function drawGenericConceptVisualOnly(g, concept, ctx) {
  const spec = specs[concept.kind] ?? specs.alternatives;
  const { beat, sceneProgress, seconds, palette, easeOut } = ctx;
  const beatIndex = ["hook", "definition", "mechanism", "implication", "handoff"].indexOf(beat.id);
  const t = sceneProgress * (beat.end - beat.start);
  const sceneGroup = g.append("g");
  const coreBox = drawCore(sceneGroup, spec, t + beatIndex * 0.5, ctx);
  drawAmbientFlow(sceneGroup, coreBox, spec, ctx);

  if (beatIndex === 0) {
    drawSideNodes(sceneGroup, spec, t, ctx);
    drawMovingSquares(sceneGroup, { x: 246, y: 230 }, { x: coreBox.x, y: coreBox.y + 118 }, spec.rows.map((row) => row.color), t, ctx, {
      count: 6,
      speed: 0.28,
      arc: -24
    });
    drawMatrix(sceneGroup, 86, 454, 7, 4, easeOut(t / 9.0), spec.rows.map((row) => row.color), ctx);
    arrow(sceneGroup, { x: 268, y: 260 }, { x: coreBox.x - 12, y: coreBox.y + 136 }, spec.color, 0.34, 3);
    return;
  }

  if (beatIndex === 1) {
    drawSideNodes(sceneGroup, spec, t + 4, ctx);
    drawParts(sceneGroup, spec, t, ctx);
    drawMatrix(sceneGroup, 86, 178, 6, 6, easeOut((t - 3.0) / 9.0), spec.rows.map((row) => row.color), ctx);
    arrow(sceneGroup, { x: 270, y: 258 }, { x: coreBox.x - 12, y: coreBox.y + 126 }, spec.color, 0.36, 3);
    arrow(sceneGroup, { x: coreBox.x + coreBox.w + 12, y: coreBox.y + 126 }, { x: 1028, y: 234 }, palette.green, 0.3, 3);
    return;
  }

  if (beatIndex === 2) {
    drawSideNodes(sceneGroup, spec, t + 7, ctx);
    drawParts(sceneGroup, spec, t + 5, ctx);
    drawLoop(sceneGroup, coreBox, spec, t, ctx);
    drawRows(sceneGroup, spec, t, ctx);
    arrow(sceneGroup, { x: 250, y: 230 }, { x: coreBox.x - 12, y: coreBox.y + 116 }, spec.color, 0.32, 3);
    arrow(sceneGroup, { x: coreBox.x + coreBox.w + 14, y: coreBox.y + 116 }, { x: 1030, y: 226 }, palette.green, 0.32, 3);
    return;
  }

  if (beatIndex === 3) {
    drawComparison(sceneGroup, spec, t, ctx);
    drawRows(sceneGroup, spec, t + 6, ctx);
    arrow(sceneGroup, { x: 280, y: 318 }, { x: coreBox.x - 12, y: coreBox.y + 154 }, spec.color, 0.32, 3);
    arrow(sceneGroup, { x: coreBox.x + coreBox.w + 14, y: coreBox.y + 154 }, { x: 904, y: 402 }, palette.purple, 0.3, 3);
    return;
  }

  drawSideNodes(sceneGroup, spec, t + 10, ctx);
  drawParts(sceneGroup, spec, t + 8, ctx);
  drawHandoff(sceneGroup, spec, t, ctx);
  drawMovingSquares(sceneGroup, { x: 246, y: 252 }, { x: coreBox.x - 8, y: coreBox.y + 126 }, spec.rows.map((row) => row.color), seconds, ctx, {
    count: 6,
    speed: 0.18,
    arc: -18,
    opacity: 0.72
  });
  drawMovingSquares(sceneGroup, { x: coreBox.x + coreBox.w + 8, y: coreBox.y + 134 }, { x: 910, y: 312 }, spec.rows.map((row) => row.color), seconds, ctx, {
    count: 6,
    speed: 0.16,
    arc: -36,
    opacity: 0.76
  });
}

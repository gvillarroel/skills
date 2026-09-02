import { drawLlmModelBox } from "./llm-model-box.js";

export const evalColors = {
  tokens: ["#007298", "#652f6c", "#45842a", "#e77204", "#9e1b32", "#f1c319"],
  pass: "#45842a",
  fail: "#9e1b32",
  cost: "#e77204",
  chance: "#652f6c",
  context: "#007298"
};

export function p01(t, start, duration, ctx) {
  return ctx.clamp((t - start) / duration, 0, 1);
}

export function easeP(t, start, duration, ctx) {
  return ctx.easeOut(p01(t, start, duration, ctx));
}

export function windowP(t, start, end, ctx, ramp = 0.5) {
  const rise = ctx.easeInOut(p01(t, start, ramp, ctx));
  const fall = 1 - ctx.easeInOut(p01(t, end, ramp, ctx));
  return ctx.clamp(rise * fall, 0, 1);
}

export function drawText(g, label, x, y, ctx, options = {}) {
  if ((options.opacity ?? 1) <= 0.01) return null;
  return ctx.drawHookText(g, label, x, y, {
    anchor: options.anchor,
    baseline: options.baseline,
    size: options.size ?? 18,
    weight: options.weight ?? 820,
    fill: options.fill ?? ctx.palette.brandNeutral,
    opacity: options.opacity ?? 1
  });
}

export function drawIcon(g, icon, x, y, ctx, options = {}) {
  if ((options.opacity ?? 1) <= 0.01) return null;
  return g.append("text")
    .attr("x", x)
    .attr("y", y)
    .attr("text-anchor", "middle")
    .attr("dominant-baseline", "middle")
    .attr("font-family", "'Material Symbols Rounded'")
    .attr("font-size", options.size ?? 28)
    .attr("font-weight", options.weight ?? 700)
    .attr("fill", options.fill ?? ctx.palette.brandNeutral)
    .attr("opacity", options.opacity ?? 1)
    .text(icon);
}

export function drawToken(g, x, y, w, h, color, ctx, options = {}) {
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const group = g.append("g").attr("opacity", opacity);
  group.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", options.rx ?? Math.min(7, h / 2))
    .attr("fill", options.fill ?? color)
    .attr("stroke", options.stroke ?? "#ffffff")
    .attr("stroke-width", options.strokeWidth ?? 1.6)
    .attr("fill-opacity", options.fillOpacity ?? 0.9);
  if (options.label) {
    drawText(group, options.label, x + w / 2, y + h / 2 + 1, ctx, {
      size: options.labelSize ?? 13,
      weight: 850,
      fill: options.textFill ?? "#ffffff",
      opacity: 0.98
    });
  }
}

export function drawPacketGrid(g, box, count, ctx, options = {}) {
  const { palette, easeOut, clamp } = ctx;
  const cols = options.cols ?? 6;
  const rows = options.rows ?? 2;
  const cell = options.cell ?? 16;
  const gap = options.gap ?? 6;
  const opacity = options.opacity ?? 1;
  const color = options.color ?? ((index) => evalColors.tokens[index % evalColors.tokens.length]);
  const total = cols * rows;
  for (let index = 0; index < total; index += 1) {
    const active = index < count;
    const reveal = active ? easeOut(clamp(count - index, 0, 5) / 5) : 0;
    drawToken(
      g,
      box.x + (index % cols) * (cell + gap),
      box.y + Math.floor(index / cols) * (cell + gap),
      cell,
      cell,
      active ? color(index) : palette.gray100,
      ctx,
      {
        opacity: opacity * (active ? 0.46 + reveal * 0.46 : 0.5),
        fillOpacity: active ? 0.88 : 0.72,
        strokeWidth: 1.2,
        rx: options.rx ?? 3
      }
    );
  }
}

export function promptTrayMetrics(tokens, scale = 1) {
  const widths = tokens.map((token) => Math.max(40, token.length * 9.2 + 22) * scale);
  const gap = 9 * scale;
  return {
    widths,
    gap,
    h: 30 * scale,
    w: widths.reduce((sum, width) => sum + width, 0) + gap * (tokens.length - 1)
  };
}

export function drawPromptTray(g, x, y, tokens, ctx, options = {}) {
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const scale = options.scale ?? 1;
  const metrics = promptTrayMetrics(tokens, scale);
  let cursor = x;
  const group = g.append("g").attr("opacity", opacity);
  tokens.forEach((token, index) => {
    const color = options.colors?.[index % options.colors.length] ?? evalColors.tokens[index % evalColors.tokens.length];
    const active = options.activeCount === undefined || index < options.activeCount;
    drawToken(group, cursor, y, metrics.widths[index], metrics.h, color, ctx, {
      opacity: active ? 1 : 0.34,
      fill: active ? color : ctx.palette.gray100,
      textFill: active ? "#ffffff" : ctx.palette.gray600,
      label: token,
      labelSize: options.labelSize ?? 13 * scale,
      rx: 7 * scale,
      strokeWidth: 1.25
    });
    cursor += metrics.widths[index] + metrics.gap;
  });
}

export function drawArrow(g, from, to, color, opacity = 1, width = 3) {
  if (opacity <= 0.01) return;
  const angle = Math.atan2(to.y - from.y, to.x - from.x);
  const head = 10;
  const hx = to.x - Math.cos(angle) * head;
  const hy = to.y - Math.sin(angle) * head;
  g.append("line")
    .attr("x1", from.x)
    .attr("y1", from.y)
    .attr("x2", hx)
    .attr("y2", hy)
    .attr("stroke", color)
    .attr("stroke-width", width)
    .attr("stroke-linecap", "round")
    .attr("opacity", opacity);
  g.append("path")
    .attr("d", [
      `M${to.x},${to.y}`,
      `L${hx - Math.cos(angle - Math.PI / 2) * 5},${hy - Math.sin(angle - Math.PI / 2) * 5}`,
      `L${hx - Math.cos(angle + Math.PI / 2) * 5},${hy - Math.sin(angle + Math.PI / 2) * 5}`,
      "Z"
    ].join(" "))
    .attr("fill", color)
    .attr("opacity", opacity);
}

export function drawModelBox(g, box, ctx, options = {}) {
  return drawLlmModelBox(g, box, ctx, {
    labelLines: options.labelLines ?? ["LLM"],
    labelSize: options.labelSize ?? 52,
    labelY: options.labelY ?? box.y + box.h / 2 - 6,
    activation: options.activation ?? 0,
    activationClock: options.activationClock ?? 0,
    opacity: options.opacity ?? 1,
    textOpacity: options.textOpacity ?? 1
  });
}

export function drawProbabilityBars(g, box, candidates, ctx, options = {}) {
  const { palette, clamp, easeOut } = ctx;
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const D3 = globalThis.d3;
  const rowH = options.rowH ?? 34;
  const barH = options.barH ?? 20;
  const maxP = D3.max(candidates, (candidate) => candidate.p) || 1;
  const reveal = options.reveal ?? 1;
  const group = g.append("g").attr("opacity", opacity);
  if (options.background !== false) {
    group.append("rect")
      .attr("x", box.x - 18)
      .attr("y", box.y - 22)
      .attr("width", box.w + 36)
      .attr("height", candidates.length * rowH + 36)
      .attr("rx", 0)
      .attr("fill", "#ffffff")
      .attr("stroke", palette.gray200)
      .attr("stroke-width", 1.1)
      .attr("opacity", 0.94);
  }
  candidates.forEach((candidate, index) => {
    const y = box.y + index * rowH;
    const rowReveal = easeOut(clamp(reveal * 1.25 - index * 0.08, 0, 1));
    const selected = options.selectedIndex === index;
    group.append("rect")
      .attr("x", box.x)
      .attr("y", y)
      .attr("width", box.w)
      .attr("height", barH)
      .attr("rx", barH / 2)
      .attr("fill", palette.gray100)
      .attr("opacity", 0.82 * rowReveal);
    group.append("rect")
      .attr("x", box.x)
      .attr("y", y)
      .attr("width", box.w * (candidate.p / maxP) * rowReveal)
      .attr("height", barH)
      .attr("rx", barH / 2)
      .attr("fill", candidate.color)
      .attr("opacity", selected ? 0.96 : 0.58);
    if (options.labels !== false) {
      drawText(group, candidate.label, box.x + 12, y + barH / 2 + 1, ctx, {
        anchor: "start",
        size: options.labelSize ?? 13,
        weight: selected ? 870 : 760,
        fill: selected ? "#ffffff" : palette.brandNeutral,
        opacity: selected ? 0.98 : 0.84
      });
      if (options.percent) {
        drawText(group, `${Math.round(candidate.p * 100)}%`, box.x + box.w + 10, y + barH / 2 + 1, ctx, {
          anchor: "start",
          size: options.percentSize ?? 12,
          weight: selected ? 850 : 730,
          fill: selected ? candidate.color : palette.gray600,
          opacity: 0.88
        });
      }
    }
  });
}

export function drawProbabilityWheel(g, wheel, candidates, ctx, options = {}) {
  const D3 = globalThis.d3;
  const { palette, clamp, easeOut, lerp } = ctx;
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const selectedIndex = options.selectedIndex ?? 0;
  const arcs = D3.pie().sort(null).value((candidate) => candidate.p)(candidates);
  const selectedArc = arcs[selectedIndex];
  const selectedCenterDeg = ((selectedArc.startAngle + selectedArc.endAngle) / 2) * 180 / Math.PI;
  const spinP = clamp(options.spinP ?? 1, 0, 1);
  const turns = options.turns ?? 4;
  const finalRotation = turns * 360 - selectedCenterDeg;
  let rotation = 0;
  if (spinP < 0.45) {
    rotation = lerp(0, finalRotation * 0.58, easeOut(spinP / 0.45));
  } else if (spinP < 0.78) {
    rotation = lerp(finalRotation * 0.58, finalRotation * 0.86, easeOut((spinP - 0.45) / 0.33));
  } else {
    rotation = lerp(finalRotation * 0.86, finalRotation, easeOut((spinP - 0.78) / 0.22));
  }
  const settled = easeOut(clamp((spinP - 0.92) / 0.08, 0, 1));
  const arc = D3.arc().innerRadius(options.innerRadius ?? 0).outerRadius(wheel.r).cornerRadius(4).padAngle(0.012);
  const selectedPath = D3.arc().innerRadius(options.innerRadius ?? 0).outerRadius(wheel.r + 5).cornerRadius(5).padAngle(0.012);
  const group = g.append("g").attr("opacity", opacity);

  group.append("circle")
    .attr("cx", wheel.cx)
    .attr("cy", wheel.cy)
    .attr("r", wheel.r + 10)
    .attr("fill", palette.gray100)
    .attr("stroke", "none")
    .attr("opacity", 0.94);

  const wheelGroup = group.append("g")
    .attr("transform", `translate(${wheel.cx},${wheel.cy}) rotate(${rotation})`);
  wheelGroup.selectAll("path.probability-wedge")
    .data(arcs)
    .join("path")
    .attr("class", "probability-wedge")
    .attr("d", arc)
    .attr("fill", (arcDatum) => arcDatum.data.color)
    .attr("fill-opacity", (arcDatum, index) => index === selectedIndex ? 0.94 : 0.66)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2);
  wheelGroup.selectAll("path.selected-wedge")
    .data(arcs.filter((_, index) => index === selectedIndex))
    .join("path")
    .attr("class", "selected-wedge")
    .attr("d", selectedPath)
    .attr("fill", "none")
    .attr("stroke", palette.redHover)
    .attr("stroke-width", 3.2)
    .attr("opacity", settled * 0.96);

  for (let tick = 0; tick < 24; tick += 1) {
    const angle = tick * 15 * Math.PI / 180;
    const r0 = wheel.r + 5;
    const r1 = wheel.r + (tick % 3 === 0 ? 14 : 10);
    group.append("line")
      .attr("x1", wheel.cx + Math.sin(angle) * r0)
      .attr("y1", wheel.cy - Math.cos(angle) * r0)
      .attr("x2", wheel.cx + Math.sin(angle) * r1)
      .attr("y2", wheel.cy - Math.cos(angle) * r1)
      .attr("stroke", tick % 3 === 0 ? palette.gray600 : palette.gray300)
      .attr("stroke-width", tick % 3 === 0 ? 1.5 : 1)
      .attr("opacity", 0.7);
  }

  group.append("path")
    .attr("d", `M${wheel.cx},${wheel.cy - wheel.r - 16} L${wheel.cx - 12},${wheel.cy - wheel.r - 39} L${wheel.cx + 12},${wheel.cy - wheel.r - 39} Z`)
    .attr("fill", palette.brandPrimary)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .attr("stroke-linejoin", "round")
    .attr("opacity", 0.94);
  return { group, selectedArc, rotation, settled };
}

export function drawResultBadge(g, x, y, state, ctx, options = {}) {
  const { palette } = ctx;
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const pass = state === "pass";
  const color = pass ? palette.green : palette.red;
  const fill = pass ? palette.greenHighlight : palette.redHighlight;
  g.append("circle")
    .attr("cx", x)
    .attr("cy", y)
    .attr("r", options.r ?? 18)
    .attr("fill", fill)
    .attr("stroke", color)
    .attr("stroke-width", 2.2)
    .attr("opacity", opacity);
  drawIcon(g, pass ? "check" : "close", x, y + 0.5, ctx, {
    size: options.iconSize ?? 25,
    fill: color,
    opacity
  });
}

export function drawCostTicks(g, x, y, count, ctx, options = {}) {
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const { palette, easeOut } = ctx;
  const reveal = options.reveal ?? 1;
  for (let index = 0; index < count; index += 1) {
    const active = easeOut(ctx.clamp(reveal * count - index, 0, 1));
    g.append("rect")
      .attr("x", x + index * (options.gap ?? 12))
      .attr("y", y)
      .attr("width", options.w ?? 8)
      .attr("height", options.h ?? 22)
      .attr("rx", 3)
      .attr("fill", options.color ?? palette.orange)
      .attr("opacity", opacity * (0.16 + active * 0.76));
  }
}

export function railPath(origin, target, options = {}) {
  const bend = options.bend ?? 0.54;
  const spread = Math.abs(target.y - origin.y);
  const c1 = {
    x: origin.x + (target.x - origin.x) * 0.34,
    y: origin.y + (target.y - origin.y) * bend - spread * 0.06
  };
  const c2 = {
    x: origin.x + (target.x - origin.x) * 0.68,
    y: target.y - (target.y - origin.y) * 0.18 + spread * 0.04
  };
  return { origin, c1, c2, target, d: `M${origin.x},${origin.y} C${c1.x},${c1.y} ${c2.x},${c2.y} ${target.x},${target.y}` };
}

export function cubicPoint(path, t) {
  const p = Math.max(0, Math.min(1, t));
  const u = 1 - p;
  return {
    x: u ** 3 * path.origin.x + 3 * u * u * p * path.c1.x + 3 * u * p * p * path.c2.x + p ** 3 * path.target.x,
    y: u ** 3 * path.origin.y + 3 * u * u * p * path.c1.y + 3 * u * p * p * path.c2.y + p ** 3 * path.target.y
  };
}

export function cubicAngle(path, t) {
  const p = Math.max(0, Math.min(1, t));
  const u = 1 - p;
  const dx = 3 * u * u * (path.c1.x - path.origin.x)
    + 6 * u * p * (path.c2.x - path.c1.x)
    + 3 * p * p * (path.target.x - path.c2.x);
  const dy = 3 * u * u * (path.c1.y - path.origin.y)
    + 6 * u * p * (path.c2.y - path.c1.y)
    + 3 * p * p * (path.target.y - path.c2.y);
  return Math.atan2(dy, dx) * 180 / Math.PI;
}

export function drawRailSwitch(g, origin, branches, ctx, options = {}) {
  const { palette, easeOut, clamp } = ctx;
  const opacity = options.opacity ?? 1;
  const reveal = options.reveal ?? 1;
  if (opacity <= 0.01) return [];
  const paths = branches.map((branch) => ({ ...branch, path: railPath(origin, branch.target, branch.pathOptions) }));
  const maxP = Math.max(...branches.map((branch) => branch.p), 0.01);

  g.append("circle")
    .attr("cx", origin.x)
    .attr("cy", origin.y)
    .attr("r", 15)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray300)
    .attr("stroke-width", 2)
    .attr("opacity", opacity * easeOut(reveal));

  paths.forEach((branch, index) => {
    const rowReveal = easeOut(clamp(reveal * 1.18 - index * 0.06, 0, 1));
    const selected = branch.selected;
    const width = (options.minWidth ?? 4) + (options.maxWidth ?? 23) * (branch.p / maxP);
    g.append("path")
      .attr("d", branch.path.d)
      .attr("fill", "none")
      .attr("stroke", branch.color)
      .attr("stroke-width", width)
      .attr("stroke-linecap", "round")
      .attr("stroke-opacity", opacity * rowReveal * (selected ? 0.74 : 0.28));
    g.append("path")
      .attr("d", branch.path.d)
      .attr("fill", "none")
      .attr("stroke", "#ffffff")
      .attr("stroke-width", Math.max(1.4, width * 0.18))
      .attr("stroke-linecap", "round")
      .attr("stroke-opacity", opacity * rowReveal * (selected ? 0.42 : 0.2));
    if (options.labels !== false) {
      drawToken(g, branch.target.x + 12, branch.target.y - 14, Math.max(48, branch.label.length * 10 + 20), 28, branch.color, ctx, {
        label: branch.label,
        labelSize: 12,
        opacity: opacity * rowReveal * (selected ? 0.9 : 0.62),
        fillOpacity: selected ? 0.86 : 0.58,
        strokeWidth: 1.1
      });
    }
  });

  return paths;
}

export function drawCapsule(g, x, y, angle, color, ctx, options = {}) {
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  const w = options.w ?? 54;
  const h = options.h ?? 24;
  const group = g.append("g")
    .attr("transform", `translate(${x},${y}) rotate(${angle})`)
    .attr("opacity", opacity);
  group.append("rect")
    .attr("x", -w / 2)
    .attr("y", -h / 2)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", h / 2)
    .attr("fill", options.fill ?? "#ffffff")
    .attr("stroke", color)
    .attr("stroke-width", options.strokeWidth ?? 3);
  group.append("circle")
    .attr("cx", w / 2 - h / 2)
    .attr("cy", 0)
    .attr("r", h * 0.28)
    .attr("fill", color)
    .attr("opacity", 0.9);
}

export function drawCapsuleOnPath(g, path, progress, color, ctx, options = {}) {
  const p = ctx.clamp(progress, 0, 1);
  const point = cubicPoint(path, p);
  const angle = cubicAngle(path, p);
  drawCapsule(g, point.x, point.y, angle, color, ctx, options);
}

export function drawContextPlates(g, plates, ctx, options = {}) {
  const { palette, easeOut, clamp } = ctx;
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  plates.forEach((plate, index) => {
    const reveal = easeOut(clamp((options.reveal ?? 1) * 1.2 - index * 0.13, 0, 1));
    const group = g.append("g").attr("opacity", opacity * reveal);
    group.append("rect")
      .attr("x", plate.x)
      .attr("y", plate.y)
      .attr("width", plate.w)
      .attr("height", plate.h)
      .attr("rx", 0)
      .attr("fill", plate.fill ?? "#ffffff")
      .attr("stroke", plate.color)
      .attr("stroke-width", 2)
      .attr("fill-opacity", 0.74);
    drawIcon(group, plate.icon ?? "tune", plate.x + plate.w / 2, plate.y + plate.h / 2, ctx, {
      size: plate.iconSize ?? 26,
      fill: plate.color,
      opacity: 0.76
    });
    group.append("line")
      .attr("x1", plate.x + plate.w / 2)
      .attr("y1", plate.y + plate.h)
      .attr("x2", plate.x + plate.w / 2)
      .attr("y2", plate.y + plate.h + (plate.drop ?? 68))
      .attr("stroke", plate.color)
      .attr("stroke-width", 2)
      .attr("stroke-linecap", "round")
      .attr("opacity", 0.18);
  });
}

export function drawTestBoard(g, box, cells, ctx, options = {}) {
  const { palette, easeOut, clamp } = ctx;
  const opacity = options.opacity ?? 1;
  if (opacity <= 0.01) return;
  g.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.2)
    .attr("opacity", opacity * 0.96);
  g.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", 8)
    .attr("height", box.h)
    .attr("fill", options.color ?? palette.green)
    .attr("opacity", opacity * 0.72);
  cells.forEach((state, index) => {
    const reveal = easeOut(clamp((options.reveal ?? 1) * 1.28 - index * 0.08, 0, 1));
    const x = box.x + 30 + (index % 4) * 42;
    const y = box.y + 22 + Math.floor(index / 4) * 34;
    const pass = state === "pass";
    g.append("rect")
      .attr("x", x)
      .attr("y", y)
      .attr("width", 28)
      .attr("height", 22)
      .attr("rx", 5)
      .attr("fill", pass ? palette.green : palette.red)
      .attr("opacity", opacity * reveal * (pass ? 0.72 : 0.88));
    drawIcon(g, pass ? "check" : "close", x + 14, y + 11, ctx, {
      size: 17,
      fill: "#ffffff",
      opacity: opacity * reveal
    });
  });
}

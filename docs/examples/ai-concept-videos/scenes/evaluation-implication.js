import {
  drawCapsule,
  drawCostTicks,
  drawIcon,
  drawResultBadge,
  drawText,
  easeP,
  p01
} from "./evaluation-shared.js";

const passIndexes = new Set([1, 3, 6, 9, 14, 18]);

function laneY(index) {
  return 98 + index * 25;
}

function drawSampleLane(g, index, t, ctx) {
  const { palette, easeOut, easeInOut } = ctx;
  const pass = passIndexes.has(index);
  const y = laneY(index);
  const reveal = easeOut(p01(t, 0.3 + index * 0.06, 1.0, ctx));
  const pathP = easeInOut(p01(t, 1.8 + index * 0.03, 4.4, ctx));
  const opacity = reveal * 0.96;
  g.append("line")
    .attr("x1", 130)
    .attr("y1", y)
    .attr("x2", 860)
    .attr("y2", y)
    .attr("stroke", pass ? palette.green : palette.gray300)
    .attr("stroke-width", pass ? 4.2 : 3)
    .attr("stroke-linecap", "round")
    .attr("opacity", opacity * (pass ? 0.52 : 0.38));
  const x = 130 + (860 - 130) * pathP;
  drawCapsule(g, x, y, 0, pass ? palette.green : palette.gray500, ctx, {
    opacity: opacity * (pathP < 0.99 ? 0.82 : 0.42),
    w: 36,
    h: 15,
    strokeWidth: 2,
    fill: "#ffffff"
  });
  if (pathP > 0.82) {
    drawResultBadge(g, 910, y, pass ? "pass" : "fail", ctx, {
      opacity: opacity * easeOut((pathP - 0.82) / 0.18),
      r: 11,
      iconSize: 15
    });
  }
}

function drawTwentyLanes(g, t, ctx) {
  const { palette } = ctx;
  const p = easeP(t, 0.2, 0.9, ctx);
  drawText(g, "20", 98, 74, ctx, {
    size: 28,
    weight: 920,
    fill: palette.brandNeutral,
    opacity: p
  });
  drawText(g, "6", 914, 74, ctx, {
    size: 28,
    weight: 920,
    fill: palette.green,
    opacity: easeP(t, 6.4, 0.9, ctx)
  });
  for (let index = 0; index < 20; index += 1) drawSampleLane(g, index, t, ctx);
}

function drawClamp(g, t, ctx) {
  const { palette, easeInOut, easeOut, lerp } = ctx;
  const p = easeP(t, 8.5, 1.1, ctx);
  if (p <= 0.01) return;
  const windows = [
    { start: 0, success: true },
    { start: 5, success: false },
    { start: 10, success: true },
    { start: 15, success: true }
  ];
  const phase = Math.min(windows.length - 1, Math.floor(Math.max(0, t - 10.2) / 4.3));
  const current = windows[phase];
  const within = easeInOut(p01(t, 10.2 + phase * 4.3, 2.0, ctx));
  const y = lerp(laneY(current.start) - 12, laneY(current.start + 4) - 12, 0);
  const x = lerp(432, 648, within);
  const h = laneY(current.start + 4) - laneY(current.start) + 24;
  const color = current.success ? palette.green : palette.red;

  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", 118)
    .attr("height", h)
    .attr("rx", 0)
    .attr("fill", current.success ? palette.greenHighlight : palette.redHighlight)
    .attr("stroke", color)
    .attr("stroke-width", 3)
    .attr("opacity", p * 0.7);
  g.append("path")
    .attr("d", `M${x - 14},${y} L${x - 2},${y} L${x - 2},${y + h} L${x - 14},${y + h}`)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 4)
    .attr("stroke-linecap", "round")
    .attr("opacity", p);
  g.append("path")
    .attr("d", `M${x + 132},${y} L${x + 120},${y} L${x + 120},${y + h} L${x + 132},${y + h}`)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 4)
    .attr("stroke-linecap", "round")
    .attr("opacity", p);
  drawResultBadge(g, x + 59, y - 30, current.success ? "pass" : "fail", ctx, {
    opacity: p * easeOut(p01(t, 11 + phase * 4.3, 0.7, ctx)),
    r: 18
  });
}

function drawEstimatorAndTradeoff(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeP(t, 20.0, 1.1, ctx);
  if (p <= 0.01) return;
  drawText(g, "pass@5", 1026, 180, ctx, {
    size: 30,
    weight: 920,
    fill: palette.brandPrimary,
    opacity: p
  });
  drawText(g, "87.1%", 1028, 226, ctx, {
    size: 42,
    weight: 920,
    fill: palette.green,
    opacity: easeP(t, 21.6, 0.9, ctx)
  });
  g.append("line")
    .attr("x1", 1000)
    .attr("y1", 286)
    .attr("x2", 1160)
    .attr("y2", 286)
    .attr("stroke", palette.gray300)
    .attr("stroke-width", 2)
    .attr("opacity", p);
  [
    { label: "N=1", n: 1, success: 0.3 },
    { label: "N=5", n: 5, success: 0.871 },
    { label: "N=20", n: 20, success: 1 }
  ].forEach((item, index) => {
    const rowY = 330 + index * 92;
    const reveal = easeOut(p01(t, 22.5 + index * 1.3, 1.0, ctx));
    drawText(g, item.label, 984, rowY + 10, ctx, {
      anchor: "start",
      size: 17,
      weight: 880,
      fill: palette.gray700,
      opacity: p * reveal
    });
    g.append("rect")
      .attr("x", 1046)
      .attr("y", rowY)
      .attr("width", 118)
      .attr("height", 16)
      .attr("rx", 8)
      .attr("fill", palette.gray100)
      .attr("opacity", p * reveal);
    g.append("rect")
      .attr("x", 1046)
      .attr("y", rowY)
      .attr("width", 118 * item.success)
      .attr("height", 16)
      .attr("rx", 8)
      .attr("fill", palette.green)
      .attr("opacity", p * reveal * 0.72);
    drawCostTicks(g, 1048, rowY + 32, Math.min(16, item.n), ctx, {
      opacity: p * reveal,
      reveal,
      w: 7,
      h: 18,
      gap: 8,
      color: palette.orange
    });
  });
}

function drawSustainedTradeoffPulse(g, t, ctx) {
  const { palette, easeOut, lerp } = ctx;
  const p = easeP(t, 25.2, 0.9, ctx);
  if (p <= 0.01) return;
  const sweep = ((t - 25.2) * 0.18) % 1;
  const sweepX = lerp(146, 802, easeOut(sweep));
  g.append("rect")
    .attr("x", sweepX)
    .attr("y", 82)
    .attr("width", 92)
    .attr("height", 518)
    .attr("rx", 0)
    .attr("fill", palette.blueHighlight)
    .attr("opacity", p * 0.42);
  g.append("line")
    .attr("x1", sweepX + 46)
    .attr("y1", 82)
    .attr("x2", sweepX + 46)
    .attr("y2", 600)
    .attr("stroke", palette.blue)
    .attr("stroke-width", 3)
    .attr("stroke-linecap", "round")
    .attr("opacity", p * 0.48);
  [
    { y: 330, n: 1, color: palette.blue },
    { y: 422, n: 5, color: palette.green },
    { y: 514, n: 20, color: palette.orange }
  ].forEach((row, rowIndex) => {
    const phase = ((t - 25.2) * 0.42 + rowIndex * 0.22) % 1;
    const wave = Math.sin(phase * Math.PI);
    const x = lerp(1048, 1164, easeOut(phase));
    drawCapsule(g, x, row.y + 41, 0, row.color, ctx, {
      opacity: p * wave * 0.58,
      w: 24,
      h: 10,
      strokeWidth: 1.5,
      fill: "#ffffff"
    });
    g.append("circle")
      .attr("cx", 1048 + Math.min(16, row.n) * 15)
      .attr("cy", row.y + 41)
      .attr("r", 5 + wave * 5)
      .attr("fill", "none")
      .attr("stroke", row.color)
      .attr("stroke-width", 2)
      .attr("opacity", p * wave * 0.32);
  });
}

export function drawEvaluationImplication(g, t, ctx) {
  const group = g.append("g").attr("opacity", easeP(t, 0, 0.8, ctx));
  drawTwentyLanes(group, t, ctx);
  drawClamp(group, t, ctx);
  drawEstimatorAndTradeoff(group, t, ctx);
  drawSustainedTradeoffPulse(group, t, ctx);
}

import {
  drawCapsule,
  drawCapsuleOnPath,
  drawContextPlates,
  drawIcon,
  drawRailSwitch,
  drawResultBadge,
  drawText,
  easeP,
  p01
} from "./evaluation-shared.js";

const actionBranches = [
  { label: "read", p: 0.39, color: "#007298", target: { x: 820, y: 218 }, selected: true },
  { label: "edit", p: 0.31, color: "#652f6c", target: { x: 884, y: 310 } },
  { label: "test", p: 0.2, color: "#45842a", target: { x: 862, y: 414 } },
  { label: "stop", p: 0.1, color: "#e77204", target: { x: 782, y: 500 } }
];

function loopPoint(cx, cy, rx, ry, p) {
  const angle = p * Math.PI * 2 - Math.PI / 2;
  return { x: cx + Math.cos(angle) * rx, y: cy + Math.sin(angle) * ry, angle: angle * 180 / Math.PI + 90 };
}

function drawLoop(g, t, ctx) {
  const { palette } = ctx;
  const p = easeP(t, 0.3, 1.1, ctx);
  const cx = 640;
  const cy = 372;
  const rx = 430;
  const ry = 224;
  g.append("ellipse")
    .attr("cx", cx)
    .attr("cy", cy)
    .attr("rx", rx)
    .attr("ry", ry)
    .attr("fill", "none")
    .attr("stroke", palette.gray300)
    .attr("stroke-width", 18)
    .attr("opacity", p * 0.22);
  g.append("ellipse")
    .attr("cx", cx)
    .attr("cy", cy)
    .attr("rx", rx)
    .attr("ry", ry)
    .attr("fill", "none")
    .attr("stroke", palette.gray500)
    .attr("stroke-width", 3)
    .attr("stroke-dasharray", "12 12")
    .attr("opacity", p * 0.42);
  return { cx, cy, rx, ry, opacity: p };
}

function drawStation(g, label, icon, x, y, color, t, start, ctx) {
  const { palette } = ctx;
  const p = easeP(t, start, 0.9, ctx);
  if (p <= 0.01) return;
  g.append("circle")
    .attr("cx", x)
    .attr("cy", y)
    .attr("r", 54)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.2)
    .attr("opacity", p * 0.96);
  drawIcon(g, icon, x, y - 8, ctx, { size: 34, fill: color, opacity: p });
  drawText(g, label, x, y + 28, ctx, { size: 15, weight: 850, fill: palette.gray700, opacity: p });
}

function drawMovingLoopCapsules(g, loop, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeP(t, 1.3, 1.0, ctx);
  if (p <= 0.01) return;
  for (let index = 0; index < 5; index += 1) {
    const position = ((t * 0.055 + index / 5) % 1);
    const pt = loopPoint(loop.cx, loop.cy, loop.rx, loop.ry, position);
    drawCapsule(g, pt.x, pt.y, pt.angle, [palette.blue, palette.purple, palette.orange, palette.green][index % 4], ctx, {
      opacity: p * (0.28 + easeOut(position) * 0.22),
      w: 30,
      h: 12,
      strokeWidth: 1.4,
      fill: "#ffffff"
    });
  }
}

function drawActionSwitch(g, t, ctx) {
  const { palette, easeInOut } = ctx;
  const origin = { x: 472, y: 352 };
  const paths = drawRailSwitch(g, origin, actionBranches, ctx, {
    reveal: p01(t, 2.5, 1.5, ctx),
    opacity: easeP(t, 2.2, 0.9, ctx),
    minWidth: 3.2,
    maxWidth: 20,
    labels: true
  });
  const sample = p01(t, 4.3, 3.4, ctx);
  if (sample > 0.01 && paths[0]) {
    drawCapsuleOnPath(g, paths[0].path, easeInOut(sample), palette.brandPrimary, ctx, {
      opacity: easeP(t, 4.2, 0.6, ctx),
      w: 60,
      h: 25,
      strokeWidth: 3.2
    });
  }
}

function drawEvalStations(g, t, ctx) {
  const { palette } = ctx;
  const p = easeP(t, 7.0, 1.0, ctx);
  if (p <= 0.01) return;
  [
    { x: 878, y: 524, state: "pass" },
    { x: 642, y: 592, state: "pass" },
    { x: 404, y: 520, state: "fail" }
  ].forEach((item, index) => {
    drawResultBadge(g, item.x, item.y, item.state, ctx, {
      opacity: p * easeP(t, 7.2 + index * 0.3, 0.7, ctx),
      r: 18
    });
  });
  g.append("rect")
    .attr("x", 544)
    .attr("y", 540)
    .attr("width", 192)
    .attr("height", 64)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.green)
    .attr("stroke-width", 2)
    .attr("opacity", p * 0.78);
  drawIcon(g, "fact_check", 640, 572, ctx, { size: 38, fill: palette.green, opacity: p });
}

function drawTraceLedger(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeP(t, 10.5, 1.0, ctx);
  if (p <= 0.01) return;
  const x = 958;
  const y = 112;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", 206)
    .attr("height", 330)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.2)
    .attr("opacity", p * 0.92);
  [palette.purple, palette.blue, palette.green, palette.orange, palette.red].forEach((color, index) => {
    const rowY = y + 42 + index * 52;
    const reveal = easeOut(p01(t, 10.9 + index * 0.65, 0.8, ctx));
    g.append("rect")
      .attr("x", x + 22)
      .attr("y", rowY)
      .attr("width", 118)
      .attr("height", 20)
      .attr("rx", 0)
      .attr("fill", color)
      .attr("opacity", p * reveal * 0.35);
    drawResultBadge(g, x + 168, rowY + 10, index === 4 ? "fail" : "pass", ctx, {
      opacity: p * reveal,
      r: 12,
      iconSize: 14
    });
  });
}

export function drawEvaluationHandoff(g, t, ctx) {
  const { palette } = ctx;
  const group = g.append("g").attr("opacity", easeP(t, 0, 0.8, ctx));
  const loop = drawLoop(group, t, ctx);
  drawStation(group, "sample", "alt_route", 640, 148, palette.purple, t, 0.8, ctx);
  drawStation(group, "action", "build", 1040, 372, palette.blue, t, 1.7, ctx);
  drawStation(group, "observe", "visibility", 240, 372, palette.orange, t, 8.7, ctx);
  drawMovingLoopCapsules(group, loop, t, ctx);
  drawContextPlates(group, [
    { x: 260, y: 170, w: 54, h: 54, color: palette.orange, fill: palette.orangeHighlight, icon: "visibility", drop: 110 },
    { x: 330, y: 142, w: 54, h: 54, color: palette.blue, fill: palette.blueHighlight, icon: "database", drop: 130 }
  ], ctx, { opacity: easeP(t, 9.0, 0.9, ctx), reveal: p01(t, 9, 2, ctx) });
  drawActionSwitch(group, t, ctx);
  drawEvalStations(group, t, ctx);
  drawTraceLedger(group, t, ctx);
  const finalP = easeP(t, 16.2, 1.3, ctx);
  if (finalP > 0.01) {
    drawText(group, "agent loop", 542, 674, ctx, {
      anchor: "start",
      size: 34,
      weight: 920,
      fill: palette.brandPrimary,
      opacity: finalP
    });
    drawIcon(group, "sync", 492, 674, ctx, { size: 42, fill: palette.brandPrimary, opacity: finalP });
  }
}

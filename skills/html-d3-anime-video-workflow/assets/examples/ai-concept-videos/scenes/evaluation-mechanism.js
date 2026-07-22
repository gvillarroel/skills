import {
  drawCapsule,
  drawIcon,
  drawResultBadge,
  drawTestBoard,
  drawText,
  drawToken,
  easeP,
  p01,
  windowP
} from "./evaluation-shared.js";

function workshopPath() {
  return [
    { x: 112, y: 362 },
    { x: 310, y: 362 },
    { x: 500, y: 244 },
    { x: 706, y: 244 },
    { x: 886, y: 424 },
    { x: 1108, y: 424 }
  ];
}

function pointOnPolyline(points, progress) {
  const lengths = [];
  let total = 0;
  for (let i = 0; i < points.length - 1; i += 1) {
    const dx = points[i + 1].x - points[i].x;
    const dy = points[i + 1].y - points[i].y;
    const len = Math.hypot(dx, dy);
    lengths.push(len);
    total += len;
  }
  let distance = Math.max(0, Math.min(1, progress)) * total;
  for (let i = 0; i < lengths.length; i += 1) {
    if (distance <= lengths[i]) {
      const p = distance / lengths[i];
      const a = points[i];
      const b = points[i + 1];
      return {
        x: a.x + (b.x - a.x) * p,
        y: a.y + (b.y - a.y) * p,
        angle: Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI
      };
    }
    distance -= lengths[i];
  }
  const a = points.at(-2);
  const b = points.at(-1);
  return { ...b, angle: Math.atan2(b.y - a.y, b.x - a.x) * 180 / Math.PI };
}

function drawWorkshopRail(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const points = workshopPath();
  const reveal = easeP(t, 0.5, 1.6, ctx);
  const line = globalThis.d3.line()
    .x((point) => point.x)
    .y((point) => point.y)
    .curve(globalThis.d3.curveCatmullRom.alpha(0.35));
  g.append("path")
    .datum(points)
    .attr("d", line)
    .attr("fill", "none")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 20)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", reveal * 0.78);
  g.append("path")
    .datum(points)
    .attr("d", line)
    .attr("fill", "none")
    .attr("stroke", palette.gray500)
    .attr("stroke-width", 3)
    .attr("stroke-linecap", "round")
    .attr("stroke-dasharray", "12 12")
    .attr("opacity", reveal * 0.42);
  for (let index = 0; index < 5; index += 1) {
    const p = ((t * 0.08 + index / 5) % 1);
    const pt = pointOnPolyline(points, p);
    drawCapsule(g, pt.x, pt.y, pt.angle, [palette.blue, palette.purple, palette.orange][index % 3], ctx, {
      opacity: reveal * easeOut(p) * 0.2,
      w: 26,
      h: 10,
      strokeWidth: 1.2,
      fill: [palette.blue, palette.purple, palette.orange][index % 3]
    });
  }
  return points;
}

function drawPatchTrain(g, t, ctx) {
  const { palette, easeInOut } = ctx;
  const travel = easeInOut(p01(t, 1.4, 21.5, ctx));
  const pt = pointOnPolyline(workshopPath(), travel);
  drawCapsule(g, pt.x, pt.y, pt.angle, palette.brandPrimary, ctx, {
    opacity: easeP(t, 1.2, 0.7, ctx),
    w: 74,
    h: 30,
    strokeWidth: 3.4
  });
  const tailCount = 4;
  for (let index = 0; index < tailCount; index += 1) {
    const tailP = Math.max(0, travel - 0.045 * (index + 1));
    const tail = pointOnPolyline(workshopPath(), tailP);
    drawCapsule(g, tail.x, tail.y, tail.angle, [palette.blue, palette.purple, palette.green, palette.orange][index], ctx, {
      opacity: easeP(t, 2.0 + index * 0.2, 0.6, ctx) * 0.8,
      w: 42,
      h: 18,
      strokeWidth: 2.2
    });
  }
}

function drawRubricGauge(g, x, y, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeP(t, 8.6, 1.0, ctx);
  if (p <= 0.01) return;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", 206)
    .attr("height", 112)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.2)
    .attr("opacity", p * 0.96);
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", 8)
    .attr("height", 112)
    .attr("fill", palette.orange)
    .attr("opacity", p * 0.74);
  [0.82, 0.58, 0.72].forEach((value, index) => {
    const yy = y + 26 + index * 30;
    g.append("rect")
      .attr("x", x + 34)
      .attr("y", yy)
      .attr("width", 124)
      .attr("height", 16)
      .attr("rx", 8)
      .attr("fill", palette.gray100)
      .attr("opacity", p);
    g.append("rect")
      .attr("x", x + 34)
      .attr("y", yy)
      .attr("width", 124 * value * easeOut(p01(t, 9.0 + index * 0.18, 1.0, ctx)))
      .attr("height", 16)
      .attr("rx", 8)
      .attr("fill", [palette.blue, palette.orange, palette.purple][index])
      .attr("opacity", p * 0.74);
  });
}

function drawJudgeLenses(g, t, ctx) {
  const { palette } = ctx;
  const modelP = easeP(t, 14.0, 1.1, ctx);
  const humanP = easeP(t, 17.4, 1.1, ctx);
  if (modelP > 0.01) {
    g.append("circle").attr("cx", 842).attr("cy", 244).attr("r", 52).attr("fill", "#ffffff").attr("stroke", palette.purple).attr("stroke-width", 2.2).attr("opacity", modelP * 0.94);
    drawIcon(g, "psychology", 842, 244, ctx, { size: 42, fill: palette.purple, opacity: modelP });
    drawResultBadge(g, 900, 244, "pass", ctx, { opacity: modelP, r: 18 });
  }
  if (humanP > 0.01) {
    g.append("circle").attr("cx", 944).attr("cy", 424).attr("r", 52).attr("fill", "#ffffff").attr("stroke", palette.blue).attr("stroke-width", 2.2).attr("opacity", humanP * 0.94);
    drawIcon(g, "person_search", 944, 424, ctx, { size: 42, fill: palette.blue, opacity: humanP });
    drawResultBadge(g, 1002, 424, "pass", ctx, { opacity: humanP, r: 18 });
  }
}

function drawPatchSource(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const p = easeP(t, 0.2, 0.9, ctx);
  for (let row = 0; row < 4; row += 1) {
    drawToken(g, 106 + row * 36, 286 + row * 12, 26, 16, [palette.blue, palette.purple, palette.green, palette.orange][row], ctx, {
      opacity: p * easeOut(p01(t, 0.2 + row * 0.12, 0.7, ctx)),
      strokeWidth: 1.1
    });
  }
  drawText(g, "patch", 112, 256, ctx, {
    anchor: "start",
    size: 20,
    weight: 880,
    fill: palette.gray700,
    opacity: p
  });
}

export function drawEvaluationMechanism(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const group = g.append("g").attr("opacity", easeP(t, 0, 0.8, ctx));
  drawWorkshopRail(group, t, ctx);
  drawPatchSource(group, t, ctx);
  drawPatchTrain(group, t, ctx);
  drawTestBoard(group, { x: 430, y: 104, w: 214, h: 112 }, ["pass", "pass", "pass", "fail", "pass", "pass", "pass", "pass"], ctx, {
    opacity: easeP(t, 4.2, 1.0, ctx),
    reveal: p01(t, 5.0, 2.4, ctx),
    color: palette.green
  });
  drawRubricGauge(group, 560, 430, t, ctx);
  drawJudgeLenses(group, t, ctx);

  const finalP = easeP(t, 22.5, 1.4, ctx);
  if (finalP > 0.01) {
    drawResultBadge(group, 1110, 424, "pass", ctx, { opacity: finalP, r: 28 });
    group.append("rect")
      .attr("x", 204)
      .attr("y", 604)
      .attr("width", 872)
      .attr("height", 6)
      .attr("rx", 3)
      .attr("fill", palette.gray200)
      .attr("opacity", finalP * 0.7);
    [palette.green, palette.orange, palette.purple, palette.blue].forEach((color, index) => {
      group.append("rect")
        .attr("x", 204 + index * 218)
        .attr("y", 600)
        .attr("width", 136)
        .attr("height", 14)
        .attr("rx", 7)
        .attr("fill", color)
        .attr("opacity", finalP * (0.48 + index * 0.08));
    });
  }
}

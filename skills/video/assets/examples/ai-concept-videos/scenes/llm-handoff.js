import { drawLlmModelBox } from "./llm-model-box.js";

const tokenColors = ["#007298", "#652f6c", "#45842a", "#e77204", "#9e1b32", "#f1c319"];
const gemmaPricePerMillion = {
  input: 0.07,
  output: 0.34
};

function p01(t, start, duration, ctx) {
  return ctx.clamp((t - start) / duration, 0, 1);
}

function easeP(t, start, duration, ctx) {
  return ctx.easeOut(p01(t, start, duration, ctx));
}

function windowP(t, start, end, ctx, ramp = 0.55) {
  const rise = ctx.easeInOut(p01(t, start, ramp, ctx));
  const fall = 1 - ctx.easeInOut(p01(t, end, ramp, ctx));
  return ctx.clamp(rise * fall, 0, 1);
}

function drawTokenSquare(g, x, y, size, color, opacity, options = {}) {
  if (opacity <= 0.01) return;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", size)
    .attr("height", size)
    .attr("rx", options.rx ?? 3)
    .attr("fill", color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", options.strokeWidth ?? 1.2)
    .attr("opacity", opacity);
}

function gridMetrics(cols, rows, cell = 16, gap = 6) {
  return {
    cols,
    rows,
    cell,
    gap,
    w: cols * cell + (cols - 1) * gap,
    h: rows * cell + (rows - 1) * gap
  };
}

function drawTokenGrid(g, box, count, ctx, options = {}) {
  const { palette, clamp, easeOut } = ctx;
  const cols = options.cols ?? 6;
  const rows = options.rows ?? 2;
  const cell = options.cell ?? 16;
  const gap = options.gap ?? 6;
  const total = cols * rows;
  const opacity = options.opacity ?? 1;
  const color = options.color ?? ((index) => tokenColors[index % tokenColors.length]);
  const emptyFill = options.emptyFill ?? palette.gray100;
  const activeOpacity = options.activeOpacity ?? 0.88;
  const emptyOpacity = options.emptyOpacity ?? 0.56;

  for (let index = 0; index < total; index += 1) {
    const active = index < count;
    const reveal = active ? easeOut(clamp(count - index, 0, 6) / 6) : 0;
    drawTokenSquare(
      g,
      box.x + (index % cols) * (cell + gap),
      box.y + Math.floor(index / cols) * (cell + gap),
      cell,
      active ? color(index) : emptyFill,
      opacity * (active ? 0.48 + reveal * activeOpacity : emptyOpacity),
      { rx: options.rx ?? 3, strokeWidth: 1.15 }
    );
  }
}

function drawRetryMark(g, x, y, opacity, ctx) {
  if (opacity <= 0.01) return;
  const { palette } = ctx;
  const r = 22;
  const arc = globalThis.d3.arc()
    .innerRadius(r - 3)
    .outerRadius(r)
    .startAngle(-Math.PI * 0.88)
    .endAngle(Math.PI * 0.74);
  g.append("path")
    .attr("d", arc)
    .attr("transform", `translate(${x},${y})`)
    .attr("fill", palette.orange)
    .attr("opacity", opacity * 0.8);
  const angle = Math.PI * 0.74;
  const tip = { x: x + Math.sin(angle) * r, y: y - Math.cos(angle) * r };
  g.append("path")
    .attr("d", `M${tip.x},${tip.y} l-12,-4 l5,12 Z`)
    .attr("fill", palette.orange)
    .attr("opacity", opacity * 0.85);
}

function drawInputRun(g, run, llmBox, t, ctx) {
  const { clamp, easeInOut, lerp, palette } = ctx;
  const metrics = gridMetrics(run.cols, run.rows, run.cell, run.gap);
  const travel = easeInOut(p01(t, run.start, run.inputDuration, ctx));
  const baseOpacity = windowP(t, run.start - 0.25, run.start + run.inputDuration + 0.7, ctx, 0.45);
  if (baseOpacity <= 0.01) return;

  const x = lerp(run.x, llmBox.x - metrics.w * 0.34, travel);
  const y = run.y;
  const fadeIntoModel = 1 - clamp((travel - 0.82) / 0.18, 0, 1) * 0.82;
  const opacity = baseOpacity * fadeIntoModel;

  if (run.retry) {
    drawRetryMark(g, x - 28, y + metrics.h / 2, opacity, ctx);
  }

  g.append("rect")
    .attr("x", x - 10)
    .attr("y", y - 10)
    .attr("width", metrics.w + 20)
    .attr("height", metrics.h + 20)
    .attr("fill", run.long ? "#ffffff" : palette.gray100)
    .attr("opacity", opacity * (run.long ? 0.72 : 0.42));

  drawTokenGrid(g, { x, y }, run.inputCount, ctx, {
    cols: run.cols,
    rows: run.rows,
    cell: run.cell,
    gap: run.gap,
    opacity,
    activeOpacity: run.long ? 0.7 : 0.84,
    color: (index) => {
      if (run.retry) return [palette.orange, palette.blue, palette.purple][index % 3];
      if (run.long) return [palette.gray700, palette.blue, palette.green, palette.purple][index % 4];
      return tokenColors[index % tokenColors.length];
    }
  });
}

function drawOutputRun(g, run, llmBox, t, ctx) {
  const { easeInOut, easeOut, lerp, palette } = ctx;
  const metrics = gridMetrics(run.outCols, run.outRows, run.outCell, run.outGap);
  const start = run.start + run.outputDelay;
  const p = easeInOut(p01(t, start, run.outputDuration, ctx));
  const visible = Math.floor(run.outputCount * easeOut(p01(t, start, run.outputDuration * 0.82, ctx)));
  const opacity = windowP(t, start - 0.1, start + run.outputDuration + run.hold, ctx, 0.45);
  if (opacity <= 0.01) return;

  const x = lerp(llmBox.x + llmBox.w - metrics.w * 0.2, run.outX, p);
  const y = run.outY;
  const colorSet = run.retry
    ? [palette.orange, palette.purple, palette.blue]
    : run.long
      ? [palette.gray700, palette.blue, palette.purple]
      : [palette.purple, palette.blue, palette.green, palette.red];

  g.append("rect")
    .attr("x", x - 10)
    .attr("y", y - 10)
    .attr("width", metrics.w + 20)
    .attr("height", metrics.h + 20)
    .attr("fill", palette.gray100)
    .attr("opacity", opacity * 0.42);

  drawTokenGrid(g, { x, y }, visible, ctx, {
    cols: run.outCols,
    rows: run.outRows,
    cell: run.outCell,
    gap: run.outGap,
    opacity,
    activeOpacity: 0.82,
    emptyOpacity: 0.5,
    emptyFill: palette.gray200,
    color: (index) => colorSet[index % colorSet.length]
  });
}

function workProgress(t, ctx) {
  const runs = [
    { start: 0.9, duration: 3.2, amount: 0.16 },
    { start: 4.4, duration: 3.4, amount: 0.25 },
    { start: 8.2, duration: 3.3, amount: 0.23 },
    { start: 12.2, duration: 5.0, amount: 0.33 }
  ];
  return ctx.clamp(
    0.02 + runs.reduce((total, run) => total + easeP(t, run.start, run.duration, ctx) * run.amount, 0),
    0,
    0.99
  );
}

function costState(t, ctx) {
  const inputs = [
    { start: 0.9, duration: 1.55, tokens: 8 },
    { start: 4.35, duration: 1.45, tokens: 8 },
    { start: 8.25, duration: 1.45, tokens: 8 },
    { start: 12.15, duration: 2.35, tokens: 54 }
  ];
  const outputs = [
    { start: 2.25, duration: 1.48, tokens: 5 },
    { start: 5.6, duration: 1.93, tokens: 16 },
    { start: 9.5, duration: 1.68, tokens: 10 },
    { start: 14.15, duration: 1.68, tokens: 8 }
  ];
  const inputTokens = inputs.reduce((total, item) => total + item.tokens * easeP(t, item.start, item.duration, ctx), 0);
  const outputTokens = outputs.reduce((total, item) => total + item.tokens * easeP(t, item.start, item.duration, ctx), 0);
  const cost = (inputTokens / 1_000_000) * gemmaPricePerMillion.input
    + (outputTokens / 1_000_000) * gemmaPricePerMillion.output;
  return { inputTokens, outputTokens, cost };
}

function pointOnPerimeter(box, p) {
  const pad = 26;
  const left = box.x - pad;
  const right = box.x + box.w + pad;
  const top = box.y - pad;
  const bottom = box.y + box.h + pad;
  const w = right - left;
  const h = bottom - top;
  const perimeter = 2 * (w + h);
  let d = p * perimeter;
  if (d <= w) return { x: left + d, y: top, angle: 0 };
  d -= w;
  if (d <= h) return { x: right, y: top + d, angle: 90 };
  d -= h;
  if (d <= w) return { x: right - d, y: bottom, angle: 180 };
  d -= w;
  return { x: left, y: bottom - d, angle: 270 };
}

function drawWorkTicks(g, box, t, ctx) {
  const { palette, clamp, easeOut } = ctx;
  const progress = workProgress(t, ctx);
  const total = 70;
  for (let index = 0; index < total; index += 1) {
    const tickP = index / total;
    const active = clamp(progress * total - index + 0.75, 0, 1);
    const pt = pointOnPerimeter(box, tickP);
    const longTick = index % 5 === 0;
    const len = longTick ? 12 : 8;
    const thickness = longTick ? 3.6 : 2.6;
    const color = active > 0 ? palette.brandPrimary : palette.gray200;
    const opacity = active > 0 ? 0.28 + easeOut(active) * 0.62 : 0.58;

    g.append("rect")
      .attr("x", pt.x - len / 2)
      .attr("y", pt.y - thickness / 2)
      .attr("width", len)
      .attr("height", thickness)
      .attr("rx", thickness / 2)
      .attr("fill", color)
      .attr("opacity", opacity)
      .attr("transform", `rotate(${pt.angle} ${pt.x} ${pt.y})`);
  }

  const last = pointOnPerimeter(box, progress);
  g.append("circle")
    .attr("cx", last.x)
    .attr("cy", last.y)
    .attr("r", 7)
    .attr("fill", palette.brandPrimary)
    .attr("opacity", 0.82);
}

function drawPriceTable(g, x, y, t, ctx) {
  const { palette, easeOut } = ctx;
  const opacity = easeOut(p01(t, 0.9, 1.2, ctx));
  if (opacity <= 0.01) return;
  const width = 230;
  const rowH = 30;
  const headerH = 30;
  const table = g.append("g").attr("opacity", opacity);

  table.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", width)
    .attr("height", headerH + rowH * 2)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.2);
  table.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", width)
    .attr("height", headerH)
    .attr("fill", palette.gray100)
    .attr("opacity", 0.92);

  ctx.drawHookText(table, "Gemma 4 26B", x + 16, y + 21, {
    size: 15,
    weight: 880,
    fill: palette.brandNeutral,
    anchor: "start",
    opacity: 0.96
  });

  const rows = [
    { label: "Input", value: `$${gemmaPricePerMillion.input.toFixed(2)} / 1M` },
    { label: "Output", value: `$${gemmaPricePerMillion.output.toFixed(2)} / 1M` }
  ];
  rows.forEach((row, index) => {
    const rowY = y + headerH + index * rowH;
    if (index > 0) {
      table.append("line")
        .attr("x1", x)
        .attr("y1", rowY)
        .attr("x2", x + width)
        .attr("y2", rowY)
        .attr("stroke", palette.gray200)
        .attr("stroke-width", 1);
    }
    ctx.drawHookText(table, row.label, x + 16, rowY + 22, {
      size: 14,
      weight: 800,
      fill: palette.gray700,
      anchor: "start",
      opacity: 0.94
    });
    ctx.drawHookText(table, row.value, x + width - 16, rowY + 22, {
      size: 14,
      weight: 850,
      fill: palette.brandPrimary,
      anchor: "end",
      opacity: 0.96
    });
  });
}

function drawCostReadout(g, x, y, t, ctx) {
  const { palette, easeOut } = ctx;
  const opacity = easeOut(p01(t, 1.1, 1.1, ctx));
  if (opacity <= 0.01) return;
  const width = 230;
  const height = 46;
  const cost = costState(t, ctx).cost;
  const readout = g.append("g").attr("opacity", opacity);

  readout.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", width)
    .attr("height", height)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.2);
  readout.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", 48)
    .attr("height", height)
    .attr("fill", palette.gray100)
    .attr("opacity", 0.9);
  ctx.drawHookText(readout, "$", x + 24, y + 30, {
    size: 28,
    weight: 900,
    fill: palette.brandPrimary,
    opacity: 0.96
  });
  ctx.drawHookText(readout, cost.toFixed(6), x + width - 16, y + 29, {
    size: 20,
    weight: 860,
    fill: palette.brandNeutral,
    anchor: "end",
    opacity: 0.95
  });
}

function drawAnswerInvalidation(g, t, ctx) {
  const { palette, clamp, easeOut } = ctx;
  const p = easeOut(p01(t, 7.45, 0.9, ctx)) * (1 - easeOut(p01(t, 9.1, 0.8, ctx)));
  if (p <= 0.01) return;
  const x = 882;
  const y = 214;
  for (let index = 0; index < 14; index += 1) {
    const col = index % 7;
    const row = Math.floor(index / 7);
    drawTokenSquare(g, x + col * 20, y + row * 20, 14, palette.gray300, p * 0.34, { rx: 3 });
  }
  drawRetryMark(g, x - 30, y + 19, p * 0.56, ctx);
}

export function drawLlmHandoffVisualOnly(g, ctx) {
  const { palette, sceneProgress, pulse, clamp, easeOut } = ctx;
  const t = sceneProgress * 20;
  const group = g.append("g").attr("opacity", easeOut(t / 1.1));

  const llmBox = { x: 502, y: 214, w: 276, h: 276 };
  const runs = [
    {
      start: 0.9,
      x: 112,
      y: 238,
      cols: 6,
      rows: 2,
      cell: 16,
      gap: 6,
      inputCount: 8,
      inputDuration: 1.55,
      outputDelay: 1.35,
      outputDuration: 1.8,
      hold: 0.75,
      outX: 882,
      outY: 238,
      outCols: 5,
      outRows: 1,
      outCell: 15,
      outGap: 6,
      outputCount: 5
    },
    {
      start: 4.35,
      x: 112,
      y: 326,
      cols: 6,
      rows: 2,
      cell: 16,
      gap: 6,
      inputCount: 8,
      inputDuration: 1.45,
      outputDelay: 1.25,
      outputDuration: 2.35,
      hold: 0.5,
      outX: 882,
      outY: 298,
      outCols: 8,
      outRows: 2,
      outCell: 14,
      outGap: 5,
      outputCount: 16
    },
    {
      start: 8.25,
      x: 112,
      y: 326,
      cols: 6,
      rows: 2,
      cell: 16,
      gap: 6,
      inputCount: 8,
      inputDuration: 1.45,
      outputDelay: 1.25,
      outputDuration: 2.05,
      hold: 0.5,
      outX: 882,
      outY: 382,
      outCols: 6,
      outRows: 2,
      outCell: 14,
      outGap: 5,
      outputCount: 10,
      retry: true
    },
    {
      start: 12.15,
      x: 82,
      y: 198,
      cols: 10,
      rows: 6,
      cell: 15,
      gap: 5,
      inputCount: 54,
      inputDuration: 2.35,
      outputDelay: 2.0,
      outputDuration: 2.05,
      hold: 1.45,
      outX: 882,
      outY: 462,
      outCols: 6,
      outRows: 2,
      outCell: 14,
      outGap: 5,
      outputCount: 8,
      long: true
    }
  ];

  const flowLayer = group.append("g");
  runs.forEach((run) => drawInputRun(flowLayer, run, llmBox, t, ctx));
  drawAnswerInvalidation(flowLayer, t, ctx);
  runs.forEach((run) => drawOutputRun(flowLayer, run, llmBox, t, ctx));

  const activation = clamp(
    0.08
      + Math.max(
        windowP(t, 0.95, 3.85, ctx) * 0.64,
        windowP(t, 4.4, 7.6, ctx) * 0.76,
        windowP(t, 8.25, 11.35, ctx) * 0.7,
        windowP(t, 12.15, 17.25, ctx) * 0.94
      )
      + pulse * 0.08,
    0,
    1
  );

  drawWorkTicks(group, llmBox, t, ctx);
  drawLlmModelBox(group, llmBox, ctx, {
    labelLines: ["Gemma", "4"],
    labelSize: 42,
    labelGap: 44,
    labelY: llmBox.y + llmBox.h / 2 - 28,
    activation,
    activationClock: t,
    opacity: 1
  });

  drawPriceTable(group, 928, 72, t, ctx);
  drawCostReadout(group, 928, 174, t, ctx);
}

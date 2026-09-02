import { drawLlmModelBox } from "./llm-model-box.js";
import { deepSweV11Points } from "./deepswe-v1.1-points.js";

const tokenColors = ["#007298", "#652f6c", "#45842a", "#e77204", "#9e1b32", "#f1c319"];
let globeStippleCells = null;

const gemmaModels = [
  {
    id: "e4b",
    name: "Gemma 4 E4B",
    short: "E4B",
    params: "4.5B / 8B",
    context: "128K",
    bf16: 17.9,
    q4: 4.5,
    vm: "L4",
    vmCost: 0.7045,
    input: 0.2,
    cache: 0.1,
    output: 0.2,
    aaIndex: 19,
    aaTokens: 22,
    color: "#007298",
    light: "#cdf3ff",
    metrics: { mmlu: 69.4, gpqa: 58.6, code: 52.0, aime: 42.5 }
  },
  {
    id: "31b",
    name: "Gemma 4 31B",
    short: "31B",
    params: "30.7B",
    context: "256K",
    bf16: 69.9,
    q4: 17.5,
    vm: "A100 80GB",
    vmCost: 5.0688,
    input: 0.12,
    cache: 0.06,
    output: 0.35,
    aaIndex: 39,
    aaTokens: 39,
    color: "#652f6c",
    light: "#f9ccff",
    metrics: { mmlu: 85.2, gpqa: 84.3, code: 80.0, aime: 89.2 }
  }
];

const metricRows = [
  { key: "mmlu", label: "MMLU" },
  { key: "gpqa", label: "GPQA" },
  { key: "code", label: "Code" },
  { key: "aime", label: "AIME" }
];

const tokenPriceRows = [
  { label: "Gemma 4 E4B", provider: "Google API", input: 0.2, output: 0.2, color: "#007298" },
  { label: "Gemma 4 31B", provider: "Google API", input: 0.12, output: 0.35, color: "#652f6c" },
  { label: "Gemini 3.5 Flash", provider: "Google", input: 1.5, output: 9, color: "#9e1b32" },
  { label: "Gemini 3.1 Pro", provider: "Google", input: 2, output: 12, color: "#007298" },
  { label: "GPT-5.5", provider: "OpenAI", input: 5, output: 30, color: "#45842a" },
  { label: "Opus 4.7", provider: "Anthropic", input: 5, output: 25, color: "#e77204" }
];

const statRows = [
  ["PARAMS", gemmaModels[0].params, gemmaModels[1].params],
  ["CONTEXT", gemmaModels[0].context, gemmaModels[1].context],
  ["Q4 MEM", "4.5GB", "17.5GB"],
  ["BF16 MEM", "17.9GB", "69.9GB"],
  ["HOST", "L4", "A100"],
  ["VM / H", "$0.70", "$5.07"],
  ["AA INDEX", "19", "39"]
];

function fmtMoney(value, digits = 4) {
  return `$${value.toFixed(digits)}`;
}

function fmtTokenPrice(value) {
  if (value === 0) return "$0";
  if (value < 0.1) return `$${value.toFixed(3)}`;
  if (value < 1) return `$${value.toFixed(2)}`;
  return `$${value.toFixed(2)}`;
}

function drawText(g, text, x, y, ctx, options = {}) {
  ctx.drawHookText(g, text, x, y, {
    anchor: options.anchor ?? "middle",
    baseline: options.baseline ?? "middle",
    size: options.size ?? 16,
    weight: options.weight ?? 800,
    fill: options.fill ?? ctx.palette.brandNeutral,
    opacity: options.opacity ?? 1
  });
}

function drawStageTitle(g, title, t, start, ctx, stageOpacity = 1) {
  const p = stageOpacity * ctx.easeOut((t - start) / 0.6) * (1 - 0.22 * ctx.easeInOut((t - start - 8.8) / 1.2));
  if (p <= 0.01) return;
  drawText(g, title, 462, 56, ctx, {
    anchor: "start",
    size: 24,
    weight: 900,
    fill: ctx.palette.brandPrimary,
    opacity: p
  });
}

function drawStatsPanel(g, t, ctx) {
  const { palette, easeOut } = ctx;
  const D3 = globalThis.d3;
  const panelW = 426;
  g.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", panelW)
    .attr("height", 720)
    .attr("fill", palette.gray100)
    .attr("opacity", 0.98);
  g.append("rect")
    .attr("x", panelW - 1)
    .attr("y", 0)
    .attr("width", 1)
    .attr("height", 720)
    .attr("fill", palette.gray300)
    .attr("opacity", 0.85);

  drawText(g, "Gemma Compare", 28, 42, ctx, {
    anchor: "start",
    size: 24,
    weight: 900,
    fill: palette.brandNeutral
  });

  const cards = [
    { model: gemmaModels[0], x: 28, w: 174 },
    { model: gemmaModels[1], x: 224, w: 174 }
  ];
  cards.forEach((card, index) => {
    const p = easeOut((t - 0.12 - index * 0.08) / 0.58);
    g.append("rect")
      .attr("x", card.x)
      .attr("y", 68)
      .attr("width", card.w)
      .attr("height", 84)
      .attr("fill", "#ffffff")
      .attr("opacity", 0.58 * p);
    g.append("circle")
      .attr("cx", card.x + 14)
      .attr("cy", 93)
      .attr("r", 3.5 * p)
      .attr("fill", card.model.color)
      .attr("opacity", 0.82 * p);
    drawText(g, card.model.name, card.x + 25, 96, ctx, {
      anchor: "start",
      size: 14,
      weight: 900,
      fill: palette.brandNeutral,
      opacity: p
    });
    drawText(g, `${card.model.params} / ${card.model.context}`, card.x + 14, 118, ctx, {
      anchor: "start",
      size: 10.5,
      weight: 820,
      fill: palette.gray700,
      opacity: p
    });
    drawText(g, card.model.id === "e4b" ? "text image audio" : "text image", card.x + 14, 137, ctx, {
      anchor: "start",
      size: 10.5,
      weight: 820,
      fill: palette.gray700,
      opacity: p
    });
  });

  drawText(g, "Benchmarks", 28, 188, ctx, {
    anchor: "start",
    size: 16,
    weight: 900,
    fill: palette.brandNeutral
  });
  const score = D3.scaleLinear().domain([35, 92]).range([122, 384]);
  metricRows.forEach((row, index) => {
    const y = 222 + index * 34;
    const p = easeOut((t - 0.38 - index * 0.08) / 0.55);
    drawText(g, row.label, 28, y + 4, ctx, {
      anchor: "start",
      size: 10.5,
      weight: 850,
      fill: palette.gray700,
      opacity: p
    });
    g.append("line")
      .attr("x1", score(35))
      .attr("x2", score(92))
      .attr("y1", y)
      .attr("y2", y)
      .attr("stroke", palette.gray200)
      .attr("stroke-width", 1.1)
      .attr("opacity", 0.9 * p);
    const x0 = score(gemmaModels[0].metrics[row.key]);
    const x1 = score(gemmaModels[1].metrics[row.key]);
    g.append("line")
      .attr("x1", x0)
      .attr("x2", x0 + (x1 - x0) * p)
      .attr("y1", y)
      .attr("y2", y)
      .attr("stroke", palette.gray500)
      .attr("stroke-width", 2)
      .attr("stroke-linecap", "round")
      .attr("opacity", 0.62 * p);
    gemmaModels.forEach((model) => {
      const dotP = easeOut(p - (model.id === "e4b" ? 0 : 0.12));
      if (dotP <= 0.01) return;
      g.append("circle")
        .attr("cx", score(model.metrics[row.key]))
        .attr("cy", y)
        .attr("r", 6 * dotP)
        .attr("fill", model.color)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.6)
        .attr("opacity", dotP);
    });
  });
  [40, 60, 80].forEach((tick) => {
    const x = score(tick);
    g.append("line")
      .attr("x1", x)
      .attr("x2", x)
      .attr("y1", 354)
      .attr("y2", 362)
      .attr("stroke", palette.gray500)
      .attr("opacity", 0.84);
    drawText(g, String(tick), x, 380, ctx, {
      size: 10,
      weight: 800,
      fill: palette.gray700,
      opacity: 0.9
    });
  });
  g.append("line")
    .attr("x1", score(35))
    .attr("x2", score(92))
    .attr("y1", 358)
    .attr("y2", 358)
    .attr("stroke", palette.gray500)
    .attr("stroke-width", 1.1)
    .attr("opacity", 0.78);

  drawText(g, "Token price / 1M", 28, 438, ctx, {
    anchor: "start",
    size: 16,
    weight: 900,
    fill: palette.brandNeutral
  });
  const priceRows = tokenPriceRows.filter((row) => row.visible !== false);
  const table = { x: 28, y: 486, w: 370, rowH: 25 };
  const metrics = [
    { key: "input", x: 160, w: 64, labelX: 231, fill: palette.blue, opacity: 1 },
    { key: "output", x: 284, w: 64, labelX: 354, fill: palette.purple, opacity: 1 }
  ].map((metric) => ({
    ...metric,
    scale: D3.scaleLinear()
      .domain([0, D3.max(priceRows, (row) => row[metric.key]) || 1])
      .range([0, metric.w])
  }));
  g.append("rect")
    .attr("x", table.x)
    .attr("y", table.y - 17)
    .attr("width", table.w)
    .attr("height", priceRows.length * table.rowH + 8)
    .attr("fill", "#ffffff")
    .attr("opacity", 0.38);
  [
    { label: "MODEL", x: 48, anchor: "start" },
    { label: "INPUT", x: 192 },
    { label: "OUTPUT", x: 316 }
  ].forEach((column) => {
    drawText(g, column.label, column.x, 464, ctx, {
      anchor: column.anchor ?? "middle",
      size: 9,
      weight: 900,
      fill: palette.gray700
    });
  });
  priceRows.forEach((row, rowIndex) => {
    const y = table.y + rowIndex * table.rowH;
    const p = easeOut((t - 0.9 - rowIndex * 0.045) / 0.55);
    g.append("rect")
      .attr("x", table.x)
      .attr("y", y - 15)
      .attr("width", table.w)
      .attr("height", table.rowH)
      .attr("fill", rowIndex % 2 ? palette.gray100 : "#ffffff")
      .attr("opacity", 0.44 * p);
    g.append("circle")
      .attr("cx", 40)
      .attr("cy", y - 3)
      .attr("r", 3.1 * p)
      .attr("fill", row.color)
      .attr("opacity", 0.82 * p);
    drawText(g, row.label, 50, y - 6, ctx, {
      anchor: "start",
      size: 9.4,
      weight: 900,
      fill: palette.brandNeutral,
      opacity: p
    });
    drawText(g, row.provider, 50, y + 6, ctx, {
      anchor: "start",
      size: 7.6,
      weight: 780,
      fill: palette.gray600,
      opacity: p * 0.86
    });
    metrics.forEach((metric) => {
      const value = row[metric.key];
      g.append("rect")
        .attr("x", metric.x)
        .attr("y", y - 10)
        .attr("width", metric.w)
        .attr("height", 13)
        .attr("fill", palette.gray200)
        .attr("opacity", 0.72 * p);
      g.append("rect")
        .attr("x", metric.x)
        .attr("y", y - 10)
        .attr("width", metric.scale(value) * p)
        .attr("height", 13)
        .attr("fill", metric.fill)
        .attr("opacity", metric.opacity * p);
      drawText(g, fmtTokenPrice(value), metric.labelX, y - 3, ctx, {
        anchor: "start",
        size: 8.8,
        weight: 860,
        fill: palette.gray700,
        opacity: p
      });
    });
  });
}

function drawTokenSquare(g, x, y, size, color, opacity, options = {}) {
  g.append("rect")
    .attr("x", x - size / 2)
    .attr("y", y - size / 2)
    .attr("width", size)
    .attr("height", size)
    .attr("rx", options.rx ?? Math.max(2, size * 0.16))
    .attr("fill", color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", Math.max(1, size * 0.12))
    .attr("opacity", opacity);
}

function drawGemmaBox(g, llm, ctx, options = {}) {
  return drawLlmModelBox(g, llm, ctx, {
    opacity: options.opacity ?? 1,
    activation: options.activation ?? 0,
    activationClock: options.activationClock ?? 0,
    textOpacity: options.textOpacity ?? 1,
    labelLines: ["Gemma", "4"],
    labelSize: options.labelSize ?? 42,
    labelGap: options.labelGap ?? 43,
    labelY: options.labelY ?? (llm.y + llm.h / 2 - 26)
  });
}

function seeded01(value) {
  const raw = Math.sin(value * 12.9898 + 78.233) * 43758.5453;
  return raw - Math.floor(raw);
}

function ellipseScore(x, y, cx, cy, rx, ry) {
  return Math.max(0, 1 - (((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2));
}

function globeSignal(x, y) {
  const northAmerica = ellipseScore(x, y, -0.42, -0.16, 0.25, 0.34);
  const southAmerica = ellipseScore(x, y, -0.28, 0.34, 0.15, 0.32);
  const europeAfrica = Math.max(
    ellipseScore(x, y, 0.07, -0.15, 0.2, 0.24),
    ellipseScore(x, y, 0.14, 0.22, 0.2, 0.36)
  );
  const asia = ellipseScore(x, y, 0.42, -0.16, 0.34, 0.26);
  const australia = ellipseScore(x, y, 0.48, 0.42, 0.14, 0.09);
  const polar = ellipseScore(x, y, 0, -0.72, 0.55, 0.07) * 0.4;
  const land = Math.max(northAmerica, southAmerica, europeAfrica, asia, australia, polar);
  return {
    density: land > 0.16 ? 0.28 + land * 0.72 : 0.16 + land * 0.34,
    region: land > 0.16 ? "land" : "water"
  };
}

function getGlobeStippleCells() {
  if (globeStippleCells) return globeStippleCells;
  const D3 = globalThis.d3;
  const sampleStep = 0.095;
  const samples = [];
  for (let y = -0.96; y <= 0.96; y += sampleStep) {
    for (let x = -0.96; x <= 0.96; x += sampleStep) {
      const radius2 = x * x + y * y;
      if (radius2 > 0.96) continue;
      const signal = globeSignal(x, y);
      const horizon = Math.sqrt(Math.max(0.08, 1 - radius2));
      samples.push({
        x,
        y,
        weight: (signal.density ** 1.45) * (0.45 + horizon * 0.55),
        region: signal.region
      });
    }
  }

  let totalWeight = 0;
  const cumulative = samples.map((sample) => {
    totalWeight += sample.weight;
    return totalWeight;
  });
  const sampleAt = (value) => samples[Math.min(samples.length - 1, D3.bisectLeft(cumulative, value))];

  let points = D3.range(118).map((index) => {
    const sample = sampleAt(((index * 0.61803398875 + 0.17) % 1) * totalWeight);
    const jitterX = (seeded01(index + 11) - 0.5) * sampleStep * 0.9;
    const jitterY = (seeded01(index + 29) - 0.5) * sampleStep * 0.9;
    const candidateX = sample.x + jitterX;
    const candidateY = sample.y + jitterY;
    const inGlobe = candidateX * candidateX + candidateY * candidateY <= 0.96;
    const signal = inGlobe ? globeSignal(candidateX, candidateY) : globeSignal(sample.x, sample.y);
    return {
      x: inGlobe ? candidateX : sample.x,
      y: inGlobe ? candidateY : sample.y,
      region: signal.region
    };
  });

  for (let iteration = 0; iteration < 5; iteration += 1) {
    const delaunay = D3.Delaunay.from(points, (point) => point.x, (point) => point.y);
    const accumulators = points.map(() => ({ x: 0, y: 0, weight: 0 }));
    samples.forEach((sample) => {
      const index = delaunay.find(sample.x, sample.y);
      const accumulator = accumulators[index];
      accumulator.x += sample.x * sample.weight;
      accumulator.y += sample.y * sample.weight;
      accumulator.weight += sample.weight;
    });
    points = points.map((point, index) => {
      const accumulator = accumulators[index];
      if (!accumulator.weight) return point;
      return {
        ...point,
        x: accumulator.x / accumulator.weight,
        y: accumulator.y / accumulator.weight
      };
    });
  }

  points.forEach((point, index) => {
    const signal = globeSignal(point.x, point.y);
    point.weight = signal.density;
    point.region = signal.region;
    point.order = index;
  });
  const voronoi = D3.Delaunay.from(points, (point) => point.x, (point) => point.y).voronoi([-1, -1, 1, 1]);
  globeStippleCells = points.map((point, index) => ({
    ...point,
    polygon: voronoi.cellPolygon(index)
  }));
  return globeStippleCells;
}

function globeCellPath(polygon, cx, cy, r) {
  if (!polygon) return "";
  return `M${polygon.map(([px, py]) => `${cx + px * r},${cy + py * r}`).join("L")}Z`;
}

function drawEarth(g, x, y, size, opacity, ctx, local = 1) {
  const { palette, easeOut } = ctx;
  const cells = getGlobeStippleCells();
  const cx = x + size / 2;
  const cy = y + size / 2;
  const r = size * 0.43;
  const reveal = easeOut((local - 0.12) / 1.05);
  const group = g.append("g").attr("opacity", opacity);
  const clipId = `globe-stipple-${Math.round(x)}-${Math.round(y)}`;
  const defs = group.append("defs");
  defs.append("clipPath")
    .attr("id", clipId)
    .append("circle")
    .attr("cx", cx)
    .attr("cy", cy)
    .attr("r", r);

  group.append("circle")
    .attr("cx", cx)
    .attr("cy", cy)
    .attr("r", r)
    .attr("fill", palette.gray100)
    .attr("stroke", palette.gray400)
    .attr("stroke-width", 1.1)
    .attr("opacity", 0.92);

  const clipped = group.append("g").attr("clip-path", `url(#${clipId})`);
  cells.forEach((cell) => {
    const p = ctx.clamp((reveal * cells.length - cell.order) / 18, 0, 1);
    const landFill = cell.weight > 0.72 ? palette.gray600 : cell.weight > 0.46 ? palette.gray500 : palette.gray300;
    clipped.append("path")
      .attr("d", globeCellPath(cell.polygon, cx, cy, r))
      .attr("fill", cell.region === "land" ? landFill : palette.blueHighlight)
      .attr("stroke", cell.region === "land" ? palette.gray200 : palette.gray100)
      .attr("stroke-width", 0.45)
      .attr("opacity", p * (cell.region === "land" ? 0.78 : 0.32));
  });

  [-0.48, 0, 0.48].forEach((offset) => {
    clipped.append("ellipse")
      .attr("cx", cx + offset * r * 0.34)
      .attr("cy", cy)
      .attr("rx", r * (0.22 + Math.abs(offset) * 0.08))
      .attr("ry", r * 0.98)
      .attr("fill", "none")
      .attr("stroke", palette.gray500)
      .attr("stroke-width", 0.8)
      .attr("opacity", 0.18 * reveal);
  });
  [-0.48, 0, 0.48].forEach((lat) => {
    clipped.append("ellipse")
      .attr("cx", cx)
      .attr("cy", cy + lat * r)
      .attr("rx", r * Math.sqrt(1 - lat * lat))
      .attr("ry", r * 0.13)
      .attr("fill", "none")
      .attr("stroke", palette.gray500)
      .attr("stroke-width", 0.8)
      .attr("opacity", 0.16 * reveal);
  });
  cells.forEach((cell) => {
    const p = ctx.clamp((reveal * cells.length - cell.order) / 18, 0, 1);
    if (p <= 0.02) return;
    clipped.append("circle")
      .attr("cx", cx + cell.x * r)
      .attr("cy", cy + cell.y * r)
      .attr("r", cell.region === "land" ? 1.9 + cell.weight * 1.8 : 1.2 + cell.weight)
      .attr("fill", cell.region === "land" ? palette.gray800 : palette.blue)
      .attr("opacity", p * (cell.region === "land" ? 0.4 : 0.18));
  });
  group.append("circle")
    .attr("cx", cx)
    .attr("cy", cy)
    .attr("r", r)
    .attr("fill", "none")
    .attr("stroke", palette.gray600)
    .attr("stroke-width", 1.25)
    .attr("opacity", 0.58 * reveal);
}

function drawTrainingTokens(g, local, opacity, ctx) {
  const start = { x: 560, y: 250 };
  const target = { x: 760, y: 420 };
  for (let i = 0; i < 64; i += 1) {
    const phase = ((local * 0.34 + i * 0.053) % 1);
    const p = ctx.easeInOut(phase);
    const arc = Math.sin(p * Math.PI) * (30 + (i % 6) * 7);
    const x = start.x + (target.x - start.x) * p + Math.sin(i * 1.7) * 38;
    const y = start.y + (target.y - start.y) * p - arc;
    const appear = Math.min(1, phase / 0.13) * Math.min(1, (1 - phase) / 0.12);
    drawTokenSquare(g, x, y, 9 + (i % 4) * 2, tokenColors[i % tokenColors.length], opacity * appear * 0.86);
  }
}

function drawCostMeter(g, x, y, w, value, max, opacity, ctx, label, suffix = "") {
  const { palette } = ctx;
  const p = ctx.clamp(value / max, 0, 1);
  drawText(g, label, x, y - 16, ctx, {
    anchor: "start",
    size: 13,
    weight: 900,
    fill: palette.gray700,
    opacity
  });
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", 20)
    .attr("fill", palette.gray100)
    .attr("opacity", opacity);
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w * p)
    .attr("height", 20)
    .attr("fill", palette.brandPrimary)
    .attr("opacity", opacity * 0.84);
  drawText(g, `${fmtMoney(value, value >= 1 ? 1 : 4)}${suffix}`, x + w + 16, y + 15, ctx, {
    anchor: "start",
    size: 20,
    weight: 900,
    fill: palette.brandPrimary,
    opacity
  });
}

function drawLossChart(g, x, y, w, h, progress, opacity, ctx) {
  const { palette } = ctx;
  const D3 = globalThis.d3;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("fill", "#ffffff")
    .attr("opacity", opacity * 0.82);
  g.append("line")
    .attr("x1", x)
    .attr("y1", y + h)
    .attr("x2", x + w)
    .attr("y2", y + h)
    .attr("stroke", palette.gray500)
    .attr("opacity", opacity);
  g.append("line")
    .attr("x1", x)
    .attr("y1", y)
    .attr("x2", x)
    .attr("y2", y + h)
    .attr("stroke", palette.gray500)
    .attr("opacity", opacity);
  drawText(g, "error rate", x + 8, y + 18, ctx, {
    anchor: "start",
    size: 16,
    weight: 900,
    fill: palette.brandNeutral,
    opacity
  });

  const points = Array.from({ length: 30 }, (_, i) => {
    const u = i / 29;
    const loss = 0.16 + 0.72 * Math.exp(-3.2 * u) + Math.sin(u * 9) * 0.018;
    return [x + u * w, y + (1 - loss) * h];
  });
  const visibleCount = Math.max(2, Math.floor(ctx.clamp(progress, 0, 1) * (points.length - 1)) + 1);
  const visible = points.slice(0, visibleCount);
  g.append("path")
    .attr("d", D3.line().curve(D3.curveCatmullRom.alpha(0.45))(visible))
    .attr("fill", "none")
    .attr("stroke", palette.green)
    .attr("stroke-width", 4)
    .attr("stroke-linecap", "round")
    .attr("opacity", opacity);
  const last = visible.at(-1);
  drawTokenSquare(g, last[0], last[1], 13, palette.green, opacity);
  const error = 42 - ctx.clamp(progress, 0, 1) * 34;
  drawText(g, `${Math.round(error)}%`, x + w - 8, ctx.clamp(last[1] - 20, y + 28, y + h - 18), ctx, {
    anchor: "end",
    size: 22,
    weight: 900,
    fill: palette.green,
    opacity
  });
}

function drawTrainingStage(g, t, ctx) {
  const { palette, easeOut, easeInOut } = ctx;
  const local = t;
  if (local > 10.35) return;
  const opacity = easeOut(local / 0.7) * (1 - easeInOut((local - 9.1) / 1.0));
  if (opacity <= 0.01) return;
  drawStageTitle(g, "Training", t, 0, ctx, opacity);
  drawEarth(g, 486, 168, 158, opacity, ctx, local);
  drawTrainingTokens(g, local, opacity, ctx);
  const llm = { x: 696, y: 338, w: 246, h: 246 };
  drawGemmaBox(g, llm, ctx, {
    opacity,
    activation: 0.34 + 0.5 * (0.5 + Math.sin(local * 2.15) * 0.5),
    activationClock: local
  });
  drawLossChart(g, 994, 172, 214, 214, easeInOut((local - 1.05) / 7.8), opacity, ctx);
  drawCostMeter(g, 984, 466, 160, 5.0 * easeInOut(local / 9.2), 5.0, opacity, ctx, "training cost", "M");
  drawText(g, "multimodal data", 560, 350, ctx, {
    size: 18,
    weight: 900,
    fill: palette.blue,
    opacity: opacity * easeOut((local - 2.2) / 1.1)
  });
}

function matrixCells(capacity, cols = 6) {
  return Array.from({ length: capacity }, (_, i) => ({
    col: i % cols,
    row: Math.floor(i / cols),
    color: tokenColors[i % tokenColors.length]
  }));
}

function drawSparseMatrixPacket(g, x, y, filled, opacity, ctx, options = {}) {
  const { palette } = ctx;
  const cols = options.cols ?? 6;
  const capacity = options.capacity ?? 36;
  const size = options.size ?? 12;
  const gap = options.gap ?? 5;
  const rows = Math.ceil(capacity / cols);
  const group = g.append("g").attr("opacity", opacity);
  group.append("rect")
    .attr("x", x - 10)
    .attr("y", y - 10)
    .attr("width", cols * size + (cols - 1) * gap + 20)
    .attr("height", rows * size + (rows - 1) * gap + 20)
    .attr("fill", options.fill ?? "#ffffff")
    .attr("opacity", 0.82);
  matrixCells(capacity, cols).forEach((cell, index) => {
    const cx = x + cell.col * (size + gap) + size / 2;
    const cy = y + cell.row * (size + gap) + size / 2;
    group.append("rect")
      .attr("x", cx - size / 2)
      .attr("y", cy - size / 2)
      .attr("width", size)
      .attr("height", size)
      .attr("rx", 2)
      .attr("fill", index < filled ? cell.color : palette.gray100)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.2)
      .attr("opacity", index < filled ? 0.88 : 0.78);
  });
}

function inferenceCycles() {
  return [
    { start: 0.35, inCount: 10, outCount: 17, inTokens: 16000, outTokens: 1800, y: 244 },
    { start: 3.35, inCount: 18, outCount: 27, inTokens: 42000, outTokens: 3600, y: 326 },
    { start: 6.35, inCount: 26, outCount: 34, inTokens: 75000, outTokens: 6800, y: 408 }
  ];
}

function cycleTokenCost(cycle, model = gemmaModels[1]) {
  return cycle.inTokens / 1e6 * model.input + cycle.outTokens / 1e6 * model.output;
}

function currentInferenceCost(local) {
  return inferenceCycles().reduce((sum, cycle) => {
    const p = Math.max(0, Math.min(1, (local - cycle.start) / 2.1));
    return sum + cycleTokenCost(cycle) * p;
  }, 0);
}

function drawInferenceCycle(g, cycle, local, opacity, llm, ctx) {
  const { palette, easeInOut, easeOut, lerp } = ctx;
  const raw = (local - cycle.start) / 2.25;
  const p = ctx.clamp(raw, 0, 1);
  if (raw <= -0.08 || raw >= 1.18) return 0;
  const appear = easeOut((raw + 0.06) / 0.22) * (1 - easeInOut((raw - 0.92) / 0.28));
  const leftX = lerp(500, llm.x + 28, easeInOut(p));
  const rightX = lerp(llm.x + llm.w - 42, 1080, easeInOut(p));
  if (p < 0.57) {
    drawSparseMatrixPacket(g, leftX, cycle.y, cycle.inCount, opacity * appear, ctx, {
      fill: palette.blueHighlight,
      size: 10,
      gap: 4
    });
  }
  return p > 0.38 ? { rightX, p, appear } : null;
}

function drawInferenceStage(g, t, ctx) {
  const { palette, clamp, easeOut, easeInOut } = ctx;
  const local = t - 12;
  if (local < 0 || local > 10.35) return;
  const opacity = easeOut(local / 0.75) * (1 - easeInOut((local - 9.25) / 0.9));
  if (opacity <= 0.01) return;
  drawStageTitle(g, "Inference", t, 12, ctx, opacity);
  const llm = { x: 704, y: 216, w: 272, h: 272 };
  const active = inferenceCycles().reduce((max, cycle) => {
    const phase = clamp((local - cycle.start - 0.62) / 1.0, 0, 1) * (1 - clamp((local - cycle.start - 1.68) / 0.55, 0, 1));
    return Math.max(max, phase);
  }, 0);

  const emerging = inferenceCycles().map((cycle) => drawInferenceCycle(g, cycle, local, opacity, llm, ctx));
  drawGemmaBox(g, llm, ctx, {
    opacity,
    activation: 0.18 + 0.62 * active,
    activationClock: local
  });
  emerging.forEach((state, index) => {
    if (!state) return;
    const cycle = inferenceCycles()[index];
    const outputP = easeOut((state.p - 0.38) / 0.4);
    drawSparseMatrixPacket(g, state.rightX, cycle.y - 6, cycle.outCount, opacity * state.appear * outputP, ctx, {
      fill: palette.greenHighlight,
      size: 10,
      gap: 4
    });
    const newCellPulse = Math.sin(ctx.clamp((state.p - 0.5) / 0.35, 0, 1) * Math.PI);
    if (newCellPulse > 0.01) {
      drawTokenSquare(g, state.rightX + 75, cycle.y + 66, 18 + newCellPulse * 8, palette.green, opacity * state.appear * outputP * 0.5);
    }
  });

  const cost = currentInferenceCost(local);
  drawCostMeter(g, 704, 574, 272, cost, 0.036, opacity, ctx, "usage cost");
}

function comparisonCosts() {
  const runs = 12;
  const inTokens = 42000 * runs;
  const outTokens = 3600 * runs;
  return {
    e4b: inTokens / 1e6 * gemmaModels[0].input + outTokens / 1e6 * gemmaModels[0].output,
    b31: inTokens / 1e6 * gemmaModels[1].input + outTokens / 1e6 * gemmaModels[1].output
  };
}

function drawScoreBars(g, x, y, w, model, progress, opacity, ctx) {
  const { palette } = ctx;
  metricRows.forEach((row, index) => {
    const yy = y + index * 22;
    const p = ctx.easeOut(progress - index * 0.08);
    if (p <= 0.01) return;
    drawText(g, row.label, x, yy + 8, ctx, {
      anchor: "start",
      size: 10,
      weight: 850,
      fill: palette.gray700,
      opacity: opacity * p
    });
    g.append("rect")
      .attr("x", x + 48)
      .attr("y", yy)
      .attr("width", w)
      .attr("height", 11)
      .attr("fill", palette.gray100)
      .attr("opacity", opacity * p);
    g.append("rect")
      .attr("x", x + 48)
      .attr("y", yy)
      .attr("width", w * (model.metrics[row.key] / 92) * p)
      .attr("height", 11)
      .attr("fill", model.color)
      .attr("opacity", opacity * p * 0.84);
  });
}

function drawCompactPipeline(g, y, model, cost, progress, opacity, ctx) {
  const { palette, easeInOut, easeOut, lerp } = ctx;
  const p = easeOut(progress);
  if (p <= 0.01) return;
  const llm = { x: 684, y: y - 70, w: 150, h: 150 };
  const packetP = easeInOut(ctx.clamp(progress * 1.2, 0, 1));
  const inputX = lerp(488, llm.x + 20, packetP);
  if (packetP < 0.62) {
    drawSparseMatrixPacket(g, inputX, y - 26, 16, opacity * p, ctx, {
      fill: "#ffffff",
      size: 8,
      gap: 4
    });
  }
  drawGemmaBox(g, llm, ctx, {
    opacity: opacity * p,
    activation: 0.24 + 0.5 * p,
    activationClock: progress * 3.2,
    labelSize: 27,
    labelGap: 28,
    labelY: llm.y + llm.h / 2 - 18
  });
  drawSparseMatrixPacket(g, lerp(llm.x + llm.w - 24, 882, packetP), y - 32, 24, opacity * p * ctx.clamp((packetP - 0.3) / 0.5, 0, 1), ctx, {
    fill: "#ffffff",
    size: 8,
    gap: 4
  });
  drawText(g, model.name, 520, y - 70, ctx, {
    anchor: "start",
    size: 17,
    weight: 900,
    fill: model.color,
    opacity: opacity * p
  });
  drawText(g, `${model.context} / ${model.vm}`, 520, y - 48, ctx, {
    anchor: "start",
    size: 11,
    weight: 850,
    fill: palette.gray700,
    opacity: opacity * p
  });
  drawScoreBars(g, 1000, y - 54, 116, model, p, opacity, ctx);
  g.append("rect")
    .attr("x", 1000)
    .attr("y", y + 48)
    .attr("width", 136)
    .attr("height", 14)
    .attr("fill", palette.gray100)
    .attr("opacity", opacity * p);
  g.append("rect")
    .attr("x", 1000)
    .attr("y", y + 48)
    .attr("width", Math.min(136, cost / 0.13 * 136))
    .attr("height", 14)
    .attr("fill", model.color)
    .attr("opacity", opacity * p * 0.82);
  drawText(g, `$${cost.toFixed(3)}`, 1154, y + 56, ctx, {
    anchor: "start",
    size: 16,
    weight: 900,
    fill: model.color,
    opacity: opacity * p
  });
}

function familyColor(point, ctx) {
  if (point.model.startsWith("claude")) return ctx.palette.orange;
  if (point.model.startsWith("gpt")) return ctx.palette.green;
  if (point.model.startsWith("gemini")) return ctx.palette.blue;
  if (point.model.startsWith("kimi")) return ctx.palette.brandPrimary;
  if (point.model.startsWith("glm")) return ctx.palette.information;
  return ctx.palette.gray700;
}

function partialPolylinePath(points, progress) {
  if (points.length < 2) return "";
  const p = Math.max(0, Math.min(1, progress));
  const target = p * (points.length - 1);
  const full = Math.floor(target);
  const frac = target - full;
  const out = [points[0]];
  for (let index = 1; index <= full && index < points.length; index += 1) out.push(points[index]);
  if (full < points.length - 1) {
    const a = points[full];
    const b = points[full + 1];
    out.push([a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac]);
  }
  return out.map((point, index) => `${index === 0 ? "M" : "L"}${point[0]},${point[1]}`).join("");
}

function deepSweLabel(point) {
  const labels = {
    "claude-fable-5|high": { text: "claude-fable-5 [high]", sub: "Default", dx: -16, dy: 22, anchor: "end" },
    "gpt-5-5|medium": { text: "gpt-5.5 [medium]", sub: "Default", dx: 18, dy: -10, anchor: "start" },
    "claude-opus-4-8|high": { text: "claude-opus-4.8 [high]", sub: "Default", dx: -12, dy: 18, anchor: "end" },
    "glm-5-2|max": { text: "glm-5.2 [max]", dx: 14, dy: 10, anchor: "start" },
    "gemini-3-5-flash|medium": { text: "gemini-3.5-flash [medium]", dx: 12, dy: 8, anchor: "start" },
    "kimi-k2-7-code|": { text: "kimi-k2.7-code", dx: 12, dy: 5, anchor: "start" },
    "claude-sonnet-4-6|high": { text: "claude-sonnet-4.6 [high]", dx: -12, dy: 5, anchor: "end" },
    "gemini-3-1-pro-preview|high": { text: "gemini-3.1-pro [high]", dx: 12, dy: 5, anchor: "start" }
  };
  return labels[`${point.model}|${point.effort}`] ?? null;
}

function drawAxisLabel(g, text, x, y, ctx, options = {}) {
  drawText(g, text, x, y, ctx, {
    anchor: options.anchor ?? "middle",
    size: options.size ?? 12,
    weight: options.weight ?? 850,
    fill: options.fill ?? ctx.palette.gray700,
    opacity: options.opacity ?? 1
  });
}

function drawDeepSweChart(g, local, opacity, ctx) {
  const D3 = globalThis.d3;
  const p = ctx.easeOut(local / 0.82);
  if (p <= 0.01) return;
  const x = 498;
  const y = 148;
  const w = 650;
  const h = 408;
  const axisP = ctx.easeOut((local - 0.1) / 0.78);
  const lineP = ctx.easeOut((local - 0.9) / 2.1);
  const labelP = ctx.easeOut((local - 3.0) / 0.9);
  const xScale = D3.scaleLinear().domain([22.5, 0]).range([x, x + w]);
  const yScale = D3.scaleLinear().domain([0, 0.8]).range([y + h, y]);
  const byModel = D3.group(deepSweV11Points, (point) => point.model);
  const group = g.append("g").attr("opacity", opacity * p);

  group.append("rect")
    .attr("x", 426)
    .attr("y", 0)
    .attr("width", 854)
    .attr("height", 720)
    .attr("fill", "#ffffff")
    .attr("opacity", 0.72);
  drawText(group, "DeepSWE", x, 58, ctx, {
    anchor: "start",
    size: 30,
    weight: 900,
    fill: ctx.palette.brandNeutral
  });
  [["v1.1", true], ["Cost", true], ["Output tokens", false], ["Agent steps", false]].forEach(([label, active], index) => {
    const widths = [38, 48, 96, 86];
    const xx = x + index * 0 + widths.slice(0, index).reduce((sum, item) => sum + item + 8, 0);
    group.append("rect")
      .attr("x", xx)
      .attr("y", 78)
      .attr("width", widths[index])
      .attr("height", 24)
      .attr("fill", active ? ctx.palette.black : "#ffffff")
      .attr("stroke", ctx.palette.gray200)
      .attr("opacity", axisP);
    drawAxisLabel(group, label, xx + widths[index] / 2, 94, ctx, {
      size: 10.5,
      fill: active ? "#ffffff" : ctx.palette.gray700,
      opacity: axisP
    });
  });
  drawAxisLabel(group, "113 tasks - updated Jun 20, 2026", x + w, 93, ctx, {
    anchor: "end",
    size: 11,
    opacity: axisP * 0.82
  });
  drawAxisLabel(group, "DeepSWE score", x, y - 18, ctx, {
    anchor: "start",
    size: 14,
    weight: 900,
    opacity: axisP
  });

  D3.range(0, 0.81, 0.1).forEach((tick) => {
    const yy = yScale(tick);
    group.append("line")
      .attr("x1", x)
      .attr("y1", yy)
      .attr("x2", x + w * axisP)
      .attr("y2", yy)
      .attr("stroke", ctx.palette.gray100)
      .attr("stroke-width", 1.4)
      .attr("opacity", axisP);
    if (Math.round(tick * 10) % 2 === 0) {
      drawAxisLabel(group, `${Math.round(tick * 100)}%`, x - 16, yy + 4, ctx, {
        anchor: "end",
        size: 11,
        opacity: axisP * 0.88
      });
    }
  });

  [20, 15, 10, 5, 0].forEach((tick) => {
    const xx = xScale(tick);
    group.append("line")
      .attr("x1", xx)
      .attr("y1", y)
      .attr("x2", xx)
      .attr("y2", y + h * axisP)
      .attr("stroke", ctx.palette.gray100)
      .attr("stroke-width", 1.2)
      .attr("opacity", axisP);
    group.append("line")
      .attr("x1", xx)
      .attr("y1", y + h)
      .attr("x2", xx)
      .attr("y2", y + h + 8)
      .attr("stroke", ctx.palette.gray500)
      .attr("stroke-width", 1.4)
      .attr("opacity", axisP);
    drawAxisLabel(group, tick === 0 ? "$0" : tick === 5 ? "$5.00" : `$${tick}`, xx, y + h + 27, ctx, {
      size: 11,
      opacity: axisP * 0.88
    });
  });

  group.append("line")
    .attr("x1", x)
    .attr("y1", y + h)
    .attr("x2", x + w * axisP)
    .attr("y2", y + h)
    .attr("stroke", ctx.palette.gray700)
    .attr("stroke-width", 2.2)
    .attr("opacity", axisP);
  group.append("line")
    .attr("x1", x)
    .attr("y1", y + h)
    .attr("x2", x)
    .attr("y2", y + h - h * axisP)
    .attr("stroke", ctx.palette.gray700)
    .attr("stroke-width", 2.2)
    .attr("opacity", axisP);

  drawAxisLabel(group, "Avg cost per task", x + w / 2, y + h + 50, ctx, {
    size: 12,
    fill: ctx.palette.black,
    opacity: axisP
  });

  byModel.forEach((points) => {
    const sorted = points.slice().sort((a, b) => D3.descending(a.cost, b.cost));
    const color = familyColor(sorted[0], ctx);
    const linePoints = sorted.map((point) => [xScale(point.cost), yScale(point.passRate)]);
    group.append("path")
      .attr("d", partialPolylinePath(linePoints, lineP))
      .attr("fill", "none")
      .attr("stroke", color)
      .attr("stroke-width", 2.2)
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round")
      .attr("opacity", 0.58 * lineP);
  });

  deepSweV11Points.forEach((point, index) => {
    const reveal = ctx.easeOut((local - 1.0 - index * 0.035) / 0.46);
    if (reveal <= 0.01) return;
    const cx = xScale(point.cost);
    const cy = yScale(point.passRate);
    const color = familyColor(point, ctx);
    group.append("circle")
      .attr("cx", cx)
      .attr("cy", cy)
      .attr("r", 6 * reveal)
      .attr("fill", color)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.8)
      .attr("opacity", 0.92 * reveal);
    const label = deepSweLabel(point);
    if (label && labelP > 0.01) {
      drawText(group, label.text, cx + label.dx, cy + label.dy, ctx, {
        anchor: label.anchor,
        size: 10.2,
        weight: 850,
        fill: color,
        opacity: labelP
      });
      if (label.sub) {
        drawText(group, label.sub, cx + label.dx, cy + label.dy + 14, ctx, {
          anchor: label.anchor,
          size: 7.8,
          weight: 800,
          fill: color,
          opacity: labelP * 0.72
        });
      }
    }
  });

  drawAxisLabel(group, "most efficient ->", x + w - 78, y + 18, ctx, {
    anchor: "start",
    size: 10,
    fill: ctx.palette.gray700,
    opacity: labelP * 0.85
  });
}

function drawCompareStage(g, t, ctx) {
  const { clamp, easeOut } = ctx;
  const local = clamp(t - 24, 0, 10);
  const opacity = easeOut(local / 0.8);
  if (opacity <= 0.01) return;
  drawDeepSweChart(g, local, opacity, ctx);
}

export function drawLlmImplicationVisualOnly(g, ctx) {
  const { sceneProgress, clamp } = ctx;
  const t = clamp(sceneProgress * 34, 0, 34);
  drawStatsPanel(g, t, ctx);
  drawTrainingStage(g, t, ctx);
  drawInferenceStage(g, t, ctx);
  drawCompareStage(g, t, ctx);
}

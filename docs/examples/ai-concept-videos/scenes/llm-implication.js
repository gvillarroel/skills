const continuationTokens = [
  { raw: " tests", piece: "tests", color: "#652f6c" },
  { raw: " for", piece: "for", color: "#007298" },
  { raw: " bugs", piece: "bugs", color: "#45842a" },
  { raw: ".", piece: ".", color: "#9e1b32" }
];

const outputSmall = [
  { piece: "fix", color: "#45842a" },
  { piece: "bug", color: "#007298" },
  { piece: ".", color: "#9e1b32" }
];

const outputLarge = [
  { piece: "write", color: "#e77204" },
  { piece: "tests", color: "#652f6c" },
  { piece: "then", color: "#007298" },
  { piece: "fix", color: "#45842a" },
  { piece: ".", color: "#9e1b32" }
];

const realModelFacts = {
  scout: {
    title: "Llama 4 Scout",
    totalParams: "109B",
    activeParams: "17B",
    experts: "16E",
    h100: "1x H100",
    h100Memory: "80GB",
    inputPrice: "$0.18",
    outputPrice: "$0.59",
    color: "#007298"
  },
  maverick: {
    title: "Llama 4 Maverick",
    totalParams: "401.6B",
    activeParams: "17B",
    experts: "128E",
    h100: "8x H100",
    h100Memory: "640GB",
    inputPrice: "$0.27",
    outputPrice: "$0.85",
    color: "#652f6c"
  }
};

function tokenWidth(piece, scale = 1) {
  if (piece === "." || piece === ",") return 30 * scale;
  return Math.max(46 * scale, piece.length * 11 * scale + 24 * scale);
}

function drawTokenPill(g, token, x, y, scale, opacity, ctx, options = {}) {
  const { drawHookText, palette } = ctx;
  const w = options.width ?? tokenWidth(token.piece, scale);
  const h = 30 * scale;
  const fill = options.solid ? token.color : "#ffffff";
  const textFill = options.solid ? "#ffffff" : token.color;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", 7 * scale)
    .attr("fill", fill)
    .attr("stroke", options.solid ? "none" : token.color)
    .attr("stroke-width", 2 * scale)
    .attr("opacity", opacity);
  if (options.noise) {
    g.append("line")
      .attr("x1", x + 7 * scale)
      .attr("y1", y + h - 7 * scale)
      .attr("x2", x + w - 7 * scale)
      .attr("y2", y + 7 * scale)
      .attr("stroke", palette.gray500)
      .attr("stroke-width", 1.8 * scale)
      .attr("opacity", opacity * 0.7);
  }
  drawHookText(g, token.piece, x + w / 2, y + h / 2 + 1, {
    size: 13 * scale,
    weight: 850,
    fill: textFill,
    opacity
  });
  return { x, y, w, h };
}

function drawTokenRow(g, tokens, centerX, y, scale, opacity, ctx, options = {}) {
  const gap = 8 * scale;
  const widths = tokens.map((token) => tokenWidth(token.piece, scale));
  const total = widths.reduce((sum, width) => sum + width, 0) + gap * (tokens.length - 1);
  let x = centerX - total / 2;
  return tokens.map((token, index) => {
    const pill = drawTokenPill(g, token, x, y, scale, opacity, ctx, {
      solid: options.solid,
      noise: options.noiseIndexes?.includes(index)
    });
    x += widths[index] + gap;
    return pill;
  });
}

function drawContextStrip(g, tokens, centerX, y, opacity, ctx, options = {}) {
  const { palette } = ctx;
  const size = options.size ?? 16;
  const gap = options.gap ?? 9;
  const total = tokens.length * size + (tokens.length - 1) * gap;
  let x = centerX - total / 2;
  tokens.forEach((token, index) => {
    const noisy = options.noiseIndexes?.includes(index);
    const fill = noisy ? palette.gray300 : token.color;
    const cellOpacity = opacity * (noisy ? 0.48 : 0.82);
    g.append("rect")
      .attr("x", x)
      .attr("y", y)
      .attr("width", size)
      .attr("height", size)
      .attr("rx", 4)
      .attr("fill", fill)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.7)
      .attr("opacity", cellOpacity);
    if (noisy) {
      g.append("line")
        .attr("x1", x + 3)
        .attr("y1", y + size - 3)
        .attr("x2", x + size - 3)
        .attr("y2", y + 3)
        .attr("stroke", palette.gray600)
        .attr("stroke-width", 1.7)
        .attr("stroke-linecap", "round")
        .attr("opacity", opacity * 0.55);
    }
    x += size + gap;
  });
}

function drawConsistentLlmBox(g, box, activation, ctx) {
  const { palette, pulse, drawHookText } = ctx;
  const group = g.append("g");
  group.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.brandPrimary)
    .attr("stroke-width", box.stroke ?? 3.6)
    .attr("opacity", 0.98);

  ["Large", "Language", "Model"].forEach((word, index) => {
    drawHookText(group, word, box.x + box.w / 2, box.y + 100 + index * 39, {
      size: 36,
      weight: 870,
      fill: palette.brandNeutral,
      opacity: 0.96
    });
  });

  const layers = [3, 4, 3];
  const network = {
    x: box.x + 178,
    y: box.y + 190,
    layerGap: 28,
    nodeGap: 17
  };
  const nodeMax = Math.max(...layers);
  const nodePositions = layers.map((count, layer) => {
    const x = network.x + layer * network.layerGap;
    const startY = network.y + ((nodeMax - count) * network.nodeGap) / 2;
    return Array.from({ length: count }, (_, index) => ({
      x,
      y: startY + index * network.nodeGap
    }));
  });

  for (let layer = 0; layer < nodePositions.length - 1; layer += 1) {
    nodePositions[layer].forEach((from, fromIndex) => {
      nodePositions[layer + 1].forEach((to, toIndex) => {
        const phase = (fromIndex + toIndex + layer) % 3;
        group.append("line")
          .attr("x1", from.x)
          .attr("y1", from.y)
          .attr("x2", to.x)
          .attr("y2", to.y)
          .attr("stroke", activation > 0.35 ? palette.blue : palette.gray400)
          .attr("stroke-width", 1.2 + activation * 0.8)
          .attr("opacity", 0.34 + activation * (phase === 0 ? 0.24 : 0.12));
      });
    });
  }

  nodePositions.flat().forEach((node, index) => {
    group.append("circle")
      .attr("cx", node.x)
      .attr("cy", node.y)
      .attr("r", 4.4 + activation * 1.4 + pulse * 0.35)
      .attr("fill", activation > 0.4 ? palette.blue : palette.gray600)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.4)
      .attr("opacity", 0.62 + activation * 0.22 - (index % 2) * 0.05);
  });
}

function drawPromptSplit(g, tokens, smallBox, largeBox, t, ctx) {
  const { palette, clamp, easeInOut } = ctx;
  const rowP = ctx.easeOut((t - 1.3) / 1.2);
  if (rowP > 0.01) {
    drawTokenRow(g, tokens, 640, 68, 0.88, rowP, ctx);
  }
  const splitP = clamp((t - 4.2) / 4.6, 0, 1);
  if (splitP <= 0.01) return;
  const leftTarget = { x: smallBox.x + smallBox.w / 2, y: smallBox.y - 16 };
  const rightTarget = { x: largeBox.x + largeBox.w / 2, y: largeBox.y - 16 };
  const source = { x: 640, y: 116 };
  [
    { target: leftTarget, color: palette.blue },
    { target: rightTarget, color: palette.purple }
  ].forEach((lane) => {
    g.append("line")
      .attr("x1", source.x)
      .attr("y1", source.y)
      .attr("x2", lane.target.x)
      .attr("y2", lane.target.y)
      .attr("stroke", lane.color)
      .attr("stroke-width", 2.6)
      .attr("stroke-linecap", "round")
      .attr("opacity", 0.08 + splitP * 0.2);
  });
  tokens.slice(0, 6).forEach((token, index) => {
    const p = easeInOut(splitP * 1.16 - index * 0.04);
    if (p <= 0.01 || p >= 0.99) return;
    [
      { target: leftTarget, offset: -1 },
      { target: rightTarget, offset: 1 }
    ].forEach((lane) => {
      g.append("rect")
        .attr("x", source.x - 6 + (lane.target.x - source.x) * p + lane.offset * index * 3)
        .attr("y", source.y - 6 + (lane.target.y - source.y) * p)
        .attr("width", 12)
        .attr("height", 12)
        .attr("rx", 3)
        .attr("fill", token.color)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.2)
        .attr("opacity", 0.82);
    });
  });
}

function drawOutputRow(g, tokens, centerX, y, t, start, ctx) {
  const { easeOut } = ctx;
  const reveal = easeOut((t - start) / 2.2);
  if (reveal <= 0.01) return;
  const visible = Math.min(tokens.length, Math.floor(reveal * (tokens.length + 0.65)));
  drawTokenRow(g, tokens.slice(0, visible), centerX, y, 0.86, reveal, ctx, { solid: true });
}

function drawGpuMark(g, x, y, count, opacity, ctx) {
  const { palette } = ctx;
  const visible = Math.min(count, 8);
  const cols = count === 1 ? 1 : 4;
  const size = count === 1 ? 28 : 14;
  const gap = count === 1 ? 0 : 7;
  for (let i = 0; i < visible; i += 1) {
    const col = i % cols;
    const row = Math.floor(i / cols);
    g.append("rect")
      .attr("x", x + col * (size + gap))
      .attr("y", y + row * (size + gap))
      .attr("width", size)
      .attr("height", size)
      .attr("rx", 4)
      .attr("fill", i === 0 ? palette.green : palette.gray300)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.6)
      .attr("opacity", opacity);
  }
}

function drawFactPill(g, x, y, w, h, label, value, color, opacity, ctx) {
  const { palette, drawHookText } = ctx;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", 7)
    .attr("fill", "#ffffff")
    .attr("stroke", color)
    .attr("stroke-width", 2)
    .attr("opacity", opacity);
  drawHookText(g, label, x + 10, y + 12, {
    anchor: "start",
    size: 10,
    weight: 760,
    fill: palette.gray600,
    opacity
  });
  drawHookText(g, value, x + w / 2, y + 30, {
    size: 19,
    weight: 880,
    fill: color,
    opacity
  });
}

function drawUsagePulse(g, x, y, w, color, t, opacity) {
  const phase = 0.5 + Math.sin(t * 2.2) * 0.5;
  const cx = x + 16 + (w - 32) * phase;
  g.append("circle")
    .attr("cx", cx)
    .attr("cy", y)
    .attr("r", 4.8)
    .attr("fill", color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.7)
    .attr("opacity", opacity * 0.9);
  g.append("circle")
    .attr("cx", cx)
    .attr("cy", y)
    .attr("r", 9 + Math.sin(t * 3.4) * 1.4)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 1.8)
    .attr("opacity", opacity * 0.32);
}

function drawModelFactPanel(g, fact, x, y, w, t, start, ctx, options = {}) {
  const { palette, easeOut, drawHookText } = ctx;
  const p = easeOut((t - start) / 2.1);
  if (p <= 0.01) return;

  const group = g.append("g").attr("opacity", p);
  group.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", 194)
    .attr("rx", 8)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 1.4)
    .attr("opacity", 0.94);

  group.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", 31)
    .attr("rx", 8)
    .attr("fill", options.headerFill ?? palette.gray100)
    .attr("opacity", 0.92);
  drawHookText(group, "Meta", x + 18, y + 20, {
    anchor: "start",
    size: 13,
    weight: 860,
    fill: palette.blue,
    opacity: 1
  });
  drawHookText(group, fact.title, x + w - 14, y + 20, {
    anchor: "end",
    size: 13,
    weight: 860,
    fill: palette.brandNeutral,
    opacity: 1
  });

  const pillW = (w - 36) / 2;
  drawFactPill(group, x + 12, y + 43, pillW, 42, "TOTAL", fact.totalParams, fact.color, 1, ctx);
  drawFactPill(group, x + 24 + pillW, y + 43, pillW, 42, "ACTIVE", fact.activeParams, palette.green, 1, ctx);

  const infraY = y + 99;
  group.append("rect")
    .attr("x", x + 12)
    .attr("y", infraY)
    .attr("width", w - 24)
    .attr("height", 42)
    .attr("rx", 7)
    .attr("fill", palette.gray100)
    .attr("opacity", 0.76);
  drawHookText(group, "NVIDIA H100", x + 24, infraY + 17, {
    anchor: "start",
    size: 11,
    weight: 860,
    fill: palette.greenHover,
    opacity: 1
  });
  drawHookText(group, `${fact.h100} ${fact.h100Memory}`, x + 24, infraY + 32, {
    anchor: "start",
    size: 12,
    weight: 840,
    fill: palette.brandNeutral,
    opacity: 1
  });
  drawGpuMark(group, x + w - (options.gpuCount === 1 ? 48 : 104), infraY + 7, options.gpuCount ?? 1, 1, ctx);

  const priceY = y + 151;
  const priceOpacity = easeOut((t - (start + 4.2)) / 1.4);
  if (priceOpacity > 0.01) {
    const priceGroup = g.append("g").attr("opacity", priceOpacity * p);
    const priceW = (w - 36) / 2;
    drawFactPill(priceGroup, x + 12, priceY, priceW, 42, "IN / 1M", fact.inputPrice, palette.orange, 1, ctx);
    drawFactPill(priceGroup, x + 24 + priceW, priceY, priceW, 42, "OUT / 1M", fact.outputPrice, palette.red, 1, ctx);
    drawUsagePulse(priceGroup, x + 12, priceY + 37, priceW, palette.orange, t, 1);
    drawUsagePulse(priceGroup, x + 24 + priceW, priceY + 37, priceW, palette.red, t + 0.7, 1);
  }

}

function drawModelNames(g, smallBox, largeBox, t, ctx) {
  const { palette, easeOut, drawHookText } = ctx;
  const p = easeOut((t - 7.8) / 1.4);
  if (p <= 0.01) return;
  [
    { box: smallBox, fact: realModelFacts.scout },
    { box: largeBox, fact: realModelFacts.maverick }
  ].forEach(({ box, fact }) => {
    drawHookText(g, fact.title, box.x + box.w / 2, box.y - 24, {
      size: 17,
      weight: 880,
      fill: palette.brandNeutral,
      opacity: p
    });
  });
}

export function drawLlmImplicationVisualOnly(g, ctx) {
  const { palette, hookTokens, sceneProgress, clamp, easeOut, pulse } = ctx;
  const t = clamp(sceneProgress * 34, 0, 34);
  const introP = easeOut((t - 0.3) / 1.55);
  if (introP <= 0.01) return;
  const group = g.append("g").attr("opacity", introP);
  const promptTokens = [...hookTokens, ...continuationTokens];
  const smallBox = { x: 126, y: 190, w: 270, h: 270, stroke: 4 };
  const largeBox = { x: 884, y: 190, w: 270, h: 270, stroke: 4 };

  drawPromptSplit(group, promptTokens, smallBox, largeBox, t, ctx);
  drawConsistentLlmBox(group, smallBox, clamp((t - 8.2) / 4.5, 0, 1), { ...ctx, pulse });
  drawConsistentLlmBox(group, largeBox, clamp((t - 8.2) / 4.5, 0, 1), { ...ctx, pulse });
  drawModelNames(group, smallBox, largeBox, t, ctx);

  drawOutputRow(group, outputSmall, smallBox.x + smallBox.w / 2, 474, t, 14.8, ctx);
  drawOutputRow(group, outputLarge, largeBox.x + largeBox.w / 2, 474, t, 16.0, ctx);

  drawModelFactPanel(group, realModelFacts.scout, 86, 514, 390, t, 13.2, ctx, {
    gpuCount: 1,
    headerFill: palette.blueHighlight
  });
  drawModelFactPanel(group, realModelFacts.maverick, 790, 514, 410, t, 14.1, ctx, {
    gpuCount: 8,
    headerFill: palette.purpleHighlight
  });

}

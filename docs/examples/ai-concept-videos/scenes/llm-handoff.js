const promptTokens = [
  { piece: "AI", color: "#007298" },
  { piece: "tools", color: "#45842a" },
  { piece: "write", color: "#e77204" },
  { piece: "code", color: "#9e1b32" }
];

const outputTokens = [
  { piece: "tests", color: "#652f6c" },
  { piece: "pass", color: "#45842a" },
  { piece: ".", color: "#9e1b32" }
];

const retryTokens = [
  { piece: "fix", color: "#e77204" },
  { piece: "edge", color: "#007298" },
  { piece: "case", color: "#652f6c" }
];

function drawText(g, text, x, y, ctx, options = {}) {
  ctx.drawHookText(g, text, x, y, {
    size: options.size ?? 18,
    weight: options.weight ?? 820,
    fill: options.fill ?? ctx.palette.brandNeutral,
    opacity: options.opacity ?? 1,
    anchor: options.anchor,
    baseline: options.baseline
  });
}

function tokenWidth(piece, scale = 1) {
  return Math.max(32 * scale, piece.length * 10.5 * scale + 22 * scale);
}

function drawMiniToken(g, token, x, y, ctx, options = {}) {
  const scale = options.scale ?? 1;
  const width = options.width ?? tokenWidth(token.piece, scale);
  const height = 28 * scale;
  const opacity = options.opacity ?? 1;
  const solid = options.solid ?? false;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", width)
    .attr("height", height)
    .attr("rx", 6 * scale)
    .attr("fill", solid ? token.color : "#ffffff")
    .attr("stroke", solid ? "none" : token.color)
    .attr("stroke-width", 2 * scale)
    .attr("opacity", opacity);
  drawText(g, token.piece, x + width / 2, y + height / 2 + 1, ctx, {
    size: 13 * scale,
    weight: 850,
    fill: solid ? "#ffffff" : token.color,
    opacity
  });
  return { x, y, width, height };
}

function drawTokenRow(g, tokens, centerX, y, ctx, options = {}) {
  const scale = options.scale ?? 1;
  const gap = 8 * scale;
  const widths = tokens.map((token) => tokenWidth(token.piece, scale));
  const total = widths.reduce((sum, width) => sum + width, 0) + gap * (tokens.length - 1);
  let x = centerX - total / 2;
  return tokens.map((token, index) => {
    const box = drawMiniToken(g, token, x, y, ctx, {
      scale,
      opacity: options.opacity ?? 1,
      solid: options.solid ?? false
    });
    x += widths[index] + gap;
    return box;
  });
}

function drawArrowLine(g, from, to, color, opacity, width = 3) {
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
  const size = 10 + width;
  const left = {
    x: to.x - Math.cos(angle - Math.PI / 6) * size,
    y: to.y - Math.sin(angle - Math.PI / 6) * size
  };
  const right = {
    x: to.x - Math.cos(angle + Math.PI / 6) * size,
    y: to.y - Math.sin(angle + Math.PI / 6) * size
  };
  g.append("path")
    .attr("d", `M${to.x},${to.y} L${left.x},${left.y} L${right.x},${right.y} Z`)
    .attr("fill", color)
    .attr("opacity", opacity);
}

function drawConsistentLlmBox(g, box, activation, ctx) {
  const { palette, pulse } = ctx;
  const group = g.append("g");
  group.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.brandPrimary)
    .attr("stroke-width", 3.6)
    .attr("opacity", 0.98);

  ["Large", "Language", "Model"].forEach((word, index) => {
    drawText(group, word, box.x + box.w / 2, box.y + 100 + index * 39, ctx, {
      size: 36,
      weight: 870,
      fill: palette.brandNeutral,
      opacity: 0.96
    });
  });

  const layers = [3, 4, 3];
  const nodeMax = Math.max(...layers);
  const origin = {
    x: box.x + 178,
    y: box.y + 190,
    layerGap: 28,
    nodeGap: 17
  };
  const nodePositions = layers.map((count, layer) => {
    const x = origin.x + layer * origin.layerGap;
    const startY = origin.y + ((nodeMax - count) * origin.nodeGap) / 2;
    return Array.from({ length: count }, (_, index) => ({
      x,
      y: startY + index * origin.nodeGap
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

function matrixLayout(box, cols = 8, rows = 8) {
  const gap = 8;
  const cell = Math.floor(Math.min((box.w - gap * (cols - 1)) / cols, (box.h - gap * (rows - 1)) / rows));
  const width = cols * cell + (cols - 1) * gap;
  const height = rows * cell + (rows - 1) * gap;
  const grid = {
    x: box.x + (box.w - width) / 2,
    y: box.y + (box.h - height) / 2
  };
  return {
    cols,
    rows,
    cell,
    gap,
    grid,
    slot(index) {
      return {
        x: grid.x + (index % cols) * (cell + gap),
        y: grid.y + Math.floor(index / cols) * (cell + gap),
        w: cell,
        h: cell
      };
    }
  };
}

function drawContextMatrix(g, box, tokens, ctx, options = {}) {
  const { palette } = ctx;
  const opacity = options.opacity ?? 1;
  const layout = matrixLayout(box, options.cols ?? 8, options.rows ?? 8);
  g.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 16)
    .attr("fill", "#ffffff")
    .attr("stroke", "none")
    .attr("opacity", opacity * 0.94);
  d3.range(layout.cols * layout.rows).forEach((index) => {
    const slot = layout.slot(index);
    g.append("rect")
      .attr("x", slot.x)
      .attr("y", slot.y)
      .attr("width", slot.w)
      .attr("height", slot.h)
      .attr("rx", 4)
      .attr("fill", palette.gray100)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.6)
      .attr("opacity", opacity * 0.74);
  });
  tokens.forEach((token, index) => {
    const slot = layout.slot(index);
    g.append("rect")
      .attr("x", slot.x)
      .attr("y", slot.y)
      .attr("width", slot.w)
      .attr("height", slot.h)
      .attr("rx", 4)
      .attr("fill", token.color)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.8)
      .attr("opacity", opacity * (token.opacity ?? 0.95));
  });
  return layout;
}

function drawTokenParticle(g, from, to, progress, token, ctx, options = {}) {
  const p = ctx.easeInOut(progress);
  if (p <= 0 || p >= 1) return;
  const x = ctx.lerp(from.x, to.x, p);
  const y = ctx.lerp(from.y, to.y, p) + Math.sin(p * Math.PI) * (options.arc ?? 0);
  g.append("rect")
    .attr("x", x - 8)
    .attr("y", y - 8)
    .attr("width", 16)
    .attr("height", 16)
    .attr("rx", 4)
    .attr("fill", token.color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.6)
    .attr("opacity", options.opacity ?? 0.9);
}

function drawMeter(g, box, t, ctx) {
  const { palette, clamp, easeOut } = ctx;
  const group = g.append("g");
  const fillP = easeOut((t - 5.0) / 12.0);
  group.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 18)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 2)
    .attr("opacity", 0.95);

  const rows = [
    { color: palette.blue, start: 5.0, cells: 7 },
    { color: palette.purple, start: 7.6, cells: 6 },
    { color: palette.orange, start: 10.1, cells: 7 },
    { color: palette.green, start: 13.0, cells: 10 }
  ];
  const cell = 16;
  const gap = 7;
  rows.forEach((row, rowIndex) => {
    const rowP = easeOut((t - row.start) / 2.4);
    const count = Math.floor(row.cells * rowP + 0.001);
    const y = box.y + 46 + rowIndex * 54;
    for (let index = 0; index < row.cells; index += 1) {
      const active = index < count;
      group.append("rect")
        .attr("x", box.x + 28 + index * (cell + gap))
        .attr("y", y)
        .attr("width", cell)
        .attr("height", cell)
        .attr("rx", 4)
        .attr("fill", active ? row.color : palette.gray100)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.2)
        .attr("opacity", active ? 0.86 : 0.66);
    }
  });

  const gauge = {
    cx: box.x + box.w / 2,
    cy: box.y + box.h - 72,
    r: 54
  };
  const arc = d3.arc()
    .innerRadius(gauge.r - 11)
    .outerRadius(gauge.r)
    .startAngle(-Math.PI * 0.72)
    .endAngle(-Math.PI * 0.72 + Math.PI * 1.44 * fillP);
  group.append("circle")
    .attr("cx", gauge.cx)
    .attr("cy", gauge.cy)
    .attr("r", gauge.r)
    .attr("fill", palette.gray100)
    .attr("opacity", 0.92);
  group.append("path")
    .attr("d", arc)
    .attr("transform", `translate(${gauge.cx},${gauge.cy})`)
    .attr("fill", palette.brandPrimary)
    .attr("opacity", 0.9);
  drawText(group, "$", gauge.cx, gauge.cy + 2, ctx, {
    size: 46,
    weight: 900,
    fill: palette.brandPrimary,
    opacity: 0.92
  });

  d3.range(4).forEach((index) => {
    const phase = clamp((t - 16.0 - index * 0.2) / 1.8, 0, 1);
    if (phase <= 0.01 || phase >= 1) return;
    group.append("circle")
      .attr("cx", gauge.cx)
      .attr("cy", gauge.cy)
      .attr("r", gauge.r + phase * 46)
      .attr("fill", "none")
      .attr("stroke", [palette.blue, palette.purple, palette.orange, palette.green][index])
      .attr("stroke-width", 3)
      .attr("opacity", (1 - phase) * 0.32);
  });
}

export function drawLlmHandoffVisualOnly(g, ctx) {
  const { palette, sceneProgress, pulse, clamp, easeOut, easeInOut } = ctx;
  const t = sceneProgress * 20;
  const sceneOpacity = easeOut(t / 1.15);
  const llmBox = { x: 505, y: 210, w: 270, h: 270 };
  const matrixBox = { x: 74, y: 210, w: 300, h: 300 };
  const meterBox = { x: 924, y: 152, w: 260, h: 430 };
  const group = g.append("g").attr("opacity", sceneOpacity);

  const baseTokens = [...promptTokens];
  const answerCount = Math.floor(outputTokens.length * easeOut((t - 6.8) / 2.2));
  const retryCount = Math.floor(retryTokens.length * easeOut((t - 10.4) / 2.2));
  const longContext = d3.range(Math.floor(24 * easeOut((t - 12.6) / 4.5))).map((index) => ({
    color: [palette.gray300, palette.blue, palette.green, palette.orange, palette.purple][index % 5],
    opacity: index % 5 === 0 ? 0.58 : 0.78
  }));
  const matrixTokens = [
    ...baseTokens,
    ...outputTokens.slice(0, answerCount),
    ...retryTokens.slice(0, retryCount),
    ...longContext
  ];
  const layout = drawContextMatrix(group, matrixBox, matrixTokens, ctx, { opacity: 0.98 });
  drawConsistentLlmBox(group, llmBox, clamp((Math.sin(t * 1.8) + 1) / 2, 0, 1) * 0.75 + pulse * 0.25, ctx);
  drawMeter(group, meterBox, t, ctx);

  const promptP = easeInOut((t - 1.0) / 3.2);
  const outputP = easeInOut((t - 5.0) / 3.0);
  const retryP = easeInOut((t - 8.4) / 3.8);
  const longP = easeInOut((t - 12.2) / 5.0);
  const matrixMid = { x: matrixBox.x + matrixBox.w, y: matrixBox.y + matrixBox.h / 2 };
  const llmLeft = { x: llmBox.x, y: llmBox.y + llmBox.h / 2 };
  const llmRight = { x: llmBox.x + llmBox.w, y: llmBox.y + llmBox.h / 2 };
  const meterLeft = { x: meterBox.x, y: meterBox.y + 188 };
  drawArrowLine(group, matrixMid, llmLeft, palette.blue, Math.min(promptP, 1 - longP * 0.3) * 0.42, 3.2);
  drawArrowLine(group, llmRight, meterLeft, palette.brandPrimary, outputP * 0.42, 3.2);

  if (promptP < 0.98) {
    promptTokens.forEach((token, index) => {
      const fromSlot = layout.slot(index);
      drawTokenParticle(group, {
        x: fromSlot.x + fromSlot.w / 2,
        y: fromSlot.y + fromSlot.h / 2
      }, {
        x: llmBox.x + 16,
        y: llmBox.y + 74 + index * 26
      }, promptP - index * 0.07, token, ctx, { arc: -26 });
    });
  }

  if (outputP > 0.02 && outputP < 0.98) {
    outputTokens.forEach((token, index) => {
      drawTokenParticle(group, {
        x: llmBox.x + llmBox.w - 12,
        y: llmBox.y + 126 + index * 28
      }, {
        x: meterBox.x + 40 + index * 32,
        y: meterBox.y + 102
      }, outputP - index * 0.08, token, ctx, { arc: -18 });
    });
  }

  const loopOpacity = easeOut((t - 8.0) / 1.6) * clamp((14.3 - t) / 2.6, 0, 1);
  if (loopOpacity > 0.02) {
    const loop = group.append("g").attr("opacity", loopOpacity);
    loop.append("path")
      .attr("d", `M${meterBox.x + 18},${meterBox.y + 302} C${840},${665} ${410},${665} ${matrixBox.x + matrixBox.w - 12},${matrixBox.y + matrixBox.h - 16}`)
      .attr("fill", "none")
      .attr("stroke", palette.orange)
      .attr("stroke-width", 3.2)
      .attr("stroke-linecap", "round")
      .attr("stroke-dasharray", "10 10")
      .attr("opacity", 0.46);
    retryTokens.forEach((token, index) => {
      const p = retryP - index * 0.08;
      drawTokenParticle(loop, {
        x: meterBox.x + 26,
        y: meterBox.y + 302
      }, {
        x: llmBox.x + 16,
        y: llmBox.y + 202 + index * 21
      }, p, token, ctx, { arc: 76, opacity: 0.86 });
    });
  }

  if (longP > 0.02) {
    d3.range(10).forEach((index) => {
      const p = easeInOut(longP - index * 0.045);
      if (p <= 0.01 || p >= 1) return;
      const slot = layout.slot(12 + index);
      drawTokenParticle(group, {
        x: slot.x + slot.w / 2,
        y: slot.y + slot.h / 2
      }, {
        x: meterBox.x + 56 + index * 17,
        y: meterBox.y + 210
      }, p, { color: [palette.green, palette.blue, palette.purple, palette.orange][index % 4] }, ctx, { arc: -44, opacity: 0.72 });
    });
  }

  const finalP = easeOut((t - 16.8) / 2.4);
  if (finalP > 0.01) {
    const outputGroup = group.append("g").attr("opacity", finalP);
    drawTokenRow(outputGroup, outputTokens, llmBox.x + llmBox.w / 2, llmBox.y + llmBox.h + 34, ctx, {
      scale: 0.9,
      solid: true,
      opacity: 0.9
    });
    d3.range(5).forEach((index) => {
      const p = (Math.sin(t * 1.6 + index * 1.1) + 1) / 2;
      outputGroup.append("rect")
        .attr("x", meterBox.x + 66 + index * 26)
        .attr("y", meterBox.y + meterBox.h + 22)
        .attr("width", 15)
        .attr("height", 15)
        .attr("rx", 4)
        .attr("fill", [palette.blue, palette.purple, palette.orange, palette.green, palette.red][index])
        .attr("opacity", 0.35 + p * 0.45);
    });
  }
}

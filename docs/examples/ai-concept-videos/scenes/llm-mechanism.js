const baseContinuationToken = { raw: " tests", piece: "tests", color: "#652f6c" };

const generationSteps = [
  {
    start: 2.5,
    selected: { raw: " for", piece: "for", color: "#007298" },
    candidates: [
      { label: "for", p: 0.42, color: "#007298" },
      { label: ".", p: 0.25, color: "#9e1b32" },
      { label: "with", p: 0.18, color: "#45842a" },
      { label: "when", p: 0.1, color: "#e77204" },
      { label: "now", p: 0.05, color: "#f1c319" }
    ]
  },
  {
    start: 11.2,
    selected: { raw: " bugs", piece: "bugs", color: "#45842a" },
    candidates: [
      { label: "bugs", p: 0.45, color: "#45842a" },
      { label: "apps", p: 0.22, color: "#007298" },
      { label: "logic", p: 0.18, color: "#652f6c" },
      { label: "users", p: 0.1, color: "#e77204" },
      { label: "speed", p: 0.05, color: "#f1c319" }
    ]
  },
  {
    start: 19.9,
    selected: { raw: ".", piece: ".", color: "#9e1b32" },
    candidates: [
      { label: ".", p: 0.52, color: "#9e1b32" },
      { label: "and", p: 0.2, color: "#007298" },
      { label: ",", p: 0.13, color: "#652f6c" },
      { label: "before", p: 0.09, color: "#e77204" },
      { label: "quickly", p: 0.06, color: "#45842a" }
    ]
  }
];

function tokenWidth(label) {
  if (label === ".") return 34;
  if (label === ",") return 34;
  return Math.max(52, label.length * 13 + 28);
}

function selectedIndex(step) {
  return step.candidates.findIndex((candidate) => candidate.label === step.selected.piece);
}

function stepAt(t) {
  let index = 0;
  for (let i = 0; i < generationSteps.length; i += 1) {
    if (t >= generationSteps[i].start) index = i;
  }
  return { step: generationSteps[index], index };
}

function completedSteps(t) {
  return generationSteps.filter((step) => t >= step.start + 6.8).length;
}

function movingStep(t) {
  return generationSteps.find((step) => {
    const local = t - step.start;
    return local >= 4.55 && local <= 6.95;
  });
}

function drawTokenTrail(g, tokens, visibleCount, ctx) {
  const { palette, drawHookText } = ctx;
  const opacityScale = ctx.trailOpacity ?? 1;
  if (opacityScale <= 0.01) return;
  const gap = 10;
  const widths = tokens.map((token) => tokenWidth(token.piece));
  const total = widths.reduce((sum, width) => sum + width, 0) + gap * (widths.length - 1);
  const startX = (1280 - total) / 2;
  const y = 630;
  let cursor = startX;
  tokens.forEach((token, index) => {
    const reveal = ctx.easeOut((visibleCount - index) / 0.75);
    if (reveal <= 0.01) {
      cursor += widths[index] + gap;
      return;
    }
    const group = g.append("g").attr("opacity", reveal * opacityScale);
    group.append("rect")
      .attr("x", cursor)
      .attr("y", y)
      .attr("width", widths[index])
      .attr("height", 30)
      .attr("rx", 7)
      .attr("fill", index < 5 ? "#ffffff" : token.color)
      .attr("stroke", token.color)
      .attr("stroke-width", index < 5 ? 2.2 : 0)
      .attr("opacity", index < 5 ? 0.94 : 0.88);
    drawHookText(group, token.piece, cursor + widths[index] / 2, y + 16,
    {
      size: 14,
      weight: 850,
      fill: index < 5 ? token.color : "#ffffff",
      opacity: 1
    });
    if (index === visibleCount - 1) {
      group.append("rect")
        .attr("x", cursor - 4)
        .attr("y", y - 4)
        .attr("width", widths[index] + 8)
        .attr("height", 38)
        .attr("rx", 9)
        .attr("fill", "none")
        .attr("stroke", palette.gray300)
        .attr("stroke-width", 2)
        .attr("opacity", 0.65);
    }
    cursor += widths[index] + gap;
  });
}

function drawLlmMachine(g, llm, activation, ctx) {
  const { palette, drawHookText, pulse, lerp } = ctx;
  const textOpacity = ctx.machineTextOpacity ?? 1;
  const textMorph = ctx.machineTextMorph ?? 1;
  const group = g.append("g");
  group.append("rect")
    .attr("x", llm.x)
    .attr("y", llm.y)
    .attr("width", llm.w)
    .attr("height", llm.h)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.brandPrimary)
    .attr("stroke-width", 4);

  ["Large", "Language", "Model"].forEach((word, index) => {
    drawHookText(group, word, llm.x + llm.w / 2, lerp(llm.y + 100 + index * 39, llm.y + 84 + index * 32, textMorph), {
      size: lerp(36, 29, textMorph),
      weight: 870,
      fill: palette.brandNeutral,
      opacity: 0.96 * textOpacity
    });
  });

  const mlp = {
    x: llm.x + 170,
    y: llm.y + 188,
    layerGap: 28,
    nodeGap: 17,
    layers: [3, 4, 3]
  };
  const network = group.append("g").attr("opacity", 0.28 + activation * 0.34);
  for (let layer = 0; layer < mlp.layers.length - 1; layer += 1) {
    const fromCount = mlp.layers[layer];
    const toCount = mlp.layers[layer + 1];
    const fromX = mlp.x + layer * mlp.layerGap;
    const toX = mlp.x + (layer + 1) * mlp.layerGap;
    for (let a = 0; a < fromCount; a += 1) {
      for (let b = 0; b < toCount; b += 1) {
        network.append("line")
          .attr("x1", fromX)
          .attr("y1", mlp.y + a * mlp.nodeGap + (4 - fromCount) * 5)
          .attr("x2", toX)
          .attr("y2", mlp.y + b * mlp.nodeGap + (4 - toCount) * 5)
          .attr("stroke", activation > 0.35 ? palette.blue : palette.gray400)
          .attr("stroke-width", 1.2 + activation * 1.2)
          .attr("opacity", 0.42 + activation * 0.32);
      }
    }
  }
  mlp.layers.forEach((count, layer) => {
    const x = mlp.x + layer * mlp.layerGap;
    for (let node = 0; node < count; node += 1) {
      network.append("circle")
        .attr("cx", x)
        .attr("cy", mlp.y + node * mlp.nodeGap + (4 - count) * 5)
        .attr("r", 4.3 + activation * 2.2 + pulse * 0.45)
        .attr("fill", activation > 0.45 ? palette.blue : palette.gray600)
        .attr("stroke", "#ffffff")
        .attr("stroke-width", 1.3)
        .attr("opacity", 0.7 + activation * 0.22);
    }
  });
}

function drawContextIngress(g, matrix, llm, layout, tokens, local, ctx) {
  const { palette, clamp, easeInOut } = ctx;
  const flowP = clamp((local - 0.15) / 2.1, 0, 1);
  if (flowP <= 0.01) return;
  const lineOpacity = clamp((1 - Math.abs(flowP - 0.5) * 1.8), 0, 1);
  const source = { x: matrix.x + matrix.w, y: matrix.y + matrix.h / 2 };
  const target = { x: llm.x, y: llm.y + llm.h / 2 };
  g.append("line")
    .attr("x1", source.x + 6)
    .attr("y1", source.y)
    .attr("x2", target.x - 8)
    .attr("y2", target.y)
    .attr("stroke", palette.blue)
    .attr("stroke-width", 3)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.1 + lineOpacity * 0.22);

  tokens.slice(0, Math.min(tokens.length, 7)).forEach((token, index) => {
    const slot = layout.slot(index);
    const p = easeInOut(flowP * 1.22 - index * 0.055);
    if (p <= 0.01 || p >= 0.995) return;
    const x = slot.x + slot.w / 2 + (target.x - 18 - slot.x - slot.w / 2) * p;
    const y = slot.y + slot.h / 2 + (target.y - slot.y - slot.h / 2) * p;
    g.append("rect")
      .attr("x", x - 7)
      .attr("y", y - 7)
      .attr("width", 14)
      .attr("height", 14)
      .attr("rx", 3)
      .attr("fill", token.color)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 1.5)
      .attr("opacity", 0.82);
  });
}

function drawSampler(g, chart, step, local, ctx) {
  const D3 = globalThis.d3;
  const { palette, drawHookText, clamp, easeInOut, easeOut, lerp } = ctx;
  const samplerP = easeOut((local - 1.15) / 0.95);
  if (samplerP <= 0.01) return;

  const fadeOut = 1 - 0.42 * easeInOut((local - 6.4) / 1.1);
  const group = g.append("g").attr("opacity", samplerP * fadeOut);
  const wheel = {
    cx: chart.x + 82,
    cy: chart.y + chart.h / 2,
    r: 66
  };
  const tokens = step.candidates.map((candidate, index) => ({
    ...candidate,
    selected: index === selectedIndex(step)
  }));
  const arcs = D3.pie().sort(null).value((token) => token.p)(tokens);
  const selectedArc = arcs[selectedIndex(step)];
  const selectedCenterDeg = ((selectedArc.startAngle + selectedArc.endAngle) / 2) * 180 / Math.PI;
  const spinP = clamp((local - 2.1) / 2.45, 0, 1);
  let wheelRotation = 0;
  const finalRotation = 1440 - selectedCenterDeg;
  if (spinP < 0.45) {
    wheelRotation = lerp(0, 720, easeOut(spinP / 0.45));
  } else if (spinP < 0.76) {
    wheelRotation = lerp(720, 1120, easeOut((spinP - 0.45) / 0.31));
  } else {
    wheelRotation = lerp(1120, finalRotation, easeOut((spinP - 0.76) / 0.24));
  }
  const settledP = easeOut((local - 4.48) / 0.38);
  const arc = D3.arc().innerRadius(0).outerRadius(wheel.r).cornerRadius(4).padAngle(0.012);
  const selectedArcPath = D3.arc().innerRadius(0).outerRadius(wheel.r + 5).cornerRadius(4).padAngle(0.012);

  group.append("circle")
    .attr("cx", wheel.cx)
    .attr("cy", wheel.cy)
    .attr("r", wheel.r + 9)
    .attr("fill", palette.gray100)
    .attr("stroke", "none")
    .attr("opacity", 0.94);

  const wheelGroup = group.append("g")
    .attr("transform", `translate(${wheel.cx},${wheel.cy}) rotate(${wheelRotation})`);
  wheelGroup.selectAll("path")
    .data(arcs)
    .join("path")
    .attr("d", arc)
    .attr("fill", (arcDatum) => arcDatum.data.color)
    .attr("fill-opacity", (arcDatum) => arcDatum.data.selected ? 0.94 : 0.68)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2);
  wheelGroup.selectAll("path.selected-ring")
    .data(arcs.filter((arcDatum) => arcDatum.data.selected))
    .join("path")
    .attr("class", "selected-ring")
    .attr("d", selectedArcPath)
    .attr("fill", "none")
    .attr("stroke", palette.redHover)
    .attr("stroke-width", 3.2)
    .attr("opacity", settledP * 0.95);

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
    .attr("opacity", 0.92);

  const labelX = chart.x + 174;
  const barsX = chart.x + 252;
  const barsY = chart.y + 50;
  tokens.forEach((token, index) => {
    const rowY = barsY + index * 34;
    const barW = 78 * (token.p / tokens[0].p);
    const row = group.append("g");
    row.append("rect")
      .attr("x", labelX - 8)
      .attr("y", rowY - 1)
      .attr("width", 68)
      .attr("height", 20)
      .attr("rx", 6)
      .attr("fill", token.selected ? token.color : "#ffffff")
      .attr("stroke", token.selected ? "none" : token.color)
      .attr("stroke-width", 1.8)
      .attr("opacity", token.selected ? 0.88 : 0.78);
    drawHookText(row, token.label, labelX + 26, rowY + 10, {
      size: 13,
      weight: token.selected ? 850 : 720,
      fill: token.selected ? "#ffffff" : token.color,
      opacity: 0.96
    });
    row.append("rect")
      .attr("x", barsX)
      .attr("y", rowY)
      .attr("width", 86)
      .attr("height", 18)
      .attr("rx", 6)
      .attr("fill", palette.gray100)
      .attr("opacity", 0.82);
    row.append("rect")
      .attr("x", barsX)
      .attr("y", rowY)
      .attr("width", barW + 12)
      .attr("height", 18)
      .attr("rx", 6)
      .attr("fill", token.color)
      .attr("fill-opacity", token.selected ? 0.9 : 0.58);
  });
}

function drawChosenToken(g, matrix, llm, layout, activeStep, allTokensBeforeStep, local, ctx) {
  if (!activeStep) return;
  const { drawHookCard, drawHookText, tokenCardGeometry, clamp, easeInOut, lerp } = ctx;
  const travelP = easeInOut((local - 4.72) / 2.08);
  if (travelP <= 0.01) return;
  const slot = layout.slot(allTokensBeforeStep.length);
  const source = {
    x: llm.x - 78,
    y: llm.y + llm.h / 2 - 24,
    w: 96,
    h: 48
  };
  const target = { x: slot.x, y: slot.y, w: slot.w, h: slot.h };
  const card = tokenCardGeometry(source, target, travelP);
  const settleP = clamp((travelP - 0.88) / 0.12, 0, 1);
  const opacity = 0.96 * (1 - settleP);
  const lineOpacity = clamp((travelP - 0.04) / 0.28, 0, 1) * clamp((1 - travelP) / 0.45, 0, 1);
  const lineStart = { x: source.x + source.w / 2, y: source.y + source.h / 2 };
  const lineEnd = { x: slot.x + slot.w / 2, y: slot.y + slot.h / 2 };
  const lineHead = { x: card.x + card.w / 2, y: card.y + card.h / 2 };

  g.append("line")
    .attr("x1", lineStart.x)
    .attr("y1", lineStart.y)
    .attr("x2", lineEnd.x)
    .attr("y2", lineEnd.y)
    .attr("stroke", activeStep.selected.color)
    .attr("stroke-width", 2)
    .attr("stroke-linecap", "round")
    .attr("opacity", lineOpacity * 0.08);
  g.append("line")
    .attr("x1", lineHead.x)
    .attr("y1", lineHead.y)
    .attr("x2", lineEnd.x)
    .attr("y2", lineEnd.y)
    .attr("stroke", activeStep.selected.color)
    .attr("stroke-width", 3.4)
    .attr("stroke-linecap", "round")
    .attr("opacity", lineOpacity * 0.42);

  if (travelP > 0.48 && travelP < 0.96) {
    g.append("rect")
      .attr("x", slot.x - 4)
      .attr("y", slot.y - 4)
      .attr("width", slot.w + 8)
      .attr("height", slot.h + 8)
      .attr("rx", 6)
      .attr("fill", "none")
      .attr("stroke", activeStep.selected.color)
      .attr("stroke-width", 2.2)
      .attr("opacity", 0.7 * (1 - settleP));
  }

  if (opacity <= 0.02) return;
  drawHookCard(g, card.x, card.y, card.w, card.h, activeStep.selected.color, opacity, {
    fill: globalThis.d3.interpolateRgb("#ffffff", activeStep.selected.color)(travelP),
    fillBand: travelP < 0.76,
    rx: lerp(12, 4, travelP),
    strokeWidth: lerp(3.3, 2, travelP),
    filter: travelP < 0.94 ? "url(#soft-glow)" : null
  });
  drawHookText(g, activeStep.selected.piece, card.x + card.w / 2, card.y + card.h / 2 + 1, {
    size: lerp(23, 7, travelP),
    weight: 870,
    fill: globalThis.d3.interpolateRgb(activeStep.selected.color, "#ffffff")(travelP),
    opacity: opacity * clamp(1 - travelP * 1.25, 0, 1)
  });
}

export function drawLlmMechanismVisualOnly(g, ctx) {
  const { palette, hookTokens, sceneProgress, llmDefinitionDecisionLayout, drawHookContextMatrix, clamp, easeInOut, easeOut } = ctx;
  const t = clamp(sceneProgress * 30, 0, 30);
  const layoutRegions = llmDefinitionDecisionLayout();
  const matrix = layoutRegions.matrix;
  const llm = layoutRegions.llm;
  const chart = layoutRegions.roulette;
  const baseTokens = [...hookTokens, { ...baseContinuationToken, color: palette.purple }];
  const generatedTokens = generationSteps.map((step) => step.selected);
  const active = stepAt(t);
  const local = t - active.step.start;
  const completed = completedSteps(t);
  const activeMoving = movingStep(t);
  const activeMovingLocal = activeMoving ? t - activeMoving.start : -1;
  const visibleTokens = [...baseTokens, ...generatedTokens.slice(0, completed)];
  if (activeMoving && activeMovingLocal > 6.55 && completed < generationSteps.indexOf(activeMoving) + 1) {
    visibleTokens.push(activeMoving.selected);
  }

  const introP = easeOut((t - 0.25) / 1.55);
  const contentGroup = g.append("g").attr("opacity", introP);
  const matrixLayout = drawHookContextMatrix(contentGroup, matrix, visibleTokens, {
    opacity: 1,
    backgroundOpacity: 0.94,
    occupiedOpacity: 0.96,
    cellOpacity: 0.74,
    cell: 24,
    gap: 8
  });
  generationSteps.forEach((step, index) => {
    const sinceAppend = t - (step.start + 6.8);
    if (sinceAppend < 0 || sinceAppend > 1.35) return;
    const pulseP = 1 - sinceAppend / 1.35;
    const slot = matrixLayout.slot(baseTokens.length + index);
    contentGroup.append("rect")
      .attr("x", slot.x - 5 - 5 * pulseP)
      .attr("y", slot.y - 5 - 5 * pulseP)
      .attr("width", slot.w + 10 + 10 * pulseP)
      .attr("height", slot.h + 10 + 10 * pulseP)
      .attr("rx", 7)
      .attr("fill", "none")
      .attr("stroke", step.selected.color)
      .attr("stroke-width", 2.4)
      .attr("opacity", 0.62 * pulseP);
  });

  const activation = Math.max(
    ...generationSteps.map((step) => {
      const stepLocal = t - step.start;
      return clamp((stepLocal - 0.75) / 1.1, 0, 1) * clamp((4.5 - stepLocal) / 1.4, 0, 1);
    }),
    0
  );
  drawContextIngress(contentGroup, matrix, llm, matrixLayout, visibleTokens, Math.max(0, local), ctx);
  drawLlmMachine(contentGroup, llm, activation, ctx);
  drawSampler(contentGroup, chart, active.step, Math.max(0, local), ctx);

  const beforeMovingTokens = activeMoving
    ? [...baseTokens, ...generatedTokens.slice(0, generationSteps.indexOf(activeMoving))]
    : visibleTokens;
  drawChosenToken(contentGroup, matrix, llm, matrixLayout, activeMoving, beforeMovingTokens, activeMovingLocal, ctx);

  const movingIndex = activeMoving ? generationSteps.indexOf(activeMoving) : -1;
  const trailVisibleCount = baseTokens.length + completed + (
    activeMoving && activeMovingLocal > 5.25 && completed < movingIndex + 1 ? 1 : 0
  );
  drawTokenTrail(contentGroup, [...baseTokens, ...generatedTokens], trailVisibleCount, ctx);

  const freshSlotIndex = Math.max(baseTokens.length, visibleTokens.length - 1);
  if (t > 27.2 && visibleTokens.length >= baseTokens.length + generationSteps.length) {
    const slot = matrixLayout.slot(freshSlotIndex);
    contentGroup.append("rect")
      .attr("x", slot.x - 6)
      .attr("y", slot.y - 6)
      .attr("width", slot.w + 12)
      .attr("height", slot.h + 12)
      .attr("rx", 7)
      .attr("fill", "none")
      .attr("stroke", palette.brandPrimary)
      .attr("stroke-width", 2.2)
      .attr("opacity", 0.22 + 0.18 * Math.sin(t * 3.8));
  }
}

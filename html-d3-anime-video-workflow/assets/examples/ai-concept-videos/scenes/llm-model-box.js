function buildMlpNodes(llm) {
  const scale = llm.scale ?? 1;
  const layers = [3, 4, 3];
  const ghost = {
    x: llm.x + llm.w - 74 * scale,
    y: llm.y + llm.h - 68 * scale,
    layerGap: 20 * scale,
    nodeGap: 12 * scale,
    layers
  };
  return layers.flatMap((count, layer) => {
    const x = ghost.x + layer * ghost.layerGap;
    return Array.from({ length: count }, (_, node) => ({
      id: `${layer}-${node}`,
      layer,
      index: node,
      x,
      y: ghost.y + node * ghost.nodeGap + (4 - count) * 5 * scale
    }));
  });
}

function buildMlpLinks(nodes) {
  const D3 = globalThis.d3;
  const byLayer = D3.group(nodes, (node) => node.layer);
  const links = [];
  for (let layer = 0; layer < byLayer.size - 1; layer += 1) {
    for (const source of byLayer.get(layer)) {
      for (const target of byLayer.get(layer + 1)) {
        links.push({ source, target, layer: layer + 1 });
      }
    }
  }
  return links;
}

export function drawLlmModelBox(g, llm, ctx, options = {}) {
  const { palette, drawHookText, clamp, easeOut } = ctx;
  const D3 = globalThis.d3;
  const scale = options.scale ?? Math.min(llm.w, llm.h) / 270;
  const box = { ...llm, scale };
  const opacity = options.opacity ?? 1;
  const textOpacity = opacity * (options.textOpacity ?? 1);
  const activation = clamp(options.activation ?? 0, 0, 1);
  const activationClock = Math.max(0, options.activationClock ?? 0);
  const group = g.append("g").attr("opacity", opacity);

  group.append("rect")
    .attr("x", box.x)
    .attr("y", box.y)
    .attr("width", box.w)
    .attr("height", box.h)
    .attr("rx", 0)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.brandPrimary)
    .attr("stroke-width", 4 * scale);

  const nodes = buildMlpNodes(box);
  const links = buildMlpLinks(nodes);
  const activationCycle = 2.45;
  const activationT = ((activationClock % activationCycle) / activationCycle) * 3.75;
  const pulseForLayer = (layer, width = 0.58) => {
    const distance = Math.abs(activationT - layer);
    return easeOut(clamp(1 - distance / width, 0, 1)) * activation;
  };
  const linkPulse = (link) => easeOut(clamp(1 - Math.abs(activationT - (link.layer - 0.45)) / 0.48, 0, 1)) * activation;
  const boxActivation = D3.max([0, 1, 2], (layer) => pulseForLayer(layer, 0.72)) ?? 0;

  group.append("rect")
    .attr("x", box.x + 8 * scale)
    .attr("y", box.y + 8 * scale)
    .attr("width", box.w - 16 * scale)
    .attr("height", box.h - 16 * scale)
    .attr("rx", 0)
    .attr("fill", "none")
    .attr("stroke", palette.redHighlight)
    .attr("stroke-width", 10 * scale)
    .attr("opacity", boxActivation * 0.22);

  const ghostGroup = group.append("g").attr("opacity", 0.26);
  ghostGroup.selectAll("line.mlp-link-base")
    .data(links)
    .join("line")
    .attr("class", "mlp-link-base")
    .attr("x1", (link) => link.source.x)
    .attr("y1", (link) => link.source.y)
    .attr("x2", (link) => link.target.x)
    .attr("y2", (link) => link.target.y)
    .attr("stroke", palette.gray400)
    .attr("stroke-width", 1.1 * scale)
    .attr("opacity", 0.42);
  ghostGroup.selectAll("circle.mlp-node-base")
    .data(nodes)
    .join("circle")
    .attr("class", "mlp-node-base")
    .attr("cx", (node) => node.x)
    .attr("cy", (node) => node.y)
    .attr("r", 3.5 * scale)
    .attr("fill", palette.gray600)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.1 * scale)
    .attr("opacity", 0.72);

  const activeGroup = group.append("g").attr("opacity", 0.92);
  activeGroup.selectAll("line.mlp-link-active")
    .data(links)
    .join("line")
    .attr("class", "mlp-link-active")
    .attr("x1", (link) => link.source.x)
    .attr("y1", (link) => link.source.y)
    .attr("x2", (link) => link.target.x)
    .attr("y2", (link) => link.target.y)
    .attr("stroke", palette.red)
    .attr("stroke-width", (link) => (1 + linkPulse(link) * 2.1) * scale)
    .attr("stroke-linecap", "round")
    .attr("opacity", (link) => linkPulse(link) * 0.42);
  activeGroup.selectAll("circle.mlp-node-active")
    .data(nodes)
    .join("circle")
    .attr("class", "mlp-node-active")
    .attr("cx", (node) => node.x)
    .attr("cy", (node) => node.y)
    .attr("r", (node) => (3.5 + pulseForLayer(node.layer) * 5.2) * scale)
    .attr("fill", palette.redHighlight)
    .attr("stroke", palette.red)
    .attr("stroke-width", (node) => (0.9 + pulseForLayer(node.layer) * 1.5) * scale)
    .attr("opacity", (node) => pulseForLayer(node.layer) * 0.76);

  const labelLines = options.labelLines ?? ["Large", "Language", "Model"];
  const labelSize = (options.labelSize ?? (labelLines.length === 1 ? 48 : 36)) * scale;
  const labelGap = (options.labelGap ?? (labelLines.length === 1 ? 0 : 39)) * scale;
  const labelY = options.labelY ?? (labelLines.length === 1 ? box.y + box.h * 0.47 : box.y + 100 * scale);
  labelLines.forEach((word, index) => {
    drawHookText(group, word, box.x + box.w / 2, labelY + index * labelGap, {
      size: labelSize,
      weight: 870,
      fill: palette.brandNeutral,
      opacity: textOpacity
    });
  });

  return group;
}

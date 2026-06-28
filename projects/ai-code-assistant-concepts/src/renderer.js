import { concepts, palette, project } from "./concepts.js";

const d3 = window.d3;
const stage = d3.select("#stage");
const conceptById = new Map(concepts.map((concept) => [concept.id, concept]));
const W = project.width;
const H = project.height;

function clamp(value, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function wave(t, offset = 0) {
  return (Math.sin(t * Math.PI * 2 + offset) + 1) / 2;
}

function easedLoop(t, offset = 0) {
  return d3.easeCubicInOut(wave(t, offset));
}

function addDefs(svg, accent) {
  const defs = svg.append("defs");
  defs
    .append("filter")
    .attr("id", "softShadow")
    .attr("x", "-20%")
    .attr("y", "-20%")
    .attr("width", "140%")
    .attr("height", "140%")
    .append("feDropShadow")
    .attr("dx", 0)
    .attr("dy", 14)
    .attr("stdDeviation", 16)
    .attr("flood-color", "#17212b")
    .attr("flood-opacity", 0.14);

  const glow = defs
    .append("filter")
    .attr("id", "glow")
    .attr("x", "-50%")
    .attr("y", "-50%")
    .attr("width", "200%")
    .attr("height", "200%");
  glow.append("feGaussianBlur").attr("stdDeviation", 7).attr("result", "coloredBlur");
  const merge = glow.append("feMerge");
  merge.append("feMergeNode").attr("in", "coloredBlur");
  merge.append("feMergeNode").attr("in", "SourceGraphic");

  defs
    .append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 0 10 10")
    .attr("refX", 8)
    .attr("refY", 5)
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .attr("orient", "auto-start-reverse")
    .append("path")
    .attr("d", "M 0 0 L 10 5 L 0 10 z")
    .attr("fill", accent);
}

function addBackground(svg, concept, t) {
  svg.append("rect").attr("width", W).attr("height", H).attr("fill", palette.paper);

  const grid = svg.append("g").attr("opacity", 0.26);
  for (let x = 72; x < W; x += 80) {
    for (let y = 80; y < H; y += 80) {
      const r = 1.3 + wave(t * 0.02, x * 0.01 + y * 0.02);
      grid.append("circle").attr("cx", x).attr("cy", y).attr("r", r).attr("fill", "#b8c6c9");
    }
  }

  svg
    .append("path")
    .attr("d", `M0,0 H${W} V178 C${W * 0.68},138 ${W * 0.33},210 0,166 Z`)
    .attr("fill", concept.accent)
    .attr("opacity", 0.13);
  svg
    .append("path")
    .attr("d", `M0,${H - 176} C${W * 0.28},${H - 232} ${W * 0.68},${H - 132} ${W},${H - 190} V${H} H0 Z`)
    .attr("fill", concept.accent)
    .attr("opacity", 0.09);
}

function addLabel(parent, text, x, y, options = {}) {
  const {
    size = 28,
    weight = 700,
    fill = palette.ink,
    anchor = "start",
    opacity = 1,
    className = "frame-text"
  } = options;
  return parent
    .append("text")
    .attr("x", x)
    .attr("y", y)
    .attr("text-anchor", anchor)
    .attr("font-size", size)
    .attr("font-weight", weight)
    .attr("fill", fill)
    .attr("opacity", opacity)
    .attr("letter-spacing", 0)
    .attr("class", className)
    .text(text);
}

function addWrappedText(parent, text, x, y, width, options = {}) {
  const {
    size = 30,
    lineHeight = 1.2,
    weight = 500,
    fill = palette.ink,
    maxLines = 4,
    opacity = 1
  } = options;
  const words = text.split(/\s+/).filter(Boolean);
  const node = parent
    .append("text")
    .attr("x", x)
    .attr("y", y)
    .attr("font-size", size)
    .attr("font-weight", weight)
    .attr("fill", fill)
    .attr("opacity", opacity)
    .attr("letter-spacing", 0)
    .attr("class", "frame-text");

  let line = [];
  let lineNumber = 0;
  let tspan = node.append("tspan").attr("x", x).attr("dy", 0);

  for (const word of words) {
    line.push(word);
    tspan.text(line.join(" "));
    const tooWide = tspan.node().getComputedTextLength() > width;
    if (tooWide && line.length > 1) {
      line.pop();
      tspan.text(line.join(" "));
      line = [word];
      lineNumber += 1;
      if (lineNumber >= maxLines) {
        tspan.text(`${tspan.text()}...`);
        break;
      }
      tspan = node
        .append("tspan")
        .attr("x", x)
        .attr("dy", `${lineHeight}em`)
        .text(word);
    }
  }
  return node;
}

function addPanel(parent, x, y, w, h, options = {}) {
  const { fill = palette.white, stroke = palette.line, opacity = 0.94, radius = 18, shadow = true } = options;
  return parent
    .append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", radius)
    .attr("fill", fill)
    .attr("stroke", stroke)
    .attr("stroke-width", 2)
    .attr("opacity", opacity)
    .attr("filter", shadow ? "url(#softShadow)" : null);
}

function addChip(parent, label, x, y, color, options = {}) {
  const { w = Math.max(112, label.length * 16 + 38), h = 42, opacity = 1 } = options;
  const g = parent.append("g").attr("opacity", opacity);
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", 20)
    .attr("fill", color)
    .attr("opacity", 0.15)
    .attr("stroke", color)
    .attr("stroke-width", 1.5);
  addLabel(g, label, x + w / 2, y + 28, { size: 20, weight: 750, anchor: "middle", fill: color });
  return g;
}

function addPacket(parent, x, y, color, label = "") {
  const g = parent.append("g").attr("transform", `translate(${x},${y})`);
  g.append("rect").attr("x", -34).attr("y", -24).attr("width", 68).attr("height", 48).attr("rx", 12).attr("fill", palette.white).attr("stroke", color).attr("stroke-width", 4);
  g.append("rect").attr("x", -22).attr("y", -10).attr("width", 44).attr("height", 6).attr("rx", 3).attr("fill", color).attr("opacity", 0.9);
  g.append("rect").attr("x", -22).attr("y", 4).attr("width", 30).attr("height", 6).attr("rx", 3).attr("fill", color).attr("opacity", 0.55);
  if (label) addLabel(g, label, 0, 48, { size: 16, weight: 800, anchor: "middle", fill: color });
  return g;
}

function addArrow(parent, x1, y1, x2, y2, color, options = {}) {
  const { opacity = 1, width = 5, dash = null } = options;
  const line = parent
    .append("line")
    .attr("x1", x1)
    .attr("y1", y1)
    .attr("x2", x2)
    .attr("y2", y2)
    .attr("stroke", color)
    .attr("stroke-width", width)
    .attr("stroke-linecap", "round")
    .attr("marker-end", "url(#arrow)")
    .attr("opacity", opacity);
  if (dash) line.attr("stroke-dasharray", dash);
  return line;
}

function sceneState(concept, time) {
  const runtime = concept.runtimeSeconds;
  const t = ((time % runtime) + runtime) % runtime;
  const sceneDuration = runtime / concept.scenes.length;
  const index = Math.min(concept.scenes.length - 1, Math.floor(t / sceneDuration));
  const local = (t - index * sceneDuration) / sceneDuration;
  const scene = concept.scenes[index];
  return { t, index, local, sceneDuration, scene, fadeIn: clamp(local / 0.14), fadeOut: clamp((1 - local) / 0.14) };
}

function addHeader(svg, concept, state) {
  const g = svg.append("g");
  addLabel(g, project.title.toUpperCase(), 96, 92, { size: 23, weight: 850, fill: palette.muted });
  addLabel(g, `${String(concept.order).padStart(2, "0")} / 15`, 96, 150, { size: 34, weight: 900, fill: concept.accent });
  addLabel(g, concept.title, 206, 152, { size: 54, weight: 900, fill: palette.ink });
  addWrappedText(g, concept.thesis, 98, 202, 1060, { size: 24, lineHeight: 1.15, maxLines: 2, fill: palette.muted, weight: 600 });

  const barX = 1238;
  const barY = 92;
  const barW = 584;
  const beatW = barW / concept.scenes.length;
  concept.scenes.forEach((scene, index) => {
    g.append("rect")
      .attr("x", barX + index * beatW)
      .attr("y", barY)
      .attr("width", beatW - 8)
      .attr("height", 12)
      .attr("rx", 6)
      .attr("fill", index < state.index ? concept.accent : index === state.index ? concept.accent : palette.line)
      .attr("opacity", index === state.index ? 0.95 : index < state.index ? 0.55 : 0.8);
    addLabel(g, scene.beat, barX + index * beatW, barY + 42, {
      size: 16,
      weight: index === state.index ? 850 : 650,
      fill: index === state.index ? concept.accent : palette.muted
    });
  });
  g.append("rect")
    .attr("x", barX + state.index * beatW)
    .attr("y", barY)
    .attr("width", (beatW - 8) * state.local)
    .attr("height", 12)
    .attr("rx", 6)
    .attr("fill", palette.ink)
    .attr("opacity", 0.25);
}

function addSceneText(svg, concept, state) {
  const x = 1220;
  const y = 250;
  const w = 604;
  const h = 500;
  const g = svg.append("g").attr("opacity", 0.92);
  addPanel(g, x, y, w, h, { fill: "#fbfcfc", radius: 22 });
  addLabel(g, state.scene.beat.toUpperCase(), x + 44, y + 66, { size: 21, weight: 900, fill: concept.accent });
  addWrappedText(g, state.scene.headline, x + 44, y + 142, w - 88, { size: 43, lineHeight: 1.05, maxLines: 2, weight: 900 });
  addWrappedText(g, state.scene.micro, x + 44, y + 252, w - 88, { size: 28, lineHeight: 1.22, maxLines: 4, weight: 560, fill: palette.muted });
  state.scene.terms.forEach((term, index) => {
    const chipX = x + 44 + (index % 2) * 250;
    const chipY = y + 386 + Math.floor(index / 2) * 58;
    addChip(g, term, chipX, chipY, index === 2 ? palette.ink : concept.accent, { w: 218 });
  });
}

function addConceptRail(svg, concept) {
  const g = svg.append("g");
  const x = 96;
  const y = 948;
  const w = 1728;
  addLabel(g, "shared concept sequence", x, y - 30, { size: 19, weight: 800, fill: palette.muted });
  g.append("line").attr("x1", x).attr("x2", x + w).attr("y1", y).attr("y2", y).attr("stroke", palette.line).attr("stroke-width", 5).attr("stroke-linecap", "round");
  const gap = w / (concepts.length - 1);
  concepts.forEach((item, index) => {
    const active = item.id === concept.id;
    const cx = x + index * gap;
    g.append("circle")
      .attr("cx", cx)
      .attr("cy", y)
      .attr("r", active ? 17 : 10)
      .attr("fill", active ? concept.accent : palette.white)
      .attr("stroke", active ? concept.accent : palette.line)
      .attr("stroke-width", active ? 5 : 3);
    addLabel(g, String(index + 1), cx, y + 54, { size: 16, weight: active ? 900 : 650, anchor: "middle", fill: active ? concept.accent : palette.muted });
  });
}

function drawTokenFlow(g, concept, state, t) {
  const x = 130;
  const y = 275;
  addPanel(g, x, y, 430, 360, { fill: "#f9fbfc", radius: 20 });
  addLabel(g, "CONTEXT", x + 36, y + 58, { size: 26, weight: 900, fill: concept.accent });
  const labels = ["user", "repo", "rules", "tool"];
  labels.forEach((label, i) => {
    const px = x + 80 + (i % 2) * 160;
    const py = y + 130 + Math.floor(i / 2) * 105;
    addPacket(g, px, py, i === state.index % 4 ? concept.accent : palette.slate, label);
  });

  const mx = 760;
  const my = 455;
  g.append("circle").attr("cx", mx).attr("cy", my).attr("r", 130).attr("fill", palette.white).attr("stroke", concept.accent).attr("stroke-width", 5).attr("filter", "url(#softShadow)");
  addLabel(g, "MODEL", mx, my - 8, { size: 38, weight: 950, anchor: "middle", fill: palette.ink });
  addLabel(g, "rank next token", mx, my + 34, { size: 22, weight: 700, anchor: "middle", fill: palette.muted });
  addArrow(g, x + 430, my, mx - 145, my, concept.accent, { opacity: 0.78 });

  const p = (t * 0.36 + state.index * 0.14) % 1;
  addPacket(g, x + 470 + p * 235, my - 6 + Math.sin(p * Math.PI * 2) * 12, concept.accent);

  const bx = 975;
  const by = 330;
  [";", ")", "fix", "test"].forEach((label, i) => {
    const v = 0.25 + 0.55 * wave(t * 0.18, i + state.index);
    const h = 54 + 142 * v;
    g.append("rect").attr("x", bx + i * 78).attr("y", by + 230 - h).attr("width", 48).attr("height", h).attr("rx", 10).attr("fill", i === state.index % 4 ? concept.accent : palette.line).attr("opacity", i === state.index % 4 ? 0.95 : 0.8);
    addLabel(g, label, bx + i * 78 + 24, by + 260, { size: 20, weight: 900, anchor: "middle", fill: palette.ink });
  });
  addLabel(g, "candidate tokens", bx, by + 304, { size: 23, weight: 800, fill: palette.muted });
}

function drawBilling(g, concept, state, t) {
  const baseX = 140;
  const baseY = 330;
  const meters = [
    ["input", 0.62, palette.blue],
    ["output", 0.82, palette.amber],
    ["model", 0.5 + 0.18 * wave(t * 0.2), palette.purple],
    ["loops", 0.36 + 0.36 * (state.index / 4), palette.red]
  ];
  meters.forEach(([label, value, color], i) => {
    const x = baseX + i * 250;
    addPanel(g, x, baseY, 205, 290, { fill: palette.white, radius: 20 });
    addLabel(g, label.toUpperCase(), x + 102, baseY + 58, { size: 22, weight: 900, anchor: "middle", fill: color });
    g.append("rect").attr("x", x + 68).attr("y", baseY + 95).attr("width", 70).attr("height", 150).attr("rx", 18).attr("fill", "#edf2f3");
    g.append("rect")
      .attr("x", x + 68)
      .attr("y", baseY + 245 - 150 * value)
      .attr("width", 70)
      .attr("height", 150 * value)
      .attr("rx", 18)
      .attr("fill", color);
    addLabel(g, `${Math.round(value * 100)}%`, x + 102, baseY + 270, { size: 24, weight: 900, anchor: "middle", fill: palette.ink });
  });
  addArrow(g, 206, 690, 1080, 690, concept.accent, { opacity: 0.65, dash: "10 16" });
  ["prompt", "cache", "retry", "accepted"].forEach((label, i) => addPacket(g, 250 + i * 240 + wave(t * 0.18, i) * 30, 690, i === state.index % 4 ? concept.accent : palette.slate, label));
}

function drawEvaluation(g, concept, state, t) {
  const x = 170;
  const y = 286;
  addPanel(g, x, y, 460, 360, { fill: palette.white, radius: 20 });
  addLabel(g, "TOKEN ODDS", x + 44, y + 60, { size: 26, weight: 900, fill: concept.accent });
  const bars = ["A", "B", "C", "D", "E"];
  bars.forEach((label, i) => {
    const v = 0.25 + 0.62 * wave(t * 0.2, i + state.index * 0.7);
    const h = 190 * v;
    g.append("rect").attr("x", x + 58 + i * 72).attr("y", y + 270 - h).attr("width", 48).attr("height", h).attr("rx", 10).attr("fill", i === state.index ? concept.accent : palette.line);
    addLabel(g, label, x + 82 + i * 72, y + 306, { size: 22, weight: 900, anchor: "middle", fill: palette.ink });
  });

  const gx = 735;
  const gy = 300;
  addLabel(g, "EVALUATION GRID", gx, gy - 24, { size: 26, weight: 900, fill: concept.accent });
  for (let row = 0; row < 4; row += 1) {
    for (let col = 0; col < 5; col += 1) {
      const idx = row * 5 + col;
      const pass = (idx + state.index) % 6 === 0 || (state.index > 2 && idx % 7 === 0);
      g.append("rect").attr("x", gx + col * 74).attr("y", gy + row * 66).attr("width", 54).attr("height", 46).attr("rx", 10).attr("fill", pass ? palette.green : "#e6ecee").attr("stroke", pass ? palette.green : palette.line).attr("stroke-width", 2);
      addLabel(g, pass ? "ok" : "x", gx + col * 74 + 27, gy + row * 66 + 31, { size: 18, weight: 900, anchor: "middle", fill: pass ? palette.white : palette.muted });
    }
  }
  addArrow(g, 630, 464, 722, 464, concept.accent, { opacity: 0.75 });
  addChip(g, "grade trace", 740, 600, palette.purple, { w: 190 });
  addChip(g, "pass@N", 958, 600, concept.accent, { w: 150 });
}

function drawAgent(g, concept, state, t) {
  const cx = 615;
  const cy = 470;
  const r = 230;
  g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", r).attr("fill", "none").attr("stroke", concept.accent).attr("stroke-width", 12).attr("stroke-linecap", "round").attr("opacity", 0.28);
  const arc = d3.arc().innerRadius(r - 6).outerRadius(r + 6).startAngle(0).endAngle(Math.PI * 2 * (0.22 + 0.18 * state.index));
  g.append("path").attr("d", arc()).attr("transform", `translate(${cx},${cy})`).attr("fill", concept.accent).attr("opacity", 0.7);
  const nodes = [
    ["observe", 0],
    ["decide", Math.PI / 2],
    ["act", Math.PI],
    ["check", Math.PI * 1.5]
  ];
  nodes.forEach(([label, angle], i) => {
    const x = cx + Math.cos(angle - Math.PI / 2) * r;
    const y = cy + Math.sin(angle - Math.PI / 2) * r;
    g.append("circle").attr("cx", x).attr("cy", y).attr("r", 64).attr("fill", i === state.index % 4 ? concept.accent : palette.white).attr("stroke", concept.accent).attr("stroke-width", 4).attr("filter", "url(#softShadow)");
    addLabel(g, label, x, y + 8, { size: 24, weight: 900, anchor: "middle", fill: i === state.index % 4 ? palette.white : concept.accent });
  });
  addLabel(g, "GOAL", cx, cy - 18, { size: 54, weight: 950, anchor: "middle", fill: palette.ink });
  addLabel(g, "state + tools + stopping rule", cx, cy + 32, { size: 24, weight: 700, anchor: "middle", fill: palette.muted });
  const dotAngle = t * 0.7;
  addPacket(g, cx + Math.cos(dotAngle - Math.PI / 2) * r, cy + Math.sin(dotAngle - Math.PI / 2) * r, concept.accent);
}

function drawGuardrail(g, concept, state, t) {
  const lanes = ["input", "output", "action"];
  lanes.forEach((lane, i) => {
    const y = 325 + i * 130;
    const laneProgress = (t * 0.18 + i * 0.21) % 1;
    addPacket(g, 180, y, i === state.index % 3 ? concept.accent : palette.slate, lane);
    addArrow(g, 250, y, 500, y, concept.accent, { opacity: 0.55 });
    addArrow(g, 690, y, 980, y, i === 1 ? palette.green : concept.accent, { opacity: 0.55 });
    addPacket(g, 270 + laneProgress * 680, y + Math.sin(laneProgress * Math.PI * 2) * 8, laneProgress > 0.45 && laneProgress < 0.58 ? palette.red : concept.accent);
    addChip(g, i === 1 ? "redact" : i === 2 ? "ask" : "allow", 990, y - 22, i === 1 ? palette.green : concept.accent, { w: 140 });
  });
  addPanel(g, 500, 230, 190, 470, { fill: "#fffafa", stroke: concept.accent, radius: 28 });
  g.append("path")
    .attr("d", "M595 286 L660 316 L648 442 C640 526 618 574 595 594 C572 574 550 526 542 442 L530 316 Z")
    .attr("fill", concept.accent)
    .attr("opacity", 0.88)
    .attr("filter", "url(#glow)");
  addLabel(g, "POLICY", 595, 454, { size: 27, weight: 950, anchor: "middle", fill: palette.white });
  addLabel(g, "gate", 595, 492, { size: 24, weight: 800, anchor: "middle", fill: palette.white });
  g.append("circle").attr("cx", 595).attr("cy", 600).attr("r", 14 + 5 * wave(t * 0.8)).attr("fill", concept.accent).attr("opacity", 0.35);
}

function drawHarness(g, concept, state) {
  const x = 250;
  const y = 250;
  const layers = [
    ["model", palette.blue],
    ["instructions", palette.slate],
    ["tools", palette.green],
    ["permissions", palette.red],
    ["loop + logs", palette.purple]
  ];
  layers.forEach(([label, color], i) => {
    const active = i === state.index;
    g.append("rect")
      .attr("x", x + i * 82)
      .attr("y", y + i * 58)
      .attr("width", 650)
      .attr("height", 78)
      .attr("rx", 18)
      .attr("fill", active ? color : palette.white)
      .attr("stroke", color)
      .attr("stroke-width", active ? 5 : 3)
      .attr("filter", "url(#softShadow)");
    addLabel(g, label, x + i * 82 + 44, y + i * 58 + 50, { size: 29, weight: 900, fill: active ? palette.white : color });
  });
  addArrow(g, 130, 455, 250, 455, concept.accent, { opacity: 0.72 });
  addPacket(g, 116, 455, concept.accent, "task");
  addArrow(g, 1030, 455, 1140, 455, concept.accent, { opacity: 0.72 });
  addPacket(g, 1160, 455, palette.green, "result");
}

function drawHook(g, concept, state, t) {
  const x = 160;
  const y = 480;
  const events = ["start", "prompt", "pre-tool", "permission", "post-tool", "stop"];
  g.append("line").attr("x1", x).attr("x2", x + 940).attr("y1", y).attr("y2", y).attr("stroke", palette.line).attr("stroke-width", 9).attr("stroke-linecap", "round");
  events.forEach((event, i) => {
    const cx = x + i * 188;
    const active = i === Math.min(events.length - 1, state.index + 1);
    g.append("circle").attr("cx", cx).attr("cy", y).attr("r", active ? 34 : 24).attr("fill", active ? concept.accent : palette.white).attr("stroke", concept.accent).attr("stroke-width", 4);
    addLabel(g, event, cx, y + 72, { size: 21, weight: active ? 900 : 700, anchor: "middle", fill: active ? concept.accent : palette.muted });
  });
  const hx = x + Math.min(events.length - 1, state.index + 1) * 188;
  addPanel(g, hx - 115, y - 210, 230, 120, { fill: "#fbfbff", stroke: concept.accent, radius: 20 });
  addLabel(g, "HOOK", hx, y - 156, { size: 34, weight: 950, anchor: "middle", fill: concept.accent });
  addLabel(g, "inspect -> decide", hx, y - 116, { size: 20, weight: 750, anchor: "middle", fill: palette.muted });
  addArrow(g, hx, y - 90, hx, y - 38, concept.accent, { opacity: 0.7 });
  addPacket(g, x + ((t * 0.12) % 1) * 940, y, concept.accent);
}

function drawPlugin(g, concept, state) {
  const cx = 595;
  const cy = 448;
  addPanel(g, cx - 220, cy - 170, 440, 340, { fill: "#fbfffe", stroke: concept.accent, radius: 26 });
  addLabel(g, "PLUGIN", cx, cy - 104, { size: 48, weight: 950, anchor: "middle", fill: concept.accent });
  const modules = ["skills", "hooks", "agents", "MCP", "settings"];
  modules.forEach((module, i) => {
    const angle = (i / modules.length) * Math.PI * 2 - Math.PI / 2;
    const x = cx + Math.cos(angle) * 130;
    const y = cy + 30 + Math.sin(angle) * 92;
    addChip(g, module, x - 66, y - 20, i === state.index ? concept.accent : palette.slate, { w: 132, h: 40 });
  });
  ["repo A", "repo B", "team"].forEach((target, i) => {
    const tx = 155 + i * 430;
    const ty = 745;
    addPanel(g, tx, ty, 210, 80, { fill: palette.white, radius: 16, shadow: false });
    addLabel(g, target, tx + 105, ty + 50, { size: 24, weight: 900, anchor: "middle", fill: palette.ink });
    addArrow(g, cx, cy + 190, tx + 105, ty - 8, concept.accent, { opacity: 0.45 });
    const installProgress = (state.local + i * 0.18) % 1;
    addPacket(g, cx + (tx + 105 - cx) * installProgress, cy + 190 + (ty - 8 - (cy + 190)) * installProgress, concept.accent);
  });
}

function drawSkill(g, concept, state) {
  const x = 210;
  const y = 250;
  const cards = [
    ["SKILL.md", "trigger + workflow", concept.accent],
    ["references", "detail on demand", palette.blue],
    ["scripts", "repeatable helpers", palette.purple],
    ["assets", "templates", palette.amber]
  ];
  cards.forEach(([title, body, color], i) => {
    const dx = i * 58;
    const dy = i * 72;
    const active = i === state.index % cards.length;
    addPanel(g, x + dx, y + dy, 620, 106, { fill: active ? color : palette.white, stroke: color, radius: 18 });
    addLabel(g, title, x + dx + 40, y + dy + 46, { size: 30, weight: 950, fill: active ? palette.white : color });
    addLabel(g, body, x + dx + 40, y + dy + 82, { size: 22, weight: 700, fill: active ? palette.white : palette.muted });
  });
  addArrow(g, 140, 610, 420, 610, concept.accent, { opacity: 0.6, dash: "12 16" });
  addPacket(g, 136, 610, concept.accent, "task");
  const loadProgress = (state.local * 1.2) % 1;
  addPacket(g, 160 + loadProgress * 520, 610 - Math.sin(loadProgress * Math.PI) * 82, concept.accent);
  g.append("circle")
    .attr("cx", 430 + (state.index % cards.length) * 58)
    .attr("cy", 300 + (state.index % cards.length) * 72)
    .attr("r", 22 + 16 * wave(state.local))
    .attr("fill", concept.accent)
    .attr("opacity", 0.18);
  addChip(g, "load only when needed", 790, 580, palette.green, { w: 260 });
}

function drawMcp(g, concept, state, t) {
  const busY = 500;
  g.append("line").attr("x1", 230).attr("x2", 1080).attr("y1", busY).attr("y2", busY).attr("stroke", concept.accent).attr("stroke-width", 20).attr("stroke-linecap", "round").attr("opacity", 0.72);
  addLabel(g, "MCP BUS", 655, busY - 40, { size: 36, weight: 950, anchor: "middle", fill: concept.accent });
  const clients = [["host", 190, 330], ["client", 190, 670]];
  const servers = [["tools", 1115, 300], ["resources", 1115, 500], ["prompts", 1115, 700]];
  [...clients, ...servers].forEach(([label, x, y], i) => {
    addPanel(g, x - 95, y - 45, 190, 90, { fill: palette.white, stroke: i === state.index ? concept.accent : palette.line, radius: 18, shadow: true });
    addLabel(g, label, x, y + 8, { size: 25, weight: 900, anchor: "middle", fill: i === state.index ? concept.accent : palette.ink });
    addArrow(g, x < 500 ? x + 96 : 1080, y, x < 500 ? 230 : x - 96, busY, concept.accent, { opacity: 0.42, width: 4 });
  });
  addPacket(g, 250 + ((t * 0.22) % 1) * 790, busY, palette.white);
}

function drawAlternatives(g, concept, state) {
  const x = 160;
  const y = 250;
  const cells = [
    ["knowledge", palette.teal],
    ["coding", palette.blue],
    ["productivity", palette.amber],
    ["custom harness", palette.purple]
  ];
  cells.forEach(([label, color], i) => {
    const cx = x + (i % 2) * 470;
    const cy = y + Math.floor(i / 2) * 220;
    addPanel(g, cx, cy, 390, 170, { fill: i === state.index % 4 ? color : palette.white, stroke: color, radius: 20 });
    addLabel(g, label, cx + 195, cy + 72, { size: 33, weight: 950, anchor: "middle", fill: i === state.index % 4 ? palette.white : color });
    addLabel(g, ["context", "actions", "plans", "control"][i], cx + 195, cy + 118, { size: 24, weight: 700, anchor: "middle", fill: i === state.index % 4 ? palette.white : palette.muted });
  });
  addLabel(g, "selection checklist", 390, 766, { size: 30, weight: 900, fill: concept.accent });
  ["context", "tools", "permissions", "eval", "billing"].forEach((label, i) => addChip(g, label, 390 + i * 138, 800, concept.accent, { w: 122 }));
  const pilot = (state.local + state.index * 0.12) % 1;
  addPacket(g, 386 + pilot * 620, 868, concept.accent, "pilot");
}

function drawObservability(g, concept, state, t) {
  const x = 190;
  const y = 245;
  addLabel(g, "RUN TRACE", x, y - 28, { size: 32, weight: 950, fill: concept.accent });
  const spans = [
    ["user goal", 0, 0, 260, palette.blue],
    ["model call", 1, -95, 230, palette.purple],
    ["tool read", 1, 95, 210, palette.teal],
    ["model call", 2, -150, 190, palette.purple],
    ["tool write", 2, 40, 170, palette.red],
    ["grader", 2, 220, 150, palette.green]
  ];
  spans.forEach(([label, depth, offset, width, color], i) => {
    const sx = x + depth * 275;
    const sy = y + 95 + i * 72;
    if (depth > 0) addArrow(g, sx - 95, sy - 36, sx - 14, sy, color, { opacity: 0.35, width: 3 });
    g.append("rect").attr("x", sx).attr("y", sy - 28).attr("width", width).attr("height", 52).attr("rx", 14).attr("fill", i === state.index ? color : palette.white).attr("stroke", color).attr("stroke-width", 3);
    addLabel(g, label, sx + 18, sy + 8, { size: 22, weight: 850, fill: i === state.index ? palette.white : color });
  });
  addPanel(g, 875, 320, 230, 270, { fill: palette.white, radius: 18 });
  ["latency", "cost", "errors", "success"].forEach((metric, i) => {
    const value = 0.35 + 0.45 * wave(t * 0.15, i);
    addLabel(g, metric, 912, 368 + i * 50, { size: 20, weight: 800, fill: palette.muted });
    g.append("rect").attr("x", 1002).attr("y", 350 + i * 50).attr("width", 78).attr("height", 16).attr("rx", 8).attr("fill", palette.line);
    g.append("rect").attr("x", 1002).attr("y", 350 + i * 50).attr("width", 78 * value).attr("height", 16).attr("rx", 8).attr("fill", i === 3 ? palette.green : concept.accent);
  });
}

function drawInstructions(g, concept, state) {
  const x = 255;
  const y = 235;
  const layers = [
    ["system", palette.ink],
    ["organization", palette.purple],
    ["repository", palette.blue],
    ["skill", palette.green],
    ["user", palette.amber]
  ];
  layers.forEach(([label, color], i) => {
    const ly = y + i * 92;
    const active = i === state.index;
    g.append("rect").attr("x", x + i * 45).attr("y", ly).attr("width", 700 - i * 50).attr("height", 72).attr("rx", 16).attr("fill", active ? color : palette.white).attr("stroke", color).attr("stroke-width", 4).attr("filter", "url(#softShadow)");
    addLabel(g, `${i + 1}. ${label}`, x + i * 45 + 36, ly + 46, { size: 28, weight: 950, fill: active ? palette.white : color });
    if (active) {
      g.append("rect")
        .attr("x", x + i * 45 + 20 + state.local * (620 - i * 45))
        .attr("y", ly + 10)
        .attr("width", 42)
        .attr("height", 52)
        .attr("rx", 12)
        .attr("fill", palette.white)
        .attr("opacity", 0.24);
    }
  });
  addArrow(g, 1080, 275, 1080, 650, concept.accent, { opacity: 0.55 });
  addPacket(g, 1080, 290 + state.local * 330, concept.accent);
  addLabel(g, "precedence", 1080, 712, { size: 26, weight: 900, anchor: "middle", fill: concept.accent });
}

function drawPermissions(g, concept, state) {
  const tools = [
    ["read", palette.green, "allow"],
    ["write", palette.amber, "ask"],
    ["run", palette.red, "ask"],
    ["deploy", palette.red, "deny"]
  ];
  tools.forEach(([tool, color, policy], i) => {
    const x = 170 + i * 250;
    const y = 330 + (i % 2) * 160;
    addPanel(g, x, y, 205, 118, { fill: palette.white, stroke: color, radius: 18 });
    addLabel(g, tool, x + 102, y + 52, { size: 30, weight: 950, anchor: "middle", fill: color });
    addChip(g, policy, x + 43, y + 72, policy === "allow" ? palette.green : policy === "deny" ? palette.red : palette.amber, { w: 120, h: 38 });
    if (i === state.index % tools.length) {
      g.append("circle").attr("cx", x + 172).attr("cy", y + 30).attr("r", 13 + 8 * wave(state.local)).attr("fill", color).attr("opacity", 0.28);
    }
  });
  addPanel(g, 525, 620, 360, 130, { fill: "#fffafa", stroke: concept.accent, radius: 22 });
  addLabel(g, "approval context", 705, 672, { size: 30, weight: 950, anchor: "middle", fill: concept.accent });
  addLabel(g, "target + reason + radius", 705, 716, { size: 22, weight: 750, anchor: "middle", fill: palette.muted });
  addArrow(g, 940, 685, 1080, 685, concept.accent, { opacity: 0.62 });
  addPacket(g, 888 + state.local * 205, 685, concept.accent);
  addChip(g, state.index > 2 ? "audit" : "hold", 1098, 664, state.index > 2 ? palette.green : palette.amber, { w: 126 });
}

function drawGovernance(g, concept, state, t) {
  const zones = [
    ["user", 205, 325, palette.blue],
    ["repo", 460, 525, palette.purple],
    ["connector", 740, 330, palette.teal],
    ["logs", 980, 545, palette.amber]
  ];
  zones.forEach(([label, x, y, color], i) => {
    g.append("circle").attr("cx", x).attr("cy", y).attr("r", i === state.index % 4 ? 92 : 76).attr("fill", palette.white).attr("stroke", color).attr("stroke-width", 5).attr("filter", "url(#softShadow)");
    addLabel(g, label, x, y + 8, { size: 28, weight: 950, anchor: "middle", fill: color });
  });
  addArrow(g, 292, 353, 400, 490, concept.accent, { opacity: 0.45 });
  addArrow(g, 536, 500, 680, 360, concept.accent, { opacity: 0.45 });
  addArrow(g, 814, 366, 920, 510, concept.accent, { opacity: 0.45 });
  addPanel(g, 520, 230, 250, 96, { fill: "#f7fffd", stroke: concept.accent, radius: 18 });
  addLabel(g, "identity scope", 645, 268, { size: 26, weight: 950, anchor: "middle", fill: concept.accent });
  addLabel(g, "same access as user", 645, 304, { size: 20, weight: 750, anchor: "middle", fill: palette.muted });
  g.append("circle").attr("cx", 645).attr("cy", 672).attr("r", 46 + 8 * wave(t * 0.55)).attr("fill", concept.accent).attr("opacity", 0.18);
  addChip(g, "retention", 545, 650, palette.amber, { w: 160 });
  addChip(g, "training use", 720, 650, palette.red, { w: 180 });
}

const renderers = {
  llm: drawTokenFlow,
  billing: drawBilling,
  evaluation: drawEvaluation,
  agent: drawAgent,
  guardrail: drawGuardrail,
  harness: drawHarness,
  hook: drawHook,
  plugin: drawPlugin,
  skill: drawSkill,
  mcp: drawMcp,
  alternatives: drawAlternatives,
  observability: drawObservability,
  instructions: drawInstructions,
  permissions: drawPermissions,
  governance: drawGovernance
};

function addSharedSymbol(svg, concept, state, t) {
  const x = 110;
  const y = 820;
  const trackY = 866;
  const g = svg.append("g").attr("opacity", 0.9);
  const travel = (t * 0.11) % 1;
  g.append("line")
    .attr("x1", x - 8)
    .attr("x2", x + 520)
    .attr("y1", trackY)
    .attr("y2", trackY)
    .attr("stroke", concept.accent)
    .attr("stroke-width", 3)
    .attr("stroke-dasharray", "8 18")
    .attr("opacity", 0.25);
  addPacket(g, x + travel * 500, trackY, concept.accent);
  addLabel(g, "shared work packet", x + 80, y + 8, { size: 22, weight: 800, fill: palette.muted });
}

export function renderConceptFrame(id, time = 0, options = {}) {
  const concept = conceptById.get(id) ?? concepts[0];
  const state = sceneState(concept, time);
  stage.selectAll("*").remove();

  const svg = stage.append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
  addDefs(svg, concept.accent);
  addBackground(svg, concept, time);
  addHeader(svg, concept, state);
  addSceneText(svg, concept, state);
  addConceptRail(svg, concept);
  addSharedSymbol(svg, concept, state, time);

  const main = svg.append("g").attr("class", "main-visual");
  const renderer = renderers[concept.kind] ?? drawTokenFlow;
  renderer(main, concept, state, time);

  const elementCount = svg.selectAll("*").size();
  const textCount = svg.selectAll("text").size();
  const bbox = svg.node().getBBox();
  const report = {
    id: concept.id,
    title: concept.title,
    sceneIndex: state.index,
    sceneHeadline: state.scene.headline,
    time: Number(time.toFixed(3)),
    elementCount,
    textCount,
    bbox: {
      x: Number(bbox.x.toFixed(1)),
      y: Number(bbox.y.toFixed(1)),
      width: Number(bbox.width.toFixed(1)),
      height: Number(bbox.height.toFixed(1))
    }
  };

  if (options.capture) return report;
  return report;
}

window.renderConceptFrame = renderConceptFrame;
window.aiConceptVideos = { concepts, project };

renderConceptFrame(new URLSearchParams(window.location.search).get("id") ?? concepts[0].id, 0);

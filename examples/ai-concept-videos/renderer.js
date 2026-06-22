import { beats, concepts, palette, researchNotes } from "./concepts.js";
import { drawEvaluationVisualOnly } from "./scenes/evaluation.js";
import { drawGenericConceptVisualOnly } from "./scenes/generic-visuals.js";
import { drawLlmHandoffVisualOnly } from "./scenes/llm-handoff.js";
import { drawLlmImplicationVisualOnly } from "./scenes/llm-implication.js";
import { drawLlmMechanismVisualOnly } from "./scenes/llm-mechanism.js";
import { drawLlmModelBox } from "./scenes/llm-model-box.js";

const SVG_WIDTH = 760;
const SVG_HEIGHT = 448;
const DURATION = 120;
const beatColors = {
  hook: palette.redHighlight,
  definition: palette.blueHighlight,
  mechanism: palette.greenHighlight,
  implication: palette.orangeHighlight,
  handoff: palette.purpleHighlight
};

const svg = d3.select("#concept-svg");
let currentConcept = concepts[0];
let lastBeatId = "";
let playbackFrame = 0;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function easeInOut(t) {
  const x = clamp(t, 0, 1);
  return x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;
}

function easeOut(t) {
  return 1 - Math.pow(1 - clamp(t, 0, 1), 3);
}

function formatTime(seconds) {
  const s = Math.floor(clamp(seconds, 0, DURATION));
  const minutes = String(Math.floor(s / 60)).padStart(2, "0");
  const rest = String(s % 60).padStart(2, "0");
  return `${minutes}:${rest}`;
}

function beatForTime(seconds) {
  return beats.find((beat) => seconds >= beat.start && seconds < beat.end) ?? beats.at(-1);
}

function sceneForTime(concept, seconds) {
  const beat = beatForTime(seconds);
  const scene = concept.scenes.find((item) => item.beat === beat.id) ?? concept.scenes[0];
  const progress = clamp((seconds - beat.start) / (beat.end - beat.start), 0, 1);
  return { beat, scene, progress };
}

function selectConcept(id) {
  if (!id) return concepts[0];
  const numeric = Number(id);
  if (Number.isFinite(numeric) && numeric >= 1 && numeric <= concepts.length) {
    return concepts[numeric - 1];
  }
  return concepts.find((item) => item.id === id || item.shortTitle.toLowerCase() === String(id).toLowerCase()) ?? concepts[0];
}

function isVisualOnlyConcept(concept) {
  return concept.visualOnly === true || concept.kind !== "llm";
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) node.textContent = value;
}

function renderBullets(scene, sceneProgress) {
  const list = document.getElementById("scene-bullets");
  list.replaceChildren();
  scene.bullets.forEach((bullet, index) => {
    const li = document.createElement("li");
    li.textContent = bullet;
    const reveal = easeOut((sceneProgress - index * 0.12) / 0.38);
    li.style.opacity = String(0.28 + reveal * 0.72);
    li.style.transform = `translateX(${Math.round((1 - reveal) * 12)}px)`;
    list.appendChild(li);
  });
}

function renderMetrics(concept, seconds) {
  const metrics = document.getElementById("metrics");
  metrics.replaceChildren();
  concept.metrics.forEach((metric, index) => {
    const pulse = 0.92 + Math.sin(seconds * 0.09 + index * 1.7) * 0.08;
    const value = clamp(metric.value * pulse, 0.05, 1);
    const row = document.createElement("div");
    row.className = "metric";
    const top = document.createElement("div");
    top.className = "metric-top";
    const label = document.createElement("span");
    label.textContent = metric.label;
    const number = document.createElement("span");
    number.className = "metric-value";
    number.textContent = `${Math.round(value * 100)}%`;
    const track = document.createElement("div");
    track.className = "metric-track";
    const fill = document.createElement("div");
    fill.className = "metric-fill";
    fill.style.width = `${Math.round(value * 100)}%`;
    fill.style.background = metric.color;
    top.append(label, number);
    track.appendChild(fill);
    row.append(top, track);
    metrics.appendChild(row);
  });

  const tags = document.getElementById("source-tags");
  tags.replaceChildren();
  concept.sourceIds.forEach((tag) => {
    const node = document.createElement("span");
    node.textContent = tag;
    tags.appendChild(node);
  });
}

function renderBeatTrack(seconds) {
  const track = document.getElementById("beat-track");
  track.replaceChildren();
  beats.forEach((beat) => {
    const segment = document.createElement("div");
    segment.className = "beat-segment";
    const fill = seconds <= beat.start ? 0 : seconds >= beat.end ? 100 : ((seconds - beat.start) / (beat.end - beat.start)) * 100;
    segment.style.setProperty("--fill", `${fill}%`);
    segment.style.setProperty("--segment-color", beatColors[beat.id]);
    const label = document.createElement("span");
    label.textContent = `${formatTime(beat.start)} ${beat.label}`;
    segment.appendChild(label);
    track.appendChild(segment);
  });
}

function setInterface(concept, seconds) {
  const { beat, scene, progress } = sceneForTime(concept, seconds);
  const conceptIndex = concepts.findIndex((item) => item.id === concept.id) + 1;
  setText("concept-index", `Concept ${String(conceptIndex).padStart(2, "0")} / ${concepts.length}`);
  setText("concept-title", concept.title);
  setText("core-idea", concept.coreIdea);
  setText("beat-label", `${beat.label} | ${formatTime(beat.start)}-${formatTime(beat.end)}`);
  setText("scene-headline", scene.headline);
  setText("scene-callout", scene.callout);
  setText("timer", `${formatTime(seconds)} / 02:00`);
  setText("handoff-line", scene.callout);
  setText("source-lockup", `Research checked ${researchNotes[0].checked}`);
  const beatLabel = document.getElementById("beat-label");
  if (beatLabel) {
    beatLabel.style.background = beatColors[beat.id];
    beatLabel.style.color = beat.id === "handoff" ? palette.purpleHover : palette.brandNeutral;
  }
  const callout = document.getElementById("scene-callout");
  if (callout) {
    callout.style.background = beatColors[beat.id];
    callout.style.borderLeftColor = beat.id === "hook" ? palette.red : beat.id === "definition" ? palette.blue : beat.id === "mechanism" ? palette.green : beat.id === "implication" ? palette.orange : palette.purple;
  }
  renderBullets(scene, progress);
  renderMetrics(concept, seconds);
  renderBeatTrack(seconds);

  if (beat.id !== lastBeatId && document.body.dataset.capture !== "1") {
    lastBeatId = beat.id;
    runAnimeCue();
  }
}

function runAnimeCue() {
  const api = window.anime || window.animejs;
  const animate = api?.animate ?? (typeof api === "function" ? api : null);
  if (!animate) return;

  try {
    animate(".script-panel li", {
      opacity: [0.2, 1],
      translateX: [18, 0],
      delay: api.stagger ? api.stagger(55) : 0,
      duration: 460,
      ease: "outQuad"
    });
    animate(".metric-fill", {
      scaleX: [0.72, 1],
      transformOrigin: "left center",
      delay: api.stagger ? api.stagger(45) : 0,
      duration: 520,
      ease: "outExpo"
    });
  } catch (_) {
    // Anime.js is an enhancement for preview mode. Deterministic capture does not depend on it.
  }
}

function prepareSvg(concept, seconds) {
  const visualOnly = isVisualOnlyConcept(concept);
  const frameWidth = visualOnly ? 1280 : SVG_WIDTH;
  const frameHeight = visualOnly ? 720 : SVG_HEIGHT;
  svg.selectAll("*").remove();
  svg.attr("aria-label", concept.title);
  svg.attr("viewBox", `0 0 ${frameWidth} ${frameHeight}`);

  const defs = svg.append("defs");
  const grid = defs.append("pattern")
    .attr("id", "soft-grid")
    .attr("width", 32)
    .attr("height", 32)
    .attr("patternUnits", "userSpaceOnUse");
  grid.append("path")
    .attr("d", "M 32 0 L 0 0 0 32")
    .attr("fill", "none")
    .attr("stroke", palette.gray100)
    .attr("stroke-width", 1);

  const glow = defs.append("filter").attr("id", "soft-glow").attr("x", "-20%").attr("y", "-20%").attr("width", "140%").attr("height", "140%");
  glow.append("feGaussianBlur").attr("stdDeviation", 3).attr("result", "blur");
  const merge = glow.append("feMerge");
  merge.append("feMergeNode").attr("in", "blur");
  merge.append("feMergeNode").attr("in", "SourceGraphic");

  svg.append("rect").attr("width", frameWidth).attr("height", frameHeight).attr("fill", "#ffffff");
  svg.append("rect").attr("width", frameWidth).attr("height", frameHeight).attr("fill", "url(#soft-grid)").attr("opacity", visualOnly ? 0.34 : 0.72);
  if (!visualOnly) {
    svg.append("text")
      .attr("x", 24)
      .attr("y", 31)
      .attr("class", "svg-title")
      .text(concept.shortTitle);
    svg.append("text")
      .attr("x", SVG_WIDTH - 24)
      .attr("y", SVG_HEIGHT - 16)
      .attr("text-anchor", "end")
      .attr("class", "capture-watermark")
      .text(`frame ${formatTime(seconds)}`);
  }

  if (!visualOnly) {
    const sync = svg.append("g").attr("transform", `translate(${frameWidth - 234},24)`);
    sync.append("rect").attr("width", 190).attr("height", 28).attr("rx", 14).attr("fill", "#ffffff").attr("stroke", palette.gray200);
    sync.append("rect").attr("x", 8).attr("y", 11).attr("width", 128).attr("height", 6).attr("rx", 3).attr("fill", palette.gray100);
    sync.append("rect").attr("x", 8).attr("y", 11).attr("width", 128 * (seconds / DURATION)).attr("height", 6).attr("rx", 3).attr("fill", palette.red);
    d3.range(4).forEach((index) => {
      const phase = progressPulse(seconds, index * 0.18, 4);
      sync.append("circle")
        .attr("cx", 150 + index * 10)
        .attr("cy", 14)
        .attr("r", 3 + phase * 2.5)
        .attr("fill", [palette.blue, palette.green, palette.orange, palette.purple][index])
        .attr("opacity", 0.25 + (1 - phase) * 0.7);
    });

    const activeBeat = beatForTime(seconds);
    const beatRail = svg.append("g").attr("transform", "translate(24,388)");
    beats.forEach((beat, index) => {
      const isActive = beat.id === activeBeat.id;
      const fill = beatColors[beat.id];
      const x = index * 68;
      beatRail.append("rect")
        .attr("x", x)
        .attr("y", 0)
        .attr("width", 58)
        .attr("height", 18)
        .attr("rx", 7)
        .attr("fill", fill)
        .attr("stroke", isActive ? palette.brandPrimary : palette.gray200)
        .attr("stroke-width", isActive ? 2.5 : 1)
        .attr("opacity", isActive ? 1 : 0.62);
      beatRail.append("text")
        .attr("x", x + 29)
        .attr("y", 12)
        .attr("text-anchor", "middle")
        .attr("class", "svg-small")
        .text(String(index + 1));
    });
  }
}

function chip(g, x, y, text, options = {}) {
  const padding = options.padding ?? 12;
  const width = options.width ?? Math.max(64, text.length * 7.5 + padding * 2);
  const height = options.height ?? 30;
  const group = g.append("g").attr("transform", `translate(${x},${y})`).attr("opacity", options.opacity ?? 1);
  group.append("rect")
    .attr("width", width)
    .attr("height", height)
    .attr("rx", 8)
    .attr("fill", options.fill ?? palette.blueHighlight)
    .attr("stroke", options.stroke ?? palette.blue)
    .attr("stroke-opacity", options.strokeOpacity ?? 0.45);
  group.append("text")
    .attr("x", width / 2)
    .attr("y", height / 2 + 4)
    .attr("text-anchor", "middle")
    .attr("class", "svg-small")
    .attr("fill", options.textColor ?? palette.brandNeutral)
    .text(text);
  return group;
}

function arrow(g, x1, y1, x2, y2, color = palette.gray500, opacity = 1, width = 2.5) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const angle = Math.atan2(dy, dx);
  const head = 9;
  const hx = x2 - Math.cos(angle) * head;
  const hy = y2 - Math.sin(angle) * head;
  g.append("line")
    .attr("x1", x1)
    .attr("y1", y1)
    .attr("x2", hx)
    .attr("y2", hy)
    .attr("stroke", color)
    .attr("stroke-width", width)
    .attr("stroke-linecap", "round")
    .attr("opacity", opacity);
  g.append("path")
    .attr("d", `M${x2},${y2} L${hx - Math.cos(angle - Math.PI / 2) * 5},${hy - Math.sin(angle - Math.PI / 2) * 5} L${hx - Math.cos(angle + Math.PI / 2) * 5},${hy - Math.sin(angle + Math.PI / 2) * 5} Z`)
    .attr("fill", color)
    .attr("opacity", opacity);
}

function movingDotOnLine(g, x1, y1, x2, y2, progress, color = palette.red, r = 6) {
  const p = clamp(progress, 0, 1);
  g.append("circle")
    .attr("cx", x1 + (x2 - x1) * p)
    .attr("cy", y1 + (y2 - y1) * p)
    .attr("r", r)
    .attr("fill", color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .attr("filter", "url(#soft-glow)");
}

function progressPulse(seconds, offset = 0, period = 5) {
  return (seconds / period + offset) % 1;
}

function lerp(start, end, progress) {
  return start + (end - start) * clamp(progress, 0, 1);
}

function drawTokenRect(g, x, y, width, height, color, opacity = 1, stroke = "#ffffff") {
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", width)
    .attr("height", height)
    .attr("rx", Math.min(9, height / 2))
    .attr("fill", color)
    .attr("stroke", stroke)
    .attr("stroke-width", 2)
    .attr("opacity", opacity);
}

const hookPrompt = "AI tools write code";
const hookTokens = [
  { raw: "AI", piece: "AI", id: "15836", color: palette.blue, start: 0, length: 2 },
  { raw: " tools", piece: "tools", id: "7526", color: palette.green, start: 2, length: 6 },
  { raw: " write", piece: "write", id: "3350", color: palette.orange, start: 8, length: 6 },
  { raw: " code", piece: "code", id: "2082", color: palette.red, start: 14, length: 5 }
];

function approximateHookTextWidth(text, fontSize = 56) {
  return Array.from(text).reduce((total, char) => {
    if (char === " ") return total + fontSize * 0.34;
    if (/[A-Z]/.test(char)) return total + fontSize * 0.68;
    if (/[il]/.test(char)) return total + fontSize * 0.28;
    return total + fontSize * 0.55;
  }, 0);
}

function drawHookText(g, text, x, y, options = {}) {
  return g.append("text")
    .attr("x", x)
    .attr("y", y)
    .attr("text-anchor", options.anchor ?? "middle")
    .attr("dominant-baseline", options.baseline ?? "middle")
    .attr("font-family", "'Open Sans', Arial, sans-serif")
    .attr("font-size", options.size ?? 30)
    .attr("font-weight", options.weight ?? 820)
    .attr("fill", options.fill ?? palette.brandNeutral)
    .attr("opacity", options.opacity ?? 1)
    .text(text);
}

function measureHookText(g, text, size = 56, weight = 820) {
  const node = drawHookText(g, text, 0, 0, {
    anchor: "start",
    size,
    weight,
    opacity: 0
  }).node();
  let total = approximateHookTextWidth(text, size);
  const prefix = (count) => approximateHookTextWidth(text.slice(0, count), size);
  const segment = (start, length) => approximateHookTextWidth(text.slice(start, start + length), size);
  if (node) {
    try {
      total = node.getComputedTextLength();
    } catch (_) {
      total = approximateHookTextWidth(text, size);
    }
  }
  const measured = {
    total,
    prefix(count) {
      if (!node || count <= 0) return count <= 0 ? 0 : prefix(count);
      try {
        return node.getSubStringLength(0, count);
      } catch (_) {
        return prefix(count);
      }
    },
    segment(start, length) {
      if (!node || length <= 0) return length <= 0 ? 0 : segment(start, length);
      try {
        return node.getSubStringLength(start, length);
      } catch (_) {
        return segment(start, length);
      }
    },
    bounds(start, length) {
      if (!node || length <= 0) {
        return {
          x: prefix(start),
          y: -size * 0.76,
          w: segment(start, length),
          h: size
        };
      }
      const boxes = [];
      for (let index = start; index < start + length; index += 1) {
        try {
          const box = node.getExtentOfChar(index);
          boxes.push({
            x: box.x,
            y: box.y,
            w: box.width,
            h: box.height
          });
        } catch (_) {
          // Some renderers can reject whitespace or unresolved glyph indexes; fall back below.
        }
      }
      if (!boxes.length) {
        return {
          x: prefix(start),
          y: -size * 0.76,
          w: segment(start, length),
          h: size
        };
      }
      const minX = d3.min(boxes, (box) => box.x);
      const minY = d3.min(boxes, (box) => box.y);
      const maxX = d3.max(boxes, (box) => box.x + box.w);
      const maxY = d3.max(boxes, (box) => box.y + box.h);
      return { x: minX, y: minY, w: maxX - minX, h: maxY - minY };
    }
  };
  d3.select(node).remove();
  return measured;
}

function roundedRectPath(x, y, width, height, radius) {
  const r = Math.min(radius, width / 2, height / 2);
  return [
    `M${x + r},${y}`,
    `H${x + width - r}`,
    `Q${x + width},${y} ${x + width},${y + r}`,
    `V${y + height - r}`,
    `Q${x + width},${y + height} ${x + width - r},${y + height}`,
    `H${x + r}`,
    `Q${x},${y + height} ${x},${y + height - r}`,
    `V${y + r}`,
    `Q${x},${y} ${x + r},${y}`,
    "Z"
  ].join(" ");
}

function drawHookCard(g, x, y, width, height, color, opacity, options = {}) {
  const rx = options.rx ?? 12;
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", width)
    .attr("height", height)
    .attr("rx", rx)
    .attr("fill", options.fill ?? "#ffffff")
    .attr("stroke", color)
    .attr("stroke-width", options.strokeWidth ?? 4)
    .attr("opacity", opacity)
    .attr("filter", options.filter ?? null);
  if (options.fillBand) {
    g.append("rect")
      .attr("x", x + 7)
      .attr("y", y + 7)
      .attr("width", Math.max(0, width - 14))
      .attr("height", Math.max(0, height - 14))
      .attr("rx", Math.max(2, rx - 4))
      .attr("fill", color)
      .attr("opacity", opacity * 0.12);
  }
}

function tokenCardGeometry(from, to, progress) {
  return {
    x: lerp(from.x, to.x, progress),
    y: lerp(from.y, to.y, progress),
    w: lerp(from.w, to.w, progress),
    h: lerp(from.h, to.h, progress)
  };
}

function llmDefinitionDecisionLayout() {
  const band = { y: 210, h: 270 };
  const columnW = 330;
  const objectSize = 270;
  const columns = [
    { x: 64, w: columnW },
    { x: 475, w: columnW },
    { x: 886, w: columnW }
  ];
  return {
    band,
    columns,
    objectSize,
    matrix: {
      x: columns[0].x + (columns[0].w - objectSize) / 2,
      y: band.y,
      w: objectSize,
      h: objectSize
    },
    llm: {
      x: columns[1].x + (columns[1].w - objectSize) / 2,
      y: band.y,
      w: objectSize,
      h: objectSize
    },
    roulette: {
      x: columns[2].x,
      y: band.y,
      w: columns[2].w,
      h: objectSize
    }
  };
}

function contextMatrixLayout(matrix, options = {}) {
  const cols = options.cols ?? 8;
  const rows = options.rows ?? 8;
  const cell = options.cell ?? 24;
  const gap = options.gap ?? 8;
  const gridW = cols * cell + (cols - 1) * gap;
  const gridH = rows * cell + (rows - 1) * gap;
  const grid = {
    x: matrix.x + (matrix.w - gridW) / 2,
    y: matrix.y + (matrix.h - gridH) / 2
  };
  const slot = (index) => ({
    x: grid.x + (index % cols) * (cell + gap),
    y: grid.y + Math.floor(index / cols) * (cell + gap),
    w: cell,
    h: cell
  });
  return { cols, rows, cell, gap, grid, slot };
}

function drawHookContextMatrix(g, matrix, occupiedTokens, options = {}) {
  const layout = contextMatrixLayout(matrix, options);
  const opacity = options.opacity ?? 1;
  const cellOpacity = options.cellOpacity ?? 0.74;
  const occupiedOpacity = options.occupiedOpacity ?? 1;
  const backgroundOpacity = options.backgroundOpacity ?? 0.94;

  g.append("rect")
    .attr("x", matrix.x)
    .attr("y", matrix.y)
    .attr("width", matrix.w)
    .attr("height", matrix.h)
    .attr("rx", 16)
    .attr("fill", "#ffffff")
    .attr("stroke", "none")
    .attr("opacity", opacity * backgroundOpacity);

  const cells = d3.range(layout.rows * layout.cols).map((index) => ({
    index,
    row: Math.floor(index / layout.cols),
    col: index % layout.cols
  }));
  g.append("g")
    .selectAll("rect")
    .data(cells)
    .join("rect")
    .attr("x", (cell) => layout.grid.x + cell.col * (layout.cell + layout.gap))
    .attr("y", (cell) => layout.grid.y + cell.row * (layout.cell + layout.gap))
    .attr("width", layout.cell)
    .attr("height", layout.cell)
    .attr("rx", 4)
    .attr("fill", palette.gray100)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.6)
    .attr("opacity", opacity * cellOpacity);

  g.append("g")
    .selectAll("rect")
    .data(occupiedTokens)
    .join("rect")
    .attr("x", (_, index) => layout.slot(index).x)
    .attr("y", (_, index) => layout.slot(index).y)
    .attr("width", layout.cell)
    .attr("height", layout.cell)
    .attr("rx", 4)
    .attr("fill", (token) => token.color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.8)
    .attr("opacity", opacity * occupiedOpacity);

  return layout;
}

function drawLlmHookVisualOnly(g, seconds, sceneProgress, pulse) {
  const local = clamp(sceneProgress, 0, 1);
  const typeP = easeOut(local / 0.28);
  const outlineP = easeInOut((local - 0.26) / 0.18);
  const liftP = easeInOut((local - 0.42) / 0.18);
  const idP = easeInOut((local - 0.58) / 0.16);
  const matrixP = easeInOut((local - 0.72) / 0.22);
  const typedChars = Math.floor(hookPrompt.length * typeP + 0.0001);
  const textSize = 58;
  const textY = 154;
  const sourcePadX = 10;
  const sourceGap = 22;
  const tokenGap = 24;
  const tokenY = 282;
  const idY = 330;
  const matrix = { x: 496, y: 398, w: 288, h: 288 };
  if (local >= 0.985) {
    drawHookContextMatrix(g, matrix, hookTokens, {
      opacity: 1,
      backgroundOpacity: 0.94,
      occupiedOpacity: 0.96,
      cellOpacity: 0.74,
      cell: 24,
      gap: 8
    });
    return;
  }
  const matrixCell = 24;
  const matrixGap = 8;
  const matrixCols = 8;
  const matrixRows = 8;
  const matrixGridW = matrixCols * matrixCell + (matrixCols - 1) * matrixGap;
  const matrixGridH = matrixRows * matrixCell + (matrixRows - 1) * matrixGap;
  const matrixGrid = {
    x: matrix.x + (matrix.w - matrixGridW) / 2,
    y: matrix.y + (matrix.h - matrixGridH) / 2
  };
  const matrixDestinations = [
    { row: 0, col: 0 },
    { row: 0, col: 1 },
    { row: 0, col: 2 },
    { row: 0, col: 3 }
  ];
  const tokenFontSize = 32;
  const idFontSize = 30;
  const sourceMeasures = hookTokens.map((token) => measureHookText(g, token.piece, textSize, 820));
  const sourceWidths = sourceMeasures.map((measure) => measure.total + sourcePadX * 2);
  const totalSourceTextWidth = d3.sum(sourceMeasures, (measure) => measure.total) + sourceGap * (hookTokens.length - 1);
  let sourceCursor = (1280 - totalSourceTextWidth) / 2;
  const sourceCards = hookTokens.map((_, index) => {
    const card = {
      x: sourceCursor - sourcePadX,
      y: textY - 36,
      w: sourceWidths[index],
      h: 72
    };
    sourceCursor += sourceMeasures[index].total + sourceGap;
    return card;
  });
  const tokenWidths = hookTokens.map((token) => {
    const pieceWidth = measureHookText(g, token.piece, tokenFontSize, 820).total;
    const idWidth = measureHookText(g, token.id, idFontSize, 850).total;
    return Math.max(pieceWidth + 50, idWidth + 48, 96);
  });
  const totalTokenWidth = d3.sum(tokenWidths) + tokenGap * (hookTokens.length - 1);
  let tokenCursor = (1280 - totalTokenWidth) / 2;
  const tokenTargets = hookTokens.map((_, index) => {
    const target = { x: tokenCursor, y: tokenY, w: tokenWidths[index], h: 62 };
    tokenCursor += tokenWidths[index] + tokenGap;
    return target;
  });
  const idTargets = tokenTargets.map((target) => ({ ...target, y: idY, h: 56 }));
  const matrixTargets = hookTokens.map((_, index) => ({
    x: matrixGrid.x + matrixDestinations[index].col * (matrixCell + matrixGap),
    y: matrixGrid.y + matrixDestinations[index].row * (matrixCell + matrixGap),
    w: matrixCell,
    h: matrixCell
  }));
  const promptOpacity = (1 - matrixP * 0.92);

  g.append("rect")
    .attr("x", 96)
    .attr("y", 78)
    .attr("width", 1088)
    .attr("height", 156)
    .attr("rx", 18)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 3)
    .attr("opacity", 0.94 * promptOpacity);
  if (typeP < 1 || (local < 0.42 && seconds % 1 < 0.55)) {
    let cursorX = sourceCards[0].x + sourcePadX;
    for (let index = 0; index < hookTokens.length; index += 1) {
      const token = hookTokens[index];
      const visibleStart = token.start + (token.raw.startsWith(" ") ? 1 : 0);
      const visibleEnd = visibleStart + token.piece.length;
      if (typedChars < visibleStart) {
        cursorX = sourceCards[index].x - sourceGap / 2;
        break;
      }
      if (typedChars <= visibleEnd) {
        const visiblePiece = token.piece.slice(0, Math.max(0, typedChars - visibleStart));
        cursorX = sourceCards[index].x + sourcePadX + measureHookText(g, visiblePiece, textSize, 820).total;
        break;
      }
      cursorX = sourceCards[index].x + sourcePadX + sourceMeasures[index].total;
    }
    g.append("rect")
      .attr("x", cursorX + 6)
      .attr("y", textY - 40)
      .attr("width", 5)
      .attr("height", 58)
      .attr("rx", 2)
      .attr("fill", palette.brandPrimary)
      .attr("opacity", promptOpacity * 0.82);
  }

  g.append("rect")
    .attr("x", matrix.x)
    .attr("y", matrix.y)
    .attr("width", matrix.w)
    .attr("height", matrix.h)
    .attr("rx", 16)
    .attr("fill", "#ffffff")
    .attr("stroke", "none")
    .attr("stroke-width", 0)
    .attr("opacity", matrixP * 0.94);

  const matrixCells = d3.range(matrixRows * matrixCols).map((cellIndex) => ({
    index: cellIndex,
    row: Math.floor(cellIndex / matrixCols),
    col: cellIndex % matrixCols
  }));
  g.append("g")
    .selectAll("rect")
    .data(matrixCells)
    .join("rect")
    .attr("x", (cell) => matrixGrid.x + cell.col * (matrixCell + matrixGap))
    .attr("y", (cell) => matrixGrid.y + cell.row * (matrixCell + matrixGap))
    .attr("width", matrixCell)
    .attr("height", matrixCell)
    .attr("rx", 4)
    .attr("fill", palette.gray100)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.6)
    .attr("opacity", (cell) => matrixP * clamp(matrixP * 1.4 - cell.index * 0.006, 0, 1) * 0.74);

  g.append("g")
    .selectAll("rect")
    .data(hookTokens)
    .join("rect")
    .attr("x", (_, index) => matrixTargets[index].x)
    .attr("y", (_, index) => matrixTargets[index].y)
    .attr("width", matrixCell)
    .attr("height", matrixCell)
    .attr("rx", 4)
    .attr("fill", (token) => token.color)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 1.8)
    .attr("opacity", (_, index) => matrixP * clamp(matrixP * 1.7 - index * 0.16, 0, 1) * 0.28);

  const tokenLayer = g.append("g").selectAll("g.hook-token")
    .data(hookTokens)
    .join("g")
    .attr("class", "hook-token");

  tokenLayer.each(function(token, index) {
    const tokenGroup = d3.select(this);
    const stagger = index * 0.018;
    const outlineReveal = clamp((outlineP - index * 0.09) / 0.74, 0, 1);
    const liftReveal = easeInOut((local - 0.42 - stagger) / 0.18);
    const idReveal = easeInOut((local - 0.58 - stagger) / 0.16);
    const matrixReveal = easeInOut((local - 0.72 - stagger) / 0.22);
    const source = sourceCards[index];
    const tokenTarget = tokenTargets[index];
    const idTarget = idTargets[index];
    const matrixTarget = matrixTargets[index];

    const lifted = tokenCardGeometry(source, tokenTarget, liftReveal);
    const numbered = tokenCardGeometry(lifted, idTarget, idReveal);
    const finalCard = tokenCardGeometry(numbered, matrixTarget, matrixReveal);
    const cardLiftOpacity = clamp(liftReveal * 1.45, 0, 1);
    const sourceBorderOpacity = outlineReveal * (1 - liftReveal * 0.25);
    const movingCardOpacity = cardLiftOpacity * (0.82 + pulse * 0.12);
    const cardOpacity = Math.max(sourceBorderOpacity, movingCardOpacity);
    const visibleStart = token.start + (token.raw.startsWith(" ") ? 1 : 0);
    const visibleCount = clamp(typedChars - visibleStart, 0, token.piece.length);
    const visiblePiece = liftReveal > 0.05 ? token.piece : token.piece.slice(0, visibleCount);
    const pieceTypedOpacity = clamp(visibleCount / Math.max(1, token.piece.length), 0, 1);
    drawHookCard(tokenGroup, finalCard.x, finalCard.y, finalCard.w, finalCard.h, token.color, cardOpacity, {
      fill: d3.interpolateRgb("#ffffff", token.color)(matrixReveal),
      fillBand: matrixReveal < 0.82,
      rx: lerp(13, 5, matrixReveal),
      strokeWidth: lerp(4, 2.4, matrixReveal),
      filter: matrixReveal > 0.68 ? null : "url(#soft-glow)"
    });

    const pieceSize = lerp(lerp(textSize, tokenFontSize, liftReveal), 20, matrixReveal);
    drawHookText(tokenGroup, visiblePiece, finalCard.x + lerp(sourcePadX, 18, liftReveal), finalCard.y + finalCard.h / 2 + lerp(0, -12, idReveal) + 1, {
      anchor: "start",
      size: pieceSize,
      weight: 820,
      fill: palette.brandNeutral,
      opacity: promptOpacity * pieceTypedOpacity * clamp(1 - idReveal * 1.6, 0, 1) * clamp(1 - matrixReveal * 1.4, 0, 1)
    });
    drawHookText(tokenGroup, token.id, finalCard.x + finalCard.w / 2, finalCard.y + finalCard.h / 2 + lerp(13, 0, idReveal) + 1, {
      size: lerp(idFontSize, 22, matrixReveal),
      weight: 850,
      fill: d3.interpolateRgb(token.color, "#ffffff")(matrixReveal),
      opacity: cardOpacity * clamp((idReveal - 0.16) / 0.84, 0, 1) * clamp(1 - matrixReveal * 1.35, 0, 1)
    });
  });
}

function drawDefinitionProcessColumn(g, elapsed, opacity) {
  if (opacity <= 0.01) return;
  const column = { x: 0, y: 0, w: 620, rowH: 180, labelW: 130 };
  const rows = [
    { label: "Text", fill: "#ffffff", color: palette.blue },
    { label: "Tokens", fill: "#e7e7e7", color: palette.green },
    { label: "IDs", fill: "#cfcfcf", color: palette.orange },
    { label: "Context", fill: "#b5b5b5", color: palette.purple }
  ];
  const contentX = column.x + column.labelW + 32;
  const contentW = column.w - column.labelW - 58;

  rows.forEach((row, rowIndex) => {
    const rowY = column.y + rowIndex * column.rowH;
    const reveal = opacity * easeOut((elapsed - 0.45 - rowIndex * 0.12) / 0.78);
    if (reveal <= 0.01) return;
    const group = g.append("g").attr("opacity", reveal);
    group.append("rect")
      .attr("x", column.x)
      .attr("y", rowY)
      .attr("width", column.w)
      .attr("height", column.rowH)
      .attr("rx", 0)
      .attr("fill", row.fill)
      .attr("stroke", "none");
    drawHookText(group, row.label, column.x + 36, rowY + 42, {
      anchor: "start",
      size: 24,
      weight: 850,
      fill: palette.gray700,
      opacity: 0.96
    });
  });

  const textY = column.y + column.rowH / 2 + 8;
  drawHookText(g, hookPrompt, contentX + contentW / 2, textY, {
    size: 38,
    weight: 850,
    fill: palette.brandNeutral,
    opacity
  });

  hookTokens.forEach((token, index) => {
    const widths = [56, 82, 82, 72];
    const gap = 12;
    const tokenW = widths[index];
    const total = widths.reduce((sum, width) => sum + width, 0) + gap * (widths.length - 1);
    const promptX = contentX + (contentW - total) / 2 + widths.slice(0, index).reduce((sum, width) => sum + width + gap, 0);
    const promptY = column.y + column.rowH + 68;
    const tokenGroup = g.append("g").attr("opacity", opacity);
    tokenGroup.append("rect")
      .attr("x", promptX)
      .attr("y", promptY)
      .attr("width", tokenW)
      .attr("height", 40)
      .attr("rx", 8)
      .attr("fill", token.color)
      .attr("stroke", "#ffffff")
      .attr("stroke-width", 2.4);
    drawHookText(tokenGroup, token.piece, promptX + tokenW / 2, promptY + 21, {
      size: 18,
      weight: 850,
      fill: "#ffffff",
      opacity
    });
  });

  hookTokens.forEach((token, index) => {
    const boxW = 72;
    const gap = 12;
    const total = hookTokens.length * boxW + (hookTokens.length - 1) * gap;
    const x = contentX + (contentW - total) / 2 + index * (boxW + gap);
    const yy = column.y + column.rowH * 2 + 68;
    const group = g.append("g").attr("opacity", opacity);
    group.append("rect")
      .attr("x", x)
      .attr("y", yy)
      .attr("width", boxW)
      .attr("height", 42)
      .attr("rx", 8)
      .attr("fill", "#ffffff")
      .attr("stroke", token.color)
      .attr("stroke-width", 2.6);
    drawHookText(group, token.id, x + boxW / 2, yy + 22, {
      size: 18,
      weight: 860,
      fill: token.color,
      opacity
    });
  });
}

function drawProbabilityDecision(g, matrix, layout, phaseSeconds, pulse, options = {}) {
  const llmP = easeOut((phaseSeconds - 0.35) / 1.1);
  const chartP = easeOut((phaseSeconds - 1.25) / 1.15);
  if (llmP <= 0.01) return null;

  const sceneLayout = llmDefinitionDecisionLayout();
  const llm = sceneLayout.llm;
  const chart = sceneLayout.roulette;
  const candidates = [
    { label: "tests", value: 0.72, color: palette.purple },
    { label: ".", value: 0.54, color: palette.red },
    { label: "for", value: 0.38, color: palette.blue },
    { label: "with", value: 0.26, color: palette.green },
    { label: "now", value: 0.17, color: palette.orange }
  ];
  const selectedIndex = 0;

  const activationAmount = chartP * easeOut((phaseSeconds - 0.6) / 0.65) * (1 - 0.42 * easeInOut((phaseSeconds - 7.6) / 3.4));
  drawLlmModelBox(g, llm, { palette, drawHookText, clamp, easeOut }, {
    opacity: llmP,
    textOpacity: options.llmTextOpacity ?? 1,
    activation: activationAmount,
    activationClock: phaseSeconds - 0.58
  });

  if (chartP <= 0.01) return { llm, chart, candidates, selectedIndex };
  const chartFade = 1 - 0.62 * easeInOut((phaseSeconds - 7.2) / 4.8);
  const chartGroup = g.append("g").attr("opacity", chartP * chartFade);
  const decisionOpacity = chartP * chartFade * easeOut((phaseSeconds - 2.35) / 0.7);
  const wheel = {
    cx: chart.x + 86,
    cy: chart.y + chart.h / 2,
    r: 74
  };
  const rouletteTokens = candidates.map((candidate, index) => ({
    text: candidate.label,
    p: candidate.value,
    color: candidate.color,
    selected: index === selectedIndex
  }));
  const arcs = d3.pie().sort(null).value((token) => token.p)(rouletteTokens);
  const selectedArc = arcs[selectedIndex];
  const selectedCenterDeg = ((selectedArc.startAngle + selectedArc.endAngle) / 2) * 180 / Math.PI;
  const finalRotation = 1440 - selectedCenterDeg;
  const spinStart = 1.55;
  const spinDuration = 3.1;
  const spinP = clamp((phaseSeconds - spinStart) / spinDuration, 0, 1);
  let wheelRotation = 0;
  if (spinP < 0.42) {
    wheelRotation = lerp(0, 760, easeOut(spinP / 0.42));
  } else if (spinP < 0.72) {
    wheelRotation = lerp(760, 1180, easeOut((spinP - 0.42) / 0.3));
  } else {
    wheelRotation = lerp(1180, finalRotation, easeOut((spinP - 0.72) / 0.28));
  }
  const wheelSettledP = easeOut((phaseSeconds - (spinStart + spinDuration)) / 0.34);
  const arc = d3.arc().innerRadius(0).outerRadius(wheel.r).cornerRadius(4).padAngle(0.012);
  const selectedArcPath = d3.arc().innerRadius(0).outerRadius(wheel.r + 5).cornerRadius(5).padAngle(0.012);

  chartGroup.append("circle")
    .attr("cx", wheel.cx)
    .attr("cy", wheel.cy)
    .attr("r", wheel.r + 10)
    .attr("fill", palette.gray100)
    .attr("stroke", palette.gray200)
    .attr("stroke-width", 2)
    .attr("opacity", 0.96);

  const rouletteWheel = chartGroup.append("g")
    .attr("class", "token-roulette-wheel")
    .attr("transform", `translate(${wheel.cx},${wheel.cy}) rotate(${wheelRotation})`);
  const wedgeGroups = rouletteWheel.selectAll("g.token-roulette-wedge")
    .data(arcs)
    .join("g")
    .attr("class", "token-roulette-wedge");
  wedgeGroups.append("path")
    .attr("d", arc)
    .attr("fill", (arcDatum) => arcDatum.data.color)
    .attr("fill-opacity", (arcDatum) => arcDatum.data.selected ? 0.94 : 0.72)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2);
  wedgeGroups.append("path")
    .filter((arcDatum) => arcDatum.data.selected)
    .attr("d", selectedArcPath)
    .attr("fill", "none")
    .attr("stroke", palette.redHover)
    .attr("stroke-width", 3.2)
    .attr("opacity", wheelSettledP * 0.96);

  d3.range(24).forEach((tick) => {
    const angle = tick * 15 * Math.PI / 180;
    const r0 = wheel.r + 6;
    const r1 = wheel.r + (tick % 3 === 0 ? 15 : 11);
    chartGroup.append("line")
      .attr("x1", wheel.cx + Math.sin(angle) * r0)
      .attr("y1", wheel.cy - Math.cos(angle) * r0)
      .attr("x2", wheel.cx + Math.sin(angle) * r1)
      .attr("y2", wheel.cy - Math.cos(angle) * r1)
      .attr("stroke", tick % 3 === 0 ? palette.gray600 : palette.gray300)
      .attr("stroke-width", tick % 3 === 0 ? 1.6 : 1)
      .attr("opacity", 0.76);
  });
  chartGroup.append("path")
    .attr("d", `M${wheel.cx},${wheel.cy - wheel.r - 18} L${wheel.cx - 13},${wheel.cy - wheel.r - 42} L${wheel.cx + 13},${wheel.cy - wheel.r - 42} Z`)
    .attr("fill", palette.brandPrimary)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 2)
    .attr("stroke-linejoin", "round")
    .attr("opacity", decisionOpacity);
  chartGroup.append("circle")
    .attr("cx", wheel.cx)
    .attr("cy", wheel.cy - wheel.r - 18)
    .attr("r", 4.6)
    .attr("fill", palette.redHover)
    .attr("opacity", decisionOpacity);

  const totalValue = d3.sum(rouletteTokens, (token) => token.p);
  const legendX = chart.x + 186;
  const legendY = chart.y + 50;
  rouletteTokens.forEach((token, index) => {
    const rowY = legendY + index * 34;
    const rowGroup = chartGroup.append("g");
    rowGroup.append("rect")
      .attr("x", legendX)
      .attr("y", rowY)
      .attr("width", 16)
      .attr("height", 16)
      .attr("rx", 4)
      .attr("fill", token.color)
      .attr("fill-opacity", token.selected ? 0.94 : 0.72);
    drawHookText(rowGroup, token.text, legendX + 26, rowY + 12, {
      anchor: "start",
      size: 15,
      weight: token.selected ? 850 : 720,
      fill: token.selected ? palette.brandNeutral : palette.gray700,
      opacity: 1
    });
    drawHookText(rowGroup, `${Math.round((token.p / totalValue) * 100)}%`, legendX + 116, rowY + 12, {
      anchor: "end",
      size: 14,
      weight: token.selected ? 820 : 680,
      fill: token.selected ? token.color : palette.gray600,
      opacity: 1
    });
  });

  arrow(g, llm.x + llm.w + 10, llm.y + llm.h / 2, wheel.cx - wheel.r - 24, wheel.cy, palette.brandPrimary, decisionOpacity * 0.42, 3);

  const travelP = easeInOut((phaseSeconds - 5.2) / 5.0);
  if (travelP > 0.01) {
    const slot = layout.slot(4);
    const start = { x: llm.x - 76, y: llm.y + llm.h / 2 - 24, w: 98, h: 48 };
    const end = { x: slot.x, y: slot.y, w: slot.w, h: slot.h };
    const card = tokenCardGeometry(start, end, travelP);
    const settleP = easeInOut((travelP - 0.88) / 0.12);
    const movingOpacity = 0.96 * (1 - settleP);
    const pathOpacity = clamp((travelP - 0.03) / 0.3, 0, 1) * clamp((1 - travelP) / 0.45, 0, 1);
    const lineStart = { x: start.x + start.w / 2, y: start.y + start.h / 2 };
    const lineEnd = { x: slot.x + slot.w / 2, y: slot.y + slot.h / 2 };
    const lineHead = {
      x: card.x + card.w / 2,
      y: card.y + card.h / 2
    };
    g.append("line")
      .attr("x1", lineStart.x)
      .attr("y1", lineStart.y)
      .attr("x2", lineEnd.x)
      .attr("y2", lineEnd.y)
      .attr("stroke", candidates[selectedIndex].color)
      .attr("stroke-width", 2)
      .attr("stroke-linecap", "round")
      .attr("opacity", pathOpacity * 0.08);
    g.append("line")
      .attr("x1", lineHead.x)
      .attr("y1", lineHead.y)
      .attr("x2", lineEnd.x)
      .attr("y2", lineEnd.y)
      .attr("stroke", candidates[selectedIndex].color)
      .attr("stroke-width", 3.5)
      .attr("stroke-linecap", "round")
      .attr("opacity", pathOpacity * 0.38);
    const targetP = clamp((travelP - 0.68) / 0.2, 0, 1) * (1 - settleP);
    if (targetP > 0.01) {
      g.append("rect")
        .attr("x", slot.x - 4)
        .attr("y", slot.y - 4)
        .attr("width", slot.w + 8)
        .attr("height", slot.h + 8)
        .attr("rx", 5)
        .attr("fill", "none")
        .attr("stroke", candidates[selectedIndex].color)
        .attr("stroke-width", 2.4)
        .attr("opacity", targetP * 0.72);
    }
    if (movingOpacity > 0.02) {
      drawHookCard(g, card.x, card.y, card.w, card.h, candidates[selectedIndex].color, movingOpacity, {
        fill: d3.interpolateRgb("#ffffff", candidates[selectedIndex].color)(travelP),
        fillBand: travelP < 0.78,
        rx: lerp(12, 4, travelP),
        strokeWidth: lerp(3.4, 2, travelP),
        filter: travelP < 0.95 ? "url(#soft-glow)" : null
      });
      drawHookText(g, candidates[selectedIndex].label, card.x + card.w / 2, card.y + card.h / 2 + 1, {
        size: lerp(24, 7, travelP),
        weight: 870,
        fill: d3.interpolateRgb(candidates[selectedIndex].color, "#ffffff")(travelP),
        opacity: movingOpacity * clamp(1 - travelP * 1.25, 0, 1)
      });
    }
  }

  return { llm, chart, candidates, selectedIndex };
}

function drawLlmDefinitionVisualOnly(g, seconds, sceneProgress, pulse, options = {}) {
  const elapsed = sceneProgress * 24;
  const originalMatrix = { x: 496, y: 398, w: 288, h: 288 };
  const processMatrix = { x: 302, y: 552, w: 152, h: 152 };
  const leftMatrix = llmDefinitionDecisionLayout().matrix;
  const moveToProcessP = easeInOut(elapsed / 1.65);
  const moveToLeftP = easeInOut((elapsed - 10) / 1.8);
  const stagedMatrix = {
    x: lerp(originalMatrix.x, processMatrix.x, moveToProcessP),
    y: lerp(originalMatrix.y, processMatrix.y, moveToProcessP),
    w: lerp(originalMatrix.w, processMatrix.w, moveToProcessP),
    h: lerp(originalMatrix.h, processMatrix.h, moveToProcessP)
  };
  const matrix = {
    x: lerp(stagedMatrix.x, leftMatrix.x, moveToLeftP),
    y: lerp(stagedMatrix.y, leftMatrix.y, moveToLeftP),
    w: lerp(stagedMatrix.w, leftMatrix.w, moveToLeftP),
    h: lerp(stagedMatrix.h, leftMatrix.h, moveToLeftP)
  };
  const matrixCell = lerp(lerp(24, 13, moveToProcessP), 24, moveToLeftP);
  const matrixGap = lerp(lerp(8, 4, moveToProcessP), 8, moveToLeftP);
  const phaseSeconds = elapsed - 11.8;
  const nextToken = { raw: " tests", piece: "tests", id: "12966", color: palette.purple, start: hookPrompt.length, length: 6 };
  const travelP = easeInOut((phaseSeconds - 5.2) / 5.0);
  const occupiedTokens = travelP > 0.88 ? [...hookTokens, nextToken] : hookTokens;

  const processOpacity = clamp((elapsed - 0.28) / 1.1, 0, 1) * clamp((10 - elapsed) / 1.0, 0, 1);
  drawDefinitionProcessColumn(g, elapsed, processOpacity);

  const layout = drawHookContextMatrix(g, matrix, occupiedTokens, {
    opacity: 1,
    backgroundOpacity: 0.94,
    occupiedOpacity: 0.96,
    cellOpacity: 0.74,
    cell: matrixCell,
    gap: matrixGap
  });

  if (phaseSeconds > -0.05) {
    drawProbabilityDecision(g, matrix, layout, phaseSeconds, pulse, options);
  }
}

function drawLlmVisualOnly(g, seconds, sceneProgress, stageIndex, pulse, moving) {
  const stage = Math.min(stageIndex, 4);
  if (stage === 0) {
    drawLlmHookVisualOnly(g, seconds, sceneProgress, pulse);
    return;
  }
  if (stage === 1) {
    drawLlmDefinitionVisualOnly(g, seconds, sceneProgress, pulse);
    return;
  }
  if (stage === 2) {
    const previousFrameSeconds = 36 - 1 / 30;
    const previousFrameProgress = (previousFrameSeconds - 12) / 24;
    const previousFramePulse = 0.84 + Math.sin(previousFrameSeconds * 0.16) * 0.16;
    const mechanismSeconds = sceneProgress * 30;
    const introP = easeOut((mechanismSeconds - 0.25) / 1.55);
    const machineTextMorph = easeInOut((mechanismSeconds - 0.45) / 1.25);
    if (introP < 0.999) {
      const previousGroup = g.append("g").attr("opacity", 1 - introP);
      drawLlmDefinitionVisualOnly(previousGroup, previousFrameSeconds, previousFrameProgress, previousFramePulse, {
        llmTextOpacity: 1 - machineTextMorph
      });
    }
    drawLlmMechanismVisualOnly(g, {
      palette,
      hookTokens,
      sceneProgress,
      pulse,
        machineTextMorph,
        trailOpacity: easeOut((mechanismSeconds - 1.1) / 0.7),
        clamp,
        easeInOut,
        easeOut,
        lerp,
      llmDefinitionDecisionLayout,
      drawHookContextMatrix,
      drawHookText,
      drawHookCard,
      tokenCardGeometry
    });
    return;
  }
  if (stage === 3) {
    const previousFrameSeconds = 66 - 1 / 30;
    const previousFrameProgress = (previousFrameSeconds - 36) / 30;
    const previousFramePulse = 0.84 + Math.sin(previousFrameSeconds * 0.16) * 0.16;
    const implicationSeconds = sceneProgress * 34;
    const introP = easeOut((implicationSeconds - 0.3) / 1.55);
    if (introP < 0.999) {
      const previousGroup = g.append("g").attr("opacity", 1 - introP);
      drawLlmMechanismVisualOnly(previousGroup, {
        palette,
        hookTokens,
        sceneProgress: previousFrameProgress,
        pulse: previousFramePulse,
        clamp,
        easeInOut,
        easeOut,
        lerp,
        llmDefinitionDecisionLayout,
        drawHookContextMatrix,
        drawHookText,
        drawHookCard,
        tokenCardGeometry
      });
    }
    if (introP <= 0.001) return;
    drawLlmImplicationVisualOnly(g, {
      palette,
      hookTokens,
      sceneProgress,
      pulse,
      clamp,
      easeInOut,
      easeOut,
      lerp,
      drawHookText,
      drawHookCard,
      tokenCardGeometry
    });
    return;
  }
  if (stage === 4) {
    const previousFrameSeconds = 100 - 1 / 30;
    const previousFrameProgress = (previousFrameSeconds - 66) / 34;
    const previousFramePulse = 0.84 + Math.sin(previousFrameSeconds * 0.16) * 0.16;
    const handoffSeconds = sceneProgress * 20;
    const introP = easeOut((handoffSeconds - 0.3) / 1.55);
    if (introP < 0.999) {
      const previousGroup = g.append("g").attr("opacity", 1 - introP);
      drawLlmImplicationVisualOnly(previousGroup, {
        palette,
        hookTokens,
        sceneProgress: previousFrameProgress,
        pulse: previousFramePulse,
        clamp,
        easeInOut,
        easeOut,
        lerp,
        drawHookText,
        drawHookCard,
        tokenCardGeometry
      });
    }
    if (introP <= 0.001) return;
    const handoffGroup = g.append("g").attr("opacity", introP);
    drawLlmHandoffVisualOnly(handoffGroup, {
      palette,
      hookTokens,
      sceneProgress,
      pulse,
      clamp,
      easeInOut,
      easeOut,
      lerp,
      drawHookText,
      drawHookCard,
      tokenCardGeometry
    });
    return;
  }

  const colors = [palette.blue, palette.green, palette.orange, palette.red, palette.purple, palette.yellow];
  const fades = {
    split: 0.56 + (stage >= 0 ? 0.34 : 0),
    context: 0.44 + (stage >= 1 ? 0.44 : 0),
    rank: 0.36 + (stage >= 2 ? 0.5 : 0),
    loop: 0.32 + (stage >= 2 ? 0.5 : 0),
    load: clamp((stage - 3) + sceneProgress, 0, 1)
  };

  const doc = { x: 74, y: 118, w: 230, h: 162 };
  const split = { x: 360, y: 154, w: 104, h: 104 };
  const context = { x: 510, y: 82, w: 250, h: 450 };
  const model = { x: 840, y: 98, w: 250, h: 300 };
  const rank = { x: 1038, y: 145, w: 168, h: 190 };
  const output = { x: 850, y: 520, w: 318, h: 78 };
  const load = { x: 112, y: 494, w: 240, h: 96 };

  g.append("rect")
    .attr("x", 38)
    .attr("y", 54)
    .attr("width", 1204)
    .attr("height", 590)
    .attr("rx", 22)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray100)
    .attr("stroke-width", 2)
    .attr("opacity", 0.84);

  g.append("rect")
    .attr("x", doc.x)
    .attr("y", doc.y)
    .attr("width", doc.w)
    .attr("height", doc.h)
    .attr("rx", 14)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray300)
    .attr("stroke-width", 3)
    .attr("opacity", 0.94);
  d3.range(7).forEach((index) => {
    const lineWidth = 92 + (index % 3) * 36;
    g.append("rect")
      .attr("x", doc.x + 28)
      .attr("y", doc.y + 30 + index * 16)
      .attr("width", lineWidth)
      .attr("height", 7)
      .attr("rx", 4)
      .attr("fill", index === 1 ? palette.redHighlight : palette.gray100)
      .attr("stroke", index === 1 ? palette.red : "none")
      .attr("opacity", 0.82);
  });

  d3.range(10).forEach((index) => {
    const row = Math.floor(index / 5);
    const col = index % 5;
    const x0 = doc.x + 26 + col * 38;
    const y0 = doc.y + 118 + row * 28;
    const p = clamp((seconds - 3 - index * 0.7) / 15, 0, 1);
    const sx = split.x + 14 + (index % 3) * 26;
    const sy = split.y + 18 + Math.floor(index / 3) * 20;
    const x = x0 + (sx - x0) * easeInOut(p);
    const y = y0 + (sy - y0) * easeInOut(p);
    drawTokenRect(g, x, y, 26 + (index % 2) * 8, 15, colors[index % colors.length], fades.split * (0.58 + p * 0.42));
  });

  g.append("rect")
    .attr("x", split.x)
    .attr("y", split.y)
    .attr("width", split.w)
    .attr("height", split.h)
    .attr("rx", 18)
    .attr("fill", palette.blueHighlight)
    .attr("stroke", palette.blue)
    .attr("stroke-width", 4)
    .attr("opacity", fades.split);
  d3.range(4).forEach((index) => {
    g.append("line")
      .attr("x1", split.x + 24 + index * 18)
      .attr("y1", split.y + 18)
      .attr("x2", split.x + 18 + index * 18)
      .attr("y2", split.y + split.h - 18)
      .attr("stroke", palette.blueHover)
      .attr("stroke-width", 4)
      .attr("stroke-linecap", "round")
      .attr("opacity", 0.55 + pulse * 0.25);
  });

  arrow(g, doc.x + doc.w + 8, doc.y + 84, split.x - 18, split.y + 52, palette.blue, 0.44 + pulse * 0.22, 4);
  arrow(g, split.x + split.w + 8, split.y + 52, context.x - 18, context.y + 184, palette.green, 0.58, 4);
  movingDotOnLine(g, split.x + split.w + 8, split.y + 52, context.x - 18, context.y + 184, moving, palette.green, 8);

  g.append("rect")
    .attr("x", context.x)
    .attr("y", context.y)
    .attr("width", context.w)
    .attr("height", context.h)
    .attr("rx", 20)
    .attr("fill", palette.greenHighlight)
    .attr("stroke", palette.green)
    .attr("stroke-width", 5)
    .attr("opacity", fades.context);

  const visibleRows = clamp(3 + stage * 1.4 + Math.floor(sceneProgress * 3), 3, 9);
  d3.range(9).forEach((row) => {
    const rowOpacity = row < visibleRows ? 0.95 : 0.22;
    d3.range(5).forEach((col) => {
      const x = context.x + 26 + col * 42;
      const y = context.y + 42 + row * 40;
      drawTokenRect(g, x, y, 28, 22, colors[(row + col) % colors.length], rowOpacity, row < visibleRows ? "#ffffff" : palette.gray200);
    });
  });

  d3.range(14).forEach((index) => {
    const a = index % 5;
    const b = 2 + (index * 2) % 7;
    const x1 = context.x + 40 + a * 42;
    const y1 = context.y + 52 + (index % 4) * 40;
    const x2 = context.x + 40 + ((a + 2) % 5) * 42;
    const y2 = context.y + 52 + b * 40;
    g.append("path")
      .attr("d", `M${x1},${y1} C${context.x - 34},${y1 + 20} ${context.x - 34},${y2 - 20} ${x2},${y2}`)
      .attr("fill", "none")
      .attr("stroke", colors[index % colors.length])
      .attr("stroke-width", 2.6)
      .attr("stroke-opacity", stage >= 1 ? 0.18 + progressPulse(seconds, index * 0.05, 3.8) * 0.16 : 0.05);
  });

  arrow(g, context.x + context.w + 10, context.y + 210, model.x - 20, model.y + 168, palette.orange, 0.62, 4);
  movingDotOnLine(g, context.x + context.w + 10, context.y + 210, model.x - 20, model.y + 168, progressPulse(seconds, 0.2, 4.8), palette.orange, 8);

  d3.range(5).forEach((layer) => {
    const x = model.x + layer * 20;
    const y = model.y + layer * 18;
    g.append("rect")
      .attr("x", x)
      .attr("y", y)
      .attr("width", model.w - 64)
      .attr("height", model.h - 72)
      .attr("rx", 18)
      .attr("fill", layer % 2 === 0 ? palette.blueHighlight : palette.purpleHighlight)
      .attr("stroke", layer % 2 === 0 ? palette.blue : palette.purple)
      .attr("stroke-width", 3)
      .attr("opacity", fades.rank * (0.32 + layer * 0.11));
    d3.range(4).forEach((row) => {
      d3.range(3).forEach((col) => {
        g.append("circle")
          .attr("cx", x + 48 + col * 42)
          .attr("cy", y + 48 + row * 40)
          .attr("r", 7 + Math.sin(seconds * 0.12 + row + col + layer) * 1.6)
          .attr("fill", colors[(row + col + layer) % colors.length])
          .attr("opacity", fades.rank * 0.72);
      });
    });
  });

  const barValues = [
    0.66 + sceneProgress * 0.22 + Math.sin(seconds * 0.09) * 0.04,
    0.48 + Math.cos(seconds * 0.11) * 0.06,
    0.34 + Math.sin(seconds * 0.08 + 1) * 0.05,
    0.2 + Math.cos(seconds * 0.1 + 2) * 0.04
  ];
  d3.range(4).forEach((index) => {
    const y = rank.y + 16 + index * 42;
    const color = index === 0 ? palette.green : colors[(index + 2) % colors.length];
    g.append("rect")
      .attr("x", rank.x)
      .attr("y", y)
      .attr("width", rank.w)
      .attr("height", 24)
      .attr("rx", 12)
      .attr("fill", palette.gray100)
      .attr("opacity", fades.rank * 0.9);
    g.append("rect")
      .attr("x", rank.x)
      .attr("y", y)
      .attr("width", rank.w * clamp(barValues[index], 0.08, 0.96))
      .attr("height", 24)
      .attr("rx", 12)
      .attr("fill", color)
      .attr("opacity", fades.rank * (index === 0 ? 0.96 : 0.58));
  });

  const chosenPulse = 0.72 + pulse * 0.28;
  drawTokenRect(g, rank.x + rank.w * 0.66, rank.y + 14, 46, 24, palette.green, fades.rank * chosenPulse);
  arrow(g, rank.x + rank.w - 4, rank.y + 96, output.x + 52, output.y - 28, palette.red, fades.loop * 0.8, 4);
  movingDotOnLine(g, rank.x + rank.w - 4, rank.y + 96, output.x + 52, output.y - 28, progressPulse(seconds, 0.46, 4.8), palette.red, 8);

  g.append("rect")
    .attr("x", output.x)
    .attr("y", output.y)
    .attr("width", output.w)
    .attr("height", output.h)
    .attr("rx", 20)
    .attr("fill", palette.redHighlight)
    .attr("stroke", palette.red)
    .attr("stroke-width", 4)
    .attr("opacity", fades.loop);
  d3.range(6).forEach((index) => {
    const reveal = clamp((seconds - 36 - index * 7) / 18, 0, 1);
    drawTokenRect(g, output.x + 24 + index * 47, output.y + 26 + Math.sin(seconds * 0.13 + index) * 2, 34, 26, colors[(index + 3) % colors.length], fades.loop * (0.24 + reveal * 0.76));
  });

  const loopPath = `M${output.x + 38},${output.y + 82} C${output.x - 60},${660} ${context.x + 80},${650} ${context.x + 90},${context.y + context.h + 8}`;
  g.append("path")
    .attr("d", loopPath)
    .attr("fill", "none")
    .attr("stroke", palette.red)
    .attr("stroke-width", 4)
    .attr("stroke-linecap", "round")
    .attr("stroke-opacity", fades.loop * 0.58);
  movingDotOnLine(g, output.x + 38, output.y + 82, context.x + 90, context.y + context.h + 8, progressPulse(seconds, 0.74, 5.6), palette.red, 7);

  g.append("rect")
    .attr("x", load.x)
    .attr("y", load.y)
    .attr("width", load.w)
    .attr("height", load.h)
    .attr("rx", 18)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.orange)
    .attr("stroke-width", 4)
    .attr("opacity", fades.load);
  d3.range(9).forEach((index) => {
    const x = load.x + 22 + index * 22;
    const height = 18 + ((index * 7) % 42) * (0.55 + pulse * 0.35);
    g.append("rect")
      .attr("x", x)
      .attr("y", load.y + load.h - 18 - height)
      .attr("width", 14)
      .attr("height", height)
      .attr("rx", 5)
      .attr("fill", index % 3 === 0 ? palette.red : index % 3 === 1 ? palette.blue : palette.green)
      .attr("opacity", fades.load * 0.82);
  });
  d3.range(5).forEach((index) => {
    movingDotOnLine(g, output.x + 24 + index * 42, output.y + 48, load.x + 34 + index * 34, load.y + 18, progressPulse(seconds, index * 0.13, 3.8), colors[index % colors.length], 5);
  });

  const focus = [
    { cx: split.x + split.w / 2, cy: split.y + split.h / 2, r: 74, visible: stage === 0, color: palette.blue },
    { cx: context.x + context.w / 2, cy: context.y + context.h / 2, r: 150, visible: stage === 1, color: palette.green },
    { cx: rank.x + 74, cy: rank.y + 90, r: 116, visible: stage === 2, color: palette.orange },
    { cx: context.x + context.w / 2, cy: context.y + 260, r: 164, visible: stage === 3, color: palette.orange },
    { cx: load.x + load.w / 2, cy: load.y + load.h / 2, r: 88, visible: stage === 4, color: palette.purple }
  ];
  focus.forEach((item) => {
    if (!item.visible) return;
    g.append("circle")
      .attr("cx", item.cx)
      .attr("cy", item.cy)
      .attr("r", item.r + pulse * 10)
      .attr("fill", "none")
      .attr("stroke", item.color)
      .attr("stroke-width", 4)
      .attr("stroke-opacity", 0.28);
  });
}

function drawCommonLegend(g, items, x = 510, y = 52) {
  items.forEach((item, index) => {
    const rowY = y + index * 26;
    g.append("circle").attr("cx", x).attr("cy", rowY - 4).attr("r", 5).attr("fill", item.color);
    g.append("text").attr("x", x + 12).attr("y", rowY).attr("class", "svg-caption").text(item.label);
  });
}

function drawLlm(g, seconds, sceneProgress) {
  const { beat } = sceneForTime(currentConcept, seconds);
  const stageIndex = Math.max(0, beats.findIndex((item) => item.id === beat.id));
  const local = clamp(sceneProgress, 0, 1);
  const pulse = 0.84 + Math.sin(seconds * 0.16) * 0.16;
  const visualOnly = currentConcept.visualOnly === true;
  const moving = progressPulse(seconds, 0, 4.8);

  if (visualOnly) {
    drawLlmVisualOnly(g, seconds, local, stageIndex, pulse, moving);
    return;
  }

  const tokenWords = ["AI", "tools", "write", "code"];
  const contextTokens = ["sys", "ask", "AI", "tools", "write", "code", "tests"];
  const outputTokens = ["code", ".", "tests"];

  const splitBox = { x: 80, y: 120, w: 112, h: 78 };
  const contextBox = { x: 292, y: 70, w: 158, h: 248 };
  const rankBox = { x: 548, y: 104, w: 142, h: 150 };
  const outputBox = { x: 534, y: 320, w: 166, h: 48 };

  const stageDots = [
    { label: "split", x: 136, y: 74, color: palette.blue },
    { label: "stack", x: 372, y: 44, color: palette.green },
    { label: "rank", x: 620, y: 76, color: palette.orange },
    { label: "append", x: 618, y: 296, color: palette.red }
  ];
  stageDots.forEach((dot, index) => {
    const active = index <= Math.min(stageIndex, 3);
    g.append("circle")
      .attr("cx", dot.x)
      .attr("cy", dot.y)
      .attr("r", active ? 13 : 9)
      .attr("fill", active ? dot.color : palette.gray100)
      .attr("stroke", active ? "#ffffff" : palette.gray300)
      .attr("stroke-width", active ? 3 : 1.5)
      .attr("opacity", active ? 0.92 : 0.55);
    g.append("text")
      .attr("x", dot.x)
      .attr("y", dot.y + 31)
      .attr("text-anchor", "middle")
      .attr("class", "svg-caption")
      .text(dot.label);
  });

  g.append("rect")
    .attr("x", splitBox.x)
    .attr("y", splitBox.y)
    .attr("width", splitBox.w)
    .attr("height", splitBox.h)
    .attr("rx", 10)
    .attr("fill", palette.blueHighlight)
    .attr("stroke", palette.blue)
    .attr("stroke-width", 2.5);
  g.append("text")
    .attr("x", splitBox.x + splitBox.w / 2)
    .attr("y", splitBox.y + 46)
    .attr("text-anchor", "middle")
    .attr("class", "svg-label")
    .text("split");

  chip(g, 54, 276, "AI tools write code", {
    width: 164,
    fill: "#ffffff",
    stroke: palette.gray400,
    opacity: 0.86
  });

  tokenWords.forEach((token, index) => {
    const reveal = clamp((seconds - 3 - index * 1.7) / 8, 0, 1);
    const intoSplit = clamp((seconds - 7 - index * 1.2) / 10, 0, 1);
    const x0 = 62 + index * 52;
    const y0 = 356;
    const x1 = splitBox.x + 14 + (index % 2) * 48;
    const y1 = splitBox.y + 14 + Math.floor(index / 2) * 35;
    const x = x0 + (x1 - x0) * easeInOut(intoSplit);
    const y = y0 + (y1 - y0) * easeInOut(intoSplit) + Math.sin(seconds * 0.2 + index) * 2;
    chip(g, x, y, token, {
      width: token.length < 3 ? 44 : 58,
      height: 28,
      fill: index <= stageIndex + 1 ? palette.greenHighlight : palette.gray100,
      stroke: index <= stageIndex + 1 ? palette.green : palette.gray300,
      opacity: 0.25 + reveal * 0.75
    });
  });

  arrow(g, splitBox.x + splitBox.w, splitBox.y + 39, contextBox.x - 18, 184, palette.green, 0.56 + pulse * 0.2, 3);
  movingDotOnLine(g, splitBox.x + splitBox.w + 4, splitBox.y + 39, contextBox.x - 18, 184, moving, palette.green, 6);

  g.append("rect")
    .attr("x", contextBox.x)
    .attr("y", contextBox.y)
    .attr("width", contextBox.w)
    .attr("height", contextBox.h)
    .attr("rx", 10)
    .attr("fill", palette.greenHighlight)
    .attr("stroke", palette.green)
    .attr("stroke-width", 2.5);
  g.append("text")
    .attr("x", contextBox.x + contextBox.w / 2)
    .attr("y", contextBox.y + 24)
    .attr("text-anchor", "middle")
    .attr("class", "svg-label")
    .text("context");

  const visibleContext = clamp(3 + stageIndex + Math.floor(local * 2), 3, contextTokens.length);
  contextTokens.forEach((token, index) => {
    const rowY = contextBox.y + 46 + index * 27;
    const active = index < visibleContext;
    g.append("rect")
      .attr("x", contextBox.x + 20)
      .attr("y", rowY)
      .attr("width", 118)
      .attr("height", 20)
      .attr("rx", 5)
      .attr("fill", active ? "#ffffff" : palette.gray100)
      .attr("stroke", active ? palette.green : palette.gray300)
      .attr("opacity", active ? 0.92 : 0.42);
    g.append("text")
      .attr("x", contextBox.x + 79)
      .attr("y", rowY + 14)
      .attr("text-anchor", "middle")
      .attr("class", "svg-small")
      .attr("fill", active ? palette.brandNeutral : palette.gray500)
      .text(token);
  });

  const attentionLinks = [
    { from: 0, to: 4, color: palette.blue },
    { from: 1, to: 5, color: palette.orange },
    { from: 3, to: 6, color: palette.purple }
  ];
  attentionLinks.forEach((link, index) => {
    const y1 = contextBox.y + 56 + link.from * 27;
    const y2 = contextBox.y + 56 + link.to * 27;
    g.append("path")
      .attr("d", `M${contextBox.x + 24},${y1} C${contextBox.x - 22},${y1 + 12} ${contextBox.x - 22},${y2 - 12} ${contextBox.x + 24},${y2}`)
      .attr("fill", "none")
      .attr("stroke", link.color)
      .attr("stroke-width", 2.5)
      .attr("stroke-opacity", 0.24 + 0.12 * Math.sin(seconds * 0.11 + index));
  });

  arrow(g, contextBox.x + contextBox.w, 184, rankBox.x - 24, 184, palette.orange, 0.62, 3);
  movingDotOnLine(g, contextBox.x + contextBox.w + 4, 184, rankBox.x - 24, 184, progressPulse(seconds, 0.32, 4.8), palette.orange, 6);

  g.append("rect")
    .attr("x", rankBox.x)
    .attr("y", rankBox.y)
    .attr("width", rankBox.w)
    .attr("height", rankBox.h)
    .attr("rx", 10)
    .attr("fill", palette.orangeHighlight)
    .attr("stroke", palette.orange)
    .attr("stroke-width", 2.5);
  g.append("text")
    .attr("x", rankBox.x + rankBox.w / 2)
    .attr("y", rankBox.y + 26)
    .attr("text-anchor", "middle")
    .attr("class", "svg-label")
    .text("rank");

  const candidates = [
    { label: "code", base: 0.74, color: palette.green },
    { label: "tests", base: 0.53, color: palette.blue },
    { label: "docs", base: 0.39, color: palette.purple },
    { label: "fix", base: 0.28, color: palette.gray500 }
  ];
  candidates.forEach((candidate, index) => {
    const y = rankBox.y + 50 + index * 25;
    const value = clamp(candidate.base + Math.sin(seconds * 0.1 + index) * 0.08 + (index === 0 ? local * 0.08 : 0), 0.08, 0.96);
    const winner = index === 0;
    g.append("rect")
      .attr("x", rankBox.x + 16)
      .attr("y", y)
      .attr("width", 92)
      .attr("height", 13)
      .attr("rx", 6)
      .attr("fill", "#ffffff")
      .attr("opacity", 0.9);
    g.append("rect")
      .attr("x", rankBox.x + 16)
      .attr("y", y)
      .attr("width", 92 * value)
      .attr("height", 13)
      .attr("rx", 6)
      .attr("fill", winner ? palette.green : candidate.color)
      .attr("opacity", winner ? 0.92 : 0.55);
    g.append("text")
      .attr("x", rankBox.x + 118)
      .attr("y", y + 11)
      .attr("class", "svg-small")
      .attr("fill", winner ? palette.greenHover : palette.brandNeutral)
      .text(candidate.label);
  });

  const chosenX = rankBox.x + 22 + Math.sin(seconds * 0.22) * 3;
  const chosenY = rankBox.y + 48;
  chip(g, chosenX, chosenY, "code", {
    width: 54,
    height: 27,
    fill: palette.greenHighlight,
    stroke: palette.green,
    opacity: 0.8 + pulse * 0.18
  });

  arrow(g, rankBox.x + rankBox.w - 16, rankBox.y + 126, outputBox.x + 24, outputBox.y - 18, palette.red, 0.62, 3);
  movingDotOnLine(g, rankBox.x + rankBox.w - 16, rankBox.y + 126, outputBox.x + 24, outputBox.y - 18, progressPulse(seconds, 0.58, 4.8), palette.red, 6);

  g.append("rect")
    .attr("x", outputBox.x)
    .attr("y", outputBox.y)
    .attr("width", outputBox.w)
    .attr("height", outputBox.h)
    .attr("rx", 10)
    .attr("fill", palette.redHighlight)
    .attr("stroke", palette.red)
    .attr("stroke-width", 2.5);
  outputTokens.forEach((token, index) => {
    const reveal = clamp((seconds - 34 - index * 10) / 18, 0, 1);
    chip(g, outputBox.x + 12 + index * 50, outputBox.y + 10, token, {
      width: token === "." ? 32 : 46,
      height: 26,
      fill: "#ffffff",
      stroke: palette.red,
      opacity: 0.35 + reveal * 0.65
    });
  });

  const loadOpacity = clamp((stageIndex - 3) + local, 0, 1);
  const loadBox = { x: 76, y: 220, w: 126, h: 22 };
  g.append("rect")
    .attr("x", loadBox.x)
    .attr("y", loadBox.y)
    .attr("width", loadBox.w)
    .attr("height", loadBox.h)
    .attr("rx", 6)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.orange)
    .attr("stroke-width", 2)
    .attr("opacity", loadOpacity * 0.95);
  g.append("rect")
    .attr("x", loadBox.x + 4)
    .attr("y", loadBox.y + 5)
    .attr("width", (loadBox.w - 8) * clamp(0.42 + loadOpacity * 0.44 + Math.sin(seconds * 0.1) * 0.04, 0.1, 0.95))
    .attr("height", 12)
    .attr("rx", 5)
    .attr("fill", palette.orange)
    .attr("opacity", loadOpacity * 0.9);
  g.append("text")
    .attr("x", loadBox.x + loadBox.w / 2)
    .attr("y", loadBox.y + 38)
    .attr("text-anchor", "middle")
    .attr("class", "svg-caption")
    .attr("opacity", loadOpacity)
    .text("load");
  d3.range(6).forEach((index) => {
    const x = loadBox.x + 8 + index * 18;
    const y = loadBox.y - 24 + Math.sin(seconds * 0.18 + index) * 3;
    g.append("rect")
      .attr("x", x)
      .attr("y", y)
      .attr("width", 12)
      .attr("height", 10)
      .attr("rx", 3)
      .attr("fill", index % 2 === 0 ? palette.redHighlight : palette.blueHighlight)
      .attr("stroke", index % 2 === 0 ? palette.red : palette.blue)
      .attr("opacity", loadOpacity);
    movingDotOnLine(g, x + 6, y + 12, loadBox.x + 12 + index * 18, loadBox.y + 6, progressPulse(seconds, index * 0.12, 3.2), index % 2 === 0 ? palette.red : palette.blue, 3);
  });

  const loop = g.append("g").attr("transform", "translate(372,352)");
  loop.append("circle")
    .attr("r", 44)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.gray300)
    .attr("stroke-width", 3)
    .attr("stroke-dasharray", "5 7");
  const loopAngle = progressPulse(seconds, 0.12, 5.6) * Math.PI * 2 - Math.PI / 2;
  loop.append("circle")
    .attr("cx", Math.cos(loopAngle) * 44)
    .attr("cy", Math.sin(loopAngle) * 44)
    .attr("r", 7)
    .attr("fill", palette.red)
    .attr("stroke", "#fff")
    .attr("stroke-width", 2);
  loop.append("text")
    .attr("text-anchor", "middle")
    .attr("class", "svg-label")
    .attr("y", 5)
    .text("loop");

  arrow(g, outputBox.x, outputBox.y + 42, contextBox.x + contextBox.w - 22, contextBox.y + contextBox.h + 12, palette.red, 0.5, 2.6);
  movingDotOnLine(g, outputBox.x, outputBox.y + 42, contextBox.x + contextBox.w - 22, contextBox.y + contextBox.h + 12, progressPulse(seconds, 0.78, 5.6), palette.red, 5);
}

function drawBilling(g, seconds, sceneProgress) {
  const lanes = [
    { label: "Input tokens", x: 54, y: 88, color: palette.blue, width: 118 },
    { label: "Output tokens", x: 54, y: 164, color: palette.red, width: 154 },
    { label: "Cached prefix", x: 54, y: 240, color: palette.green, width: 86 },
    { label: "Tool loop", x: 54, y: 316, color: palette.orange, width: 130 }
  ];
  lanes.forEach((lane, index) => {
    chip(g, lane.x, lane.y, lane.label, { width: 148, fill: "#ffffff", stroke: lane.color });
    const flowWidth = lane.width + Math.sin(seconds * 0.08 + index) * 14;
    g.append("path")
      .attr("d", `M${lane.x + 150},${lane.y + 15} C${lane.x + 245},${lane.y + 15} ${lane.x + 278},${202 + index * 9} 372,210`)
      .attr("fill", "none")
      .attr("stroke", lane.color)
      .attr("stroke-width", 8 + index)
      .attr("stroke-opacity", 0.32 + sceneProgress * 0.28)
      .attr("stroke-linecap", "round");
    movingDotOnLine(g, lane.x + 150, lane.y + 15, 372, 210, progressPulse(seconds, index * 0.21, 4.4), lane.color, 5);
    g.append("rect").attr("x", 226).attr("y", lane.y + 4).attr("width", flowWidth).attr("height", 8).attr("rx", 4).attr("fill", lane.color).attr("opacity", 0.72);
  });

  g.append("circle").attr("cx", 430).attr("cy", 210).attr("r", 82).attr("fill", palette.yellowHighlight).attr("stroke", palette.yellow).attr("stroke-width", 3);
  g.append("text").attr("x", 430).attr("y", 200).attr("text-anchor", "middle").attr("class", "svg-title").text("Usage");
  g.append("text").attr("x", 430).attr("y", 224).attr("text-anchor", "middle").attr("class", "svg-caption").text("model x tokens");

  const credits = d3.range(12);
  credits.forEach((_, index) => {
    const angle = (index / credits.length) * Math.PI * 2 + seconds * 0.018;
    const r = 124 + (index % 2) * 14;
    g.append("rect")
      .attr("x", 430 + Math.cos(angle) * r - 12)
      .attr("y", 210 + Math.sin(angle) * r - 8)
      .attr("width", 24)
      .attr("height", 16)
      .attr("rx", 4)
      .attr("fill", index % 3 === 0 ? palette.redHighlight : palette.blueHighlight)
      .attr("stroke", index % 3 === 0 ? palette.red : palette.blue);
  });

  chip(g, 570, 82, "Cost per successful task", { width: 150, fill: palette.purpleHighlight, stroke: palette.purple });
  chip(g, 570, 138, "Budget caps", { width: 150, fill: palette.blueHighlight, stroke: palette.blue });
  chip(g, 570, 194, "Cache reuse", { width: 150, fill: palette.greenHighlight, stroke: palette.green });
  chip(g, 570, 250, "Local operations", { width: 150, fill: palette.orangeHighlight, stroke: palette.orange });
}

function drawEvaluation(g, seconds, sceneProgress) {
  const plot = { x: 72, y: 82, w: 318, h: 168 };
  const x = d3.scaleLinear().domain([-3, 3]).range([plot.x, plot.x + plot.w]);
  const y = d3.scaleLinear().domain([0, 0.42]).range([plot.y + plot.h, plot.y]);
  const line = d3.line()
    .x((d) => x(d.x))
    .y((d) => y(d.y))
    .curve(d3.curveBasis);
  const shift = (sceneProgress - 0.5) * 0.9;
  const data = d3.range(-3, 3.05, 0.12).map((value) => ({
    x: value,
    y: Math.exp(-Math.pow(value - shift, 2) / 1.45) / 3.2
  }));
  g.append("rect").attr("x", plot.x).attr("y", plot.y).attr("width", plot.w).attr("height", plot.h).attr("fill", "#ffffff").attr("stroke", palette.gray200);
  g.append("path").datum(data).attr("d", line).attr("fill", "none").attr("stroke", palette.blue).attr("stroke-width", 4);
  g.append("text").attr("x", plot.x).attr("y", plot.y - 18).attr("class", "svg-label").text("Next-token distribution");
  const sampleX = x(-2.2 + progressPulse(seconds, 0, 6) * 4.4);
  g.append("line").attr("x1", sampleX).attr("x2", sampleX).attr("y1", plot.y + 8).attr("y2", plot.y + plot.h).attr("stroke", palette.red).attr("stroke-width", 3).attr("stroke-dasharray", "6 5");
  g.append("circle").attr("cx", sampleX).attr("cy", y(0.29)).attr("r", 7).attr("fill", palette.red).attr("stroke", "#fff").attr("stroke-width", 2);

  const attempts = d3.range(20).map((i) => ({ i, pass: [1, 3, 6, 9, 14, 18].includes(i) }));
  attempts.forEach((attempt, index) => {
    const col = index % 10;
    const row = Math.floor(index / 10);
    const reveal = clamp((seconds - 54 - index * 0.9) / 10, 0.2, 1);
    g.append("rect")
      .attr("x", 438 + col * 26)
      .attr("y", 88 + row * 42)
      .attr("width", 20)
      .attr("height", 20)
      .attr("rx", 5)
      .attr("fill", attempt.pass ? palette.green : palette.gray200)
      .attr("opacity", reveal)
      .attr("stroke", attempt.pass ? palette.greenHover : palette.gray400);
  });
  g.append("text").attr("x", 438).attr("y", 69).attr("class", "svg-label").text("20 sampled attempts");
  g.append("text").attr("x", 438).attr("y", 190).attr("class", "svg-caption").text("6 pass deterministic checks");

  const rubrics = [
    ["Tests", palette.green],
    ["Rubric", palette.orange],
    ["Trace grader", palette.purple],
    ["Human review", palette.blue]
  ];
  rubrics.forEach(([label, color], index) => {
    chip(g, 116 + index * 142, 312 + Math.sin(seconds * 0.12 + index) * 4, label, { width: 118, fill: "#ffffff", stroke: color });
    if (index < rubrics.length - 1) arrow(g, 234 + index * 142, 327, 256 + index * 142, 327, palette.gray500, 0.8);
  });
}

function drawAgent(g, seconds, sceneProgress) {
  const nodes = [
    { id: "Goal", x: 382, y: 70, color: palette.red },
    { id: "Model", x: 578, y: 188, color: palette.blue },
    { id: "Tool", x: 382, y: 322, color: palette.green },
    { id: "Observe", x: 178, y: 188, color: palette.orange }
  ];
  const center = { x: 382, y: 200 };
  g.append("circle").attr("cx", center.x).attr("cy", center.y).attr("r", 154).attr("fill", "#ffffff").attr("stroke", palette.gray200).attr("stroke-width", 2).attr("stroke-dasharray", "7 8");
  nodes.forEach((node, index) => {
    const next = nodes[(index + 1) % nodes.length];
    arrow(g, node.x, node.y, next.x, next.y, palette.gray500, 0.52, 2.4);
  });
  nodes.forEach((node) => {
    g.append("circle").attr("cx", node.x).attr("cy", node.y).attr("r", 45).attr("fill", `${node.color}22`).attr("stroke", node.color).attr("stroke-width", 3);
    g.append("text").attr("x", node.x).attr("y", node.y + 5).attr("text-anchor", "middle").attr("class", "svg-label").text(node.id);
  });
  const loopP = progressPulse(seconds, 0, 8);
  const angle = loopP * Math.PI * 2 - Math.PI / 2;
  g.append("circle").attr("cx", center.x + Math.cos(angle) * 154).attr("cy", center.y + Math.sin(angle) * 154).attr("r", 9).attr("fill", palette.red).attr("stroke", "#fff").attr("stroke-width", 2);

  const branches = [
    { label: "search", y: 82, color: palette.blue },
    { label: "read file", y: 132, color: palette.green },
    { label: "run test", y: 272, color: palette.orange },
    { label: "stop", y: 322, color: palette.purple }
  ];
  branches.forEach((branch, index) => {
    const opacity = 0.35 + Math.max(0, Math.sin(seconds * 0.35 + index)) * 0.55;
    chip(g, 46, branch.y, branch.label, { width: 96, fill: "#ffffff", stroke: branch.color, opacity });
  });
  chip(g, 606, 334, "permissions", { width: 112, fill: palette.redHighlight, stroke: palette.red });
}

function drawGuardrail(g, seconds, sceneProgress) {
  const stages = [
    { label: "User input", x: 50, color: palette.blue },
    { label: "Model", x: 240, color: palette.purple },
    { label: "Tool request", x: 430, color: palette.orange },
    { label: "Final output", x: 620, color: palette.green }
  ];
  stages.forEach((stage, index) => {
    chip(g, stage.x, 202, stage.label, { width: 118, fill: "#ffffff", stroke: stage.color });
    if (index < stages.length - 1) arrow(g, stage.x + 118, 217, stages[index + 1].x, 217, palette.gray500, 0.7);
  });
  const controls = [
    { label: "ingress", x: 176, y: 132 },
    { label: "pre-tool", x: 365, y: 132 },
    { label: "egress", x: 555, y: 132 }
  ];
  controls.forEach((control, index) => {
    const pulse = 0.75 + Math.sin(seconds * 0.18 + index) * 0.18;
    g.append("path")
      .attr("d", `M${control.x},${control.y - 38} L${control.x + 42},${control.y - 20} L${control.x + 36},${control.y + 35} L${control.x},${control.y + 55} L${control.x - 36},${control.y + 35} L${control.x - 42},${control.y - 20} Z`)
      .attr("fill", index === 1 ? palette.orangeHighlight : palette.blueHighlight)
      .attr("stroke", index === 1 ? palette.orange : palette.blue)
      .attr("stroke-width", 3)
      .attr("opacity", pulse);
    g.append("text").attr("x", control.x).attr("y", control.y + 8).attr("text-anchor", "middle").attr("class", "svg-label").text(control.label);
  });
  const blockedP = progressPulse(seconds, 0.12, 5);
  g.append("path").attr("d", "M70,316 C210,366 290,328 392,360").attr("fill", "none").attr("stroke", palette.red).attr("stroke-width", 5).attr("stroke-dasharray", "9 8");
  movingDotOnLine(g, 70, 316, 392, 360, blockedP, palette.red, 7);
  g.append("text").attr("x", 410).attr("y", 364).attr("class", "svg-label").text("blocked or escalated");
  chip(g, 526, 306, "allow", { width: 82, fill: palette.greenHighlight, stroke: palette.green });
  chip(g, 620, 306, "redact", { width: 82, fill: palette.yellowHighlight, stroke: palette.yellow });
}

function drawHarness(g, seconds, sceneProgress) {
  const cx = 378;
  const cy = 206;
  const layers = [
    { r: 168, label: "environment", color: palette.gray300 },
    { r: 132, label: "permissions", color: palette.red },
    { r: 96, label: "tools + MCP", color: palette.green },
    { r: 58, label: "model", color: palette.blue }
  ];
  layers.forEach((layer, index) => {
    g.append("circle")
      .attr("cx", cx)
      .attr("cy", cy)
      .attr("r", layer.r + Math.sin(seconds * 0.07 + index) * 2)
      .attr("fill", index === layers.length - 1 ? palette.blueHighlight : "none")
      .attr("stroke", layer.color)
      .attr("stroke-width", index === layers.length - 1 ? 4 : 2.5)
      .attr("stroke-dasharray", index === 0 ? "8 8" : null)
      .attr("opacity", 0.45 + index * 0.12);
    g.append("text").attr("x", cx + layer.r + 10).attr("y", cy - layer.r + 14).attr("class", "svg-caption").text(layer.label);
  });
  g.append("text").attr("x", cx).attr("y", cy + 6).attr("text-anchor", "middle").attr("class", "svg-title").text("LLM");
  const left = [
    ["system prompt", palette.purple],
    ["context rules", palette.blue],
    ["stop condition", palette.orange]
  ];
  left.forEach(([label, color], index) => {
    chip(g, 54, 94 + index * 72, label, { width: 128, fill: "#ffffff", stroke: color });
    arrow(g, 182, 109 + index * 72, 236, 170 + index * 12, color, 0.55);
  });
  const tools = [
    ["files", 584, 92, palette.green],
    ["tests", 616, 168, palette.orange],
    ["search", 588, 244, palette.blue],
    ["calendar", 554, 320, palette.purple]
  ];
  tools.forEach(([label, x, y, color], index) => {
    chip(g, x, y, label, { width: 92, fill: "#ffffff", stroke: color });
    movingDotOnLine(g, cx + 76, cy, x, y + 15, progressPulse(seconds, index * 0.17, 5.8), color, 4.5);
  });
}

function drawHook(g, seconds, sceneProgress) {
  const events = [
    ["SessionStart", palette.blue],
    ["UserPromptSubmit", palette.green],
    ["PreToolUse", palette.red],
    ["PostToolUse", palette.orange],
    ["SessionEnd", palette.purple]
  ];
  const x = 150;
  events.forEach(([label, color], index) => {
    const y = 70 + index * 70;
    g.append("circle").attr("cx", x).attr("cy", y).attr("r", 14).attr("fill", color).attr("stroke", "#fff").attr("stroke-width", 2);
    if (index < events.length - 1) g.append("line").attr("x1", x).attr("x2", x).attr("y1", y + 14).attr("y2", y + 56).attr("stroke", palette.gray300).attr("stroke-width", 3);
    g.append("text").attr("x", x + 28).attr("y", y + 5).attr("class", "svg-label").text(label);
  });
  const activeIndex = Math.floor(progressPulse(seconds, 0, 10) * events.length);
  g.append("circle").attr("cx", x).attr("cy", 70 + activeIndex * 70).attr("r", 22).attr("fill", "none").attr("stroke", palette.red).attr("stroke-width", 4);

  const boxX = 420;
  g.append("rect").attr("x", boxX).attr("y", 92).attr("width", 210).attr("height", 186).attr("rx", 12).attr("fill", palette.blueHighlight).attr("stroke", palette.blue).attr("stroke-width", 3);
  g.append("text").attr("x", boxX + 105).attr("y", 126).attr("text-anchor", "middle").attr("class", "svg-title").text("Hook handler");
  ["inspect payload", "apply policy", "return decision"].forEach((label, index) => {
    chip(g, boxX + 35, 154 + index * 42, label, { width: 140, fill: "#ffffff", stroke: index === 1 ? palette.red : palette.blue });
  });
  arrow(g, 310, 210, boxX, 184, palette.red, 0.85, 3);
  arrow(g, boxX + 210, 184, 700, 184, palette.green, 0.85, 3);
  chip(g, 638, 168, progressPulse(seconds, 0.2, 6) > 0.5 ? "allow" : "deny", {
    width: 74,
    fill: progressPulse(seconds, 0.2, 6) > 0.5 ? palette.greenHighlight : palette.redHighlight,
    stroke: progressPulse(seconds, 0.2, 6) > 0.5 ? palette.green : palette.red
  });
  drawCommonLegend(g, [
    { label: "synchronous checks affect latency", color: palette.orange },
    { label: "audit fields preserve evidence", color: palette.purple }
  ], 430, 332);
}

function drawPlugin(g, seconds, sceneProgress) {
  const packageX = 86;
  const packageY = 84;
  g.append("rect").attr("x", packageX).attr("y", packageY).attr("width", 272).attr("height", 242).attr("rx", 14).attr("fill", palette.purpleHighlight).attr("stroke", palette.purple).attr("stroke-width", 3);
  g.append("text").attr("x", packageX + 136).attr("y", packageY + 36).attr("text-anchor", "middle").attr("class", "svg-title").text("Plugin package");
  const parts = [
    ["skills", palette.green],
    ["agents", palette.blue],
    ["hooks", palette.red],
    ["MCP config", palette.orange],
    ["metadata", palette.purple],
    ["policy defaults", palette.gray600]
  ];
  parts.forEach(([label, color], index) => {
    const col = index % 2;
    const row = Math.floor(index / 2);
    chip(g, packageX + 30 + col * 122, packageY + 68 + row * 54, label, { width: 104, fill: "#ffffff", stroke: color });
  });
  const harnessX = 500;
  g.append("rect").attr("x", harnessX).attr("y", 112).attr("width", 180).attr("height", 188).attr("rx", 14).attr("fill", "#ffffff").attr("stroke", palette.blue).attr("stroke-width", 3);
  g.append("text").attr("x", harnessX + 90).attr("y", 152).attr("text-anchor", "middle").attr("class", "svg-title").text("Harness");
  ["discover", "enable", "govern"].forEach((label, index) => {
    chip(g, harnessX + 42, 176 + index * 42, label, { width: 96, fill: index === 2 ? palette.redHighlight : palette.blueHighlight, stroke: index === 2 ? palette.red : palette.blue });
  });
  arrow(g, packageX + 272, 205, harnessX, 205, palette.purple, 0.85, 4);
  movingDotOnLine(g, packageX + 282, 205, harnessX - 4, 205, progressPulse(seconds, 0, 4.8), palette.purple, 7);
  chip(g, 230, 356, "review source", { width: 116, fill: palette.yellowHighlight, stroke: palette.yellow });
  chip(g, 372, 356, "version", { width: 92, fill: palette.blueHighlight, stroke: palette.blue });
  chip(g, 490, 356, "rollback", { width: 100, fill: palette.redHighlight, stroke: palette.red });
}

function drawSkill(g, seconds, sceneProgress) {
  const triggerX = 68;
  chip(g, triggerX, 72, "task trigger", { width: 122, fill: palette.blueHighlight, stroke: palette.blue });
  chip(g, triggerX, 162, "SKILL.md", { width: 122, fill: palette.greenHighlight, stroke: palette.green });
  chip(g, triggerX, 252, "support files", { width: 122, fill: palette.orangeHighlight, stroke: palette.orange });
  arrow(g, triggerX + 122, 87, 282, 126, palette.blue, 0.75);
  arrow(g, triggerX + 122, 177, 282, 176, palette.green, 0.75);
  arrow(g, triggerX + 122, 267, 282, 228, palette.orange, 0.75);

  g.append("rect").attr("x", 282).attr("y", 96).attr("width", 224).attr("height", 164).attr("rx", 12).attr("fill", "#ffffff").attr("stroke", palette.green).attr("stroke-width", 3);
  g.append("text").attr("x", 394).attr("y", 132).attr("text-anchor", "middle").attr("class", "svg-title").text("Loaded skill");
  ["description", "procedure", "references", "scripts"].forEach((label, index) => {
    const y = 154 + index * 24;
    g.append("rect").attr("x", 320).attr("y", y - 12).attr("width", 148 + index * 10).attr("height", 12).attr("rx", 6).attr("fill", [palette.blue, palette.green, palette.orange, palette.purple][index]).attr("opacity", 0.72);
    g.append("text").attr("x", 320).attr("y", y + 16).attr("class", "svg-caption").text(label);
  });

  const budget = 0.38 + sceneProgress * 0.42;
  g.append("text").attr("x", 570).attr("y", 112).attr("class", "svg-label").text("Context budget");
  g.append("rect").attr("x", 570).attr("y", 132).attr("width", 112).attr("height", 212).attr("rx", 12).attr("fill", palette.gray100).attr("stroke", palette.gray300);
  g.append("rect").attr("x", 570).attr("y", 132 + 212 * (1 - budget)).attr("width", 112).attr("height", 212 * budget).attr("rx", 12).attr("fill", palette.green).attr("opacity", 0.82);
  g.append("text").attr("x", 626).attr("y", 370).attr("text-anchor", "middle").attr("class", "svg-caption").text("load detail only when needed");
  movingDotOnLine(g, 190, 177, 282, 176, progressPulse(seconds, 0.2, 4.8), palette.green, 6);
}

function drawMcp(g, seconds, sceneProgress) {
  const host = { x: 64, y: 150, w: 154, h: 126, label: "Host app", color: palette.blue };
  const client = { x: 304, y: 170, w: 136, h: 88, label: "MCP client", color: palette.green };
  const server = { x: 544, y: 116, w: 150, h: 196, label: "MCP server", color: palette.purple };
  [host, client, server].forEach((box) => {
    g.append("rect").attr("x", box.x).attr("y", box.y).attr("width", box.w).attr("height", box.h).attr("rx", 12).attr("fill", "#ffffff").attr("stroke", box.color).attr("stroke-width", 3);
    g.append("text").attr("x", box.x + box.w / 2).attr("y", box.y + 36).attr("text-anchor", "middle").attr("class", "svg-title").text(box.label);
  });
  chip(g, 94, 206, "model UI", { width: 94, fill: palette.blueHighlight, stroke: palette.blue });
  chip(g, 326, 210, "protocol", { width: 92, fill: palette.greenHighlight, stroke: palette.green });
  ["tools", "resources", "prompts"].forEach((label, index) => {
    chip(g, 572, 166 + index * 46, label, { width: 94, fill: "#ffffff", stroke: [palette.red, palette.orange, palette.purple][index] });
  });
  arrow(g, host.x + host.w, 212, client.x, 212, palette.blue, 0.8, 3);
  arrow(g, client.x + client.w, 212, server.x, 212, palette.purple, 0.8, 3);
  movingDotOnLine(g, host.x + host.w, 212, client.x, 212, progressPulse(seconds, 0, 4.2), palette.blue, 6);
  movingDotOnLine(g, client.x + client.w, 212, server.x, 212, progressPulse(seconds, 0.44, 4.2), palette.purple, 6);
  chip(g, 160, 344, "consent", { width: 96, fill: palette.yellowHighlight, stroke: palette.yellow });
  chip(g, 278, 344, "auth mode", { width: 106, fill: palette.redHighlight, stroke: palette.red });
  chip(g, 406, 344, "audit log", { width: 98, fill: palette.blueHighlight, stroke: palette.blue });
  chip(g, 526, 344, "fallback", { width: 96, fill: palette.greenHighlight, stroke: palette.green });
}

function drawAlternatives(g, seconds, sceneProgress) {
  const criteria = ["Context", "Actions", "Permissions", "Evals", "Billing"];
  const products = [
    { label: "Rovo", color: palette.orange, values: [0.82, 0.62, 0.72, 0.48, 0.58] },
    { label: "Gemini", color: palette.blue, values: [0.76, 0.58, 0.62, 0.52, 0.55] },
    { label: "Copilot", color: palette.green, values: [0.68, 0.86, 0.76, 0.72, 0.66] },
    { label: "Claude", color: palette.purple, values: [0.72, 0.82, 0.8, 0.76, 0.5] }
  ];
  const cx = 260;
  const cy = 214;
  const radius = 128;
  criteria.forEach((criterion, index) => {
    const angle = (index / criteria.length) * Math.PI * 2 - Math.PI / 2;
    g.append("line").attr("x1", cx).attr("y1", cy).attr("x2", cx + Math.cos(angle) * radius).attr("y2", cy + Math.sin(angle) * radius).attr("stroke", palette.gray200);
    g.append("text").attr("x", cx + Math.cos(angle) * (radius + 38)).attr("y", cy + Math.sin(angle) * (radius + 28)).attr("text-anchor", "middle").attr("class", "svg-caption").text(criterion);
  });
  [0.33, 0.66, 1].forEach((r) => {
    const points = criteria.map((_, index) => {
      const angle = (index / criteria.length) * Math.PI * 2 - Math.PI / 2;
      return [cx + Math.cos(angle) * radius * r, cy + Math.sin(angle) * radius * r];
    });
    g.append("path").attr("d", `${d3.line()(points)}Z`).attr("fill", "none").attr("stroke", palette.gray200);
  });
  const line = d3.line().curve(d3.curveLinearClosed);
  products.forEach((product, productIndex) => {
    const reveal = clamp((sceneProgress + productIndex * 0.07), 0.2, 1);
    const points = product.values.map((value, index) => {
      const angle = (index / criteria.length) * Math.PI * 2 - Math.PI / 2;
      return [cx + Math.cos(angle) * radius * value * reveal, cy + Math.sin(angle) * radius * value * reveal];
    });
    g.append("path").attr("d", line(points)).attr("fill", product.color).attr("fill-opacity", 0.08).attr("stroke", product.color).attr("stroke-width", 2.4);
  });
  products.forEach((product, index) => {
    chip(g, 500, 96 + index * 52, product.label, { width: 116, fill: "#ffffff", stroke: product.color });
  });
  chip(g, 486, 330, "same checklist", { width: 134, fill: palette.yellowHighlight, stroke: palette.yellow });
}

function drawConceptVisual(concept, seconds) {
  prepareSvg(concept, seconds);
  const { beat, progress } = sceneForTime(concept, seconds);
  const g = svg.append("g");
  if (concept.kind === "evaluation") {
    drawEvaluationVisualOnly(g, {
      palette,
      beat,
      sceneProgress: progress,
      seconds,
      pulse: 0.84 + Math.sin(seconds * 0.16) * 0.16,
      clamp,
      easeInOut,
      easeOut,
      lerp,
      drawHookText
    });
    return;
  }
  if (concept.kind !== "llm" && isVisualOnlyConcept(concept)) {
    drawGenericConceptVisualOnly(g, concept, {
      palette,
      beat,
      sceneProgress: progress,
      seconds,
      clamp,
      easeInOut,
      easeOut,
      lerp,
      drawHookText
    });
    return;
  }
  switch (concept.kind) {
    case "llm":
      drawLlm(g, seconds, progress);
      break;
    case "billing":
      drawBilling(g, seconds, progress);
      break;
    case "evaluation":
      drawEvaluation(g, seconds, progress);
      break;
    case "agent":
      drawAgent(g, seconds, progress);
      break;
    case "guardrail":
      drawGuardrail(g, seconds, progress);
      break;
    case "harness":
      drawHarness(g, seconds, progress);
      break;
    case "hook":
      drawHook(g, seconds, progress);
      break;
    case "plugin":
      drawPlugin(g, seconds, progress);
      break;
    case "skill":
      drawSkill(g, seconds, progress);
      break;
    case "mcp":
      drawMcp(g, seconds, progress);
      break;
    case "alternatives":
      drawAlternatives(g, seconds, progress);
      break;
    default:
      drawLlm(g, seconds, progress);
  }
}

export function renderConceptFrame(conceptId, seconds, options = {}) {
  const concept = selectConcept(conceptId);
  currentConcept = concept;
  const time = clamp(Number(seconds) || 0, 0, DURATION);
  if (options.capture) document.body.dataset.capture = "1";
  document.body.classList.toggle("visual-only", isVisualOnlyConcept(concept));
  setInterface(concept, time);
  drawConceptVisual(concept, time);
  return {
    conceptId: concept.id,
    time,
    beat: sceneForTime(concept, time).beat.id,
    svgElementCount: svg.selectAll("*").size(),
    bulletCount: concept.scenes.flatMap((scene) => scene.bullets).length,
    references: concept.references.length,
    animationsPerFrame: 4
  };
}

function startPlayback(conceptId) {
  cancelAnimationFrame(playbackFrame);
  const concept = selectConcept(conceptId);
  const start = performance.now();
  function tick(now) {
    const seconds = ((now - start) / 1000) % DURATION;
    renderConceptFrame(concept.id, seconds);
    playbackFrame = requestAnimationFrame(tick);
  }
  tick(start);
}

function init() {
  const params = new URLSearchParams(window.location.search);
  const concept = selectConcept(params.get("concept"));
  const t = Number(params.get("t") ?? "0");
  const autoplay = params.get("play") === "1";
  window.AI_CONCEPTS = concepts;
  window.AI_RESEARCH_NOTES = researchNotes;
  window.renderConceptFrame = renderConceptFrame;
  window.startConceptPlayback = startPlayback;
  renderConceptFrame(concept.id, t);
  if (autoplay) startPlayback(concept.id);
}

init();

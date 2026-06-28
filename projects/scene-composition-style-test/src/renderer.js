import { animate } from "../node_modules/animejs/dist/bundles/anime.esm.js";

const d3 = window.d3;
if (!d3) throw new Error("D3 must be loaded before renderer.js");

const WIDTH = 1280;
const HEIGHT = 720;
const DURATION = 12;

const C = {
  paper: "#f8fafc",
  paper2: "#eef4f1",
  ink: "#24313a",
  muted: "#6e7b84",
  hairline: "#c8d5d6",
  grid: "#dfe8e7",
  teal: "#0f9f8c",
  tealSoft: "#d8f3ee",
  blue: "#2f80ed",
  blueSoft: "#dbeafe",
  green: "#2ea66f",
  greenSoft: "#def7e9",
  coral: "#d4515f",
  coralSoft: "#ffe3e5",
  yellow: "#f0b83f",
  yellowSoft: "#fff3c4",
  white: "#ffffff"
};

const svg = document.querySelector("#scene-svg");
const curveLine = d3.line().x((d) => d.x).y((d) => d.y).curve(d3.curveCatmullRom.alpha(0.5));
const straightLine = d3.line().x((d) => d.x).y((d) => d.y);
const branchLink = d3.linkHorizontal().x((d) => d.x).y((d) => d.y);

function clamp(value, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function easeOut(t) {
  return 1 - Math.pow(1 - clamp(t), 3);
}

function easeInOut(t) {
  t = clamp(t);
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function pulse(t) {
  return Math.sin(clamp(t) * Math.PI);
}

function ns(name) {
  return document.createElementNS("http://www.w3.org/2000/svg", name);
}

function clear() {
  while (svg.lastChild && !["title", "desc"].includes(svg.lastChild.id)) {
    svg.removeChild(svg.lastChild);
  }
}

function add(tag, attrs = {}, parent = svg) {
  const el = ns(tag);
  for (const [key, value] of Object.entries(attrs)) {
    if (value !== undefined && value !== null) el.setAttribute(key, String(value));
  }
  parent.appendChild(el);
  return el;
}

function group(attrs = {}) {
  return add("g", attrs);
}

function text(x, y, content, attrs = {}, parent = svg) {
  const el = add("text", { x, y, ...attrs }, parent);
  el.textContent = content;
  return el;
}

function roundRect(x, y, w, h, r, attrs = {}, parent = svg) {
  return add("rect", { x, y, width: w, height: h, rx: r, ry: r, ...attrs }, parent);
}

function line(x1, y1, x2, y2, attrs = {}, parent = svg) {
  return add("line", { x1, y1, x2, y2, ...attrs }, parent);
}

function circle(cx, cy, r, attrs = {}, parent = svg) {
  return add("circle", { cx, cy, r, ...attrs }, parent);
}

function path(d, attrs = {}, parent = svg) {
  return add("path", { d, ...attrs }, parent);
}

function background(sceneTint = C.paper2) {
  roundRect(0, 0, WIDTH, HEIGHT, 0, { fill: C.paper });
  for (let x = 80; x <= WIDTH - 80; x += 80) {
    line(x, 56, x, HEIGHT - 108, { stroke: C.grid, "stroke-width": 1, opacity: 0.55 });
  }
  for (let y = 72; y <= HEIGHT - 120; y += 72) {
    line(56, y, WIDTH - 56, y, { stroke: C.grid, "stroke-width": 1, opacity: 0.55 });
  }
  roundRect(56, HEIGHT - 108, WIDTH - 112, 1, 0, { fill: C.hairline, opacity: 0.9 });
  roundRect(48, 48, WIDTH - 96, HEIGHT - 156, 8, {
    fill: "none",
    stroke: sceneTint,
    "stroke-width": 2,
    opacity: 0.7
  });
}

function sceneLabel(id, title) {
  text(72, 96, id, { class: "small-label mono", "font-size": 16 });
  text(72, 128, title, { class: "label", "font-size": 26 });
}

function token(x, y, r, attrs = {}) {
  circle(x, y, r + 12, { fill: attrs.haloFill ?? C.tealSoft, opacity: attrs.halo ?? 0.9 });
  circle(x, y, r, {
    fill: attrs.fill ?? C.teal,
    stroke: C.white,
    "stroke-width": attrs.strokeWidth ?? 4
  });
}

function checkMark(x, y, scale = 1, attrs = {}, parent = svg) {
  path(`M${x - 7 * scale} ${y} L${x - 1 * scale} ${y + 7 * scale} L${x + 10 * scale} ${y - 8 * scale}`, {
    fill: "none",
    stroke: attrs.stroke ?? C.green,
    "stroke-width": attrs.width ?? 4,
    opacity: attrs.opacity ?? 1,
    "stroke-linecap": "round",
    "stroke-linejoin": "round"
  }, parent);
}

function segmentLengths(points) {
  const lengths = [];
  let total = 0;
  for (let i = 1; i < points.length; i += 1) {
    const a = points[i - 1];
    const b = points[i];
    const len = Math.hypot(b.x - a.x, b.y - a.y);
    lengths.push(len);
    total += len;
  }
  return { lengths, total };
}

function pointOnPolyline(points, t) {
  const { lengths, total } = segmentLengths(points);
  let remaining = clamp(t) * total;
  for (let i = 1; i < points.length; i += 1) {
    const len = lengths[i - 1];
    if (remaining <= len) {
      const local = len === 0 ? 0 : remaining / len;
      return {
        x: lerp(points[i - 1].x, points[i].x, local),
        y: lerp(points[i - 1].y, points[i].y, local)
      };
    }
    remaining -= len;
  }
  return points[points.length - 1];
}

function partialPolyline(points, t) {
  const { lengths, total } = segmentLengths(points);
  const out = [points[0]];
  let remaining = clamp(t) * total;
  for (let i = 1; i < points.length; i += 1) {
    const len = lengths[i - 1];
    if (remaining >= len) {
      out.push(points[i]);
      remaining -= len;
    } else {
      const local = len === 0 ? 0 : remaining / len;
      out.push({
        x: lerp(points[i - 1].x, points[i].x, local),
        y: lerp(points[i - 1].y, points[i].y, local)
      });
      break;
    }
  }
  return straightLine(out);
}

function bezierPoint(p0, p1, p2, p3, t) {
  const u = 1 - clamp(t);
  const tt = t * t;
  const uu = u * u;
  const uuu = uu * u;
  const ttt = tt * t;
  return {
    x: uuu * p0.x + 3 * uu * t * p1.x + 3 * u * tt * p2.x + ttt * p3.x,
    y: uuu * p0.y + 3 * uu * t * p1.y + 3 * u * tt * p2.y + ttt * p3.y
  };
}

function horizontalBezierPoint(source, target, t) {
  const midX = (source.x + target.x) / 2;
  return bezierPoint(source, { x: midX, y: source.y }, { x: midX, y: target.y }, target, t);
}

function drawSceneOne(local) {
  background(C.blueSoft);
  sceneLabel("THIRDS / NETWORK", "Cache policy impact");
  svg.setAttribute("data-current-composition", "d3-composition-thirds-force-network-cache-policy");

  const intro = easeOut(local / 0.8);
  const route = easeInOut((local - 0.35) / 2.35);
  const questionPulse = 0.5 + 0.5 * Math.sin(local * Math.PI * 2.2);

  const root = group({
    "data-composition-id": "thirds-force-network",
    "data-pattern-id": "d3-pattern-force-network",
    "data-composition-pattern-id": "d3-composition-thirds-force-network-cache-policy"
  });
  const nodes = [
    { id: "app", label: "APP", x: 160, y: 292, r: 33, role: "source" },
    { id: "api", label: "API", x: 310, y: 225, r: 35, role: "router" },
    { id: "log", label: "LOG", x: 278, y: 390, r: 31, role: "support" },
    { id: "cache", label: "CACHE", x: 468, y: 318, r: 42, role: "store" },
    { id: "policy", label: "POLICY", x: 616, y: 242, r: 28, role: "rule" },
    { id: "hit", label: "HIT", x: 628, y: 420, r: 27, role: "metric" },
    { id: "miss", label: "MISS", x: 394, y: 468, r: 24, role: "risk" }
  ];
  const byId = new Map(nodes.map((node) => [node.id, node]));
  const links = [
    ["app", "api"],
    ["app", "log"],
    ["api", "cache"],
    ["log", "cache"],
    ["cache", "policy"],
    ["cache", "hit"],
    ["miss", "log"]
  ];

  links.forEach(([a, b], i) => {
    const source = byId.get(a);
    const target = byId.get(b);
    path(curveLine([source, target]), {
      fill: "none",
      stroke: i === 5 ? C.green : C.hairline,
      "stroke-width": i === 5 ? 4 : 3,
      opacity: intro * (i === 5 ? 0.55 : 0.72),
      "stroke-linecap": "round"
    }, root);
  });

  nodes.forEach((node, i) => {
    const appear = clamp((intro - i * 0.035) / 0.7);
    const roleColor = node.role === "risk" ? C.coralSoft : node.role === "metric" ? C.greenSoft : C.white;
    circle(node.x, node.y, node.r + (node.id === "cache" ? questionPulse * 4 : 0), {
      fill: roleColor,
      stroke: node.id === "cache" ? C.blue : C.hairline,
      "stroke-width": node.id === "cache" ? 3 : 2,
      opacity: 0.15 + appear * 0.85
    }, root);
    text(node.x, node.y + 6, node.label, {
      "text-anchor": "middle",
      class: "small-label mono",
      "font-size": node.label.length > 4 ? 12 : 14,
      opacity: appear
    }, root);
  });

  const cardX = lerp(870, 770, intro);
  roundRect(cardX, 190, 390, 236, 8, {
    fill: C.white,
    stroke: C.ink,
    "stroke-width": 2.5,
    opacity: intro
  });
  roundRect(cardX + 28, 226, 132, 30, 4, { fill: C.yellowSoft, opacity: intro });
  text(cardX + 44, 248, "POLICY", { class: "small-label mono", "font-size": 16, opacity: intro });
  text(cardX + 28, 318, "HELPING?", { class: "label", "font-size": 54, opacity: intro });
  text(cardX + 30, 366, "cache hit rate unknown", {
    class: "small-label mono",
    "font-size": 20,
    opacity: intro * 0.9
  });
  circle(cardX + 330, 244, 25 + questionPulse * 7, {
    fill: C.coralSoft,
    stroke: C.coral,
    "stroke-width": 3,
    opacity: intro
  });
  text(cardX + 330, 254, "?", {
    "text-anchor": "middle",
    class: "label",
    "font-size": 34,
    fill: C.coral,
    opacity: intro
  });

  const routePath = [
    { x: 160, y: 520 },
    { x: 278, y: 390 },
    { x: 468, y: 318 },
    { x: 616, y: 242 },
    { x: cardX + 48, y: 300 }
  ];
  path(straightLine(routePath), {
    fill: "none",
    stroke: C.teal,
    "stroke-width": 2,
    opacity: 0.16,
    "stroke-linecap": "round"
  }, root);
  path(partialPolyline(routePath, route), {
    fill: "none",
    stroke: C.teal,
    "stroke-width": 5,
    opacity: 0.35 + route * 0.45,
    "stroke-linecap": "round",
    "stroke-linejoin": "round"
  }, root);
  const moving = pointOnPolyline(routePath, route);
  token(moving.x, moving.y, 14 + questionPulse * 2, { halo: 0.75 });
}

function drawSceneTwo(local) {
  background(C.tealSoft);
  sceneLabel("FLOW SPINE / BRANCH", "Lookup branch");
  svg.setAttribute("data-current-composition", "d3-composition-flow-spine-router-branch");

  const enter = easeOut(local / 0.75);
  const split = easeInOut((local - 0.72) / 1.85);
  const settle = easeOut((local - 2.15) / 0.7);
  const root = group({
    "data-composition-id": "flow-spine",
    "data-pattern-id": "d3-pattern-router-branch",
    "data-composition-pattern-id": "d3-composition-flow-spine-router-branch"
  });

  line(640, 152, 640, 590, { stroke: C.hairline, "stroke-width": 2, opacity: 0.8 }, root);
  roundRect(96, 172, 500, 360, 8, {
    fill: C.white,
    stroke: C.green,
    "stroke-width": 3,
    opacity: 0.98
  }, root);
  roundRect(684, 172, 500, 360, 8, {
    fill: C.white,
    stroke: C.coral,
    "stroke-width": 3,
    opacity: 0.98
  }, root);
  const laneWake = easeInOut(local / 1.35);
  roundRect(108, 180, 476, 344 * laneWake, 6, {
    fill: C.greenSoft,
    opacity: 0.2 + split * 0.12
  }, root);
  roundRect(696, 180, 476, 344 * laneWake, 6, {
    fill: C.coralSoft,
    opacity: 0.16 + split * 0.1
  }, root);
  text(132, 222, "CACHE HIT", { class: "label mono", "font-size": 28, fill: C.green }, root);
  text(720, 222, "ORIGIN FALLBACK", { class: "label mono", "font-size": 28, fill: C.coral }, root);

  const gate = { x: 640, y: 300 };
  const start = { x: 640, y: 104 };
  const gateTop = { x: 640, y: gate.y - 52 };
  const gateExit = { x: 640, y: gate.y + 52 };
  const hit = { x: 348, y: 388 };
  const miss = { x: 934, y: 388 };
  const hitWarm = { x: 347, y: 458 };
  const missOrigin = { x: 940, y: 458 };

  roundRect(535, gate.y - 35, 210, 70, 8, {
    fill: C.yellowSoft,
    stroke: C.yellow,
    "stroke-width": 3
  }, root);
  text(640, gate.y + 9, "LOOKUP", {
    "text-anchor": "middle",
    class: "label mono",
    "font-size": 24
  }, root);

  const inlet = pointOnPolyline([start, gateTop], enter);
  path(straightLine([start, gateTop]), {
    fill: "none",
    stroke: C.teal,
    "stroke-width": 2,
    opacity: 0.18,
    "stroke-linecap": "round"
  }, root);
  path(partialPolyline([start, gateTop], enter), {
    fill: "none",
    stroke: C.teal,
    "stroke-width": 5,
    opacity: 0.55,
    "stroke-linecap": "round"
  }, root);
  token(inlet.x, inlet.y, 13);

  const hitPath = branchLink({ source: gateExit, target: hit });
  const missPath = branchLink({ source: gateExit, target: miss });
  path(hitPath, {
    fill: "none",
    stroke: C.green,
    "stroke-width": 5,
    opacity: 0.18 + split * 0.55,
    "stroke-linecap": "round"
  }, root);
  path(missPath, {
    fill: "none",
    stroke: C.coral,
    "stroke-width": 5,
    opacity: 0.18 + split * 0.55,
    "stroke-linecap": "round"
  }, root);

  const hitToken = horizontalBezierPoint(gateExit, hit, split);
  const missToken = horizontalBezierPoint(gateExit, miss, split);
  token(hitToken.x, hitToken.y, 12, { halo: 0.55, haloFill: C.greenSoft, fill: C.green });
  token(missToken.x, missToken.y, 12, { halo: 0.55, haloFill: C.coralSoft, fill: C.coral });

  const laneScale = d3.scaleLinear().domain([0, 1]).range([0, 178]);
  roundRect(236, 430, 222, 58, 6, {
    fill: C.greenSoft,
    stroke: C.green,
    "stroke-width": 2,
    opacity: settle
  }, root);
  roundRect(255, 462, laneScale(settle), 8, 4, { fill: C.green, opacity: settle }, root);
  text(hitWarm.x, hitWarm.y, "WARM KEY", {
    "text-anchor": "middle",
    class: "label mono",
    "font-size": 22,
    fill: C.green,
    opacity: settle
  }, root);

  roundRect(812, 430, 256, 58, 6, {
    fill: C.coralSoft,
    stroke: C.coral,
    "stroke-width": 2,
    opacity: settle
  }, root);
  roundRect(834, 462, laneScale(settle), 8, 4, { fill: C.coral, opacity: settle }, root);
  text(missOrigin.x, missOrigin.y, "FETCH ORIGIN", {
    "text-anchor": "middle",
    class: "label mono",
    "font-size": 22,
    fill: C.coral,
    opacity: settle
  }, root);
}

function drawSceneThree(local) {
  background(C.greenSoft);
  sceneLabel("GOLDEN / PROOF", "Before/after diff");
  svg.setAttribute("data-current-composition", "d3-composition-golden-root-before-after-bars");

  const draw = easeOut(local / 0.75);
  const fill = easeOut((local - 0.62) / 1.55);
  const lock = easeOut((local - 2.1) / 0.7);
  const proofPulse = 0.5 + 0.5 * Math.sin(local * Math.PI * 2.6);
  const root = group({
    "data-composition-id": "golden-root",
    "data-pattern-id": "d3-pattern-before-after-bars",
    "data-composition-pattern-id": "d3-composition-golden-root-before-after-bars"
  });

  roundRect(94, 190, 280, 330, 8, {
    fill: C.white,
    stroke: C.ink,
    "stroke-width": 2,
    opacity: draw
  }, root);
  text(130, 238, "37 ms", { class: "label mono", "font-size": 54, fill: C.green, opacity: fill }, root);
  text(132, 274, "latency improvement", {
    class: "small-label",
    "font-size": 18,
    opacity: fill
  }, root);
  text(130, 358, "cache hit rate", { class: "label mono", "font-size": 25, opacity: fill }, root);
  roundRect(132, 388, 190, 18, 4, { fill: C.hairline, opacity: fill }, root);
  roundRect(132, 388, d3.scaleLinear().domain([0, 1]).range([0, 190])(fill), 18, 4, {
    fill: C.teal,
    opacity: fill
  }, root);
  text(132, 454, "PROOF RAIL", {
    class: "small-label mono",
    "font-size": 16,
    opacity: 0.6 + lock * 0.4
  }, root);

  roundRect(440, 152, 720, 410, 8, {
    fill: C.white,
    stroke: C.ink,
    "stroke-width": 2.5,
    opacity: draw
  }, root);
  text(488, 210, "BEFORE", { class: "label mono", "font-size": 22, fill: C.muted, opacity: draw }, root);
  text(836, 210, "AFTER", { class: "label mono", "font-size": 22, fill: C.green, opacity: draw }, root);
  line(800, 184, 800, 530, { stroke: C.hairline, "stroke-width": 2, opacity: draw }, root);
  const diffCursor = easeInOut((local - 1.05) / 1.95);
  const cursorX = lerp(488, 1086, diffCursor);
  roundRect(cursorX - 18, 236, 36, 272, 0, {
    fill: C.yellow,
    opacity: 0.08 + lock * 0.08
  }, root);
  line(cursorX, 236, cursorX, 508, {
    stroke: C.yellow,
    "stroke-width": 3,
    opacity: 0.18 + lock * 0.34
  }, root);

  const rows = [
    { id: "p50", y: 258, before: 220, after: 134 },
    { id: "p75", y: 316, before: 176, after: 112 },
    { id: "p95", y: 374, before: 248, after: 156 },
    { id: "cold", y: 432, before: 206, after: 122 }
  ];
  const beforeScale = d3.scaleLinear().domain([0, 260]).range([0, 260]);
  const afterScale = d3.scaleLinear().domain([0, 260]).range([0, 260]);

  rows.forEach((row, i) => {
    const rowT = clamp((fill - i * 0.08) / 0.8);
    const beforeW = beforeScale(row.before) * rowT;
    const afterW = afterScale(row.after) * rowT;
    roundRect(494, row.y, beforeW, 24, 4, { fill: C.coral, opacity: 0.72 }, root);
    roundRect(846, row.y, afterW, 24, 4, { fill: C.green, opacity: 0.86 }, root);
    path(straightLine([
      { x: 494 + beforeW, y: row.y + 12 },
      { x: 804, y: row.y + 12 },
      { x: 846 + afterW, y: row.y + 12 }
    ]), {
      fill: "none",
      stroke: C.yellow,
      "stroke-width": 2,
      opacity: rowT * 0.42,
      "stroke-linecap": "round"
    }, root);
  });

  const bracket = [
    { x: 742, y: 376 },
    { x: 770, y: 360 - proofPulse * 8 },
    { x: 804, y: 360 - proofPulse * 8 },
    { x: 832, y: 376 }
  ];
  path(curveLine(bracket), {
    fill: "none",
    stroke: C.yellow,
    "stroke-width": 5,
    opacity: lock,
    "stroke-linecap": "round"
  }, root);
  circle(832, 376, 9 + lock * 3 + proofPulse * 2, { fill: C.yellow, opacity: lock }, root);
}

function drawSceneFour(local) {
  background(C.yellowSoft);
  svg.setAttribute("data-current-composition", "d3-composition-radial-rosette-rollout-checklist");
  const intro = easeOut(local / 0.8);
  const checks = easeOut((local - 0.68) / 1.45);
  const hold = easeOut((local - 2.0) / 0.8);
  const orbit = local * Math.PI * 1.35;
  const root = group({
    "data-composition-id": "radial-rosette",
    "data-pattern-id": "d3-pattern-rollout-checklist",
    "data-composition-pattern-id": "d3-composition-radial-rosette-rollout-checklist"
  });

  const center = { x: 640, y: 338 };
  const ringOuter = 176;
  const ringInner = 146;
  const items = [
    { id: "policy", label: "policy", color: C.teal, soft: C.tealSoft },
    { id: "hit-rate", label: "hit rate", color: C.green, soft: C.greenSoft },
    { id: "rollback", label: "rollback", color: C.coral, soft: C.coralSoft }
  ];
  const arcs = d3.pie().value(1).sort(null).padAngle(0.08)(items);
  const arcGen = d3.arc().innerRadius(ringInner).outerRadius(ringOuter);

  roundRect(442, 228, 396, 218, 8, {
    fill: C.white,
    stroke: C.ink,
    "stroke-width": 3,
    opacity: intro
  }, root);
  text(center.x, 310, "REVIEW", {
    "text-anchor": "middle",
    class: "label",
    "font-size": 76,
    opacity: intro,
    fill: C.ink
  }, root);
  text(center.x, 362, "ROLLOUT CHECKLIST", {
    "text-anchor": "middle",
    class: "label mono",
    "font-size": 30,
    opacity: intro,
    fill: C.teal
  }, root);

  arcs.forEach((arc, i) => {
    const t = clamp((checks - i * 0.18) / 0.62);
    const partialArc = {
      ...arc,
      endAngle: arc.startAngle + (arc.endAngle - arc.startAngle) * t
    };
    path(arcGen(partialArc), {
      transform: `translate(${center.x}, ${center.y})`,
      fill: items[i].soft,
      stroke: items[i].color,
      "stroke-width": 2,
      opacity: intro * (0.3 + t * 0.7)
    }, root);

    const angle = (arc.startAngle + arc.endAngle) / 2 - Math.PI / 2;
    const labelR = 226;
    const x = center.x + Math.cos(angle) * labelR;
    const y = center.y + Math.sin(angle) * labelR;
    circle(x, y, 17, {
      fill: C.white,
      stroke: items[i].color,
      "stroke-width": 3,
      opacity: t
    }, root);
    checkMark(x, y, 0.9, { stroke: items[i].color, opacity: t }, root);
    text(x, y + 44, items[i].label, {
      "text-anchor": "middle",
      class: "small-label mono",
      "font-size": 18,
      opacity: t
    }, root);
  });

  const orbitR = ringOuter + 19;
  const orbitX = center.x + Math.cos(orbit) * orbitR;
  const orbitY = center.y + Math.sin(orbit) * orbitR;
  circle(orbitX, orbitY, 7 + hold * 3, {
    fill: C.teal,
    opacity: 0.15 + hold * 0.75,
    stroke: C.white,
    "stroke-width": 3
  }, root);
  roundRect(458, 526, 364 * (0.4 + hold * 0.6), 8, 4, { fill: C.teal, opacity: 0.25 + hold * 0.5 }, root);
}

export function renderFrame(seconds) {
  const s = ((seconds % DURATION) + DURATION) % DURATION;
  clear();
  if (s < 3) drawSceneOne(s);
  else if (s < 6) drawSceneTwo(s - 3);
  else if (s < 9) drawSceneThree(s - 6);
  else drawSceneFour(s - 9);
  return {
    seconds: Number(s.toFixed(3)),
    scene:
      s < 3 ? "scene-01-hook" : s < 6 ? "scene-02-mechanism" : s < 9 ? "scene-03-proof" : "scene-04-cta",
    composition: svg.getAttribute("data-current-composition")
  };
}

window.renderFrame = renderFrame;
window.__sceneCompositionStyleTest = { duration: DURATION, renderFrame };

if (!new URLSearchParams(window.location.search).has("capture")) {
  const state = { seconds: 0 };
  animate(state, {
    seconds: DURATION,
    duration: DURATION * 1000,
    loop: true,
    ease: "linear",
    onUpdate: () => renderFrame(state.seconds)
  });
} else {
  renderFrame(0);
}

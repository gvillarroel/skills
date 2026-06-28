import { video } from "./video-data.js";

const W = video.width;
const H = video.height;
const svg = d3.select("#stage");

const palette = {
  bg: "#f6f7f9",
  ink: "#111827",
  muted: "#5b6472",
  panel: "#ffffff",
  panelAlt: "#eef2f7",
  line: "#cbd5e1",
  blue: "#2563eb",
  blueSoft: "#dbeafe",
  teal: "#0f766e",
  tealSoft: "#ccfbf1",
  amber: "#f59e0b",
  amberSoft: "#fef3c7",
  red: "#dc2626",
  redSoft: "#fee2e2",
  violet: "#7c3aed",
  violetSoft: "#ede9fe",
  green: "#16a34a",
  greenSoft: "#dcfce7"
};

const sceneBackgrounds = {
  "s01-model-vs-harness": "#f6f7f9",
  "s02-agent-loop": "#f4f7fb",
  "s03-coding-workflow": "#f5f8f7",
  "s04-boundaries-evidence": "#f7f7f6",
  "s05-closing-formula": "#f6f8f5"
};

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function smooth(value) {
  const x = clamp01(value);
  return x * x * (3 - 2 * x);
}

function lerp(a, b, t) {
  return a + (b - a) * clamp01(t);
}

function pulse(t, cycles = 1) {
  return (Math.sin(t * Math.PI * 2 * cycles) + 1) / 2;
}

function hexToRgb(hex) {
  const normalized = hex.replace("#", "");
  const value = Number.parseInt(normalized, 16);
  return {
    r: (value >> 16) & 255,
    g: (value >> 8) & 255,
    b: value & 255
  };
}

function rgba(hex, alpha) {
  const { r, g, b } = hexToRgb(hex);
  return `rgba(${r},${g},${b},${alpha})`;
}

function shotAt(seconds) {
  return video.shots.find((shot) => seconds >= shot.start && seconds < shot.start + shot.duration) ?? video.shots[video.shots.length - 1];
}

function backgroundFor(shot) {
  return sceneBackgrounds[shot.id] ?? palette.bg;
}

function localProgress(shot, seconds) {
  return clamp01((seconds - shot.start) / shot.duration);
}

function activeTransitionAt(seconds) {
  return video.transitions.find((transition) => seconds >= transition.start && seconds <= transition.start + transition.duration) ?? null;
}

function incomingTransitionFor(shot) {
  return video.transitions.find((transition) => transition.toScene === shot.id) ?? null;
}

function outgoingTransitionFor(shot) {
  return video.transitions.find((transition) => transition.fromScene === shot.id) ?? null;
}

function centerTransform(scale = 1, originX = W / 2, originY = H / 2, tx = 0, ty = 0) {
  return `translate(${W / 2 + tx},${H / 2 + ty}) scale(${scale}) translate(${-originX},${-originY})`;
}

function transformedForMechanic(transition, role, u) {
  if (transition.mechanic === "static-anchor-sweep") {
    return role === "outgoing"
      ? centerTransform(1, W / 2, H / 2, lerp(0, -W * 0.92, u), lerp(0, 28, u))
      : centerTransform(1, W / 2, H / 2, lerp(W * 0.92, 0, u), lerp(-28, 0, u));
  }

  if (transition.mechanic === "object-color-cover") {
    return role === "outgoing"
      ? centerTransform(lerp(1, 0.94, u), W / 2, H / 2, lerp(0, -84, u), 0)
      : centerTransform(lerp(1.06, 1, u), W / 2, H / 2, 0, lerp(54, 0, u));
  }

  if (transition.mechanic === "extreme-zoom-reframe") {
    if (role === "outgoing") {
      const originX = lerp(W / 2, transition.outgoing[0], u);
      const originY = lerp(H / 2, transition.outgoing[1], u);
      return centerTransform(lerp(1, 3.35, u), originX, originY);
    }
    const originX = lerp(transition.incoming[0], W / 2, u);
    const originY = lerp(transition.incoming[1], H / 2, u);
    return centerTransform(lerp(2.65, 1, u), originX, originY);
  }

  if (transition.mechanic === "full-screen-color-card") {
    return role === "outgoing"
      ? centerTransform(lerp(1, 0.9, u), W / 2, H / 2, 0, lerp(0, 24, u))
      : centerTransform(lerp(1.1, 1, u), W / 2, H / 2, 0, 0);
  }

  return null;
}

function cameraForShot(shot, seconds) {
  const incoming = incomingTransitionFor(shot);
  const outgoing = outgoingTransitionFor(shot);
  let scale = 1;
  let tx = 0;
  let ty = 0;

  if (incoming) {
    const boundary = shot.start;
    const post = incoming.start + incoming.duration - boundary;
    if (seconds >= boundary && seconds <= boundary + post) {
      const u = smooth((seconds - boundary) / Math.max(0.001, post));
      const transform = transformedForMechanic(incoming, "incoming", u);
      if (transform) return transform;
      scale = lerp(1.035, scale, u);
      tx += lerp(-(incoming.shift?.[0] ?? 0), 0, u);
      ty += lerp(-(incoming.shift?.[1] ?? 0), 0, u);
    }
  }

  if (outgoing) {
    const boundary = video.shots.find((candidate) => candidate.id === outgoing.toScene)?.start ?? (shot.start + shot.duration);
    const pre = boundary - outgoing.start;
    if (seconds >= outgoing.start && seconds < boundary) {
      const u = smooth((seconds - outgoing.start) / Math.max(0.001, pre));
      const transform = transformedForMechanic(outgoing, "outgoing", u);
      if (transform) return transform;
      scale = lerp(scale, 0.988, u);
      tx += lerp(0, outgoing.shift?.[0] ?? 0, u);
      ty += lerp(0, outgoing.shift?.[1] ?? 0, u);
    }
  }

  return centerTransform(scale, W / 2, H / 2, tx, ty);
}

function addDefs(root) {
  const defs = root.append("defs");

  const softShadow = defs.append("filter")
    .attr("id", "soft-shadow")
    .attr("x", "-20%")
    .attr("y", "-20%")
    .attr("width", "140%")
    .attr("height", "140%");
  softShadow.append("feDropShadow")
    .attr("dx", 0)
    .attr("dy", 12)
    .attr("stdDeviation", 16)
    .attr("flood-color", "#111827")
    .attr("flood-opacity", 0.12);

  const arrow = defs.append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 9)
    .attr("refY", 0)
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .attr("orient", "auto");
  arrow.append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", palette.blue);

  const arrowTeal = defs.append("marker")
    .attr("id", "arrow-teal")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 9)
    .attr("refY", 0)
    .attr("markerWidth", 8)
    .attr("markerHeight", 8)
    .attr("orient", "auto");
  arrowTeal.append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", palette.teal);
}

function baseFrame(root, shot, seconds) {
  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", backgroundFor(shot));

  root.append("path")
    .attr("d", "M0,608 C260,572 430,640 690,604 C910,574 1040,548 1280,584 L1280,720 L0,720 Z")
    .attr("fill", "#e8eef6")
    .attr("opacity", 0.65);

  root.append("text")
    .attr("class", "title")
    .attr("x", 70)
    .attr("y", 78)
    .attr("font-size", 44)
    .text(shot.headline);

  root.append("text")
    .attr("class", "subtitle")
    .attr("x", 72)
    .attr("y", 118)
    .attr("font-size", 24)
    .text(shot.subhead);
}

function rect(root, x, y, w, h, options = {}) {
  return root.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", options.rx ?? 8)
    .attr("fill", options.fill ?? palette.panel)
    .attr("stroke", options.stroke ?? palette.line)
    .attr("stroke-width", options.strokeWidth ?? 2)
    .attr("opacity", options.opacity ?? 1)
    .attr("filter", options.shadow ? "url(#soft-shadow)" : null);
}

function label(root, text, x, y, size = 20, options = {}) {
  return root.append("text")
    .attr("class", options.className ?? "small-label")
    .attr("x", x)
    .attr("y", y)
    .attr("font-size", size)
    .attr("font-weight", options.weight ?? null)
    .attr("text-anchor", options.anchor ?? "middle")
    .attr("fill", options.fill ?? null)
    .style("fill", options.fill ?? null)
    .text(text);
}

function multiline(root, lines, x, y, size = 24, lineHeight = 30, options = {}) {
  const text = root.append("text")
    .attr("x", x)
    .attr("y", y)
    .attr("font-size", size)
    .attr("font-weight", options.weight ?? 650)
    .attr("text-anchor", options.anchor ?? "middle")
    .attr("fill", options.fill ?? palette.ink)
    .attr("letter-spacing", 0);
  for (const [index, line] of lines.entries()) {
    text.append("tspan")
      .attr("x", x)
      .attr("dy", index === 0 ? 0 : lineHeight)
      .text(line);
  }
  return text;
}

function line(root, x1, y1, x2, y2, options = {}) {
  return root.append("line")
    .attr("x1", x1)
    .attr("y1", y1)
    .attr("x2", x2)
    .attr("y2", y2)
    .attr("stroke", options.stroke ?? palette.blue)
    .attr("stroke-width", options.width ?? 4)
    .attr("stroke-linecap", "round")
    .attr("opacity", options.opacity ?? 1)
    .attr("marker-end", options.arrow === false ? null : `url(#${options.marker ?? "arrow"})`);
}

function path(root, d, options = {}) {
  return root.append("path")
    .attr("d", d)
    .attr("fill", "none")
    .attr("stroke", options.stroke ?? palette.blue)
    .attr("stroke-width", options.width ?? 4)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", options.opacity ?? 1)
    .attr("marker-end", options.arrow === false ? null : `url(#${options.marker ?? "arrow"})`);
}

function packet(root, x, y, options = {}) {
  const g = root.append("g")
    .attr("transform", `translate(${x},${y})`)
    .attr("opacity", options.opacity ?? 1);
  g.append("rect")
    .attr("x", -22)
    .attr("y", -15)
    .attr("width", 44)
    .attr("height", 30)
    .attr("rx", 7)
    .attr("fill", options.fill ?? palette.amber)
    .attr("stroke", options.stroke ?? "#b45309")
    .attr("stroke-width", 2);
  g.append("circle")
    .attr("cx", -8)
    .attr("cy", 0)
    .attr("r", 4)
    .attr("fill", "#fff7ed");
  g.append("circle")
    .attr("cx", 8)
    .attr("cy", 0)
    .attr("r", 4)
    .attr("fill", "#fff7ed");
  return g;
}

function strokeForPacket(fill) {
  const strokes = {
    [palette.teal]: "#115e59",
    [palette.blue]: "#1d4ed8",
    [palette.red]: "#991b1b",
    [palette.green]: "#166534"
  };
  return strokes[fill] ?? "#92400e";
}

function interpolateBridge(transition, phase) {
  if (phase < 0.5) {
    const u = smooth(phase / 0.5);
    return [
      lerp(transition.outgoing[0], transition.bridge[0], u),
      lerp(transition.outgoing[1], transition.bridge[1], u)
    ];
  }
  const u = smooth((phase - 0.5) / 0.5);
  return [
    lerp(transition.bridge[0], transition.incoming[0], u),
    lerp(transition.bridge[1], transition.incoming[1], u)
  ];
}

function transitionCurve(source, target, bend = 42) {
  const controlX = source[0] < target[0]
    ? Math.max(source[0], target[0]) + bend
    : Math.min(source[0], target[0]) - bend;
  return `M${source[0]} ${source[1]} C${controlX} ${source[1]}, ${controlX} ${target[1]}, ${target[0]} ${target[1]}`;
}

function transitionSegmentPath(transition, phase, bend = 42) {
  const source = phase < 0.5 ? transition.outgoing : transition.bridge;
  const target = phase < 0.5 ? transition.bridge : transition.incoming;
  return transitionCurve(source, target, bend);
}

function drawArrivalRing(root, x, y, color, phase, radius = 42) {
  const land = smooth((phase - 0.56) / 0.36);
  root.append("circle")
    .attr("cx", x)
    .attr("cy", y)
    .attr("r", radius + land * 32)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", 4)
    .attr("opacity", 0.35 * land * (1 - smooth((phase - 0.86) / 0.12)));
}

function drawRibbon(root, transition, phase, options = {}) {
  const color = options.color ?? transition.color;
  const d = transitionSegmentPath(transition, phase, options.bend ?? 42);
  const opacity = 0.25 + 0.75 * Math.sin(Math.PI * phase);

  root.append("path")
    .attr("d", d)
    .attr("fill", "none")
    .attr("stroke", color)
    .attr("stroke-width", options.width ?? 8)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", (options.baseOpacity ?? 0.16) + (options.opacityBoost ?? 0.28) * opacity);

  root.append("path")
    .attr("d", d)
    .attr("fill", "none")
    .attr("stroke", options.secondaryColor ?? color)
    .attr("stroke-width", options.detailWidth ?? 2.5)
    .attr("stroke-linecap", "round")
    .attr("stroke-dasharray", options.dash ?? "10 12")
    .attr("opacity", (options.detailOpacity ?? 0.42) + 0.34 * opacity);
}

function drawPersistentFlight(root, transition, phase) {
  drawRibbon(root, transition, phase, {
    width: 9,
    color: transition.color,
    secondaryColor: transition.secondaryColor,
    bend: 64
  });
  const [px, py] = interpolateBridge(transition, phase);
  for (let i = 1; i <= 3; i += 1) {
    const echoPhase = clamp01(phase - i * 0.08);
    const [ex, ey] = interpolateBridge(transition, echoPhase);
    packet(root, ex, ey, {
      fill: transition.color,
      stroke: strokeForPacket(transition.color),
      opacity: Math.max(0, 0.22 - i * 0.045) * Math.sin(Math.PI * phase)
    });
  }
  drawArrivalRing(root, transition.incoming[0], transition.incoming[1], transition.color, phase);
  packet(root, px, py, {
    fill: transition.color,
    stroke: strokeForPacket(transition.color),
    opacity: 0.92
  });
}

function drawPortalPreview(root, transition, phase) {
  const portal = root.append("g").attr("opacity", 0.18 + 0.66 * Math.sin(Math.PI * phase));
  const width = lerp(68, 430, smooth((phase - 0.1) / 0.46));
  const height = lerp(86, 250, smooth((phase - 0.08) / 0.48));
  const cx = transition.bridge[0] - 34;
  const cy = transition.bridge[1] - 18;

  portal.append("ellipse")
    .attr("cx", cx)
    .attr("cy", cy)
    .attr("rx", width / 2)
    .attr("ry", height / 2)
    .attr("fill", transition.spaceColor)
    .attr("stroke", transition.color)
    .attr("stroke-width", 7)
    .attr("filter", "url(#soft-shadow)");

  for (let i = 0; i < 4; i += 1) {
    const x = cx - width * 0.34 + i * width * 0.22;
    portal.append("line")
      .attr("x1", x)
      .attr("y1", cy - height * 0.38)
      .attr("x2", x + width * 0.18)
      .attr("y2", cy + height * 0.36)
      .attr("stroke", transition.color)
      .attr("stroke-width", 3)
      .attr("opacity", 0.2 + i * 0.08);
  }

  for (let i = 0; i < 3; i += 1) {
    portal.append("rect")
      .attr("x", cx - width * 0.28 + i * width * 0.2)
      .attr("y", cy - height * 0.16 + i * 9)
      .attr("width", width * 0.18)
      .attr("height", height * 0.24)
      .attr("rx", 8)
      .attr("fill", "#ffffff")
      .attr("stroke", transition.secondaryColor)
      .attr("stroke-width", 2)
      .attr("opacity", 0.62);
  }
}

function drawSpatialPortal(root, transition, phase) {
  drawPortalPreview(root, transition, phase);
  drawRibbon(root, transition, phase, {
    width: 10,
    color: transition.color,
    secondaryColor: transition.secondaryColor,
    bend: 88,
    dash: "18 14",
    baseOpacity: 0.12
  });
  const [px, py] = interpolateBridge(transition, phase);
  const portalScale = 1 + 0.18 * Math.sin(Math.PI * phase);
  packet(root, px, py, {
    fill: transition.color,
    stroke: strokeForPacket(transition.color),
    opacity: 0.96
  }).attr("transform", `translate(${px},${py}) scale(${portalScale})`);
  drawArrivalRing(root, transition.incoming[0], transition.incoming[1], transition.color, phase, 36);
}

function drawInterruptGate(root, transition, phase, seconds) {
  const flash = Math.sin(Math.PI * phase);
  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.spaceColor)
    .attr("opacity", 0.06 + 0.16 * flash);

  const gateX = lerp(W + 40, 928, smooth((phase - 0.14) / 0.18));
  const shake = Math.sin(seconds * 76) * 5 * flash;
  const gate = root.append("g")
    .attr("transform", `translate(${shake},0)`)
    .attr("opacity", 0.16 + 0.84 * smooth((phase - 0.1) / 0.2));

  gate.append("line")
    .attr("x1", gateX)
    .attr("y1", 130)
    .attr("x2", gateX - 58)
    .attr("y2", 650)
    .attr("stroke", transition.color)
    .attr("stroke-width", 12)
    .attr("stroke-linecap", "round");
  gate.append("line")
    .attr("x1", gateX + 42)
    .attr("y1", 130)
    .attr("x2", gateX - 16)
    .attr("y2", 650)
    .attr("stroke", transition.secondaryColor)
    .attr("stroke-width", 5)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.75);

  drawRibbon(root, transition, phase, {
    width: 7,
    color: transition.color,
    secondaryColor: "#991b1b",
    bend: 24,
    dash: "5 8",
    baseOpacity: 0.12,
    opacityBoost: 0.38
  });
  const [baseX, baseY] = interpolateBridge(transition, phase);
  const snapped = smooth((phase - 0.44) / 0.2);
  const px = baseX + Math.sin(seconds * 58) * 7 * snapped;
  const py = baseY + Math.cos(seconds * 54) * 5 * snapped;
  for (let i = 0; i < 3; i += 1) {
    root.append("circle")
      .attr("cx", px)
      .attr("cy", py)
      .attr("r", 28 + i * 18 + 16 * snapped)
      .attr("fill", "none")
      .attr("stroke", transition.color)
      .attr("stroke-width", 3)
      .attr("opacity", (0.24 - i * 0.055) * snapped * (1 - smooth((phase - 0.84) / 0.1)));
  }
  packet(root, px, py, {
    fill: transition.color,
    stroke: strokeForPacket(transition.color),
    opacity: 0.95
  });
}

function drawMorphContinuity(root, transition, phase) {
  const [px, py] = interpolateBridge(transition, phase);
  const morph = smooth((phase - 0.28) / 0.48);
  const w = lerp(48, 178, morph);
  const h = lerp(32, 58, morph);
  const rx = lerp(8, 16, morph);
  const preview = smooth((phase - 0.5) / 0.22) * (1 - smooth((phase - 0.94) / 0.06));

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.spaceColor)
    .attr("opacity", 0.04 + 0.12 * Math.sin(Math.PI * phase));

  const ghost = root.append("g").attr("opacity", 0.42 * preview);
  const ghostTiles = [
    [116, "modelo"],
    [497, "harness"],
    [878, "ayudante"]
  ];
  for (const [x, text] of ghostTiles) {
    ghost.append("rect")
      .attr("x", x)
      .attr("y", 226)
      .attr("width", 286)
      .attr("height", 138)
      .attr("rx", 8)
      .attr("fill", "#ffffff")
      .attr("stroke", transition.color)
      .attr("stroke-width", 2.5);
    label(ghost, text, x + 143, 308, 25, { weight: 820, fill: palette.ink });
  }
  ghost.append("line")
    .attr("x1", 250)
    .attr("y1", 445)
    .attr("x2", 997)
    .attr("y2", 445)
    .attr("stroke", transition.color)
    .attr("stroke-width", 6)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.6);
  ghost.append("circle")
    .attr("cx", transition.incoming[0])
    .attr("cy", transition.incoming[1])
    .attr("r", 46)
    .attr("fill", transition.spaceColor)
    .attr("stroke", transition.color)
    .attr("stroke-width", 3);

  drawRibbon(root, transition, phase, {
    width: 8,
    color: transition.color,
    secondaryColor: transition.secondaryColor,
    bend: 36,
    dash: "24 10",
    baseOpacity: 0.1
  });

  const g = root.append("g")
    .attr("transform", `translate(${px},${py})`)
    .attr("opacity", 0.95);
  g.append("rect")
    .attr("x", -w / 2)
    .attr("y", -h / 2)
    .attr("width", w)
    .attr("height", h)
    .attr("rx", rx)
    .attr("fill", rgba(transition.color, 0.92))
    .attr("stroke", strokeForPacket(transition.color))
    .attr("stroke-width", 2.5);
  g.append("path")
    .attr("d", `M${-w * 0.22} 0 L${-w * 0.04} ${h * 0.18} L${w * 0.24} ${-h * 0.18}`)
    .attr("fill", "none")
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 4)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", smooth((phase - 0.5) / 0.24));
  drawArrivalRing(root, transition.incoming[0], transition.incoming[1], transition.color, phase, 48);
}

function drawStaticAnchorSweep(root, transition, phase) {
  const anchorOpacity = smooth(phase / 0.16) * (1 - smooth((phase - 0.78) / 0.1));
  const wipe = Math.sin(Math.PI * phase);
  const cleanPlate = smooth((phase - 0.02) / 0.1) * (1 - smooth((phase - 0.66) / 0.16));

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", "#f6f7f9")
    .attr("opacity", cleanPlate);

  const g = root.append("g").attr("opacity", anchorOpacity);

  g.append("rect")
    .attr("x", 260)
    .attr("y", 182)
    .attr("width", 760)
    .attr("height", 332)
    .attr("rx", 26)
    .attr("fill", "#f6f7f9")
    .attr("opacity", 1);

  g.append("rect")
    .attr("x", 260)
    .attr("y", 182)
    .attr("width", 760)
    .attr("height", 332)
    .attr("rx", 26)
    .attr("fill", "none")
    .attr("stroke", transition.color)
    .attr("stroke-width", 7)
    .attr("stroke-dasharray", "34 16")
    .attr("stroke-dashoffset", -phase * 120);
  label(g, "HARNESS", 640, 168, 28, { weight: 900, fill: transition.color });

  g.append("line")
    .attr("x1", 210)
    .attr("y1", 348)
    .attr("x2", 1070)
    .attr("y2", 348)
    .attr("stroke", transition.secondaryColor)
    .attr("stroke-width", 4)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.3 + 0.32 * wipe);

  root.append("rect")
    .attr("x", lerp(-340, 0, smooth(phase / 0.38)))
    .attr("y", 0)
    .attr("width", 460)
    .attr("height", H)
    .attr("fill", "#ffffff")
    .attr("opacity", Math.min(1, 1.12 * wipe));

  root.append("rect")
    .attr("x", lerp(W, W - 300, smooth((phase - 0.5) / 0.34)))
    .attr("y", 0)
    .attr("width", 300)
    .attr("height", H)
    .attr("fill", "#ffffff")
    .attr("opacity", 0.86 * wipe);
}

function drawObjectColorCover(root, transition, phase) {
  const coverIn = smooth(phase / 0.26);
  const reveal = smooth((phase - 0.48) / 0.3);
  const coverOpacity = coverIn * (1 - reveal);
  const radius = lerp(26, 1540, coverIn);

  root.append("circle")
    .attr("cx", transition.outgoing[0])
    .attr("cy", transition.outgoing[1])
    .attr("r", radius)
    .attr("fill", transition.color)
    .attr("opacity", Math.min(0.72, coverOpacity));

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.color)
    .attr("opacity", 0.74 * coverOpacity);

  const wordOpacity = smooth((phase - 0.18) / 0.1) * (1 - smooth((phase - 0.44) / 0.1));
  label(root, "ACCIÓN", W / 2, H / 2 + 18, 88, {
    weight: 930,
    fill: "#ffffff"
  }).attr("opacity", wordOpacity);

  root.append("line")
    .attr("x1", W / 2 - 210)
    .attr("y1", H / 2 + 56)
    .attr("x2", W / 2 + 210)
    .attr("y2", H / 2 + 56)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 8)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.55 * wordOpacity);

  const shutterOpacity = smooth((phase - 0.48) / 0.08) * (1 - smooth((phase - 0.84) / 0.08));
  const aperture = smooth((phase - 0.48) / 0.3);
  const gap = lerp(0, H * 0.82, aperture);
  const topHeight = Math.max(0, H / 2 - gap / 2);
  const bottomY = H / 2 + gap / 2;
  root.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", W)
    .attr("height", topHeight)
    .attr("fill", transition.color)
    .attr("opacity", 0.58 * shutterOpacity);
  root.append("rect")
    .attr("x", 0)
    .attr("y", bottomY)
    .attr("width", W)
    .attr("height", Math.max(0, H - bottomY))
    .attr("fill", transition.color)
    .attr("opacity", 0.58 * shutterOpacity);

  const laneCue = aperture * (1 - smooth((phase - 0.86) / 0.08));
  for (const y of [310, 372, 434]) {
    root.append("line")
      .attr("x1", lerp(W / 2 - 80, 104, aperture))
      .attr("y1", y)
      .attr("x2", lerp(W / 2 + 80, 1176, aperture))
      .attr("y2", y)
      .attr("stroke", transition.secondaryColor)
      .attr("stroke-width", 6)
      .attr("stroke-linecap", "round")
      .attr("opacity", 0.38 * laneCue);
  }
}

function drawCenterPortalReveal(root, transition, phase) {
  const open = smooth((phase - 0.08) / 0.34);
  const fade = 1 - smooth((phase - 0.82) / 0.12);
  const opacity = smooth(phase / 0.12) * fade;
  const portalX = lerp(510, 78, open);
  const portalY = lerp(332, 206, open);
  const portalW = lerp(260, 1124, open);
  const portalH = lerp(54, 278, open);
  const centerY = portalY + portalH / 2;

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.spaceColor)
    .attr("opacity", 0.12 * Math.sin(Math.PI * phase));

  const preview = root.append("g")
    .attr("opacity", 0.42 * open * (1 - smooth((phase - 0.56) / 0.12)));
  const previewCards = [
    [portalX + portalW * 0.12, "repo"],
    [portalX + portalW * 0.32, "editor"],
    [portalX + portalW * 0.52, "terminal"],
    [portalX + portalW * 0.72, "pruebas"]
  ];
  preview.append("line")
    .attr("x1", portalX + 56)
    .attr("y1", centerY)
    .attr("x2", portalX + portalW - 56)
    .attr("y2", centerY)
    .attr("stroke", transition.secondaryColor)
    .attr("stroke-width", 6)
    .attr("stroke-linecap", "round");
  for (const [x, text] of previewCards) {
    preview.append("rect")
      .attr("x", x - 66)
      .attr("y", centerY - 35)
      .attr("width", 132)
      .attr("height", 70)
      .attr("rx", 10)
      .attr("fill", "#ffffff")
      .attr("stroke", transition.color)
      .attr("stroke-width", 3);
    label(preview, text, x, centerY + 7, 20, { weight: 820, fill: palette.ink });
  }

  const portal = root.append("g").attr("opacity", opacity);
  portal.append("rect")
    .attr("x", portalX)
    .attr("y", portalY)
    .attr("width", portalW)
    .attr("height", portalH)
    .attr("rx", 24)
    .attr("fill", "#ffffff")
    .attr("opacity", 0.12);
  portal.append("rect")
    .attr("x", portalX)
    .attr("y", portalY)
    .attr("width", portalW)
    .attr("height", portalH)
    .attr("rx", 24)
    .attr("fill", "none")
    .attr("stroke", transition.color)
    .attr("stroke-width", 7)
    .attr("stroke-dasharray", "28 16")
    .attr("stroke-dashoffset", -phase * 148);
  portal.append("line")
    .attr("x1", portalX + 44)
    .attr("y1", centerY)
    .attr("x2", portalX + portalW - 44)
    .attr("y2", centerY)
    .attr("stroke", transition.secondaryColor)
    .attr("stroke-width", 8)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.54);
  label(portal, "ACCIÓN", portalX + portalW / 2, portalY - 22, 36, {
    weight: 900,
    fill: transition.color
  }).attr("opacity", 1 - smooth((phase - 0.58) / 0.18));
}

function drawExtremeZoomReframe(root, transition, phase) {
  const zoomIn = smooth(phase / 0.46);
  const redShift = smooth((phase - 0.48) / 0.24);
  const greenOpacity = zoomIn * (1 - smooth((phase - 0.58) / 0.2));
  const policyCard = smooth((phase - 0.5) / 0.12) * (1 - smooth((phase - 0.69) / 0.14));

  root.append("circle")
    .attr("cx", W / 2)
    .attr("cy", H / 2)
    .attr("r", lerp(52, 980, zoomIn))
    .attr("fill", palette.greenSoft)
    .attr("stroke", palette.green)
    .attr("stroke-width", lerp(5, 18, zoomIn))
    .attr("opacity", 0.14 + 0.34 * greenOpacity);

  root.append("path")
    .attr("d", `M${W / 2 - 96} ${H / 2} L${W / 2 - 22} ${H / 2 + 74} L${W / 2 + 118} ${H / 2 - 84}`)
    .attr("fill", "none")
    .attr("stroke", palette.green)
    .attr("stroke-width", lerp(10, 30, zoomIn))
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", greenOpacity);

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.spaceColor)
    .attr("opacity", 0.22 * redShift * (1 - smooth((phase - 0.84) / 0.1)));

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.color)
    .attr("opacity", 0.68 * policyCard);

  label(root, "POLÍTICA", W / 2, H / 2 + 20, 82, {
    weight: 930,
    fill: "#ffffff"
  }).attr("opacity", policyCard);

  root.append("line")
    .attr("x1", W / 2 - 220)
    .attr("y1", H / 2 + 58)
    .attr("x2", W / 2 + 220)
    .attr("y2", H / 2 + 58)
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 8)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.54 * policyCard);

  const gate = root.append("g").attr("opacity", redShift);
  for (const offset of [-52, 22]) {
    gate.append("line")
      .attr("x1", W / 2 + offset)
      .attr("y1", 86)
      .attr("x2", W / 2 + offset - 96)
      .attr("y2", 654)
      .attr("stroke", offset < 0 ? transition.color : transition.secondaryColor)
      .attr("stroke-width", offset < 0 ? 15 : 7)
      .attr("stroke-linecap", "round");
  }
}

function drawFullScreenColorCard(root, transition, phase) {
  const coverIn = smooth(phase / 0.3);
  const coverOut = smooth((phase - 0.56) / 0.22);
  const opacity = coverIn * (1 - coverOut);

  root.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", transition.color)
    .attr("opacity", 0.9 * opacity);

  const wordOpacity = smooth((phase - 0.18) / 0.16) * (1 - smooth((phase - 0.58) / 0.14));
  label(root, "VALIDADO", W / 2, H / 2 + 20, 84, {
    weight: 930,
    fill: "#ffffff"
  }).attr("opacity", wordOpacity);

  root.append("path")
    .attr("d", `M${W / 2 - 150} ${H / 2 + 72} L${W / 2 - 54} ${H / 2 + 142} L${W / 2 + 158} ${H / 2 - 88}`)
    .attr("fill", "none")
    .attr("stroke", "#ffffff")
    .attr("stroke-width", 18)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", 0.38 * wordOpacity);

  const white = smooth((phase - 0.64) / 0.22);
  root.append("rect")
    .attr("x", W / 2 - (W * white) / 2)
    .attr("y", H / 2 - (H * white) / 2)
    .attr("width", W * white)
    .attr("height", H * white)
    .attr("fill", "#f6f8f5")
    .attr("opacity", 0.96 * white * (1 - smooth((phase - 0.94) / 0.06)));

  const formulaPreview = smooth((phase - 0.74) / 0.16) * (1 - smooth((phase - 0.96) / 0.05));
  const preview = root.append("g").attr("opacity", 0.48 * formulaPreview);
  const tiles = [
    [116, "modelo"],
    [497, "harness"],
    [878, "ayudante"]
  ];
  for (const [x, text] of tiles) {
    preview.append("rect")
      .attr("x", x)
      .attr("y", 226)
      .attr("width", 286)
      .attr("height", 138)
      .attr("rx", 8)
      .attr("fill", "#ffffff")
      .attr("stroke", transition.color)
      .attr("stroke-width", 3);
    label(preview, text, x + 143, 308, 25, { weight: 820, fill: palette.ink });
  }
}

function drawTransitionOverlay(root, seconds) {
  const transition = activeTransitionAt(seconds);
  if (!transition) return;

  const phase = clamp01((seconds - transition.start) / transition.duration);

  if (transition.mechanic === "static-anchor-sweep") {
    drawStaticAnchorSweep(root, transition, phase);
  } else if (transition.mechanic === "object-color-cover") {
    drawObjectColorCover(root, transition, phase);
  } else if (transition.mechanic === "center-portal-reveal") {
    drawCenterPortalReveal(root, transition, phase);
  } else if (transition.mechanic === "extreme-zoom-reframe") {
    drawExtremeZoomReframe(root, transition, phase);
  } else if (transition.mechanic === "full-screen-color-card") {
    drawFullScreenColorCard(root, transition, phase);
  } else if (transition.mechanic === "spatial-portal-reveal") {
    drawSpatialPortal(root, transition, phase);
  } else if (transition.mechanic === "interrupt-gate-snap") {
    drawInterruptGate(root, transition, phase, seconds);
  } else if (transition.mechanic === "morph-continuity") {
    drawMorphContinuity(root, transition, phase);
  } else {
    drawPersistentFlight(root, transition, phase);
  }
}

function drawModule(root, x, y, text, fill, stroke, enter = 1) {
  const dy = (1 - smooth(enter)) * 24;
  const g = root.append("g").attr("transform", `translate(${x},${y + dy})`).attr("opacity", smooth(enter));
  rect(g, -74, -33, 148, 66, { fill, stroke, shadow: true });
  label(g, text, 0, 7, 19, { weight: 760 });
  return g;
}

function drawModelCore(root, cx, cy, r, p, active = 0) {
  const g = root.append("g")
    .attr("transform", `translate(${cx},${cy}) scale(${lerp(0.88, 1, smooth(p))})`)
    .attr("opacity", smooth(p));
  g.append("circle")
    .attr("r", r)
    .attr("fill", palette.violetSoft)
    .attr("stroke", palette.violet)
    .attr("stroke-width", 4)
    .attr("filter", "url(#soft-shadow)");
  const nodes = [
    [-36, -20], [0, -34], [38, -18], [-28, 24], [20, 26], [0, 0]
  ];
  for (let i = 0; i < nodes.length - 1; i += 1) {
    for (let j = i + 1; j < nodes.length; j += 2) {
      g.append("line")
        .attr("x1", nodes[i][0])
        .attr("y1", nodes[i][1])
        .attr("x2", nodes[j][0])
        .attr("y2", nodes[j][1])
        .attr("stroke", palette.violet)
        .attr("stroke-width", 2)
        .attr("opacity", 0.25 + 0.25 * pulse(active + i * 0.12));
    }
  }
  for (const [i, node] of nodes.entries()) {
    g.append("circle")
      .attr("cx", node[0])
      .attr("cy", node[1])
      .attr("r", 8 + 3 * pulse(active + i * 0.17))
      .attr("fill", palette.violet)
      .attr("opacity", 0.76);
  }
  label(g, "MODELO", 0, r + 44, 24, { weight: 820, fill: palette.ink });
  return g;
}

function drawScene1(root, seconds, shot, p) {
  const harness = smooth((p - 0.22) / 0.28);
  const modules = smooth((p - 0.38) / 0.24);
  const route = smooth((p - 0.58) / 0.32);

  drawModelCore(root, 640, 363, 92, p / 0.28, seconds);

  const frame = rect(root, 292, 205, 696, 288, {
    rx: 18,
    fill: "#ffffff",
    stroke: palette.teal,
    strokeWidth: 5,
    opacity: 0.12 + 0.88 * harness,
    shadow: true
  });
  frame.attr("stroke-dasharray", 1900)
    .attr("stroke-dashoffset", 1900 * (1 - harness));

  label(root, "HARNESS", 640, 194, 26, { weight: 860, fill: palette.teal });
  drawModule(root, 390, 258, "herramientas", palette.blueSoft, palette.blue, modules);
  drawModule(root, 890, 258, "memoria", palette.amberSoft, palette.amber, modules - 0.12);
  drawModule(root, 390, 448, "políticas", palette.redSoft, palette.red, modules - 0.2);
  drawModule(root, 890, 448, "pruebas", palette.greenSoft, palette.green, modules - 0.28);

  line(root, 465, 258, 548, 315, { opacity: 0.35 + 0.45 * modules, arrow: false, stroke: palette.line, width: 3 });
  line(root, 815, 258, 732, 315, { opacity: 0.35 + 0.45 * modules, arrow: false, stroke: palette.line, width: 3 });
  line(root, 465, 448, 548, 410, { opacity: 0.35 + 0.45 * modules, arrow: false, stroke: palette.line, width: 3 });
  line(root, 815, 448, 732, 410, { opacity: 0.35 + 0.45 * modules, arrow: false, stroke: palette.line, width: 3 });

  const px = lerp(160, 1120, route);
  const py = 352 + Math.sin(route * Math.PI) * -24;
  path(root, "M165 352 C330 320 430 352 540 352 C680 352 730 352 860 352 C980 352 1050 352 1120 352", {
    opacity: 0.22 + 0.45 * route,
    width: 5
  });
  packet(root, px, py, { opacity: route });
  rect(root, 82, 318, 126, 68, { fill: palette.amberSoft, stroke: palette.amber, opacity: 0.9 });
  label(root, "tarea", 145, 358, 23, { weight: 820 });
  rect(root, 1070, 318, 132, 68, { fill: palette.greenSoft, stroke: palette.green, opacity: 0.25 + 0.75 * route });
  label(root, "patch", 1136, 358, 23, { weight: 820 });

  const calloutOpacity = smooth((p - 0.72) / 0.18);
  multiline(root, ["El harness es el sistema", "que controla cómo opera."], 640, 570, 30, 36, {
    weight: 780,
    fill: palette.ink
  }).attr("opacity", calloutOpacity);
}

function loopPoint(t) {
  const points = [
    [420, 325],
    [640, 238],
    [860, 325],
    [640, 455]
  ];
  const scaled = (t % 1) * points.length;
  const i = Math.floor(scaled);
  const j = (i + 1) % points.length;
  const f = smooth(scaled - i);
  return [lerp(points[i][0], points[j][0], f), lerp(points[i][1], points[j][1], f)];
}

function drawLoopNode(root, x, y, text, color, active) {
  const g = root.append("g").attr("transform", `translate(${x},${y})`);
  g.append("circle")
    .attr("r", 60 + 7 * active)
    .attr("fill", color.soft)
    .attr("stroke", color.main)
    .attr("stroke-width", 4);
  label(g, text, 0, 8, 22, { weight: 820, fill: palette.ink });
  return g;
}

function drawTraceCard(root, x, y, text, index, show) {
  const g = root.append("g")
    .attr("transform", `translate(${x},${y + (1 - show) * 24})`)
    .attr("opacity", show);
  rect(g, 0, 0, 194, 44, { fill: "#ffffff", stroke: palette.line, rx: 7 });
  g.append("circle").attr("cx", 22).attr("cy", 22).attr("r", 8).attr("fill", [palette.blue, palette.amber, palette.teal, palette.green][index % 4]);
  label(g, text, 108, 28, 16, { anchor: "middle", weight: 680, fill: palette.ink });
}

function drawScene2(root, seconds, shot, p) {
  const colors = [
    { main: palette.blue, soft: palette.blueSoft },
    { main: palette.amber, soft: palette.amberSoft },
    { main: palette.teal, soft: palette.tealSoft },
    { main: palette.green, soft: palette.greenSoft }
  ];

  path(root, "M420 325 C470 225 590 210 640 238 C720 195 825 235 860 325 C905 405 725 480 640 455 C555 482 375 405 420 325", {
    width: 5,
    opacity: 0.5,
    stroke: palette.blue,
    marker: "arrow"
  });

  const loop = ((seconds - shot.start) / 2.8) % 1;
  const activeIndex = Math.floor(loop * 4);
  drawLoopNode(root, 420, 325, "observar", colors[0], activeIndex === 0 ? 1 : 0);
  drawLoopNode(root, 640, 238, "decidir", colors[1], activeIndex === 1 ? 1 : 0);
  drawLoopNode(root, 860, 325, "actuar", colors[2], activeIndex === 2 ? 1 : 0);
  drawLoopNode(root, 640, 455, "verificar", colors[3], activeIndex === 3 ? 1 : 0);

  for (let k = 0; k < 3; k += 1) {
    const [x, y] = loopPoint(loop + k * 0.12);
    packet(root, x, y, {
      fill: [palette.amber, palette.blue, palette.teal][k],
      opacity: 0.85 - k * 0.18
    });
  }

  rect(root, 930, 223, 230, 270, { fill: "#ffffff", stroke: palette.line, shadow: true });
  label(root, "trazas", 1045, 260, 26, { weight: 860, fill: palette.ink });
  const traces = ["prompt", "acción", "salida", "veredicto"];
  for (let i = 0; i < traces.length; i += 1) {
    drawTraceCard(root, 948, 287 + i * 52, traces[i], i, smooth((p - 0.12 - i * 0.13) / 0.12));
  }

  rect(root, 116, 268, 214, 132, { fill: palette.violetSoft, stroke: palette.violet, shadow: true });
  multiline(root, ["un agente", "no adivina", "a ciegas"], 223, 308, 24, 31, { weight: 780 });
  line(root, 330, 334, 354, 334, { stroke: palette.violet, marker: "arrow", opacity: 0.7 });

  multiline(root, ["Cada vuelta agrega", "observación y decisión."], 640, 574, 30, 36, {
    weight: 780,
    fill: palette.ink
  }).attr("opacity", smooth((p - 0.68) / 0.18));
}

function drawToolPanel(root, x, y, w, h, title, fill, stroke, lines, show) {
  const g = root.append("g")
    .attr("transform", `translate(${x},${y + (1 - show) * 18})`)
    .attr("opacity", show);
  rect(g, 0, 0, w, h, { fill, stroke, shadow: true, strokeWidth: 3 });
  g.append("circle")
    .attr("cx", 34)
    .attr("cy", 36)
    .attr("r", 14)
    .attr("fill", stroke)
    .attr("opacity", 0.84);
  label(g, title, w / 2 + 16, 43, 25, { weight: 860, fill: palette.ink });
  for (const [i, row] of lines.entries()) {
    g.append("rect")
      .attr("x", 28)
      .attr("y", 74 + i * 26)
      .attr("width", row.w)
      .attr("height", 12)
      .attr("rx", 6)
      .attr("fill", row.color ?? stroke)
      .attr("opacity", row.opacity ?? 0.65);
  }
  return g;
}

function pointOnPolyline(points, t) {
  const lengths = [];
  let total = 0;
  for (let i = 0; i < points.length - 1; i += 1) {
    const dx = points[i + 1][0] - points[i][0];
    const dy = points[i + 1][1] - points[i][1];
    const len = Math.hypot(dx, dy);
    lengths.push(len);
    total += len;
  }
  let distance = clamp01(t) * total;
  for (let i = 0; i < lengths.length; i += 1) {
    if (distance <= lengths[i]) {
      const f = distance / lengths[i];
      return [lerp(points[i][0], points[i + 1][0], f), lerp(points[i][1], points[i + 1][1], f)];
    }
    distance -= lengths[i];
  }
  return points[points.length - 1];
}

function drawScene3(root, seconds, shot, p) {
  const panels = [
    { x: 235, y: 232, title: "repo", fill: palette.blueSoft, stroke: palette.blue, lines: [{ w: 140 }, { w: 104 }, { w: 160 }] },
    { x: 478, y: 232, title: "editor", fill: palette.violetSoft, stroke: palette.violet, lines: [{ w: 152, color: palette.green }, { w: 112, color: palette.red }, { w: 132 }] },
    { x: 721, y: 232, title: "terminal", fill: "#e5e7eb", stroke: "#4b5563", lines: [{ w: 138 }, { w: 170 }, { w: 104 }] },
    { x: 964, y: 232, title: "pruebas", fill: palette.greenSoft, stroke: palette.green, lines: [{ w: 154 }, { w: 126 }, { w: 170 }] }
  ];

  rect(root, 76, 346, 168, 104, { fill: palette.amberSoft, stroke: palette.amber, shadow: true, strokeWidth: 3 });
  multiline(root, ["tarea", "arreglar bug"], 160, 386, 24, 30, { weight: 840 });

  for (const [i, panel] of panels.entries()) {
    drawToolPanel(root, panel.x, panel.y, 198, 158, panel.title, panel.fill, panel.stroke, panel.lines, smooth((p - 0.08 - i * 0.08) / 0.12));
    if (i < panels.length - 1) {
      line(root, panel.x + 199, panel.y + 79, panels[i + 1].x - 10, panels[i + 1].y + 79, {
        stroke: palette.blue,
        width: 6,
        opacity: 0.35 + 0.45 * smooth((p - 0.18 - i * 0.1) / 0.14)
      });
    }
  }

  const routePoints = [
    [244, 398],
    [286, 311],
    [577, 311],
    [820, 311],
    [1063, 311],
    [1115, 445]
  ];
  const d = `M${routePoints.map((pt) => pt.join(" ")).join(" L")}`;
  path(root, d, { stroke: palette.teal, marker: "arrow-teal", width: 7, opacity: 0.32 + 0.5 * p });
  const [px, py] = pointOnPolyline(routePoints, smooth((p - 0.12) / 0.62));
  packet(root, px, py, { fill: palette.teal, stroke: "#115e59", opacity: smooth((p - 0.08) / 0.14) });

  rect(root, 1018, 414, 190, 96, { fill: palette.greenSoft, stroke: palette.green, shadow: true, opacity: 0.95, strokeWidth: 3 });
  label(root, "patch", 1113, 456, 30, { weight: 880, fill: palette.ink });
  label(root, "validado", 1113, 486, 21, { weight: 800, fill: palette.green });

  const checkP = smooth((p - 0.72) / 0.18);
  root.append("circle")
    .attr("cx", 1008)
    .attr("cy", 407)
    .attr("r", 35 + 5 * pulse(seconds))
    .attr("fill", palette.greenSoft)
    .attr("stroke", palette.green)
    .attr("stroke-width", 4)
    .attr("opacity", checkP);
  root.append("path")
    .attr("d", "M991 407 L1004 421 L1028 391")
    .attr("fill", "none")
    .attr("stroke", palette.green)
    .attr("stroke-width", 6)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", checkP);

  const evidence = smooth((p - 0.44) / 0.22);
  rect(root, 348, 448, 580, 52, { fill: "#ffffff", stroke: palette.line, opacity: evidence });
  label(root, "evidencia: contexto + diff + salida de comandos + pruebas", 638, 482, 22, {
    weight: 760,
    fill: palette.ink
  }).attr("opacity", evidence);

  multiline(root, ["No solo responde:", "usa herramientas y comprueba."], 640, 590, 32, 38, {
    weight: 780,
    fill: palette.ink
  }).attr("opacity", smooth((p - 0.66) / 0.18));
}

function drawChecklist(root, x, y, items, show) {
  const g = root.append("g")
    .attr("transform", `translate(${x},${y})`)
    .attr("opacity", show);
  for (const [i, item] of items.entries()) {
    const yy = i * 48;
    g.append("rect")
      .attr("x", 0)
      .attr("y", yy)
      .attr("width", 30)
      .attr("height", 30)
      .attr("rx", 6)
      .attr("fill", item.colorSoft)
      .attr("stroke", item.color)
      .attr("stroke-width", 2);
    g.append("path")
      .attr("d", `M8 ${yy + 15} L14 ${yy + 22} L24 ${yy + 9}`)
      .attr("fill", "none")
      .attr("stroke", item.color)
      .attr("stroke-width", 4)
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round");
    label(g, item.text, 50, yy + 22, 21, { anchor: "start", weight: 740, fill: palette.ink });
  }
  return g;
}

function drawScene4(root, seconds, shot, p) {
  rect(root, 92, 190, 490, 354, { fill: "#ffffff", stroke: "#d1d5db", shadow: true });
  rect(root, 698, 190, 490, 354, { fill: "#ffffff", stroke: palette.teal, strokeWidth: 4, shadow: true });
  label(root, "solo modelo", 337, 238, 30, { weight: 860, fill: palette.ink });
  label(root, "modelo + harness", 943, 238, 30, { weight: 860, fill: palette.teal });

  drawModelCore(root, 337, 328, 62, 1, seconds);
  rect(root, 210, 468, 254, 58, { fill: "#f3f4f6", stroke: "#d1d5db" });
  label(root, "respuesta sin prueba", 337, 504, 22, { weight: 760, fill: palette.muted });
  line(root, 337, 427, 337, 462, { stroke: "#9ca3af", width: 4, marker: "arrow", opacity: 0.7 });
  root.append("path")
    .attr("d", "M482 304 L532 350 L482 396")
    .attr("fill", "none")
    .attr("stroke", palette.red)
    .attr("stroke-width", 9)
    .attr("stroke-linecap", "round")
    .attr("stroke-linejoin", "round")
    .attr("opacity", smooth((p - 0.26) / 0.14));
  label(root, "sin trazas ni evaluación", 337, 572, 24, { weight: 820, fill: palette.red });

  const chassis = rect(root, 778, 270, 330, 260, {
    fill: palette.tealSoft,
    stroke: palette.teal,
    strokeWidth: 4
  });
  chassis.attr("opacity", 0.95);
  label(root, "harness", 943, 312, 28, { weight: 880, fill: palette.teal });
  drawChecklist(root, 818, 346, [
    { text: "sandbox", color: palette.red, colorSoft: palette.redSoft },
    { text: "permisos", color: palette.amber, colorSoft: palette.amberSoft },
    { text: "trazas", color: palette.blue, colorSoft: palette.blueSoft },
    { text: "evaluación", color: palette.green, colorSoft: palette.greenSoft }
  ], smooth((p - 0.18) / 0.25));

  const risky = smooth((p - 0.33) / 0.25);
  const xRisk = lerp(660, 792, risky);
  rect(root, xRisk, 544, 210, 54, { fill: palette.redSoft, stroke: palette.red, opacity: 0.94, strokeWidth: 3 });
  label(root, "acción riesgosa", xRisk + 105, 578, 21, { weight: 820, fill: palette.red });
  root.append("line")
    .attr("x1", 902)
    .attr("y1", 530)
    .attr("x2", 902)
    .attr("y2", 606)
    .attr("stroke", palette.red)
    .attr("stroke-width", 7)
    .attr("opacity", smooth((p - 0.42) / 0.12));
  label(root, "bloqueada", 986, 623, 24, { weight: 860, fill: palette.red }).attr("opacity", smooth((p - 0.46) / 0.14));

  const stamp = smooth((p - 0.62) / 0.2);
  rect(root, 1026, 538, 150, 58, { fill: palette.blueSoft, stroke: palette.blue, opacity: stamp, strokeWidth: 3 });
  label(root, "traza", 1101, 574, 23, { weight: 860, fill: palette.blue }).attr("opacity", stamp);
  rect(root, 1026, 604, 150, 58, { fill: palette.greenSoft, stroke: palette.green, opacity: stamp, strokeWidth: 3 });
  label(root, "eval OK", 1101, 640, 23, { weight: 860, fill: palette.green }).attr("opacity", stamp);

}

function drawFormulaTile(root, x, y, w, h, title, subtitle, fill, stroke, show) {
  const g = root.append("g")
    .attr("transform", `translate(${x},${y + (1 - show) * 24})`)
    .attr("opacity", show);
  rect(g, 0, 0, w, h, { fill, stroke, strokeWidth: 3, shadow: true });
  label(g, title, w / 2, 48, 28, { weight: 880, fill: palette.ink });
  label(g, subtitle, w / 2, 86, 19, { weight: 650, fill: palette.muted });
  return g;
}

function drawScene5(root, seconds, shot, p) {
  const a = smooth((p - 0.04) / 0.16);
  const b = smooth((p - 0.18) / 0.16);
  const c = smooth((p - 0.44) / 0.18);
  drawFormulaTile(root, 116, 226, 286, 138, "modelo", "razona y genera", palette.violetSoft, palette.violet, a);
  drawFormulaTile(root, 497, 226, 286, 138, "harness", "opera y verifica", palette.tealSoft, palette.teal, b);
  drawFormulaTile(root, 878, 226, 286, 138, "ayudante", "trabaja en el repo", palette.greenSoft, palette.green, c);

  label(root, "+", 450, 306, 58, { weight: 900, fill: palette.ink }).attr("opacity", Math.min(a, b));
  line(root, 801, 295, 858, 295, { stroke: palette.green, marker: "arrow-teal", opacity: c, width: 7 });

  const lanes = [
    ["objetivo", palette.amber, 250],
    ["acciones", palette.blue, 445],
    ["observación", palette.teal, 640],
    ["validación", palette.green, 835]
  ];
  for (const [i, lane] of lanes.entries()) {
    const show = smooth((p - 0.42 - i * 0.06) / 0.12);
    rect(root, lane[2], 414, 162, 62, { fill: "#ffffff", stroke: lane[1], opacity: show, strokeWidth: 3 });
    label(root, lane[0], lane[2] + 81, 453, 21, { weight: 800, fill: palette.ink }).attr("opacity", show);
    if (i < lanes.length - 1) {
      line(root, lane[2] + 163, 445, lanes[i + 1][2] - 10, 445, { stroke: palette.line, marker: "arrow", opacity: 0.45 * show, width: 4 });
    }
  }

  const finalShow = smooth((p - 0.62) / 0.16);
  rect(root, 132, 530, 1016, 98, { fill: "#ffffff", stroke: palette.teal, shadow: true, opacity: finalShow, strokeWidth: 3 });
  multiline(root, ["El harness es el sistema de ejecución", "que permite al agente actuar con controles y pruebas."], 640, 570, 31, 38, {
    weight: 820,
    fill: palette.ink
  }).attr("opacity", finalShow);

  packet(root, lerp(183, 1096, smooth((p - 0.28) / 0.42)), 394 + Math.sin(p * Math.PI * 4) * 6, {
    fill: palette.amber,
    opacity: smooth((p - 0.24) / 0.12) * (1 - smooth((p - 0.78) / 0.12))
  });
}

const sceneRenderers = {
  "s01-model-vs-harness": drawScene1,
  "s02-agent-loop": drawScene2,
  "s03-coding-workflow": drawScene3,
  "s04-boundaries-evidence": drawScene4,
  "s05-closing-formula": drawScene5
};

function render(seconds) {
  const clampedSeconds = Math.max(0, Math.min(video.durationSeconds - 0.001, seconds));
  const shot = shotAt(clampedSeconds);
  const p = localProgress(shot, clampedSeconds);
  svg.selectAll("*").remove();
  addDefs(svg);
  svg.append("rect")
    .attr("width", W)
    .attr("height", H)
    .attr("fill", backgroundFor(shot));
  const sceneLayer = svg.append("g")
    .attr("transform", cameraForShot(shot, clampedSeconds));
  baseFrame(sceneLayer, shot, clampedSeconds);
  sceneRenderers[shot.id](sceneLayer, clampedSeconds, shot, p);
  drawTransitionOverlay(svg, clampedSeconds);
  return {
    videoId: video.id,
    seconds: Number(clampedSeconds.toFixed(3)),
    shotId: shot.id,
    transitionId: activeTransitionAt(clampedSeconds)?.id ?? null,
    progress: Number(p.toFixed(3)),
    labels: shot.labels
  };
}

window.renderConceptFrame = (conceptId, seconds) => {
  if (conceptId !== video.id) {
    throw new Error(`Unknown concept: ${conceptId}`);
  }
  return render(seconds);
};

const params = new URLSearchParams(window.location.search);
const initialSeconds = Number(params.get("t") ?? "0");
render(Number.isFinite(initialSeconds) ? initialSeconds : 0);

if (params.get("preview") === "1") {
  const started = performance.now();
  d3.timer(() => {
    const elapsed = ((performance.now() - started) / 1000) % video.durationSeconds;
    render(elapsed);
  });
}

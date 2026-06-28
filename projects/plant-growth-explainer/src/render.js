import { video } from "./video-data.js";

const d3 = window.d3;
const svg = d3.select("#stage");

const palette = {
  bg: "#f7f7f7",
  ink: "#333e48",
  muted: "#696969",
  grid: "#e7e7e7",
  soil: "#e7e7e7",
  soilDark: "#cfcfcf",
  seed: "#f1c319",
  seedStroke: "#98700c",
  root: "#e77204",
  rootDark: "#994a00",
  plant: "#45842a",
  plantDark: "#294d19",
  leaf: "#6fbf52",
  leafLight: "#dbffcc",
  water: "#007298",
  waterLight: "#cdf3ff",
  light: "#f1c319",
  air: "#00ace6",
  mineral: "#652f6c",
  mineralAlt: "#9e1b32",
  sugar: "#652f6c",
  sugarLight: "#f9ccff",
  oxygen: "#00ace6",
  white: "#ffffff"
};

function clamp(value, min = 0, max = 1) {
  return Math.max(min, Math.min(max, value));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function smooth(t) {
  const x = clamp(t);
  return x * x * (3 - 2 * x);
}

function easeOut(t) {
  return 1 - Math.pow(1 - clamp(t), 3);
}

function easeInOut(t) {
  const x = clamp(t);
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}

function pulse(t, cycles = 1) {
  return 0.5 + 0.5 * Math.sin(clamp(t) * Math.PI * 2 * cycles - Math.PI / 2);
}

function local(seconds, shot) {
  return clamp((seconds - shot.start) / shot.duration);
}

function clear() {
  svg.selectAll("*").remove();
  svg.attr("viewBox", `0 0 ${video.width} ${video.height}`);
}

function addBackground(g, seconds) {
  g.append("rect")
    .attr("width", video.width)
    .attr("height", video.height)
    .attr("fill", palette.bg);

  const grid = g.append("g").attr("opacity", 0.36);
  for (let x = 80; x < video.width; x += 80) {
    grid.append("line")
      .attr("x1", x)
      .attr("x2", x)
      .attr("y1", 48)
      .attr("y2", video.height - 48)
      .attr("stroke", palette.grid)
      .attr("stroke-width", 1);
  }
  for (let y = 80; y < video.height; y += 80) {
    grid.append("line")
      .attr("x1", 56)
      .attr("x2", video.width - 56)
      .attr("y1", y)
      .attr("y2", y)
      .attr("stroke", palette.grid)
      .attr("stroke-width", 1);
  }

  const title = g.append("g").attr("transform", "translate(64 48)");
  title.append("text")
    .attr("class", "small-label")
    .attr("font-size", 18)
    .attr("fill", palette.muted)
    .text(video.title);

  const tick = ((seconds * 0.18) % 1) * 240;
  g.append("path")
    .attr("d", `M${940 + tick} 52 C${990 + tick} 32 ${1030 + tick} 72 ${1080 + tick} 52`)
    .attr("fill", "none")
    .attr("stroke", palette.grid)
    .attr("stroke-width", 2)
    .attr("opacity", 0.32);
}

function label(g, text, x, y, size = 22, anchor = "middle", fill = palette.ink) {
  const parent = size >= 30 ? svg : g;
  return parent.append("text")
    .attr("class", size <= 16 ? "micro-label" : "label")
    .attr("x", x)
    .attr("y", y)
    .attr("text-anchor", anchor)
    .attr("font-size", size)
    .attr("paint-order", "stroke")
    .attr("stroke", palette.bg)
    .attr("stroke-width", size >= 30 ? 8 : 4)
    .attr("stroke-linejoin", "round")
    .attr("fill", fill)
    .text(text);
}

function roundedLabel(g, text, x, y, fill, stroke = "none", size = 17) {
  const node = g.append("g").attr("transform", `translate(${x} ${y})`);
  const width = Math.max(54, text.length * size * 0.55 + 24);
  node.append("rect")
    .attr("x", -width / 2)
    .attr("y", -22)
    .attr("width", width)
    .attr("height", 32)
    .attr("rx", 16)
    .attr("fill", fill)
    .attr("stroke", stroke)
    .attr("stroke-width", stroke === "none" ? 0 : 1.5);
  node.append("text")
    .attr("class", "micro-label")
    .attr("text-anchor", "middle")
    .attr("font-size", size)
    .attr("fill", palette.ink)
    .attr("y", 0)
    .text(text);
  return node;
}

function dropletPath(x, y, scale = 1) {
  return `M${x} ${y - 14 * scale} C${x - 12 * scale} ${y - 2 * scale} ${x - 10 * scale} ${y + 12 * scale} ${x} ${y + 15 * scale} C${x + 10 * scale} ${y + 12 * scale} ${x + 12 * scale} ${y - 2 * scale} ${x} ${y - 14 * scale} Z`;
}

function drawDroplet(g, x, y, scale = 1, opacity = 1) {
  g.append("path")
    .attr("d", dropletPath(x, y, scale))
    .attr("fill", palette.waterLight)
    .attr("stroke", palette.water)
    .attr("stroke-width", 2)
    .attr("opacity", opacity);
}

function drawSeed(g, x, y, scale, crack = 0, root = 0) {
  const seed = g.append("g").attr("transform", `translate(${x} ${y}) scale(${scale})`);
  seed.append("ellipse")
    .attr("rx", 92)
    .attr("ry", 58)
    .attr("fill", palette.seed)
    .attr("stroke", palette.seedStroke)
    .attr("stroke-width", 5);
  seed.append("path")
    .attr("d", "M-42 -18 C-5 -44 38 -30 58 12")
    .attr("fill", "none")
    .attr("stroke", "#fff4cc")
    .attr("stroke-width", 10)
    .attr("stroke-linecap", "round")
    .attr("opacity", 0.48);
  if (crack > 0) {
    const c = smooth(crack);
    seed.append("path")
      .attr("d", `M18 -42 L${lerp(18, -8, c)} ${lerp(-42, -12, c)} L${lerp(-8, 16, c)} ${lerp(-12, 20, c)} L${lerp(16, -4, c)} ${lerp(20, 48, c)}`)
      .attr("fill", "none")
      .attr("stroke", palette.seedStroke)
      .attr("stroke-width", 6)
      .attr("stroke-linecap", "round")
      .attr("stroke-linejoin", "round");
  }
  if (root > 0) {
    const r = smooth(root);
    seed.append("path")
      .attr("d", `M20 48 C${20 + 12 * r} ${72 + 28 * r} ${-12 + 14 * r} ${96 + 72 * r} ${-8} ${120 + 118 * r}`)
      .attr("fill", "none")
      .attr("stroke", palette.root)
      .attr("stroke-width", 16)
      .attr("stroke-linecap", "round");
    seed.append("circle")
      .attr("cx", -8)
      .attr("cy", 120 + 118 * r)
      .attr("r", 11)
      .attr("fill", palette.rootDark);
  }
  return seed;
}

function drawSoil(g, y = 430, height = 250, opacity = 1) {
  const soil = g.append("g").attr("opacity", opacity);
  soil.append("rect")
    .attr("x", 0)
    .attr("y", y)
    .attr("width", video.width)
    .attr("height", height)
    .attr("fill", palette.soil);
  for (let i = 0; i < 4; i += 1) {
    soil.append("path")
      .attr("d", `M0 ${y + 42 + i * 48} C240 ${y + 18 + i * 44} 430 ${y + 78 + i * 36} 690 ${y + 48 + i * 48} S1050 ${y + 24 + i * 50} 1280 ${y + 58 + i * 42}`)
      .attr("fill", "none")
      .attr("stroke", i % 2 ? palette.soilDark : "#ffffff")
      .attr("stroke-width", 2)
      .attr("opacity", 0.62);
  }
  return soil;
}

function drawParticles(g, particles, progress, options = {}) {
  const count = Math.floor(particles.length * clamp(progress));
  particles.forEach((p, index) => {
    const appear = smooth((progress * particles.length - index) / 1.2);
    if (appear <= 0) return;
    const tx = p.to ? lerp(p.x, p.to[0], smooth(progress)) : p.x;
    const ty = p.to ? lerp(p.y, p.to[1], smooth(progress)) : p.y;
    g.append("circle")
      .attr("cx", tx)
      .attr("cy", ty)
      .attr("r", p.r ?? 7)
      .attr("fill", p.fill)
      .attr("stroke", p.stroke ?? "none")
      .attr("stroke-width", p.stroke ? 1.5 : 0)
      .attr("opacity", Math.min(appear, options.opacity ?? 1));
  });
  return count;
}

function drawSeedAwakens(g, seconds, shot) {
  const p = local(seconds, shot);
  drawSoil(g, 420, 300, 1);
  label(g, "germination starts with inputs", 640, 126, 34);

  const seedScale = 1 + 0.12 * smooth((p - 0.24) / 0.34) + 0.02 * pulse(p, 4);
  drawSeed(g, 640, 392, seedScale, (p - 0.38) / 0.22, (p - 0.54) / 0.36);

  const waterProgress = smooth((p - 0.06) / 0.42);
  const drops = [
    { x: 450, y: 132, to: [570, 342], delay: 0 },
    { x: 590, y: 104, to: [625, 330], delay: 0.12 },
    { x: 740, y: 112, to: [682, 338], delay: 0.24 },
    { x: 835, y: 156, to: [702, 366], delay: 0.36 }
  ];
  drops.forEach((d, i) => {
    const q = smooth((waterProgress - d.delay) / 0.45);
    if (q <= 0) return;
    drawDroplet(g, lerp(d.x, d.to[0], q), lerp(d.y, d.to[1], q), 0.7, 0.96);
    if (i === 0) roundedLabel(g, "water", d.x - 12, d.y - 58, palette.waterLight, palette.water);
  });

  const oxygen = [
    { x: 930, y: 190, to: [735, 352] },
    { x: 988, y: 250, to: [715, 374] },
    { x: 878, y: 296, to: [692, 388] }
  ];
  oxygen.forEach((d, i) => {
    const q = smooth((p - 0.16 - i * 0.06) / 0.34);
    if (q <= 0) return;
    g.append("circle")
      .attr("cx", lerp(d.x, d.to[0], q))
      .attr("cy", lerp(d.y, d.to[1], q))
      .attr("r", 10)
      .attr("fill", palette.white)
      .attr("stroke", palette.air)
      .attr("stroke-width", 3)
      .attr("opacity", 0.9);
  });
  roundedLabel(g, "oxygen", 962, 178, "#ffffff", palette.air);

  const warm = smooth((p - 0.08) / 0.36);
  const sun = g.append("g").attr("opacity", 0.4 + 0.6 * warm);
  sun.append("circle").attr("cx", 257).attr("cy", 180).attr("r", 44 + 6 * pulse(p, 2)).attr("fill", palette.light);
  for (let i = 0; i < 9; i += 1) {
    const a = (-50 + i * 14) * Math.PI / 180;
    const x1 = 257 + Math.cos(a) * 68;
    const y1 = 180 + Math.sin(a) * 68;
    const x2 = 257 + Math.cos(a) * (154 + 24 * warm);
    const y2 = 180 + Math.sin(a) * (154 + 24 * warm);
    sun.append("line").attr("x1", x1).attr("y1", y1).attr("x2", x2).attr("y2", y2).attr("stroke", palette.light).attr("stroke-width", 5).attr("stroke-linecap", "round");
  }
  roundedLabel(g, "warmth", 258, 112, "#fff4cc", palette.seedStroke);

  const rootGlow = smooth((p - 0.72) / 0.18);
  if (rootGlow > 0) {
    g.append("circle")
      .attr("cx", 632)
      .attr("cy", 612)
      .attr("r", 24 + 18 * pulse(p, 2))
      .attr("fill", "none")
      .attr("stroke", palette.plant)
      .attr("stroke-width", 5)
      .attr("opacity", 0.65 * rootGlow);
    roundedLabel(g, "first root", 756, 606, palette.leafLight, palette.plant);
  }

  return { shot: shot.id, progress: p, focal: "seed", anchors: ["seed", "water", "oxygen", "warmth"] };
}

function rootPath(length = 1) {
  const y2 = lerp(168, 616, smooth(length));
  return `M640 150 C628 250 660 342 638 ${y2}`;
}

function drawRootNetwork(g, seconds, shot) {
  const p = local(seconds, shot);
  drawSoil(g, 112, 608, 1);
  label(g, "roots anchor and absorb", 640, 76, 34);

  const root = g.append("g");
  const grow = smooth((p - 0.06) / 0.42);
  root.append("path")
    .attr("d", rootPath(grow))
    .attr("fill", "none")
    .attr("stroke", palette.root)
    .attr("stroke-width", 18)
    .attr("stroke-linecap", "round");
  root.append("path")
    .attr("d", rootPath(grow))
    .attr("fill", "none")
    .attr("stroke", palette.rootDark)
    .attr("stroke-width", 3)
    .attr("opacity", 0.55);

  const branches = [
    { from: [636, 245], c: [536, 270], to: [438, 320], side: -1 },
    { from: [650, 318], c: [770, 340], to: [862, 404], side: 1 },
    { from: [636, 408], c: [520, 438], to: [388, 504], side: -1 },
    { from: [643, 500], c: [780, 522], to: [928, 590], side: 1 }
  ];

  branches.forEach((b, i) => {
    const q = smooth((p - 0.18 - i * 0.07) / 0.38);
    const end = [lerp(b.from[0], b.to[0], q), lerp(b.from[1], b.to[1], q)];
    root.append("path")
      .attr("d", `M${b.from[0]} ${b.from[1]} Q${b.c[0]} ${b.c[1]} ${end[0]} ${end[1]}`)
      .attr("fill", "none")
      .attr("stroke", palette.root)
      .attr("stroke-width", 10)
      .attr("stroke-linecap", "round")
      .attr("opacity", q > 0 ? 1 : 0);
    if (q > 0.6) {
      for (let h = 0; h < 5; h += 1) {
        const hx = lerp(b.from[0], b.to[0], 0.48 + h * 0.09);
        const hy = lerp(b.from[1], b.to[1], 0.48 + h * 0.09);
        root.append("line")
          .attr("x1", hx)
          .attr("y1", hy)
          .attr("x2", hx + b.side * (18 + h * 3))
          .attr("y2", hy + 20)
          .attr("stroke", palette.rootDark)
          .attr("stroke-width", 3)
          .attr("stroke-linecap", "round")
          .attr("opacity", 0.55 * smooth((q - 0.58) / 0.28));
      }
    }
  });

  const resources = [
    { x: 310, y: 320, fill: palette.water, to: [438, 320], r: 8 },
    { x: 980, y: 390, fill: palette.mineral, to: [862, 404], r: 7 },
    { x: 274, y: 510, fill: palette.water, to: [388, 504], r: 8 },
    { x: 1032, y: 588, fill: palette.mineralAlt, to: [928, 590], r: 7 },
    { x: 480, y: 615, fill: palette.mineral, to: [640, 585], r: 7 },
    { x: 810, y: 224, fill: palette.water, to: [680, 268], r: 8 }
  ];
  drawParticles(g, resources, smooth((p - 0.28) / 0.44), { opacity: 0.95 });

  const streamP = smooth((p - 0.42) / 0.5);
  for (let i = 0; i < 11; i += 1) {
    const q = (streamP * 1.35 - i * 0.09) % 1;
    if (streamP <= 0) continue;
    const y = lerp(608, 170, q);
    const x = 640 + Math.sin(q * Math.PI * 2) * 18;
    g.append("circle")
      .attr("cx", x)
      .attr("cy", y)
      .attr("r", i % 2 ? 6 : 8)
      .attr("fill", i % 3 ? palette.water : palette.mineral)
      .attr("opacity", 0.82 * streamP);
  }

  roundedLabel(g, "water + minerals", 288, 220, "#ffffff", palette.water);
  roundedLabel(g, "roots", 732, 308, "#fff4cc", palette.rootDark);
  roundedLabel(g, "anchor", 788, 640, palette.soil, palette.rootDark);

  return { shot: shot.id, progress: p, focal: "root network", anchors: ["roots", "water", "minerals"] };
}

function drawPlantStem(g, baseX, baseY, topY, progress = 1, options = {}) {
  const h = (baseY - topY) * smooth(progress);
  const top = baseY - h;
  const path = `M${baseX} ${baseY} C${baseX - 14} ${baseY - h * 0.32} ${baseX + 28} ${baseY - h * 0.7} ${baseX + 8} ${top}`;
  g.append("path")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", options.stroke ?? palette.plant)
    .attr("stroke-width", options.width ?? 22)
    .attr("stroke-linecap", "round");
  return { topX: baseX + 8, topY: top, path };
}

function leafPath(cx, cy, rx, ry, angle = 0) {
  return `M${cx} ${cy} C${cx - rx} ${cy - ry} ${cx - rx} ${cy + ry} ${cx} ${cy + ry * 0.84} C${cx + rx} ${cy + ry} ${cx + rx} ${cy - ry} ${cx} ${cy} Z`;
}

function drawLeaf(g, cx, cy, rx, ry, angle = 0, open = 1, fill = palette.leaf) {
  const scaleX = 0.22 + 0.78 * smooth(open);
  const node = g.append("g").attr("transform", `translate(${cx} ${cy}) rotate(${angle}) scale(${scaleX} 1) translate(${-cx} ${-cy})`);
  node.append("path")
    .attr("d", leafPath(cx, cy, rx, ry))
    .attr("fill", fill)
    .attr("stroke", palette.plantDark)
    .attr("stroke-width", 3);
  node.append("path")
    .attr("d", `M${cx} ${cy + ry * 0.72} C${cx} ${cy + ry * 0.2} ${cx} ${cy - ry * 0.2} ${cx} ${cy}`)
    .attr("fill", "none")
    .attr("stroke", palette.plantDark)
    .attr("stroke-width", 2)
    .attr("opacity", 0.65);
  return node;
}

function drawShootFindsLight(g, seconds, shot) {
  const p = local(seconds, shot);
  drawSoil(g, 512, 208, 1);
  label(g, "shoots lift leaves into light", 640, 76, 34);

  const sun = g.append("g");
  sun.append("circle").attr("cx", 1034).attr("cy", 132).attr("r", 54).attr("fill", palette.light).attr("opacity", 0.9);
  for (let i = 0; i < 12; i += 1) {
    const a = (150 + i * 9) * Math.PI / 180;
    sun.append("line")
      .attr("x1", 1034 + Math.cos(a) * 76)
      .attr("y1", 132 + Math.sin(a) * 76)
      .attr("x2", 1034 + Math.cos(a) * 300)
      .attr("y2", 132 + Math.sin(a) * 300)
      .attr("stroke", palette.light)
      .attr("stroke-width", 4)
      .attr("stroke-linecap", "round")
      .attr("opacity", 0.35 + 0.35 * pulse((p + i / 12) % 1, 1));
  }

  drawSeed(g, 540, 514, 0.55, 1, 1);
  const grow = smooth((p - 0.08) / 0.48);
  const stem = drawPlantStem(g, 564, 510, 188, grow, { width: 24 });
  const leafOpen = smooth((p - 0.42) / 0.38);
  drawLeaf(g, stem.topX - 68, stem.topY + 18, 70, 34, -54, leafOpen);
  drawLeaf(g, stem.topX + 78, stem.topY + 10, 80, 38, 48, leafOpen);
  drawLeaf(g, stem.topX + 6, stem.topY - 20, 64, 30, 0, smooth((p - 0.55) / 0.34), palette.leafLight);

  const intercept = smooth((p - 0.62) / 0.28);
  for (let i = 0; i < 9; i += 1) {
    const start = [944 + i * 14, 170 + i * 12];
    const end = [650 + i * 10, 278 + i * 7];
    const q = smooth((intercept * 1.2 - i * 0.06) / 0.45);
    if (q <= 0) continue;
    g.append("circle")
      .attr("cx", lerp(start[0], end[0], q))
      .attr("cy", lerp(start[1], end[1], q))
      .attr("r", 7)
      .attr("fill", palette.light)
      .attr("opacity", 0.85);
  }

  roundedLabel(g, "shoot", 432, 370, palette.leafLight, palette.plant);
  roundedLabel(g, "leaves", 746, 238, palette.leafLight, palette.plant);
  roundedLabel(g, "light", 1036, 226, "#fff4cc", palette.seedStroke);

  return { shot: shot.id, progress: p, focal: "shoot and leaves", anchors: ["shoot", "leaves", "light"] };
}

function drawLargeLeaf(g, cx, cy, scale = 1) {
  const node = g.append("g").attr("transform", `translate(${cx} ${cy}) scale(${scale}) translate(${-cx} ${-cy})`);
  node.append("path")
    .attr("d", `M${cx - 320} ${cy + 26} C${cx - 160} ${cy - 210} ${cx + 150} ${cy - 210} ${cx + 324} ${cy + 18} C${cx + 128} ${cy + 182} ${cx - 122} ${cy + 194} ${cx - 320} ${cy + 26} Z`)
    .attr("fill", palette.leafLight)
    .attr("stroke", palette.plant)
    .attr("stroke-width", 6);
  node.append("path")
    .attr("d", `M${cx - 288} ${cy + 30} C${cx - 90} ${cy + 10} ${cx + 104} ${cy + 10} ${cx + 298} ${cy + 20}`)
    .attr("fill", "none")
    .attr("stroke", palette.plantDark)
    .attr("stroke-width", 6)
    .attr("stroke-linecap", "round");
  for (let i = -4; i <= 4; i += 1) {
    if (i === 0) continue;
    const x = cx + i * 58;
    node.append("path")
      .attr("d", `M${x} ${cy + 14} C${x - 24 * Math.sign(i)} ${cy - 48} ${x - 92 * Math.sign(i)} ${cy - 86} ${x - 144 * Math.sign(i)} ${cy - 92}`)
      .attr("fill", "none")
      .attr("stroke", palette.plant)
      .attr("stroke-width", 3)
      .attr("opacity", 0.55);
    node.append("path")
      .attr("d", `M${x} ${cy + 26} C${x - 24 * Math.sign(i)} ${cy + 70} ${x - 82 * Math.sign(i)} ${cy + 92} ${x - 122 * Math.sign(i)} ${cy + 98}`)
      .attr("fill", "none")
      .attr("stroke", palette.plant)
      .attr("stroke-width", 3)
      .attr("opacity", 0.5);
  }
  return node;
}

function movingCircle(g, path, t, r, fill, opacity = 1) {
  const index = Math.min(path.length - 2, Math.floor(clamp(t) * (path.length - 1)));
  const localT = clamp(t * (path.length - 1) - index);
  const a = path[index];
  const b = path[index + 1];
  g.append("circle")
    .attr("cx", lerp(a[0], b[0], localT))
    .attr("cy", lerp(a[1], b[1], localT))
    .attr("r", r)
    .attr("fill", fill)
    .attr("opacity", opacity);
}

function drawPhotosynthesis(g, seconds, shot) {
  const p = local(seconds, shot);
  label(g, "leaves make sugars", 640, 72, 34);
  drawLargeLeaf(g, 512, 356, 1);

  const inputP = smooth((p - 0.06) / 0.32);
  for (let i = 0; i < 11; i += 1) {
    const q = smooth((inputP * 1.18 - i * 0.055) / 0.42);
    if (q > 0) {
      movingCircle(g, [[200 + i * 20, 110], [270 + i * 18, 210], [344 + i * 18, 304]], q, 7, palette.light, 0.9);
    }
  }
  for (let i = 0; i < 8; i += 1) {
    const q = smooth((inputP * 1.25 - i * 0.07) / 0.45);
    if (q > 0) {
      g.append("circle")
        .attr("cx", lerp(104, 306, q) + i * 16)
        .attr("cy", lerp(470 + i * 10, 382 + i * 4, q))
        .attr("r", 12)
        .attr("fill", palette.white)
        .attr("stroke", palette.air)
        .attr("stroke-width", 3)
        .attr("opacity", 0.92);
      if (q > 0.5 && i % 3 === 0) {
        label(g, "CO2", lerp(104, 306, q) + i * 16, lerp(470 + i * 10, 382 + i * 4, q) + 4, 10, "middle", palette.air);
      }
    }
  }
  for (let i = 0; i < 9; i += 1) {
    const q = smooth((inputP * 1.22 - i * 0.07) / 0.42);
    if (q > 0) {
      drawDroplet(g, lerp(540, 478 + i * 20, q), lerp(662, 460, q) - i * 10, 0.45, 0.85);
    }
  }

  const assemble = smooth((p - 0.32) / 0.34);
  for (let i = 0; i < 10; i += 1) {
    const q = smooth((assemble * 1.25 - i * 0.06) / 0.45);
    if (q <= 0) continue;
    const x = lerp(472 + (i % 4) * 32, 658 + i * 12, q);
    const y = lerp(358 + Math.floor(i / 4) * 26, 350 + Math.sin(i) * 28, q);
    g.append("rect")
      .attr("x", x - 11)
      .attr("y", y - 11)
      .attr("width", 22)
      .attr("height", 22)
      .attr("rx", 5)
      .attr("fill", palette.sugarLight)
      .attr("stroke", palette.sugar)
      .attr("stroke-width", 3)
      .attr("opacity", 0.95);
  }

  const outputP = smooth((p - 0.52) / 0.4);
  for (let i = 0; i < 10; i += 1) {
    const q = smooth((outputP * 1.22 - i * 0.06) / 0.44);
    if (q <= 0) continue;
    g.append("rect")
      .attr("x", lerp(710, 1020, q) + i * 9 - 12)
      .attr("y", lerp(360, 420 + Math.sin(i) * 28, q) - 12)
      .attr("width", 24)
      .attr("height", 24)
      .attr("rx", 5)
      .attr("fill", palette.sugarLight)
      .attr("stroke", palette.sugar)
      .attr("stroke-width", 3)
      .attr("opacity", 0.95);
  }
  for (let i = 0; i < 8; i += 1) {
    const q = smooth((outputP * 1.12 - i * 0.07) / 0.4);
    if (q <= 0) continue;
    g.append("circle")
      .attr("cx", lerp(690, 965, q) + i * 14)
      .attr("cy", lerp(300, 190 - i * 8, q))
      .attr("r", 11)
      .attr("fill", palette.waterLight)
      .attr("stroke", palette.oxygen)
      .attr("stroke-width", 3)
      .attr("opacity", 0.86);
  }

  roundedLabel(g, "light", 260, 150, "#fff4cc", palette.seedStroke);
  roundedLabel(g, "CO2", 144, 446, "#ffffff", palette.air);
  roundedLabel(g, "water", 558, 640, palette.waterLight, palette.water);
  roundedLabel(g, "sugars", 1054, 426, palette.sugarLight, palette.sugar);
  roundedLabel(g, "O2", 1030, 160, palette.waterLight, palette.oxygen);

  const formula = g.append("g").attr("transform", "translate(780 552)");
  formula.append("rect")
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", 376)
    .attr("height", 72)
    .attr("rx", 8)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.grid)
    .attr("stroke-width", 2);
  formula.append("text")
    .attr("class", "small-label")
    .attr("x", 188)
    .attr("y", 43)
    .attr("text-anchor", "middle")
    .attr("font-size", 22)
    .text("light + CO2 + water -> sugar + O2");

  return { shot: shot.id, progress: p, focal: "leaf conversion", anchors: ["light", "CO2", "water", "sugars", "O2"] };
}

function drawWholePlant(g, progress = 1, options = {}) {
  const baseX = options.baseX ?? 410;
  const baseY = options.baseY ?? 590;
  const topY = options.topY ?? 188;
  drawPlantStem(g, baseX, baseY, topY, progress, { width: options.width ?? 28, stroke: options.stroke ?? palette.plant });
  const open = smooth(progress);
  drawLeaf(g, baseX - 108, lerp(baseY - 120, topY + 94, open), 92, 42, -58, open);
  drawLeaf(g, baseX + 116, lerp(baseY - 168, topY + 78, open), 102, 44, 50, open);
  drawLeaf(g, baseX - 72, lerp(baseY - 230, topY + 26, open), 82, 36, -44, open);
  drawLeaf(g, baseX + 72, lerp(baseY - 280, topY + 8, open), 76, 32, 42, open);
}

function drawCellPanel(g, x, y, title, progress, accent) {
  const panel = g.append("g").attr("transform", `translate(${x} ${y})`);
  panel.append("rect")
    .attr("width", 318)
    .attr("height", 184)
    .attr("rx", 8)
    .attr("fill", "#ffffff")
    .attr("stroke", palette.grid)
    .attr("stroke-width", 2);
  label(panel, title, 159, 34, 20);
  const cols = 5;
  const rows = 3;
  const gap = 8;
  const cellW = 44;
  const cellH = 34;
  for (let r = 0; r < rows; r += 1) {
    for (let c = 0; c < cols; c += 1) {
      const i = r * cols + c;
      const q = smooth((progress * 1.25 - i * 0.035) / 0.35);
      const grow = 0.72 + 0.28 * q + 0.06 * pulse(progress + i * 0.08, 1) * q;
      const cx = 37 + c * (cellW + gap);
      const cy = 64 + r * (cellH + gap);
      panel.append("rect")
        .attr("x", cx + (cellW * (1 - grow)) / 2)
        .attr("y", cy + (cellH * (1 - grow)) / 2)
        .attr("width", cellW * grow)
        .attr("height", cellH * grow)
        .attr("rx", 8)
        .attr("fill", q > 0.28 ? accent : "#f7f7f7")
        .attr("stroke", q > 0.28 ? palette.plant : palette.soilDark)
        .attr("stroke-width", 2)
        .attr("opacity", 0.98);
      if (q > 0.48 && i % 4 === 0) {
        panel.append("line")
          .attr("x1", cx + cellW / 2)
          .attr("x2", cx + cellW / 2)
          .attr("y1", cy + 6)
          .attr("y2", cy + cellH - 6)
          .attr("stroke", palette.white)
          .attr("stroke-width", 3)
          .attr("opacity", 0.9);
      }
    }
  }
}

function drawGrowthZones(g, seconds, shot) {
  const p = local(seconds, shot);
  label(g, "transport feeds new cells", 640, 72, 34);
  drawSoil(g, 606, 114, 0.78);
  drawWholePlant(g, 1, { baseX: 392, baseY: 606, topY: 166 });

  const routeP = smooth((p - 0.08) / 0.34);
  const xylem = g.append("g").attr("opacity", routeP);
  xylem.append("path")
    .attr("d", "M360 598 C350 454 382 320 398 174")
    .attr("fill", "none")
    .attr("stroke", palette.water)
    .attr("stroke-width", 7)
    .attr("stroke-linecap", "round");
  xylem.append("path")
    .attr("d", "M424 178 C500 222 555 274 612 308")
    .attr("fill", "none")
    .attr("stroke", palette.water)
    .attr("stroke-width", 5)
    .attr("stroke-linecap", "round");

  const phloem = g.append("g").attr("opacity", smooth((p - 0.22) / 0.34));
  phloem.append("path")
    .attr("d", "M612 308 C690 340 730 382 806 394")
    .attr("fill", "none")
    .attr("stroke", palette.sugar)
    .attr("stroke-width", 7)
    .attr("stroke-linecap", "round");
  phloem.append("path")
    .attr("d", "M508 302 C610 390 674 486 812 546")
    .attr("fill", "none")
    .attr("stroke", palette.sugar)
    .attr("stroke-width", 7)
    .attr("stroke-linecap", "round");

  for (let i = 0; i < 10; i += 1) {
    const q = (routeP * 1.25 - i * 0.08) % 1;
    if (routeP > 0.05) movingCircle(g, [[360, 598], [350, 454], [382, 320], [398, 174]], q, 6, palette.water, 0.85);
  }
  const sugarP = smooth((p - 0.28) / 0.42);
  for (let i = 0; i < 11; i += 1) {
    const q = smooth((sugarP * 1.28 - i * 0.06) / 0.48);
    if (q <= 0) continue;
    const target = i % 2 ? [[508, 302], [610, 390], [674, 486], [812, 546]] : [[612, 308], [690, 340], [730, 382], [806, 394]];
    const segment = Math.min(target.length - 2, Math.floor(q * (target.length - 1)));
    const rt = q * (target.length - 1) - segment;
    const a = target[segment];
    const b = target[segment + 1];
    g.append("rect")
      .attr("x", lerp(a[0], b[0], rt) - 10)
      .attr("y", lerp(a[1], b[1], rt) - 10)
      .attr("width", 20)
      .attr("height", 20)
      .attr("rx", 5)
      .attr("fill", palette.sugarLight)
      .attr("stroke", palette.sugar)
      .attr("stroke-width", 2);
  }

  const lensOpacity = smooth((p - 0.22) / 0.28);
  const lens = g.append("g").attr("opacity", lensOpacity);
  lens.append("circle")
    .attr("cx", 410)
    .attr("cy", 178)
    .attr("r", 42)
    .attr("fill", "none")
    .attr("stroke", palette.plant)
    .attr("stroke-width", 4);
  lens.append("path")
    .attr("d", "M448 196 C570 142 696 148 820 222")
    .attr("fill", "none")
    .attr("stroke", palette.plant)
    .attr("stroke-width", 3)
    .attr("stroke-dasharray", "8 10")
    .attr("opacity", 0.72);
  lens.append("circle")
    .attr("cx", 360)
    .attr("cy", 598)
    .attr("r", 38)
    .attr("fill", "none")
    .attr("stroke", palette.root)
    .attr("stroke-width", 4);
  lens.append("path")
    .attr("d", "M398 592 C548 650 690 636 820 530")
    .attr("fill", "none")
    .attr("stroke", palette.root)
    .attr("stroke-width", 3)
    .attr("stroke-dasharray", "8 10")
    .attr("opacity", 0.72);

  drawCellPanel(g, 820, 176, "shoot tip: new cells", smooth((p - 0.3) / 0.38), palette.leafLight);
  drawCellPanel(g, 820, 432, "root tip: new cells", smooth((p - 0.36) / 0.34), "#fff4cc");

  roundedLabel(g, "xylem up", 240, 340, palette.waterLight, palette.water).attr("opacity", routeP);
  roundedLabel(g, "phloem to growth", 622, 516, palette.sugarLight, palette.sugar).attr("opacity", sugarP);

  return { shot: shot.id, progress: p, focal: "transport and cells", anchors: ["xylem", "phloem", "new cells"] };
}

function drawFlower(g, cx, cy, open = 1) {
  const o = smooth(open);
  for (let i = 0; i < 6; i += 1) {
    const a = i * Math.PI / 3;
    const px = cx + Math.cos(a) * 22 * o;
    const py = cy + Math.sin(a) * 22 * o;
    g.append("ellipse")
      .attr("cx", px)
      .attr("cy", py)
      .attr("rx", 14 * o)
      .attr("ry", 26 * o)
      .attr("fill", "#ffccd5")
      .attr("stroke", palette.mineralAlt)
      .attr("stroke-width", 2)
      .attr("transform", `rotate(${i * 60} ${px} ${py})`);
  }
  g.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 13 * o).attr("fill", palette.seed);
}

function drawCycleIcon(g, kind, x, y, progress) {
  const node = g.append("g").attr("transform", `translate(${x} ${y})`).attr("opacity", smooth(progress));
  if (kind === "seed") {
    drawSeed(node, 0, 0, 0.28, 1, 0);
  } else if (kind === "sprout") {
    drawSeed(node, -8, 22, 0.22, 1, 1);
    drawPlantStem(node, 0, 22, -32, 1, { width: 8 });
    drawLeaf(node, -16, -26, 20, 10, -48, 1);
    drawLeaf(node, 20, -28, 22, 10, 44, 1);
  } else if (kind === "plant") {
    drawWholePlant(node, 1, { baseX: 0, baseY: 54, topY: -42, width: 10 });
  } else if (kind === "flower") {
    drawWholePlant(node, 1, { baseX: 0, baseY: 54, topY: -42, width: 10 });
    drawFlower(node, 8, -46, 1);
  } else {
    node.append("ellipse").attr("cx", 0).attr("cy", 8).attr("rx", 34).attr("ry", 46).attr("fill", "#ffe5cc").attr("stroke", palette.root).attr("stroke-width", 3);
    for (let i = 0; i < 5; i += 1) {
      node.append("circle").attr("cx", -18 + i * 9).attr("cy", 8 + Math.sin(i) * 10).attr("r", 5).attr("fill", palette.seed).attr("stroke", palette.seedStroke).attr("stroke-width", 1);
    }
  }
  return node;
}

function drawCycleContinues(g, seconds, shot) {
  const p = local(seconds, shot);
  label(g, "mature plants make new seeds", 640, 72, 34);
  const plantLayer = g.append("g").attr("opacity", 0.42);
  drawWholePlant(plantLayer, 1, { baseX: 640, baseY: 604, topY: 304, width: 20 });
  drawFlower(plantLayer, 648, 292, smooth((p - 0.08) / 0.26));

  const center = [640, 392];
  const radius = 230;
  const stages = [
    { id: "seed", a: -90, label: "seed", dx: 0, dy: -10 },
    { id: "sprout", a: -18, label: "sprout", dx: 26, dy: 6 },
    { id: "plant", a: 54, label: "plant", dx: 20, dy: 22 },
    { id: "flower", a: 126, label: "flower", dx: -20, dy: 22 },
    { id: "fruit", a: 198, label: "fruit + seeds", dx: -30, dy: 4 }
  ];
  const ringP = smooth((p - 0.26) / 0.46);
  const ring = g.append("g").attr("opacity", 0.96);
  stages.forEach((s, i) => {
    const a = s.a * Math.PI / 180;
    const x = center[0] + Math.cos(a) * radius;
    const y = center[1] + Math.sin(a) * radius;
    drawCycleIcon(ring, s.id, x + s.dx, y + s.dy, smooth((ringP * 1.2 - i * 0.1) / 0.45));
    roundedLabel(ring, s.label, x + s.dx, y + s.dy + 78, "#ffffff", palette.grid, 15);
  });

  const arc = d3.arc().innerRadius(radius - 4).outerRadius(radius + 4).startAngle(-Math.PI / 2).endAngle(-Math.PI / 2 + Math.PI * 2 * ringP);
  ring.append("path")
    .attr("d", arc())
    .attr("transform", `translate(${center[0]} ${center[1]})`)
    .attr("fill", palette.plant)
    .attr("opacity", 0.78);

  const seedReturn = smooth((p - 0.64) / 0.3);
  for (let i = 0; i < 7; i += 1) {
    const q = smooth((seedReturn * 1.2 - i * 0.06) / 0.5);
    if (q <= 0) continue;
    const a = (198 - 288 * q) * Math.PI / 180;
    g.append("circle")
      .attr("cx", center[0] + Math.cos(a) * radius)
      .attr("cy", center[1] + Math.sin(a) * radius)
      .attr("r", 8)
      .attr("fill", palette.seed)
      .attr("stroke", palette.seedStroke)
      .attr("stroke-width", 2);
  }

  return { shot: shot.id, progress: p, focal: "seed cycle", anchors: ["flower", "fruit", "seeds"] };
}

function drawTransitionPulse(g, seconds) {
  const active = video.transitions.find((transition) => seconds >= transition.start && seconds <= transition.start + transition.duration);
  if (!active) return null;
  const p = smooth((seconds - active.start) / active.duration);
  const paths = {
    "t01-seed-to-roots": [[640, 498], [638, 568], [640, 632]],
    "t02-roots-to-shoot": [[640, 164], [590, 344], [574, 500]],
    "t03-shoot-to-leaf": [[662, 232], [598, 284], [512, 356]],
    "t04-leaf-to-growth-zones": [[970, 410], [760, 386], [610, 308]],
    "t05-growth-to-cycle": [[820, 214], [810, 280], [640, 162]]
  };
  const path = paths[active.id];
  if (!path) return null;

  if (active.id === "t03-shoot-to-leaf") {
    const preview = g.append("g").attr("opacity", 0.18 + 0.62 * p);
    preview.append("circle")
      .attr("cx", 640)
      .attr("cy", 356)
      .attr("r", lerp(70, 345, p))
      .attr("fill", "#ffffff")
      .attr("opacity", 0.36);
    drawLargeLeaf(preview, 640, 356, lerp(0.24, 0.98, p));
  }

  const layer = g.append("g").attr("opacity", 0.8);
  movingCircle(layer, path, p, 17 + 5 * pulse(p, 1), palette.seed, 0.88);
  layer.append("circle")
    .attr("cx", path[Math.min(path.length - 1, Math.floor(p * (path.length - 1)))][0])
    .attr("cy", path[Math.min(path.length - 1, Math.floor(p * (path.length - 1)))][1])
    .attr("r", 34 + 16 * pulse(p, 1))
    .attr("fill", "none")
    .attr("stroke", palette.plant)
    .attr("stroke-width", 5)
    .attr("opacity", 0.25);
  return active.id;
}

function drawFrame(seconds) {
  clear();
  const root = svg.append("g");
  addBackground(root, seconds);

  const shot = video.shots.find((item) => seconds >= item.start && seconds < item.start + item.duration) ?? video.shots[video.shots.length - 1];
  let state;
  if (shot.id === "s01-seed-awakens") state = drawSeedAwakens(root, seconds, shot);
  else if (shot.id === "s02-roots-feed") state = drawRootNetwork(root, seconds, shot);
  else if (shot.id === "s03-shoot-finds-light") state = drawShootFindsLight(root, seconds, shot);
  else if (shot.id === "s04-leaf-makes-sugar") state = drawPhotosynthesis(root, seconds, shot);
  else if (shot.id === "s05-growth-zones") state = drawGrowthZones(root, seconds, shot);
  else state = drawCycleContinues(root, seconds, shot);

  const transition = drawTransitionPulse(root, seconds);
  return {
    videoId: video.id,
    seconds: Number(seconds.toFixed(3)),
    shot: state.shot,
    progress: Number(state.progress.toFixed(3)),
    focal: state.focal,
    anchors: state.anchors,
    transition,
    elementCount: svg.selectAll("*").size()
  };
}

window.renderConceptFrame = (_id, seconds) => drawFrame(clamp(seconds, 0, video.durationSeconds - 1 / 30));
window.__plantGrowthVideo = video;

drawFrame(0);

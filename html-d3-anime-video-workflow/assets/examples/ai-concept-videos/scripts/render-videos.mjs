#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { createReadStream, existsSync, mkdirSync, readFileSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { concepts } from "../concepts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const deckDir = resolve(__dirname, "..");
const repoRoot = resolve(deckDir, "..", "..", "..", "..");
const defaultOutput = resolve(repoRoot, "output", "ai-concept-videos");

const encoderPresets = new Set(["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow", "placebo"]);
const renderPresets = {
  quick: {
    fps: 6,
    quality: 24,
    deviceScaleFactor: 1,
    encoderPreset: "veryfast",
    contactSheet: false
  },
  draft: {
    fps: 12,
    quality: 24,
    deviceScaleFactor: 1,
    encoderPreset: "veryfast",
    contactSheet: false
  },
  motion: {
    fps: 30,
    quality: 20,
    deviceScaleFactor: 1,
    encoderPreset: "faster",
    contactSheet: true
  },
  fast: {
    fps: 30,
    quality: 16,
    deviceScaleFactor: 2,
    encoderPreset: "veryfast",
    contactSheet: false
  },
  final: {
    fps: 30,
    quality: 16,
    deviceScaleFactor: 2,
    encoderPreset: "slow",
    contactSheet: true
  }
};

function findPresetName(argv) {
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--preset") return argv[i + 1];
  }
  return null;
}

function parseArgs(argv) {
  const presetName = findPresetName(argv);
  if (presetName && !renderPresets[presetName]) {
    throw new Error(`Unknown preset: ${presetName}. Use one of: ${Object.keys(renderPresets).join(", ")}.`);
  }
  const labelWasExplicit = argv.includes("--label");
  const args = {
    fps: 30,
    quality: 16,
    width: 1280,
    height: 720,
    deviceScaleFactor: 1,
    out: defaultOutput,
    concept: "all",
    label: labelWasExplicit ? "final" : (presetName ?? "final"),
    start: 0,
    duration: null,
    keepFrames: false,
    append: false,
    preset: presetName ?? "custom",
    encoderPreset: "slow",
    contactSheet: true,
    ...renderPresets[presetName]
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--preset") i += 1;
    else if (arg === "--fps") args.fps = Number(argv[++i]);
    else if (arg === "--quality") args.quality = Number(argv[++i]);
    else if (arg === "--width") args.width = Number(argv[++i]);
    else if (arg === "--height") args.height = Number(argv[++i]);
    else if (arg === "--device-scale-factor") args.deviceScaleFactor = Number(argv[++i]);
    else if (arg === "--encoder-preset") args.encoderPreset = argv[++i];
    else if (arg === "--out") args.out = resolve(argv[++i]);
    else if (arg === "--concept") args.concept = argv[++i];
    else if (arg === "--label") args.label = argv[++i];
    else if (arg === "--start") args.start = Number(argv[++i]);
    else if (arg === "--duration") args.duration = Number(argv[++i]);
    else if (arg === "--keep-frames") args.keepFrames = true;
    else if (arg === "--contact-sheet") args.contactSheet = true;
    else if (arg === "--no-contact-sheet") args.contactSheet = false;
    else if (arg === "--append") args.append = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!Number.isFinite(args.fps) || args.fps <= 0) throw new Error("--fps must be a positive number.");
  if (!Number.isFinite(args.quality) || args.quality < 0 || args.quality > 51) throw new Error("--quality must be between 0 and 51.");
  if (!Number.isFinite(args.width) || args.width <= 0) throw new Error("--width must be a positive number.");
  if (!Number.isFinite(args.height) || args.height <= 0) throw new Error("--height must be a positive number.");
  if (!Number.isFinite(args.deviceScaleFactor) || args.deviceScaleFactor <= 0) throw new Error("--device-scale-factor must be a positive number.");
  if (!encoderPresets.has(args.encoderPreset)) {
    throw new Error(`--encoder-preset must be one of: ${[...encoderPresets].join(", ")}.`);
  }
  if (!Number.isFinite(args.start) || args.start < 0) throw new Error("--start must be zero or a positive number.");
  if (args.duration !== null && (!Number.isFinite(args.duration) || args.duration <= 0)) throw new Error("--duration must be a positive number.");
  return args;
}

function ensureInside(root, target) {
  const resolvedRoot = resolve(root);
  const resolvedTarget = resolve(target);
  if (resolvedTarget !== resolvedRoot && !resolvedTarget.startsWith(`${resolvedRoot}\\`) && !resolvedTarget.startsWith(`${resolvedRoot}/`)) {
    throw new Error(`Refusing to operate outside ${resolvedRoot}: ${resolvedTarget}`);
  }
  return resolvedTarget;
}

function cleanDirectory(root, target) {
  const safeTarget = ensureInside(root, target);
  if (existsSync(safeTarget)) rmSync(safeTarget, { recursive: true, force: true });
  mkdirSync(safeTarget, { recursive: true });
}

function run(command, args, cwd = deckDir) {
  const result = spawnSync(command, args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed\n${result.stdout}\n${result.stderr}`);
  }
  return result;
}

function contentType(filePath) {
  const types = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".woff2": "font/woff2"
  };
  return types[extname(filePath).toLowerCase()] ?? "application/octet-stream";
}

function startStaticServer(root) {
  const staticRoot = resolve(root);
  const server = createServer((request, response) => {
    try {
      const requestUrl = new URL(request.url ?? "/", "http://127.0.0.1");
      const requestedPath = decodeURIComponent(requestUrl.pathname === "/" ? "/index.html" : requestUrl.pathname);
      const filePath = resolve(staticRoot, `.${requestedPath}`);
      if (filePath !== staticRoot && !filePath.startsWith(`${staticRoot}\\`) && !filePath.startsWith(`${staticRoot}/`)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }
      const stat = statSync(filePath);
      if (!stat.isFile()) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }
      response.writeHead(200, { "Content-Type": contentType(filePath) });
      createReadStream(filePath).pipe(response);
    } catch (_) {
      response.writeHead(404);
      response.end("Not found");
    }
  });
  return new Promise((resolveServer) => {
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolveServer({ server, url: `http://127.0.0.1:${address.port}` });
    });
  });
}

function selectConcepts(selector) {
  if (selector === "all") return concepts;
  const requested = new Set(selector.split(",").map((item) => item.trim()).filter(Boolean));
  return concepts.filter((concept, index) => requested.has(concept.id) || requested.has(concept.shortTitle.toLowerCase()) || requested.has(String(index + 1)));
}

async function captureFrames(page, concept, frameDir, fps, start, duration) {
  const frameCount = Math.round(duration * fps);
  const stats = [];
  for (let frame = 0; frame < frameCount; frame += 1) {
    const seconds = start + frame / fps;
    const state = await page.evaluate(({ id, t }) => window.renderConceptFrame(id, t, { capture: true }), { id: concept.id, t: seconds });
    if (frame % Math.max(1, Math.floor(fps * 10)) === 0) stats.push(state);
    const file = join(frameDir, `frame_${String(frame).padStart(5, "0")}.png`);
    await page.screenshot({ path: file, animations: "disabled" });
  }
  return { frameCount, stats };
}

function encodeVideo(frameDir, outputFile, fps, quality, encoderPreset) {
  run("ffmpeg", [
    "-y",
    "-framerate", String(fps),
    "-i", join(frameDir, "frame_%05d.png"),
    "-c:v", "libx264",
    "-preset", encoderPreset,
    "-tune", "animation",
    "-pix_fmt", "yuv420p",
    "-vf", "scale=1280:720:flags=lanczos",
    "-r", String(fps),
    "-movflags", "+faststart",
    "-crf", String(quality),
    outputFile
  ]);
}

function createContactSheet(videoFile, sheetFile, duration) {
  const sampleRate = duration <= 20 ? "1" : "1/10";
  run("ffmpeg", [
    "-y",
    "-i", videoFile,
    "-vf", `fps=${sampleRate},scale=320:180:flags=lanczos,tile=4x3`,
    "-frames:v", "1",
    "-update", "1",
    sheetFile
  ]);
}

function probeVideo(videoFile) {
  const result = run("ffprobe", [
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,avg_frame_rate,nb_frames:format=duration,size",
    "-of", "json",
    videoFile
  ]);
  return JSON.parse(result.stdout);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const outputRoot = resolve(args.out, args.label);
  const frameRoot = resolve(outputRoot, "frames");
  const videoRoot = resolve(outputRoot, "videos");
  const reviewRoot = resolve(outputRoot, "review");
  mkdirSync(outputRoot, { recursive: true });
  cleanDirectory(outputRoot, frameRoot);
  mkdirSync(videoRoot, { recursive: true });
  mkdirSync(reviewRoot, { recursive: true });

  const selected = selectConcepts(args.concept);
  if (!selected.length) throw new Error(`No concepts matched ${args.concept}`);

  const staticServer = await startStaticServer(deckDir);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: args.width, height: args.height }, deviceScaleFactor: args.deviceScaleFactor });
  const manifestFile = join(outputRoot, "render-manifest.json");
  const manifest = args.append && existsSync(manifestFile) ? JSON.parse(readFileSync(manifestFile, "utf8")) : {
    generatedAt: new Date().toISOString(),
    label: args.label,
    preset: args.preset,
    fps: args.fps,
    quality: args.quality,
    width: args.width,
    height: args.height,
    deviceScaleFactor: args.deviceScaleFactor,
    encoderPreset: args.encoderPreset,
    contactSheet: args.contactSheet,
    videos: []
  };
  manifest.updatedAt = new Date().toISOString();

  try {
    for (const concept of selected) {
      const renderStart = args.start;
      const renderDuration = args.duration ?? (concept.runtimeSeconds - renderStart);
      if (renderStart >= concept.runtimeSeconds) throw new Error(`--start is outside ${concept.id} duration.`);
      if (renderStart + renderDuration > concept.runtimeSeconds + 0.0001) throw new Error(`Requested segment exceeds ${concept.id} duration.`);
      console.log(`Rendering ${concept.id} from ${renderStart}s for ${renderDuration}s at ${args.fps} fps (${args.preset}, ${args.encoderPreset}).`);
      const frameDir = join(frameRoot, concept.id);
      mkdirSync(frameDir, { recursive: true });
      const url = `${staticServer.url}/index.html?concept=${encodeURIComponent(concept.id)}&t=0`;
      await page.goto(url, { waitUntil: "networkidle" });
      await page.evaluate(async () => {
        if (document.fonts?.ready) await document.fonts.ready;
      });
      const capture = await captureFrames(page, concept, frameDir, args.fps, renderStart, renderDuration);
      const outputFile = join(videoRoot, `${concept.id}.mp4`);
      encodeVideo(frameDir, outputFile, args.fps, args.quality, args.encoderPreset);
      const sheetFile = args.contactSheet ? join(reviewRoot, `${concept.id}-contact-sheet.png`) : null;
      if (sheetFile) createContactSheet(outputFile, sheetFile, renderDuration);
      const probe = probeVideo(outputFile);
      manifest.videos = manifest.videos.filter((video) => video.id !== concept.id);
      manifest.videos.push({
        id: concept.id,
        title: concept.title,
        file: outputFile,
        contactSheet: sheetFile,
        durationTarget: renderDuration,
        segmentStart: renderStart,
        segmentDuration: renderDuration,
        frameCount: capture.frameCount,
        sampledStates: capture.stats,
        probe
      });
      if (!args.keepFrames) {
        rmSync(ensureInside(outputRoot, frameDir), { recursive: true, force: true });
      }
    }
  } finally {
    await browser.close();
    staticServer.server.close();
  }

  manifest.videos.sort((a, b) => a.id.localeCompare(b.id));
  writeFileSync(manifestFile, JSON.stringify(manifest, null, 2));
  console.log(`Rendered ${manifest.videos.length} videos to ${videoRoot}`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});

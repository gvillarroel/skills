#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { createReadStream, existsSync, mkdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { concepts, project } from "../src/concepts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");
const artifactsDir = resolve(projectDir, "artifacts");

const presets = {
  quick: { fps: 6, crf: 28, deviceScaleFactor: 1, encoderPreset: "veryfast", contactSheet: true },
  draft: { fps: 12, crf: 24, deviceScaleFactor: 1, encoderPreset: "veryfast", contactSheet: true },
  final: { fps: 30, crf: 18, deviceScaleFactor: 1, encoderPreset: "medium", contactSheet: true }
};

function parseArgs(argv) {
  const args = { preset: "final", id: "all", keepFrames: false, limit: null };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--preset") args.preset = argv[++i];
    else if (arg === "--id") args.id = argv[++i];
    else if (arg === "--limit") args.limit = Number(argv[++i]);
    else if (arg === "--keep-frames") args.keepFrames = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!presets[args.preset]) throw new Error(`Unknown preset: ${args.preset}`);
  if (args.limit !== null && (!Number.isInteger(args.limit) || args.limit <= 0)) throw new Error("--limit must be a positive integer");
  return { ...args, ...presets[args.preset] };
}

function selectedConcepts(args) {
  let selected = args.id === "all" ? concepts : concepts.filter((concept) => concept.id === args.id);
  if (!selected.length) throw new Error(`No concept matched --id ${args.id}`);
  if (args.limit !== null) selected = selected.slice(0, args.limit);
  return selected;
}

function ensureInside(root, target) {
  const safeRoot = resolve(root);
  const safeTarget = resolve(target);
  if (safeTarget !== safeRoot && !safeTarget.startsWith(`${safeRoot}\\`) && !safeTarget.startsWith(`${safeRoot}/`)) {
    throw new Error(`Refusing to operate outside ${safeRoot}: ${safeTarget}`);
  }
  return safeTarget;
}

function run(command, args, cwd = projectDir) {
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
    ".png": "image/png"
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

async function captureFrames(page, concept, args, frameDir) {
  const totalFrames = Math.round(concept.runtimeSeconds * args.fps);
  const sampledStates = [];
  const sampleEvery = Math.max(1, Math.floor(args.fps * 6));

  for (let frame = 0; frame < totalFrames; frame += 1) {
    const seconds = frame / args.fps;
    const state = await page.evaluate(({ id, t }) => window.renderConceptFrame(id, t, { capture: true }), {
      id: concept.id,
      t: seconds
    });
    if (frame % sampleEvery === 0 || frame === totalFrames - 1) sampledStates.push(state);
    await page.screenshot({
      path: join(frameDir, `frame_${String(frame).padStart(5, "0")}.png`),
      animations: "disabled"
    });
  }

  return { totalFrames, sampledStates };
}

function encodeVideo(frameDir, outputFile, args) {
  run("ffmpeg", [
    "-y",
    "-framerate",
    String(args.fps),
    "-i",
    join(frameDir, "frame_%05d.png"),
    "-c:v",
    "libx264",
    "-preset",
    args.encoderPreset,
    "-tune",
    "animation",
    "-pix_fmt",
    "yuv420p",
    "-vf",
    `scale=${project.width}:${project.height}:flags=lanczos`,
    "-r",
    String(args.fps),
    "-movflags",
    "+faststart",
    "-crf",
    String(args.crf),
    outputFile
  ]);
}

function createContactSheet(videoFile, sheetFile) {
  run("ffmpeg", [
    "-y",
    "-i",
    videoFile,
    "-vf",
    "fps=1/5,scale=384:216:flags=lanczos,tile=4x2",
    "-frames:v",
    "1",
    "-update",
    "1",
    sheetFile
  ]);
}

function probeVideo(videoFile) {
  const result = run("ffprobe", [
    "-v",
    "error",
    "-select_streams",
    "v:0",
    "-show_entries",
    "stream=width,height,avg_frame_rate,nb_frames:format=duration,size,bit_rate",
    "-of",
    "json",
    videoFile
  ]);
  return JSON.parse(result.stdout);
}

async function renderConcept(page, concept, args) {
  const frameDir = resolve(artifactsDir, "frames", `${args.preset}-${concept.id}`);
  const videoDir = resolve(artifactsDir, "videos", concept.id);
  const reviewDir = resolve(artifactsDir, "review", concept.id);
  const manifestDir = resolve(artifactsDir, "manifests", concept.id);
  const outputFile = join(videoDir, `${concept.id}.mp4`);
  const contactSheet = join(reviewDir, `${concept.id}-contact-sheet.jpg`);
  const manifestFile = join(manifestDir, `${concept.id}-render-manifest.json`);

  if (existsSync(frameDir)) rmSync(ensureInside(artifactsDir, frameDir), { recursive: true, force: true });
  mkdirSync(frameDir, { recursive: true });
  mkdirSync(videoDir, { recursive: true });
  mkdirSync(reviewDir, { recursive: true });
  mkdirSync(manifestDir, { recursive: true });

  const capture = await captureFrames(page, concept, args, frameDir);
  encodeVideo(frameDir, outputFile, args);
  if (args.contactSheet) createContactSheet(outputFile, contactSheet);
  const probe = probeVideo(outputFile);
  const manifest = {
    generatedAt: new Date().toISOString(),
    preset: args.preset,
    fps: args.fps,
    crf: args.crf,
    width: project.width,
    height: project.height,
    durationSeconds: concept.runtimeSeconds,
    frameCount: capture.totalFrames,
    sampledStates: capture.sampledStates,
    video: outputFile,
    contactSheet,
    probe
  };
  writeFileSync(manifestFile, JSON.stringify(manifest, null, 2));
  if (!args.keepFrames) rmSync(ensureInside(artifactsDir, frameDir), { recursive: true, force: true });
  return { id: concept.id, video: outputFile, contactSheet, manifest: manifestFile };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const selected = selectedConcepts(args);
  mkdirSync(artifactsDir, { recursive: true });
  const staticServer = await startStaticServer(projectDir);
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: project.width, height: project.height },
    deviceScaleFactor: args.deviceScaleFactor
  });
  try {
    await page.goto(`${staticServer.url}/index.html`, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      if (document.fonts?.ready) await document.fonts.ready;
    });
    const results = [];
    for (const concept of selected) {
      const result = await renderConcept(page, concept, args);
      results.push(result);
      console.log(`Rendered ${concept.id} -> ${result.video}`);
    }
    const aggregate = {
      generatedAt: new Date().toISOString(),
      preset: args.preset,
      rendered: results.length,
      results
    };
    mkdirSync(resolve(artifactsDir, "manifests"), { recursive: true });
    writeFileSync(resolve(artifactsDir, "manifests", `${args.preset}-render-index.json`), JSON.stringify(aggregate, null, 2));
  } finally {
    await browser.close();
    staticServer.server.close();
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});

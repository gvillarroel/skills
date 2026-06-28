#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { createReadStream, existsSync, mkdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import { video } from "../src/video-data.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");
const artifactsDir = resolve(projectDir, "artifacts");

const presets = {
  quick: { fps: 6, crf: 26, deviceScaleFactor: 1, encoderPreset: "veryfast", contactSheet: true },
  draft: { fps: 12, crf: 24, deviceScaleFactor: 1, encoderPreset: "veryfast", contactSheet: true },
  motion: { fps: 30, crf: 20, deviceScaleFactor: 1, encoderPreset: "faster", contactSheet: true },
  fast: { fps: 30, crf: 16, deviceScaleFactor: 2, encoderPreset: "veryfast", contactSheet: false },
  final: { fps: 30, crf: 16, deviceScaleFactor: 2, encoderPreset: "slow", contactSheet: true }
};

function parseArgs(argv) {
  const args = {
    preset: "final",
    start: 0,
    duration: video.durationSeconds,
    width: video.width,
    height: video.height,
    keepFrames: false
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--preset") args.preset = argv[++i];
    else if (arg === "--start") args.start = Number(argv[++i]);
    else if (arg === "--duration") args.duration = Number(argv[++i]);
    else if (arg === "--keep-frames") args.keepFrames = true;
    else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!presets[args.preset]) throw new Error(`Unknown preset: ${args.preset}`);
  if (!Number.isFinite(args.start) || args.start < 0) throw new Error("--start must be a non-negative number");
  if (!Number.isFinite(args.duration) || args.duration <= 0) throw new Error("--duration must be positive");
  return { ...args, ...presets[args.preset] };
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

async function captureFrames(page, args, frameDir) {
  const totalFrames = Math.round(args.duration * args.fps);
  const sampledStates = [];
  const sampleEvery = Math.max(1, Math.floor(args.fps * 4));

  for (let frame = 0; frame < totalFrames; frame += 1) {
    const seconds = args.start + frame / args.fps;
    const state = await page.evaluate(({ id, t }) => window.renderConceptFrame(id, t, { capture: true }), {
      id: video.id,
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

function outputBasename(args) {
  const full = args.start === 0 && Math.abs(args.duration - video.durationSeconds) < 0.001;
  if (full) return video.id;
  return `${video.id}-${args.preset}-${args.start.toFixed(1)}-${args.duration.toFixed(1)}`.replaceAll(".", "p");
}

function encodeVideo(frameDir, outputFile, args) {
  run("ffmpeg", [
    "-y",
    "-framerate", String(args.fps),
    "-i", join(frameDir, "frame_%05d.png"),
    "-c:v", "libx264",
    "-preset", args.encoderPreset,
    "-tune", "animation",
    "-pix_fmt", "yuv420p",
    "-vf", `scale=${video.width}:${video.height}:flags=lanczos`,
    "-r", String(args.fps),
    "-movflags", "+faststart",
    "-crf", String(args.crf),
    outputFile
  ]);
}

function createContactSheet(videoFile, sheetFile) {
  run("ffmpeg", [
    "-y",
    "-i", videoFile,
    "-vf", "fps=1/4,scale=320:180:flags=lanczos,tile=4x3",
    "-frames:v", "1",
    "-update", "1",
    sheetFile
  ]);
}

function probeVideo(videoFile) {
  const result = run("ffprobe", [
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,avg_frame_rate,nb_frames:format=duration,size,bit_rate",
    "-of", "json",
    videoFile
  ]);
  return JSON.parse(result.stdout);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const name = outputBasename(args);
  const frameDir = resolve(artifactsDir, "frames", `${args.preset}-${args.start}-${args.duration}`);
  const videoDir = resolve(artifactsDir, "videos");
  const reviewDir = resolve(artifactsDir, "review");
  const manifestDir = resolve(artifactsDir, "manifests");
  const outputFile = join(videoDir, `${name}.mp4`);
  const contactSheet = join(reviewDir, `${name}-contact-sheet.jpg`);
  const manifestFile = join(manifestDir, `${name}-render-manifest.json`);

  if (existsSync(frameDir)) rmSync(ensureInside(artifactsDir, frameDir), { recursive: true, force: true });
  mkdirSync(frameDir, { recursive: true });
  mkdirSync(videoDir, { recursive: true });
  mkdirSync(reviewDir, { recursive: true });
  mkdirSync(manifestDir, { recursive: true });

  const staticServer = await startStaticServer(projectDir);
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: args.width, height: args.height },
    deviceScaleFactor: args.deviceScaleFactor
  });

  try {
    await page.goto(`${staticServer.url}/index.html`, { waitUntil: "networkidle" });
    await page.evaluate(async () => {
      if (document.fonts?.ready) await document.fonts.ready;
    });
    const capture = await captureFrames(page, args, frameDir);
    encodeVideo(frameDir, outputFile, args);
    if (args.contactSheet) createContactSheet(outputFile, contactSheet);
    const probe = probeVideo(outputFile);
    const manifest = {
      generatedAt: new Date().toISOString(),
      preset: args.preset,
      fps: args.fps,
      crf: args.crf,
      width: video.width,
      height: video.height,
      durationSeconds: args.duration,
      startSeconds: args.start,
      frameCount: capture.totalFrames,
      sampledStates: capture.sampledStates,
      video: outputFile,
      contactSheet,
      probe
    };
    writeFileSync(manifestFile, JSON.stringify(manifest, null, 2));
  } finally {
    await browser.close();
    staticServer.server.close();
  }

  if (!args.keepFrames) rmSync(ensureInside(artifactsDir, frameDir), { recursive: true, force: true });
  console.log(`Rendered ${outputFile}`);
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
});

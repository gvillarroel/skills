#!/usr/bin/env node
import { createServer } from "node:http";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { createReadStream, existsSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { chromium } from "playwright";

const projectRoot = resolve(new URL("..", import.meta.url).pathname.slice(process.platform === "win32" ? 1 : 0));
const srcRoot = join(projectRoot, "src");
const nodeModulesRoot = join(projectRoot, "node_modules");
const outRoot = join(projectRoot, "artifacts", "video-renders", "final");
const frameDir = join(outRoot, "frames");
const videoDir = join(outRoot, "videos");
const reviewDir = join(outRoot, "review");
const manifestPath = join(outRoot, "render-manifest.json");
const notesPath = join(outRoot, "production-notes.md");

const presets = {
  smoke: { fps: 10, duration: 2, crf: 24, preset: "veryfast", keepFrames: false },
  final: { fps: 30, duration: 12, crf: 18, preset: "veryfast", keepFrames: false }
};

const args = new Map();
for (let i = 2; i < process.argv.length; i += 1) {
  const arg = process.argv[i];
  if (arg.startsWith("--")) {
    const key = arg.slice(2);
    const next = process.argv[i + 1];
    if (next && !next.startsWith("--")) {
      args.set(key, next);
      i += 1;
    } else {
      args.set(key, true);
    }
  }
}

const presetName = args.get("preset") || "final";
const preset = presets[presetName];
if (!preset) throw new Error(`Unknown preset: ${presetName}`);

const width = Number(args.get("width") || 1280);
const height = Number(args.get("height") || 720);
const fps = Number(args.get("fps") || preset.fps);
const duration = Number(args.get("duration") || preset.duration);
const frameCount = Math.round(duration * fps);
const videoPath = join(videoDir, `scene-composition-style-test-${presetName}.mp4`);
const contactSheetPath = join(reviewDir, `scene-composition-style-test-${presetName}-contact-sheet.jpg`);

const mimeByExt = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};

function run(command, commandArgs, options = {}) {
  return new Promise((resolveRun, reject) => {
    const child = spawn(command, commandArgs, {
      stdio: options.stdio || "pipe"
    });
    let stdout = "";
    let stderr = "";
    child.stdout?.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr?.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolveRun({ stdout, stderr });
      else reject(new Error(`${command} exited ${code}\n${stderr || stdout}`));
    });
  });
}

function startServer() {
  const server = createServer((req, res) => {
    const url = new URL(req.url || "/", "http://127.0.0.1");
    let pathname = decodeURIComponent(url.pathname);
    if (pathname === "/") pathname = "/index.html";
    const root = pathname.startsWith("/node_modules/") ? nodeModulesRoot : srcRoot;
    const rel = pathname.startsWith("/node_modules/")
      ? pathname.replace(/^\/node_modules\//, "")
      : pathname.replace(/^\//, "");
    const filePath = resolve(root, rel);
    if (!filePath.startsWith(root) || !existsSync(filePath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "content-type": mimeByExt[extname(filePath)] || "application/octet-stream" });
    createReadStream(filePath).pipe(res);
  });

  return new Promise((resolveServer, reject) => {
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolveServer({ server, url: `http://127.0.0.1:${address.port}/index.html?capture=1` });
    });
  });
}

async function main() {
  await mkdir(frameDir, { recursive: true });
  await mkdir(videoDir, { recursive: true });
  await mkdir(reviewDir, { recursive: true });
  await rm(frameDir, { recursive: true, force: true });
  await mkdir(frameDir, { recursive: true });

  const { server, url } = await startServer();
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  const validationStates = [];
  try {
    await page.goto(url, { waitUntil: "networkidle" });
    await page.waitForFunction(() => typeof window.renderFrame === "function");
    for (let frame = 0; frame < frameCount; frame += 1) {
      const seconds = frame / fps;
      const state = await page.evaluate((t) => window.renderFrame(t), seconds);
      if (frame % Math.max(1, Math.floor(fps)) === 0 || frame === frameCount - 1) validationStates.push(state);
      const file = join(frameDir, `frame_${String(frame).padStart(5, "0")}.png`);
      await page.screenshot({ path: file, type: "png" });
    }
  } finally {
    await browser.close();
    await new Promise((resolveClose) => server.close(resolveClose));
  }

  await run("ffmpeg", [
    "-y",
    "-framerate",
    String(fps),
    "-i",
    join(frameDir, "frame_%05d.png"),
    "-vf",
    "format=yuv420p",
    "-c:v",
    "libx264",
    "-preset",
    preset.preset,
    "-crf",
    String(preset.crf),
    "-movflags",
    "+faststart",
    videoPath
  ]);

  await run("ffmpeg", [
    "-y",
    "-i",
    videoPath,
    "-vf",
    "fps=1,scale=320:-1:flags=lanczos,tile=4x3",
    "-frames:v",
    "1",
    contactSheetPath
  ]);

  const ffprobe = await run("ffprobe", [
    "-v",
    "error",
    "-select_streams",
    "v:0",
    "-show_entries",
    "stream=width,height,avg_frame_rate,nb_frames,duration",
    "-of",
    "json",
    videoPath
  ]);
  const probe = JSON.parse(ffprobe.stdout);

  const manifest = {
    project: "scene-composition-style-test",
    preset: presetName,
    width,
    height,
    fps,
    duration,
    frameCount,
    videoPath,
    contactSheetPath,
    validationStates,
    ffprobe: probe
  };
  await writeFile(manifestPath, JSON.stringify(manifest, null, 2), "utf8");
  await writeFile(
    notesPath,
    [
      "# Production Notes",
      "",
      `- Preset: ${presetName}`,
      `- Runtime: HTML/SVG with D3-generated diagrams and Anime.js preview only; final capture uses deterministic timestamp rendering.`,
      "- D3 compositions: thirds force-network, flow-spine branch, golden/root before-after bars, radial rosette checklist.",
      `- Output: ${videoPath}`,
      `- Contact sheet: ${contactSheetPath}`,
      `- Frames: ${frameCount} at ${fps} fps`,
      "- Validation: ffprobe metadata captured in render-manifest.json.",
      "- Animation runtime policy: Anime.js preview only; final export is timestamp-driven."
    ].join("\n"),
    "utf8"
  );

  if (!preset.keepFrames && !args.has("keep-frames")) {
    await rm(frameDir, { recursive: true, force: true });
  }

  console.log(JSON.stringify({ videoPath, contactSheetPath, manifestPath, notesPath }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});

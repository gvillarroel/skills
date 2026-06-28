#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { video } from "../src/video-data.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");
const artifactsDir = resolve(projectDir, "artifacts");
const videoFile = resolve(artifactsDir, "videos", `${video.id}.mp4`);
const reviewDir = resolve(artifactsDir, "review");
const keyframeDir = resolve(reviewDir, "keyframes");
const manifestFile = resolve(artifactsDir, "manifests", `${video.id}-render-manifest.json`);

function run(command, args, cwd = projectDir) {
  const result = spawnSync(command, args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  return {
    status: result.status,
    stdout: result.stdout ?? "",
    stderr: result.stderr ?? ""
  };
}

function requiredRun(command, args) {
  const result = run(command, args);
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed\n${result.stdout}\n${result.stderr}`);
  }
  return result;
}

function probeVideo() {
  const result = requiredRun("ffprobe", [
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,avg_frame_rate,nb_frames:format=duration,size,bit_rate",
    "-of", "json",
    videoFile
  ]);
  return JSON.parse(result.stdout);
}

function scanVideo() {
  const result = run("ffmpeg", [
    "-hide_banner",
    "-nostats",
    "-i", videoFile,
    "-vf", "blackdetect=d=0.2:pix_th=0.08,freezedetect=n=-70dB:d=5",
    "-an",
    "-f",
    "null",
    "-"
  ]);
  const output = `${result.stdout}\n${result.stderr}`;
  return {
    status: result.status,
    blackSegments: output.split(/\r?\n/).filter((line) => line.includes("black_start")),
    freezeSegments: output.split(/\r?\n/).filter((line) => line.includes("freeze_start")),
    rawTail: output.split(/\r?\n/).slice(-16).join("\n")
  };
}

function createContactSheet() {
  const sheetFile = join(reviewDir, "contact-sheet.jpg");
  requiredRun("ffmpeg", [
    "-y",
    "-i", videoFile,
    "-vf", "fps=1/4,scale=320:180:flags=lanczos,tile=4x3",
    "-frames:v", "1",
    "-update", "1",
    sheetFile
  ]);
  return sheetFile;
}

function extractKeyframes() {
  mkdirSync(keyframeDir, { recursive: true });
  const times = [1, 6, 10, 15, 18, 23, 26, 32, 36, 41, 44, 47];
  const files = [];
  for (const time of times) {
    const file = join(keyframeDir, `${String(time).padStart(2, "0")}s.png`);
    requiredRun("ffmpeg", ["-y", "-ss", String(time), "-i", videoFile, "-frames:v", "1", "-vf", "scale=1280:720:flags=lanczos", file]);
    files.push(file);
  }
  return files;
}

function renderMarkdown(report) {
  const lines = [
    "# Plant Growth Explainer Review",
    "",
    `Reviewed at: ${report.reviewedAt}`,
    `Video: ${report.video}`,
    `Contact sheet: ${report.contactSheet}`,
    "",
    "## Automated Checks",
    "",
    `- Duration: ${report.duration.toFixed(3)} seconds, expected ${video.durationSeconds} seconds`,
    `- Resolution: ${report.width}x${report.height}`,
    `- Average frame rate: ${report.avgFrameRate}`,
    `- Frames: ${report.nbFrames}`,
    `- Black segments: ${report.blackSegments.length}`,
    `- Freeze segments: ${report.freezeSegments.length}`,
    `- Status: ${report.failures.length ? "needs work" : "pass"}`,
    "",
    "## Keyframes",
    ""
  ];
  for (const file of report.keyframes) lines.push(`- ${file}`);
  lines.push("");
  if (report.failures.length) {
    lines.push("## Failures", "");
    for (const failure of report.failures) lines.push(`- ${failure}`);
    lines.push("");
  }
  return `${lines.join("\n")}\n`;
}

function main() {
  if (!existsSync(videoFile)) throw new Error(`Missing video: ${videoFile}`);
  mkdirSync(reviewDir, { recursive: true });
  const manifest = existsSync(manifestFile) ? JSON.parse(readFileSync(manifestFile, "utf8")) : null;
  const probe = probeVideo();
  const stream = probe.streams?.[0] ?? {};
  const scan = scanVideo();
  const contactSheet = createContactSheet();
  const keyframes = extractKeyframes();
  const duration = Number(probe.format?.duration ?? 0);
  const failures = [];

  if (Math.abs(duration - video.durationSeconds) > 0.25) failures.push(`Duration ${duration.toFixed(3)} is outside tolerance.`);
  if (Number(stream.width) !== video.width || Number(stream.height) !== video.height) {
    failures.push(`Resolution is ${stream.width}x${stream.height}, expected ${video.width}x${video.height}.`);
  }
  if (scan.status !== 0) failures.push("ffmpeg black/freeze scan returned nonzero status.");
  if (scan.blackSegments.length) failures.push(`Black segments detected: ${scan.blackSegments.length}.`);
  if (scan.freezeSegments.length) failures.push(`Freeze segments detected: ${scan.freezeSegments.length}.`);

  const report = {
    reviewedAt: new Date().toISOString(),
    video: videoFile,
    contactSheet,
    manifest: manifestFile,
    manifestPreset: manifest?.preset ?? null,
    duration,
    width: Number(stream.width),
    height: Number(stream.height),
    avgFrameRate: stream.avg_frame_rate,
    nbFrames: stream.nb_frames,
    size: Number(probe.format?.size ?? 0),
    bitRate: Number(probe.format?.bit_rate ?? 0),
    blackSegments: scan.blackSegments,
    freezeSegments: scan.freezeSegments,
    keyframes,
    failures
  };

  writeFileSync(join(reviewDir, "review.json"), JSON.stringify(report, null, 2));
  writeFileSync(join(reviewDir, "review.md"), renderMarkdown(report));
  console.log(renderMarkdown(report));
  if (failures.length) process.exit(1);
}

main();

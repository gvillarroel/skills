#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { concepts, project } from "../src/concepts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");
const artifactsDir = resolve(projectDir, "artifacts");

function parseArgs(argv) {
  const args = { id: "all" };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--id") args.id = argv[++i];
    else throw new Error(`Unknown argument: ${arg}`);
  }
  return args;
}

function selectedConcepts(args) {
  const selected = args.id === "all" ? concepts : concepts.filter((concept) => concept.id === args.id);
  if (!selected.length) throw new Error(`No concept matched --id ${args.id}`);
  return selected;
}

function run(command, args, cwd = projectDir) {
  const result = spawnSync(command, args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  return { status: result.status, stdout: result.stdout ?? "", stderr: result.stderr ?? "" };
}

function requiredRun(command, args) {
  const result = run(command, args);
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed\n${result.stdout}\n${result.stderr}`);
  }
  return result;
}

function probeVideo(videoFile) {
  const result = requiredRun("ffprobe", [
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

function scanVideo(videoFile) {
  const result = run("ffmpeg", [
    "-hide_banner",
    "-nostats",
    "-i",
    videoFile,
    "-vf",
    "blackdetect=d=0.2:pix_th=0.08,freezedetect=n=-70dB:d=6",
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

function createContactSheet(videoFile, sheetFile) {
  requiredRun("ffmpeg", [
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

function extractKeyframes(videoFile, keyframeDir, concept) {
  mkdirSync(keyframeDir, { recursive: true });
  const times = [1, 8, 16, 24, 32, 40].filter((time) => time < concept.runtimeSeconds);
  const files = [];
  for (const time of times) {
    const file = join(keyframeDir, `${String(time).padStart(2, "0")}s.png`);
    requiredRun("ffmpeg", ["-y", "-ss", String(time), "-i", videoFile, "-frames:v", "1", "-vf", "scale=1280:720:flags=lanczos", file]);
    files.push(file);
  }
  return files;
}

function reviewConcept(concept) {
  const videoFile = resolve(artifactsDir, "videos", concept.id, `${concept.id}.mp4`);
  const reviewDir = resolve(artifactsDir, "review", concept.id);
  const keyframeDir = resolve(reviewDir, "keyframes");
  const contactSheet = resolve(reviewDir, `${concept.id}-contact-sheet.jpg`);
  mkdirSync(reviewDir, { recursive: true });

  if (!existsSync(videoFile)) {
    return {
      id: concept.id,
      video: videoFile,
      status: "missing",
      failures: [`Missing video: ${videoFile}`]
    };
  }

  const probe = probeVideo(videoFile);
  const stream = probe.streams?.[0] ?? {};
  const scan = scanVideo(videoFile);
  createContactSheet(videoFile, contactSheet);
  const keyframes = extractKeyframes(videoFile, keyframeDir, concept);
  const duration = Number(probe.format?.duration ?? 0);
  const failures = [];

  if (Math.abs(duration - concept.runtimeSeconds) > 0.25) failures.push(`Duration ${duration.toFixed(3)} outside tolerance for ${concept.runtimeSeconds}s.`);
  if (Number(stream.width) !== project.width || Number(stream.height) !== project.height) {
    failures.push(`Resolution ${stream.width}x${stream.height}, expected ${project.width}x${project.height}.`);
  }
  if (scan.status !== 0) failures.push("ffmpeg black/freeze scan returned nonzero status.");
  if (scan.blackSegments.length) failures.push(`Black segments detected: ${scan.blackSegments.length}.`);
  if (scan.freezeSegments.length) failures.push(`Freeze segments detected: ${scan.freezeSegments.length}.`);

  const report = {
    id: concept.id,
    title: concept.title,
    reviewedAt: new Date().toISOString(),
    video: videoFile,
    contactSheet,
    keyframes,
    status: failures.length ? "needs-work" : "pass",
    duration,
    width: Number(stream.width),
    height: Number(stream.height),
    avgFrameRate: stream.avg_frame_rate,
    nbFrames: stream.nb_frames,
    size: Number(probe.format?.size ?? 0),
    bitRate: Number(probe.format?.bit_rate ?? 0),
    blackSegments: scan.blackSegments,
    freezeSegments: scan.freezeSegments,
    failures
  };
  writeFileSync(resolve(reviewDir, "review.json"), JSON.stringify(report, null, 2));
  writeFileSync(resolve(reviewDir, "review.md"), renderConceptMarkdown(report));
  return report;
}

function renderConceptMarkdown(report) {
  const lines = [
    `# ${report.title} Review`,
    "",
    `Video: ${report.video}`,
    `Contact sheet: ${report.contactSheet}`,
    `Status: ${report.status}`,
    "",
    "## Automated Checks",
    "",
    `- Duration: ${Number(report.duration ?? 0).toFixed(3)} seconds`,
    `- Resolution: ${report.width ?? "n/a"}x${report.height ?? "n/a"}`,
    `- Average frame rate: ${report.avgFrameRate ?? "n/a"}`,
    `- Frames: ${report.nbFrames ?? "n/a"}`,
    `- Black segments: ${report.blackSegments?.length ?? 0}`,
    `- Freeze segments: ${report.freezeSegments?.length ?? 0}`,
    "",
    "## Keyframes",
    ""
  ];
  for (const file of report.keyframes ?? []) lines.push(`- ${file}`);
  if (report.failures?.length) {
    lines.push("", "## Failures", "");
    for (const failure of report.failures) lines.push(`- ${failure}`);
  }
  return `${lines.join("\n")}\n`;
}

function renderAggregateMarkdown(reports) {
  const failures = reports.flatMap((report) => report.failures.map((failure) => `${report.id}: ${failure}`));
  const lines = [
    "# AI Code Assistant Concepts Review",
    "",
    `Reviewed at: ${new Date().toISOString()}`,
    `Videos reviewed: ${reports.length}`,
    `Status: ${failures.length ? "needs-work" : "pass"}`,
    "",
    "| Video | Status | Duration | Resolution | Frames |",
    "|---|---|---:|---|---:|"
  ];
  for (const report of reports) {
    lines.push(`| ${report.id} | ${report.status} | ${Number(report.duration ?? 0).toFixed(3)} | ${report.width ?? "n/a"}x${report.height ?? "n/a"} | ${report.nbFrames ?? "n/a"} |`);
  }
  if (failures.length) {
    lines.push("", "## Failures", "");
    for (const failure of failures) lines.push(`- ${failure}`);
  }
  return `${lines.join("\n")}\n`;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const selected = selectedConcepts(args);
  const reports = selected.map(reviewConcept);
  const aggregateDir = resolve(artifactsDir, "review");
  mkdirSync(aggregateDir, { recursive: true });
  writeFileSync(resolve(aggregateDir, "review-all.json"), JSON.stringify({ reviewedAt: new Date().toISOString(), reports }, null, 2));
  const markdown = renderAggregateMarkdown(reports);
  writeFileSync(resolve(aggregateDir, "review-all.md"), markdown);
  console.log(markdown);
  if (reports.some((report) => report.failures.length)) process.exit(1);
}

main();

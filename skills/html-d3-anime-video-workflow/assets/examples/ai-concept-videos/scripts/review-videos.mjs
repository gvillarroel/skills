#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const deckDir = resolve(scriptDir, "..");
const skillDir = resolve(deckDir, "..", "..", "..");
const defaultArtifactRoot = resolve(
  process.env.AI_CONCEPT_VIDEO_ARTIFACTS_ROOT
    || join(tmpdir(), "codex-skill-artifacts", "html-d3-anime-video-workflow", "ai-concept-videos"),
);
const defaultRoot = resolve(defaultArtifactRoot, "video-renders", "final");
const { concepts } = await import(pathToFileURL(join(deckDir, "concepts.js")).href);

function usage() {
  return [
    "Review videos rendered from the bundled AI concept video fixture.",
    "",
    "Usage:",
    "  node scripts/review-videos.mjs [options]",
    "",
    "Options:",
    "  --root <directory>            Render pass root containing render-manifest.json.",
    "  --pass <name>                 Review report suffix; default: final.",
    "  --concept <id[,id...]>        Concept id, short title, one-based index, or all.",
    "  --dry-run                     Validate selection and paths without reading or writing artifacts.",
    "  --help",
    "",
    "The default review root is outside the skill bundle:",
    "  " + defaultRoot,
    "Override its base with AI_CONCEPT_VIDEO_ARTIFACTS_ROOT or pass --root.",
  ].join("\n");
}

function valueAfter(argv, index, option) {
  const value = argv[index + 1];
  if (value === undefined || value.startsWith("--")) {
    throw new Error(option + " requires a value.");
  }
  return value;
}

function parseArgs(argv) {
  const args = {
    root: defaultRoot,
    pass: "final",
    concept: "all",
    dryRun: false,
    help: false,
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--root") args.root = resolve(valueAfter(argv, i++, arg));
    else if (arg === "--pass") args.pass = valueAfter(argv, i++, arg);
    else if (arg === "--concept") args.concept = valueAfter(argv, i++, arg);
    else if (arg === "--dry-run") args.dryRun = true;
    else if (arg === "--help" || arg === "-h") args.help = true;
    else throw new Error("Unknown argument: " + arg);
  }
  return args;
}

function isWithin(root, target) {
  const relation = relative(resolve(root), resolve(target));
  return relation === "" || (!relation.startsWith("..") && !isAbsolute(relation));
}

function requireExternalOutput(target, option) {
  const resolvedTarget = resolve(target);
  if (isWithin(skillDir, resolvedTarget)) {
    throw new Error(option + " must be outside the read-only skill bundle: " + skillDir);
  }
  return resolvedTarget;
}

function run(command, args, cwd = deckDir) {
  const result = spawnSync(command, args, { cwd, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  return {
    status: result.status,
    stdout: result.stdout || "",
    stderr: result.stderr || "",
  };
}

function probeVideo(videoFile) {
  const result = run("ffprobe", [
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,avg_frame_rate,nb_frames:format=duration,size,bit_rate",
    "-of", "json",
    videoFile,
  ]);
  if (result.status !== 0) throw new Error("ffprobe failed for " + videoFile + "\n" + result.stderr);
  return JSON.parse(result.stdout);
}

function scanVideo(videoFile) {
  const result = run("ffmpeg", [
    "-hide_banner",
    "-nostats",
    "-i", videoFile,
    "-vf", "blackdetect=d=0.2:pix_th=0.08,freezedetect=n=-70dB:d=8",
    "-an",
    "-f", "null",
    "-",
  ]);
  const output = result.stdout + "\n" + result.stderr;
  return {
    status: result.status,
    blackSegments: output.split(/\r?\n/).filter((line) => line.includes("black_start")),
    freezeSegments: output.split(/\r?\n/).filter((line) => line.includes("freeze_start")),
    rawTail: output.split(/\r?\n/).slice(-12).join("\n"),
  };
}

function createContactSheet(videoFile, sheetFile, duration) {
  const sampleRate = duration <= 20 ? "1" : "1/10";
  const result = run("ffmpeg", [
    "-y",
    "-i", videoFile,
    "-vf", "fps=" + sampleRate + ",scale=320:180:flags=lanczos,tile=4x3",
    "-frames:v", "1",
    "-update", "1",
    sheetFile,
  ]);
  if (result.status !== 0) throw new Error("contact sheet failed for " + videoFile + "\n" + result.stderr);
}

function numericDuration(probe) {
  return Number(probe.format?.duration || 0);
}

function stream(probe) {
  return probe.streams?.[0] || {};
}

function reviewConcept(root, concept, manifestVideo) {
  const videoFile = join(root, "videos", concept.id + ".mp4");
  if (!existsSync(videoFile)) {
    return { id: concept.id, title: concept.title, missing: true, failures: ["Missing video: " + videoFile] };
  }
  const probe = probeVideo(videoFile);
  const videoStream = stream(probe);
  const scan = scanVideo(videoFile);
  const sheetFile = join(root, "review", concept.id + "-contact-sheet.png");
  mkdirSync(dirname(sheetFile), { recursive: true });
  const duration = numericDuration(probe);
  const expectedDuration = Number(manifestVideo?.durationTarget ?? concept.runtimeSeconds);
  createContactSheet(videoFile, sheetFile, expectedDuration);
  const failures = [];
  if (Math.abs(duration - expectedDuration) > 0.18) {
    failures.push("Duration " + duration.toFixed(3) + "s is not within tolerance of " + expectedDuration + "s.");
  }
  if (Number(videoStream.width) !== 1280 || Number(videoStream.height) !== 720) {
    failures.push("Resolution is " + videoStream.width + "x" + videoStream.height + ", expected 1280x720.");
  }
  if (scan.status !== 0) failures.push("ffmpeg scan returned a nonzero status.");
  if (scan.blackSegments.length) failures.push("Black segments detected: " + scan.blackSegments.length + ".");
  if (scan.freezeSegments.length) failures.push("Freeze segments detected: " + scan.freezeSegments.length + ".");

  return {
    id: concept.id,
    title: concept.title,
    file: videoFile,
    contactSheet: sheetFile,
    expectedDuration,
    duration,
    width: Number(videoStream.width),
    height: Number(videoStream.height),
    avgFrameRate: videoStream.avg_frame_rate,
    nbFrames: videoStream.nb_frames,
    blackSegments: scan.blackSegments,
    freezeSegments: scan.freezeSegments,
    failures,
  };
}

function selectConcepts(selector) {
  if (selector === "all") return concepts;
  const requested = new Set(selector.split(",").map((item) => item.trim()).filter(Boolean));
  return concepts.filter((concept, index) => (
    requested.has(concept.id)
    || requested.has(concept.shortTitle.toLowerCase())
    || requested.has(String(index + 1))
  ));
}

function renderMarkdown(report) {
  const lines = [
    "# AI Concept Video Review - " + report.pass,
    "",
    "Root: " + report.root,
    "Reviewed at: " + report.reviewedAt,
    "",
    "## Summary",
    "",
    "- Videos reviewed: " + report.results.length,
    "- Failures: " + report.results.reduce((total, item) => total + item.failures.length, 0),
    "",
    "## Full Timeline Checks",
    "",
  ];
  for (const result of report.results) {
    lines.push("### " + result.id);
    if (result.missing) {
      lines.push("- Missing: " + result.failures.join("; "));
      lines.push("");
      continue;
    }
    lines.push("- Duration: " + result.duration.toFixed(3) + " seconds");
    lines.push("- Expected duration: " + result.expectedDuration.toFixed(3) + " seconds");
    lines.push("- Resolution: " + result.width + "x" + result.height);
    lines.push("- Average frame rate: " + result.avgFrameRate);
    lines.push("- Frames: " + result.nbFrames);
    lines.push("- Contact sheet: " + result.contactSheet);
    lines.push("- Black segments: " + result.blackSegments.length);
    lines.push("- Freeze segments: " + result.freezeSegments.length);
    lines.push("- Status: " + (result.failures.length ? "needs work" : "pass"));
    if (result.failures.length) {
      for (const failure of result.failures) lines.push("  - " + failure);
    }
    lines.push("");
  }
  return lines.join("\n") + "\n";
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }

  const root = requireExternalOutput(args.root, "--root");
  const selected = selectConcepts(args.concept);
  if (!selected.length) throw new Error("No concepts matched " + args.concept);

  if (args.dryRun) {
    console.log(JSON.stringify({
      passed: true,
      deckDir,
      skillDir,
      root,
      pass: args.pass,
      selectedConcepts: selected.map((concept) => concept.id),
      writesPerformed: false,
    }, null, 2));
    return;
  }

  const manifestFile = join(root, "render-manifest.json");
  if (!existsSync(manifestFile)) throw new Error("Missing render manifest: " + manifestFile);
  const renderManifest = JSON.parse(readFileSync(manifestFile, "utf8"));
  const manifestVideos = new Map((renderManifest.videos || []).map((video) => [video.id, video]));
  const report = {
    pass: args.pass,
    root,
    reviewedAt: new Date().toISOString(),
    renderManifest: manifestFile,
    results: selected.map((concept) => reviewConcept(root, concept, manifestVideos.get(concept.id))),
  };
  const reportDir = join(root, "review");
  mkdirSync(reportDir, { recursive: true });
  writeFileSync(join(reportDir, "review-" + args.pass + ".json"), JSON.stringify(report, null, 2));
  writeFileSync(join(reportDir, "review-" + args.pass + ".md"), renderMarkdown(report));
  const failures = report.results.flatMap((result) => (
    result.failures.map((failure) => result.id + ": " + failure)
  ));
  console.log("Reviewed " + report.results.length + " videos for pass " + args.pass + ".");
  if (failures.length) {
    console.error(failures.join("\n"));
    process.exit(1);
  }
}

try {
  main();
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exit(1);
}

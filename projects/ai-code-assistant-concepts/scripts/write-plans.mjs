#!/usr/bin/env node
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { concepts, project, sources } from "../src/concepts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");

function write(relativePath, content) {
  const file = resolve(projectDir, relativePath);
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, `${content.trimEnd()}\n`, "utf8");
}

function asJson(value) {
  return JSON.stringify(value, null, 2);
}

function timeRange(index, total) {
  const sceneDuration = project.runtimeSeconds / project.sceneCount;
  const start = index * sceneDuration;
  const end = start + sceneDuration;
  return `${start.toFixed(1)}-${end.toFixed(1)}s`;
}

function videoBrief(concept) {
  const sceneLines = concept.scenes
    .map((scene, index) => {
      const terms = scene.terms.join(", ");
      return `| ${timeRange(index)} | ${scene.beat} | ${scene.headline} | ${scene.micro} | ${terms} |`;
    })
    .join("\n");

  return `# ${concept.title}

Project: ${project.title}
Video ID: ${concept.id}
Runtime: ${project.runtimeSeconds} seconds

## Learning Objective

${concept.thesis}

## Reused Symbolic Language

- Work packet: moving prompt, task, or data unit.
- Blue context box: visible information available to a model or agent.
- Green check: verified or allowed result.
- Red shield: policy, permission, guardrail, or governance boundary.
- Teal bus: standardized connection surface.
- Amber meter: cost, latency, or operational load.

## Scene Plan

| Time | Beat | Headline | Supporting idea | Screen terms |
|---|---|---|---|---|
${sceneLines}

## Production Note

This module is intentionally compact and visual-first. Exact product prices, plan limits, and plan names are kept in source notes instead of on-screen copy because those facts change quickly.
`;
}

function shotContract(concept) {
  return {
    projectId: project.id,
    videoId: concept.id,
    runtimeSeconds: project.runtimeSeconds,
    resolution: { width: project.width, height: project.height },
    primaryObjective: concept.thesis,
    shots: concept.scenes.map((scene, index) => ({
      id: `${concept.id}-shot-${index + 1}`,
      timeRange: timeRange(index),
      beat: scene.beat,
      requiredOnScreenText: [scene.headline, ...scene.terms],
      visualFocus: `${concept.kind} metaphor with shared work packet and concept rail`,
      acceptance: [
        "Frame is nonblank and uses the active concept accent.",
        "Headline and three term chips are visible.",
        "Shared work packet appears before the bottom concept rail.",
        "The scene can be understood without voiceover."
      ]
    }))
  };
}

function compositionPlan(concept) {
  return {
    projectId: project.id,
    videoId: concept.id,
    compositionArmature: "dominant left visual, right explanation panel, bottom sequence rail",
    hierarchy: [
      "Concept title and current beat",
      "Main visual metaphor",
      "Right-side headline and microcopy",
      "Term chips and shared concept rail"
    ],
    reusableAssets: project.recurringSymbols,
    sceneComposition: concept.scenes.map((scene, index) => ({
      sceneId: `${concept.id}-scene-${index + 1}`,
      timeRange: timeRange(index),
      focalObject: scene.headline,
      motionCue: "The work packet or active node moves to the next relevant boundary.",
      contrastCue: `Active state uses ${concept.shortTitle} accent; inactive states use neutral line work.`
    })),
    critiqueChecklist: [
      "No text depends on voiceover to be understandable.",
      "The active visual focus matches the current beat.",
      "Recurring symbols keep the same meaning across all videos.",
      "The right panel does not compete with the main visual.",
      "The bottom rail identifies the module without becoming a second narrative."
    ]
  };
}

function transitionPlan(concept) {
  return {
    projectId: project.id,
    videoId: concept.id,
    recurringTransitionDevice: "The work packet persists while the main metaphor changes.",
    internalTransitions: concept.scenes.slice(1).map((scene, index) => ({
      fromBeat: concept.scenes[index].beat,
      toBeat: scene.beat,
      time: `${((index + 1) * project.runtimeSeconds / project.sceneCount).toFixed(1)}s`,
      action: "Retain title, concept rail, and work packet; update the main metaphor and right-panel copy.",
      validation: "A screenshot 0.3 seconds before and after the transition should show continuity rather than a visual reset."
    })),
    crossVideoTransition: {
      from: concept.order === 1 ? "series opening" : concepts[concept.order - 2].id,
      to: concept.order === concepts.length ? "series close" : concepts[concept.order].id,
      action: "The same work packet and bottom sequence rail establish continuity across modules."
    }
  };
}

function sourcePackage() {
  return {
    projectId: project.id,
    title: project.title,
    createdFor: "Short instructional videos about AI code assistant concepts.",
    checkedDate: project.checkedDate,
    productionAssumptions: [
      "Each video is compact and visual-first.",
      "Exact prices and product limits are treated as volatile and are not encoded on-screen.",
      "The primary deliverable is a coherent multi-video set, not a single monolithic lecture."
    ],
    sourceMaterialPolicy: [
      "Use official documentation for volatile product claims.",
      "Use the user's report as the content outline and dependency map.",
      "Keep reusable visual primitives consistent across all videos."
    ],
    concepts: concepts.map((concept) => ({
      id: concept.id,
      title: concept.title,
      objective: concept.thesis,
      kind: concept.kind,
      scenes: concept.scenes.map((scene) => ({
        beat: scene.beat,
        headline: scene.headline,
        micro: scene.micro,
        terms: scene.terms
      }))
    })),
    sources
  };
}

function storyboard() {
  const sections = concepts.map((concept) => {
    const rows = concept.scenes
      .map((scene, index) => `| ${timeRange(index)} | ${scene.headline} | ${scene.micro} | ${scene.terms.join(", ")} |`)
      .join("\n");
    return `## ${String(concept.order).padStart(2, "0")}. ${concept.title}

Learning objective: ${concept.thesis}

| Time | Screen headline | Supporting idea | Term chips |
|---|---|---|---|
${rows}`;
  });
  return `# ${project.title} Storyboard

This storyboard is the global dependency map for the fifteen compact concept videos. Each video keeps one learning objective and reuses the same symbolic language.

${sections.join("\n\n")}
`;
}

function globalShotContract() {
  return {
    projectId: project.id,
    runtimePerVideoSeconds: project.runtimeSeconds,
    resolution: { width: project.width, height: project.height },
    videoCount: concepts.length,
    totalRuntimeSeconds: concepts.length * project.runtimeSeconds,
    videos: concepts.map((concept) => shotContract(concept))
  };
}

function globalCompositionPlan() {
  return {
    projectId: project.id,
    narrativeContinuity: project.visualThesis,
    recurringSymbols: project.recurringSymbols,
    compositionSystem: "Left visual metaphor plus right explanatory panel plus bottom series rail.",
    videos: concepts.map((concept) => ({
      id: concept.id,
      title: concept.title,
      kind: concept.kind,
      accent: concept.accent,
      objective: concept.thesis
    }))
  };
}

function globalTransitionPlan() {
  return {
    projectId: project.id,
    transitionThesis: "Continuity comes from retaining the work packet, top identity, and bottom rail while changing the domain metaphor.",
    betweenVideos: concepts.map((concept, index) => ({
      from: concept.id,
      to: concepts[index + 1]?.id ?? "series end",
      device: "The bottom rail advances one node and the work packet reappears in the new metaphor."
    }))
  };
}

function researchNotes() {
  const lines = [
    `# ${project.title} Research Notes`,
    "",
    `Checked date: ${project.checkedDate}`,
    "",
    "The videos avoid exact current prices or plan limits in on-screen text. These sources support the conceptual claims and provide places to verify live product facts before a future update.",
    "",
    "| Source | URL | Use in package |",
    "|---|---|---|"
  ];
  for (const source of sources) lines.push(`| ${source.label} | ${source.url} | ${source.note} |`);
  return lines.join("\n");
}

function readme() {
  return `# ${project.title}

This project generates a coherent set of fifteen compact instructional videos about AI code assistant concepts.

## Outputs

- Per-video planning folders: \`videos/<video-id>/\`
- Rendered MP4s: \`artifacts/videos/<video-id>/<video-id>.mp4\`
- Review reports: \`artifacts/review/<video-id>/\`
- Smoke screenshots: \`artifacts/screenshots/smoke/<video-id>/\`

## Commands

- \`npm run plans\`: regenerate briefs, contracts, composition plans, and transition plans.
- \`npm run validate\`: validate data shape and generated planning files.
- \`npm run smoke\`: render representative browser frames for every module.
- \`npm run render:quick\`: create low-frame-rate MP4s for critique.
- \`npm run render:final\`: create final MP4s.
- \`npm run review\`: run ffprobe, black/freeze scans, keyframe extraction, and review reports.
`;
}

function productionNotes() {
  return `# Production Notes

## Direction

The package treats each concept as a compact visual module. The same work packet moves through every video so the audience sees a single system becoming more complete: model, billing, probability, agent loop, guardrail, harness, hook, plugin, skill, MCP, product alternatives, observability, instruction layers, tool permissions, and data governance.

## Deliberate Choices

- Runtime is ${project.runtimeSeconds} seconds per module to make the full set reviewable in one pass.
- Videos are silent and visual-first; every module has enough on-screen structure to stand alone.
- Exact volatile pricing and plan limits are documented in research notes rather than animated into the final frames.
- The right-side panel is consistent across videos so the left-side metaphor can vary without changing the reading path.

## Improvement Loop

The expected critique loop is:

1. Generate plans from the concept data.
2. Smoke-test representative frames for browser errors, blank frames, and composition bounds.
3. Render quick MP4s and inspect contact sheets.
4. Fix visual composition or data copy problems.
5. Render final MP4s and run ffprobe, blackdetect, freezedetect, and keyframe extraction.
6. Promote reusable lessons to the owning video workflow skill.
`;
}

function main() {
  write("README.md", readme());
  write("source-package.json", asJson(sourcePackage()));
  write("storyboard.md", storyboard());
  write("shot-contract.json", asJson(globalShotContract()));
  write("composition-plan.json", asJson(globalCompositionPlan()));
  write("transition-plan.json", asJson(globalTransitionPlan()));
  write("research-notes.md", researchNotes());
  write("production-notes.md", productionNotes());

  for (const concept of concepts) {
    const base = `videos/${concept.id}`;
    write(`${base}/brief.md`, videoBrief(concept));
    write(`${base}/shot-contract.json`, asJson(shotContract(concept)));
    write(`${base}/composition-plan.json`, asJson(compositionPlan(concept)));
    write(`${base}/transition-plan.json`, asJson(transitionPlan(concept)));
  }

  console.log(`Generated plans for ${concepts.length} videos in ${project.id}.`);
}

main();

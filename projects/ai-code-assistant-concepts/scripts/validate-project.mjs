#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { concepts, project, sources } from "../src/concepts.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectDir = resolve(__dirname, "..");

function fail(message) {
  throw new Error(message);
}

function assertFile(relativePath) {
  const file = resolve(projectDir, relativePath);
  if (!existsSync(file)) fail(`Missing expected file: ${relativePath}`);
  return file;
}

function readJson(relativePath) {
  const file = assertFile(relativePath);
  return JSON.parse(readFileSync(file, "utf8"));
}

function validateConcepts() {
  const ids = new Set();
  concepts.forEach((concept, index) => {
    if (!/^[a-z0-9-]+$/.test(concept.id)) fail(`Invalid concept id: ${concept.id}`);
    if (ids.has(concept.id)) fail(`Duplicate concept id: ${concept.id}`);
    ids.add(concept.id);
    if (concept.order !== index + 1) fail(`Order mismatch for ${concept.id}`);
    if (!concept.title || !concept.shortTitle || !concept.kind || !concept.thesis) fail(`Missing required concept fields for ${concept.id}`);
    if (concept.runtimeSeconds !== project.runtimeSeconds) fail(`Runtime mismatch for ${concept.id}`);
    if (concept.scenes.length !== project.sceneCount) fail(`Scene count mismatch for ${concept.id}`);
    concept.scenes.forEach((scene, sceneIndex) => {
      if (scene.index !== sceneIndex) fail(`Scene index mismatch in ${concept.id}`);
      if (!scene.headline || !scene.micro) fail(`Missing scene copy in ${concept.id} scene ${sceneIndex + 1}`);
      if (!Array.isArray(scene.terms) || scene.terms.length !== 3) fail(`Each scene must have exactly three term chips in ${concept.id}`);
      if (scene.headline.length > 62) fail(`Headline too long in ${concept.id}: ${scene.headline}`);
      if (scene.micro.length > 132) fail(`Microcopy too long in ${concept.id}: ${scene.micro}`);
    });
  });
  if (concepts.length !== 15) fail(`Expected 15 concepts, found ${concepts.length}`);
}

function validatePlans() {
  const sourcePackage = readJson("source-package.json");
  if (sourcePackage.concepts?.length !== concepts.length) fail("source-package.json concept count mismatch");
  const globalContract = readJson("shot-contract.json");
  if (globalContract.videoCount !== concepts.length) fail("shot-contract.json video count mismatch");
  assertFile("storyboard.md");
  assertFile("composition-plan.json");
  assertFile("transition-plan.json");
  assertFile("research-notes.md");
  assertFile("production-notes.md");
  assertFile("README.md");

  for (const concept of concepts) {
    const base = `videos/${concept.id}`;
    assertFile(`${base}/brief.md`);
    const contract = readJson(`${base}/shot-contract.json`);
    if (contract.shots?.length !== project.sceneCount) fail(`Shot count mismatch in ${base}/shot-contract.json`);
    assertFile(`${base}/composition-plan.json`);
    assertFile(`${base}/transition-plan.json`);
  }
}

function validateSources() {
  if (sources.length < 8) fail("Expected official source coverage for volatile concepts");
  for (const source of sources) {
    if (!/^https:\/\//.test(source.url)) fail(`Source URL must be HTTPS: ${source.url}`);
    if (!source.label || !source.note) fail(`Incomplete source entry: ${source.url}`);
  }
}

function main() {
  validateConcepts();
  validateSources();
  validatePlans();
  console.log(JSON.stringify({ status: "pass", concepts: concepts.length, runtimeSeconds: project.runtimeSeconds }, null, 2));
}

main();

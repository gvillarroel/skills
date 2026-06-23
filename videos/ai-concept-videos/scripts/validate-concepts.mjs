#!/usr/bin/env node
import { join, resolve, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = resolve(__dirname, "..", "..", "..");
const deckDir = resolve(repoRoot, ".agents", "skills", "html-d3-anime-video-workflow", "assets", "examples", "ai-concept-videos");
const { beats, concepts, palette, researchNotes } = await import(pathToFileURL(join(deckDir, "concepts.js")).href);

const errors = [];
const beatIds = beats.map((beat) => beat.id);
const paletteValues = new Set(Object.values(palette));

function assert(condition, message) {
  if (!condition) errors.push(message);
}

assert(concepts.length === 11, `Expected 11 concepts, found ${concepts.length}.`);
assert(researchNotes.length >= 10, "Expected at least 10 current research notes.");

for (const concept of concepts) {
  assert(concept.runtimeSeconds === 120, `${concept.id}: runtimeSeconds must be 120.`);
  assert(concept.scenes.length === beats.length, `${concept.id}: expected ${beats.length} scenes.`);
  assert(JSON.stringify(concept.scenes.map((scene) => scene.beat)) === JSON.stringify(beatIds), `${concept.id}: scenes must match the standard beat order.`);
  assert(concept.references.length >= 2, `${concept.id}: expected at least two references.`);
  assert(concept.metrics.length >= 3, `${concept.id}: expected at least three metrics.`);
  assert(concept.coreIdea.length <= 155, `${concept.id}: core idea is too long for the title band.`);

  for (const scene of concept.scenes) {
    assert(scene.headline.length <= 70, `${concept.id}/${scene.beat}: headline is too long.`);
    assert(scene.bullets.length >= 3, `${concept.id}/${scene.beat}: expected at least three bullets.`);
    assert(scene.bullets.every((bullet) => bullet.length <= 86), `${concept.id}/${scene.beat}: a bullet is too long.`);
    assert(scene.callout.length <= 92, `${concept.id}/${scene.beat}: callout is too long.`);
  }

  for (const metric of concept.metrics) {
    assert(metric.value > 0 && metric.value <= 1, `${concept.id}/${metric.label}: metric value must be 0-1.`);
    assert(paletteValues.has(metric.color), `${concept.id}/${metric.label}: metric color must use a token palette value.`);
  }
}

if (errors.length) {
  console.error("AI concept video validation failed:");
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Validated ${concepts.length} AI concept videos, ${beats.length} beats, and ${researchNotes.length} research notes.`);

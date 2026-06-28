#!/usr/bin/env node
// Run: node projects/d3-generalization/scripts/validate-generalization.ts <html-file>
// Dependencies: none

import fs from "node:fs";
import path from "node:path";

const targetPath = process.argv[2];
if (!targetPath) {
  console.error("Usage: node projects/d3-generalization/scripts/validate-generalization.ts <html-file>");
  process.exit(2);
}

const htmlPath = path.resolve(targetPath);
const html = fs.readFileSync(htmlPath, "utf8");
const findings = [];
const summaries = [];

if (/(?:src|href)\s*=\s*["']https?:\/\//i.test(html) || /@import\s+url\(\s*["']?https?:\/\//i.test(html)) {
  findings.push("HTML references a remote script, stylesheet, image, or import.");
}
if (/<script\b[^>]*\bsrc\s*=/i.test(html)) {
  findings.push("HTML uses an external script instead of inline final SVG geometry.");
}
if (!/prefers-reduced-motion/i.test(html)) {
  findings.push("Missing reduced-motion fallback.");
}
if (!/(?:@keyframes|<animate\b|<animateTransform\b|animation\s*:)/i.test(html)) {
  findings.push("Missing portable CSS or SVG-native animation.");
}

const expected = [
  {
    id: "force-small",
    pattern: "d3-pattern-force-network",
    size: "small",
    target: 5,
    markClass: "node",
    secondaryClass: "link",
    minMarks: 4,
    maxMarks: 8,
    minSecondary: 5,
  },
  {
    id: "force-medium",
    pattern: "d3-pattern-force-network",
    size: "medium",
    target: 12,
    markClass: "node",
    secondaryClass: "link",
    minMarks: 10,
    maxMarks: 16,
    minSecondary: 16,
  },
  {
    id: "force-large",
    pattern: "d3-pattern-force-network",
    size: "large",
    target: 36,
    markClass: "node",
    secondaryClass: "link",
    minMarks: 30,
    maxMarks: 44,
    minSecondary: 45,
  },
  {
    id: "beeswarm-small",
    pattern: "d3-pattern-beeswarm",
    size: "small",
    target: 9,
    markClass: "dot",
    minMarks: 7,
    maxMarks: 12,
  },
  {
    id: "beeswarm-medium",
    pattern: "d3-pattern-beeswarm",
    size: "medium",
    target: 30,
    markClass: "dot",
    minMarks: 25,
    maxMarks: 36,
  },
  {
    id: "beeswarm-large",
    pattern: "d3-pattern-beeswarm",
    size: "large",
    target: 90,
    markClass: "dot",
    minMarks: 75,
    maxMarks: 110,
  },
];

const byPattern = new Map();
for (const spec of expected) {
  const svg = extractSvgById(html, spec.id);
  if (!svg) {
    findings.push(`Missing svg#${spec.id}.`);
    continue;
  }

  const markCount = countClass(svg, spec.markClass);
  const secondaryCount = spec.secondaryClass ? countClass(svg, spec.secondaryClass) : 0;
  const textCount = countTag(svg, "text");
  const elementCount = countSvgElements(svg);
  const summary = {
    id: spec.id,
    pattern: spec.pattern,
    size: spec.size,
    target: spec.target,
    marks: markCount,
    secondaryMarks: secondaryCount,
    text: textCount,
    elements: elementCount,
  };
  summaries.push(summary);

  if (!/\bviewBox\s*=/i.test(svg)) {
    findings.push(`${spec.id}: missing viewBox.`);
  }
  if (!/<title\b[\s\S]*?<\/title>/i.test(svg)) {
    findings.push(`${spec.id}: missing title.`);
  }
  if (!/<desc\b[\s\S]*?<\/desc>/i.test(svg)) {
    findings.push(`${spec.id}: missing desc.`);
  }
  if (!new RegExp(`data-pattern-id\\s*=\\s*["']${escapeRegExp(spec.pattern)}["']`, "i").test(svg)) {
    findings.push(`${spec.id}: missing or wrong data-pattern-id.`);
  }
  if (!new RegExp(`data-size\\s*=\\s*["']${spec.size}["']`, "i").test(svg)) {
    findings.push(`${spec.id}: missing or wrong data-size.`);
  }
  if (!new RegExp(`data-target-count\\s*=\\s*["']${spec.target}["']`, "i").test(svg)) {
    findings.push(`${spec.id}: missing or wrong data-target-count.`);
  }
  if (!/font-family\s*[:=]/i.test(svg) && !/font-family\s*:/i.test(html)) {
    findings.push(`${spec.id}: missing explicit font-family.`);
  }
  if (markCount < spec.minMarks || markCount > spec.maxMarks) {
    findings.push(`${spec.id}: expected ${spec.minMarks}-${spec.maxMarks} .${spec.markClass} marks, got ${markCount}.`);
  }
  if (spec.secondaryClass && secondaryCount < spec.minSecondary) {
    findings.push(`${spec.id}: expected at least ${spec.minSecondary} .${spec.secondaryClass} marks, got ${secondaryCount}.`);
  }
  if (elementCount < Math.max(20, markCount + secondaryCount + textCount)) {
    findings.push(`${spec.id}: SVG element count looks too sparse for rendered final-state geometry.`);
  }
  if (textCount < 2) {
    findings.push(`${spec.id}: not enough visible text/labels.`);
  }

  const group = byPattern.get(spec.pattern) ?? [];
  group.push(summary);
  byPattern.set(spec.pattern, group);
}

for (const [pattern, rows] of byPattern.entries()) {
  const ordered = ["small", "medium", "large"].map((size) => rows.find((row) => row.size === size));
  if (ordered.some((row) => !row)) {
    continue;
  }
  const [small, medium, large] = ordered;
  if (!(small.marks < medium.marks && medium.marks < large.marks)) {
    findings.push(`${pattern}: mark counts are not monotonic small < medium < large.`);
  }
  if (!(small.elements < medium.elements && medium.elements < large.elements)) {
    findings.push(`${pattern}: element counts are not monotonic small < medium < large.`);
  }
  if (pattern === "d3-pattern-force-network" && !(small.secondaryMarks < medium.secondaryMarks && medium.secondaryMarks < large.secondaryMarks)) {
    findings.push(`${pattern}: link counts are not monotonic small < medium < large.`);
  }
}

const report = {
  file: htmlPath,
  passed: findings.length === 0,
  summaries,
  findings,
};

console.log(JSON.stringify(report, null, 2));
process.exit(findings.length === 0 ? 0 : 1);

function extractSvgById(source, id) {
  const openTagPattern = new RegExp(`<svg\\b(?=[^>]*\\bid\\s*=\\s*["']${escapeRegExp(id)}["'])[^>]*>`, "i");
  const openMatch = source.match(openTagPattern);
  if (!openMatch || openMatch.index === undefined) {
    return null;
  }
  const start = openMatch.index;
  const closeIndex = source.indexOf("</svg>", start);
  if (closeIndex === -1) {
    return null;
  }
  return source.slice(start, closeIndex + "</svg>".length);
}

function countClass(source, className) {
  const classPattern = /\bclass\s*=\s*["']([^"']+)["']/gi;
  let count = 0;
  for (const match of source.matchAll(classPattern)) {
    const classes = match[1].split(/\s+/);
    if (classes.includes(className)) {
      count += 1;
    }
  }
  return count;
}

function countTag(source, tagName) {
  return (source.match(new RegExp(`<\\s*${tagName}(?=[\\s>/])`, "gi")) ?? []).length;
}

function countSvgElements(source) {
  return (source.match(/<\s*[A-Za-z][\w:-]*(?=[\s>/])/g) ?? []).length;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

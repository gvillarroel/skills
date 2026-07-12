#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Verify the published D3 logo-design gallery in Chromium."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright


EXPECTED_PATTERNS = 90
EXPECTED_COMPOSITIONS = 90
EXPECTED_TEXTURES = 10
CONTROL_IDS = (
    "brand",
    "tagline",
    "colorset",
    "font",
    "pattern",
    "texture",
    "density",
    "curvature",
    "scale",
    "rotation",
    "textureStrength",
)
RANGE_CONTROL_IDS = ("density", "curvature", "scale", "rotation", "textureStrength")
TEXT_SAMPLE_STEP_PX = 2.75
TEXT_OCCLUSION_TOLERANCE = 0.01
TEXT_CLIP_TOLERANCE_PX = 0.75
TEXT_MIN_OCCLUDED_SAMPLES = 3

COLORSETS = {
    "colorset1": [
        "#000000",
        "#1c1c1c",
        "#333e48",
        "#363636",
        "#4f4f4f",
        "#696969",
        "#6d1222",
        "#828282",
        "#9c9c9c",
        "#9e1b32",
        "#b5b5b5",
        "#cfcfcf",
        "#e7e7e7",
        "#e8002a",
        "#f7f7f7",
        "#ffccd5",
        "#ffffff",
    ],
    "colorset2": [
        "#000000",
        "#004d66",
        "#007298",
        "#00ace6",
        "#1c1c1c",
        "#294d19",
        "#333e48",
        "#363636",
        "#36b300",
        "#431f47",
        "#45842a",
        "#4f4f4f",
        "#652f6c",
        "#696969",
        "#6d1222",
        "#828282",
        "#98700c",
        "#994a00",
        "#9c9c9c",
        "#9e00b3",
        "#9e1b32",
        "#b5b5b5",
        "#cdf3ff",
        "#cfcfcf",
        "#dbffcc",
        "#e77204",
        "#e7e7e7",
        "#e8002a",
        "#f1c319",
        "#f7f7f7",
        "#f9ccff",
        "#ff9633",
        "#ffccd5",
        "#ffd332",
        "#ffe5cc",
        "#fff4cc",
        "#ffffff",
    ],
}


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("viewport must use WIDTHxHEIGHT, for example 1440x1100")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 320 or height < 320:
        raise argparse.ArgumentTypeError("viewport dimensions must be at least 320 pixels")
    return width, height


def source_to_url(source: str) -> str:
    if re.match(r"^https?://", source) or source.startswith("file://"):
        return source
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input HTML not found: {path}")
    return path.as_uri()


STATIC_AUDIT_JS = r"""
({ expectedPatterns, expectedCompositions, expectedTextures, controlIds }) => {
  const findings = [];
  const cards = Array.from(document.querySelectorAll("[data-example]"));
  const gallerySvgs = cards.flatMap(card => Array.from(card.querySelectorAll("svg")));
  const body = document.body;
  const idPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

  function textureIds(registry) {
    if (registry instanceof Map) {
      return Array.from(registry.entries(), ([key, value]) =>
        typeof value === "string" ? value : value?.id || value?.textureId || key
      );
    }
    if (Array.isArray(registry)) {
      return registry.map((value, index) =>
        typeof value === "string" ? value : value?.id || value?.textureId || value?.patternId || String(index)
      );
    }
    if (registry && typeof registry === "object") {
      return Object.entries(registry).map(([key, value]) =>
        typeof value === "string" && value.startsWith("d3-")
          ? value
          : value?.id || value?.textureId || value?.patternId || key
      );
    }
    return [];
  }

  function duplicateValues(values) {
    const counts = new Map();
    values.forEach(value => counts.set(value, (counts.get(value) || 0) + 1));
    return Array.from(counts, ([value, count]) => ({ value, count })).filter(item => item.count > 1);
  }

  const bodyCounts = {
    exampleCount: body?.dataset.exampleCount || "",
    patternCount: body?.dataset.patternCount || "",
    compositionCount: body?.dataset.compositionCount || "",
    textureCount: body?.dataset.textureCount || ""
  };
  const expectedBodyCounts = {
    exampleCount: String(expectedPatterns),
    patternCount: String(expectedPatterns),
    compositionCount: String(expectedCompositions),
    textureCount: String(expectedTextures)
  };
  for (const [name, expected] of Object.entries(expectedBodyCounts)) {
    if (bodyCounts[name] !== expected) {
      findings.push(`Body data-${name.replace(/[A-Z]/g, match => `-${match.toLowerCase()}`)} is ${bodyCounts[name] || "missing"}; expected ${expected}.`);
    }
  }

  if (cards.length !== expectedPatterns) {
    findings.push(`Expected ${expectedPatterns} [data-example] cards, found ${cards.length}.`);
  }
  if (gallerySvgs.length !== expectedPatterns) {
    findings.push(`Expected ${expectedPatterns} gallery SVGs, found ${gallerySvgs.length}.`);
  }

  const exampleIds = cards.map(card => card.dataset.exampleId || "");
  const patternIds = cards.map(card => card.dataset.patternId || "");
  const compositionIds = cards.map(card => card.dataset.compositionId || "");
  const legacyExampleIds = cards.map(card => card.dataset.legacyExampleId || "");
  const geometrySignatures = cards.map(card => card.dataset.geometrySignature || "");
  const usedTextureIds = cards.map(card => card.dataset.textureId || "");

  for (const [label, values, expected] of [
    ["example", exampleIds, expectedPatterns],
    ["pattern", patternIds, expectedPatterns],
    ["composition", compositionIds, expectedCompositions],
    ["geometry signature", geometrySignatures, expectedPatterns]
  ]) {
    const missing = values.map((value, index) => ({ value, index })).filter(item => !item.value);
    const duplicates = duplicateValues(values.filter(Boolean));
    const uniqueCount = new Set(values.filter(Boolean)).size;
    if (missing.length) findings.push(`${label} IDs/signatures missing on card indexes: ${missing.map(item => item.index).join(", ")}.`);
    if (duplicates.length) findings.push(`Duplicate ${label} IDs/signatures: ${JSON.stringify(duplicates.slice(0, 10))}`);
    if (uniqueCount !== expected) findings.push(`Expected ${expected} unique ${label} IDs/signatures, found ${uniqueCount}.`);
  }

  const invalidExampleIds = exampleIds.filter(value => value && !idPattern.test(value));
  const invalidPatternIds = patternIds.filter(value => value && !idPattern.test(value));
  const invalidCompositionIds = compositionIds.filter(value => value && !idPattern.test(value));
  if (invalidExampleIds.length) findings.push(`Invalid example IDs: ${invalidExampleIds.join(", ")}.`);
  if (invalidPatternIds.length) findings.push(`Invalid pattern IDs: ${invalidPatternIds.join(", ")}.`);
  if (invalidCompositionIds.length) findings.push(`Invalid composition IDs: ${invalidCompositionIds.join(", ")}.`);
  cards.forEach((card, index) => {
    const expectedPatternId = `d3-logo-${exampleIds[index]}`;
    const expectedLegacyExampleId = compositionIds[index].replace(/^d3-logo-/, "");
    const visibleId = card.querySelector(".card-head p")?.textContent?.trim() || "";
    if (card.dataset.example !== exampleIds[index]) findings.push(`Card ${patternIds[index] || index} data-example does not match data-example-id.`);
    if (patternIds[index] !== expectedPatternId) findings.push(`Card ${patternIds[index] || index} example/pattern parity mismatch: ${exampleIds[index]} -> ${expectedPatternId}.`);
    if (card.id !== patternIds[index]) findings.push(`Card ${patternIds[index] || index} DOM id must equal data-pattern-id.`);
    if (visibleId !== patternIds[index]) findings.push(`Card ${patternIds[index] || index} visible ID label is ${visibleId || "missing"}.`);
    if (legacyExampleIds[index] !== expectedLegacyExampleId) findings.push(`Card ${patternIds[index] || index} legacy example alias is ${legacyExampleIds[index] || "missing"}; expected ${expectedLegacyExampleId}.`);
  });

  const registry = window.D3LogoDesign?.TEXTURES;
  const registeredTextureIds = textureIds(registry);
  const uniqueTextureIds = Array.from(new Set(registeredTextureIds));
  const duplicateTextureIds = duplicateValues(registeredTextureIds);
  if (registeredTextureIds.length !== expectedTextures || uniqueTextureIds.length !== expectedTextures) {
    findings.push(`Expected ${expectedTextures} unique window.D3LogoDesign.TEXTURES records, found ${registeredTextureIds.length} records and ${uniqueTextureIds.length} unique IDs.`);
  }
  if (duplicateTextureIds.length) findings.push(`Duplicate texture IDs: ${JSON.stringify(duplicateTextureIds)}`);
  const missingTextureUse = uniqueTextureIds.filter(id => !usedTextureIds.includes(id));
  const unknownTextureUse = Array.from(new Set(usedTextureIds.filter(Boolean))).filter(id => !uniqueTextureIds.includes(id));
  const missingCardTextures = usedTextureIds.map((value, index) => ({ value, index })).filter(item => !item.value);
  if (missingTextureUse.length) findings.push(`Registered textures unused by compositions: ${missingTextureUse.join(", ")}.`);
  if (unknownTextureUse.length) findings.push(`Compositions use unregistered textures: ${unknownTextureUse.join(", ")}.`);
  if (missingCardTextures.length) findings.push(`Cards missing data-texture-id: ${missingCardTextures.map(item => item.index).join(", ")}.`);

  const allIds = Array.from(document.querySelectorAll("[id]"), node => node.id).filter(Boolean);
  const duplicateDomIds = duplicateValues(allIds);
  if (duplicateDomIds.length) findings.push(`Duplicate DOM IDs: ${JSON.stringify(duplicateDomIds.slice(0, 20))}`);

  function geometryFingerprint(svg) {
    const attributes = ["d", "points", "x", "y", "x1", "x2", "y1", "y2", "cx", "cy", "r", "rx", "ry", "width", "height", "transform", "font-size", "stroke-width"];
    const source = Array.from(svg.querySelectorAll("path, rect, circle, ellipse, line, polyline, polygon, text, g"))
      .filter(node => !node.closest("defs"))
      .map(node => `${node.tagName}|${attributes.flatMap(name => node.hasAttribute(name) ? [`${name}=${node.getAttribute(name)}`] : []).join("|")}`)
      .join("\n");
    let hash = 2166136261;
    for (let index = 0; index < source.length; index += 1) {
      hash ^= source.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16);
  }

  const geometryHashes = gallerySvgs.map(geometryFingerprint);
  const uniqueGeometryHashes = new Set(geometryHashes).size;
  if (uniqueGeometryHashes !== expectedPatterns) {
    findings.push(`Expected ${expectedPatterns} unique rendered geometry hashes, found ${uniqueGeometryHashes}.`);
  }

  const svgReports = cards.map((card, index) => {
    const svgs = Array.from(card.querySelectorAll("svg"));
    const svg = svgs[0] || null;
    const title = svg?.querySelector(":scope > title") || null;
    const desc = svg?.querySelector(":scope > desc") || null;
    const labelledBy = (svg?.getAttribute("aria-labelledby") || "").split(/\s+/).filter(Boolean);
    const composition = svg?.querySelector(".logo-composition") || null;
    let contentBox = null;
    try {
      const box = composition?.getBBox();
      if (box) contentBox = {x: box.x, y: box.y, width: box.width, height: box.height};
    } catch (_) {
      contentBox = null;
    }
    const withinViewBox = Boolean(contentBox) && contentBox.x >= -3 && contentBox.y >= -3 &&
      contentBox.x + contentBox.width <= 483 && contentBox.y + contentBox.height <= 323;
    const report = {
      index,
      exampleId: card.dataset.exampleId || "",
      svgCount: svgs.length,
      elementCount: svg?.querySelectorAll("*").length || 0,
      titleId: title?.id || "",
      descId: desc?.id || "",
      hasTitle: Boolean(title?.textContent?.trim()),
      hasDesc: Boolean(desc?.textContent?.trim()),
      ariaLabelledby: labelledBy,
      cardPatternId: card.dataset.patternId || "",
      svgExampleId: svg?.dataset.exampleId || "",
      svgPatternId: svg?.dataset.patternId || "",
      cardCompositionId: card.dataset.compositionId || "",
      svgCompositionId: svg?.dataset.compositionId || "",
      cardGeometrySignature: card.dataset.geometrySignature || "",
      svgGeometrySignature: svg?.dataset.geometrySignature || "",
      cardTextureId: card.dataset.textureId || "",
      svgTextureId: svg?.dataset.textureId || "",
      viewBox: svg?.getAttribute("viewBox") || "",
      geometryHash: svg ? geometryFingerprint(svg) : "",
      contentBox,
      withinViewBox
    };
    if (report.svgCount !== 1) findings.push(`Card ${report.exampleId || index} contains ${report.svgCount} SVGs; expected one.`);
    if (report.elementCount <= 8) findings.push(`SVG ${report.exampleId || index} has ${report.elementCount} descendant elements; expected more than 8.`);
    if (!report.hasTitle || !report.hasDesc || !report.titleId || !report.descId ||
        !labelledBy.includes(report.titleId) || !labelledBy.includes(report.descId)) {
      findings.push(`SVG ${report.exampleId || index} is missing a direct title/desc or matching aria-labelledby references.`);
    }
    if (svg && report.svgPatternId !== report.cardPatternId) findings.push(`SVG/card pattern ID mismatch for ${report.exampleId || index}.`);
    if (svg && report.svgExampleId !== report.exampleId) findings.push(`SVG/card example ID mismatch for ${report.exampleId || index}.`);
    if (svg && report.svgCompositionId !== report.cardCompositionId) findings.push(`SVG/card composition ID mismatch for ${report.exampleId || index}.`);
    if (svg && report.svgGeometrySignature && report.svgGeometrySignature !== report.cardGeometrySignature) findings.push(`SVG/card geometry signature mismatch for ${report.exampleId || index}.`);
    if (svg && report.svgTextureId !== report.cardTextureId) findings.push(`SVG/card texture ID mismatch for ${report.exampleId || index}.`);
    if (svg && report.viewBox !== "0 0 480 320") findings.push(`SVG ${report.exampleId || index} has unexpected viewBox ${report.viewBox || "missing"}.`);
    if (svg && !report.withinViewBox) findings.push(`SVG ${report.exampleId || index} has clipped or out-of-bounds content: ${JSON.stringify(report.contentBox)}.`);
    return report;
  });

  const missingControls = controlIds.filter(id => !document.getElementById(id));
  if (missingControls.length) findings.push(`Missing studio controls: ${missingControls.join(", ")}.`);
  const studio = document.querySelector("svg#studio-logo");
  if (!studio) findings.push("Missing studio SVG #studio-logo.");
  const api = window.D3LogoGallery;
  if (!api || typeof api !== "object") {
    findings.push("Missing window.D3LogoGallery API.");
  } else {
    if (typeof api.renderStudio !== "function") findings.push("window.D3LogoGallery.renderStudio is not a function.");
    if (typeof api.renderAll !== "function") findings.push("window.D3LogoGallery.renderAll is not a function.");
    if (!api.currentConfig || typeof api.currentConfig !== "object") findings.push("window.D3LogoGallery.currentConfig is not an object.");
  }

  const gradientElements = Array.from(document.querySelectorAll("linearGradient, radialGradient, meshgradient"));
  const stylesheetParts = Array.from(document.querySelectorAll("style"), node => node.textContent || "");
  for (const sheet of Array.from(document.styleSheets)) {
    try {
      stylesheetParts.push(Array.from(sheet.cssRules || [], rule => rule.cssText || "").join("\n"));
    } catch (_) {
      // Cross-origin font stylesheets are not part of the gallery paint contract.
    }
  }
  const stylesheetText = stylesheetParts.join("\n");
  const inlineGradientNodes = Array.from(document.querySelectorAll("[style]")).filter(node => /(?:linear|radial|conic)-gradient\s*\(/i.test(node.getAttribute("style") || ""));
  const computedGradientNodes = Array.from(document.querySelectorAll("body, body *")).filter(node => {
    const style = getComputedStyle(node);
    return [style.backgroundImage, style.maskImage, style.borderImageSource]
      .some(value => /(?:linear|radial|conic)-gradient\s*\(/i.test(value || ""));
  });
  const stylesheetHasGradient = /(?:linear|radial|conic)-gradient\s*\(/i.test(stylesheetText);
  if (gradientElements.length || stylesheetHasGradient || inlineGradientNodes.length || computedGradientNodes.length) {
    findings.push(`Gradients are forbidden: ${gradientElements.length} SVG gradient elements, ${inlineGradientNodes.length} inline gradient styles, ${computedGradientNodes.length} computed gradient styles, stylesheet=${stylesheetHasGradient}.`);
  }

  function isExternalImageHref(value) {
    const raw = String(value || "").trim();
    if (!raw || raw.startsWith("#") || /^(?:data|blob):/i.test(raw)) return false;
    try {
      const resolved = new URL(raw, document.baseURI);
      const pageUrl = new URL(document.baseURI);
      if (!/^https?:$/.test(resolved.protocol)) return false;
      return !/^https?:$/.test(pageUrl.protocol) || resolved.origin !== pageUrl.origin;
    } catch (_) {
      return /^https?:\/\//i.test(raw) || /^\/\//.test(raw);
    }
  }
  const externalImages = Array.from(document.querySelectorAll("img[src], input[type='image'][src], image[href], image[xlink\\:href]")).flatMap(node => {
    const href = node.getAttribute("src") || node.getAttribute("href") || node.getAttribute("xlink:href") || "";
    return isExternalImageHref(href) ? [{ tag: node.tagName.toLowerCase(), href }] : [];
  });
  const externalBackgrounds = Array.from(document.querySelectorAll("body, body *")).flatMap(node => {
    const style = getComputedStyle(node);
    const imageValues = [style.backgroundImage, style.maskImage, style.borderImageSource].join(" ");
    const matches = Array.from(imageValues.matchAll(/url\(["']?([^"')]+)["']?\)/gi), match => match[1]);
    return matches.filter(isExternalImageHref).map(href => ({ tag: node.tagName.toLowerCase(), href }));
  });
  if (externalImages.length || externalBackgrounds.length) {
    findings.push(`External images are forbidden: ${JSON.stringify([...externalImages, ...externalBackgrounds].slice(0, 12))}`);
  }

  return {
    clean: findings.length === 0,
    findings,
    bodyCounts,
    cardCount: cards.length,
    gallerySvgCount: gallerySvgs.length,
    uniqueExampleIds: new Set(exampleIds).size,
    legacyExampleIds,
    uniquePatternIds: new Set(patternIds.filter(Boolean)).size,
    uniqueCompositionIds: new Set(compositionIds.filter(Boolean)).size,
    uniqueGeometrySignatures: new Set(geometrySignatures.filter(Boolean)).size,
    uniqueGeometryHashes,
    geometryHashes,
    registeredTextureIds,
    usedTextureIds: Array.from(new Set(usedTextureIds.filter(Boolean))),
    duplicateDomIds,
    svgReports,
    missingControls,
    hasStudio: Boolean(studio),
    hasGalleryApi: Boolean(api),
    gradientElementCount: gradientElements.length,
    computedGradientCount: computedGradientNodes.length,
    stylesheetHasGradient,
    externalImageCount: externalImages.length + externalBackgrounds.length
  };
}
"""


TEXT_CLEARANCE_AUDIT_JS = r"""
(card, { sampleStepPx, occlusionTolerance, clipTolerancePx, minOccludedSamples }) => {
  const svg = card.querySelector(".viz-frame svg, svg");
  const exampleId = card.dataset.exampleId || svg?.dataset.exampleId || "";
  const patternId = card.dataset.patternId || svg?.dataset.patternId || "";
  const compositionId = card.dataset.compositionId || svg?.dataset.compositionId || "";
  const findingRecords = [];
  const findingMessages = [];
  const knownPolicies = new Set(["clear"]);
  const drawableTags = new Set(["path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "textPath", "use"]);

  function addFinding(kind, message, details = {}) {
    const record = { kind, severity: "error", exampleId, patternId, compositionId, message, ...details };
    findingRecords.push(record);
    findingMessages.push(`[text-clearance][exampleId=${exampleId || "missing"}][patternId=${patternId || "missing"}] ${message}`);
  }

  function parseJsonContract(owner, datasetKey, label) {
    const raw = owner?.dataset?.[datasetKey];
    if (typeof raw !== "string") {
      addFinding("contract", `${label} JSON metadata is missing.`, { datasetKey });
      return [];
    }
    try {
      const value = JSON.parse(raw);
      if (!Array.isArray(value)) {
        addFinding("contract", `${label} JSON must be an array.`, { datasetKey, raw });
        return [];
      }
      return value;
    } catch (error) {
      addFinding("contract", `${label} JSON is invalid: ${error.message}.`, { datasetKey, raw });
      return [];
    }
  }

  function normalizedJson(value) {
    return JSON.stringify(value);
  }

  function roleToken(value) {
    return /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(String(value || ""));
  }

  function ruleAppliesNow(rule) {
    const when = String(rule?.when || "always");
    if (when === "always") return true;
    if (when === "small-size") return svg?.dataset.smallSize === "true";
    if (when === "not-small-size") return svg?.dataset.smallSize !== "true";
    const mode = svg?.querySelector("[data-lockup-mode]")?.dataset.lockupMode || "";
    if (["wide", "stacked", "compact"].includes(when)) return mode === when;
    return false;
  }

  function validateOcclusionRule(rule, index) {
    if (!rule || typeof rule !== "object" || Array.isArray(rule)) {
      addFinding("contract", `Intentional occlusion rule ${index} must be an object.`, { exceptionIndex: index });
      return false;
    }
    const hasTextMatcher = Boolean(rule.textLayerId || rule.textRole);
    const hasOccluderMatcher = Boolean(rule.occluderLayerId || rule.occluderRole);
    const ratio = Number(rule.maxOcclusionRatio);
    let valid = true;
    if (!hasTextMatcher || !hasOccluderMatcher) {
      addFinding("contract", `Intentional occlusion rule ${index} must identify both the text and occluder by role or layer ID.`, { exceptionIndex: index, rule });
      valid = false;
    }
    if (rule.textRole && !roleToken(rule.textRole)) {
      addFinding("contract", `Intentional occlusion rule ${index} has invalid textRole ${JSON.stringify(rule.textRole)}.`, { exceptionIndex: index, rule });
      valid = false;
    }
    if (rule.occluderRole && !roleToken(rule.occluderRole)) {
      addFinding("contract", `Intentional occlusion rule ${index} has invalid occluderRole ${JSON.stringify(rule.occluderRole)}.`, { exceptionIndex: index, rule });
      valid = false;
    }
    if (!String(rule.reason || "").trim()) {
      addFinding("contract", `Intentional occlusion rule ${index} needs a nonblank reason.`, { exceptionIndex: index, rule });
      valid = false;
    }
    if (!Number.isFinite(ratio) || ratio <= 0 || ratio > 0.30) {
      addFinding("contract", `Intentional occlusion rule ${index} has invalid maxOcclusionRatio ${JSON.stringify(rule.maxOcclusionRatio)}; expected > 0 and <= 0.30.`, { exceptionIndex: index, rule });
      valid = false;
    }
    if (rule.when && !["always", "small-size", "not-small-size", "wide", "stacked", "compact"].includes(String(rule.when))) {
      addFinding("contract", `Intentional occlusion rule ${index} has unsupported when=${JSON.stringify(rule.when)}.`, { exceptionIndex: index, rule });
      valid = false;
    }
    return valid;
  }

  function validateOmissionRule(rule, index) {
    if (!rule || typeof rule !== "object" || Array.isArray(rule)) {
      addFinding("contract", `Intentional omission rule ${index} must be an object.`, { omissionIndex: index });
      return false;
    }
    let valid = true;
    if (!rule.textRole && !rule.textLayerId) {
      addFinding("contract", `Intentional omission rule ${index} must identify a text role or layer ID.`, { omissionIndex: index, rule });
      valid = false;
    }
    if (rule.textRole && !roleToken(rule.textRole)) {
      addFinding("contract", `Intentional omission rule ${index} has invalid textRole ${JSON.stringify(rule.textRole)}.`, { omissionIndex: index, rule });
      valid = false;
    }
    if (!String(rule.reason || "").trim()) {
      addFinding("contract", `Intentional omission rule ${index} needs a nonblank reason.`, { omissionIndex: index, rule });
      valid = false;
    }
    if (!rule.when || !["small-size", "wide", "stacked", "compact"].includes(String(rule.when))) {
      addFinding("contract", `Intentional omission rule ${index} needs a supported conditional when value.`, { omissionIndex: index, rule });
      valid = false;
    }
    return valid;
  }

  function semanticNodeFor(entry, composition) {
    if (!(entry instanceof Element) || entry.namespaceURI !== "http://www.w3.org/2000/svg") return null;
    if (!drawableTags.has(entry.localName)) return null;
    const semantic = entry.closest("[data-text-layer-id], [data-layer-id]");
    if (!semantic || !composition.contains(semantic)) return entry;
    return semantic;
  }

  function requiresIndependentGlyph(node) {
    if (node?.localName === "text" && !String(node.textContent || "").trim()) return false;
    const classList = node?.classList;
    return Boolean(classList?.contains("axis-glyph") || classList?.contains("rosette-glyph"));
  }

  function isWhitespaceSpacer(node) {
    if (node?.localName !== "text") return false;
    const value = String(node.textContent || "");
    return value.length > 0 && !value.trim();
  }

  function semanticIdentity(node, composition) {
    const baseTextLayerId = node?.dataset?.textLayerId || "";
    const independentGlyph = Boolean(baseTextLayerId && requiresIndependentGlyph(node));
    let glyphIndex = null;
    let effectiveLayerId = baseTextLayerId;
    if (independentGlyph) {
      const peers = Array.from(composition.querySelectorAll("[data-text-layer-id]"))
        .filter(candidate => candidate.dataset.textLayerId === baseTextLayerId && requiresIndependentGlyph(candidate));
      glyphIndex = peers.indexOf(node);
      if (peers.length > 1 && glyphIndex >= 0) {
        effectiveLayerId = `${baseTextLayerId}--glyph-${String(glyphIndex + 1).padStart(2, "0")}`;
      }
    }
    return {
      layerId: effectiveLayerId || node?.dataset?.layerId || "",
      baseLayerId: baseTextLayerId || node?.dataset?.layerId || "",
      role: baseTextLayerId ? node?.dataset?.textRole || "" : node?.dataset?.layerRole || "",
      isText: Boolean(baseTextLayerId),
      independentGlyph,
      glyphIndex: glyphIndex == null || glyphIndex < 0 ? null : glyphIndex + 1,
      tag: node?.localName || "",
      className: node?.getAttribute?.("class") || ""
    };
  }

  function ruleMatches(rule, target, occluder) {
    if (!ruleAppliesNow(rule)) return false;
    if (rule.textLayerId && ![target.layerId, target.baseLayerId].includes(rule.textLayerId)) return false;
    if (rule.textRole && rule.textRole !== target.role) return false;
    if (rule.occluderLayerId && ![occluder.layerId, occluder.baseLayerId].includes(rule.occluderLayerId)) return false;
    if (rule.occluderRole && rule.occluderRole !== occluder.role) return false;
    return true;
  }

  function omissionMatches(rule, target) {
    if (!ruleAppliesNow(rule)) return false;
    if (rule.textLayerId && ![target.layerId, target.baseLayerId].includes(rule.textLayerId)) return false;
    if (rule.textRole && rule.textRole !== target.role) return false;
    return true;
  }

  function renderedText(node) {
    const direct = String(node.textContent || "").replace(/\s+/g, " ").trim();
    if (direct) return direct;
    if (node.localName !== "use") return "";
    const href = node.getAttribute("href") || node.getAttribute("xlink:href") || "";
    const source = href.startsWith("#") ? svg?.querySelector(href) : null;
    return String(source?.textContent || "").replace(/\s+/g, " ").trim();
  }

  if (!svg) {
    addFinding("contract", "Gallery card has no SVG to audit.");
    return { clean: false, exampleId, patternId, compositionId, findings: findingRecords, findingMessages, textLayers: [] };
  }
  const composition = svg.querySelector(".logo-composition");
  if (!composition) {
    addFinding("contract", "SVG has no .logo-composition group.");
    return { clean: false, exampleId, patternId, compositionId, findings: findingRecords, findingMessages, textLayers: [] };
  }

  const svgOcclusions = parseJsonContract(svg, "intentionalTextOcclusions", "SVG intentional text occlusions");
  const cardOcclusions = parseJsonContract(card, "intentionalTextOcclusions", "Card intentional text occlusions");
  const svgOmissions = parseJsonContract(svg, "intentionalTextOmissions", "SVG intentional text omissions");
  const cardOmissions = parseJsonContract(card, "intentionalTextOmissions", "Card intentional text omissions");
  if (normalizedJson(svgOcclusions) !== normalizedJson(cardOcclusions)) {
    addFinding("contract", "Card/SVG intentional text occlusion metadata differs.", { cardOcclusions, svgOcclusions });
  }
  if (normalizedJson(svgOmissions) !== normalizedJson(cardOmissions)) {
    addFinding("contract", "Card/SVG intentional text omission metadata differs.", { cardOmissions, svgOmissions });
  }
  const validOcclusionRules = svgOcclusions.filter((rule, index) => validateOcclusionRule(rule, index));
  const validOmissionRules = svgOmissions.filter((rule, index) => validateOmissionRule(rule, index));

  const rawTextCandidates = Array.from(composition.querySelectorAll("text, use, [data-text-proxy]"));
  const missingSemanticText = rawTextCandidates.filter(node => {
    if (node.closest("defs")) return false;
    if (isWhitespaceSpacer(node)) return false;
    if (node.closest("[data-text-layer-id]")) return false;
    if (node.localName === "use") {
      const href = node.getAttribute("href") || node.getAttribute("xlink:href") || "";
      const source = href.startsWith("#") ? svg.querySelector(href) : null;
      if (source?.localName !== "text" && !node.hasAttribute("data-text-proxy")) return false;
    }
    return node.localName === "text" || node.hasAttribute("data-text-proxy") || node.localName === "use";
  });
  if (missingSemanticText.length) {
    addFinding("contract", `${missingSemanticText.length} rendered text candidates lack data-text-layer-id metadata.`, {
      missingSemanticText: missingSemanticText.slice(0, 12).map(node => ({ tag: node.localName, className: node.getAttribute("class") || "" }))
    });
  }

  const unannotatedDrawables = Array.from(composition.querySelectorAll("path, rect, circle, ellipse, line, polyline, polygon, use, text"))
    .filter(node => !node.closest("defs") && !node.closest("[data-text-layer-id]") && !node.hasAttribute("data-layer-id"));
  if (unannotatedDrawables.length) {
    addFinding("contract", `${unannotatedDrawables.length} drawable layers lack data-layer-id metadata.`, {
      unannotatedDrawables: unannotatedDrawables.slice(0, 12).map(node => ({ tag: node.localName, className: node.getAttribute("class") || "" }))
    });
  }

  const svgRect = svg.getBoundingClientRect();
  const textNodes = Array.from(composition.querySelectorAll("[data-text-layer-id]")).filter(node => !isWhitespaceSpacer(node));
  if (!textNodes.length) addFinding("contract", "SVG exposes no semantic text layers.");
  const textLayers = [];
  const usedExceptionIndexes = new Set();

  textNodes.forEach((targetNode, targetIndex) => {
    const target = semanticIdentity(targetNode, composition);
    const policy = targetNode.dataset.textPolicy || "";
    const source = targetNode.dataset.textSource || "";
    const rect = targetNode.getBoundingClientRect();
    const computedStyle = getComputedStyle(targetNode);
    const visible = rect.width > 0 && rect.height > 0 && computedStyle.display !== "none" &&
      computedStyle.visibility !== "hidden" && Number(computedStyle.opacity || 1) > 0;
    const activeOmissionRules = validOmissionRules.filter(rule => omissionMatches(rule, target));
    if (!target.layerId || !target.role || !source || !policy) {
      addFinding("contract", `Text layer ${target.layerId || targetIndex} is missing layer ID, role, source, or policy metadata.`, {
        textLayerId: target.layerId, textRole: target.role, textSource: source, textPolicy: policy
      });
    }
    if (target.layerId && !target.layerId.startsWith(`${exampleId}--`)) {
      addFinding("contract", `Text layer ID ${target.layerId} must begin with ${exampleId}--.`, { textLayerId: target.layerId, textRole: target.role });
    }
    if (target.role && !roleToken(target.role)) {
      addFinding("contract", `Text layer ${target.layerId || targetIndex} has invalid role ${JSON.stringify(target.role)}.`, { textLayerId: target.layerId, textRole: target.role });
    }
    if (policy && !knownPolicies.has(policy)) {
      addFinding("contract", `Text layer ${target.layerId || targetIndex} has unknown policy ${JSON.stringify(policy)}.`, { textLayerId: target.layerId, textRole: target.role, textPolicy: policy });
    }

    const overflowPx = {
      left: Math.max(0, svgRect.left - rect.left),
      right: Math.max(0, rect.right - svgRect.right),
      top: Math.max(0, svgRect.top - rect.top),
      bottom: Math.max(0, rect.bottom - svgRect.bottom)
    };
    const maxOverflowPx = Math.max(...Object.values(overflowPx));
    const policyAllowsClipping = false;
    const clipped = visible && maxOverflowPx > clipTolerancePx;
    if (clipped && !policyAllowsClipping) {
      addFinding("clipping", `Text layer ${target.layerId || targetIndex} (${target.role || "missing-role"}) exceeds the SVG viewport by ${maxOverflowPx.toFixed(2)} px.`, {
        textLayerId: target.layerId, textRole: target.role, textPolicy: policy, overflowPx
      });
    }

    let paintedSamples = 0;
    const occluderCounts = new Map();
    if (visible) {
      const step = Math.max(1.5, Number(sampleStepPx) || 2.75);
      const originalStyleAttribute = targetNode.getAttribute("style");
      targetNode.style.pointerEvents = "visiblePainted";
      for (let y = Math.floor(rect.top); y <= Math.ceil(rect.bottom); y += step) {
        if (y < svgRect.top - 1 || y > svgRect.bottom + 1) continue;
        for (let x = Math.floor(rect.left); x <= Math.ceil(rect.right); x += step) {
          if (x < svgRect.left - 1 || x > svgRect.right + 1) continue;
          const stack = document.elementsFromPoint(x, y);
          const targetStackIndex = stack.findIndex(entry => entry === targetNode || targetNode.contains(entry));
          if (targetStackIndex < 0) continue;
          paintedSamples += 1;
          let occluderNode = null;
          for (const entry of stack.slice(0, targetStackIndex)) {
            const semantic = semanticNodeFor(entry, composition);
            if (!semantic || semantic === targetNode || targetNode.contains(semantic)) continue;
            occluderNode = semantic;
            break;
          }
          if (!occluderNode) continue;
          const occluder = semanticIdentity(occluderNode, composition);
          if (target.baseLayerId && target.baseLayerId === occluder.baseLayerId &&
              !target.independentGlyph && !occluder.independentGlyph) {
            continue;
          }
          const key = `${occluder.layerId}\u0000${occluder.role}\u0000${occluder.tag}\u0000${occluder.className}`;
          const current = occluderCounts.get(key) || { ...occluder, samples: 0 };
          current.samples += 1;
          occluderCounts.set(key, current);
        }
      }
      if (originalStyleAttribute == null) targetNode.removeAttribute("style");
      else targetNode.setAttribute("style", originalStyleAttribute);
    }

    const policyAllowsOcclusion = false;
    let allowedOccludedSamples = 0;
    let unexpectedOccludedSamples = 0;
    const occluders = Array.from(occluderCounts.values()).map(occluder => {
      const ratio = paintedSamples ? occluder.samples / paintedSamples : 0;
      const matchingRules = validOcclusionRules
        .map((rule, index) => ({ rule, index }))
        .filter(item => ruleMatches(item.rule, target, occluder));
      matchingRules.forEach(item => usedExceptionIndexes.add(item.index));
      const maxDeclaredRatio = matchingRules.length
        ? Math.max(...matchingRules.map(item => Number(item.rule.maxOcclusionRatio)))
        : null;
      const allowedByException = maxDeclaredRatio != null && ratio <= maxDeclaredRatio + occlusionTolerance;
      const allowed = policyAllowsOcclusion || allowedByException;
      if (allowed) allowedOccludedSamples += occluder.samples;
      else unexpectedOccludedSamples += occluder.samples;
      return {
        ...occluder,
        ratio,
        allowed,
        maxDeclaredRatio,
        matchingExceptionIndexes: matchingRules.map(item => item.index)
      };
    }).sort((left, right) => right.samples - left.samples);
    const totalOccludedSamples = allowedOccludedSamples + unexpectedOccludedSamples;
    const totalOcclusionRatio = paintedSamples ? totalOccludedSamples / paintedSamples : 0;
    const unexpectedOcclusionRatio = paintedSamples ? unexpectedOccludedSamples / paintedSamples : 0;
    const unexpectedOcclusion = unexpectedOccludedSamples >= minOccludedSamples && unexpectedOcclusionRatio > occlusionTolerance;
    if (unexpectedOcclusion) {
      const leading = occluders.filter(item => !item.allowed).slice(0, 4);
      addFinding("occlusion", `Text layer ${target.layerId || targetIndex} (${target.role || "missing-role"}) has ${(unexpectedOcclusionRatio * 100).toFixed(1)}% unexpected occlusion.`, {
        textLayerId: target.layerId,
        textRole: target.role,
        textPolicy: policy,
        unexpectedOcclusionRatio,
        unexpectedOccludedSamples,
        paintedSamples,
        occluders: leading
      });
    }
    for (const occluder of occluders) {
      if (!occluder.matchingExceptionIndexes.length || occluder.allowed) continue;
      addFinding("exception-exceeded", `Text layer ${target.layerId || targetIndex} exceeds its declared occlusion limit against ${occluder.layerId || occluder.role || occluder.tag}: ${(occluder.ratio * 100).toFixed(1)}% observed.`, {
        textLayerId: target.layerId,
        textRole: target.role,
        occluder,
        matchingExceptionIndexes: occluder.matchingExceptionIndexes
      });
    }

    textLayers.push({
      index: targetIndex,
      layerId: target.layerId,
      baseLayerId: target.baseLayerId,
      role: target.role,
      independentGlyph: target.independentGlyph,
      glyphIndex: target.glyphIndex,
      policy,
      source,
      tag: target.tag,
      className: target.className,
      text: renderedText(targetNode),
      visible,
      activeOmissionRuleCount: activeOmissionRules.length,
      renderState: {
        display: computedStyle.display,
        visibility: computedStyle.visibility,
        opacity: computedStyle.opacity
      },
      bbox: { x: rect.x - svgRect.x, y: rect.y - svgRect.y, width: rect.width, height: rect.height },
      overflowPx,
      clipped,
      paintedSamples,
      totalOccludedSamples,
      totalOcclusionRatio,
      allowedOccludedSamples,
      unexpectedOccludedSamples,
      unexpectedOcclusionRatio,
      occluders
    });
  });

  const baseLayerGroups = new Map();
  for (const layer of textLayers) {
    const key = layer.independentGlyph ? layer.layerId : layer.baseLayerId;
    const group = baseLayerGroups.get(key) || [];
    group.push(layer);
    baseLayerGroups.set(key, group);
  }
  for (const [baseLayerId, layers] of baseLayerGroups) {
    const independentlyAudited = layers.some(layer => layer.independentGlyph);
    if (independentlyAudited) {
      for (const layer of layers) {
        if (layer.activeOmissionRuleCount) continue;
        if (!layer.visible || layer.paintedSamples === 0) {
          addFinding("hidden", `Text sublayer ${layer.layerId} (${layer.role || "missing-role"}) is not visibly painted.`, {
            textLayerId: layer.layerId,
            baseTextLayerId: layer.baseLayerId,
            textRole: layer.role,
            textPolicy: layer.policy,
            glyphIndex: layer.glyphIndex,
            paintedSamples: layer.paintedSamples,
            renderState: layer.renderState,
            bbox: layer.bbox
          });
        }
      }
      continue;
    }
    const hasPaintedMember = layers.some(layer => layer.visible && layer.paintedSamples > 0);
    const hasActiveOmission = layers.some(layer => layer.activeOmissionRuleCount > 0);
    if (!hasPaintedMember && !hasActiveOmission) {
      addFinding("hidden", `Semantic text layer ${baseLayerId} (${layers[0]?.role || "missing-role"}) has no visibly painted member.`, {
        textLayerId: baseLayerId,
        textRole: layers[0]?.role || "",
        textPolicy: layers[0]?.policy || "",
        memberCount: layers.length,
        members: layers.map(layer => ({ index: layer.index, visible: layer.visible, paintedSamples: layer.paintedSamples, renderState: layer.renderState, bbox: layer.bbox }))
      });
    }
  }

  return {
    clean: findingRecords.length === 0,
    exampleId,
    patternId,
    compositionId,
    requestedScale: Number(svg?.dataset.scale || NaN),
    effectiveScale: Number(svg?.dataset.effectiveScale || NaN),
    requestedRotation: Number(svg?.dataset.rotation || NaN),
    effectiveRotation: Number(svg?.dataset.effectiveRotation || NaN),
    findings: findingRecords,
    findingMessages,
    textLayerCount: textLayers.length,
    textLayers,
    intentionalOcclusionRules: validOcclusionRules,
    intentionalOmissionRules: validOmissionRules,
    usedExceptionIndexes: Array.from(usedExceptionIndexes).sort((a, b) => a - b),
    unusedExceptionIndexes: validOcclusionRules.map((_, index) => index).filter(index => !usedExceptionIndexes.has(index))
  };
}
"""


PALETTE_AUDIT_JS = r"""
({ colorset, allowedColors }) => {
  const allowed = new Set(allowedColors.map(value => value.toLowerCase()));
  const findings = [];
  const badPaints = [];
  const unsupportedPaints = [];
  const ignoredValues = new Set(["", "none", "transparent", "currentcolor", "auto"]);
  const computedProperties = [
    "color", "backgroundColor", "borderTopColor", "borderRightColor", "borderBottomColor", "borderLeftColor",
    "outlineColor", "textDecorationColor", "caretColor", "accentColor", "fill", "stroke", "stopColor", "floodColor", "lightingColor"
  ];
  const paintAttributes = ["color", "fill", "stroke", "stop-color", "flood-color", "lighting-color"];

  function normalizeColor(rawValue) {
    if (rawValue == null) return { ignored: true, normalized: null };
    const raw = String(rawValue).trim().toLowerCase();
    if (ignoredValues.has(raw) || raw.startsWith("url(") || raw.startsWith("var(")) {
      return { ignored: true, normalized: null };
    }
    const hex = raw.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/);
    if (hex) {
      const value = hex[1];
      const normalized = value.length === 3
        ? `#${value[0]}${value[0]}${value[1]}${value[1]}${value[2]}${value[2]}`
        : `#${value}`;
      return { ignored: false, normalized };
    }
    const rgb = raw.match(/^rgba?\(([^)]+)\)$/);
    if (rgb) {
      const parts = rgb[1].replace("/", " ").split(/[\s,]+/).filter(Boolean);
      if (parts.length >= 3) {
        const alpha = parts.length >= 4 ? Number(parts[3]) : 1;
        if (Number.isFinite(alpha) && alpha <= 0) return { ignored: true, normalized: null };
        const channel = part => {
          const value = String(part).endsWith("%") ? Number.parseFloat(part) * 2.55 : Number.parseFloat(part);
          return Math.max(0, Math.min(255, Math.round(value))).toString(16).padStart(2, "0");
        };
        if (parts.slice(0, 3).every(part => Number.isFinite(Number.parseFloat(part)))) {
          return { ignored: false, normalized: `#${channel(parts[0])}${channel(parts[1])}${channel(parts[2])}` };
        }
      }
    }
    return { ignored: false, normalized: null };
  }

  function auditPaint(node, property, rawValue, source) {
    const result = normalizeColor(rawValue);
    if (result.ignored) return;
    const context = {
      tag: node.tagName?.toLowerCase() || "unknown",
      id: node.id || "",
      property,
      source,
      raw: String(rawValue)
    };
    if (!result.normalized) {
      unsupportedPaints.push(context);
      return;
    }
    if (!allowed.has(result.normalized)) {
      badPaints.push({ ...context, normalized: result.normalized });
    }
  }

  function shouldAuditComputed(node, style, property) {
    if (["fill", "stroke", "stopColor", "floodColor", "lightingColor"].includes(property)) {
      return node instanceof SVGElement;
    }
    if (property === "color" && node instanceof HTMLInputElement && node.type === "range") return false;
    if (property.startsWith("border")) {
      const side = property.slice("border".length, -"Color".length);
      const borderStyle = style[`border${side}Style`];
      const borderWidth = Number.parseFloat(style[`border${side}Width`] || "0");
      return borderStyle !== "none" && borderStyle !== "hidden" && borderWidth > 0;
    }
    if (property === "outlineColor") {
      return style.outlineStyle !== "none" && Number.parseFloat(style.outlineWidth || "0") > 0;
    }
    if (property === "textDecorationColor") return style.textDecorationLine !== "none";
    if (property === "caretColor") {
      const acceptsText = node instanceof HTMLTextAreaElement ||
        (node instanceof HTMLInputElement && !["range", "checkbox", "radio", "button", "submit", "reset"].includes(node.type)) ||
        node.isContentEditable;
      return acceptsText && document.activeElement === node;
    }
    return true;
  }

  const nodes = [document.documentElement, ...Array.from(document.querySelectorAll("body, body *"))];
  for (const node of nodes) {
    const style = getComputedStyle(node);
    for (const property of computedProperties) {
      if (shouldAuditComputed(node, style, property)) auditPaint(node, property, style[property], "computed");
    }
    for (const attribute of paintAttributes) {
      if (node.hasAttribute?.(attribute)) auditPaint(node, attribute, node.getAttribute(attribute), "attribute");
    }
    const shadowValues = [style.boxShadow, style.textShadow].filter(value => value && value !== "none");
    for (const shadow of shadowValues) {
      const colors = shadow.match(/#[0-9a-fA-F]{3,6}\b|rgba?\([^)]+\)/g) || [];
      colors.forEach(color => auditPaint(node, "shadow", color, "computed"));
    }
  }

  const bodyColorset = document.body?.dataset.colorset || document.body?.dataset.colorSet || "";
  const configColorset = window.D3LogoGallery?.currentConfig?.colorset || "";
  const controlColorset = document.getElementById("colorset")?.value || "";
  if (bodyColorset !== colorset) findings.push(`Body active colorset is ${bodyColorset || "missing"}; expected ${colorset}.`);
  if (configColorset !== colorset) findings.push(`currentConfig.colorset is ${configColorset || "missing"}; expected ${colorset}.`);
  if (controlColorset !== colorset) findings.push(`#colorset value is ${controlColorset || "missing"}; expected ${colorset}.`);

  const svgColorsetMismatches = Array.from(document.querySelectorAll("[data-example] svg, svg#studio-logo")).flatMap(svg => {
    const active = svg.dataset.colorset || svg.dataset.colorSet || "";
    return active === colorset ? [] : [{ id: svg.id || "", active }];
  });
  if (svgColorsetMismatches.length) {
    findings.push(`SVG colorset metadata mismatches: ${JSON.stringify(svgColorsetMismatches.slice(0, 12))}`);
  }
  if (badPaints.length) findings.push(`Paints outside ${colorset}: ${JSON.stringify(badPaints.slice(0, 20))}`);
  if (unsupportedPaints.length) findings.push(`Unsupported active paint syntax: ${JSON.stringify(unsupportedPaints.slice(0, 20))}`);

  return {
    clean: findings.length === 0,
    findings,
    colorset,
    paletteSize: allowed.size,
    auditedNodeCount: nodes.length,
    badPaintCount: badPaints.length,
    unsupportedPaintCount: unsupportedPaints.length,
    badPaints: badPaints.slice(0, 40),
    unsupportedPaints: unsupportedPaints.slice(0, 40),
    svgColorsetMismatches
  };
}
"""


CONTROL_INFO_JS = r"""
(id) => {
  const control = document.getElementById(id);
  if (!control) return null;
  return {
    id,
    tag: control.tagName.toLowerCase(),
    type: control.type || "",
    value: String(control.value ?? ""),
    min: control.min === "" ? null : Number(control.min),
    max: control.max === "" ? null : Number(control.max),
    step: control.step === "" || control.step === "any" ? null : Number(control.step),
    options: Array.from(control.options || [], option => ({ value: option.value, disabled: option.disabled }))
  };
}
"""


APPLY_CONTROL_JS = r"""
async ({ id, value, renderAll }) => {
  const control = document.getElementById(id);
  if (!control) throw new Error(`Missing control #${id}`);
  control.value = String(value);
  control.dispatchEvent(new Event("input", { bubbles: true }));
  control.dispatchEvent(new Event("change", { bubbles: true }));
  await Promise.resolve();
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const api = window.D3LogoGallery;
  if (typeof api?.renderStudio === "function") {
    const result = api.renderStudio();
    if (result && typeof result.then === "function") await result;
  }
  if (renderAll && typeof api?.renderAll === "function") {
    const result = api.renderAll(api.currentConfig);
    if (result && typeof result.then === "function") await result;
  }
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  return String(control.value ?? "");
}
"""


STUDIO_SNAPSHOT_JS = r"""
() => {
  const svg = document.querySelector("svg#studio-logo");
  if (!svg) return null;
  const config = window.D3LogoGallery?.currentConfig || {};
  const primitiveConfig = {};
  for (const [key, value] of Object.entries(config)) {
    if (value == null || ["string", "number", "boolean"].includes(typeof value)) primitiveConfig[key] = value;
  }
  const geometryAttributes = [
    "d", "points", "x", "y", "x1", "x2", "y1", "y2", "cx", "cy", "r", "rx", "ry", "width", "height",
    "transform", "viewBox", "fill", "stroke", "stroke-width", "opacity", "fill-opacity", "stroke-opacity",
    "font-family", "font-size", "font-weight", "letter-spacing", "text-anchor", "href", "xlink:href",
    "clip-path", "mask", "patternTransform", "style"
  ];
  const geometryNodes = [svg, ...Array.from(svg.querySelectorAll("path, rect, circle, ellipse, line, polyline, polygon, text, textPath, use, g, pattern, mask, clipPath"))];
  const geometry = geometryNodes
    .map(node => {
      const attrs = geometryAttributes.flatMap(name => node.hasAttribute(name) ? [`${name}=${node.getAttribute(name)}`] : []);
      const text = ["text", "textPath"].includes(node.tagName) ? (node.textContent || "").trim() : "";
      return `${node.tagName.toLowerCase()}|${attrs.join("|")}|${text}`;
    }).join("\n");
  const firstText = svg.querySelector("text");
  return {
    dataset: Object.fromEntries(Object.entries(svg.dataset).sort(([a], [b]) => a.localeCompare(b))),
    config: primitiveConfig,
    text: (svg.textContent || "").replace(/\s+/g, " ").trim(),
    geometry,
    innerHtml: svg.innerHTML,
    elementCount: svg.querySelectorAll("*").length,
    fontFamily: firstText ? getComputedStyle(firstText).fontFamily : ""
  };
}
"""


RENDER_PASSES_JS = r"""
() => Array.from(document.querySelectorAll("[data-example]"), card => ({
  exampleId: card.dataset.exampleId || "",
  patternId: card.dataset.patternId || "",
  domId: card.id || "",
  visibleId: card.querySelector(".card-head p")?.textContent?.trim() || "",
  svgExampleId: card.querySelector("svg")?.dataset.exampleId || "",
  svgPatternId: card.querySelector("svg")?.dataset.patternId || "",
  compositionId: card.dataset.compositionId || "",
  renderPass: card.dataset.renderPass || card.querySelector("svg")?.dataset.renderPass || null,
  elementCount: card.querySelector("svg")?.querySelectorAll("*").length || 0
}))
"""


def choose_alternate_option(info: dict[str, Any]) -> str | None:
    current = str(info.get("value", ""))
    for option in info.get("options", []):
        value = str(option.get("value", ""))
        if value and value != current and not option.get("disabled"):
            return value
    return None


def choose_alternate_range(info: dict[str, Any]) -> str | None:
    try:
        current = float(info.get("value", 0))
    except (TypeError, ValueError):
        return None
    minimum = info.get("min")
    maximum = info.get("max")
    step = info.get("step")
    minimum = float(minimum) if isinstance(minimum, (int, float)) else 0.0
    maximum = float(maximum) if isinstance(maximum, (int, float)) else max(1.0, current + 1.0)
    step = float(step) if isinstance(step, (int, float)) and step > 0 else max((maximum - minimum) / 10.0, 0.1)
    candidate = maximum if abs(current - maximum) > step / 2 else minimum
    if abs(candidate - current) <= 1e-9:
        candidate = min(maximum, max(minimum, current + step))
    if abs(candidate - current) <= 1e-9:
        return None
    return f"{candidate:g}"


def snapshot_studio(page: Page) -> dict[str, Any] | None:
    return page.evaluate(STUDIO_SNAPSHOT_JS)


def apply_control(page: Page, control_id: str, value: str, *, render_all: bool, wait_ms: int) -> str:
    applied = page.evaluate(APPLY_CONTROL_JS, {"id": control_id, "value": value, "renderAll": render_all})
    page.wait_for_timeout(max(40, min(wait_ms, 500)))
    return str(applied)


def state_changed(before: dict[str, Any], after: dict[str, Any]) -> bool:
    return before.get("dataset") != after.get("dataset") or before.get("config") != after.get("config")


def audit_text_clearance(page: Page, wait_ms: int) -> dict[str, Any]:
    """Audit semantic text layers after scrolling each gallery card into the viewport."""

    card_locator = page.locator("[data-example]")
    card_count = card_locator.count()
    card_reports: list[dict[str, Any]] = []
    finding_records: list[dict[str, Any]] = []
    finding_messages: list[str] = []

    for index in range(card_count):
        card = card_locator.nth(index)
        card.scroll_into_view_if_needed()
        page.wait_for_timeout(max(10, min(wait_ms, 80)))
        card_report = card.evaluate(
            TEXT_CLEARANCE_AUDIT_JS,
            {
                "sampleStepPx": TEXT_SAMPLE_STEP_PX,
                "occlusionTolerance": TEXT_OCCLUSION_TOLERANCE,
                "clipTolerancePx": TEXT_CLIP_TOLERANCE_PX,
                "minOccludedSamples": TEXT_MIN_OCCLUDED_SAMPLES,
            },
        )
        card_reports.append(card_report)
        finding_records.extend(card_report.get("findings", []))
        finding_messages.extend(card_report.get("findingMessages", []))

    return {
        "clean": not finding_records,
        "cardCount": card_count,
        "auditedTextLayerCount": sum(int(item.get("textLayerCount") or 0) for item in card_reports),
        "findingCount": len(finding_records),
        "findings": finding_records,
        "findingMessages": finding_messages,
        "cards": card_reports,
        "thresholds": {
            "sampleStepPx": TEXT_SAMPLE_STEP_PX,
            "occlusionTolerance": TEXT_OCCLUSION_TOLERANCE,
            "clipTolerancePx": TEXT_CLIP_TOLERANCE_PX,
            "minOccludedSamples": TEXT_MIN_OCCLUDED_SAMPLES,
        },
    }


def exercise_controls(page: Page, wait_ms: int) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    findings: list[str] = []
    requested_values: dict[str, str] = {
        "brand": "Verifier Northlight",
        "tagline": "Signal in deterministic motion",
    }

    for control_id in ("brand", "tagline", "font", "pattern", "texture", *RANGE_CONTROL_IDS):
        info = page.evaluate(CONTROL_INFO_JS, control_id)
        if not info:
            findings.append(f"Cannot exercise missing control #{control_id}.")
            continue
        if control_id in requested_values:
            requested = requested_values[control_id]
            if requested == info.get("value"):
                requested += " updated"
        elif control_id in RANGE_CONTROL_IDS:
            requested = choose_alternate_range(info)
        else:
            requested = choose_alternate_option(info)
        if requested is None:
            findings.append(f"Control #{control_id} has no alternate usable value.")
            continue

        before = snapshot_studio(page)
        if before is None:
            findings.append(f"Cannot exercise #{control_id}: #studio-logo is missing.")
            break
        try:
            applied = apply_control(page, control_id, requested, render_all=False, wait_ms=wait_ms)
        except PlaywrightError as error:
            findings.append(f"Control #{control_id} failed during interaction: {error}")
            continue
        after = snapshot_studio(page)
        if after is None:
            findings.append(f"Control #{control_id} removed #studio-logo.")
            continue

        dataset_or_config_changed = state_changed(before, after)
        geometry_changed = before.get("geometry") != after.get("geometry")
        html_changed = before.get("innerHtml") != after.get("innerHtml")
        report = {
            "id": control_id,
            "beforeValue": info.get("value"),
            "requestedValue": requested,
            "appliedValue": applied,
            "datasetOrConfigChanged": dataset_or_config_changed,
            "geometryChanged": geometry_changed,
            "htmlChanged": html_changed,
            "beforeElementCount": before.get("elementCount"),
            "afterElementCount": after.get("elementCount"),
        }
        reports.append(report)

        if applied != str(requested):
            findings.append(f"Control #{control_id} applied {applied!r}; expected {requested!r}.")
        if not dataset_or_config_changed:
            findings.append(f"Control #{control_id} did not change studio dataset or currentConfig.")
        if control_id == "brand" and requested not in after.get("text", ""):
            findings.append("Brand control did not place the requested brand text in #studio-logo.")
        if control_id == "tagline" and requested not in after.get("text", ""):
            findings.append("Tagline control did not place the requested tagline in #studio-logo.")
        if control_id == "font":
            font_changed = before.get("fontFamily") != after.get("fontFamily") or geometry_changed or html_changed
            report["fontChanged"] = font_changed
            if not font_changed:
                findings.append("Font control did not change the rendered studio font or markup.")
        elif control_id not in {"brand", "tagline"} and not geometry_changed:
            findings.append(f"Control #{control_id} did not change studio geometry.")
        elif control_id in {"brand", "tagline"} and not html_changed:
            findings.append(f"Control #{control_id} did not change studio SVG content.")

    return reports, findings


def exercise_boundary_controls(page: Page, wait_ms: int) -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    requested_values: dict[str, str] = {
        "brand": "W" * 32,
        "tagline": "W" * 56,
        "font": "editorial",
    }
    applied_values: dict[str, str] = {}

    for control_id in ("brand", "tagline", "font", *RANGE_CONTROL_IDS):
        info = page.evaluate(CONTROL_INFO_JS, control_id)
        if not info:
            findings.append(f"Cannot exercise boundary value for missing control #{control_id}.")
            continue
        requested = requested_values.get(control_id)
        if requested is None:
            requested = str(info.get("max", ""))
        if not requested:
            findings.append(f"Control #{control_id} does not expose a usable maximum boundary.")
            continue
        try:
            applied = apply_control(page, control_id, requested, render_all=False, wait_ms=wait_ms)
        except PlaywrightError as error:
            findings.append(f"Boundary control #{control_id} failed during interaction: {error}")
            continue
        applied_values[control_id] = applied
        if applied != requested:
            findings.append(f"Boundary control #{control_id} applied {applied!r}; expected {requested!r}.")

    try:
        page.evaluate("() => window.D3LogoGallery.renderAll()")
        page.wait_for_timeout(max(wait_ms, 0))
    except PlaywrightError as error:
        findings.append(f"Boundary renderAll failed: {error}")

    snapshot = snapshot_studio(page)
    if snapshot is None:
        findings.append("Boundary controls removed #studio-logo.")
    return {
        "requestedValues": requested_values,
        "appliedValues": applied_values,
        "brandLength": len(requested_values["brand"]),
        "taglineLength": len(requested_values["tagline"]),
        "studio": snapshot,
    }, findings


def exercise_colorsets(page: Page, wait_ms: int) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    findings: list[str] = []
    info = page.evaluate(CONTROL_INFO_JS, "colorset")
    if not info:
        return reports, ["Cannot exercise missing control #colorset."]
    initial = str(info.get("value", ""))
    modes = ["colorset2", "colorset1"] if initial == "colorset1" else ["colorset1", "colorset2"]

    for mode in modes:
        before = snapshot_studio(page)
        if before is None:
            findings.append(f"Cannot exercise {mode}: #studio-logo is missing.")
            break
        try:
            applied = apply_control(page, "colorset", mode, render_all=True, wait_ms=wait_ms)
        except PlaywrightError as error:
            findings.append(f"Colorset {mode} failed during interaction: {error}")
            continue
        after = snapshot_studio(page)
        if after is None:
            findings.append(f"Colorset {mode} removed #studio-logo.")
            continue
        palette_report = page.evaluate(PALETTE_AUDIT_JS, {"colorset": mode, "allowedColors": COLORSETS[mode]})
        dataset_or_config_changed = state_changed(before, after)
        geometry_changed = before.get("geometry") != after.get("geometry")
        report = {
            "mode": mode,
            "appliedValue": applied,
            "datasetOrConfigChanged": dataset_or_config_changed,
            "geometryChanged": geometry_changed,
            "palette": palette_report,
        }
        reports.append(report)
        if applied != mode:
            findings.append(f"Colorset control applied {applied!r}; expected {mode!r}.")
        if not dataset_or_config_changed:
            findings.append(f"Switching to {mode} did not change studio dataset or currentConfig.")
        if not geometry_changed:
            findings.append(f"Switching to {mode} did not change rendered studio geometry/paint attributes.")
        findings.extend(f"{mode}: {item}" for item in palette_report.get("findings", []))

    return reports, findings


def exercise_replay(page: Page, wait_ms: int) -> tuple[list[dict[str, Any]], list[str]]:
    reports: list[dict[str, Any]] = []
    findings: list[str] = []
    replay_buttons = page.locator("[data-example] [data-replay]")
    button_count = replay_buttons.count()
    if button_count != EXPECTED_PATTERNS:
        findings.append(f"Expected {EXPECTED_PATTERNS} per-card replay buttons, found {button_count}.")

    for index in range(button_count):
        button = replay_buttons.nth(index)
        card = button.locator("xpath=ancestor::*[@data-example][1]")
        card_index = int(
            card.evaluate(
                "card => Array.from(document.querySelectorAll('[data-example]')).indexOf(card)"
            )
        )
        if card_index < 0:
            findings.append(f"Replay button index {index} is not inside a gallery card.")
            continue

        before = page.evaluate(RENDER_PASSES_JS)
        target = button.get_attribute("data-replay") or ""
        card_record = before[card_index]
        valid_targets = {
            card_record.get("exampleId", ""),
            card_record.get("patternId", ""),
            card_record.get("compositionId", ""),
        }
        if target not in valid_targets:
            findings.append(
                f"Replay target {target!r} for card {card_record.get('exampleId') or card_index} does not match its example, pattern, or composition ID."
            )
        try:
            button.evaluate("button => button.click()")
            page.wait_for_timeout(max(70, min(wait_ms, 350)))
        except PlaywrightError as error:
            findings.append(f"Replay button for {card_record.get('exampleId') or card_index} failed: {error}")
            continue
        after = page.evaluate(RENDER_PASSES_JS)
        if len(after) != len(before):
            findings.append(
                f"Replay for {card_record.get('exampleId') or card_index} changed the gallery card count from {len(before)} to {len(after)}."
            )
            continue
        changed_indexes = [
            candidate
            for candidate, (old, new) in enumerate(zip(before, after))
            if old.get("renderPass") != new.get("renderPass")
        ]
        report = {
            "index": card_index,
            "exampleId": card_record.get("exampleId"),
            "target": target,
            "beforeRenderPass": before[card_index].get("renderPass"),
            "afterRenderPass": after[card_index].get("renderPass"),
            "changedIndexes": changed_indexes,
            "elementCount": after[card_index].get("elementCount"),
        }
        reports.append(report)
        if before[card_index].get("renderPass") is None:
            findings.append(f"Card {card_record.get('exampleId') or card_index} did not expose data-render-pass before replay.")
        if changed_indexes != [card_index]:
            findings.append(
                f"Replay for {card_record.get('exampleId') or card_index} changed render-pass indexes {changed_indexes}; expected only [{card_index}]."
            )
        if int(after[card_index].get("elementCount") or 0) <= 8:
            findings.append(f"Replay left card {card_record.get('exampleId') or card_index} with too little SVG content.")
        replayed = after[card_index]
        expected_pattern_id = f"d3-logo-{replayed.get('exampleId', '')}"
        if replayed.get("patternId") != expected_pattern_id:
            findings.append(f"Replay broke example/pattern parity for {replayed.get('exampleId') or card_index}.")
        if replayed.get("domId") != replayed.get("patternId") or replayed.get("visibleId") != replayed.get("patternId"):
            findings.append(f"Replay broke DOM or visible ID parity for {replayed.get('exampleId') or card_index}.")
        if replayed.get("svgExampleId") != replayed.get("exampleId") or replayed.get("svgPatternId") != replayed.get("patternId"):
            findings.append(f"Replay broke SVG ID parity for {replayed.get('exampleId') or card_index}.")

    return reports, findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Gallery HTML file, file URL, or HTTP URL")
    parser.add_argument("--screenshot", type=Path, help="Optional full-page screenshot path")
    parser.add_argument("--initial-screenshot", type=Path, help="Optional full-page screenshot before controls mutate the default compositions")
    parser.add_argument("--small-logo-screenshot", type=Path, help="Optional 96x64 screenshot of the responsive studio mark")
    parser.add_argument("--small-only", action="store_true", help="Run static and 96x64 checks without exercising all controls and replays")
    parser.add_argument("--json-report", type=Path, help="Optional JSON report path")
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("1440x1100"))
    parser.add_argument("--wait-ms", type=int, default=1000, help="Extra browser settle time after load and interactions")
    parser.add_argument("--timeout-ms", type=int, default=60000, help="Navigation and selector timeout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    url = source_to_url(args.input)
    width, height = args.viewport
    console_errors: list[str] = []
    page_errors: list[str] = []
    resource_requests: list[str] = []
    findings: list[str] = []
    report: dict[str, Any] = {
        "clean": False,
        "input": args.input,
        "url": url,
        "viewport": {"width": width, "height": height},
        "expected": {
            "patterns": EXPECTED_PATTERNS,
            "compositions": EXPECTED_COMPOSITIONS,
            "textures": EXPECTED_TEXTURES,
        },
    }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on(
                "request",
                lambda request: resource_requests.append(request.url)
                if request.url.startswith(("http://", "https://")) and request.url.rstrip("/") != url.rstrip("/")
                else None,
            )
            page.goto(url, wait_until="load", timeout=args.timeout_ms)
            try:
                page.wait_for_selector("[data-example] svg", timeout=args.timeout_ms)
            except PlaywrightError as error:
                findings.append(f"Gallery SVG selector did not become ready: {error}")
            page.wait_for_timeout(max(args.wait_ms, 0))

            static_report = page.evaluate(
                STATIC_AUDIT_JS,
                {
                    "expectedPatterns": EXPECTED_PATTERNS,
                    "expectedCompositions": EXPECTED_COMPOSITIONS,
                    "expectedTextures": EXPECTED_TEXTURES,
                    "controlIds": list(CONTROL_IDS),
                },
            )
            report["static"] = static_report
            findings.extend(static_report.get("findings", []))
            d3_version = page.evaluate("() => globalThis.d3 && globalThis.d3.version")
            report["d3Version"] = d3_version
            if d3_version != "7.9.0":
                findings.append(f"Expected embedded D3 7.9.0, found {d3_version!r}.")

            text_clearance_report = audit_text_clearance(page, args.wait_ms)
            report["textClearance"] = text_clearance_report
            findings.extend(text_clearance_report.get("findingMessages", []))

            if args.initial_screenshot:
                args.initial_screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.initial_screenshot.resolve()), full_page=True)
                report["initialScreenshot"] = str(args.initial_screenshot.resolve())

            if args.small_logo_screenshot:
                studio_locator = page.locator("#studio-logo")
                previous_style = studio_locator.get_attribute("style")
                page.evaluate(
                    """() => {
                      const svg = document.querySelector('#studio-logo');
                      svg.style.width = '96px';
                      svg.style.height = '64px';
                      svg.style.minHeight = '0';
                      svg.style.maxHeight = '64px';
                      svg.style.flex = 'none';
                      window.D3LogoGallery.renderStudio();
                    }"""
                )
                page.wait_for_timeout(max(args.wait_ms, 0))
                small_report = page.evaluate(
                    """() => {
                      const svg = document.querySelector('#studio-logo');
                      const compact = svg.querySelector('[data-small-size-lockup="compact-horizontal"]');
                      const initials = svg.querySelector('.orbit-compact-initials');
                      const wordmark = svg.querySelector('.orbit-compact-wordmark');
                      const box = svg.getBoundingClientRect();
                      const initialsBox = initials && initials.getBoundingClientRect();
                      const wordmarkBox = wordmark && wordmark.getBoundingClientRect();
                      let omissionRules = [];
                      try { omissionRules = JSON.parse(svg.dataset.intentionalTextOmissions || "[]"); } catch (_) {}
                      const taglineOmissionDeclared = omissionRules.some(rule => rule?.textRole === "tagline" && rule?.when === "small-size" && String(rule?.reason || "").trim());
                      const visibleTagline = Array.from(svg.querySelectorAll('[data-text-role="tagline"]')).some(node => {
                        const rect = node.getBoundingClientRect();
                        const style = getComputedStyle(node);
                        return rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity || 1) > 0;
                      });
                      const configuredTagline = String(window.D3LogoGallery?.currentConfig?.tagline || "");
                      const accessibleDescription = svg.querySelector(':scope > desc')?.textContent || '';
                      return {
                        width: box.width,
                        height: box.height,
                        smallSize: svg.dataset.smallSize,
                        compactLockup: Boolean(compact),
                        initialsHeight: initialsBox ? initialsBox.height : 0,
                        wordmarkHeight: wordmarkBox ? wordmarkBox.height : 0,
                        wordmarkText: wordmark ? wordmark.textContent : '',
                        taglineOmissionDeclared,
                        visibleTagline,
                        configuredTagline,
                        accessibleDescription,
                        accessibleTaglinePreserved: !configuredTagline || accessibleDescription.includes(configuredTagline)
                      };
                    }"""
                )
                if small_report.get("smallSize") != "true":
                    findings.append("The 96x64 studio mark did not activate data-small-size=true.")
                if not small_report.get("compactLockup"):
                    findings.append("The 96x64 type-orbit mark did not use the compact horizontal lockup.")
                if small_report.get("initialsHeight", 0) < 10:
                    findings.append(f"The 96x64 compact initials are too small: {small_report.get('initialsHeight', 0):.2f}px high.")
                if small_report.get("wordmarkHeight", 0) < 6:
                    findings.append(f"The 96x64 compact wordmark is too small: {small_report.get('wordmarkHeight', 0):.2f}px high.")
                if not small_report.get("taglineOmissionDeclared"):
                    findings.append("The 96x64 compact lockup omits its tagline without an exact small-size omission declaration.")
                if small_report.get("visibleTagline"):
                    findings.append("The 96x64 compact lockup renders the tagline even though the declared small-size state omits it.")
                if not small_report.get("accessibleTaglinePreserved"):
                    findings.append("The 96x64 compact lockup does not preserve the omitted tagline in its accessible description.")
                args.small_logo_screenshot.parent.mkdir(parents=True, exist_ok=True)
                studio_locator.scroll_into_view_if_needed(timeout=args.timeout_ms)
                studio_box = studio_locator.bounding_box()
                report["smallLogo"] = small_report
                report["smallLogoBox"] = studio_box
                if studio_box is None:
                    findings.append("The 96x64 studio mark has no browser bounding box.")
                else:
                    page.screenshot(
                        path=str(args.small_logo_screenshot.resolve()),
                        clip=studio_box,
                        animations="disabled",
                        timeout=args.timeout_ms,
                    )
                report["smallLogoScreenshot"] = str(args.small_logo_screenshot.resolve())
                if previous_style is None:
                    studio_locator.evaluate("element => element.removeAttribute('style')")
                else:
                    studio_locator.set_attribute("style", previous_style)
                page.evaluate("() => window.D3LogoGallery.renderStudio()")
                page.wait_for_timeout(max(args.wait_ms, 0))

            if not args.small_only:
                control_reports, control_findings = exercise_controls(page, args.wait_ms)
                report["controls"] = control_reports
                findings.extend(control_findings)

                colorset_reports, colorset_findings = exercise_colorsets(page, args.wait_ms)
                report["colorsets"] = colorset_reports
                findings.extend(colorset_findings)

                post_control_text_clearance = audit_text_clearance(page, args.wait_ms)
                report["textClearanceAfterControls"] = post_control_text_clearance
                findings.extend(post_control_text_clearance.get("findingMessages", []))

                boundary_report, boundary_findings = exercise_boundary_controls(page, args.wait_ms)
                report["boundaryControls"] = boundary_report
                findings.extend(boundary_findings)

                boundary_text_clearance = audit_text_clearance(page, args.wait_ms)
                report["textClearanceAtControlBoundaries"] = boundary_text_clearance
                findings.extend(boundary_text_clearance.get("findingMessages", []))

                replay_reports, replay_findings = exercise_replay(page, args.wait_ms)
                report["replay"] = replay_reports
                findings.extend(replay_findings)

            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot.resolve()), full_page=True)
                report["screenshot"] = str(args.screenshot.resolve())
            browser.close()
    except PlaywrightError as error:
        findings.append(f"Playwright failed: {error}")
    except Exception as error:  # noqa: BLE001 - preserve a JSON report for unexpected verifier failures.
        findings.append(f"Verifier failed unexpectedly: {type(error).__name__}: {error}")

    if console_errors:
        findings.extend(f"Browser console error: {item}" for item in console_errors)
    if page_errors:
        findings.extend(f"Browser page error: {item}" for item in page_errors)
    if resource_requests:
        findings.append(f"Standalone gallery requested external resources: {resource_requests[:12]}")

    report["browser"] = {
        "consoleErrors": console_errors,
        "pageErrors": page_errors,
        "externalResourceRequests": resource_requests,
    }
    report["findings"] = findings
    report["clean"] = not findings

    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    print(json.dumps(report, indent=2))
    return 0 if report["clean"] else 1


if __name__ == "__main__":
    sys.exit(main())

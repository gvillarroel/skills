#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Verify the standalone D3 logo texture gallery in Chromium."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


EXPECTED_TEXTURES = 40
SMALL_WIDTH = 96


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("viewport must use WIDTHxHEIGHT, for example 1440x1100")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 320 or height < 320:
        raise argparse.ArgumentTypeError("viewport dimensions must be at least 320 pixels")
    return width, height


def source_to_url(source: str) -> str:
    if re.match(r"^https?://", source, flags=re.IGNORECASE) or source.startswith("file://"):
        return source
    path = Path(source).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input HTML not found: {path}")
    return path.as_uri()


CORE_AUDIT_JS = r"""
({ expectedTextures, smallWidth }) => {
  const findings = [];
  const engine = window.D3LogoDesign;
  const galleryApi = window.D3LogoTextureGallery;
  const cards = Array.from(document.querySelectorAll(".texture-card[data-texture-id]"));
  const gallerySvgs = cards.flatMap(card => Array.from(card.querySelectorAll("svg")));
  const swatches = cards.map(card => card.querySelector("svg[data-texture-swatch]"));
  const canonicalId = /^d3-logo-[a-z0-9]+(?:-[a-z0-9]+)*$/;
  const slugId = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

  function addFinding(message) {
    findings.push(message);
  }

  function duplicates(values) {
    const counts = new Map();
    for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
    return Array.from(counts, ([value, count]) => ({value, count})).filter(item => item.count > 1);
  }

  function registryRecords(registry) {
    if (registry instanceof Map) {
      return Array.from(registry, ([key, value]) =>
        typeof value === "string" ? {id: value} : {...(value || {}), id: value?.id || key}
      );
    }
    if (Array.isArray(registry)) {
      return registry.map((value, index) =>
        typeof value === "string" ? {id: value} : {...(value || {}), id: value?.id || String(index)}
      );
    }
    if (registry && typeof registry === "object") {
      return Object.entries(registry).map(([key, value]) =>
        typeof value === "string" ? {id: value.startsWith("d3-") ? value : key} : {...(value || {}), id: value?.id || key}
      );
    }
    return [];
  }

  function normalizeNumber(value) {
    if (!Number.isFinite(value)) return String(value);
    const rounded = Math.round(value * 10000) / 10000;
    return Object.is(rounded, -0) ? "0" : String(rounded);
  }

  function normalizeAttributeValue(value) {
    return String(value).replace(
      /-?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:e[+-]?\d+)?/gi,
      token => normalizeNumber(Number(token))
    ).replace(/\s+/g, " ").trim();
  }

  const ignoredGeometryAttributes = new Set([
    "id", "class", "fill", "stroke", "color", "opacity", "fill-opacity", "stroke-opacity",
    "stop-color", "stop-opacity", "flood-color", "style", "role", "focusable", "aria-label",
    "aria-labelledby", "aria-describedby"
  ]);

  function normalizedGeometry(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const text = (node.textContent || "").replace(/\s+/g, " ").trim();
      return text ? `#text:${text}` : "";
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return "";
    const tag = node.localName.toLowerCase();
    const attributes = Array.from(node.attributes)
      .filter(attribute => {
        const name = attribute.name.toLowerCase();
        const value = attribute.value.trim();
        if (ignoredGeometryAttributes.has(name) || name.startsWith("data-")) return false;
        if ((name === "href" || name === "xlink:href") && value.startsWith("#")) return false;
        if (/url\(\s*#[^)]+\)/i.test(value)) return false;
        return true;
      })
      .map(attribute => `${attribute.name.toLowerCase()}=${normalizeAttributeValue(attribute.value)}`)
      .sort();
    const children = Array.from(node.childNodes, normalizedGeometry).filter(Boolean).join("");
    return `<${tag}${attributes.length ? " " + attributes.join("|") : ""}>${children}</${tag}>`;
  }

  function fnv1a(source) {
    let hash = 2166136261;
    for (let index = 0; index < source.length; index += 1) {
      hash ^= source.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function patternFingerprint(pattern) {
    const source = pattern ? normalizedGeometry(pattern) : "";
    return {source, hash: source ? fnv1a(source) : ""};
  }

  function paletteCatalog() {
    return galleryApi?.palettes?.colorsets || engine?.PALETTES || engine?.COLORSETS || {};
  }

  function paletteRecord(colorset) {
    const record = paletteCatalog()[colorset];
    return record && typeof record === "object" ? record : null;
  }

  function auditPalette(svg, colorset) {
    const violations = [];
    const palette = paletteRecord(colorset);
    const allowed = new Set(Array.isArray(palette?.allowed) ? palette.allowed.map(value => String(value).toLowerCase()) : []);
    if (!allowed.size) {
      return {safe: false, violations: [`Missing allowed-color tokens for ${colorset}.`]};
    }
    const paintAttributes = ["fill", "stroke", "color", "stop-color", "flood-color"];
    const paintStyleProperties = ["fill", "stroke", "color", "stop-color", "flood-color"];
    const inspectPaint = (element, source, raw) => {
      const value = String(raw || "").trim();
      const normalized = value.toLowerCase();
      if (!value || normalized === "none" || normalized === "currentcolor") return;
      const fragment = normalized.match(/^url\(\s*#([^)\s]+)\s*\)$/);
      if (fragment) {
        if (!svg.querySelector(`#${CSS.escape(fragment[1])}`)) {
          violations.push(`${element.localName} ${source} references missing local paint server #${fragment[1]}.`);
        }
        return;
      }
      if (!allowed.has(normalized)) violations.push(`${element.localName} ${source} uses non-palette paint ${value}.`);
    };
    for (const element of [svg, ...svg.querySelectorAll("*")]) {
      for (const name of paintAttributes) {
        if (element.hasAttribute(name)) inspectPaint(element, name, element.getAttribute(name));
      }
      for (const name of paintStyleProperties) {
        const value = element.style?.getPropertyValue(name);
        if (value) inspectPaint(element, `style.${name}`, value);
      }
    }
    return {safe: violations.length === 0, violations};
  }

  function prohibitedContent(root) {
    const svgGradients = root.querySelectorAll("linearGradient, radialGradient, meshgradient").length;
    const rasterNodes = root.querySelectorAll("img, picture, video, canvas, svg image").length;
    const styleText = Array.from(root.querySelectorAll("style"), node => node.textContent || "").join("\n");
    const cssGradients = (styleText.match(/(?:linear|radial|conic)-gradient\s*\(/gi) || []).length;
    const cssRasterUrls = (styleText.match(/(?:background(?:-image)?|mask(?:-image)?)\s*:[^;{}]*url\(\s*["']?(?:data:image|blob:)/gi) || []).length;
    return {svgGradients, cssGradients, rasterNodes, cssRasterUrls};
  }

  const engineRecords = registryRecords(engine?.TEXTURES);
  const engineIds = engineRecords.map(record => String(record.id || ""));
  const engineById = new Map(engineRecords.map(record => [String(record.id || ""), record]));
  const cardIds = cards.map(card => card.dataset.textureId || "");
  const exampleIds = cards.map(card => card.dataset.exampleId || "");
  const signatures = cards.map(card => card.dataset.geometrySignature || "");
  const bodyCount = Number(document.body?.dataset.textureCount || 0);

  if (!engine || typeof engine.renderTexture !== "function") addFinding("D3LogoDesign.renderTexture is unavailable.");
  if (!galleryApi || typeof galleryApi.renderAll !== "function") addFinding("D3LogoTextureGallery.renderAll is unavailable.");
  if (bodyCount !== expectedTextures) addFinding(`Body data-texture-count is ${bodyCount}; expected ${expectedTextures}.`);
  if (cards.length !== expectedTextures) addFinding(`Expected ${expectedTextures} texture cards, found ${cards.length}.`);
  if (gallerySvgs.length !== expectedTextures) addFinding(`Expected ${expectedTextures} texture SVGs, found ${gallerySvgs.length}.`);
  if (engineIds.length !== expectedTextures) addFinding(`Expected ${expectedTextures} engine textures, found ${engineIds.length}.`);
  if (JSON.stringify(cardIds) !== JSON.stringify(engineIds)) {
    addFinding("Card and engine texture IDs do not have exact ordered parity.");
  }

  const duplicateCardIds = duplicates(cardIds.filter(Boolean));
  const duplicateEngineIds = duplicates(engineIds.filter(Boolean));
  const duplicateExampleIds = duplicates(exampleIds.filter(Boolean));
  const duplicateSignatures = duplicates(signatures.filter(Boolean));
  if (duplicateCardIds.length) addFinding(`Duplicate card texture IDs: ${JSON.stringify(duplicateCardIds)}`);
  if (duplicateEngineIds.length) addFinding(`Duplicate engine texture IDs: ${JSON.stringify(duplicateEngineIds)}`);
  if (duplicateExampleIds.length) addFinding(`Duplicate example IDs: ${JSON.stringify(duplicateExampleIds)}`);
  if (duplicateSignatures.length) addFinding(`Duplicate geometry signatures: ${JSON.stringify(duplicateSignatures)}`);
  if (new Set(exampleIds.filter(Boolean)).size !== expectedTextures) addFinding(`Expected ${expectedTextures} unique example IDs.`);
  if (new Set(signatures.filter(Boolean)).size !== expectedTextures) addFinding(`Expected ${expectedTextures} unique geometry signatures.`);

  const allDomIds = Array.from(document.querySelectorAll("[id]"), node => node.id).filter(Boolean);
  const duplicateDomIds = duplicates(allDomIds);
  if (duplicateDomIds.length) addFinding(`Duplicate DOM IDs: ${JSON.stringify(duplicateDomIds.slice(0, 20))}`);

  const semanticContracts = new Map([
    ["d3-logo-topographic-lines", pattern =>
      pattern?.dataset.textureMechanism === "nested-closed-isolines" &&
      pattern.querySelectorAll('.topographic-isoline[data-isoline-closed="true"]').length >= 8],
    ["d3-logo-chainmail-rings", pattern =>
      pattern?.dataset.textureMechanism === "alternating-under-over-ring-crossings" &&
      pattern.querySelectorAll(".chainmail-under-ring").length > 0 &&
      pattern.querySelectorAll(".chainmail-crossing-cover").length > 0 &&
      pattern.querySelectorAll(".chainmail-over-arc").length > 0],
    ["d3-logo-knit-v-loops", pattern =>
      pattern?.dataset.textureMechanism === "alternating-knit-loop-crossings" &&
      pattern.querySelectorAll(".knit-loop-under").length > 0 &&
      pattern.querySelectorAll(".knit-crossing-cover").length > 0 &&
      pattern.querySelectorAll(".knit-loop-over-bridge").length > 0],
    ["d3-logo-letterpress-slippage", pattern => {
      const stamp = pattern?.querySelector(".letterpress-first-impression");
      const pointCount = String(stamp?.getAttribute("points") || "").trim().split(/\s+/).filter(Boolean).length;
      return pattern?.dataset.textureMechanism === "offset-type-slug-registration" &&
        pattern.querySelectorAll(".letterpress-first-impression").length > 0 &&
        pattern.querySelectorAll(".letterpress-offset-impression").length > 0 &&
        pointCount >= 6;
    }],
    ["d3-logo-embossed-lozenges", pattern =>
      pattern?.dataset.textureMechanism === "faceted-lozenge-relief" &&
      pattern.querySelectorAll(".embossed-bevel-facet").length >= 8 &&
      pattern.querySelectorAll(".embossed-center").length > 0]
  ]);
  const semanticFailures = [];

  const cardDetails = [];
  for (let index = 0; index < cards.length; index += 1) {
    const card = cards[index];
    const textureId = cardIds[index];
    const exampleId = exampleIds[index];
    const signature = signatures[index];
    const expectedExampleId = textureId.replace(/^d3-logo-/, "");
    const title = card.querySelector("h3");
    const idLabel = card.querySelector(".texture-id");
    const svg = swatches[index];
    const record = engineById.get(textureId);
    const cardSvgCount = card.querySelectorAll("svg").length;
    if (!canonicalId.test(textureId)) addFinding(`Card ${index} has invalid canonical texture ID ${textureId || "(missing)"}.`);
    if (!slugId.test(exampleId)) addFinding(`Card ${textureId || index} has invalid example ID ${exampleId || "(missing)"}.`);
    if (exampleId !== expectedExampleId) addFinding(`Card ${textureId || index} example ID must be ${expectedExampleId}.`);
    if (card.id !== textureId) addFinding(`Card ${textureId || index} DOM id must equal its canonical texture ID.`);
    if ((idLabel?.textContent || "").trim() !== textureId) addFinding(`Card ${textureId || index} does not expose its canonical ID visibly.`);
    if (!(title?.textContent || "").trim()) addFinding(`Card ${textureId || index} has no visible title.`);
    if (record && (title?.textContent || "").trim() !== String(record.label || "").trim()) addFinding(`Card/engine visible title mismatch for ${textureId}.`);
    if (record && String(record.geometrySignature || "") !== signature) addFinding(`Card/engine geometry signature mismatch for ${textureId}.`);
    if (cardSvgCount !== 1) addFinding(`Card ${textureId || index} contains ${cardSvgCount} SVGs; expected one.`);
    if (!svg) addFinding(`Card ${textureId || index} has no texture swatch SVG.`);
    if (svg && svg.dataset.textureId !== textureId) addFinding(`SVG/card texture ID mismatch for ${textureId}.`);
    const patterns = svg ? Array.from(svg.querySelectorAll("defs pattern")) : [];
    if (patterns.length !== 1) addFinding(`Texture ${textureId || index} has ${patterns.length} SVG patterns; expected one.`);
    if (patterns[0]?.dataset.textureId !== textureId) addFinding(`Pattern/card texture ID mismatch for ${textureId}.`);
    const semanticContract = semanticContracts.get(textureId);
    if (semanticContract && !semanticContract(patterns[0])) {
      semanticFailures.push(textureId);
      addFinding(`Texture ${textureId} does not satisfy its semantic distinction contract.`);
    }
    const fingerprint = patternFingerprint(patterns[0]);
    if (!fingerprint.source) addFinding(`Texture ${textureId || index} has no normalized pattern geometry.`);
    const colorset = svg?.dataset.colorset || card.dataset.colorset || galleryApi?.currentConfig?.colorset || "colorset1";
    const palette = svg ? auditPalette(svg, colorset) : {safe: false, violations: ["Missing SVG."]};
    if (!palette.safe) addFinding(`Palette violations for ${textureId || index}: ${palette.violations.slice(0, 5).join(" ")}`);
    cardDetails.push({textureId, exampleId, signature, hash: fingerprint.hash, colorset, paletteSafe: palette.safe});
  }

  const hashesByTexture = Object.fromEntries(cardDetails.map(item => [item.textureId, item.hash]));
  const uniqueHashes = new Set(Object.values(hashesByTexture).filter(Boolean)).size;
  if (uniqueHashes !== expectedTextures) addFinding(`Expected ${expectedTextures} unique normalized texture geometry hashes, found ${uniqueHashes}.`);

  const determinismFailures = [];
  if (engine && typeof engine.renderTexture === "function") {
    const current = galleryApi?.currentConfig || {};
    for (let index = 0; index < cards.length; index += 1) {
      const textureId = cardIds[index];
      const svg = swatches[index];
      if (!svg) continue;
      const beforePattern = svg.querySelector("defs pattern");
      const before = patternFingerprint(beforePattern).hash;
      const config = {
        textureId,
        colorset: svg.dataset.colorset || current.colorset || "colorset1",
        density: Number(current.density ?? svg.dataset.density ?? 1),
        curvature: Number(current.curvature ?? svg.dataset.curvature ?? 0.55),
        textureStrength: Number(current.textureStrength ?? svg.dataset.textureStrength ?? 0.7),
        seed: Math.trunc(Number(current.seed ?? svg.dataset.seed ?? 104729))
      };
      try {
        engine.renderTexture(svg, config);
        const afterPattern = svg.querySelector("defs pattern");
        const after = patternFingerprint(afterPattern).hash;
        if (!before || before !== after) determinismFailures.push({textureId, before, after});
      } catch (error) {
        determinismFailures.push({textureId, error: String(error?.message || error)});
      }
    }
  }
  if (determinismFailures.length) addFinding(`Deterministic rerender failures: ${JSON.stringify(determinismFailures.slice(0, 8))}`);

  const offscreen = document.createElement("div");
  offscreen.id = "texture-verifier-offscreen";
  Object.assign(offscreen.style, {position: "fixed", left: "-12000px", top: "0", opacity: "0", pointerEvents: "none"});
  document.body.appendChild(offscreen);

  function renderPass(colorset, smallSize) {
    const failures = [];
    let rendered = 0;
    let paletteSafe = 0;
    let geometryPresent = 0;
    for (const record of engineRecords) {
      const textureId = String(record.id || "");
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      const width = smallSize ? smallWidth : 480;
      const height = smallSize ? Math.round(smallWidth * 270 / 480) : 270;
      svg.id = `verify-${colorset}-${smallSize ? "small" : "full"}-${textureId}`;
      svg.setAttribute("width", String(width));
      svg.setAttribute("height", String(height));
      svg.style.width = `${width}px`;
      svg.style.height = `${height}px`;
      offscreen.appendChild(svg);
      try {
        engine.renderTexture(svg, {
          textureId,
          colorset,
          density: 1,
          curvature: 0.55,
          textureStrength: 0.7,
          seed: 104729,
          outputWidth: width,
          smallSize
        }, {outputWidth: width, smallSize});
        rendered += 1;
        const patterns = svg.querySelectorAll("defs pattern");
        const pattern = patterns[0] || null;
        const fingerprint = patternFingerprint(pattern);
        if (patterns.length === 1 && fingerprint.source) geometryPresent += 1;
        else failures.push(`${textureId}: expected one nonempty pattern, found ${patterns.length}.`);
        if (svg.dataset.textureId !== textureId) failures.push(`${textureId}: rendered SVG texture ID mismatch.`);
        if (svg.dataset.colorset !== colorset) failures.push(`${textureId}: rendered colorset mismatch.`);
        const palette = auditPalette(svg, colorset);
        if (palette.safe) paletteSafe += 1;
        else failures.push(`${textureId}: ${palette.violations.slice(0, 3).join(" ")}`);
        const prohibited = prohibitedContent(svg);
        if (Object.values(prohibited).some(Number)) failures.push(`${textureId}: prohibited content ${JSON.stringify(prohibited)}.`);
        if (smallSize) {
          const actualWidth = svg.getBoundingClientRect().width;
          if (Math.abs(actualWidth - smallWidth) > 1) failures.push(`${textureId}: small render width is ${actualWidth}, expected ${smallWidth}.`);
        }
      } catch (error) {
        failures.push(`${textureId}: ${String(error?.message || error)}`);
      } finally {
        svg.remove();
      }
    }
    return {rendered, paletteSafe, geometryPresent, failures};
  }

  const colorsets = {
    colorset1: renderPass("colorset1", false),
    colorset2: renderPass("colorset2", false)
  };
  const smallSize = {
    width: smallWidth,
    colorset1: renderPass("colorset1", true),
    colorset2: renderPass("colorset2", true)
  };
  offscreen.remove();

  for (const [colorset, result] of Object.entries(colorsets)) {
    if (result.rendered !== expectedTextures || result.paletteSafe !== expectedTextures || result.geometryPresent !== expectedTextures || result.failures.length) {
      addFinding(`${colorset} full-size pass failed: ${JSON.stringify(result.failures.slice(0, 8))}`);
    }
  }
  for (const [colorset, result] of Object.entries({colorset1: smallSize.colorset1, colorset2: smallSize.colorset2})) {
    if (result.rendered !== expectedTextures || result.paletteSafe !== expectedTextures || result.geometryPresent !== expectedTextures || result.failures.length) {
      addFinding(`${colorset} ${smallWidth}px pass failed: ${JSON.stringify(result.failures.slice(0, 8))}`);
    }
  }

  const prohibited = prohibitedContent(document);
  if (prohibited.svgGradients || prohibited.cssGradients) addFinding(`Gradients are forbidden: ${JSON.stringify(prohibited)}.`);
  if (prohibited.rasterNodes || prohibited.cssRasterUrls) addFinding(`Raster or canvas content is forbidden: ${JSON.stringify(prohibited)}.`);

  return {
    findings,
    counts: {
      expected: expectedTextures,
      body: bodyCount,
      cards: cards.length,
      svgs: gallerySvgs.length,
      engineTextures: engineIds.length,
      uniqueCardIds: new Set(cardIds.filter(Boolean)).size,
      uniqueExampleIds: new Set(exampleIds.filter(Boolean)).size,
      uniqueGeometrySignatures: new Set(signatures.filter(Boolean)).size,
      duplicateDomIds: duplicateDomIds.length
    },
    hashes: {unique: uniqueHashes, byTexture: hashesByTexture},
    semanticContracts: {
      checked: semanticContracts.size,
      passing: semanticContracts.size - semanticFailures.length,
      failures: semanticFailures
    },
    determinism: {
      checked: cards.length,
      matching: cards.length - determinismFailures.length,
      failures: determinismFailures
    },
    colorsets,
    smallSize,
    prohibited
  };
}
"""


HASH_AND_LAYOUT_AUDIT_JS = r"""
async ({ expectedTextures }) => {
  const findings = [];
  document.documentElement.style.scrollBehavior = "auto";
  document.body.style.scrollBehavior = "auto";
  const cards = Array.from(document.querySelectorAll(".texture-card[data-texture-id]"));
  const hashFailures = [];
  const layoutFailures = [];
  let workingHashes = 0;
  let labelsChecked = 0;
  let labelsInBounds = 0;
  let labelsUnobscured = 0;

  const settle = () => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const visible = node => {
    if (!node) return false;
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return !node.hidden && style.display !== "none" && style.visibility !== "hidden" && Number(style.opacity || 1) > 0 && rect.width > 0 && rect.height > 0;
  };
  const inside = (inner, outer, tolerance = 0.75) =>
    inner.left >= outer.left - tolerance && inner.top >= outer.top - tolerance &&
    inner.right <= outer.right + tolerance && inner.bottom <= outer.bottom + tolerance;
  const overlaps = (a, b, tolerance = 0.75) =>
    Math.min(a.right, b.right) - Math.max(a.left, b.left) > tolerance &&
    Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > tolerance;
  const unobscured = node => {
    const rect = node.getBoundingClientRect();
    const insetX = Math.min(3, rect.width / 4);
    const insetY = Math.min(3, rect.height / 4);
    const points = [
      [rect.left + rect.width / 2, rect.top + rect.height / 2],
      [rect.left + insetX, rect.top + insetY],
      [rect.right - insetX, rect.top + insetY],
      [rect.left + insetX, rect.bottom - insetY],
      [rect.right - insetX, rect.bottom - insetY]
    ];
    return points.every(([x, y]) => {
      if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) return false;
      const stack = document.elementsFromPoint(x, y);
      const nodeIndex = stack.findIndex(element => element === node || node.contains(element));
      if (nodeIndex < 0) return false;
      return stack.slice(0, nodeIndex).every(element => node.contains(element) || element.contains(node));
    });
  };

  for (const card of cards) {
    const textureId = card.dataset.textureId || "";
    location.hash = `#${encodeURIComponent(textureId)}`;
    await settle();
    const target = document.getElementById(textureId);
    const targetRect = target?.getBoundingClientRect();
    const works = Boolean(
      target && target === card && target.matches(":target") && !target.hidden &&
      targetRect && targetRect.bottom > 0 && targetRect.top < innerHeight
    );
    if (works) workingHashes += 1;
    else hashFailures.push(textureId);

    const title = card.querySelector("h3");
    const idLabel = card.querySelector(".texture-id");
    const cardRect = card.getBoundingClientRect();
    const titleRect = title?.getBoundingClientRect();
    const idRect = idLabel?.getBoundingClientRect();
    if (titleRect && idRect && overlaps(titleRect, idRect)) {
      layoutFailures.push(`${textureId}: title and ID overlap.`);
    }
    for (const [role, node] of [["title", title], ["ID", idLabel]]) {
      labelsChecked += 1;
      if (!visible(node)) {
        layoutFailures.push(`${textureId}: ${role} is not visible.`);
        continue;
      }
      const nodeRect = node.getBoundingClientRect();
      const currentCardRect = card.getBoundingClientRect();
      if (inside(nodeRect, currentCardRect)) labelsInBounds += 1;
      else layoutFailures.push(`${textureId}: ${role} leaves its card.`);
      node.scrollIntoView({block: "center", inline: "nearest"});
      await settle();
      if (unobscured(node)) labelsUnobscured += 1;
      else layoutFailures.push(`${textureId}: ${role} is overlapped or not fully hittable.`);
    }
  }
  history.replaceState(null, "", `${location.pathname}${location.search}`);
  window.scrollTo(0, 0);
  await settle();

  if (cards.length !== expectedTextures) findings.push(`Hash/layout pass found ${cards.length} cards; expected ${expectedTextures}.`);
  if (hashFailures.length) findings.push(`Direct hash failures: ${hashFailures.join(", ")}.`);
  if (layoutFailures.length) findings.push(`Title/ID layout failures: ${layoutFailures.slice(0, 12).join(" ")}`);
  return {
    findings,
    directHashes: {checked: cards.length, working: workingHashes, failures: hashFailures},
    labels: {
      checked: labelsChecked,
      inBounds: labelsInBounds,
      unobscured: labelsUnobscured,
      failures: layoutFailures
    }
  };
}
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify the standalone D3 logo texture gallery in Chromium.")
    parser.add_argument("input", help="Local HTML path, file URL, or HTTP(S) URL")
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("1440x1100"))
    parser.add_argument("--screenshot", type=Path, help="Optional full-page screenshot path")
    parser.add_argument("--json-report", type=Path, help="Optional JSON report path")
    parser.add_argument("--wait-ms", type=int, default=500, help="Extra settle time after page load")
    parser.add_argument("--timeout-ms", type=int, default=60000, help="Navigation and readiness timeout")
    args = parser.parse_args()
    if args.wait_ms < 0:
        parser.error("--wait-ms must be nonnegative")
    if args.timeout_ms <= 0:
        parser.error("--timeout-ms must be positive")
    return args


def main() -> int:
    args = parse_args()
    url = source_to_url(args.input)
    width, height = args.viewport
    findings: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    external_requests: list[str] = []
    report: dict[str, Any] = {
        "clean": False,
        "input": args.input,
        "url": url,
        "viewport": {"width": width, "height": height},
    }

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.on(
                "console",
                lambda message: console_errors.append(message.text) if message.type == "error" else None,
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))

            initial_url_without_hash = url.split("#", 1)[0]

            def record_request(request: Any) -> None:
                request_url = str(request.url).split("#", 1)[0]
                if request_url.startswith(("http://", "https://")) and request_url != initial_url_without_hash:
                    external_requests.append(request.url)

            page.on("request", record_request)
            page.goto(url, wait_until="load", timeout=args.timeout_ms)
            try:
                page.wait_for_function(
                    """expected => {
                      const cards = Array.from(document.querySelectorAll('.texture-card[data-texture-id]'));
                      return cards.length === expected &&
                        cards.every(card => card.dataset.renderState === 'ready' && card.querySelector('svg defs pattern')) &&
                        typeof window.D3LogoDesign?.renderTexture === 'function';
                    }""",
                    arg=EXPECTED_TEXTURES,
                    timeout=args.timeout_ms,
                )
            except PlaywrightError as error:
                findings.append(f"Texture gallery did not become ready: {error}")
            page.wait_for_timeout(args.wait_ms)

            try:
                core = page.evaluate(
                    CORE_AUDIT_JS,
                    {"expectedTextures": EXPECTED_TEXTURES, "smallWidth": SMALL_WIDTH},
                )
                report.update(
                    {
                        "counts": core.get("counts", {}),
                        "hashes": core.get("hashes", {}),
                        "semanticContracts": core.get("semanticContracts", {}),
                        "determinism": core.get("determinism", {}),
                        "colorsets": core.get("colorsets", {}),
                        "smallSize": core.get("smallSize", {}),
                        "prohibited": core.get("prohibited", {}),
                    }
                )
                findings.extend(core.get("findings", []))
            except PlaywrightError as error:
                findings.append(f"Core browser audit failed: {error}")

            raster_hashes: dict[str, Any] = {}
            for colorset in ("colorset1", "colorset2"):
                try:
                    page.select_option("#colorset", colorset)
                    page.wait_for_function(
                        """value => Array.from(document.querySelectorAll('[data-texture-swatch]')).every(svg => svg.dataset.colorset === value)""",
                        arg=colorset,
                        timeout=args.timeout_ms,
                    )
                    swatches = page.locator("[data-texture-swatch]")
                    by_texture: dict[str, str] = {}
                    for index in range(swatches.count()):
                        swatch = swatches.nth(index)
                        texture_id = swatch.get_attribute("data-texture-swatch") or f"texture-{index}"
                        png = swatch.screenshot(animations="disabled", timeout=args.timeout_ms)
                        by_texture[texture_id] = hashlib.sha256(png).hexdigest()[:16]
                    unique_count = len(set(by_texture.values()))
                    raster_hashes[colorset] = {
                        "count": len(by_texture),
                        "unique": unique_count,
                        "byTexture": by_texture,
                    }
                    if len(by_texture) != EXPECTED_TEXTURES or unique_count != EXPECTED_TEXTURES:
                        findings.append(
                            f"Expected {EXPECTED_TEXTURES} unique raster-visible swatches in {colorset}; "
                            f"found {len(by_texture)} swatches and {unique_count} unique hashes."
                        )
                except PlaywrightError as error:
                    findings.append(f"Raster uniqueness audit failed for {colorset}: {error}")
            report["rasterHashes"] = raster_hashes
            try:
                page.select_option("#colorset", "colorset1")
            except PlaywrightError as error:
                findings.append(f"Could not restore colorset1 after raster audit: {error}")

            try:
                layout = page.evaluate(
                    HASH_AND_LAYOUT_AUDIT_JS,
                    {"expectedTextures": EXPECTED_TEXTURES},
                )
                report["directHashes"] = layout.get("directHashes", {})
                report["labels"] = layout.get("labels", {})
                findings.extend(layout.get("findings", []))
            except PlaywrightError as error:
                findings.append(f"Hash and label-layout audit failed: {error}")

            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshot.resolve()), full_page=True, timeout=args.timeout_ms)
                report["screenshot"] = str(args.screenshot.resolve())
            browser.close()
    except PlaywrightError as error:
        findings.append(f"Playwright failed: {error}")
    except Exception as error:  # noqa: BLE001 - preserve diagnostic JSON on unexpected failures.
        findings.append(f"Verifier failed unexpectedly: {type(error).__name__}: {error}")

    if console_errors:
        findings.extend(f"Browser console error: {message}" for message in console_errors)
    if page_errors:
        findings.extend(f"Browser page error: {message}" for message in page_errors)
    if external_requests:
        findings.append(f"External resource requests are forbidden: {external_requests[:12]}")

    report["browserErrors"] = {
        "console": console_errors,
        "page": page_errors,
        "externalRequests": external_requests,
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

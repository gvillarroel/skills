#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.52.0",
# ]
# ///

"""Evaluate D3 composition variants against source closeness and target armature quality."""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_COMPOSITION = REPO_ROOT / ".agents" / "skills" / "d3-animated-svg" / "assets" / "examples" / "d3-animated-svg" / "composition-sheets.html"
DEFAULT_BASE = REPO_ROOT / ".agents" / "skills" / "d3-animated-svg" / "assets" / "examples" / "d3-animated-svg" / "index.html"

EXPECTED_RENDERERS = {
    "network": {"network"},
    "hierarchy": {"hierarchy", "radial"},
    "flow": {"flow", "matrix"},
    "table": {"table", "matrix", "bar"},
    "matrix": {"matrix", "table", "bar"},
    "set-overlap": {"set-overlap", "lanes"},
    "radial": {"radial", "set-overlap"},
    "geospatial": {"route", "lanes", "radial"},
    "lanes": {"lanes", "table"},
    "geometry": {"flow", "radial", "scatter"},
    "chart": {"scatter", "bar", "lanes", "flow"},
}

TAG_NAMES = ["circle", "ellipse", "rect", "path", "line", "polygon", "polyline", "text"]

EXTRACT_BASE_JS = r"""
() => {
  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  function collectFeatures(svg, options = {}) {
    if (!svg) return null;
    const ignoredSelectors = options.ignoreSelectors || [];
    const ignored = node => ignoredSelectors.some(selector => node.closest(selector));
    const tags = ["circle", "ellipse", "rect", "path", "line", "polygon", "polyline", "text"];
    const tagCounts = Object.fromEntries(tags.map(tag => [tag, 0]));
    const classTokens = {};
    const colors = {};
    const centers = [];
    const visibleNodes = Array.from(svg.querySelectorAll(tags.join(","))).filter(node => {
      if (ignored(node)) return false;
      if (node.closest("defs,title,desc")) return false;
      return true;
    });
    for (const node of visibleNodes) {
      const tag = node.tagName.toLowerCase();
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      for (const token of (node.getAttribute("class") || "").split(/\s+/).filter(Boolean)) {
        classTokens[token] = (classTokens[token] || 0) + 1;
      }
      for (const attr of ["fill", "stroke"]) {
        const value = node.getAttribute(attr);
        if (value && value !== "none" && !value.startsWith("url(")) {
          colors[value.toLowerCase()] = (colors[value.toLowerCase()] || 0) + 1;
        }
      }
      try {
        const box = node.getBBox();
        if (Number.isFinite(box.x) && Number.isFinite(box.y) && box.width >= 0 && box.height >= 0) {
          const rootMatrix = svg.getScreenCTM();
          const nodeMatrix = node.getScreenCTM();
          const matrix = rootMatrix && nodeMatrix ? rootMatrix.inverse().multiply(nodeMatrix) : node.getCTM();
          const corners = [
            new DOMPoint(box.x, box.y),
            new DOMPoint(box.x + box.width, box.y),
            new DOMPoint(box.x + box.width, box.y + box.height),
            new DOMPoint(box.x, box.y + box.height)
          ].map(point => matrix ? point.matrixTransform(matrix) : point);
          const xs = corners.map(point => point.x);
          const ys = corners.map(point => point.y);
          const x = Math.min(...xs);
          const y = Math.min(...ys);
          const width = Math.max(...xs) - x;
          const height = Math.max(...ys) - y;
          const area = Math.max(1, width * height);
          centers.push({
            tag,
            className: node.getAttribute("class") || "",
            x: x + width / 2,
            y: y + height / 2,
            width,
            height,
            area
          });
        }
      } catch (error) {
        // Some transient SVG nodes cannot report a box. They still count in the tag profile.
      }
    }
    const box = svg.getBoundingClientRect();
    return {
      id: svg.id || "",
      viewBox: svg.getAttribute("viewBox") || "",
      width: box.width,
      height: box.height,
      title: svg.querySelector("title")?.textContent || "",
      desc: svg.querySelector("desc")?.textContent || "",
      elementCount: svg.querySelectorAll("*").length,
      markCount: visibleNodes.length,
      tagCounts,
      classTokens,
      colors,
      centers,
      text: (svg.textContent || "").replace(/\s+/g, " ").trim()
    };
  }

  const metadata = window.D3_ANIMATED_SVG_EXAMPLES || [];
  const patterns = metadata.map(item => {
    const svg = document.querySelector(`svg#${cssEscape(item.id)}`);
    return {
      sourceId: item.id,
      patternId: item.patternId || `d3-pattern-${item.id}`,
      title: item.title || item.id,
      kicker: item.kicker || "",
      copy: item.copy || "",
      features: collectFeatures(svg)
    };
  });
  return {
    metadata,
    bodyExampleCount: Number(document.body.dataset.exampleCount || 0),
    patterns
  };
}
"""

EXTRACT_COMPOSITION_JS = r"""
async ({ onlyIds }) => {
  const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
  const only = new Set(onlyIds || []);
  const shouldKeep = id => !only.size || only.has(id);

  function cssEscape(value) {
    if (window.CSS && typeof window.CSS.escape === "function") return window.CSS.escape(value);
    return String(value).replace(/[^a-zA-Z0-9_-]/g, "\\$&");
  }

  function collectFeatures(svg, options = {}) {
    if (!svg) return null;
    const ignoredSelectors = options.ignoreSelectors || [
      ".composition-guide",
      ".composition-line",
      ".quadrant-field",
      ".base-signature",
      ".source-pattern-field",
      ".source-adaptation-cues",
      "defs"
    ];
    const ignored = node => ignoredSelectors.some(selector => node.closest(selector));
    const tags = ["circle", "ellipse", "rect", "path", "line", "polygon", "polyline", "text"];
    const tagCounts = Object.fromEntries(tags.map(tag => [tag, 0]));
    const classTokens = {};
    const colors = {};
    const centers = [];
    const segments = [];
    const isVisible = node => {
      const style = window.getComputedStyle(node);
      if (!style || style.display === "none" || style.visibility === "hidden") return false;
      const opacity = Number(style.opacity || node.getAttribute("opacity") || 1);
      if (Number.isFinite(opacity) && opacity <= 0.025) return false;
      return true;
    };
    const pointInSvgSpace = (node, x, y) => {
      const rootMatrix = svg.getScreenCTM();
      const nodeMatrix = node.getScreenCTM();
      const matrix = rootMatrix && nodeMatrix ? rootMatrix.inverse().multiply(nodeMatrix) : node.getCTM();
      const point = new DOMPoint(x, y);
      return matrix ? point.matrixTransform(matrix) : point;
    };
    const addSegment = (node, a, b) => {
      const length = Math.hypot(b.x - a.x, b.y - a.y);
      if (!Number.isFinite(length) || length < 2) return;
      segments.push({
        tag: node.tagName.toLowerCase(),
        className: node.getAttribute("class") || "",
        x1: a.x,
        y1: a.y,
        x2: b.x,
        y2: b.y,
        midX: (a.x + b.x) / 2,
        midY: (a.y + b.y) / 2,
        length,
        stroke: node.getAttribute("stroke") || ""
      });
    };
    const collectSegments = node => {
      const tag = node.tagName.toLowerCase();
      try {
        if (tag === "line") {
          addSegment(
            node,
            pointInSvgSpace(node, Number(node.getAttribute("x1") || 0), Number(node.getAttribute("y1") || 0)),
            pointInSvgSpace(node, Number(node.getAttribute("x2") || 0), Number(node.getAttribute("y2") || 0))
          );
        } else if (tag === "path") {
          const length = node.getTotalLength();
          if (Number.isFinite(length) && length > 2) {
            const start = node.getPointAtLength(0);
            const end = node.getPointAtLength(length);
            addSegment(node, pointInSvgSpace(node, start.x, start.y), pointInSvgSpace(node, end.x, end.y));
          }
        } else if (tag === "polyline" || tag === "polygon") {
          const values = Array.from(node.points || []).map(point => pointInSvgSpace(node, point.x, point.y));
          for (let index = 1; index < values.length; index += 1) addSegment(node, values[index - 1], values[index]);
          if (tag === "polygon" && values.length > 2) addSegment(node, values[values.length - 1], values[0]);
        }
      } catch (error) {
        // Segment extraction is best effort; the center still participates.
      }
    };
    const visibleNodes = Array.from(svg.querySelectorAll(tags.join(","))).filter(node => {
      if (ignored(node)) return false;
      if (node.closest("defs,title,desc")) return false;
      if (!isVisible(node)) return false;
      return true;
    });
    for (const node of visibleNodes) {
      const tag = node.tagName.toLowerCase();
      tagCounts[tag] = (tagCounts[tag] || 0) + 1;
      for (const token of (node.getAttribute("class") || "").split(/\s+/).filter(Boolean)) {
        classTokens[token] = (classTokens[token] || 0) + 1;
      }
      for (const attr of ["fill", "stroke"]) {
        const value = node.getAttribute(attr);
        if (value && value !== "none" && !value.startsWith("url(")) {
          colors[value.toLowerCase()] = (colors[value.toLowerCase()] || 0) + 1;
        }
      }
      try {
        const box = node.getBBox();
        if (Number.isFinite(box.x) && Number.isFinite(box.y) && box.width >= 0 && box.height >= 0) {
          const rootMatrix = svg.getScreenCTM();
          const nodeMatrix = node.getScreenCTM();
          const matrix = rootMatrix && nodeMatrix ? rootMatrix.inverse().multiply(nodeMatrix) : node.getCTM();
          const corners = [
            new DOMPoint(box.x, box.y),
            new DOMPoint(box.x + box.width, box.y),
            new DOMPoint(box.x + box.width, box.y + box.height),
            new DOMPoint(box.x, box.y + box.height)
          ].map(point => matrix ? point.matrixTransform(matrix) : point);
          const xs = corners.map(point => point.x);
          const ys = corners.map(point => point.y);
          const x = Math.min(...xs);
          const y = Math.min(...ys);
          const width = Math.max(...xs) - x;
          const height = Math.max(...ys) - y;
          const area = Math.max(1, width * height);
          centers.push({
            tag,
            className: node.getAttribute("class") || "",
            x: x + width / 2,
            y: y + height / 2,
            width,
            height,
            area
          });
        }
      } catch (error) {
        // Browser-computed boxes are best effort for path-heavy generated SVGs.
      }
      collectSegments(node);
    }
    const box = svg.getBoundingClientRect();
    return {
      id: svg.id || "",
      viewBox: svg.getAttribute("viewBox") || "",
      width: box.width,
      height: box.height,
      title: svg.querySelector("title")?.textContent || "",
      desc: svg.querySelector("desc")?.textContent || "",
      elementCount: svg.querySelectorAll("*").length,
      markCount: visibleNodes.length,
      tagCounts,
      classTokens,
      colors,
      centers,
      segments,
      text: (svg.textContent || "").replace(/\s+/g, " ").trim()
    };
  }

  const sheets = window.D3_COMPOSITION_SHEETS || [];
  const variants = window.D3_COMPOSITION_VARIANTS || [];
  const reviews = window.D3_COMPOSITION_REVIEW || [];
  const metadata = window.D3_ANIMATED_SVG_EXAMPLES || [];
  const rows = [];
  for (const sheet of sheets) {
    document.querySelector(`[data-sheet-tab="${cssEscape(sheet.id)}"]`)?.click();
    await sleep(1500);
    for (const row of Array.from(document.querySelectorAll(`.composition-card[data-composition-id="${cssEscape(sheet.id)}"]`))) {
      const variantId = row.dataset.compositionPatternId || "";
      if (!shouldKeep(variantId)) continue;
      const svg = row.querySelector("svg[data-composition-pattern-id]");
      rows.push({
        id: variantId,
        compositionId: row.dataset.compositionId || "",
        sourceId: row.dataset.exampleId || "",
        patternId: row.dataset.patternId || "",
        kind: row.dataset.kind || "",
        sourceFamily: row.dataset.sourceFamily || "",
        armatureLines: row.dataset.armatureLines || "",
        quadrants: row.dataset.quadrants || "",
        reviewed: row.dataset.reviewed || "",
        linkHref: row.querySelector("a")?.getAttribute("href") || "",
        visibleText: (row.textContent || "").replace(/\s+/g, " ").trim(),
        svgDataset: svg ? { ...svg.dataset } : {},
        compositionLineCount: svg ? svg.querySelectorAll(".composition-line").length : 0,
        quadrantFieldCount: svg ? svg.querySelectorAll(".quadrant-field").length : 0,
        hasBaseSignature: Boolean(svg?.querySelector(".base-signature")),
        baseSignatureText: svg?.querySelector(".base-signature")?.textContent?.replace(/\s+/g, " ").trim() || "",
        feature: collectFeatures(svg),
        sourceFeature: collectFeatures(svg, { ignoreSelectors: [".composition-guide", ".composition-line", ".quadrant-field", ".base-signature", ".source-adaptation-cues", ".source-pattern-field", "defs"] })
      });
    }
  }
  return { sheets, variants: variants.filter(variant => shouldKeep(variant.id)), reviews, metadata, rows };
}
"""


@dataclass
class Thresholds:
    source: float
    composition: float
    overall: float


def source_to_url(source: str | Path) -> str:
    value = str(source)
    if re.match(r"^https?://", value) or value.startswith("file://"):
        return value
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Input not found: {path}")
    return path.as_uri()


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)x(\d+)", value.strip().lower())
    if not match:
        raise argparse.ArgumentTypeError("Viewport must use WIDTHxHEIGHT, for example 1366x900.")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 320 or height < 320:
        raise argparse.ArgumentTypeError("Viewport dimensions must be at least 320 pixels.")
    return width, height


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    if not math.isfinite(value):
        return low
    return max(low, min(high, value))


def weighted_average(parts: list[tuple[float, float]]) -> float:
    total_weight = sum(weight for _, weight in parts)
    if total_weight <= 0:
        return 0.0
    return clamp(sum(clamp(value) * weight for value, weight in parts) / total_weight)


def vector_cosine(left: dict[str, int], right: dict[str, int]) -> float:
    keys = set(left) | set(right)
    if not keys:
        return 0.0
    dot = sum(float(left.get(key, 0)) * float(right.get(key, 0)) for key in keys)
    l_norm = math.sqrt(sum(float(left.get(key, 0)) ** 2 for key in keys))
    r_norm = math.sqrt(sum(float(right.get(key, 0)) ** 2 for key in keys))
    if l_norm <= 0 or r_norm <= 0:
        return 0.0
    return clamp(dot / (l_norm * r_norm))


def jaccard(left: dict[str, int], right: dict[str, int]) -> float:
    left_keys = {key for key, value in left.items() if value}
    right_keys = {key for key, value in right.items() if value}
    if not left_keys and not right_keys:
        return 0.0
    return len(left_keys & right_keys) / len(left_keys | right_keys)


def mean(values: list[float], fallback: float = 0.0) -> float:
    return statistics.fmean(values) if values else fallback


def median(values: list[float], fallback: float = 0.0) -> float:
    return statistics.median(values) if values else fallback


def centers(feature: dict[str, Any] | None, tags: set[str] | None = None) -> list[dict[str, Any]]:
    if not feature:
        return []
    values = feature.get("centers") or []
    if tags is None:
        return values
    return [item for item in values if item.get("tag") in tags]


def feature_segments(feature: dict[str, Any] | None, tags: set[str] | None = None) -> list[dict[str, Any]]:
    if not feature:
        return []
    values = feature.get("segments") or []
    if tags is None:
        return values
    return [item for item in values if item.get("tag") in tags]


def class_has(item: dict[str, Any], *tokens: str) -> bool:
    class_name = f" {item.get('className') or ''} "
    return any(f" {token} " in class_name for token in tokens)


def focus_family(variant: dict[str, Any]) -> str:
    renderer = variant.get("renderer") or variant.get("kind") or ""
    inferred = variant.get("inferredKind") or variant.get("kind") or ""
    composition_id = variant.get("compositionId") or ""
    if composition_id == "dense-label-lanes":
        return "lanes"
    if renderer in {"network", "flow", "set-overlap", "radial", "hierarchy", "scatter"}:
        return renderer
    if renderer in {"matrix", "table", "bar", "document"}:
        return "grid"
    if inferred in {"network", "flow", "set-overlap", "radial", "hierarchy", "lanes", "chart", "geospatial"}:
        return "scatter" if inferred == "chart" else inferred
    return renderer or inferred or "generic"


def relevant_focus_points(feature: dict[str, Any], variant: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    family = focus_family(variant)
    points = centers(feature)
    source_id = variant.get("sourceId") or ""

    if family == "network":
        selected = [point for point in points if class_has(point, "semantic-network-node") or point.get("tag") in {"circle", "ellipse"}]
    elif family == "flow":
        selected = [point for point in points if class_has(point, "semantic-flow-station") or point.get("tag") in {"circle", "ellipse"}]
        if len(selected) < 3:
            selected = [point for point in points if point.get("tag") in {"circle", "ellipse", "text"}]
    elif family == "set-overlap":
        selected = [point for point in points if class_has(point, "semantic-set-circle") or point.get("tag") in {"circle", "ellipse"}]
    elif family == "grid":
        selected = [point for point in points if class_has(point, "semantic-grid-cell") or point.get("tag") == "rect"]
    elif family == "lanes":
        selected = [
            point for point in points
            if point.get("tag") in {"text", "circle", "ellipse", "rect"}
            or class_has(point, "semantic-lane-mark")
        ]
    elif family == "radial":
        selected = [
            point for point in points
            if class_has(point, "semantic-radial-segment", "semantic-radial-center")
            or point.get("tag") in {"path", "circle", "ellipse", "rect"}
        ]
    elif family == "hierarchy":
        selected = [point for point in points if point.get("tag") in {"circle", "ellipse", "rect", "text"}]
    elif family in {"scatter", "geospatial", "geometry"}:
        selected = [point for point in points if class_has(point, "semantic-scatter-mark") or point.get("tag") in {"circle", "ellipse", "rect"}]
        if len(selected) < 3 and re.search(r"line|area|slope|connected|path|bump|moving|index|forecast|cursor|ecdf", source_id):
            selected = [point for point in points if point.get("tag") in {"path", "line", "polyline", "circle", "ellipse", "rect"}]
    else:
        selected = [point for point in points if point.get("tag") != "text"]

    if not selected:
        selected = points
    return family, selected


def relevant_focus_segments(feature: dict[str, Any], family: str) -> list[dict[str, Any]]:
    segments = feature_segments(feature, {"line", "path", "polyline", "polygon"})
    if family == "network":
        filtered = [segment for segment in segments if class_has(segment, "semantic-network-link") or segment.get("tag") in {"line", "path"}]
    elif family == "flow":
        filtered = [segment for segment in segments if class_has(segment, "semantic-flow-link") or segment.get("tag") in {"path", "line"}]
    elif family == "lanes":
        filtered = [segment for segment in segments if class_has(segment, "semantic-lane-leader") or segment.get("tag") in {"line", "path"}]
    elif family == "hierarchy":
        filtered = [segment for segment in segments if segment.get("tag") in {"line", "path", "polyline"}]
    elif family == "radial":
        filtered = [segment for segment in segments if segment.get("tag") in {"path", "line", "polyline", "polygon"}]
    else:
        filtered = segments
    return filtered or segments


def focus_visibility_score(points: list[dict[str, Any]], family: str) -> float:
    minimums = {
        "network": 7,
        "flow": 4,
        "set-overlap": 3,
        "grid": 9,
        "lanes": 8,
        "radial": 6,
        "hierarchy": 5,
        "scatter": 6,
        "geospatial": 5,
        "geometry": 5,
    }
    return clamp(len(points) / minimums.get(family, 5))


def focus_feature(points: list[dict[str, Any]], segments: list[dict[str, Any]]) -> dict[str, Any]:
    tag_counts = Counter(point.get("tag") or "" for point in points)
    for segment in segments:
        tag_counts[segment.get("tag") or ""] += 1
    return {
        "tagCounts": dict(tag_counts),
        "markCount": len(points) + len(segments),
        "segmentCount": len(segments),
    }


def weighted_center(points: list[dict[str, Any]]) -> tuple[float, float]:
    if not points:
        return 180.0, 110.0
    total = sum(float(point.get("area") or 1) for point in points)
    if total <= 0:
        return mean([float(point["x"]) for point in points], 180.0), mean([float(point["y"]) for point in points], 110.0)
    x = sum(float(point["x"]) * float(point.get("area") or 1) for point in points) / total
    y = sum(float(point["y"]) * float(point.get("area") or 1) for point in points) / total
    return x, y


def line_distance(point: dict[str, Any], start: tuple[float, float], end: tuple[float, float]) -> float:
    px = float(point["x"])
    py = float(point["y"])
    x1, y1 = start
    x2, y2 = end
    numerator = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
    denominator = math.hypot(y2 - y1, x2 - x1)
    return numerator / denominator if denominator else 0.0


def segment_midpoint(segment: dict[str, Any]) -> dict[str, Any]:
    return {
        "x": float(segment.get("midX", (float(segment.get("x1", 0)) + float(segment.get("x2", 0))) / 2)),
        "y": float(segment.get("midY", (float(segment.get("y1", 0)) + float(segment.get("y2", 0))) / 2)),
        "area": max(float(segment.get("length") or 1), 1),
        "tag": segment.get("tag", "line"),
        "className": segment.get("className", ""),
    }


def segment_angle(segment: dict[str, Any]) -> float:
    return math.atan2(float(segment.get("y2", 0)) - float(segment.get("y1", 0)), float(segment.get("x2", 0)) - float(segment.get("x1", 0)))


def angle_similarity(angle: float, target: float) -> float:
    # Directionless segment alignment: a line can be drawn either way and still follow an armature.
    diff = abs((angle - target + math.pi / 2) % math.pi - math.pi / 2)
    return 1 - clamp(diff / (math.pi / 2))


def score_segment_diagonal(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.35
    target = math.atan2(34 - 186, 326 - 34)
    values = []
    for segment in segments:
        mid = segment_midpoint(segment)
        proximity = 1 - clamp(line_distance(mid, (34, 186), (326, 34)) / 92)
        alignment = angle_similarity(segment_angle(segment), target)
        values.append(weighted_average([(proximity, 0.55), (alignment, 0.45)]))
    return mean(values)


def score_segment_grid(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.62
    values = []
    for segment in segments:
        angle = segment_angle(segment)
        values.append(max(angle_similarity(angle, 0), angle_similarity(angle, math.pi / 2)))
    return mean(values)


def score_segment_flow(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.35
    values = []
    for segment in segments:
        dx = abs(float(segment.get("x2", 0)) - float(segment.get("x1", 0)))
        dy = abs(float(segment.get("y2", 0)) - float(segment.get("y1", 0)))
        horizontal = clamp(dx / max(dx + dy, 1))
        span = clamp(dx / 72)
        compact = 1 - clamp(dy / 120)
        values.append(weighted_average([(horizontal, 0.42), (span, 0.34), (compact, 0.24)]))
    return mean(values)


def score_segment_radial(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.45
    values = []
    for segment in segments:
        mid = segment_midpoint(segment)
        radial_angle = math.atan2(float(mid["y"]) - 110, float(mid["x"]) - 180)
        angle = segment_angle(segment)
        radial = angle_similarity(angle, radial_angle)
        tangent = angle_similarity(angle, radial_angle + math.pi / 2)
        radius = math.hypot(float(mid["x"]) - 180, float(mid["y"]) - 110)
        ring_presence = 1.0 if radius > 18 else 0.45
        values.append(weighted_average([(max(radial, tangent), 0.72), (ring_presence, 0.28)]))
    return mean(values)


def score_segment_lanes(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.35
    values = []
    for segment in segments:
        x1 = float(segment.get("x1", 0))
        x2 = float(segment.get("x2", 0))
        y1 = float(segment.get("y1", 0))
        y2 = float(segment.get("y2", 0))
        endpoint_in_lane = (x1 < 110 or x1 > 250) or (x2 < 110 or x2 > 250)
        endpoint_in_field = (105 <= x1 <= 255) or (105 <= x2 <= 255)
        useful_bridge = 1.0 if endpoint_in_lane and endpoint_in_field else 0.35
        readable = 1 - clamp(abs(y2 - y1) / 150)
        values.append(weighted_average([(useful_bridge, 0.68), (readable, 0.32)]))
    return mean(values)


def score_relationships(
    composition_id: str,
    family: str,
    segments: list[dict[str, Any]],
    points: list[dict[str, Any]],
) -> tuple[float, dict[str, float]]:
    if composition_id == "diagonal-armature":
        value = score_segment_diagonal(segments)
    elif composition_id == "flow-spine":
        value = score_segment_flow(segments)
    elif composition_id == "thirds-fifths-grid":
        value = score_segment_grid(segments)
    elif composition_id == "radial-rosette":
        value = score_segment_radial(segments)
    elif composition_id == "dense-label-lanes":
        value = score_segment_lanes(segments)
    elif composition_id == "balance-symmetry":
        midpoints = [segment_midpoint(segment) for segment in segments]
        value = score_balance(midpoints or points)[0] if (midpoints or points) else 0.0
    elif composition_id == "golden-root":
        midpoints = [segment_midpoint(segment) for segment in segments]
        value = score_golden(midpoints or points)[0] if (midpoints or points) else 0.62
    else:
        value = 0.5

    required_relationships = family in {"network", "flow", "lanes", "hierarchy"}
    if not segments and not required_relationships:
        value = max(value, 0.65)
    return value, {"relationshipAlignment": value, "relationshipSegmentCount": float(len(segments))}


def axis_correlation(points: list[dict[str, Any]]) -> float:
    if len(points) < 3:
        return 0.5
    xs = [float(point["x"]) for point in points]
    ys = [-float(point["y"]) for point in points]
    mx = mean(xs)
    my = mean(ys)
    x_var = sum((x - mx) ** 2 for x in xs)
    y_var = sum((y - my) ** 2 for y in ys)
    if x_var <= 0 or y_var <= 0:
        return 0.5
    corr = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(x_var * y_var)
    return clamp((corr + 1) / 2)


def contract_score(row: dict[str, Any], variant: dict[str, Any]) -> tuple[float, list[str]]:
    feature = row.get("feature") or {}
    checks = {
        "stable variant id": bool(re.fullmatch(r"d3-composition-[a-z0-9][a-z0-9-]*-[a-z0-9][a-z0-9-]*", row.get("id", ""))),
        "source id": row.get("sourceId") == variant.get("sourceId"),
        "pattern id": bool(row.get("patternId")) and row.get("patternId") in row.get("linkHref", ""),
        "title and desc": bool(feature.get("title")) and bool(feature.get("desc")),
        "visible svg marks": (feature.get("markCount") or 0) >= 8,
        "composition lines": row.get("compositionLineCount", 0) >= 2,
        "quadrant fields": row.get("quadrantFieldCount", 0) >= 4,
        "source signature": bool(row.get("hasBaseSignature")) and row.get("sourceId", "") in row.get("baseSignatureText", ""),
        "armature metadata": bool(row.get("armatureLines")) and bool(row.get("quadrants")),
        "review metadata": row.get("reviewed") == "true" and bool(variant.get("reviewed")),
    }
    missing = [name for name, ok in checks.items() if not ok]
    return sum(1 for ok in checks.values() if ok) / len(checks), missing


def renderer_score(variant: dict[str, Any]) -> float:
    source_kind = variant.get("inferredKind") or variant.get("kind") or ""
    renderer = variant.get("renderer") or variant.get("kind") or ""
    expected = EXPECTED_RENDERERS.get(source_kind, {source_kind})
    if renderer in expected:
        return 1.0
    if renderer == source_kind:
        return 0.9
    if source_kind == "chart" and renderer in {"scatter", "bar", "lanes"}:
        return 1.0
    return 0.35


def score_source_closeness(
    row: dict[str, Any],
    variant: dict[str, Any],
    base: dict[str, Any] | None,
    contract: float,
) -> tuple[float, dict[str, float], list[str]]:
    base_features = (base or {}).get("features") or {}
    variant_features = row.get("sourceFeature") or row.get("feature") or {}
    source_id = variant.get("sourceId") or row.get("sourceId") or ""
    base_title = (base or {}).get("title") or source_id

    tag_similarity = vector_cosine(base_features.get("tagCounts") or {}, variant_features.get("tagCounts") or {})
    color_similarity = jaccard(base_features.get("colors") or {}, variant_features.get("colors") or {})
    base_dominant = dominant_tag(base_features.get("tagCounts") or {})
    variant_dominant = dominant_tag(variant_features.get("tagCounts") or {})
    dominant_match = 1.0 if base_dominant and base_dominant == variant_dominant else 0.45
    signature = 1.0 if source_id and source_id in row.get("baseSignatureText", "") else 0.0
    title_trace = 1.0 if base_title and base_title.lower() in (row.get("visibleText", "") + " " + variant_features.get("title", "")).lower() else 0.35
    metadata_trace = mean([
        1.0 if row.get("sourceId") == source_id else 0.0,
        1.0 if row.get("patternId") == (variant.get("patternId") or row.get("patternId")) else 0.0,
        1.0 if row.get("patternId") and row.get("patternId") in row.get("linkHref", "") else 0.0,
        1.0 if row.get("sourceFamily") else 0.0,
    ])
    renderer = renderer_score(variant)
    geometry = protected_geometry_score(base_features, variant_features, variant)

    components = {
        "metadataTrace": metadata_trace,
        "rendererContinuity": renderer,
        "markProfileSimilarity": tag_similarity,
        "dominantMarkMatch": dominant_match,
        "paletteOverlap": color_similarity,
        "sourceSignature": signature,
        "titleTrace": title_trace,
        "protectedGeometry": geometry,
        "contract": contract,
    }
    score = weighted_average([
        (metadata_trace, 0.20),
        (renderer, 0.21),
        (tag_similarity, 0.17),
        (dominant_match, 0.09),
        (color_similarity, 0.06),
        (signature, 0.09),
        (title_trace, 0.04),
        (geometry, 0.10),
        (contract, 0.04),
    ])
    notes: list[str] = []
    if tag_similarity < 0.35:
        notes.append("low mark-profile similarity to source SVG")
    if renderer < 0.7:
        notes.append("renderer is weakly compatible with inferred source kind")
    if signature < 1:
        notes.append("missing source-pattern signature")
    if geometry < 0.5:
        notes.append("protected chart/map geometry changed substantially")
    return score, components, notes


def dominant_tag(counts: dict[str, int]) -> str:
    filtered = {key: value for key, value in counts.items() if value and key in TAG_NAMES}
    if not filtered:
        return ""
    return max(filtered.items(), key=lambda item: item[1])[0]


def protected_geometry_points(feature: dict[str, Any], source_kind: str) -> list[dict[str, Any]]:
    values = centers(feature)
    if source_kind == "chart":
        selected = [point for point in values if point.get("tag") in {"circle", "ellipse", "rect", "path", "line", "polyline"}]
    elif source_kind == "geospatial":
        selected = [point for point in values if point.get("tag") in {"path", "polygon", "polyline", "circle", "ellipse"}]
    else:
        selected = []
    return selected


def spatial_profile(points: list[dict[str, Any]], bins: int = 4) -> dict[str, int]:
    if not points:
        return {}
    xs = [float(point["x"]) for point in points]
    ys = [float(point["y"]) for point in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max(max_x - min_x, 1)
    height = max(max_y - min_y, 1)
    profile: Counter[str] = Counter()
    for point in points:
        bx = min(bins - 1, max(0, int(((float(point["x"]) - min_x) / width) * bins)))
        by = min(bins - 1, max(0, int(((float(point["y"]) - min_y) / height) * bins)))
        profile[f"{bx}:{by}"] += 1
    return dict(profile)


def protected_geometry_score(
    base_features: dict[str, Any],
    variant_features: dict[str, Any],
    variant: dict[str, Any],
) -> float:
    source_kind = variant.get("inferredKind") or variant.get("kind") or ""
    if source_kind not in {"chart", "geospatial"}:
        return 1.0
    base_points = protected_geometry_points(base_features, source_kind)
    variant_points = protected_geometry_points(variant_features, source_kind)
    if len(base_points) < 4 or len(variant_points) < 4:
        return 0.72
    count_score = 1 - clamp(abs(len(base_points) - len(variant_points)) / max(len(base_points), len(variant_points), 1))
    distribution_score = vector_cosine(spatial_profile(base_points), spatial_profile(variant_points))
    return weighted_average([(count_score, 0.36), (distribution_score, 0.64)])


def score_balance(points: list[dict[str, Any]]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    total = len(points)
    q1 = sum(1 for p in points if p["x"] >= 180 and p["y"] < 110)
    q2 = sum(1 for p in points if p["x"] < 180 and p["y"] < 110)
    q3 = sum(1 for p in points if p["x"] < 180 and p["y"] >= 110)
    q4 = sum(1 for p in points if p["x"] >= 180 and p["y"] >= 110)
    occupied = sum(1 for value in [q1, q2, q3, q4] if value > 0) / 4
    lr = abs((q1 + q4) - (q2 + q3)) / total
    tb = abs((q1 + q2) - (q3 + q4)) / total
    cx, cy = weighted_center(points)
    center_score = 1 - clamp(math.hypot(cx - 180, cy - 110) / 115)
    score = weighted_average([(1 - lr, 0.28), (1 - tb, 0.24), (occupied, 0.23), (center_score, 0.25)])
    return score, {"leftRightBalance": 1 - lr, "topBottomBalance": 1 - tb, "occupiedQuadrants": occupied, "centerScore": center_score}


def score_diagonal(points: list[dict[str, Any]]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    distance_scores = [1 - clamp(line_distance(point, (34, 186), (326, 34)) / 86) for point in points]
    xs = [float(point["x"]) for point in points]
    ys = [float(point["y"]) for point in points]
    spread = min(1.0, (max(xs) - min(xs)) / 250) * min(1.0, (max(ys) - min(ys)) / 125)
    corr = axis_correlation(points)
    score = weighted_average([(mean(distance_scores), 0.45), (spread, 0.25), (corr, 0.30)])
    return score, {"lineProximity": mean(distance_scores), "span": spread, "diagonalCorrelation": corr}


def score_golden(points: list[dict[str, Any]]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    left = [point for point in points if point["x"] < 220]
    right = [point for point in points if point["x"] >= 220]
    left_share = len(left) / len(points)
    right_present = 1.0 if right else 0.0
    left_present = 1.0 if left else 0.0
    ratio_score = 1 - clamp(abs(left_share - 0.62) / 0.45)
    dominance = 1.0 if 0.45 <= left_share <= 0.85 else 0.45
    score = weighted_average([(ratio_score, 0.45), (right_present, 0.22), (left_present, 0.18), (dominance, 0.15)])
    return score, {"leftShare": left_share, "ratioScore": ratio_score, "rightFieldPresent": right_present, "dominance": dominance}


def score_grid(points: list[dict[str, Any]], feature: dict[str, Any]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    xs = [74, 137, 180, 223, 286]
    ys = [66, 110, 154]
    x_scores = [1 - clamp(min(abs(float(point["x"]) - x) for x in xs) / 34) for point in points]
    y_scores = [1 - clamp(min(abs(float(point["y"]) - y) for y in ys) / 28) for point in points]
    rect_share = (feature.get("tagCounts") or {}).get("rect", 0) / max(1, feature.get("markCount") or 1)
    score = weighted_average([(mean(x_scores), 0.30), (mean(y_scores), 0.30), (clamp(rect_share * 2.0), 0.25), (1.0, 0.15)])
    return score, {"xTrackAlignment": mean(x_scores), "yTrackAlignment": mean(y_scores), "rectShare": rect_share}


def score_radial(points: list[dict[str, Any]]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    radii = [math.hypot(float(point["x"]) - 180, float(point["y"]) - 110) for point in points]
    angles = [math.atan2(float(point["y"]) - 110, float(point["x"]) - 180) for point in points if math.hypot(float(point["x"]) - 180, float(point["y"]) - 110) > 8]
    sectors = set(int(((angle + math.pi) / (2 * math.pi)) * 8) % 8 for angle in angles)
    sector_score = len(sectors) / 8
    center_mark = 1.0 if any(math.hypot(float(point["x"]) - 180, float(point["y"]) - 110) < 24 for point in points) else 0.0
    ring_score = 1.0 if len({round(radius / 18) for radius in radii if radius > 12}) >= 2 else 0.45
    radial_extent = clamp((max(radii) - min(radii)) / 80) if radii else 0.0
    score = weighted_average([(sector_score, 0.35), (center_mark, 0.25), (ring_score, 0.22), (radial_extent, 0.18)])
    return score, {"sectorCoverage": sector_score, "centerMark": center_mark, "ringScore": ring_score, "radialExtent": radial_extent}


def score_flow(points: list[dict[str, Any]], feature: dict[str, Any]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    xs = [float(point["x"]) for point in points]
    ys = [float(point["y"]) for point in points]
    span = clamp((max(xs) - min(xs)) / 270)
    left = 1.0 if min(xs) < 75 else 0.4
    right = 1.0 if max(xs) > 285 else 0.4
    path_share = ((feature.get("tagCounts") or {}).get("path", 0) + (feature.get("tagCounts") or {}).get("line", 0)) / max(1, feature.get("markCount") or 1)
    station_rows = 1 - clamp((max(ys) - min(ys)) / 180)
    score = weighted_average([(span, 0.32), (left, 0.16), (right, 0.16), (clamp(path_share * 2.4), 0.22), (station_rows, 0.14)])
    return score, {"xSpan": span, "sourcePresent": left, "outputPresent": right, "connectorShare": path_share, "spineCompactness": station_rows}


def score_lanes(points: list[dict[str, Any]], feature: dict[str, Any]) -> tuple[float, dict[str, float]]:
    if not points:
        return 0.0, {}
    text_points = [point for point in points if point.get("tag") == "text"]
    lane_text = [point for point in text_points if point["x"] < 110 or point["x"] > 250]
    center_marks = [point for point in points if 105 <= point["x"] <= 255 and 35 <= point["y"] <= 185]
    text_lane_score = min(1.0, len(lane_text) / 8) if text_points else 0.65
    data_field_score = len(center_marks) / max(1, len(points))
    connector_share = ((feature.get("tagCounts") or {}).get("line", 0) + (feature.get("tagCounts") or {}).get("path", 0)) / max(1, feature.get("markCount") or 1)
    score = weighted_average([(text_lane_score, 0.36), (data_field_score, 0.34), (clamp(connector_share * 3.0), 0.20), (1.0, 0.10)])
    return score, {"textLaneShare": text_lane_score, "dataFieldShare": data_field_score, "connectorShare": connector_share}


def score_composition(row: dict[str, Any], variant: dict[str, Any], contract: float) -> tuple[float, dict[str, float], list[str]]:
    feature = row.get("sourceFeature") or row.get("feature") or {}
    family, points = relevant_focus_points(feature, variant)
    segment_values = relevant_focus_segments(feature, family)
    selected_feature = focus_feature(points, segment_values)
    composition_id = variant.get("compositionId") or row.get("compositionId")
    if composition_id == "balance-symmetry":
        armature, metrics = score_balance(points)
    elif composition_id == "diagonal-armature":
        armature, metrics = score_diagonal(points)
    elif composition_id == "golden-root":
        armature, metrics = score_golden(points)
    elif composition_id == "thirds-fifths-grid":
        armature, metrics = score_grid(points, selected_feature)
    elif composition_id == "radial-rosette":
        armature, metrics = score_radial(points)
    elif composition_id == "flow-spine":
        armature, metrics = score_flow(points, selected_feature)
    elif composition_id == "dense-label-lanes":
        armature, metrics = score_lanes(points, selected_feature)
    else:
        armature, metrics = 0.0, {}
    relationship, relationship_metrics = score_relationships(composition_id, family, segment_values, points)
    visibility = focus_visibility_score(points, family)
    line_score = clamp(row.get("compositionLineCount", 0) / 4)
    quadrant_score = clamp(row.get("quadrantFieldCount", 0) / 4)
    metadata_score = mean([
        1.0 if variant.get("armatureLines") else 0.0,
        1.0 if variant.get("quadrants") else 0.0,
        1.0 if variant.get("compositionId") == row.get("compositionId") else 0.0,
    ])
    score = weighted_average([
        (armature, 0.48),
        (relationship, 0.18),
        (visibility, 0.10),
        (contract, 0.10),
        (line_score, 0.04),
        (quadrant_score, 0.03),
        (metadata_score, 0.07),
    ])
    notes: list[str] = []
    if armature < 0.55:
        notes.append(f"weak {composition_id} armature metric")
    if visibility < 0.75:
        notes.append("too few visible focus marks for the source family")
    if relationship < 0.45 and family in {"network", "flow", "lanes", "hierarchy"}:
        notes.append("weak relationship alignment for the selected focus marks")
    if contract < 0.9:
        notes.append("composition contract is incomplete")
    metrics.update(relationship_metrics)
    metrics.update({
        "armatureMetric": armature,
        "focusVisibility": visibility,
        "evaluatedFocusMarkCount": float(len(points)),
        "lineScore": line_score,
        "quadrantScore": quadrant_score,
        "metadataScore": metadata_score,
    })
    return score, metrics, notes


def summarize_scores(values: list[dict[str, Any]]) -> dict[str, Any]:
    if not values:
        return {}
    source = [item["sourceClosenessScore"] for item in values]
    composition = [item["compositionScore"] for item in values]
    overall = [item["overallScore"] for item in values]
    return {
        "count": len(values),
        "source": {"min": min(source), "median": median(source), "mean": mean(source), "max": max(source)},
        "composition": {"min": min(composition), "median": median(composition), "mean": mean(composition), "max": max(composition)},
        "overall": {"min": min(overall), "median": median(overall), "mean": mean(overall), "max": max(overall)},
    }


def build_markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# D3 Composition Variant Evaluation",
        "",
        f"- Variants evaluated: {result['summary']['variantCount']}",
        f"- Source patterns loaded: {result['summary']['sourcePatternCount']}",
        f"- Clean: {str(result['clean']).lower()}",
        f"- Thresholds: source {result['thresholds']['source']:.2f}, composition {result['thresholds']['composition']:.2f}, overall {result['thresholds']['overall']:.2f}",
        "",
        "## Score Summary",
        "",
        f"- Source closeness: min {result['summary']['scores']['source']['min']:.3f}, median {result['summary']['scores']['source']['median']:.3f}, mean {result['summary']['scores']['source']['mean']:.3f}",
        f"- Composition fit: min {result['summary']['scores']['composition']['min']:.3f}, median {result['summary']['scores']['composition']['median']:.3f}, mean {result['summary']['scores']['composition']['mean']:.3f}",
        f"- Overall: min {result['summary']['scores']['overall']['min']:.3f}, median {result['summary']['scores']['overall']['median']:.3f}, mean {result['summary']['scores']['overall']['mean']:.3f}",
        "",
        "## By Composition",
        "",
    ]
    for composition_id, stats in result["summary"]["byComposition"].items():
        lines.append(
            f"- `{composition_id}`: {stats['count']} variants, source mean {stats['source']['mean']:.3f}, composition mean {stats['composition']['mean']:.3f}, overall mean {stats['overall']['mean']:.3f}"
        )
    lines.extend(["", "## Lowest Source-Closeness Variants", ""])
    for item in result["lowestSourceCloseness"]:
        lines.append(f"- `{item['id']}`: {item['sourceClosenessScore']:.3f} source, {item['compositionScore']:.3f} composition; {', '.join(item['findings']) or 'no findings'}")
    lines.extend(["", "## Lowest Composition-Fit Variants", ""])
    for item in result["lowestCompositionFit"]:
        lines.append(f"- `{item['id']}`: {item['compositionScore']:.3f} composition, {item['sourceClosenessScore']:.3f} source; {', '.join(item['findings']) or 'no findings'}")
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def capture_samples(page: Any, variants: list[dict[str, Any]], output_dir: Path, limit: int) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    captured: list[str] = []
    selected: list[dict[str, Any]] = []
    source_quota = max(1, limit // 2)
    composition_quota = max(1, limit - source_quota)
    for item in sorted(variants, key=lambda value: value["sourceClosenessScore"])[:source_quota]:
        selected.append(item)
    for item in sorted(variants, key=lambda value: value["compositionScore"])[:composition_quota]:
        if item["id"] not in {entry["id"] for entry in selected}:
            selected.append(item)
    for item in sorted(variants, key=lambda value: value["overallScore"]):
        if len(selected) >= limit:
            break
        if item["id"] not in {entry["id"] for entry in selected}:
            selected.append(item)
    selected = selected[: max(0, limit)]
    for item in selected:
        page.locator(f'[data-sheet-tab="{item["compositionId"]}"]').click()
        page.wait_for_timeout(1500)
        card = page.locator(f'[data-composition-pattern-id="{item["id"]}"]').first
        path = output_dir / f"{item['id']}.png"
        card.screenshot(path=path)
        captured.append(path.as_posix())
    return captured


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("composition_source", nargs="?", default=str(DEFAULT_COMPOSITION), help="Composition sheets HTML file, file URL, or HTTP URL.")
    parser.add_argument("--base-gallery", default=str(DEFAULT_BASE), help="Base D3 gallery HTML file, file URL, or HTTP URL.")
    parser.add_argument("--output", type=Path, help="Write full JSON evaluation output.")
    parser.add_argument("--report", type=Path, help="Write a Markdown summary report.")
    parser.add_argument("--screenshot-dir", type=Path, help="Capture worst-score card screenshots for visual review.")
    parser.add_argument("--screenshot-limit", type=int, default=8)
    parser.add_argument("--only", action="append", default=[], help="Evaluate only this composition variant ID. Repeatable.")
    parser.add_argument("--wait-ms", type=int, default=1800)
    parser.add_argument("--composition-wait-ms", type=int, default=700)
    parser.add_argument("--viewport", type=parse_viewport, default=parse_viewport("1366x900"))
    parser.add_argument("--min-source-score", type=float, default=0.55)
    parser.add_argument("--min-composition-score", type=float, default=0.62)
    parser.add_argument("--min-overall-score", type=float, default=0.60)
    parser.add_argument("--expect-clean", action="store_true", help="Exit non-zero when any score falls below a minimum.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    thresholds = Thresholds(args.min_source_score, args.min_composition_score, args.min_overall_score)
    width, height = args.viewport
    console_errors: list[str] = []
    page_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        base_page = browser.new_page(viewport={"width": width, "height": height})
        composition_page = browser.new_page(viewport={"width": width, "height": height})
        for page in [base_page, composition_page]:
            page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: page_errors.append(str(error)))

        base_page.goto(source_to_url(args.base_gallery), wait_until="load", timeout=90_000)
        base_page.wait_for_timeout(max(args.wait_ms, 0))
        base_data = base_page.evaluate(EXTRACT_BASE_JS)

        composition_page.goto(source_to_url(args.composition_source), wait_until="load", timeout=90_000)
        composition_page.wait_for_timeout(max(args.composition_wait_ms, 0))
        composition_data = composition_page.evaluate(EXTRACT_COMPOSITION_JS, {"onlyIds": args.only})

        base_by_source = {item["sourceId"]: item for item in base_data["patterns"] if item.get("features")}
        variant_by_id = {item["id"]: item for item in composition_data["variants"]}
        rows_by_id = {item["id"]: item for item in composition_data["rows"]}

        evaluations: list[dict[str, Any]] = []
        findings: list[str] = []
        missing_rows = sorted(set(variant_by_id) - set(rows_by_id))
        if missing_rows:
            findings.append(f"{len(missing_rows)} variants were not rendered as cards.")

        for variant_id, variant in sorted(variant_by_id.items()):
            row = rows_by_id.get(variant_id)
            if not row:
                continue
            base = base_by_source.get(variant.get("sourceId"))
            contract, missing_contract = contract_score(row, variant)
            source_score, source_components, source_notes = score_source_closeness(row, variant, base, contract)
            composition_score, composition_components, composition_notes = score_composition(row, variant, contract)
            overall = weighted_average([(source_score, 0.48), (composition_score, 0.52)])
            item_findings: list[str] = []
            if not base:
                item_findings.append("source SVG was not found in the base gallery")
            if missing_contract:
                item_findings.append("missing contract: " + ", ".join(missing_contract))
            item_findings.extend(source_notes)
            item_findings.extend(composition_notes)
            if source_score < thresholds.source:
                item_findings.append(f"source closeness below threshold {thresholds.source:.2f}")
            if composition_score < thresholds.composition:
                item_findings.append(f"composition fit below threshold {thresholds.composition:.2f}")
            if overall < thresholds.overall:
                item_findings.append(f"overall score below threshold {thresholds.overall:.2f}")
            evaluations.append({
                "id": variant_id,
                "compositionId": variant.get("compositionId"),
                "sourceId": variant.get("sourceId"),
                "patternId": row.get("patternId"),
                "renderer": variant.get("renderer") or variant.get("kind"),
                "inferredKind": variant.get("inferredKind"),
                "sourceFamily": variant.get("sourceFamily"),
                "sourceClosenessScore": round(source_score, 4),
                "compositionScore": round(composition_score, 4),
                "overallScore": round(overall, 4),
                "contractScore": round(contract, 4),
                "sourceComponents": {key: round(value, 4) for key, value in source_components.items()},
                "compositionComponents": {key: round(value, 4) for key, value in composition_components.items()},
                "findings": item_findings,
            })

        by_composition: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for evaluation in evaluations:
            by_composition[evaluation["compositionId"]].append(evaluation)
        by_composition_summary = {
            composition_id: summarize_scores(items)
            for composition_id, items in sorted(by_composition.items())
        }
        below = [
            item for item in evaluations
            if item["sourceClosenessScore"] < thresholds.source
            or item["compositionScore"] < thresholds.composition
            or item["overallScore"] < thresholds.overall
        ]
        result = {
            "clean": not findings and not below and not console_errors and not page_errors,
            "findings": findings,
            "thresholds": {
                "source": thresholds.source,
                "composition": thresholds.composition,
                "overall": thresholds.overall,
            },
            "summary": {
                "variantCount": len(evaluations),
                "sourcePatternCount": len(base_by_source),
                "baseMetadataCount": len(base_data.get("metadata") or []),
                "compositionMetadataCount": len(composition_data.get("metadata") or []),
                "reviewedPatternCount": len(composition_data.get("reviews") or []),
                "scores": summarize_scores(evaluations),
                "byComposition": by_composition_summary,
                "belowThresholdCount": len(below),
                "consoleErrorCount": len(console_errors),
                "pageErrorCount": len(page_errors),
            },
            "lowestSourceCloseness": sorted(evaluations, key=lambda item: item["sourceClosenessScore"])[:10],
            "lowestCompositionFit": sorted(evaluations, key=lambda item: item["compositionScore"])[:10],
            "belowThreshold": below[:50],
            "consoleErrors": console_errors[:20],
            "pageErrors": page_errors[:20],
            "variants": evaluations,
        }
        if args.screenshot_dir:
            captured = capture_samples(composition_page, evaluations, args.screenshot_dir, args.screenshot_limit)
            result["sampleScreenshots"] = captured
        browser.close()

    print(json.dumps({
        "clean": result["clean"],
        "variantCount": result["summary"]["variantCount"],
        "sourcePatternCount": result["summary"]["sourcePatternCount"],
        "belowThresholdCount": result["summary"]["belowThresholdCount"],
        "scoreSummary": result["summary"]["scores"],
        "lowestSourceCloseness": [
            {key: item[key] for key in ["id", "sourceClosenessScore", "compositionScore", "overallScore"]}
            for item in result["lowestSourceCloseness"][:5]
        ],
        "lowestCompositionFit": [
            {key: item[key] for key in ["id", "sourceClosenessScore", "compositionScore", "overallScore"]}
            for item in result["lowestCompositionFit"][:5]
        ],
    }, indent=2))
    if args.output:
        write_json(args.output, result)
    if args.report:
        write_text(args.report, build_markdown_report(result))
    if args.expect_clean and not result["clean"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

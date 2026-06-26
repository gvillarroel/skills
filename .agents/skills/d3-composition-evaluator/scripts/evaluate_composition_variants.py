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
          const area = Math.max(1, box.width * box.height);
          centers.push({
            tag,
            className: node.getAttribute("class") || "",
            x: box.x + box.width / 2,
            y: box.y + box.height / 2,
            width: box.width,
            height: box.height,
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

  function collectFeatures(svg) {
    if (!svg) return null;
    const ignoredSelectors = [".composition-guide", ".base-signature", "defs"];
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
          const area = Math.max(1, box.width * box.height);
          centers.push({
            tag,
            className: node.getAttribute("class") || "",
            x: box.x + box.width / 2,
            y: box.y + box.height / 2,
            width: box.width,
            height: box.height,
            area
          });
        }
      } catch (error) {
        // Browser-computed boxes are best effort for path-heavy generated SVGs.
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

  const sheets = window.D3_COMPOSITION_SHEETS || [];
  const variants = window.D3_COMPOSITION_VARIANTS || [];
  const reviews = window.D3_COMPOSITION_REVIEW || [];
  const metadata = window.D3_ANIMATED_SVG_EXAMPLES || [];
  const rows = [];
  for (const sheet of sheets) {
    document.querySelector(`[data-sheet-tab="${cssEscape(sheet.id)}"]`)?.click();
    await sleep(80);
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
        feature: collectFeatures(svg)
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
    variant_features = row.get("feature") or {}
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

    components = {
        "metadataTrace": metadata_trace,
        "rendererContinuity": renderer,
        "markProfileSimilarity": tag_similarity,
        "dominantMarkMatch": dominant_match,
        "paletteOverlap": color_similarity,
        "sourceSignature": signature,
        "titleTrace": title_trace,
        "contract": contract,
    }
    score = weighted_average([
        (metadata_trace, 0.22),
        (renderer, 0.23),
        (tag_similarity, 0.18),
        (dominant_match, 0.10),
        (color_similarity, 0.07),
        (signature, 0.10),
        (title_trace, 0.05),
        (contract, 0.05),
    ])
    notes: list[str] = []
    if tag_similarity < 0.35:
        notes.append("low mark-profile similarity to source SVG")
    if renderer < 0.7:
        notes.append("renderer is weakly compatible with inferred source kind")
    if signature < 1:
        notes.append("missing source-pattern signature")
    return score, components, notes


def dominant_tag(counts: dict[str, int]) -> str:
    filtered = {key: value for key, value in counts.items() if value and key in TAG_NAMES}
    if not filtered:
        return ""
    return max(filtered.items(), key=lambda item: item[1])[0]


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
    data_points = [point for point in points if point.get("tag") != "text"]
    lane_text = [point for point in text_points if point["x"] < 110 or point["x"] > 250]
    center_data = [point for point in data_points if 105 <= point["x"] <= 255 and 35 <= point["y"] <= 185]
    text_lane_score = len(lane_text) / max(1, len(text_points)) if text_points else 0.65
    data_field_score = len(center_data) / max(1, len(data_points)) if data_points else 0.0
    connector_share = ((feature.get("tagCounts") or {}).get("line", 0) + (feature.get("tagCounts") or {}).get("path", 0)) / max(1, feature.get("markCount") or 1)
    score = weighted_average([(text_lane_score, 0.36), (data_field_score, 0.34), (clamp(connector_share * 3.0), 0.20), (1.0, 0.10)])
    return score, {"textLaneShare": text_lane_score, "dataFieldShare": data_field_score, "connectorShare": connector_share}


def score_composition(row: dict[str, Any], variant: dict[str, Any], contract: float) -> tuple[float, dict[str, float], list[str]]:
    feature = row.get("feature") or {}
    points = centers(feature)
    composition_id = variant.get("compositionId") or row.get("compositionId")
    if composition_id == "balance-symmetry":
        armature, metrics = score_balance(points)
    elif composition_id == "diagonal-armature":
        armature, metrics = score_diagonal(points)
    elif composition_id == "golden-root":
        armature, metrics = score_golden(points)
    elif composition_id == "thirds-fifths-grid":
        armature, metrics = score_grid(points, feature)
    elif composition_id == "radial-rosette":
        armature, metrics = score_radial(points)
    elif composition_id == "flow-spine":
        armature, metrics = score_flow(points, feature)
    elif composition_id == "dense-label-lanes":
        armature, metrics = score_lanes(points, feature)
    else:
        armature, metrics = 0.0, {}
    line_score = clamp(row.get("compositionLineCount", 0) / 4)
    quadrant_score = clamp(row.get("quadrantFieldCount", 0) / 4)
    metadata_score = mean([
        1.0 if variant.get("armatureLines") else 0.0,
        1.0 if variant.get("quadrants") else 0.0,
        1.0 if variant.get("compositionId") == row.get("compositionId") else 0.0,
    ])
    score = weighted_average([(armature, 0.56), (contract, 0.16), (line_score, 0.10), (quadrant_score, 0.08), (metadata_score, 0.10)])
    notes: list[str] = []
    if armature < 0.55:
        notes.append(f"weak {composition_id} armature metric")
    if contract < 0.9:
        notes.append("composition contract is incomplete")
    metrics.update({"armatureMetric": armature, "lineScore": line_score, "quadrantScore": quadrant_score, "metadataScore": metadata_score})
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
        page.wait_for_timeout(80)
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

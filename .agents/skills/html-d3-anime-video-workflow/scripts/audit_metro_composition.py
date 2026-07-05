#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


NUMBER = r"-?\d+(?:\.\d+)?"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit Metro Minimal Tonal Motion composition basics in generated standalone HTML."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--source-package",
        type=Path,
        help="Optional source-package.json. When present, gray hierarchy is checked inside the selected visualPattern branch.",
    )
    parser.add_argument("--grid", type=float, default=4.0, help="Expected grid unit for major edges.")
    parser.add_argument(
        "--max-rounded-values",
        type=int,
        default=0,
        help="Maximum nonzero rx/ry/border-radius values allowed.",
    )
    parser.add_argument(
        "--max-rounded-line-signals",
        type=int,
        default=0,
        help="Maximum rounded stroke-linecap/stroke-linejoin signals allowed.",
    )
    parser.add_argument(
        "--max-unnormalized-dynamic-rects",
        type=int,
        default=0,
        help="Maximum dynamic rect geometry calls allowed when runtime rect normalization is missing.",
    )
    parser.add_argument(
        "--max-offgrid-ratio",
        type=float,
        default=0.40,
        help="Maximum fraction of extracted rect edges that may fall off the requested grid.",
    )
    parser.add_argument(
        "--min-shared-edge-ratio",
        type=float,
        default=0.25,
        help="Minimum fraction of rect edges that should share an x or y coordinate with another rect.",
    )
    parser.add_argument(
        "--max-padding-signals",
        type=int,
        default=0,
        help="Maximum allowed box-padding or inset signals in generated HTML.",
    )
    parser.add_argument(
        "--min-gray-levels",
        type=int,
        default=4,
        help="Minimum distinct grayscale hex colors expected for hierarchy levels.",
    )
    parser.add_argument(
        "--min-selected-gray-levels",
        type=int,
        default=4,
        help="Minimum distinct grayscale colors expected inside the selected visualPattern branch when --source-package is supplied.",
    )
    parser.add_argument(
        "--min-gray-luminance-spread",
        type=float,
        default=80.0,
        help="Minimum lightest-to-darkest grayscale spread expected inside the selected visualPattern branch.",
    )
    return parser.parse_args()


def number_value(value: str) -> float:
    return float(value.strip())


def extract_nonzero_rounding(html: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    patterns = [
        ("rx-object", rf"\brx:\s*({NUMBER})"),
        ("ry-object", rf"\bry:\s*({NUMBER})"),
        ("rx-dynamic-object", rf"\brx:\s*[^,\n{{}}]*\?\s*0\s*:\s*({NUMBER})"),
        ("ry-dynamic-object", rf"\bry:\s*[^,\n{{}}]*\?\s*0\s*:\s*({NUMBER})"),
        ("rx-dynamic-object-alt", rf"\brx:\s*[^,\n{{}}]*\?\s*({NUMBER})\s*:\s*0"),
        ("ry-dynamic-object-alt", rf"\bry:\s*[^,\n{{}}]*\?\s*({NUMBER})\s*:\s*0"),
        ("rx-attr", rf"\brx=['\"]({NUMBER})['\"]"),
        ("ry-attr", rf"\bry=['\"]({NUMBER})['\"]"),
        ("border-radius", rf"border-radius\s*:\s*({NUMBER})(?:px)?"),
    ]
    for kind, pattern in patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            value = number_value(match.group(1))
            if abs(value) > 0.001:
                findings.append({"kind": kind, "value": value, "offset": match.start()})
    return findings


def extract_rounded_line_signals(html: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    patterns = [
        ("stroke-linecap", r"(?:\"stroke-linecap\"\s*:\s*\"round\"|stroke-linecap=[\"']round[\"'])"),
        ("stroke-linejoin", r"(?:\"stroke-linejoin\"\s*:\s*\"round\"|stroke-linejoin=[\"']round[\"'])"),
    ]
    for kind, pattern in patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            findings.append({"kind": kind, "offset": match.start(), "sample": match.group(0)[:80]})
    return findings


def has_runtime_rect_normalizer(html: str) -> bool:
    return "function normalizeSvgAttrs" in html and "name === \"rect\"" in html and "snapToGrid" in html


def extract_dynamic_rect_signals(html: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    object_rect = re.compile(r'el\("rect",\s*\{(?P<attrs>.*?)\}\);', flags=re.DOTALL)
    numeric_field = re.compile(r"\b(?:x|y|width|height):\s*-?\d+(?:\.\d+)?(?:\s*,|\s*})")
    required_fields = ("x", "y", "width", "height")
    for match in object_rect.finditer(html):
        attrs = match.group("attrs")
        if not all(re.search(rf"\b{field}\s*:", attrs) for field in required_fields):
            continue
        if len(numeric_field.findall(attrs)) < 4:
            findings.append({"kind": "dynamic-rect-geometry", "offset": match.start(), "sample": attrs[:120]})
    return findings


def extract_rect_edges(html: str) -> list[float]:
    edges: list[float] = []
    object_rect = re.compile(
        rf"x:\s*({NUMBER})\s*,\s*y:\s*({NUMBER})\s*,\s*width:\s*({NUMBER})\s*,\s*height:\s*({NUMBER})",
        flags=re.IGNORECASE,
    )
    attr_rect = re.compile(
        rf"<rect\b[^>]*\bx=['\"]({NUMBER})['\"][^>]*\by=['\"]({NUMBER})['\"][^>]*\bwidth=['\"]({NUMBER})['\"][^>]*\bheight=['\"]({NUMBER})['\"]",
        flags=re.IGNORECASE,
    )
    for pattern in (object_rect, attr_rect):
        for match in pattern.finditer(html):
            x, y, width, height = (number_value(value) for value in match.groups())
            edges.extend([x, x + width, y, y + height])
    return edges


def extract_padding_signals(html: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    patterns = [
        ("css-padding", r"\bpadding(?:-[a-z]+)?\s*:"),
        ("inset", r"\binset\s*:"),
        ("internal-x-offset", r"\bx:\s*[^,\n{}]+?\+\s*(?:8|10|12|14|16|18|20|24|28|32)\b"),
        ("internal-y-offset", r"\by:\s*[^,\n{}]+?\+\s*(?:8|10|12|14|16|18|20|24|28|32|36|38|40|48)\b"),
        ("internal-width-shrink", r"\bwidth:\s*[^,\n{}]+?-\s*(?:16|20|24|28|32|36|40|48|64)\b"),
        ("internal-height-shrink", r"\bheight:\s*[^,\n{}]+?-\s*(?:16|20|24|28|32|36|40|48|64)\b"),
    ]
    for kind, pattern in patterns:
        for match in re.finditer(pattern, html, flags=re.IGNORECASE):
            findings.append({"kind": kind, "offset": match.start(), "sample": match.group(0)[:80]})
    return findings


def parse_hex_color(value: str) -> tuple[int, int, int] | None:
    value = value.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(ch * 2 for ch in value[1:])
    if not re.fullmatch(r"#[0-9a-f]{6}", value):
        return None
    return int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16)


def palette_map(html: str) -> dict[str, str]:
    match = re.search(r"const\s+palette\s*=\s*(\{.*?\});", html, flags=re.DOTALL)
    if not match:
        return {}
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {}
    return {str(key): str(value) for key, value in data.items()}


def declared_gray_levels(html: str) -> list[str]:
    match = re.search(r'data-gray-levels=["\']([^"\']+)["\']', html)
    if not match:
        return []
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


def fill_candidates(expression: str, palette: dict[str, str], gray_levels: list[str]) -> list[str]:
    colors = re.findall(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", expression)
    for name in re.findall(r"palette\.([A-Za-z0-9_]+)", expression):
        if name in palette:
            colors.append(palette[name])
    for raw_index in re.findall(r"grayLevel\((\d+)\)", expression):
        index = int(raw_index)
        if 0 <= index < len(gray_levels):
            colors.append(gray_levels[index])
    return colors


def rect_fill_expressions(html: str) -> list[str]:
    expressions: list[str] = []
    object_rect = re.compile(r'el\("rect",\s*\{(?P<attrs>.*?)\}\);', flags=re.DOTALL)
    for match in object_rect.finditer(html):
        attrs = match.group("attrs")
        fill_match = re.search(r"\bfill:\s*([^,\n{}]+(?:\?[^,\n{}]+:[^,\n{}]+)?)", attrs)
        if fill_match:
            expressions.append(fill_match.group(1))
    for match in re.finditer(r"<rect\b[^>]*\bfill=['\"]([^'\"]+)['\"]", html, flags=re.IGNORECASE):
        expressions.append(match.group(1))
    return expressions


def gray_level_call_colors(scope: str, gray_levels: list[str]) -> list[str]:
    colors: list[str] = []
    for raw_index in re.findall(r"grayLevel\((\d+)\)", scope):
        index = int(raw_index)
        if 0 <= index < len(gray_levels):
            colors.append(gray_levels[index])
    return colors


def extract_gray_levels(
    html: str,
    *,
    scope: str | None = None,
    include_scope_gray_calls: bool = False,
) -> list[str]:
    palette = palette_map(html)
    gray_levels = declared_gray_levels(html)
    fill_source = scope if scope is not None else html
    colors: set[str] = set()
    for expression in rect_fill_expressions(fill_source):
        colors.update(fill_candidates(expression, palette, gray_levels))
    if include_scope_gray_calls and scope is not None:
        colors.update(gray_level_call_colors(scope, gray_levels))
    grays: set[str] = set()
    for color in colors:
        rgb = parse_hex_color(color)
        if rgb and rgb[0] == rgb[1] == rgb[2]:
            grays.add(f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")
    return sorted(grays)


def gray_luminance_spread(gray_levels: list[str]) -> float:
    values = []
    for color in gray_levels:
        rgb = parse_hex_color(color)
        if rgb and rgb[0] == rgb[1] == rgb[2]:
            values.append(rgb[0])
    if len(values) < 2:
        return 0.0
    return float(max(values) - min(values))


def selected_visual_pattern(source_package: Path | None) -> str | None:
    if not source_package:
        return None
    try:
        data = json.loads(source_package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    value = data.get("visualPattern")
    return str(value) if value else None


def selected_pattern_scope(html: str, pattern: str | None) -> str | None:
    if not pattern:
        return None
    matches = list(
        re.finditer(
            r'if\s*\(\s*PACKAGE\.visualPattern\s*===\s*"([^"]+)"\s*\)\s*\{',
            html,
        )
    )
    for index, match in enumerate(matches):
        if match.group(1) != pattern:
            continue
        end = matches[index + 1].start() if index + 1 < len(matches) else html.find("window.renderConceptFrame", match.end())
        if end < 0:
            end = len(html)
        return html[match.start() : end]
    return None


def offgrid_ratio(values: list[float], grid: float) -> float:
    if not values or grid <= 0:
        return 0.0
    offgrid = 0
    for value in values:
        nearest = round(value / grid) * grid
        if abs(value - nearest) > 0.01:
            offgrid += 1
    return offgrid / len(values)


def shared_edge_ratio(values: list[float]) -> float:
    if not values:
        return 0.0
    rounded = [round(value, 2) for value in values]
    counts = Counter(rounded)
    shared = sum(1 for value in rounded if counts[value] > 1)
    return shared / len(rounded)


def main() -> int:
    args = parse_args()
    html = args.html.read_text(encoding="utf-8")
    rounding = extract_nonzero_rounding(html)
    rounded_lines = extract_rounded_line_signals(html)
    rect_edges = extract_rect_edges(html)
    dynamic_rects = extract_dynamic_rect_signals(html)
    runtime_rect_normalizer = has_runtime_rect_normalizer(html)
    padding_signals = extract_padding_signals(html)
    gray_levels = extract_gray_levels(html)
    visual_pattern = selected_visual_pattern(args.source_package)
    pattern_scope = selected_pattern_scope(html, visual_pattern)
    selected_gray_levels = (
        extract_gray_levels(html, scope=pattern_scope, include_scope_gray_calls=True)
        if pattern_scope is not None
        else []
    )
    selected_gray_spread = gray_luminance_spread(selected_gray_levels)
    offgrid = offgrid_ratio(rect_edges, args.grid)
    shared = shared_edge_ratio(rect_edges)
    findings: list[dict[str, object]] = []
    if len(rounding) > args.max_rounded_values:
        findings.append(
            {
                "code": "rounded-borders",
                "message": f"{len(rounding)} nonzero rounding values exceed allowed {args.max_rounded_values}",
                "samples": rounding[:12],
            }
        )
    if len(rounded_lines) > args.max_rounded_line_signals:
        findings.append(
            {
                "code": "rounded-line-caps-or-joins",
                "message": f"{len(rounded_lines)} rounded line cap/join signals exceed allowed {args.max_rounded_line_signals}",
                "samples": rounded_lines[:12],
            }
        )
    if not runtime_rect_normalizer and len(dynamic_rects) > args.max_unnormalized_dynamic_rects:
        findings.append(
            {
                "code": "dynamic-rects-without-runtime-normalizer",
                "message": f"{len(dynamic_rects)} dynamic rect calls cannot be grid-audited without runtime normalization",
                "samples": dynamic_rects[:12],
            }
        )
    if offgrid > args.max_offgrid_ratio:
        findings.append(
            {
                "code": "weak-grid-alignment",
                "message": f"off-grid edge ratio {offgrid:.3f} exceeds {args.max_offgrid_ratio:.3f}",
            }
        )
    if shared < args.min_shared_edge_ratio:
        findings.append(
            {
                "code": "weak-shared-edge-composition",
                "message": f"shared edge ratio {shared:.3f} is below {args.min_shared_edge_ratio:.3f}",
            }
        )
    if len(padding_signals) > args.max_padding_signals:
        findings.append(
            {
                "code": "box-padding-signals",
                "message": f"{len(padding_signals)} box-padding or inset signals exceed allowed {args.max_padding_signals}",
                "samples": padding_signals[:12],
            }
        )
    if len(gray_levels) < args.min_gray_levels:
        findings.append(
            {
                "code": "insufficient-gray-hierarchy",
                "message": f"{len(gray_levels)} grayscale levels found; expected at least {args.min_gray_levels}",
                "grayLevels": gray_levels,
            }
        )
    if args.source_package and pattern_scope is None:
        findings.append(
            {
                "code": "selected-pattern-scope-missing",
                "message": f"Could not locate selected visualPattern branch for {visual_pattern!r}",
            }
        )
    if pattern_scope is not None and len(selected_gray_levels) < args.min_selected_gray_levels:
        findings.append(
            {
                "code": "insufficient-selected-gray-hierarchy",
                "message": (
                    f"{len(selected_gray_levels)} grayscale levels found in selected pattern {visual_pattern!r}; "
                    f"expected at least {args.min_selected_gray_levels}"
                ),
                "grayLevels": selected_gray_levels,
            }
        )
    if pattern_scope is not None and selected_gray_spread < args.min_gray_luminance_spread:
        findings.append(
            {
                "code": "weak-selected-gray-spread",
                "message": (
                    f"selected pattern grayscale luminance spread {selected_gray_spread:.1f} "
                    f"is below {args.min_gray_luminance_spread:.1f}"
                ),
                "grayLevels": selected_gray_levels,
            }
        )
    report = {
        "passed": not findings,
        "html": args.html.as_posix(),
        "grid": args.grid,
        "roundedValueCount": len(rounding),
        "roundedLineSignalCount": len(rounded_lines),
        "rectEdgeCount": len(rect_edges),
        "dynamicRectSignalCount": len(dynamic_rects),
        "runtimeRectNormalizer": runtime_rect_normalizer,
        "offgridRatio": offgrid,
        "sharedEdgeRatio": shared,
        "paddingSignalCount": len(padding_signals),
        "grayLevelCount": len(gray_levels),
        "grayLevels": gray_levels,
        "selectedVisualPattern": visual_pattern,
        "selectedPatternGrayLevelCount": len(selected_gray_levels),
        "selectedPatternGrayLevels": selected_gray_levels,
        "selectedPatternGrayLuminanceSpread": selected_gray_spread,
        "findings": findings,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

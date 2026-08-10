#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare source and recreated SVG visual-style signatures.

The checker is intentionally stricter for style than for data. It allows labels,
values, and mark counts to change, but fails when a reconstruction drifts from
the source pattern's palette, type scale, font family, stroke/opacity profile, or
animation contract.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


RENDER_TAGS = {
    "circle",
    "ellipse",
    "image",
    "line",
    "path",
    "polygon",
    "polyline",
    "rect",
    "text",
    "tspan",
    "use",
}

ANIMATION_TAGS = {"animate", "animateMotion", "animateTransform", "set"}

STYLE_PROPERTIES = {
    "fill",
    "stroke",
    "stroke-width",
    "stroke-dasharray",
    "stroke-linecap",
    "stroke-linejoin",
    "fill-opacity",
    "stroke-opacity",
    "opacity",
    "font-family",
    "font-size",
    "font-weight",
    "paint-order",
}

INHERITED_PROPERTIES = {
    "fill",
    "stroke",
    "font-family",
    "font-size",
    "font-weight",
    "paint-order",
    "stroke-linecap",
    "stroke-linejoin",
}

DEFAULT_CLASS_STYLE = {
    "caption": {
        "fill": "#4f4f4f",
        "font-size": "12px",
        "paint-order": "stroke",
        "stroke": "#ffffff",
        "stroke-width": "3px",
        "stroke-linejoin": "round",
    },
    "label": {
        "fill": "#4f4f4f",
        "font-size": "12px",
        "paint-order": "stroke",
        "stroke": "#ffffff",
        "stroke-width": "3px",
        "stroke-linejoin": "round",
    },
    "mark-label": {
        "fill": "#333e48",
        "font-size": "12px",
        "font-weight": "650",
        "paint-order": "stroke",
        "stroke": "#ffffff",
        "stroke-width": "3px",
        "stroke-linejoin": "round",
    },
    "reverse-label": {
        "fill": "#ffffff",
        "font-size": "12px",
        "font-weight": "700",
        "paint-order": "stroke",
        "stroke": "#333e48",
        "stroke-width": "2px",
        "stroke-linejoin": "round",
    },
}

CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]+)\}", re.MULTILINE | re.DOTALL)
RGB_RE = re.compile(r"rgba?\(([^)]+)\)")
HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)")

NAMED_COLORS = {
    "black": "#000000",
    "white": "#ffffff",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "none": "none",
    "transparent": "transparent",
}


@dataclass
class SvgSignature:
    path: str
    viewbox: tuple[float, float, float, float] | None = None
    width: float | None = None
    height: float | None = None
    root_font_family: str | None = None
    root_font_family_explicit: bool = False
    tag_counts: Counter[str] = field(default_factory=Counter)
    render_tag_counts: Counter[str] = field(default_factory=Counter)
    animation_counts: Counter[str] = field(default_factory=Counter)
    colors: Counter[str] = field(default_factory=Counter)
    fills: Counter[str] = field(default_factory=Counter)
    strokes: Counter[str] = field(default_factory=Counter)
    font_families: Counter[str] = field(default_factory=Counter)
    font_sizes: Counter[float] = field(default_factory=Counter)
    font_weights: Counter[str] = field(default_factory=Counter)
    stroke_widths: Counter[float] = field(default_factory=Counter)
    opacities: Counter[float] = field(default_factory=Counter)
    dasharrays: Counter[str] = field(default_factory=Counter)
    paint_orders: Counter[str] = field(default_factory=Counter)
    animation_durations: Counter[float] = field(default_factory=Counter)
    animation_begins: Counter[float] = field(default_factory=Counter)
    text_count: int = 0
    text_chars: int = 0

    @property
    def aspect_ratio(self) -> float | None:
        if self.viewbox and self.viewbox[3]:
            return self.viewbox[2] / self.viewbox[3]
        if self.width and self.height:
            return self.width / self.height
        return None

    def to_jsonable(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "viewbox": self.viewbox,
            "width": self.width,
            "height": self.height,
            "rootFontFamily": self.root_font_family,
            "rootFontFamilyExplicit": self.root_font_family_explicit,
            "tagCounts": dict(self.tag_counts),
            "renderTagCounts": dict(self.render_tag_counts),
            "animationCounts": dict(self.animation_counts),
            "colors": dict(self.colors),
            "fills": dict(self.fills),
            "strokes": dict(self.strokes),
            "fontFamilies": dict(self.font_families),
            "fontSizes": {str(k): v for k, v in self.font_sizes.items()},
            "fontWeights": dict(self.font_weights),
            "strokeWidths": {str(k): v for k, v in self.stroke_widths.items()},
            "opacities": {str(k): v for k, v in self.opacities.items()},
            "dasharrays": dict(self.dasharrays),
            "paintOrders": dict(self.paint_orders),
            "animationDurations": {str(k): v for k, v in self.animation_durations.items()},
            "animationBegins": {str(k): v for k, v in self.animation_begins.items()},
            "textCount": self.text_count,
            "textChars": self.text_chars,
        }


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def parse_style_attr(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    result: dict[str, str] = {}
    for chunk in value.split(";"):
        if ":" not in chunk:
            continue
        key, val = chunk.split(":", 1)
        key = key.strip()
        if key in STYLE_PROPERTIES:
            result[key] = val.strip()
    return result


def parse_css(style_text: str) -> dict[str, dict[str, str]]:
    rules: dict[str, dict[str, str]] = {}
    if not style_text:
        return rules
    text = re.sub(r"/\*.*?\*/", "", style_text, flags=re.DOTALL)
    for selector_text, body in CSS_RULE_RE.findall(text):
        props = parse_style_attr(body)
        if not props:
            continue
        for selector in selector_text.split(","):
            selector = selector.strip()
            if selector:
                rules[selector] = {**rules.get(selector, {}), **props}
    return rules


def collect_css_rules(root: ET.Element) -> dict[str, dict[str, str]]:
    rules: dict[str, dict[str, str]] = {}
    for cls, props in DEFAULT_CLASS_STYLE.items():
        rules[f".{cls}"] = dict(props)
    for node in root.iter():
        if local_name(node.tag) == "style":
            for selector, props in parse_css("".join(node.itertext())).items():
                rules[selector] = {**rules.get(selector, {}), **props}
    return rules


def selector_matches(selector: str, tag: str, element_id: str | None, classes: set[str]) -> bool:
    selector = selector.strip()
    if not selector or any(token in selector for token in (" ", ">", "+", "~", ":")):
        return False
    if selector.startswith("."):
        return selector[1:] in classes
    if selector.startswith("#"):
        return selector[1:] == element_id
    if "." in selector:
        tag_part, class_part = selector.split(".", 1)
        return tag_part == tag and class_part in classes
    if "#" in selector:
        tag_part, id_part = selector.split("#", 1)
        return tag_part == tag and id_part == element_id
    return selector == tag


def element_style(
    node: ET.Element,
    tag: str,
    css_rules: dict[str, dict[str, str]],
    parent: dict[str, str],
) -> tuple[dict[str, str], set[str]]:
    computed = {k: v for k, v in parent.items() if k in INHERITED_PROPERTIES}
    classes = set((node.get("class") or "").split())
    element_id = node.get("id")

    for selector, props in css_rules.items():
        if selector_matches(selector, tag, element_id, classes):
            computed.update(props)

    for prop in STYLE_PROPERTIES:
        value = node.get(prop)
        if value is not None:
            computed[prop] = value
    computed.update(parse_style_attr(node.get("style")))
    return computed, classes


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    match = NUMBER_RE.search(str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_time(value: str | None) -> float | None:
    if value is None:
        return None
    value = str(value).strip()
    match = NUMBER_RE.search(value)
    if not match:
        return None
    number = float(match.group(0))
    if "ms" in value:
        return number / 1000
    return number


def round_bin(value: float, step: float = 0.5) -> float:
    return round(round(value / step) * step, 3)


def normalize_font_family(value: str | None) -> str | None:
    if not value:
        return None
    parts = [part.strip().strip("'\"").lower() for part in value.split(",")]
    parts = [part for part in parts if part]
    if not parts:
        return None
    return ", ".join(parts)


def normalize_color(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    if not value or value.startswith("url(") or value == "currentcolor":
        return None
    if value in NAMED_COLORS:
        return NAMED_COLORS[value]
    match = HEX_RE.match(value)
    if match:
        body = match.group(1)
        if len(body) == 3:
            body = "".join(ch * 2 for ch in body)
        return f"#{body.lower()}"
    match = RGB_RE.match(value)
    if match:
        parts = [part.strip() for part in match.group(1).split(",")]
        if len(parts) < 3:
            return None
        nums: list[int] = []
        for part in parts[:3]:
            if part.endswith("%"):
                nums.append(round(float(part[:-1]) * 2.55))
            else:
                nums.append(round(float(part)))
        nums = [max(0, min(255, n)) for n in nums]
        return "#{:02x}{:02x}{:02x}".format(*nums)
    return value


def parse_viewbox(value: str | None) -> tuple[float, float, float, float] | None:
    if not value:
        return None
    values = [float(match.group(0)) for match in NUMBER_RE.finditer(value)]
    if len(values) != 4:
        return None
    return values[0], values[1], values[2], values[3]


def text_content(node: ET.Element) -> str:
    return "".join(node.itertext()).strip()


def build_signature(path: Path) -> SvgSignature:
    root = ET.parse(path).getroot()
    css_rules = collect_css_rules(root)
    sig = SvgSignature(path=str(path))
    sig.viewbox = parse_viewbox(root.get("viewBox"))
    sig.width = parse_float(root.get("width"))
    sig.height = parse_float(root.get("height"))
    sig.root_font_family = normalize_font_family(root.get("font-family"))
    sig.root_font_family_explicit = root.get("font-family") is not None

    def walk(node: ET.Element, parent_style: dict[str, str]) -> None:
        tag = local_name(node.tag)
        style, _classes = element_style(node, tag, css_rules, parent_style)
        sig.tag_counts[tag] += 1
        if tag in RENDER_TAGS:
            sig.render_tag_counts[tag] += 1
            fill = normalize_color(style.get("fill"))
            stroke = normalize_color(style.get("stroke"))
            if fill and fill not in {"none", "transparent"}:
                sig.fills[fill] += 1
                sig.colors[fill] += 1
            if stroke and stroke not in {"none", "transparent"}:
                sig.strokes[stroke] += 1
                sig.colors[stroke] += 1
            stroke_width = parse_float(style.get("stroke-width"))
            if stroke_width is not None:
                sig.stroke_widths[round_bin(stroke_width, 0.25)] += 1
            for prop in ("opacity", "fill-opacity", "stroke-opacity"):
                opacity = parse_float(style.get(prop))
                if opacity is not None:
                    sig.opacities[round_bin(opacity, 0.05)] += 1
            if style.get("stroke-dasharray"):
                sig.dasharrays[style["stroke-dasharray"].strip()] += 1
            if style.get("paint-order"):
                sig.paint_orders[style["paint-order"].strip().lower()] += 1

        if tag in {"text", "tspan"}:
            content = text_content(node)
            if content:
                sig.text_count += 1
                sig.text_chars += len(content)
                family = normalize_font_family(style.get("font-family") or root.get("font-family"))
                if family:
                    sig.font_families[family] += 1
                size = parse_float(style.get("font-size"))
                if size is None:
                    size = 16.0
                sig.font_sizes[round_bin(size)] += 1
                weight = style.get("font-weight")
                if weight:
                    sig.font_weights[str(weight).strip().lower()] += 1

        if tag in ANIMATION_TAGS:
            sig.animation_counts[tag] += 1
            duration = parse_time(node.get("dur"))
            begin = parse_time(node.get("begin"))
            if duration is not None:
                sig.animation_durations[round_bin(duration, 0.05)] += 1
            if begin is not None:
                sig.animation_begins[round_bin(begin, 0.05)] += 1

        for child in list(node):
            walk(child, style)

    walk(root, {})
    if not sig.root_font_family:
        inherited = sig.font_families.most_common(1)
        if inherited:
            sig.root_font_family = inherited[0][0]
    return sig


def weighted_jaccard(left: Counter[Any], right: Counter[Any]) -> float:
    keys = set(left) | set(right)
    if not keys:
        return 1.0
    numerator = sum(min(left.get(key, 0), right.get(key, 0)) for key in keys)
    denominator = sum(max(left.get(key, 0), right.get(key, 0)) for key in keys)
    if denominator == 0:
        return 1.0
    return numerator / denominator


def counter_total(counter: Counter[Any]) -> int:
    return sum(counter.values())


def prominent_keys(counter: Counter[Any], min_count: int = 2, min_share: float = 0.03) -> set[Any]:
    total = counter_total(counter)
    if total == 0:
        return set()
    return {key for key, count in counter.items() if count >= min_count and count / total >= min_share}


def values_close(source_values: set[float], candidate_values: set[float], tolerance: float) -> tuple[list[float], list[float]]:
    missing = [
        value
        for value in sorted(source_values)
        if not any(abs(value - other) <= tolerance for other in candidate_values)
    ]
    extra = [
        value
        for value in sorted(candidate_values)
        if not any(abs(value - other) <= tolerance for other in source_values)
    ]
    return missing, extra


def ratio_diff(a: int | float, b: int | float) -> float:
    denom = max(abs(a), abs(b), 1)
    return abs(a - b) / denom


def quantiles(counter: Counter[float]) -> dict[str, float] | None:
    values: list[float] = []
    for value, count in counter.items():
        values.extend([float(value)] * count)
    if not values:
        return None
    values.sort()
    return {
        "min": values[0],
        "median": statistics.median(values),
        "max": values[-1],
    }


def compare_pair(
    name: str,
    source: SvgSignature,
    candidate: SvgSignature,
    *,
    font_tolerance: float,
    stroke_tolerance: float,
    min_color_jaccard: float,
    min_font_jaccard: float,
    min_stroke_jaccard: float,
    max_count_ratio_delta: float,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if source.aspect_ratio and candidate.aspect_ratio:
        if abs(source.aspect_ratio - candidate.aspect_ratio) / source.aspect_ratio > 0.02:
            errors.append(
                f"viewBox aspect ratio changed from {source.aspect_ratio:.3f} to {candidate.aspect_ratio:.3f}"
            )
    if source.viewbox and candidate.viewbox:
        sw, sh = source.viewbox[2], source.viewbox[3]
        cw, ch = candidate.viewbox[2], candidate.viewbox[3]
        if ratio_diff(sw, cw) > 0.02 or ratio_diff(sh, ch) > 0.02:
            errors.append(f"viewBox size changed from {sw:g}x{sh:g} to {cw:g}x{ch:g}")

    if not candidate.root_font_family_explicit:
        errors.append("candidate SVG does not set an explicit root font-family")
    if source.root_font_family and candidate.root_font_family:
        source_families = set(part.strip() for part in source.root_font_family.split(","))
        candidate_families = set(part.strip() for part in candidate.root_font_family.split(","))
        if source_families and candidate_families and source_families.isdisjoint(candidate_families):
            errors.append(
                f"font family drift: source {source.root_font_family!r}, candidate {candidate.root_font_family!r}"
            )

    color_jaccard = weighted_jaccard(source.colors, candidate.colors)
    if color_jaccard < min_color_jaccard:
        errors.append(f"color distribution differs too much: weighted Jaccard {color_jaccard:.3f}")

    source_prominent_colors = prominent_keys(source.colors)
    candidate_colors = set(candidate.colors)
    missing_colors = sorted(source_prominent_colors - candidate_colors)
    extra_colors = sorted(set(candidate.colors) - set(source.colors))
    if missing_colors:
        errors.append(f"candidate is missing prominent source colors: {', '.join(missing_colors)}")
    if extra_colors:
        errors.append(f"candidate introduced colors not present in source: {', '.join(extra_colors)}")

    font_jaccard = weighted_jaccard(source.font_sizes, candidate.font_sizes)
    if font_jaccard < min_font_jaccard:
        errors.append(f"font-size distribution differs too much: weighted Jaccard {font_jaccard:.3f}")
    missing_sizes, extra_sizes = values_close(set(source.font_sizes), set(candidate.font_sizes), font_tolerance)
    if missing_sizes:
        errors.append(f"candidate is missing source font sizes: {', '.join(f'{v:g}' for v in missing_sizes)}")
    if extra_sizes:
        errors.append(f"candidate introduced font sizes not in source profile: {', '.join(f'{v:g}' for v in extra_sizes)}")

    stroke_jaccard = weighted_jaccard(source.stroke_widths, candidate.stroke_widths)
    if stroke_jaccard < min_stroke_jaccard:
        errors.append(f"stroke-width distribution differs too much: weighted Jaccard {stroke_jaccard:.3f}")
    missing_strokes, extra_strokes = values_close(set(source.stroke_widths), set(candidate.stroke_widths), stroke_tolerance)
    if missing_strokes:
        errors.append(f"candidate is missing source stroke widths: {', '.join(f'{v:g}' for v in missing_strokes)}")
    if extra_strokes:
        errors.append(f"candidate introduced stroke widths not in source profile: {', '.join(f'{v:g}' for v in extra_strokes)}")

    opacity_jaccard = weighted_jaccard(source.opacities, candidate.opacities)
    if opacity_jaccard < 0.65 and source.opacities:
        errors.append(f"opacity distribution differs too much: weighted Jaccard {opacity_jaccard:.3f}")

    source_anim_total = counter_total(source.animation_counts)
    candidate_anim_total = counter_total(candidate.animation_counts)
    if source_anim_total and not candidate_anim_total:
        errors.append("source has animation nodes but candidate has none")
    elif source_anim_total and ratio_diff(source_anim_total, candidate_anim_total) > 0.5:
        errors.append(f"animation node count changed from {source_anim_total} to {candidate_anim_total}")

    for tag in sorted(set(source.render_tag_counts) | set(candidate.render_tag_counts)):
        source_count = source.render_tag_counts.get(tag, 0)
        candidate_count = candidate.render_tag_counts.get(tag, 0)
        if source_count >= 8 and candidate_count >= 8 and ratio_diff(source_count, candidate_count) > max_count_ratio_delta:
            warnings.append(f"render tag count for <{tag}> changed from {source_count} to {candidate_count}")
        elif source_count >= 8 and candidate_count < max(4, source_count * 0.35):
            warnings.append(f"candidate has far fewer <{tag}> elements: {candidate_count} vs source {source_count}")

    if source.text_count and candidate.text_count and ratio_diff(source.text_count, candidate.text_count) > 0.45:
        warnings.append(f"text node count changed from {source.text_count} to {candidate.text_count}")

    return {
        "name": name,
        "source": source.to_jsonable(),
        "candidate": candidate.to_jsonable(),
        "metrics": {
            "colorJaccard": color_jaccard,
            "fontSizeJaccard": font_jaccard,
            "strokeWidthJaccard": stroke_jaccard,
            "opacityJaccard": opacity_jaccard,
            "sourceFontSizeQuantiles": quantiles(source.font_sizes),
            "candidateFontSizeQuantiles": quantiles(candidate.font_sizes),
            "sourceTopColors": source.colors.most_common(12),
            "candidateTopColors": candidate.colors.most_common(12),
        },
        "errors": errors,
        "warnings": warnings,
    }


def parse_pair(value: str) -> tuple[str, Path, Path]:
    for delimiter in ("=", "::"):
        if delimiter in value:
            left, right = value.split(delimiter, 1)
            source = Path(left)
            candidate = Path(right)
            return f"{source.stem} -> {candidate.stem}", source, candidate
    raise argparse.ArgumentTypeError("pairs must use SOURCE=CANDIDATE")


def load_pairs(args: argparse.Namespace) -> list[tuple[str, Path, Path]]:
    pairs: list[tuple[str, Path, Path]] = []
    for pair_value in args.pair or []:
        pairs.append(parse_pair(pair_value))
    if args.pairs_file:
        data = json.loads(Path(args.pairs_file).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise SystemExit("--pairs-file must contain a JSON list")
        for item in data:
            if not isinstance(item, dict):
                raise SystemExit("--pairs-file entries must be objects")
            source = Path(item["source"])
            candidate = Path(item["candidate"])
            name = item.get("name") or f"{source.stem} -> {candidate.stem}"
            pairs.append((name, source, candidate))
    if not pairs:
        raise SystemExit("Provide at least one --pair SOURCE=CANDIDATE or --pairs-file.")
    return pairs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pair", action="append", help="SVG pair as SOURCE=CANDIDATE. Repeat for multiple pairs.")
    parser.add_argument("--pairs-file", help="JSON file with objects containing source, candidate, and optional name.")
    parser.add_argument("--report", help="Write a JSON report to this path.")
    parser.add_argument("--font-tolerance", type=float, default=0.5, help="Allowed px difference when matching font-size bins.")
    parser.add_argument("--stroke-tolerance", type=float, default=0.25, help="Allowed px difference when matching stroke-width bins.")
    parser.add_argument("--min-color-jaccard", type=float, default=0.82)
    parser.add_argument("--min-font-jaccard", type=float, default=0.58)
    parser.add_argument("--min-stroke-jaccard", type=float, default=0.68)
    parser.add_argument("--max-count-ratio-delta", type=float, default=0.55)
    parser.add_argument("--warnings-fail", action="store_true", help="Treat structural warnings as failures.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pairs = load_pairs(args)
    results = []
    any_failure = False

    for name, source_path, candidate_path in pairs:
        if not source_path.exists():
            raise SystemExit(f"Source SVG does not exist: {source_path}")
        if not candidate_path.exists():
            raise SystemExit(f"Candidate SVG does not exist: {candidate_path}")
        source = build_signature(source_path)
        candidate = build_signature(candidate_path)
        result = compare_pair(
            name,
            source,
            candidate,
            font_tolerance=args.font_tolerance,
            stroke_tolerance=args.stroke_tolerance,
            min_color_jaccard=args.min_color_jaccard,
            min_font_jaccard=args.min_font_jaccard,
            min_stroke_jaccard=args.min_stroke_jaccard,
            max_count_ratio_delta=args.max_count_ratio_delta,
        )
        results.append(result)
        pair_failed = bool(result["errors"]) or (args.warnings_fail and bool(result["warnings"]))
        any_failure = any_failure or pair_failed

        status = "FAIL" if pair_failed else "PASS"
        print(f"[{status}] {name}")
        metrics = result["metrics"]
        print(
            "  style: "
            f"colors={metrics['colorJaccard']:.3f}, "
            f"fontSizes={metrics['fontSizeJaccard']:.3f}, "
            f"strokeWidths={metrics['strokeWidthJaccard']:.3f}, "
            f"opacities={metrics['opacityJaccard']:.3f}"
        )
        for error in result["errors"]:
            print(f"  ERROR: {error}")
        for warning in result["warnings"]:
            print(f"  WARN: {warning}")

    report = {
        "ok": not any_failure,
        "pairCount": len(results),
        "results": results,
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Report: {report_path.resolve()}")

    if any_failure:
        failed = sum(1 for result in results if result["errors"] or (args.warnings_fail and result["warnings"]))
        print(f"[ERROR] {failed}/{len(results)} SVG pair(s) failed style-signature comparison.")
        return 1
    print(f"[OK] {len(results)} SVG pair(s) passed style-signature comparison.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)

DRAWABLE_TAGS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text"}
PATHLIKE_TAGS = {"path", "line", "polyline", "polygon"}
SKIP_TAGS = {
    "defs",
    "clipPath",
    "mask",
    "pattern",
    "linearGradient",
    "radialGradient",
    "filter",
    "style",
    "script",
    "title",
    "desc",
}

CHART_TYPES = {
    "bar",
    "boxplot",
    "candlestick",
    "chord",
    "custom",
    "effect-scatter",
    "effectScatter",
    "funnel",
    "gauge",
    "graph",
    "heatmap",
    "line",
    "lines",
    "map",
    "parallel",
    "pictorial-bar",
    "pictorialBar",
    "pie",
    "radar",
    "sankey",
    "scatter",
    "sunburst",
    "theme-river",
    "themeRiver",
    "tree",
    "treemap",
}

DRAW_PROFILES = {"line", "lines", "parallel", "tree"}
POP_PROFILES = {"scatter", "effectScatter", "effect-scatter", "graph"}
SCALE_Y_PROFILES = {"bar", "boxplot", "candlestick", "custom", "funnel", "heatmap", "pictorialBar", "pictorial-bar", "treemap"}
RADIAL_PROFILES = {"chord", "gauge", "pie", "radar", "sunburst", "themeRiver", "theme-river", "map", "sankey"}


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def qname(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.replace("_", "-").replace(" ", "-").lower()).strip("-")


def append_class(element: ET.Element, class_name: str) -> None:
    existing = element.attrib.get("class", "").strip()
    classes = [part for part in existing.split() if part]
    for part in class_name.split():
        if part not in classes:
            classes.append(part)
    element.attrib["class"] = " ".join(classes)


def append_style(element: ET.Element, declaration: str) -> None:
    existing = element.attrib.get("style", "").strip()
    if existing and not existing.endswith(";"):
        existing += ";"
    element.attrib["style"] = f"{existing} {declaration}".strip()


def role_for(chart_type: str, tag: str, element: ET.Element) -> str:
    if tag == "text":
        return "label"
    if "transform" in element.attrib:
        return "fade"
    if chart_type in DRAW_PROFILES and tag in PATHLIKE_TAGS:
        return "draw"
    if chart_type in POP_PROFILES:
        return "draw" if tag in {"line", "polyline"} else "pop"
    if chart_type in SCALE_Y_PROFILES:
        return "scale-y"
    if chart_type in RADIAL_PROFILES:
        return "draw" if chart_type == "radar" and tag in {"line", "polyline", "polygon"} else "fade"
    stroke = element.attrib.get("stroke", "")
    if tag in PATHLIKE_TAGS and stroke and stroke.lower() != "none":
        return "draw"
    return "fade"


def decorate(
    element: ET.Element,
    chart_type: str,
    order: int,
    stagger_ms: int,
    max_delay_ms: int,
    in_skip: bool = False,
) -> int:
    tag = local_name(element.tag)
    should_skip = in_skip or tag in SKIP_TAGS

    if not should_skip and tag in DRAWABLE_TAGS:
        role = role_for(chart_type, tag, element)
        append_class(element, f"easv-mark easv-{role}")
        delay = min(order * stagger_ms, max_delay_ms)
        element.attrib["data-easv-order"] = str(order)
        append_style(element, f"--easv-delay: {delay}ms;")
        if role == "draw" and tag in PATHLIKE_TAGS and "pathLength" not in element.attrib:
            element.attrib["pathLength"] = "1"
        order += 1

    for child in list(element):
        order = decorate(child, chart_type, order, stagger_ms, max_delay_ms, should_skip)
    return order


def animation_style(duration_ms: int) -> str:
    return f"""
.echarts-animated-svg .easv-mark {{
  transform-box: fill-box;
  transform-origin: center;
}}
.echarts-animated-svg.easv-playing .easv-fade,
.echarts-animated-svg.easv-playing .easv-label {{
  opacity: 0;
  animation: easv-fade {duration_ms}ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}}
.echarts-animated-svg.easv-playing .easv-pop {{
  opacity: 0;
  transform: scale(.35);
  animation: easv-pop {duration_ms}ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}}
.echarts-animated-svg.easv-playing .easv-scale-y {{
  opacity: 0;
  transform: scaleY(.04);
  transform-origin: center bottom;
  animation: easv-scale-y {duration_ms}ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}}
.echarts-animated-svg.easv-playing .easv-draw {{
  opacity: 1;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: easv-draw {duration_ms}ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}}
@keyframes easv-fade {{ to {{ opacity: 1; }} }}
@keyframes easv-pop {{ to {{ opacity: 1; transform: scale(1); }} }}
@keyframes easv-scale-y {{ to {{ opacity: 1; transform: scaleY(1); }} }}
@keyframes easv-draw {{ to {{ stroke-dashoffset: 0; }} }}
@media (prefers-reduced-motion: reduce) {{
  .echarts-animated-svg.easv-playing .easv-mark {{
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
    stroke-dashoffset: 0 !important;
  }}
}}
""".strip()


def animate_svg(svg_input: Path, output: Path, chart_type: str, duration_ms: int, stagger_ms: int, max_delay_ms: int) -> None:
    try:
        tree = ET.parse(svg_input)
    except ET.ParseError as error:
        raise SystemExit(f"Failed to parse SVG: {error}") from error

    root = tree.getroot()
    if local_name(root.tag) != "svg":
        raise SystemExit("Input file root element is not <svg>.")

    normalized_type = chart_type
    append_class(root, f"echarts-animated-svg easv-profile-{slug(normalized_type)} easv-playing")
    root.attrib["data-echarts-chart-type"] = normalized_type
    root.attrib["data-easv-replay"] = "remove-and-readd-easv-playing"

    style = ET.Element(qname("style"))
    style.text = animation_style(duration_ms)
    root.insert(0, style)

    decorate(root, normalized_type, 0, stagger_ms, max_delay_ms)
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Animate an already-rendered Apache ECharts SVG.")
    parser.add_argument("svg_input", type=Path, help="Path to a static SVG produced by ECharts SVGRenderer or SSR.")
    parser.add_argument("-o", "--output", type=Path, help="Animated SVG output path.")
    parser.add_argument("--chart-type", required=True, choices=sorted(CHART_TYPES), help="ECharts chart type profile to apply.")
    parser.add_argument("--duration-ms", type=int, default=760, help="Animation duration for each mark.")
    parser.add_argument("--stagger-ms", type=int, default=36, help="Delay between decorated marks.")
    parser.add_argument("--max-delay-ms", type=int, default=1100, help="Maximum per-mark delay.")
    args = parser.parse_args()

    output = args.output or args.svg_input.with_name(f"{args.svg_input.stem}.animated.svg")
    animate_svg(args.svg_input, output, args.chart_type, args.duration_ms, args.stagger_ms, args.max_delay_ms)
    print(f"Wrote animated ECharts SVG: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

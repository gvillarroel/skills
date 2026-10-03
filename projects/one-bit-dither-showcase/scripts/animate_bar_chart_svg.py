#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Add a deterministic staged baseline reveal to a settled D3 bar-chart SVG."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG = f"{{{SVG_NAMESPACE}}}"
ET.register_namespace("", SVG_NAMESPACE)


def has_class(element: ET.Element, token: str) -> bool:
    return token in element.get("class", "").split()


def compact_number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def add_animation(element: ET.Element, attribute: str, values: Sequence[float], key_times: Sequence[float], duration: float) -> None:
    ET.SubElement(
        element,
        f"{SVG}animate",
        {
            "attributeName": attribute,
            "values": ";".join(compact_number(value) for value in values),
            "keyTimes": ";".join(compact_number(value) for value in key_times),
            "dur": f"{duration:g}s",
            "repeatCount": "indefinite",
            "calcMode": "linear",
        },
    )


def animate(source: Path, output: Path, duration: float) -> None:
    try:
        tree = ET.parse(source)
    except (OSError, ET.ParseError) as error:
        raise SystemExit(f"Cannot parse source SVG: {error}") from error
    root = tree.getroot()
    if root.tag != f"{SVG}svg":
        raise SystemExit("Source root must be SVG")

    bars = sorted(
        (element for element in root.iter(f"{SVG}rect") if has_class(element, "throughput-bar")),
        key=lambda element: float(element.get("x", "0")),
    )
    if len(bars) < 2:
        raise SystemExit("Expected at least two .throughput-bar rectangles")

    baselines = [float(bar.get("y", "0")) + float(bar.get("height", "0")) for bar in bars]
    baseline = sum(baselines) / len(baselines)
    if any(abs(item - baseline) > 0.01 for item in baselines):
        raise SystemExit("All bars must share one quantitative baseline")

    parents = {child: parent for parent in root.iter() for child in parent}
    for index, bar in enumerate(bars):
        final_y = float(bar.get("y", "0"))
        final_height = float(bar.get("height", "0"))
        start = 0.025 + index * 0.085
        end = start + 0.31
        key_times = (0.0, start, end, 1.0)
        add_animation(bar, "y", (baseline, baseline, final_y, final_y), key_times, duration)
        add_animation(bar, "height", (0.0, 0.0, final_height, final_height), key_times, duration)

        parent = parents.get(bar)
        if parent is None:
            continue
        labels = [child for child in parent if child.tag == f"{SVG}text"]
        if len(labels) >= 2:
            value_label = labels[-1]
            add_animation(value_label, "opacity", (0.0, 0.0, 1.0, 1.0), key_times, duration)

    # Insert a crisp shared baseline before the bar groups.
    plot_group = parents.get(parents.get(bars[0])) if parents.get(bars[0]) is not None else None
    baseline_line = ET.Element(
        f"{SVG}line",
        {
            "class": "quantitative-baseline",
            "x1": "58",
            "x2": "902",
            "y1": compact_number(baseline),
            "y2": compact_number(baseline),
            "stroke": "#333e48",
            "stroke-width": "2",
        },
    )
    if plot_group is not None:
        plot_group.insert(0, baseline_line)
    else:
        root.append(baseline_line)

    style = ET.Element(f"{SVG}style")
    style.text = (
        "text{font-family:Arial,Helvetica,sans-serif;fill:#333e48;font-size:18px}"
        ".contract-title{font-size:20px;font-weight:700}"
        ".throughput-bar{shape-rendering:geometricPrecision}"
        ".quantitative-baseline{shape-rendering:crispEdges}"
    )
    insert_index = 2 if len(root) >= 2 else len(root)
    root.insert(insert_index, style)
    root.set("data-animation-duration", f"{duration:g}s")
    root.set("data-animation-pattern", "staged-baseline-reveal")
    root.set("data-animation-source", root.get("data-pattern-id", "d3-bar"))

    description = next((child for child in root if child.tag == f"{SVG}desc"), None)
    if description is not None and description.text:
        description.text += " Bars grow upward from the shared baseline in a staggered loop."

    ET.indent(tree, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output, encoding="utf-8", xml_declaration=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration", type=float, default=3.0)
    args = parser.parse_args(argv)
    if not args.source.is_file():
        parser.error(f"source SVG not found: {args.source}")
    if args.source.suffix.lower() != ".svg" or args.output.suffix.lower() != ".svg":
        parser.error("source and output must end in .svg")
    if not 1.0 <= args.duration <= 30:
        parser.error("--duration must be between 1 and 30 seconds")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    animate(args.source, args.output, args.duration)
    print(f"Wrote {args.output.resolve()} with a {args.duration:g}s staged bar reveal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

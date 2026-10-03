#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Add a deterministic looping SMIL motion layer to the D3 Signal Compass SVG."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Sequence


SVG_NAMESPACE = "http://www.w3.org/2000/svg"
SVG = f"{{{SVG_NAMESPACE}}}"
ET.register_namespace("", SVG_NAMESPACE)


def find_by_class(root: ET.Element, token: str) -> ET.Element:
    for element in root.iter():
        if token in element.get("class", "").split():
            return element
    raise SystemExit(f"Source SVG is missing .{token}")


def direct_parent(root: ET.Element, child: ET.Element) -> ET.Element:
    for candidate in root.iter():
        if child in list(candidate):
            return candidate
    raise SystemExit("Cannot locate the logo mark parent")


def animate(source: Path, output: Path, duration: float) -> None:
    try:
        tree = ET.parse(source)
    except (OSError, ET.ParseError) as error:
        raise SystemExit(f"Cannot parse source SVG: {error}") from error
    root = tree.getroot()
    if root.tag != f"{SVG}svg":
        raise SystemExit("Source root must be SVG")

    mark = find_by_class(root, "logo-mark")
    parent = direct_parent(root, mark)
    index = list(parent).index(mark)
    parent.remove(mark)

    center_x = 268.8
    center_y = 248.4
    wrapper = ET.Element(f"{SVG}g", {"class": "compass-motion", "data-animation": "continuous-rotation"})
    ET.SubElement(
        wrapper,
        f"{SVG}animateTransform",
        {
            "attributeName": "transform",
            "attributeType": "XML",
            "type": "rotate",
            "from": f"0 {center_x} {center_y}",
            "to": f"360 {center_x} {center_y}",
            "dur": f"{duration:g}s",
            "repeatCount": "indefinite",
        },
    )
    wrapper.append(mark)
    # An asymmetric bearing tick keeps motion readable after conversion to two tones.
    ET.SubElement(
        wrapper,
        f"{SVG}circle",
        {
            "class": "bearing-tick",
            "cx": str(center_x),
            "cy": "110",
            "r": "7",
            "fill": "#333e48",
            "stroke": "#ffffff",
            "stroke-width": "3",
        },
    )
    parent.insert(index, wrapper)

    root.set("data-animation-duration", f"{duration:g}s")
    root.set("data-animation-source", "d3-signal-compass")
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
    if not 0.5 <= args.duration <= 30:
        parser.error("--duration must be between 0.5 and 30 seconds")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    animate(args.source, args.output, args.duration)
    print(f"Wrote {args.output.resolve()} with a {args.duration:g}s looping SMIL animation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

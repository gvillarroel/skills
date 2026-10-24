#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Repair XY 0.0.8's duplicate fill attribute on native line-only point glyphs.

Only a path carrying adjacent fill="none" fill="#rrggbb" and a matching
stroke="#rrggbb" is repaired. Every result must parse as SVG XML; unrelated
malformed XML raises instead of being silently rewritten.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

_PATH = re.compile(r"<path\b(?:\"[^\"]*\"|'[^']*'|[^'\">])*>", re.DOTALL)
_ATTRIBUTE = re.compile(r"(?P<name>[\w:.-]+)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)", re.DOTALL)
_HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")


def _parse_svg(text: str) -> None:
    root = ET.fromstring(text)
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise ValueError("Expected an SVG root element")


def repair_duplicate_line_symbol_fill(svg: str) -> tuple[str, int]:
    """Return SVG text and repaired path count, preserving every other byte.

    A valid SVG returns unchanged. The repair retains fill="none", the original
    path data, and the original stroke; it removes only the redundant matching
    hex fill attribute. XML unrelated to this exact defect fails closed.
    """
    if not isinstance(svg, str):
        raise TypeError("SVG input must be text")
    try:
        _parse_svg(svg)
        return svg, 0
    except ET.ParseError:
        pass
    count = 0

    def repair(match: re.Match) -> str:
        nonlocal count
        tag = match.group()
        attributes = list(_ATTRIBUTE.finditer(tag))
        fills = [attr for attr in attributes if attr.group("name") == "fill"]
        strokes = [attr for attr in attributes if attr.group("name") == "stroke"]
        if len(fills) != 2 or len(strokes) != 1:
            return tag
        first, second = fills
        paint = second.group("value")
        if (first.group("value") != "none" or not _HEX.fullmatch(paint)
                or strokes[0].group("value").lower() != paint.lower()
                or tag[first.end():second.start()].strip()):
            return tag
        count += 1
        return tag[:second.start()] + tag[second.end():]

    repaired = _PATH.sub(repair, svg)
    try:
        _parse_svg(repaired)
    except ET.ParseError as error:
        raise ValueError("SVG contains malformed XML outside the supported line-symbol fill defect") from error
    return repaired, count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source, output = args.input.resolve(), args.output.resolve()
    bundle = Path(__file__).resolve().parent.parent
    if source.is_relative_to(bundle) or output.is_relative_to(bundle):
        parser.error("Input and output artifacts must be outside the read-only skill bundle")
    if source == output:
        parser.error("Use a different output path to preserve the original SVG evidence")
    repaired, count = repair_duplicate_line_symbol_fill(source.read_text(encoding="utf-8"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(repaired, encoding="utf-8")
    print(json.dumps({"input": str(source), "output": str(output), "repairedPaths": count, "validSvgXml": True}))


if __name__ == "__main__":
    main()

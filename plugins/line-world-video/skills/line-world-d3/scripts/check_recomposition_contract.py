#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Check stable IDs and basic mark counts in a recomposed SVG HTML artifact."""

from __future__ import annotations

import argparse
import json
from html.parser import HTMLParser
from pathlib import Path


class SvgContractParser(HTMLParser):
    def __init__(self, expected_id: str) -> None:
        super().__init__(convert_charrefs=True)
        self.expected_id = expected_id
        self.svg_attributes: dict[str, str] | None = None
        self.depth = 0
        self.node_count = 0
        self.link_count = 0
        self.mark_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        if tag == "svg" and attributes.get("id") == self.expected_id:
            self.svg_attributes = attributes
            self.depth = 1
            return
        if self.depth < 1:
            return
        self.depth += 1
        classes = set(attributes.get("class", "").split())
        if "node" in classes:
            self.node_count += 1
        if "link" in classes:
            self.link_count += 1
        if tag in {"circle", "ellipse", "line", "path", "polygon", "polyline", "rect", "text"}:
            self.mark_count += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.depth > 1:
            self.depth -= 1

    def handle_endtag(self, tag: str) -> None:
        if self.depth < 1:
            return
        self.depth -= 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Standalone HTML artifact to check.")
    parser.add_argument("--source-id", required=True, help="Source pattern ID without the d3- namespace.")
    parser.add_argument("--composition-id", required=True, help="Target composition ID.")
    parser.add_argument("--base-pattern-id", help="Expected base pattern ID. Defaults to d3-<source-id>.")
    parser.add_argument("--min-nodes", type=int, default=0, help="Minimum elements carrying the node class.")
    parser.add_argument("--min-links", type=int, default=0, help="Minimum elements carrying the link class.")
    parser.add_argument("--min-marks", type=int, default=1, help="Minimum visible SVG mark elements.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    expected_variant_id = f"d3-composition-{args.composition_id}-{args.source_id}"
    expected_base_id = args.base_pattern_id or f"d3-{args.source_id}"
    findings: list[str] = []

    if not source.is_file():
        findings.append(f"Source file does not exist: {source}")
        parser = SvgContractParser(expected_variant_id)
    else:
        parser = SvgContractParser(expected_variant_id)
        parser.feed(source.read_text(encoding="utf-8"))

    attributes = parser.svg_attributes or {}
    expected_attributes = {
        "id": expected_variant_id,
        "data-composition-id": args.composition_id,
        "data-example-id": args.source_id,
        "data-pattern-id": expected_base_id,
        "data-composition-pattern-id": expected_variant_id,
    }
    if not parser.svg_attributes:
        findings.append(f"Missing SVG with id {expected_variant_id}.")
    for name, expected in expected_attributes.items():
        if attributes.get(name) != expected:
            findings.append(f"Expected {name}={expected!r}, found {attributes.get(name, '')!r}.")
    if parser.node_count < args.min_nodes:
        findings.append(f"Expected at least {args.min_nodes} node-class elements, found {parser.node_count}.")
    if parser.link_count < args.min_links:
        findings.append(f"Expected at least {args.min_links} link-class elements, found {parser.link_count}.")
    if parser.mark_count < args.min_marks:
        findings.append(f"Expected at least {args.min_marks} SVG marks, found {parser.mark_count}.")

    report = {
        "ok": not findings,
        "source": str(source),
        "variantId": expected_variant_id,
        "basePatternId": expected_base_id,
        "nodes": parser.node_count,
        "links": parser.link_count,
        "marks": parser.mark_count,
        "findings": findings,
    }
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

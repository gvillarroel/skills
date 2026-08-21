#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check literal structure and visible text in a rendered D3 HTML/SVG artifact."""

from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys


class SurfaceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: Counter[str] = Counter()
        self.classes: Counter[str] = Counter()
        self.ids: set[str] = set()
        self.attributes: list[dict[str, str]] = []
        self.text_parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.casefold()
        if lowered in {"script", "style", "template"}:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        values = {name.casefold(): value or "" for name, value in attrs}
        self.tags[lowered] += 1
        self.attributes.append(values)
        if values.get("id"):
            self.ids.add(values["id"])
        for class_name in values.get("class", "").split():
            self.classes[class_name] += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered in {"script", "style", "template"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.text_parts.append(data.strip())

    @property
    def visible_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.text_parts)).strip()


def parse_count_spec(value: str) -> tuple[str, int]:
    name, separator, count_text = value.rpartition(":")
    if not separator:
        return value, 1
    if not name or not count_text.isdigit() or int(count_text) < 1:
        raise argparse.ArgumentTypeError(f"Expected NAME or NAME:MINIMUM, got {value!r}")
    return name, int(count_text)


def parse_attribute(value: str) -> tuple[str, str]:
    name, separator, expected = value.partition("=")
    if not separator or not name:
        raise argparse.ArgumentTypeError(f"Expected NAME=VALUE, got {value!r}")
    return name.casefold(), expected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--require-id", action="append", default=[])
    parser.add_argument("--require-class", action="append", type=parse_count_spec, default=[])
    parser.add_argument("--require-tag", action="append", type=parse_count_spec, default=[])
    parser.add_argument("--require-attribute", action="append", type=parse_attribute, default=[])
    parser.add_argument("--require-text", action="append", default=[])
    parser.add_argument(
        "--ordered-text",
        action="append",
        default=[],
        help="Visible text token; repeat flags in the required reading order.",
    )
    parser.add_argument("--no-require-svg-contract", action="store_true")
    parser.add_argument("--json-report", type=Path)
    return parser.parse_args()


def check(args: argparse.Namespace) -> dict[str, object]:
    findings: list[str] = []
    try:
        source = args.artifact.read_text(encoding="utf-8")
    except OSError as error:
        return {"ok": False, "findings": [f"artifact is missing or unreadable: {error}"]}
    surface = SurfaceParser()
    surface.feed(source)
    surface.close()

    if not args.no_require_svg_contract:
        if surface.tags["svg"] < 1:
            findings.append("missing rendered svg")
        if surface.tags["title"] < 1:
            findings.append("missing rendered title")
        if surface.tags["desc"] < 1:
            findings.append("missing rendered desc")
        if not any(values.get("viewbox", "").strip() for values in surface.attributes):
            findings.append("missing stable SVG viewBox")
    for required_id in args.require_id:
        if required_id not in surface.ids:
            findings.append(f"missing ID: {required_id}")
    for class_name, minimum in args.require_class:
        if surface.classes[class_name] < minimum:
            findings.append(
                f"class {class_name} count {surface.classes[class_name]} is below {minimum}"
            )
    for tag, minimum in args.require_tag:
        observed = surface.tags[tag.casefold()]
        if observed < minimum:
            findings.append(f"tag {tag} count {observed} is below {minimum}")
    for name, expected in args.require_attribute:
        if not any(values.get(name) == expected for values in surface.attributes):
            findings.append(f"missing attribute: {name}={expected}")

    visible = surface.visible_text
    folded = visible.casefold()
    for token in args.require_text:
        if token.casefold() not in folded:
            findings.append(f"missing visible text: {token}")
    cursor = 0
    for token in args.ordered_text:
        folded_token = token.casefold()
        position = folded.find(folded_token, cursor)
        if position < 0:
            findings.append("ordered visible text is missing or out of order")
            break
        cursor = position + len(folded_token)

    return {
        "ok": not findings,
        "findings": findings,
        "artifact": str(args.artifact.resolve()),
        "inventory": {
            "tags": dict(sorted(surface.tags.items())),
            "classes": dict(sorted(surface.classes.items())),
            "ids": sorted(surface.ids),
        },
    }


def main() -> int:
    args = parse_args()
    result = check(args)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(payload, encoding="utf-8", newline="\n")
    print(payload, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

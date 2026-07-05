#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


COLORSET1 = {
    "#9e1b32",
    "#6d1222",
    "#ffccd5",
    "#e8002a",
    "#333e48",
    "#000000",
    "#ffffff",
    "#f7f7f7",
    "#e7e7e7",
    "#cfcfcf",
    "#b5b5b5",
    "#9c9c9c",
    "#828282",
    "#696969",
    "#4f4f4f",
    "#363636",
    "#1c1c1c",
    "#ccd6e3",
}

EDITORIAL_PATTERNS = [
    re.compile(r">\s*checked\s+[^<]+<", re.IGNORECASE),
    re.compile(r"deterministic\s+[-a-z]+\s+(?:draft|scaffold)", re.IGNORECASE),
    re.compile(r"draft\s+visual\s+strategy", re.IGNORECASE),
]

FONT_FAMILY_PATTERN = re.compile(r"font-family\s*:\s*([^;}]+)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit generated standalone HTML for Metro Minimal Tonal Motion basics."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--source-package", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--allow-colorset2",
        action="store_true",
        help="Allow non-colorset1 colors when a project explicitly chose colorset2.",
    )
    parser.add_argument(
        "--require-open-sans",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require the Metro source CSS to use the colorset1 Open Sans font stack.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    html = args.html.read_text(encoding="utf-8")
    colors = sorted({match.group(0).lower() for match in re.finditer(r"#[0-9a-fA-F]{6}", html)})
    forbidden_colors = [color for color in colors if color not in COLORSET1]
    findings: list[dict[str, str]] = []
    if forbidden_colors and not args.allow_colorset2:
        findings.append(
            {
                "code": "non-colorset1-colors",
                "path": args.html.as_posix(),
                "message": ", ".join(forbidden_colors),
            }
        )
    for pattern in EDITORIAL_PATTERNS:
        if pattern.search(html):
            findings.append(
                {
                    "code": "editorial-frame-text",
                    "path": args.html.as_posix(),
                    "message": pattern.pattern,
                }
            )
    font_families = [match.group(1).strip() for match in FONT_FAMILY_PATTERN.finditer(html)]
    if args.require_open_sans:
        if not font_families:
            findings.append(
                {
                    "code": "missing-open-sans-font",
                    "path": args.html.as_posix(),
                    "message": "No CSS font-family declaration was found.",
                }
            )
        elif not any("open sans" in family.lower() for family in font_families):
            findings.append(
                {
                    "code": "wrong-metro-font-stack",
                    "path": args.html.as_posix(),
                    "message": "; ".join(font_families[:4]),
                }
            )
    if args.source_package and args.source_package.exists():
        data = json.loads(args.source_package.read_text(encoding="utf-8"))
        anchors = data.get("strategyAnchors", [])
        if not isinstance(anchors, list) or not anchors:
            findings.append(
                {
                    "code": "missing-visual-anchors",
                    "path": args.source_package.as_posix(),
                    "message": "source package should preserve visual anchors",
                }
            )
    report = {
        "passed": not findings,
        "html": args.html.as_posix(),
        "colors": colors,
        "colorset": "colorset1" if not args.allow_colorset2 else "colorset1-or-colorset2",
        "fontFamilies": font_families,
        "requireOpenSans": args.require_open_sans,
        "findings": findings,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

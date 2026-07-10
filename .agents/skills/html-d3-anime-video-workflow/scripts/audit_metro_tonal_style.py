#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import colorsys
import json
import re
from pathlib import Path

from compile_metro_design_profile import DEFAULT_PROFILE, load_design_profile

EDITORIAL_PATTERNS = [
    re.compile(r">\s*checked\s+[^<]+<", re.IGNORECASE),
    re.compile(r"deterministic\s+[-a-z]+\s+(?:draft|scaffold)", re.IGNORECASE),
    re.compile(r"draft\s+visual\s+strategy", re.IGNORECASE),
]

FONT_FAMILY_PATTERN = re.compile(r"font-family\s*:\s*([^;}]+)", re.IGNORECASE)
HEX_PATTERN = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?\b")
RGB_PATTERN = re.compile(
    r"rgba?\(\s*([0-9.]+%?)\s*[, ]\s*([0-9.]+%?)\s*[, ]\s*([0-9.]+%?)(?:\s*[,/]\s*[0-9.]+%?)?\s*\)",
    re.IGNORECASE,
)
HSL_PATTERN = re.compile(
    r"hsla?\(\s*([0-9.]+)(?:deg)?\s*[, ]\s*([0-9.]+)%\s*[, ]\s*([0-9.]+)%(?:\s*[,/]\s*[0-9.]+%?)?\s*\)",
    re.IGNORECASE,
)


def channel_value(raw: str) -> int:
    if raw.endswith("%"):
        return round(max(0.0, min(100.0, float(raw[:-1]))) * 2.55)
    return round(max(0.0, min(255.0, float(raw))))


def extract_colors(text: str) -> list[str]:
    colors: set[str] = set()
    for match in HEX_PATTERN.finditer(text):
        value = match.group(0).lower()
        if len(value) == 4:
            value = "#" + "".join(character * 2 for character in value[1:])
        colors.add(value)
    for match in RGB_PATTERN.finditer(text):
        channels = [channel_value(match.group(index)) for index in range(1, 4)]
        colors.add("#" + "".join(f"{channel:02x}" for channel in channels))
    for match in HSL_PATTERN.finditer(text):
        hue = float(match.group(1)) % 360 / 360
        saturation = max(0.0, min(100.0, float(match.group(2)))) / 100
        lightness = max(0.0, min(100.0, float(match.group(3)))) / 100
        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
        colors.add(f"#{round(red * 255):02x}{round(green * 255):02x}{round(blue * 255):02x}")
    return sorted(colors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit generated standalone HTML for Metro Minimal Tonal Motion basics."
    )
    parser.add_argument("--html", required=True, type=Path)
    parser.add_argument("--source-package", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--design-profile",
        type=Path,
        default=DEFAULT_PROFILE,
        help="Compiled Metro design profile. Defaults to the bundled profile generated from style.md and the colorsets.",
    )
    parser.add_argument(
        "--allow-colorset2",
        action="store_true",
        help="Allow only colors declared by colorset2 when a project explicitly needs them.",
    )
    parser.add_argument(
        "--colorset2-reason",
        default="",
        help="Required semantic justification when --allow-colorset2 is used.",
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
    profile = load_design_profile(args.design_profile)
    colorset1 = set(profile["colorsets"]["colorset1"]["colors"])
    colorset2 = set(profile["colorsets"]["colorset2"]["colors"])
    allowed_colors = colorset1 | colorset2 if args.allow_colorset2 else colorset1
    html = args.html.read_text(encoding="utf-8")
    colors = extract_colors(html)
    forbidden_colors = [color for color in colors if color not in allowed_colors]
    findings: list[dict[str, str]] = []
    if args.allow_colorset2 and not args.colorset2_reason.strip():
        findings.append(
            {
                "code": "missing-colorset2-reason",
                "path": args.html.as_posix(),
                "message": "--allow-colorset2 requires --colorset2-reason with a semantic need.",
            }
        )
    if forbidden_colors:
        findings.append(
            {
                "code": "non-selected-colorset-colors",
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
        "colorset2Reason": args.colorset2_reason.strip() or None,
        "designProfile": {
            "path": args.design_profile.as_posix(),
            "profileId": profile.get("profileId"),
            "profileVersion": profile.get("profileVersion"),
            "profileSha256": profile.get("profileSha256"),
            "sourceDigests": {
                key: value.get("sha256")
                for key, value in profile.get("sources", {}).items()
                if isinstance(value, dict)
            },
        },
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

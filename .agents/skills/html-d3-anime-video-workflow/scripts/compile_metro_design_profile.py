#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILE = SCRIPT_DIR.parent / "references" / "metro-design-profile.json"
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")
VALUE_LINE = re.compile(r"^\s*value\s*:\s*[\"']?(.+?)[\"']?\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compile Metro style and colorset source files into one deterministic runtime profile."
    )
    parser.add_argument("--style", required=True, type=Path)
    parser.add_argument("--colorset1", required=True, type=Path)
    parser.add_argument("--colorset2", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_PROFILE)
    return parser.parse_args()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ordered_colors(text: str) -> list[str]:
    seen: set[str] = set()
    colors: list[str] = []
    for match in HEX_COLOR.finditer(text):
        color = match.group(0).lower()
        if color not in seen:
            seen.add(color)
            colors.append(color)
    return colors


def primary_font(text: str) -> str | None:
    lines = text.splitlines()
    in_typography = False
    in_primary = False
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if indent == 0:
            in_typography = stripped == "typography:"
            in_primary = False
            continue
        if not in_typography:
            continue
        if indent == 2:
            in_primary = stripped == "primary:"
            continue
        if in_primary:
            match = VALUE_LINE.match(line)
            if match:
                value = match.group(1).strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
                    value = value[1:-1]
                return value
    return None


def style_rules(text: str) -> dict[str, bool]:
    lower = text.lower()
    return {
        "megacanvas": "megacanvas" in lower or "large navigable visual object" in lower,
        "continuousComposition": "continuous" in lower and "disconnected slides" in lower,
        "noReservedEditorialSpace": (
            "do not reserve space for titles or subtitles" in lower
            or "no space should be reserved for titles" in lower
        ),
        "hardEdges": "no rounded borders" in lower,
        "masonry": "masonry" in lower,
        "cameraExploration": "zoom in" in lower and "zoom out" in lower and "pan" in lower,
        "flatGeometry": "flat shapes" in lower or "remain flat" in lower,
        "functionalTextOnly": "functional text" in lower,
    }


def source_record(path: Path, text: str) -> dict[str, str]:
    return {"name": path.name, "sha256": sha256_text(text)}


def compile_profile(style_path: Path, colorset1_path: Path, colorset2_path: Path | None) -> dict[str, Any]:
    style_text = style_path.read_text(encoding="utf-8")
    colorset1_text = colorset1_path.read_text(encoding="utf-8")
    colorset2_text = colorset2_path.read_text(encoding="utf-8") if colorset2_path else ""
    rules = style_rules(style_text)
    colors1 = ordered_colors(colorset1_text)
    colors2 = ordered_colors(colorset2_text)
    font = primary_font(colorset1_text)
    findings: list[dict[str, str]] = []

    for rule, present in rules.items():
        if not present:
            findings.append({"code": "missing-style-rule", "rule": rule})
    if not font or "open sans" not in font.lower():
        findings.append({"code": "missing-open-sans-source", "message": str(font or "")})
    if len(colors1) < 12:
        findings.append({"code": "colorset1-too-small", "message": str(len(colors1))})
    for required in ("#9e1b32", "#6d1222", "#e8002a", "#ffccd5", "#000000", "#ffffff"):
        if required not in colors1:
            findings.append({"code": "colorset1-missing-required-color", "message": required})
    if colorset2_path and not colors2:
        findings.append({"code": "colorset2-empty", "message": colorset2_path.name})

    sources: dict[str, Any] = {
        "style": source_record(style_path, style_text),
        "colorset1": source_record(colorset1_path, colorset1_text),
        "colorset2": source_record(colorset2_path, colorset2_text) if colorset2_path else None,
    }
    profile = {
        "schemaVersion": 1,
        "profileId": "metro-minimal-tonal-motion-colorset1",
        "profileVersion": "2026-07-09.1",
        "passed": not findings,
        "sources": sources,
        "style": {
            "name": "Metro Minimal Tonal Motion",
            "rules": rules,
        },
        "typography": {"primary": font},
        "geometry": {
            "cornerRadiusPx": 0,
            "gridPx": 4,
            "internalPaddingPx": 0,
            "hardLineCapsAndJoins": True,
            "sharedEdges": True,
            "externalGuttersOnly": True,
        },
        "colorsets": {
            "colorset1": {"colors": colors1},
            "colorset2": {"colors": colors2},
        },
        "policy": {
            "defaultColorset": "colorset1",
            "colorset2RequiresSemanticNeed": True,
            "colorset2RequiresRecordedReason": True,
            "redRole": "state, emphasis, failure, selection, alert path, or primary flow",
            "hierarchyBeforeHue": "Use distinct grayscale levels before adding hue.",
        },
        "findings": findings,
    }
    canonical = json.dumps(profile, sort_keys=True, separators=(",", ":"))
    profile["profileSha256"] = sha256_text(canonical)
    return profile


def load_design_profile(path: Path = DEFAULT_PROFILE) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Design profile root must be an object: {path}")
    if data.get("passed") is not True:
        raise ValueError(f"Design profile is not passing: {path}")
    return data


def profile_prompt_contract(profile: dict[str, Any]) -> str:
    colors = profile["colorsets"]["colorset1"]["colors"]
    geometry = profile["geometry"]
    source_bits = [
        f"{name} sha256 `{entry['sha256']}`"
        for name, entry in profile.get("sources", {}).items()
        if isinstance(entry, dict) and entry.get("sha256")
    ]
    palette = ", ".join(f"`{color}`" for color in colors)
    return f"""Style contract (compiled profile `{profile['profileId']}` version `{profile['profileVersion']}`, sha256 `{profile['profileSha256']}`):

- Source evidence: {'; '.join(source_bits)}.
- This is a design-repair run: prior output was rejected as not following the design.
- Use Metro Minimal Tonal Motion as one continuous navigable megacanvas, not isolated slides.
- Use a masonry wall or masonry-like modular construction with varied module sizes, shared edges, and visible construction over time.
- Do not reserve title, subtitle, caption, date, draft-label, or editorial-text bands.
- Use only functional text attached to data-bearing visual objects.
- Allowed colorset1 values: {palette}.
- Use colorset2 only for a necessary semantic distinction and record the reason in production notes.
- Use {geometry['cornerRadiusPx']} px corner radius, hard line caps and joins, {geometry['gridPx']} px grid alignment, shared edges, and external gutters.
- Use {geometry['internalPaddingPx']} px internal box padding. The rectangle edge is the content boundary.
- Build hierarchy with distinct grayscale levels before hue. Red carries {profile['policy']['redRole']}.
- With text hidden, marks, motion, zones, and gray hierarchy must still communicate the mechanism.
"""


def main() -> int:
    args = parse_args()
    try:
        profile = compile_profile(args.style, args.colorset1, args.colorset2)
    except (OSError, UnicodeError) as exc:
        print(f"compile_metro_design_profile.py: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": args.output.as_posix(), "passed": profile["passed"], "profileSha256": profile["profileSha256"]}, indent=2))
    return 0 if profile["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

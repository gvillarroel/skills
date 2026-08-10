#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate static HTML, SVG, or CSS paint against the unified D3 colorsets."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
HEX_RE = re.compile(r"(?<![A-Za-z0-9_-])#[0-9A-Fa-f]{3,8}\b")
FUNCTIONAL_COLOR_RE = re.compile(
    r"(?i)(?<![A-Za-z0-9_-])(?:rgb|rgba|hsl|hsla|lab|lch|oklab|oklch|color)\s*\("
)
PAINT_VALUE_RE = re.compile(
    r"(?i)(?:\b(?:fill|stroke|color|stop-color|flood-color|lighting-color)\b\s*(?:=|:)\s*[\"']?)"
    r"([A-Za-z][A-Za-z-]*)(?![A-Za-z0-9_-])"
)
METADATA_RE = re.compile(
    r"(?i)(?:data-(?:colorset|color-set)\s*=\s*[\"'](colorset[12])[\"']|"
    r"[\"']colorset[\"']\s*:\s*[\"'](colorset[12])[\"'])"
)
ALLOWED_NON_COLOR_VALUES = {
    "none",
    "currentcolor",
    "inherit",
    "initial",
    "unset",
    "transparent",
    "url",
    "var",
    "rgb",
    "rgba",
    "hsl",
    "hsla",
    "lab",
    "lch",
    "oklab",
    "oklch",
    "color",
    "context-fill",
    "context-stroke",
}


class StaticMarkupExtractor(HTMLParser):
    """Collect visible markup and CSS while excluding JavaScript/template bodies."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self._ignored_depth = 0
        self.ignored_script_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in {"script", "template"}:
            self._ignored_depth += 1
            if lowered == "script":
                self.ignored_script_count += 1
            return
        if self._ignored_depth:
            return
        rendered_attrs = " ".join(
            f'{name}="{value or ""}"' for name, value in attrs
        )
        self.parts.append(f"<{tag} {rendered_attrs}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"script", "template"} and self._ignored_depth:
            self._ignored_depth -= 1
            return
        if not self._ignored_depth:
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)

    @property
    def text(self) -> str:
        return "\n".join(self.parts)


def load_colorsets(path: Path = PALETTE_PATH) -> dict[str, set[str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    colorsets = payload.get("colorsets")
    if not isinstance(colorsets, dict):
        raise ValueError(f"Missing colorsets object in {path}")
    result: dict[str, set[str]] = {}
    for colorset_id in ("colorset1", "colorset2"):
        record = colorsets.get(colorset_id)
        allowed = record.get("allowed") if isinstance(record, dict) else None
        if not isinstance(allowed, list) or not allowed:
            raise ValueError(f"Missing {colorset_id}.allowed in {path}")
        normalized = {str(value) for value in allowed}
        if any(not re.fullmatch(r"#[0-9a-f]{6}", value) for value in normalized):
            raise ValueError(f"{colorset_id} contains a non-canonical token in {path}")
        result[colorset_id] = normalized
    if not result["colorset1"].issubset(result["colorset2"]):
        raise ValueError("colorset2 must contain every colorset1 token")
    return result


def static_surface(path: Path, source: str) -> tuple[str, int]:
    if path.suffix.lower() not in {".html", ".htm"}:
        return source, 0
    parser = StaticMarkupExtractor()
    parser.feed(source)
    parser.close()
    return parser.text, parser.ignored_script_count


def validate_artifact(
    path: Path,
    *,
    colorset: str,
    require_extended: bool = False,
    require_metadata: bool = True,
    palette_path: Path = PALETTE_PATH,
) -> dict[str, Any]:
    resolved = path.resolve()
    source = resolved.read_text(encoding="utf-8")
    visible_source, ignored_script_count = static_surface(resolved, source)
    colorsets = load_colorsets(palette_path)
    allowed = colorsets[colorset]
    extended = colorsets["colorset2"] - colorsets["colorset1"]

    raw_colors = sorted(set(HEX_RE.findall(visible_source)))
    canonical_colors = sorted({value.lower() for value in raw_colors if len(value) == 7})
    malformed_colors = sorted(
        value for value in raw_colors if len(value) != 7 or value != value.lower()
    )
    forbidden_colors = sorted(value for value in canonical_colors if value not in allowed)
    functional_syntax = sorted(set(match.group(0) for match in FUNCTIONAL_COLOR_RE.finditer(visible_source)))
    named_paints = sorted(
        {
            match.group(1)
            for match in PAINT_VALUE_RE.finditer(visible_source)
            if match.group(1).lower() not in ALLOWED_NON_COLOR_VALUES
        },
        key=str.lower,
    )

    metadata_values = sorted(
        {
            value.lower()
            for match in METADATA_RE.finditer(source)
            for value in match.groups()
            if value
        }
    )
    metadata_matches = colorset in metadata_values
    extended_colors = sorted(set(canonical_colors) & extended)

    findings: list[str] = []
    if malformed_colors:
        findings.append("Use exact lowercase six-digit hex tokens only.")
    if forbidden_colors:
        findings.append(f"Found colors outside {colorset}.")
    if functional_syntax:
        findings.append("Functional color syntax is forbidden; use palette hex plus opacity.")
    if named_paints:
        findings.append("Named paint values are forbidden.")
    if require_metadata and not metadata_matches:
        findings.append(f"Missing active palette metadata for {colorset}.")
    if require_extended and colorset != "colorset2":
        findings.append("--require-extended is valid only with colorset2.")
    if require_extended and not extended_colors:
        findings.append("No colorset2-only token appears on the static surface.")

    return {
        "ok": not findings,
        "artifact": str(resolved),
        "colorset": colorset,
        "requireExtended": require_extended,
        "requireMetadata": require_metadata,
        "metadataValues": metadata_values,
        "metadataMatches": metadata_matches,
        "colorsUsed": canonical_colors,
        "extendedColorsUsed": extended_colors,
        "malformedColors": malformed_colors,
        "forbiddenColors": forbidden_colors,
        "functionalColorSyntax": functional_syntax,
        "namedPaints": named_paints,
        "ignoredDynamicScriptCount": ignored_script_count,
        "findings": findings,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="HTML, SVG, or CSS artifact to validate.")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument(
        "--require-extended",
        action="store_true",
        help="Require a colorset2-only token on the statically visible surface.",
    )
    parser.add_argument(
        "--no-require-metadata",
        action="store_true",
        help="Do not require data-colorset/data-color-set or JSON colorset metadata.",
    )
    parser.add_argument("--json-report", type=Path, help="Optional report output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.artifact.is_file():
        raise SystemExit(f"Artifact does not exist: {args.artifact}")
    report = validate_artifact(
        args.artifact,
        colorset=args.colorset,
        require_extended=args.require_extended,
        require_metadata=not args.no_require_metadata,
    )
    serialized = json.dumps(report, indent=2, sort_keys=True)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(serialized + "\n", encoding="utf-8", newline="\n")
    print(serialized)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

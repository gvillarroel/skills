#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check a Slidev Mermaid deck's static inputs without modifying the deck."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
STYLE_LINE = re.compile(r"^\s*(?:style|classDef|linkStyle)\b", re.IGNORECASE)
INIT_LINE = re.compile(r"^\s*%%\s*\{\s*(?:init|config)\s*:", re.IGNORECASE)
THEME_FIELD = re.compile(r"\b(?:theme|themeVariables|themeCSS|colorsetPresentation)['\"]?\s*[:=]", re.IGNORECASE)
RUNTIME_FILES = ("diagram-style.mjs", "setup/mermaid.ts", "setup/mermaid-renderer.ts")


def mermaid_blocks(source: str) -> tuple[list[tuple[int, str, str]], list[str]]:
    blocks: list[tuple[int, str, str]] = []
    errors: list[str] = []
    opened: tuple[str, int, str] | None = None
    body: list[str] = []
    for line_number, line in enumerate(source.splitlines(), 1):
        match = FENCE.match(line)
        if opened is None:
            if match:
                marker, info = match.groups()
                opened = (marker, line_number, info.strip())
                body = []
            continue
        marker, start, info = opened
        if match and match[1][0] == marker[0] and len(match[1]) >= len(marker) and not match[2].strip():
            if info.split(maxsplit=1)[0:1] == ["mermaid"]:
                blocks.append((start, info, "\n".join(body)))
            opened = None
        else:
            body.append(line)
    if opened is not None:
        errors.append(f"Unclosed Markdown fence opened on line {opened[1]}.")
    return blocks, errors


def plain_errors(blocks: list[tuple[int, str, str]]) -> list[str]:
    errors: list[str] = []
    for start, info, body in blocks:
        if THEME_FIELD.search(info):
            errors.append(f"Mermaid fence on line {start} has a presentation override.")
        lines = body.splitlines()
        for offset, line in enumerate(lines, 1):
            if STYLE_LINE.match(line) or INIT_LINE.match(line):
                errors.append(f"Mermaid body on line {start + offset} has a style or init directive.")
        # Mermaid's own YAML frontmatter is inside its fence. Slidev headmatter
        # outside fences is legal and is never tested by this plain-source gate.
        first = next((index for index, line in enumerate(lines) if line.strip()), None)
        if first is not None and lines[first].strip() == "---":
            end = next((index for index in range(first + 1, len(lines)) if lines[index].strip() == "---"), len(lines))
            if THEME_FIELD.search("\n".join(lines[first + 1:end])):
                errors.append(f"Mermaid fence on line {start} has a theme in diagram frontmatter.")
    return errors


def check(deck: Path, expect_blocks: int | None, plain: bool) -> dict[str, object]:
    errors: list[str] = []
    for relative in RUNTIME_FILES:
        if not (deck / relative).is_file():
            errors.append(f"Missing runtime file: {relative}.")
        elif (deck / relative).stat().st_size == 0:
            errors.append(f"Empty runtime file: {relative}.")
    dependencies: dict[str, str] = {}
    try:
        package = json.loads((deck / "package.json").read_text(encoding="utf-8-sig"))
        if not isinstance(package, dict):
            raise ValueError("package.json must contain an object")
        for group in ("dependencies", "devDependencies"):
            values = package.get(group, {})
            if isinstance(values, dict):
                dependencies.update({name: version for name, version in values.items() if isinstance(version, str) and version.strip()})
    except (OSError, ValueError) as error:
        errors.append(f"Cannot read package.json: {error}.")
    if "@slidev/cli" not in dependencies:
        errors.append("Declare @slidev/cli in dependencies or devDependencies.")
    themes = sorted(name for name in dependencies if name.startswith("@slidev/theme-") or name.startswith("slidev-theme-") or "/slidev-theme-" in name)
    if not themes:
        errors.append("Declare the selected Slidev theme package in dependencies or devDependencies, including @slidev/theme-default for the default theme.")
    blocks: list[tuple[int, str, str]] = []
    try:
        blocks, fence_errors = mermaid_blocks((deck / "slides.md").read_text(encoding="utf-8-sig"))
        errors.extend(fence_errors)
    except OSError as error:
        errors.append(f"Cannot read slides.md: {error}.")
    if expect_blocks is not None and len(blocks) != expect_blocks:
        errors.append(f"Expected {expect_blocks} Mermaid blocks; found {len(blocks)}.")
    if plain:
        errors.extend(plain_errors(blocks))
    return {
        "passed": not errors,
        "deck": str(deck),
        "mermaidBlocks": len(blocks),
        "plainMermaid": plain,
        "declaredThemePackages": themes,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deck", required=True, type=Path, help="Read-only Slidev deck root.")
    parser.add_argument("--expect-blocks", type=int, help="Required Mermaid fence count, not a slide count.")
    parser.add_argument("--plain-mermaid", action="store_true", help="Reject presentation directives only in Mermaid fences and their own frontmatter.")
    args = parser.parse_args()
    if args.expect_blocks is not None and args.expect_blocks < 0:
        parser.error("--expect-blocks must be nonnegative")
    result = check(args.deck.resolve(), args.expect_blocks, args.plain_mermaid)
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

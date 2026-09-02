#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PLACEHOLDER_RE = re.compile(
    r"(?i)\b(TBD|TODO|PLACEHOLDER|INSERT HERE|TO FILL|FILL IN)\b|\[[^\]]*(insert|todo|tbd|placeholder)[^\]]*\]"
)


def load_text(path: Path) -> str:
    if not path.exists():
        raise ValueError(f"{path}: file does not exist")
    if not path.is_file():
        raise ValueError(f"{path}: expected a file")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError(f"{path}: file is empty")
    return text


def load_json(path: Path) -> Any:
    text = load_text(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError(f"{path}: invalid JSON: {error}") from error


def require_mapping(value: Any, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def validate_source_package(path: Path) -> str:
    data = require_mapping(load_json(path), path)
    required = ["version", "sourceId", "route", "facts", "literalAnchors"]
    for key in required:
        if key not in data:
            raise ValueError(f"{path}: missing required key '{key}'")
    if not isinstance(data["facts"], list) or not data["facts"]:
        raise ValueError(f"{path}: facts must be a non-empty list")
    if not isinstance(data["literalAnchors"], list):
        raise ValueError(f"{path}: literalAnchors must be a list")
    return path.read_text(encoding="utf-8")


def validate_shot_contract(path: Path) -> tuple[str, int]:
    data = require_mapping(load_json(path), path)
    required = ["version", "durationSeconds", "shots", "literalAnchors"]
    for key in required:
        if key not in data:
            raise ValueError(f"{path}: missing required key '{key}'")
    shots = data["shots"]
    if not isinstance(shots, list) or not shots:
        raise ValueError(f"{path}: shots must be a non-empty list")
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            raise ValueError(f"{path}: shot {index} must be an object")
        for key in ["id", "start", "duration", "purpose", "visual", "motionIntent", "media", "validation"]:
            if key not in shot:
                raise ValueError(f"{path}: shot {index} missing '{key}'")
        if not isinstance(shot["motionIntent"], list) or not shot["motionIntent"]:
            raise ValueError(f"{path}: shot {index} motionIntent must be a non-empty list")
    return path.read_text(encoding="utf-8"), len(shots)


def scan_text(name: str, text: str, forbidden: list[str]) -> list[str]:
    findings: list[str] = []
    match = PLACEHOLDER_RE.search(text)
    if match:
        findings.append(f"{name}: placeholder text found near '{match.group(0)}'")
    lowered = text.lower()
    for token in forbidden:
        token_lower = token.lower()
        if token_lower == "gsap":
            patterns = ["gsap.", "gsap(", "from \"gsap\"", "from 'gsap'", "gsap.min.js", "gsap@"]
            for pattern in patterns:
                if pattern in lowered:
                    findings.append(f"{name}: forbidden GSAP implementation pattern found: {pattern}")
            continue
        if token_lower in lowered:
            findings.append(f"{name}: forbidden token found: {token}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate engine-agnostic video planning artifacts.")
    parser.add_argument("--source-package", type=Path, help="Path to source-package.json.")
    parser.add_argument("--storyboard", type=Path, help="Path to storyboard.md.")
    parser.add_argument("--shot-contract", type=Path, help="Path to shot-contract.json.")
    parser.add_argument("--require-anchor", action="append", default=[], help="Literal string that must appear.")
    parser.add_argument("--forbid", action="append", default=["gsap"], help="Case-insensitive forbidden token.")
    parser.add_argument("--expect-shots", type=int, help="Exact expected shot count for shot-contract.json.")
    parser.add_argument("--min-shots", type=int, help="Minimum expected shot count for shot-contract.json.")
    parser.add_argument("--max-shots", type=int, help="Maximum expected shot count for shot-contract.json.")
    args = parser.parse_args()

    texts: list[tuple[str, str]] = []
    findings: list[str] = []
    shot_count: int | None = None

    try:
        if args.source_package:
            texts.append((str(args.source_package), validate_source_package(args.source_package)))
        if args.storyboard:
            texts.append((str(args.storyboard), load_text(args.storyboard)))
        if args.shot_contract:
            shot_text, shot_count = validate_shot_contract(args.shot_contract)
            texts.append((str(args.shot_contract), shot_text))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    if not texts:
        print("Provide at least one artifact path.", file=sys.stderr)
        return 2

    combined = "\n".join(text for _, text in texts)
    for name, text in texts:
        findings.extend(scan_text(name, text, args.forbid))

    for anchor in args.require_anchor:
        if anchor not in combined:
            findings.append(f"required anchor missing: {anchor}")

    if args.expect_shots is not None and shot_count != args.expect_shots:
        findings.append(f"expected {args.expect_shots} shots, found {shot_count}")
    if args.min_shots is not None and (shot_count is None or shot_count < args.min_shots):
        findings.append(f"expected at least {args.min_shots} shots, found {shot_count}")
    if args.max_shots is not None and (shot_count is None or shot_count > args.max_shots):
        findings.append(f"expected at most {args.max_shots} shots, found {shot_count}")

    if findings:
        print(f"Validation failed with {len(findings)} finding(s):")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("Video contract validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

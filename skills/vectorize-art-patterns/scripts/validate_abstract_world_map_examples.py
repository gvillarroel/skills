#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate the published abstract-world-map example set."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET


SKILL_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_ROOT = (
    SKILL_ROOT / "assets" / "examples" / "vectorize-abstract-world-maps"
)
MANIFEST_PATH = EXAMPLE_ROOT / "manifest.json"
INDEX_PATH = EXAMPLE_ROOT / "index.html"
PALETTE_PATH = SKILL_ROOT / "assets" / "palettes" / "colorsets.json"

EXPECTED_IDS = {
    "vectorize-abstract-continental-drift-cs1",
    "vectorize-biomorphic-world-map-cs1",
}
FORBIDDEN_TAGS = {"image", "script", "foreignObject", "iframe", "a", "use"}
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")
CURVE_COMMAND = re.compile(r"[CQASTcqast]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-report", type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def validate_svg(
    record: dict,
    allowed_colors: set[str],
    errors: list[str],
) -> dict:
    pattern_id = record["id"]
    svg_path = EXAMPLE_ROOT / record["file"]
    finding = {
        "id": pattern_id,
        "file": record["file"],
        "sha256": None,
        "pathCount": 0,
    }
    if not svg_path.is_file():
        errors.append(f"{pattern_id}: missing SVG {record['file']}")
        return finding
    digest = sha256_file(svg_path)
    finding["sha256"] = digest
    if digest != record["sha256"]:
        errors.append(f"{pattern_id}: manifest SHA-256 mismatch")
    text = svg_path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        errors.append(f"{pattern_id}: invalid XML: {error}")
        return finding

    elements = list(root.iter())
    tags = [local_name(element.tag) for element in elements]
    paths = [element for element in elements if local_name(element.tag) == "path"]
    finding["pathCount"] = len(paths)
    if local_name(root.tag) != "svg":
        errors.append(f"{pattern_id}: root is not svg")
    if root.attrib.get("data-pattern-id") != pattern_id:
        errors.append(f"{pattern_id}: root pattern ID mismatch")
    if root.attrib.get("data-colorset") != "colorset1":
        errors.append(f"{pattern_id}: expected Colorset 1")
    if root.attrib.get("role") != "img":
        errors.append(f"{pattern_id}: missing role=img")
    if root.attrib.get("viewBox") != record["viewBox"]:
        errors.append(f"{pattern_id}: viewBox mismatch")
    if tags.count("title") != 1 or tags.count("desc") != 1:
        errors.append(f"{pattern_id}: expected one title and one desc")
    forbidden = sorted(set(tags) & FORBIDDEN_TAGS)
    if forbidden:
        errors.append(f"{pattern_id}: forbidden tags: {', '.join(forbidden)}")
    if not paths:
        errors.append(f"{pattern_id}: no editable paths")
    if re.search(r"(?:href|src)\s*=", text):
        errors.append(f"{pattern_id}: href/src references are forbidden")
    for element in elements:
        for value in element.attrib.values():
            if "url(" in value:
                for reference in re.findall(r"url\(([^)]+)\)", value):
                    if not reference.strip("'\" ").startswith("#"):
                        errors.append(
                            f"{pattern_id}: external URL reference {reference}"
                        )
    used_colors = {match.lower() for match in HEX_COLOR.findall(text)}
    disallowed = sorted(used_colors - allowed_colors)
    if disallowed:
        errors.append(
            f"{pattern_id}: disallowed Colorset 1 colors: {', '.join(disallowed)}"
        )
    path_data = [path.attrib.get("d", "") for path in paths]
    if any(not value for value in path_data):
        errors.append(f"{pattern_id}: empty path data")

    metadata_element = next(
        (element for element in elements if local_name(element.tag) == "metadata"),
        None,
    )
    metadata: dict = {}
    if metadata_element is None:
        errors.append(f"{pattern_id}: missing metadata")
    else:
        try:
            metadata = json.loads(metadata_element.text or "")
        except json.JSONDecodeError as error:
            errors.append(f"{pattern_id}: invalid metadata JSON: {error}")

    if pattern_id == "vectorize-abstract-continental-drift-cs1":
        art_paths = [
            path
            for path in paths
            if path.attrib.get("id", "").startswith(
                (
                    "north-",
                    "south-",
                    "europe-",
                    "africa-",
                    "asia-",
                    "oceania-",
                    "antarctica-",
                    "atlantic-",
                    "indian-",
                    "axis-",
                )
            )
        ]
        axes = [path for path in art_paths if path.attrib.get("fill") == "none"]
        masses = [path for path in art_paths if path.attrib.get("fill") != "none"]
        if len(masses) != 36 or len(axes) != 7:
            errors.append(
                f"{pattern_id}: expected 36 masses and 7 axes, "
                f"found {len(masses)} and {len(axes)}"
            )
        curved = [
            path.attrib.get("id", "")
            for path in art_paths
            if CURVE_COMMAND.search(path.attrib.get("d", ""))
        ]
        if curved:
            errors.append(
                f"{pattern_id}: curve commands found in {', '.join(curved)}"
            )
        if any(local_name(element.tag) in {"clipPath", "mask"} for element in elements):
            errors.append(f"{pattern_id}: abstract variant retains a clip or mask")
        if metadata.get("pipeline", {}).get("cartographic_precision") != (
            "intentionally low"
        ):
            errors.append(f"{pattern_id}: low-precision contract is missing")
    else:
        art_paths = [
            path
            for path in paths
            if path.attrib.get("id", "").startswith(("drift-", "mass-"))
        ]
        if len(art_paths) != 25:
            errors.append(
                f"{pattern_id}: expected 25 art paths, found {len(art_paths)}"
            )
        if tags.count("clipPath") != 1:
            errors.append(f"{pattern_id}: expected one land clip")
        if metadata.get("pipeline", {}).get("projection") != "Equal Earth":
            errors.append(f"{pattern_id}: Equal Earth metadata is missing")

    return finding


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    palette = json.loads(PALETTE_PATH.read_text(encoding="utf-8"))
    allowed_colors = {
        color.lower()
        for color in palette["colorsets"]["colorset1"]["allowed"]
    }
    records = manifest.get("patterns", [])
    record_ids = {record.get("id") for record in records}
    if manifest.get("exampleSetId") != "vectorize-abstract-world-maps":
        errors.append("Unexpected example-set ID")
    if record_ids != EXPECTED_IDS:
        errors.append(
            f"Manifest IDs differ: expected {sorted(EXPECTED_IDS)}, "
            f"found {sorted(record_ids)}"
        )
    if len(records) != 2:
        errors.append(f"Expected 2 manifest records, found {len(records)}")

    html = INDEX_PATH.read_text(encoding="utf-8")
    if 'data-example-set-id="vectorize-abstract-world-maps"' not in html:
        errors.append("Page example-set ID is missing")
    for record in records:
        pattern_id = record["id"]
        if html.count(f'data-pattern-id="{pattern_id}"') != 1:
            errors.append(f"{pattern_id}: page data-pattern-id parity failure")
        if record["file"] not in html:
            errors.append(f"{pattern_id}: page file link is missing")

    findings = [
        validate_svg(record, allowed_colors, errors)
        for record in records
    ]
    result = {
        "schemaVersion": 1,
        "exampleSetId": "vectorize-abstract-world-maps",
        "status": "pass" if not errors else "fail",
        "patternCount": len(records),
        "patterns": findings,
        "errors": errors,
    }
    output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(output, end="")
    if args.output_report:
        args.output_report.parent.mkdir(parents=True, exist_ok=True)
        args.output_report.write_text(output, encoding="utf-8", newline="\n")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

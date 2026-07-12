#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate manifest, SVG, and producer-report semantic proof consistency."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "source" / "asset-manifest.json"
REQUIRED_CHECKS = {
    "viewbox-dimensions",
    "color-contrast",
    "three-second-silent-comprehension",
    "directed-semantic-flow",
    "stable-semantic-ids",
}
REQUIRED_GROUP_IDS = {"input", "process", "output", "active-state"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def project_path(relative_path: str) -> Path:
    normalized = Path(relative_path.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise ValueError(f"Path must stay inside the project: {relative_path}")
    resolved = (PROJECT_ROOT / normalized).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT) or not resolved.is_file():
        raise ValueError(f"Missing or unsafe project file: {relative_path}")
    return resolved


def find_element_by_id(root: ET.Element, element_id: str) -> ET.Element | None:
    for element in root.iter():
        if element.get("id") == element_id:
            return element
    return None


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("asset-manifest.json needs a non-empty assets list")

    results: list[dict[str, Any]] = []
    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("Each manifest asset must be an object")
        asset_id = asset.get("id")
        output = asset.get("output")
        producer = asset.get("producer")
        quality_checks = asset.get("qualityChecks")
        if not isinstance(asset_id, str) or not isinstance(output, str):
            raise ValueError("Each asset needs string id and output fields")
        if not isinstance(producer, dict) or not isinstance(producer.get("report"), str):
            raise ValueError(f"Asset {asset_id!r} needs a producer report")
        if not isinstance(quality_checks, list) or len(quality_checks) < 5:
            raise ValueError(f"Asset {asset_id!r} needs the five semantic quality checks")

        svg_path = project_path(output)
        digest = sha256(svg_path)
        report_path = project_path(producer["report"])
        report = read_json(report_path)
        if asset.get("sha256") != digest:
            raise ValueError(f"Manifest hash mismatch for {asset_id}")
        if report.get("sha256") != digest or report.get("outputSha256") != digest:
            raise ValueError(f"Producer report hash mismatch for {asset_id}")
        if report.get("assetId") != asset_id or report.get("output") != output:
            raise ValueError(f"Producer report identity mismatch for {asset_id}")
        if report.get("ok") is not True:
            raise ValueError(f"Producer report is not approved for {asset_id}")

        root = ET.parse(svg_path).getroot()
        if root.get("id") != asset_id or root.get("data-asset-id") != asset_id:
            raise ValueError(f"SVG root identity mismatch for {asset_id}")
        missing_group_ids = sorted(
            group_id
            for group_id in REQUIRED_GROUP_IDS
            if find_element_by_id(root, group_id) is None
        )
        if missing_group_ids:
            raise ValueError(f"SVG semantic group mismatch for {asset_id}: {missing_group_ids}")

        semantic_contract = report.get("semanticContract")
        if not isinstance(semantic_contract, dict):
            raise ValueError(f"Producer report lacks semanticContract for {asset_id}")
        if semantic_contract.get("silentFrameSeconds") != 3:
            raise ValueError(f"Silent-frame duration mismatch for {asset_id}")
        declared_labels = semantic_contract.get("visibleLabels")
        if not isinstance(declared_labels, list) or not declared_labels:
            raise ValueError(f"Producer report lacks visible labels for {asset_id}")
        visible_text = "\n".join(
            " ".join("".join(element.itertext()).split()) for element in root.iter()
        )
        missing_labels = [label for label in declared_labels if label not in visible_text]
        if missing_labels:
            raise ValueError(f"Declared labels are absent from {asset_id}: {missing_labels}")

        checks = report.get("checks")
        if not isinstance(checks, list):
            raise ValueError(f"Producer report lacks checks for {asset_id}")
        check_names = {
            check.get("name")
            for check in checks
            if isinstance(check, dict) and check.get("passed") is True
        }
        if check_names != REQUIRED_CHECKS:
            raise ValueError(
                f"Producer report semantic checks mismatch for {asset_id}: {check_names}"
            )

        results.append(
            {
                "assetId": asset_id,
                "sha256": digest,
                "manifestHashMatches": True,
                "reportHashesMatch": True,
                "rootAndSemanticIdsMatch": True,
                "silentFrameLabelsPresent": True,
                "semanticChecksPassed": sorted(check_names),
            }
        )

    print(
        json.dumps(
            {
                "ok": True,
                "assetCount": len(results),
                "assets": results,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from plantuml_coverage import (
    DEFAULT_MANIFEST,
    load_json,
    validate_fixture_directory,
    validate_gallery_metadata,
    validate_manifest,
    validate_report_coverage,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate frozen PlantUML family, fixture, report, and gallery coverage.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Frozen PlantUML coverage manifest.")
    parser.add_argument("--fixtures", type=Path, required=True, help="Acceptance fixture directory.")
    parser.add_argument("--report", type=Path, action="append", default=[], help="Coverage render report. May be repeated.")
    parser.add_argument("--gallery", type=Path, action="append", default=[], help="Gallery directory containing coverage.json. May be repeated.")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    findings = validate_manifest(manifest)
    if not findings:
        findings.extend(validate_fixture_directory(manifest, args.fixtures))

    for report_path in args.report:
        report = load_json(report_path)
        findings.extend(f"{report_path}: {finding}" for finding in validate_report_coverage(report, manifest))

    for gallery_dir in args.gallery:
        metadata_path = gallery_dir / "coverage.json"
        if not metadata_path.is_file():
            findings.append(f"{gallery_dir}: missing coverage.json")
            continue
        metadata = load_json(metadata_path)
        findings.extend(
            f"{gallery_dir}: {finding}"
            for finding in validate_gallery_metadata(metadata, manifest, gallery_dir)
        )

    result = {
        "ok": not findings,
        "baselineVersion": manifest.get("baseline", {}).get("version"),
        "canonicalFamilyCount": manifest.get("counts", {}).get("canonicalFamilies"),
        "releaseExtraFamilyCount": manifest.get("counts", {}).get("releaseExtraFamilies"),
        "totalFamilyCount": manifest.get("counts", {}).get("totalFamilies"),
        "fixtureCount": manifest.get("counts", {}).get("fixtures"),
        "publishedFixtureCount": manifest.get("counts", {}).get("publishedFixtures"),
        "findings": findings,
    }
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

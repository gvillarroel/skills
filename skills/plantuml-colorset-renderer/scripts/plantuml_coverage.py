#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_MANIFEST = SKILL_DIR / "references" / "diagram-types.json"
SUPPORTED_FORMATS = {"svg", "png"}
SUPPORTED_TAXONOMIES = {"canonical", "release-extra"}
SUPPORTED_THEME_MODES = {"inject", "none"}
SUPPORTED_AVAILABILITY = {"available", "upstream-unavailable"}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = (path or DEFAULT_MANIFEST).resolve()
    manifest = load_json(manifest_path)
    findings = validate_manifest(manifest)
    if findings:
        raise ValueError("Invalid PlantUML coverage manifest: " + "; ".join(findings))
    return manifest


def _duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def flatten_fixtures(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for family in manifest.get("families", []):
        if not isinstance(family, dict):
            continue
        for fixture in family.get("fixtures", []):
            if not isinstance(fixture, dict):
                continue
            flattened.append(
                {
                    "familyId": family.get("id"),
                    "fixtureId": fixture.get("id"),
                    "source": fixture.get("source"),
                    "label": family.get("label"),
                    "category": family.get("category"),
                    "taxonomy": family.get("taxonomy"),
                    "directives": family.get("directives", []),
                    "themeMode": family.get("themeMode"),
                    "availability": family.get("availability"),
                    "formats": family.get("formats", []),
                    "sourceUrls": family.get("sourceUrls", []),
                    "publication": fixture.get("publication", {}),
                }
            )
    return flattened


def fixture_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {fixture["source"]: fixture for fixture in flatten_fixtures(manifest)}


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if manifest.get("schemaVersion") != 1:
        findings.append("schemaVersion must be 1")

    baseline = manifest.get("baseline")
    if not isinstance(baseline, dict):
        findings.append("baseline must be an object")
    else:
        for field in ("product", "version", "releaseDate", "auditedAt", "taxonomyUrl", "releaseUrl", "changesUrl"):
            if not isinstance(baseline.get(field), str) or not baseline[field].strip():
                findings.append(f"baseline.{field} must be a non-empty string")

    families = manifest.get("families")
    if not isinstance(families, list) or not families:
        return findings + ["families must be a non-empty list"]

    family_ids: list[str] = []
    fixture_ids: list[str] = []
    fixture_sources: list[str] = []
    canonical_count = 0
    release_extra_count = 0
    published_count = 0

    for index, family in enumerate(families):
        prefix = f"families[{index}]"
        if not isinstance(family, dict):
            findings.append(f"{prefix} must be an object")
            continue
        family_id = family.get("id")
        if not isinstance(family_id, str) or not family_id:
            findings.append(f"{prefix}.id must be a non-empty string")
            family_id = f"#{index}"
        else:
            family_ids.append(family_id)
        if not isinstance(family.get("label"), str) or not family["label"].strip():
            findings.append(f"{family_id}: label must be a non-empty string")
        if not isinstance(family.get("category"), str) or not family["category"].strip():
            findings.append(f"{family_id}: category must be a non-empty string")

        taxonomy = family.get("taxonomy")
        if taxonomy not in SUPPORTED_TAXONOMIES:
            findings.append(f"{family_id}: taxonomy must be canonical or release-extra")
        elif taxonomy == "canonical":
            canonical_count += 1
        else:
            release_extra_count += 1

        if family.get("themeMode") not in SUPPORTED_THEME_MODES:
            findings.append(f"{family_id}: unsupported themeMode")
        availability = family.get("availability")
        if availability not in SUPPORTED_AVAILABILITY:
            findings.append(f"{family_id}: unsupported availability")

        formats = family.get("formats")
        if not isinstance(formats, list) or any(fmt not in SUPPORTED_FORMATS for fmt in formats):
            findings.append(f"{family_id}: formats must contain only svg and png")
        if availability == "available" and not formats:
            findings.append(f"{family_id}: available family must declare at least one format")
        if availability == "upstream-unavailable" and formats:
            findings.append(f"{family_id}: upstream-unavailable family formats must be empty")

        directives = family.get("directives")
        if not isinstance(directives, list) or not directives:
            findings.append(f"{family_id}: directives must be a non-empty list")
            directives = []
        for directive in directives:
            if not isinstance(directive, dict):
                findings.append(f"{family_id}: directive must be an object")
                continue
            start = directive.get("start")
            end = directive.get("end")
            if not isinstance(start, str) or not start.startswith("@start"):
                findings.append(f"{family_id}: invalid start directive")
            if not isinstance(end, str) or not end.startswith("@end"):
                findings.append(f"{family_id}: invalid end directive")

        urls = family.get("sourceUrls")
        if not isinstance(urls, list) or not urls or any(not isinstance(url, str) or not url.startswith("https://") for url in urls):
            findings.append(f"{family_id}: sourceUrls must contain HTTPS URLs")

        fixtures = family.get("fixtures")
        if not isinstance(fixtures, list) or not fixtures:
            findings.append(f"{family_id}: fixtures must be a non-empty list")
            continue
        for fixture in fixtures:
            if not isinstance(fixture, dict):
                findings.append(f"{family_id}: fixture must be an object")
                continue
            fixture_id = fixture.get("id")
            source = fixture.get("source")
            if not isinstance(fixture_id, str) or not fixture_id:
                findings.append(f"{family_id}: fixture id must be a non-empty string")
            else:
                fixture_ids.append(fixture_id)
            if not isinstance(source, str) or not source.endswith((".puml", ".plantuml", ".pu")):
                findings.append(f"{family_id}/{fixture_id}: fixture source must be a PlantUML filename")
            else:
                fixture_sources.append(source)
            publication = fixture.get("publication")
            if not isinstance(publication, dict) or not isinstance(publication.get("enabled"), bool):
                findings.append(f"{family_id}/{fixture_id}: publication.enabled must be boolean")
                continue
            if publication["enabled"]:
                published_count += 1
                asset_format = publication.get("assetFormat")
                if asset_format not in formats:
                    findings.append(f"{family_id}/{fixture_id}: publication assetFormat must be a supported family format")
                for field in ("kicker", "title", "copy"):
                    if not isinstance(publication.get(field), str) or not publication[field].strip():
                        findings.append(f"{family_id}/{fixture_id}: publication.{field} must be a non-empty string")
            elif publication.get("assetFormat") is not None:
                findings.append(f"{family_id}/{fixture_id}: unpublished fixture assetFormat must be null")

    for duplicate in _duplicates(family_ids):
        findings.append(f"duplicate family id: {duplicate}")
    for duplicate in _duplicates(fixture_ids):
        findings.append(f"duplicate fixture id: {duplicate}")
    for duplicate in _duplicates(fixture_sources):
        findings.append(f"duplicate fixture source: {duplicate}")

    counts = manifest.get("counts")
    actual_counts = {
        "canonicalFamilies": canonical_count,
        "releaseExtraFamilies": release_extra_count,
        "totalFamilies": len(family_ids),
        "fixtures": len(fixture_ids),
        "publishedFixtures": published_count,
    }
    if not isinstance(counts, dict):
        findings.append("counts must be an object")
    else:
        for key, actual in actual_counts.items():
            if counts.get(key) != actual:
                findings.append(f"counts.{key} must be {actual}")
    return findings


def _first_directive(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip().lower()
        if stripped.startswith(prefix):
            return stripped.split()[0]
    return None


def validate_fixture_directory(manifest: dict[str, Any], fixture_dir: Path) -> list[str]:
    findings: list[str] = []
    expected = fixture_index(manifest)
    observed_paths = sorted(
        path for path in fixture_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".puml", ".plantuml", ".pu"}
    )
    observed = {path.relative_to(fixture_dir).as_posix(): path for path in observed_paths}
    missing = sorted(set(expected) - set(observed))
    unexpected = sorted(set(observed) - set(expected))
    if missing:
        findings.append(f"missing fixture sources: {missing}")
    if unexpected:
        findings.append(f"unexpected fixture sources: {unexpected}")

    for source in sorted(set(expected) & set(observed)):
        fixture = expected[source]
        text = observed[source].read_text(encoding="utf-8")
        start = _first_directive(text, "@start")
        end = _first_directive(text, "@end")
        allowed = {
            (directive.get("start", "").lower(), directive.get("end", "").lower())
            for directive in fixture["directives"]
            if isinstance(directive, dict)
        }
        if (start, end) not in allowed:
            findings.append(f"{source}: directives {(start, end)} not in manifest {sorted(allowed)}")
    return findings


def expected_output_formats(fixture: dict[str, Any], report: dict[str, Any]) -> set[str]:
    if fixture["availability"] != "available":
        return set()
    if report.get("publicationOnly") is True:
        publication = fixture["publication"]
        return {publication["assetFormat"]} if publication.get("enabled") else set()
    requested = set(report.get("formats") or [])
    return requested & set(fixture["formats"])


def validate_report_coverage(report: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if report.get("coverageBaseline") != manifest.get("baseline"):
        findings.append("report coverageBaseline must exactly match the frozen manifest")
    if report.get("coverageCounts") != manifest.get("counts"):
        findings.append("report coverageCounts must exactly match the frozen manifest")
    expected_fixtures = flatten_fixtures(manifest)
    expected_by_id = {fixture["fixtureId"]: fixture for fixture in expected_fixtures}
    expected_family_ids = {fixture["familyId"] for fixture in expected_fixtures}
    results = report.get("results")
    if not isinstance(results, list):
        return ["coverage report results must be a list"]

    fixture_ids = [result.get("fixtureId") for result in results if isinstance(result, dict) and isinstance(result.get("fixtureId"), str)]
    family_ids = [result.get("familyId") for result in results if isinstance(result, dict) and isinstance(result.get("familyId"), str)]
    sources = [result.get("source") for result in results if isinstance(result, dict) and isinstance(result.get("source"), str)]
    diagram_ids = [result.get("diagramId") for result in results if isinstance(result, dict) and isinstance(result.get("diagramId"), str)]

    for label, values in (("fixture id", fixture_ids), ("source", sources), ("diagram id", diagram_ids)):
        duplicates = _duplicates(values)
        if duplicates:
            findings.append(f"duplicate report {label}s: {duplicates}")

    missing_fixtures = sorted(set(expected_by_id) - set(fixture_ids))
    unexpected_fixtures = sorted(set(fixture_ids) - set(expected_by_id))
    if missing_fixtures:
        findings.append(f"missing report fixture ids: {missing_fixtures}")
    if unexpected_fixtures:
        findings.append(f"unexpected report fixture ids: {unexpected_fixtures}")

    observed_family_ids = set(family_ids)
    missing_families = sorted(expected_family_ids - observed_family_ids)
    unexpected_families = sorted(observed_family_ids - expected_family_ids)
    if missing_families:
        findings.append(f"missing report family ids: {missing_families}")
    if unexpected_families:
        findings.append(f"unexpected report family ids: {unexpected_families}")

    counts = manifest["counts"]
    if len(results) != counts["fixtures"]:
        findings.append(f"report result count must be {counts['fixtures']}")
    if report.get("sourceDiagramCount") != counts["fixtures"]:
        findings.append(f"sourceDiagramCount must be {counts['fixtures']}")
    if len(observed_family_ids) != counts["totalFamilies"]:
        findings.append(f"observed family count must be {counts['totalFamilies']}")

    result_by_fixture = {
        result.get("fixtureId"): result
        for result in results
        if isinstance(result, dict) and isinstance(result.get("fixtureId"), str)
    }
    for fixture_id in sorted(set(expected_by_id) & set(result_by_fixture)):
        fixture = expected_by_id[fixture_id]
        result = result_by_fixture[fixture_id]
        if result.get("familyId") != fixture["familyId"]:
            findings.append(f"{fixture_id}: familyId must be {fixture['familyId']}")
        if result.get("source") != fixture["source"]:
            findings.append(f"{fixture_id}: source must be {fixture['source']}")
        if result.get("themeMode") != fixture["themeMode"]:
            findings.append(f"{fixture_id}: themeMode must be {fixture['themeMode']}")
        if result.get("availability") != fixture["availability"]:
            findings.append(f"{fixture_id}: availability must be {fixture['availability']}")
        expected_status = "rendered" if fixture["availability"] == "available" else "expected-unavailable"
        if result.get("status") != expected_status:
            findings.append(f"{fixture_id}: status must be {expected_status}")
        outputs = result.get("outputs")
        output_formats = (
            {output.get("format") for output in outputs if isinstance(output, dict)}
            if isinstance(outputs, list)
            else set()
        )
        expected_formats = expected_output_formats(fixture, report)
        if output_formats != expected_formats:
            findings.append(f"{fixture_id}: output formats {sorted(output_formats)} must equal {sorted(expected_formats)}")
    return findings


def build_gallery_metadata(manifest: dict[str, Any], colorset: str) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for fixture in flatten_fixtures(manifest):
        publication = fixture["publication"]
        if not publication.get("enabled"):
            continue
        asset_format = publication["assetFormat"]
        item = {
            "id": fixture["fixtureId"],
            "familyId": fixture["familyId"],
            "taxonomy": fixture["taxonomy"],
            "source": fixture["source"],
            "assetFormat": asset_format,
            "asset": f"{asset_format}/{fixture['fixtureId']}.{asset_format}",
            "kicker": publication["kicker"],
            "title": publication["title"],
            "copy": publication["copy"],
        }
        if publication.get("size"):
            item["size"] = publication["size"]
        items.append(item)
    return {
        "schemaVersion": 1,
        "colorset": colorset,
        "baseline": manifest["baseline"],
        "itemCount": len(items),
        "items": items,
    }


def validate_gallery_metadata(
    metadata: dict[str, Any], manifest: dict[str, Any], gallery_dir: Path | None = None
) -> list[str]:
    findings: list[str] = []
    if metadata.get("schemaVersion") != 1:
        findings.append("gallery schemaVersion must be 1")
    if metadata.get("colorset") not in {"colorset1", "colorset2"}:
        findings.append("gallery colorset must be colorset1 or colorset2")
    if metadata.get("baseline") != manifest.get("baseline"):
        findings.append("gallery baseline must exactly match the frozen manifest")
    expected = build_gallery_metadata(manifest, str(metadata.get("colorset") or ""))
    items = metadata.get("items")
    if not isinstance(items, list):
        return ["gallery items must be a list"]
    ids = [item.get("id") for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)]
    duplicates = _duplicates(ids)
    if duplicates:
        findings.append(f"duplicate gallery item ids: {duplicates}")
    expected_by_id = {item["id"]: item for item in expected["items"]}
    observed_by_id = {item.get("id"): item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)}
    missing = sorted(set(expected_by_id) - set(observed_by_id))
    unexpected = sorted(set(observed_by_id) - set(expected_by_id))
    if missing:
        findings.append(f"missing gallery item ids: {missing}")
    if unexpected:
        findings.append(f"unexpected gallery item ids: {unexpected}")
    if metadata.get("itemCount") != len(items):
        findings.append(f"gallery itemCount must be {len(items)}")
    if len(items) != manifest["counts"]["publishedFixtures"]:
        findings.append(f"gallery must contain {manifest['counts']['publishedFixtures']} published fixtures")
    for item_id in sorted(set(expected_by_id) & set(observed_by_id)):
        expected_item = expected_by_id[item_id]
        observed_item = observed_by_id[item_id]
        for field in ("familyId", "taxonomy", "source", "assetFormat", "asset"):
            if observed_item.get(field) != expected_item[field]:
                findings.append(f"{item_id}: gallery {field} must be {expected_item[field]}")
        if gallery_dir is not None:
            asset = gallery_dir / expected_item["asset"]
            if not asset.is_file() or asset.stat().st_size <= 0:
                findings.append(f"{item_id}: missing or empty gallery asset {expected_item['asset']}")
    return findings

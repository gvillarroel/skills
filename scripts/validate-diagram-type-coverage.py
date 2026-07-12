#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECK_TIMEOUT_SECONDS = 900

MERMAID_VERSION = "11.16.0"
MERMAID_FAMILY_COUNT = 31
MERMAID_CURRENT_DECLARATION_COUNT = 40
MERMAID_RENDERABLE_DECLARATION_COUNT = 48
MERMAID_CLASSDEF_FAMILY_COUNT = 9
MERMAID_FAMILIES = frozenset(
    {
        "architecture", "block", "c4", "classDiagram", "cynefin", "erDiagram", "eventmodeling",
        "flowchart", "gantt", "gitGraph", "ishikawa", "journey", "kanban", "mindmap", "packet",
        "pie", "quadrantChart", "radar", "railroad", "requirementDiagram", "sankey", "sequenceDiagram",
        "stateDiagram", "swimlane", "timeline", "treeView", "treemap", "venn", "wardley", "xyChart",
        "zenuml",
    }
)
MERMAID_CURRENT_DECLARATIONS = frozenset(
    {
        "C4Component", "C4Container", "C4Context", "C4Deployment", "C4Dynamic", "architecture-beta",
        "block", "classDiagram", "cynefin-beta", "erDiagram", "eventmodeling", "flowchart", "gantt",
        "gitGraph", "graph", "ishikawa-beta", "journey", "kanban", "mindmap", "packet", "pie",
        "quadrantChart", "radar-beta", "railroad-abnf-beta", "railroad-beta", "railroad-ebnf-beta",
        "railroad-peg-beta", "requirementDiagram", "sankey", "sequenceDiagram", "stateDiagram",
        "stateDiagram-v2", "swimlane-beta", "timeline", "treeView-beta", "treemap-beta", "venn-beta",
        "wardley-beta", "xychart", "zenuml",
    }
)
MERMAID_RENDERABLE_DECLARATIONS = frozenset(
    {
        "C4Component", "C4Container", "C4Context", "C4Deployment", "C4Dynamic", "architecture-beta",
        "block", "block-beta", "classDiagram", "classDiagram-v2", "cynefin-beta", "erDiagram",
        "eventmodeling", "flowchart", "flowchart-elk", "gantt", "gitGraph", "graph", "ishikawa",
        "ishikawa-beta", "journey", "kanban", "mindmap", "packet", "packet-beta", "pie",
        "quadrantChart", "radar-beta", "railroad-abnf-beta", "railroad-beta", "railroad-ebnf-beta",
        "railroad-peg-beta", "requirementDiagram", "sankey", "sankey-beta", "sequenceDiagram",
        "stateDiagram", "stateDiagram-v2", "swimlane-beta", "timeline", "treeView-beta", "treemap",
        "treemap-beta", "venn-beta", "wardley-beta", "xychart", "xychart-beta", "zenuml",
    }
)
MERMAID_CLASSDEF_FAMILIES = frozenset(
    {"block", "classDiagram", "erDiagram", "flowchart", "quadrantChart", "requirementDiagram", "stateDiagram", "swimlane", "treemap"}
)
MERMAID_ANIMATED_TO_STYLER_FAMILY = {
    "flowchart": "flowchart",
    "swimlane": "swimlane",
    "sequence": "sequenceDiagram",
    "class": "classDiagram",
    "state": "stateDiagram",
    "entity-relationship": "erDiagram",
    "journey": "journey",
    "gantt": "gantt",
    "pie": "pie",
    "quadrant": "quadrantChart",
    "requirement": "requirementDiagram",
    "gitgraph": "gitGraph",
    "c4": "c4",
    "mindmap": "mindmap",
    "timeline": "timeline",
    "zenuml": "zenuml",
    "sankey": "sankey",
    "xychart": "xyChart",
    "block": "block",
    "packet": "packet",
    "kanban": "kanban",
    "architecture": "architecture",
    "radar": "radar",
    "event-modeling": "eventmodeling",
    "treemap": "treemap",
    "venn": "venn",
    "ishikawa": "ishikawa",
    "wardley": "wardley",
    "cynefin": "cynefin",
    "tree-view": "treeView",
    "railroad": "railroad",
}

PLANTUML_VERSION = "1.2026.6"
PLANTUML_CANONICAL_FAMILY_COUNT = 27
PLANTUML_RELEASE_EXTRA_FAMILY_COUNT = 1
PLANTUML_TRACKED_FAMILY_COUNT = 28
PLANTUML_AVAILABLE_FAMILY_COUNT = 27
PLANTUML_FIXTURE_COUNT = 29
PLANTUML_PUBLISHED_FIXTURE_COUNT = 28
PLANTUML_CANONICAL_FAMILIES = frozenset(
    {
        "activity", "archimate", "chart", "chen", "chronology", "class", "component", "deployment",
        "ditaa", "ebnf", "files", "gantt", "ie", "json", "math", "mindmap", "nwdiag", "object",
        "regex", "salt", "sdl", "sequence", "state", "timing", "usecase", "wbs", "yaml",
    }
)
PLANTUML_RELEASE_EXTRA_FAMILIES = frozenset({"packetdiag"})
PLANTUML_FIXTURES = frozenset(
    {
        "activity", "archimate", "chart", "chen", "chronology", "class", "component", "deployment",
        "ditaa", "ebnf", "files", "gantt", "ie", "json", "latex", "math", "mindmap", "nwdiag",
        "object", "packetdiag", "regex", "salt", "sdl", "sequence", "state", "timing", "usecase",
        "wbs", "yaml",
    }
)

MERMAID_STYLER = ROOT / ".agents" / "skills" / "mermaid-colorset-styler"
MERMAID_ANIMATED = ROOT / ".agents" / "skills" / "mermaid-animated-svg"
PLANTUML = ROOT / ".agents" / "skills" / "plantuml-colorset-renderer"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def require_equal(findings: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        findings.append(f"{label} is {actual!r}; expected {expected!r}")


def require_exact_set(findings: list[str], label: str, actual: list[str] | set[str], expected: frozenset[str]) -> None:
    actual_set = set(actual)
    if actual_set != expected:
        findings.append(
            f"{label} differs: missing={sorted(expected - actual_set)}, unexpected={sorted(actual_set - expected)}"
        )


def run_check(name: str, command: list[str]) -> tuple[dict[str, Any], list[str]]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
            timeout=CHECK_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        record = {"name": name, "ok": False, "exitCode": None}
        return record, [f"{name} timed out after {CHECK_TIMEOUT_SECONDS} seconds"]
    record: dict[str, Any] = {
        "name": name,
        "ok": result.returncode == 0,
        "exitCode": result.returncode,
    }
    findings: list[str] = []
    if result.returncode != 0:
        detail = (result.stderr.strip() or result.stdout.strip())[-4000:]
        findings.append(f"{name} failed with exit {result.returncode}: {detail}")
    return record, findings


def validate_mermaid_taxonomies() -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    styler = load_json(MERMAID_STYLER / "references" / "diagram-types.json")
    animated = load_json(MERMAID_ANIMATED / "references" / "diagram-family-coverage.json")

    require_equal(findings, "Mermaid styler version", styler.get("upstream", {}).get("version"), MERMAID_VERSION)
    require_equal(findings, "Mermaid animated version", animated.get("mermaidVersion"), MERMAID_VERSION)

    styler_families = styler.get("families")
    animated_families = animated.get("families")
    if not isinstance(styler_families, list) or not all(isinstance(family, dict) for family in styler_families):
        return {}, findings + ["Mermaid styler families must be a list of objects"]
    if not isinstance(animated_families, list) or not all(isinstance(family, dict) for family in animated_families):
        return {}, findings + ["Mermaid animated families must be a list of objects"]

    require_equal(findings, "Mermaid styler family count", len(styler_families), MERMAID_FAMILY_COUNT)
    require_equal(findings, "Mermaid animated required family count", animated.get("requiredFamilyCount"), MERMAID_FAMILY_COUNT)
    require_equal(findings, "Mermaid animated family count", len(animated_families), MERMAID_FAMILY_COUNT)

    styler_ids = [str(family.get("id")) for family in styler_families]
    animated_ids = [str(family.get("id")) for family in animated_families]
    if duplicate_ids := duplicates(styler_ids):
        findings.append(f"Mermaid styler has duplicate family ids: {duplicate_ids}")
    if duplicate_ids := duplicates(animated_ids):
        findings.append(f"Mermaid animated has duplicate family ids: {duplicate_ids}")
    require_exact_set(findings, "Mermaid family identities", styler_ids, MERMAID_FAMILIES)
    require_exact_set(
        findings,
        "Mermaid animated family identities",
        animated_ids,
        frozenset(MERMAID_ANIMATED_TO_STYLER_FAMILY),
    )

    current_declarations = [
        str(declaration)
        for family in styler_families
        for declaration in family.get("currentDeclarations", [])
    ]
    renderable_declarations = [
        str(declaration)
        for family in styler_families
        for declaration in family.get("acceptedDeclarations", [])
    ]
    classdef_families = [family for family in styler_families if family.get("classDef") is True]
    require_equal(findings, "Mermaid current declaration count", len(current_declarations), MERMAID_CURRENT_DECLARATION_COUNT)
    require_equal(findings, "Mermaid renderable declaration count", len(renderable_declarations), MERMAID_RENDERABLE_DECLARATION_COUNT)
    require_equal(findings, "Mermaid classDef family count", len(classdef_families), MERMAID_CLASSDEF_FAMILY_COUNT)
    require_exact_set(findings, "Mermaid current declaration identities", current_declarations, MERMAID_CURRENT_DECLARATIONS)
    require_exact_set(findings, "Mermaid renderable declaration identities", renderable_declarations, MERMAID_RENDERABLE_DECLARATIONS)
    require_exact_set(
        findings,
        "Mermaid classDef family identities",
        [str(family.get("id")) for family in classdef_families],
        MERMAID_CLASSDEF_FAMILIES,
    )
    if duplicate_values := duplicates(current_declarations):
        findings.append(f"Mermaid has duplicate current declarations: {duplicate_values}")
    if duplicate_values := duplicates(renderable_declarations):
        findings.append(f"Mermaid has duplicate renderable declarations: {duplicate_values}")
    missing_current = sorted(set(current_declarations) - set(renderable_declarations))
    if missing_current:
        findings.append(f"Mermaid current declarations missing from renderable set: {missing_current}")
    if "architecture" in renderable_declarations:
        findings.append("Mermaid detector-only shorthand 'architecture' must not count as renderable")
    if "architecture-beta" not in renderable_declarations:
        findings.append("Mermaid renderable declaration 'architecture-beta' is missing")

    declaration_to_styler_family: dict[str, dict[str, Any]] = {}
    for family in styler_families:
        for declaration in family.get("acceptedDeclarations", []):
            declaration_to_styler_family[str(declaration)] = family

    mapped_styler_ids: list[str] = []
    for family in animated_families:
        family_id = str(family.get("id"))
        source_declaration = str(family.get("sourceDeclaration"))
        styler_family = declaration_to_styler_family.get(source_declaration)
        if styler_family is None:
            findings.append(
                f"Mermaid animated family {family_id} uses untracked source declaration {source_declaration!r}"
            )
            continue
        mapped_styler_id = str(styler_family["id"])
        mapped_styler_ids.append(mapped_styler_id)
        expected_styler_id = MERMAID_ANIMATED_TO_STYLER_FAMILY.get(family_id)
        if expected_styler_id is not None and mapped_styler_id != expected_styler_id:
            findings.append(
                f"Mermaid animated family {family_id} maps to {mapped_styler_id!r}; expected {expected_styler_id!r}"
            )
        animated_declarations = {str(value) for value in family.get("declarations", [])}
        accepted_declarations = {str(value) for value in styler_family.get("acceptedDeclarations", [])}
        unexpected = sorted(animated_declarations - accepted_declarations)
        if unexpected:
            findings.append(
                f"Mermaid animated family {family_id} lists declarations outside its styler family: {unexpected}"
            )

    if duplicate_values := duplicates(mapped_styler_ids):
        findings.append(f"Multiple Mermaid animated families map to the same styler family: {duplicate_values}")
    missing_animated_families = sorted(set(styler_ids) - set(mapped_styler_ids))
    unexpected_animated_families = sorted(set(mapped_styler_ids) - set(styler_ids))
    if missing_animated_families:
        findings.append(f"Mermaid animated coverage misses styler families: {missing_animated_families}")
    if unexpected_animated_families:
        findings.append(f"Mermaid animated coverage has unexpected styler families: {unexpected_animated_families}")

    return {
        "version": MERMAID_VERSION,
        "familyCount": len(styler_families),
        "animatedFamilyCount": len(set(mapped_styler_ids)),
        "familyCoveragePercent": round(100.0 * len(set(mapped_styler_ids)) / MERMAID_FAMILY_COUNT, 2),
        "currentDeclarationCount": len(current_declarations),
        "renderableDeclarationCount": len(renderable_declarations),
        "classDefFamilyCount": len(classdef_families),
    }, findings


def validate_plantuml_taxonomy() -> tuple[dict[str, Any], list[str]]:
    findings: list[str] = []
    manifest = load_json(PLANTUML / "references" / "diagram-types.json")
    require_equal(findings, "PlantUML version", manifest.get("baseline", {}).get("version"), PLANTUML_VERSION)

    families = manifest.get("families")
    if not isinstance(families, list) or not all(isinstance(family, dict) for family in families):
        return {}, findings + ["PlantUML families must be a list of objects"]
    family_ids = [str(family.get("id")) for family in families]
    if duplicate_ids := duplicates(family_ids):
        findings.append(f"PlantUML has duplicate family ids: {duplicate_ids}")

    canonical = [family for family in families if family.get("taxonomy") == "canonical"]
    release_extras = [family for family in families if family.get("taxonomy") == "release-extra"]
    available = [family for family in families if family.get("availability") == "available"]
    unavailable = [family for family in families if family.get("availability") == "upstream-unavailable"]
    fixtures = [fixture for family in families for fixture in family.get("fixtures", [])]
    published = [fixture for fixture in fixtures if fixture.get("publication", {}).get("enabled") is True]
    fixture_ids = [str(fixture.get("id")) for fixture in fixtures]

    require_equal(findings, "PlantUML canonical family count", len(canonical), PLANTUML_CANONICAL_FAMILY_COUNT)
    require_equal(findings, "PlantUML release-extra family count", len(release_extras), PLANTUML_RELEASE_EXTRA_FAMILY_COUNT)
    require_equal(findings, "PlantUML tracked family count", len(families), PLANTUML_TRACKED_FAMILY_COUNT)
    require_equal(findings, "PlantUML available family count", len(available), PLANTUML_AVAILABLE_FAMILY_COUNT)
    require_equal(findings, "PlantUML fixture count", len(fixtures), PLANTUML_FIXTURE_COUNT)
    require_equal(findings, "PlantUML published fixture count", len(published), PLANTUML_PUBLISHED_FIXTURE_COUNT)
    require_exact_set(
        findings,
        "PlantUML canonical family identities",
        [str(family.get("id")) for family in canonical],
        PLANTUML_CANONICAL_FAMILIES,
    )
    require_exact_set(
        findings,
        "PlantUML release-extra family identities",
        [str(family.get("id")) for family in release_extras],
        PLANTUML_RELEASE_EXTRA_FAMILIES,
    )
    require_exact_set(findings, "PlantUML fixture identities", fixture_ids, PLANTUML_FIXTURES)
    require_exact_set(
        findings,
        "PlantUML published fixture identities",
        [str(fixture.get("id")) for fixture in published],
        PLANTUML_FIXTURES - {"chronology"},
    )
    require_equal(findings, "PlantUML upstream-unavailable ids", {family.get("id") for family in unavailable}, {"chronology"})

    available_without_publication = sorted(
        str(family.get("id"))
        for family in available
        if not any(fixture.get("publication", {}).get("enabled") is True for fixture in family.get("fixtures", []))
    )
    if available_without_publication:
        findings.append(f"PlantUML available families without published fixtures: {available_without_publication}")
    incorrectly_published_unavailable = sorted(
        str(family.get("id"))
        for family in unavailable
        if any(fixture.get("publication", {}).get("enabled") is True for fixture in family.get("fixtures", []))
    )
    if incorrectly_published_unavailable:
        findings.append(f"PlantUML upstream-unavailable families are published: {incorrectly_published_unavailable}")

    return {
        "version": PLANTUML_VERSION,
        "canonicalFamilyCount": len(canonical),
        "releaseExtraFamilyCount": len(release_extras),
        "trackedFamilyCount": len(families),
        "trackedFamilyCoveragePercent": round(100.0 * len(families) / PLANTUML_TRACKED_FAMILY_COUNT, 2),
        "availableFamilyCount": len(available),
        "availableFamilyCoveragePercent": round(100.0 * (len(available) - len(available_without_publication)) / PLANTUML_AVAILABLE_FAMILY_COUNT, 2),
        "upstreamUnavailableFamilies": sorted(str(family.get("id")) for family in unavailable),
        "fixtureCount": len(fixtures),
        "publishedFixtureCount": len(published),
    }, findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate exact Mermaid and PlantUML diagram-type coverage.")
    parser.add_argument("--report", type=Path, help="Write the combined coverage report as JSON.")
    parser.add_argument(
        "--disable-mermaid-browser-sandbox",
        action="store_true",
        help="Disable Chromium's sandbox only for trusted Mermaid CI fixtures.",
    )
    args = parser.parse_args()

    findings: list[str] = []
    mermaid, taxonomy_findings = validate_mermaid_taxonomies()
    findings.extend(taxonomy_findings)
    plantuml, taxonomy_findings = validate_plantuml_taxonomy()
    findings.extend(taxonomy_findings)

    checks: list[dict[str, Any]] = []
    mermaid_render_command = [
        sys.executable,
        str(MERMAID_STYLER / "scripts" / "validate_mermaid_render_coverage.py"),
    ]
    if args.disable_mermaid_browser_sandbox:
        mermaid_render_command.append("--disable-browser-sandbox")

    commands = [
        (
            "Mermaid colorset exact coverage",
            [sys.executable, str(MERMAID_STYLER / "scripts" / "test_style_mermaid_directory.py")],
        ),
        (
            "Mermaid animated family coverage",
            [sys.executable, str(MERMAID_ANIMATED / "scripts" / "validate_mermaid_family_coverage.py")],
        ),
        (
            "Mermaid fresh batch render coverage",
            mermaid_render_command,
        ),
        (
            "PlantUML fixture, render-report, and gallery coverage",
            [
                sys.executable,
                str(PLANTUML / "scripts" / "validate_plantuml_coverage.py"),
                "--fixtures",
                str(PLANTUML / "assets" / "examples" / "base"),
                "--report",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer" / "render-report.json"),
                "--report",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer-cs1" / "render-report.json"),
                "--gallery",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer"),
                "--gallery",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer-cs1"),
            ],
        ),
        (
            "PlantUML coverage unit tests",
            [sys.executable, str(PLANTUML / "scripts" / "test_plantuml_coverage.py")],
        ),
        (
            "PlantUML colorset2 artifact validation",
            [
                sys.executable,
                str(PLANTUML / "scripts" / "validate_plantuml_render_report.py"),
                "--report",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer" / "render-report.json"),
                "--output",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer"),
                "--colorset",
                "colorset2",
                "--coverage-manifest",
                str(PLANTUML / "references" / "diagram-types.json"),
            ],
        ),
        (
            "PlantUML colorset1 artifact validation",
            [
                sys.executable,
                str(PLANTUML / "scripts" / "validate_plantuml_render_report.py"),
                "--report",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer-cs1" / "render-report.json"),
                "--output",
                str(PLANTUML / "assets" / "examples" / "plantuml-colorset-renderer-cs1"),
                "--colorset",
                "colorset1",
                "--coverage-manifest",
                str(PLANTUML / "references" / "diagram-types.json"),
            ],
        ),
    ]
    for name, command in commands:
        record, check_findings = run_check(name, command)
        checks.append(record)
        findings.extend(check_findings)

    result = {
        "ok": not findings and all(check["ok"] for check in checks),
        "mermaid": mermaid,
        "plantuml": plantuml,
        "checks": checks,
        "findings": findings,
    }
    if args.report:
        report_path = args.report if args.report.is_absolute() else ROOT / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

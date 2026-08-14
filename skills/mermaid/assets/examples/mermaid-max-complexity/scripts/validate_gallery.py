#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate the published Mermaid maximum-complexity gallery."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


GALLERY_DIR = Path(__file__).resolve().parents[1]
SKILL_DIR = Path(__file__).resolve().parents[4]
EXPECTED_FAMILIES = 31
EXPECTED_PATTERNS = 62
EXPECTED_OUTPUTS = 124
EXPECTED_FINITE_CASES = 25
EXPECTED_FINITE_SLOTS = 200
ID_RE = re.compile(r"^mermaid-[a-z0-9]+(?:-[a-z0-9]+)*-(?:cs1|cs2)$")
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")
GEOMETRY_TAGS = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def normalized_text(root: ET.Element) -> list[str]:
    ignored = {"style", "title", "desc", "metadata"}
    values: list[str] = []
    for element in root.iter():
        if local_name(element.tag) in ignored or list(element):
            continue
        text = " ".join("".join(element.itertext()).split())
        if text:
            values.append(text)
    return values


def geometry_counts(root: ET.Element) -> Counter[str]:
    return Counter(local_name(element.tag) for element in root.iter() if local_name(element.tag) in GEOMETRY_TAGS)


def direct_child(root: ET.Element, name: str) -> ET.Element | None:
    return next((child for child in root if local_name(child.tag) == name), None)


def validate_svg(path: Path, *, animated: bool, findings: list[str]) -> ET.Element | None:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: invalid SVG XML: {error}")
        return None
    if local_name(root.tag) != "svg":
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: root element is not svg")
        return root
    serialized = path.read_text(encoding="utf-8", errors="replace")
    if "Syntax error in text" in serialized or "mermaid-error" in serialized:
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: contains a Mermaid error marker")

    title = direct_child(root, "title")
    description = direct_child(root, "desc")
    if title is None or not " ".join(title.itertext()).strip():
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing a non-empty direct title")
    if description is None or not " ".join(description.itertext()).strip():
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing a non-empty direct description")

    ids = [element.get("id") for element in root.iter() if element.get("id")]
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        findings.append(
            f"{path.relative_to(GALLERY_DIR).as_posix()}: duplicate SVG IDs: {', '.join(duplicates[:5])}"
        )
    id_set = set(ids)
    for attribute in ("aria-labelledby", "aria-describedby"):
        references = root.get(attribute, "").split()
        if not references:
            findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: root is missing {attribute}")
        missing = [reference for reference in references if reference not in id_set]
        if missing:
            findings.append(
                f"{path.relative_to(GALLERY_DIR).as_posix()}: unresolved {attribute}: {', '.join(missing)}"
            )

    if animated:
        if root.get("data-animated-mermaid") != "true":
            findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing animated Mermaid marker")
        if "animated-mermaid-style" not in serialized:
            findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing animation CSS")
        if "prefers-reduced-motion" not in serialized:
            findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing reduced-motion fallback")
    return root


def validate_source(
    path: Path,
    colorset: str,
    declaration: str,
    accessibility_mode: str,
    findings: list[str],
) -> None:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: could not read source: {error}")
        return
    required = (
        'theme: "base"',
        f'colorset: "{colorset}"',
    )
    for token in required:
        if token not in content:
            findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing {token}")
    if "%%{init:" in content:
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: contains a generated JSON init directive")
    has_accessibility_directives = "accTitle:" in content and "accDescr:" in content
    if accessibility_mode == "source-directives" and not has_accessibility_directives:
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: missing source accessibility directives")
    elif accessibility_mode == "rendered-svg-fallback" and (
        "accTitle:" in content or "accDescr:" in content
    ):
        findings.append(
            f"{path.relative_to(GALLERY_DIR).as_posix()}: fallback grammar must not contain rejected directives"
        )
    elif accessibility_mode not in {"source-directives", "rendered-svg-fallback"}:
        findings.append(f"{path.relative_to(GALLERY_DIR).as_posix()}: unknown accessibility mode")
    declaration_re = re.compile(rf"^\s*{re.escape(declaration)}(?:\s|$)", re.MULTILINE)
    if not declaration_re.search(content):
        findings.append(
            f"{path.relative_to(GALLERY_DIR).as_posix()}: expected declaration {declaration!r} was not found"
        )


def validate(root: Path) -> tuple[list[str], dict[str, object]]:
    findings: list[str] = []
    manifest_path = root / "gallery.json"
    catalog_path = root / "catalog.json"
    taxonomy_path = SKILL_DIR / "references" / "diagram-types.json"
    try:
        manifest = load_json(manifest_path)
        catalog = load_json(catalog_path)
        taxonomy = load_json(taxonomy_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [f"could not load gallery contract: {error}"], {}

    expected_scalars = {
        "familyCount": EXPECTED_FAMILIES,
        "patternCount": EXPECTED_PATTERNS,
        "outputCount": EXPECTED_OUTPUTS,
        "finiteCapacityCaseCount": EXPECTED_FINITE_CASES,
        "finiteCapacitySlots": EXPECTED_FINITE_SLOTS,
    }
    for field, expected in expected_scalars.items():
        if manifest.get(field) != expected:
            findings.append(f"gallery.json: {field} must be {expected}, found {manifest.get(field)!r}")

    families = manifest.get("families")
    patterns = manifest.get("patterns")
    catalog_families = catalog.get("families")
    taxonomy_families = taxonomy.get("families")
    if not isinstance(families, list) or not isinstance(patterns, list):
        return findings + ["gallery.json must contain families and patterns lists"], {}
    if not isinstance(catalog_families, list) or not isinstance(taxonomy_families, list):
        return findings + ["catalog and taxonomy must contain families lists"], {}

    family_ids = [str(item.get("familyId", "")) for item in families if isinstance(item, dict)]
    taxonomy_ids = [str(item.get("id", "")) for item in taxonomy_families if isinstance(item, dict)]
    catalog_ids = [str(item.get("familyId", "")) for item in catalog_families if isinstance(item, dict)]
    if family_ids != taxonomy_ids or family_ids != catalog_ids:
        findings.append("family order must match catalog.json and references/diagram-types.json exactly")
    if len(family_ids) != EXPECTED_FAMILIES or len(set(family_ids)) != EXPECTED_FAMILIES:
        findings.append(f"expected {EXPECTED_FAMILIES} unique family IDs, found {len(set(family_ids))}")

    family_by_id = {str(item["familyId"]): item for item in families if isinstance(item, dict) and "familyId" in item}
    observed_ids: list[str] = []
    variant_pairs: Counter[str] = Counter()
    checked_pairs = 0
    color_counts: dict[str, list[int]] = {"colorset1": [], "colorset2": []}
    for raw_pattern in patterns:
        if not isinstance(raw_pattern, dict):
            findings.append("gallery.json pattern entries must be objects")
            continue
        pattern_id = raw_pattern.get("id")
        family_id = raw_pattern.get("familyId")
        variant = raw_pattern.get("variant")
        colorset = raw_pattern.get("colorset")
        if not isinstance(pattern_id, str) or not ID_RE.fullmatch(pattern_id):
            findings.append(f"invalid Mermaid pattern ID: {pattern_id!r}")
            continue
        observed_ids.append(pattern_id)
        if family_id not in family_by_id:
            findings.append(f"{pattern_id}: unknown family ID {family_id!r}")
            continue
        expected_colorset = "colorset1" if variant == "cs1" else "colorset2" if variant == "cs2" else None
        if colorset != expected_colorset:
            findings.append(f"{pattern_id}: variant and colorset do not agree")
        variant_pairs[str(family_id)] += 1
        family = family_by_id[str(family_id)]

        source = root / str(raw_pattern.get("source", ""))
        static_svg = root / str(raw_pattern.get("staticSvg", ""))
        animated_svg = root / str(raw_pattern.get("animatedSvg", ""))
        for path, hash_field in (
            (source, "sourceSha256"),
            (static_svg, "staticSha256"),
            (animated_svg, "animatedSha256"),
        ):
            if not path.is_file() or path.stat().st_size == 0:
                findings.append(f"{pattern_id}: missing or empty {path.relative_to(root).as_posix()}")
            elif sha256(path) != raw_pattern.get(hash_field):
                findings.append(f"{pattern_id}: {hash_field} does not match {path.relative_to(root).as_posix()}")
        if not source.is_file() or not static_svg.is_file() or not animated_svg.is_file():
            continue

        validate_source(
            source,
            str(colorset),
            str(family.get("declaration", "")),
            str(family.get("accessibilityMode", "source-directives")),
            findings,
        )
        static_root = validate_svg(static_svg, animated=False, findings=findings)
        animated_root = validate_svg(animated_svg, animated=True, findings=findings)
        if static_root is not None and animated_root is not None:
            checked_pairs += 1
            if static_root.get("viewBox") != animated_root.get("viewBox"):
                findings.append(f"{pattern_id}: animated and static viewBox values differ")
            if normalized_text(static_root) != normalized_text(animated_root):
                findings.append(f"{pattern_id}: animated and static visible text differs")
            if geometry_counts(static_root) != geometry_counts(animated_root):
                findings.append(f"{pattern_id}: animated and static geometry counts differ")
        color_counts[str(colorset)].append(len(set(HEX_RE.findall(static_svg.read_text(encoding="utf-8")))))

    if len(observed_ids) != EXPECTED_PATTERNS or len(set(observed_ids)) != EXPECTED_PATTERNS:
        findings.append(f"expected {EXPECTED_PATTERNS} unique pattern IDs, found {len(set(observed_ids))}")
    wrong_pairs = sorted(family_id for family_id, count in variant_pairs.items() if count != 2)
    if wrong_pairs:
        findings.append(f"every family must have two variants: {', '.join(wrong_pairs)}")

    source_files = sorted((root / "source").rglob("*.mmd"))
    static_files = sorted((root / "svg").rglob("*.static.svg"))
    animated_files = sorted((root / "svg").rglob("*.animated.svg"))
    if len(source_files) != EXPECTED_PATTERNS:
        findings.append(f"expected {EXPECTED_PATTERNS} generated sources, found {len(source_files)}")
    if len(static_files) != EXPECTED_PATTERNS:
        findings.append(f"expected {EXPECTED_PATTERNS} static SVGs, found {len(static_files)}")
    if len(animated_files) != EXPECTED_PATTERNS:
        findings.append(f"expected {EXPECTED_PATTERNS} animated SVGs, found {len(animated_files)}")

    for required_path in (root / "index.html", root / "gallery.css", root / "gallery.js"):
        if not required_path.is_file() or required_path.stat().st_size == 0:
            findings.append(f"missing gallery page asset: {required_path.relative_to(root).as_posix()}")

    stats: dict[str, object] = {
        "ok": not findings,
        "familyCount": len(family_ids),
        "patternCount": len(observed_ids),
        "checkedStaticAnimatedPairs": checked_pairs,
        "sourceCount": len(source_files),
        "staticSvgCount": len(static_files),
        "animatedSvgCount": len(animated_files),
        "minimumColorset1SvgColors": min(color_counts["colorset1"], default=0),
        "minimumColorset2SvgColors": min(color_counts["colorset2"], default=0),
        "findings": findings,
    }
    return findings, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the Mermaid maximum-complexity gallery.")
    parser.add_argument("--root", type=Path, default=GALLERY_DIR, help="Gallery root to validate.")
    parser.add_argument("--report", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()
    root = args.root.resolve()
    findings, stats = validate(root)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(stats, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())

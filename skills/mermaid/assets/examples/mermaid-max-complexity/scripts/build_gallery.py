#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Build the published Mermaid maximum-complexity gallery."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


GALLERY_DIR = Path(__file__).resolve().parents[1]
SKILL_DIR = Path(__file__).resolve().parents[4]
CAPACITY_DIR = GALLERY_DIR.parent / "mermaid-max-elements"
CAPACITY_MANIFEST = CAPACITY_DIR / "manifest.json"
CATALOG_PATH = GALLERY_DIR / "catalog.json"
DIAGRAM_TYPES_PATH = SKILL_DIR / "references" / "diagram-types.json"
STYLE_SCRIPT = SKILL_DIR / "scripts" / "style_mermaid_directory.py"
ANIMATE_SCRIPT = SKILL_DIR / "scripts" / "animate_mermaid_svg.py"
COLORSETS = (("colorset1", "cs1"), ("colorset2", "cs2"))
ACCESSIBILITY_MODES = {"source-directives", "rendered-svg-fallback"}


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


def ensure_within_gallery(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(GALLERY_DIR.resolve()):
        raise ValueError(f"Refusing to modify a path outside the gallery: {resolved}")
    return resolved


def reset_directory(path: Path) -> None:
    target = ensure_within_gallery(path)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)


def run(command: list[str], *, cwd: Path = GALLERY_DIR) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        details = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
        raise RuntimeError(f"Command failed ({completed.returncode}): {' '.join(command)}\n{details}")


def normalize_text_file(path: Path) -> None:
    """Use LF, strip line-end whitespace, and keep exactly one final newline."""

    lines = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def inject_accessibility(source: str, title: str, description: str) -> str:
    lines = source.strip().splitlines()
    declaration_index = next((index for index, line in enumerate(lines) if line.strip()), None)
    if declaration_index is None:
        raise ValueError("Mermaid source is empty")
    if any("accTitle:" in line or "accDescr" in line for line in lines):
        raise ValueError("Base source must not contain accessibility directives")
    directives = [f"  accTitle: {title}", f"  accDescr: {description}"]
    return "\n".join(lines[: declaration_index + 1] + directives + lines[declaration_index + 1 :]) + "\n"


def inject_svg_accessibility(path: Path, title: str, description: str, metadata_key: str) -> None:
    """Ensure direct SVG metadata even when a Mermaid renderer omits source directives."""

    content = path.read_text(encoding="utf-8")
    import xml.etree.ElementTree as ET

    root = ET.fromstring(content)
    direct_title = next((child for child in root if child.tag.rsplit("}", 1)[-1] == "title"), None)
    direct_description = next((child for child in root if child.tag.rsplit("}", 1)[-1] == "desc"), None)
    opening_match = re.search(r"<svg\b[^>]*>", content, flags=re.IGNORECASE)
    if opening_match is None:
        raise ValueError(f"Rendered output has no SVG root: {path}")
    opening = opening_match.group(0)
    safe_key = re.sub(r"[^a-z0-9-]+", "-", metadata_key.lower()).strip("-")
    title_id = f"{safe_key}-title"
    description_id = f"{safe_key}-desc"

    def set_attribute(markup: str, name: str, value: str) -> str:
        attribute_re = re.compile(rf"\s{re.escape(name)}=(?:\"[^\"]*\"|'[^']*')", re.IGNORECASE)
        replacement = f' {name}="{html.escape(value, quote=True)}"'
        if attribute_re.search(markup):
            return attribute_re.sub(replacement, markup, count=1)
        return markup[:-1] + replacement + ">"

    existing_title_id = direct_title.get("id") if direct_title is not None else None
    existing_description_id = direct_description.get("id") if direct_description is not None else None
    has_title = direct_title is not None and bool(" ".join(direct_title.itertext()).strip()) and existing_title_id
    has_description = (
        direct_description is not None
        and bool(" ".join(direct_description.itertext()).strip())
        and existing_description_id
    )
    if has_title:
        title_id = str(existing_title_id)
    if has_description:
        description_id = str(existing_description_id)

    if not root.get("role"):
        opening = set_attribute(opening, "role", "img")
    opening = set_attribute(opening, "aria-labelledby", title_id)
    opening = set_attribute(opening, "aria-describedby", description_id)
    metadata = ""
    if not has_title:
        metadata += f'<title id="{title_id}">{html.escape(title)}</title>'
    if not has_description:
        metadata += f'<desc id="{description_id}">{html.escape(description)}</desc>'
    content = content[: opening_match.start()] + opening + metadata + content[opening_match.end() :]
    path.write_text(content, encoding="utf-8", newline="\n")

    # Fail immediately if the minimal metadata patch damaged the renderer output.
    ET.parse(path)


def normalize_duplicate_svg_ids(path: Path) -> None:
    """Rename later duplicate IDs while preserving the renderer's first-reference behavior."""

    content = path.read_text(encoding="utf-8")
    id_pattern = re.compile(r"\bid=(?P<quote>[\"'])(?P<value>[^\"']+)(?P=quote)")
    seen: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        value = match.group("value")
        seen[value] = seen.get(value, 0) + 1
        if seen[value] == 1:
            return match.group(0)
        replacement = f"{value}-duplicate-{seen[value]}"
        return f'id={match.group("quote")}{replacement}{match.group("quote")}'

    normalized = id_pattern.sub(replace, content)
    if normalized != content:
        path.write_text(normalized, encoding="utf-8", newline="\n")

    import xml.etree.ElementTree as ET

    root = ET.parse(path).getroot()
    ids = [element.get("id") for element in root.iter() if element.get("id")]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate SVG IDs remain after normalization: {path}")


def capacity_sources(manifest: dict[str, object]) -> dict[str, str]:
    raw_sources = manifest.get("sources")
    if not isinstance(raw_sources, dict):
        raise ValueError("Capacity manifest must contain a sources object")
    sources: dict[str, str] = {}
    for key, value in raw_sources.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("Capacity manifest source entries must map strings to strings")
        sources[key] = value
    return sources


def family_contracts(manifest: dict[str, object]) -> dict[str, dict[str, object]]:
    raw_families = manifest.get("families")
    if not isinstance(raw_families, list):
        raise ValueError("Capacity manifest must contain a families list")
    contracts: dict[str, dict[str, object]] = {}
    for item in raw_families:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Capacity family entries must be objects with string IDs")
        contracts[str(item["id"])] = item
    return contracts


def taxonomy_families(taxonomy: dict[str, object]) -> dict[str, dict[str, object]]:
    raw_families = taxonomy.get("families")
    if not isinstance(raw_families, list):
        raise ValueError("Diagram taxonomy must contain a families list")
    result: dict[str, dict[str, object]] = {}
    for item in raw_families:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Diagram taxonomy entries must be objects with string IDs")
        result[str(item["id"])] = item
    return result


def base_source(
    entry: dict[str, object],
    contract: dict[str, object],
    sources: dict[str, str],
) -> str:
    override = entry.get("sourceOverride")
    if override is not None:
        if not isinstance(override, str):
            raise ValueError(f"sourceOverride must be a string for {entry.get('familyId')}")
        override_path = ensure_within_gallery(GALLERY_DIR / override)
        return override_path.read_text(encoding="utf-8")
    source_key = contract.get("source")
    if not isinstance(source_key, str) or source_key not in sources:
        raise ValueError(f"Missing capacity source for {entry.get('familyId')}")
    return sources[source_key]


def style_sources(source_root: Path, colorset: str, report_root: Path) -> None:
    write_report = report_root / f"{colorset}-style.json"
    check_report = report_root / f"{colorset}-check.json"
    command = ["uv", "run", "--script", str(STYLE_SCRIPT), str(source_root), "--write", "--report", str(write_report)]
    if colorset == "colorset2":
        command.extend(["--colorset", "colorset2"])
    run(command)
    for source_path in source_root.rglob("*.mmd"):
        normalize_text_file(source_path)
    check_command = [
        "uv",
        "run",
        "--script",
        str(STYLE_SCRIPT),
        str(source_root),
        "--check",
        "--report",
        str(check_report),
    ]
    if colorset == "colorset2":
        check_command.extend(["--colorset", "colorset2"])
    run(check_command)
    normalize_text_file(write_report)
    normalize_text_file(check_report)


def render_one(
    source: Path,
    static_svg: Path,
    animated_svg: Path,
    title: str,
    description: str,
    accessibility_mode: str,
    metadata_key: str,
) -> None:
    run(
        [
            "uv",
            "run",
            "--script",
            str(ANIMATE_SCRIPT),
            str(source),
            "-o",
            str(animated_svg),
            "--static-output",
            str(static_svg),
            "--animation",
            "auto",
            "--duration-ms",
            "480",
            "--stagger-ms",
            "65",
            "--initial-delay-ms",
            "100",
        ]
    )
    for path in (static_svg, animated_svg):
        inject_svg_accessibility(path, title, description, metadata_key)
        normalize_duplicate_svg_ids(path)
        normalize_text_file(path)


def build(*, jobs: int) -> dict[str, object]:
    catalog = load_json(CATALOG_PATH)
    capacity = load_json(CAPACITY_MANIFEST)
    taxonomy = load_json(DIAGRAM_TYPES_PATH)
    entries = catalog.get("families")
    if not isinstance(entries, list):
        raise ValueError("Gallery catalog must contain a families list")

    sources = capacity_sources(capacity)
    contracts = family_contracts(capacity)
    taxonomy_by_id = taxonomy_families(taxonomy)
    source_root = GALLERY_DIR / "source"
    svg_root = GALLERY_DIR / "svg"
    report_root = GALLERY_DIR / "reports"
    reset_directory(source_root)
    reset_directory(svg_root)
    reset_directory(report_root)

    prepared_entries: list[dict[str, object]] = []
    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            raise ValueError("Gallery family entries must be objects")
        entry = dict(raw_entry)
        family_id = entry.get("familyId")
        slug = entry.get("slug")
        if not isinstance(family_id, str) or not isinstance(slug, str):
            raise ValueError("Every gallery family requires familyId and slug strings")
        contract = contracts.get(family_id)
        family_taxonomy = taxonomy_by_id.get(family_id)
        if contract is None or family_taxonomy is None:
            raise ValueError(f"Unknown Mermaid family in gallery catalog: {family_id}")
        source = base_source(entry, contract, sources)
        title = f"{entry['label']} maximum complexity showcase"
        description = str(entry["accessibleDescription"])
        accessibility_mode = str(entry.get("accessibilityMode", "source-directives"))
        if accessibility_mode not in ACCESSIBILITY_MODES:
            raise ValueError(f"Unsupported accessibility mode for {family_id}: {accessibility_mode}")
        accessible_source = (
            inject_accessibility(source, title, description)
            if accessibility_mode == "source-directives"
            else source.strip() + "\n"
        )
        for colorset, _suffix in COLORSETS:
            destination = source_root / colorset / f"{slug}.mmd"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(accessible_source, encoding="utf-8", newline="\n")

        entry.update(
            {
                "capacityKind": contract.get("capacityKind"),
                "maxSlots": contract.get("maxSlots"),
                "fixtureElementCount": contract.get("fixtureElementCount"),
                "currentDeclarations": family_taxonomy.get("currentDeclarations", []),
                "acceptedDeclarations": family_taxonomy.get("acceptedDeclarations", []),
                "accessibleTitle": title,
                "accessibilityMode": accessibility_mode,
            }
        )
        prepared_entries.append(entry)

    for colorset, _suffix in COLORSETS:
        style_sources(source_root / colorset, colorset, report_root)

    render_jobs: list[tuple[Path, Path, Path, str, str, str, str]] = []
    for entry in prepared_entries:
        slug = str(entry["slug"])
        for colorset, _suffix in COLORSETS:
            output_dir = svg_root / colorset
            output_dir.mkdir(parents=True, exist_ok=True)
            render_jobs.append(
                (
                    source_root / colorset / f"{slug}.mmd",
                    output_dir / f"{slug}.static.svg",
                    output_dir / f"{slug}.animated.svg",
                    str(entry["accessibleTitle"]),
                    str(entry["accessibleDescription"]),
                    str(entry["accessibilityMode"]),
                    f"mermaid-{slug}-{colorset}",
                )
            )

    failures: list[str] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        future_map = {
            executor.submit(render_one, *render_job): render_job[0]
            for render_job in render_jobs
        }
        for future in concurrent.futures.as_completed(future_map):
            source = future_map[future]
            try:
                future.result()
                print(f"Rendered {source.relative_to(GALLERY_DIR).as_posix()}")
            except Exception as error:  # noqa: BLE001 - aggregate all deterministic render failures
                failures.append(f"{source.relative_to(GALLERY_DIR).as_posix()}: {error}")
    if failures:
        raise RuntimeError("Gallery rendering failed:\n- " + "\n- ".join(sorted(failures)))

    patterns: list[dict[str, object]] = []
    for entry in prepared_entries:
        slug = str(entry["slug"])
        family_id = str(entry["familyId"])
        for colorset, suffix in COLORSETS:
            source_path = source_root / colorset / f"{slug}.mmd"
            static_path = svg_root / colorset / f"{slug}.static.svg"
            animated_path = svg_root / colorset / f"{slug}.animated.svg"
            patterns.append(
                {
                    "id": f"mermaid-{slug}-{suffix}",
                    "familyId": family_id,
                    "colorset": colorset,
                    "variant": suffix,
                    "source": source_path.relative_to(GALLERY_DIR).as_posix(),
                    "staticSvg": static_path.relative_to(GALLERY_DIR).as_posix(),
                    "animatedSvg": animated_path.relative_to(GALLERY_DIR).as_posix(),
                    "sourceSha256": sha256(source_path),
                    "staticSha256": sha256(static_path),
                    "animatedSha256": sha256(animated_path),
                }
            )

    finite_contracts = [entry for entry in prepared_entries if entry.get("maxSlots") is not None]
    gallery_manifest: dict[str, object] = {
        "schemaVersion": 1,
        "namespace": "mermaid",
        "exampleSetId": catalog.get("exampleSetId"),
        "title": catalog.get("title"),
        "mermaidVersion": capacity.get("mermaidVersion"),
        "familyCount": len(prepared_entries),
        "patternCount": len(patterns),
        "outputCount": len(patterns) * 2,
        "finiteCapacityCaseCount": len(finite_contracts),
        "finiteCapacitySlots": sum(int(entry["maxSlots"]) for entry in finite_contracts),
        "colorsets": [colorset for colorset, _suffix in COLORSETS],
        "families": prepared_entries,
        "patterns": patterns,
    }
    manifest_path = GALLERY_DIR / "gallery.json"
    manifest_path.write_text(json.dumps(gallery_manifest, indent=2) + "\n", encoding="utf-8", newline="\n")

    report = {
        "ok": True,
        "familyCount": len(prepared_entries),
        "patternCount": len(patterns),
        "sourceCount": len(patterns),
        "staticSvgCount": len(patterns),
        "animatedSvgCount": len(patterns),
        "finiteCapacityCaseCount": len(finite_contracts),
        "finiteCapacitySlots": gallery_manifest["finiteCapacitySlots"],
        "manifestSha256": sha256(manifest_path),
    }
    (report_root / "build-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Mermaid maximum-complexity gallery.")
    parser.add_argument("--jobs", type=int, default=2, help="Number of concurrent Mermaid render processes.")
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    try:
        report = build(jobs=args.jobs)
    except Exception as error:  # noqa: BLE001 - emit one user-facing failure
        print(f"Gallery build failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Consolidate small D3 recipes into anchored, independently routed collections."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys


@dataclass(frozen=True)
class Collection:
    filename: str
    title: str
    sources: tuple[str, ...]


COLLECTIONS = (
    Collection(
        "interaction-motion-collection.md",
        "Interaction and Motion Pattern Collection",
        (
            "shape-tween.md",
            "arc-tween.md",
            "path-tween.md",
            "text-tween.md",
            "brush-handles.md",
            "brush-snapping.md",
            "ordinal-brushing.md",
            "zoomable-bar.md",
            "xy-zoom.md",
            "versor-dragging.md",
            "you-draw-it.md",
        ),
    ),
    Collection(
        "science-geometry-collection.md",
        "Science and Geometry Pattern Collection",
        (
            "hr-diagram.md",
            "solar-path.md",
            "parabolic-arcs.md",
            "apollonius-circles.md",
            "tissot-indicatrix.md",
            "vector-field.md",
            "curve-contexts.md",
            "adaptive-sampling.md",
            "satellite-projection.md",
            "exoplanet-orbits.md",
            "epicyclic-gearing.md",
        ),
    ),
    Collection(
        "statistical-collection.md",
        "Statistical and Analytical Pattern Collection",
        (
            "qq-plot.md",
            "dot-plot.md",
            "boxplot.md",
            "ecdf.md",
            "bullet.md",
            "point-range.md",
            "barcode-plot.md",
            "facet-sparklines.md",
            "normalized-stacked-area.md",
            "moving-average.md",
            "variable-color-line.md",
        ),
    ),
)

PATTERN_ID = re.compile(r"(?m)^- \*\*Pattern ID:\*\* `(d3-[a-z0-9-]+)`\s*$")
HEADING = re.compile(r"^(#{1,4})(\s+.*)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path("skills/d3"))
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def nested_recipe(source: Path) -> tuple[str, str]:
    text = source.read_text(encoding="utf-8")
    match = PATTERN_ID.search(text)
    if not match:
        raise ValueError(f"Missing Pattern ID in {source}")
    pattern_id = match.group(1)
    if pattern_id != f"d3-{source.stem}":
        raise ValueError(f"Pattern ID and filename differ in {source}")
    lines = text.rstrip().splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError(f"Expected one top-level title in {source}")
    title = lines[0].removeprefix("# ")
    rendered = [f"## {pattern_id}", "", f"### {title}"]
    in_fence = False
    for line in lines[1:]:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            rendered.append(line)
            continue
        heading = HEADING.match(line) if not in_fence else None
        if heading:
            level = min(6, len(heading.group(1)) + 2)
            rendered.append("#" * level + heading.group(2))
        else:
            rendered.append(line)
    return pattern_id, "\n".join(rendered).rstrip() + "\n"


def applied_state_report(pattern_root: Path, index_text: str) -> dict[str, object] | None:
    targets = [pattern_root / collection.filename for collection in COLLECTIONS]
    sources = [
        pattern_root / filename
        for collection in COLLECTIONS
        for filename in collection.sources
    ]
    target_count = sum(path.is_file() for path in targets)
    source_count = sum(path.is_file() for path in sources)
    if target_count == 0 and source_count == len(sources):
        return None
    if target_count != len(targets) or source_count:
        raise ValueError(
            "Consolidation is partially applied: expected either all source recipes or "
            "all collections with no source recipes"
        )

    route_count = 0
    for collection, target in zip(COLLECTIONS, targets, strict=True):
        text = target.read_text(encoding="utf-8")
        for filename in collection.sources:
            pattern_id = f"d3-{Path(filename).stem}"
            route = f"references/patterns/{collection.filename}#{pattern_id}"
            if text.count(f"## {pattern_id}") != 1:
                raise ValueError(f"Collection route anchor is missing or duplicated: {route}")
            if index_text.count(route) != 1:
                raise ValueError(f"Index route is missing or duplicated: {route}")
            route_count += 1
    sizes = [path.stat().st_size for path in targets]
    return {
        "state": "already-applied",
        "collectionsPresent": len(targets),
        "sourceFilesRemaining": 0,
        "runtimeFileDelta": len(targets) - len(sources),
        "collectionBytes": sum(sizes),
        "largestCollectionBytes": max(sizes),
        "patternRoutesPreserved": route_count,
    }


def main() -> int:
    args = parse_args()
    skill_root = args.skill_root.resolve()
    pattern_root = skill_root / "references" / "patterns"
    index_path = skill_root / "references" / "pattern-index.md"
    index_text = index_path.read_text(encoding="utf-8")
    applied = applied_state_report(pattern_root, index_text)
    if applied is not None:
        print(json.dumps({"apply": args.apply, **applied}, indent=2, sort_keys=True))
        return 0
    markdown_paths = sorted(skill_root.rglob("*.md"))
    outputs: dict[Path, str] = {}
    replacements: list[tuple[str, str]] = []
    source_paths: list[Path] = []

    for collection in COLLECTIONS:
        target = pattern_root / collection.filename
        if target.exists():
            raise ValueError(f"Refusing existing collection: {target}")
        sections: list[str] = []
        for filename in collection.sources:
            source = pattern_root / filename
            if not source.is_file():
                raise ValueError(f"Missing source recipe: {source}")
            route = f"references/patterns/{filename}"
            references = [
                path
                for path in markdown_paths
                if route in path.read_text(encoding="utf-8", errors="replace")
            ]
            if references != [index_path]:
                relative_refs = [path.relative_to(skill_root).as_posix() for path in references]
                raise ValueError(f"Unexpected routes for {route}: {relative_refs}")
            if index_text.count(route) != 1:
                raise ValueError(f"Expected exactly one index route for {route}")
            pattern_id, section = nested_recipe(source)
            sections.append(section)
            replacements.append(
                (route, f"references/patterns/{collection.filename}#{pattern_id}")
            )
            source_paths.append(source)
        header = (
            f"# {collection.title}\n\n"
            "Use the pattern index to route directly to one section in this compact "
            "collection. Read only that section and any reference it explicitly names.\n\n"
        )
        outputs[target] = header + "\n".join(sections)

    updated_index = index_text
    for old, new in replacements:
        updated_index = updated_index.replace(old, new)
    if len(replacements) != 33 or len(source_paths) != len(set(source_paths)):
        raise ValueError("The consolidation plan must contain 33 unique source recipes")

    source_bytes = sum(path.stat().st_size for path in source_paths)
    collection_bytes = sum(len(text.encode("utf-8")) for text in outputs.values())
    report = {
        "apply": args.apply,
        "state": "applied" if args.apply else "planned",
        "collectionsAdded": len(outputs),
        "sourceFilesRemoved": len(source_paths),
        "runtimeFileDelta": len(outputs) - len(source_paths),
        "sourceBytes": source_bytes,
        "collectionBytes": collection_bytes,
        "byteDelta": collection_bytes - source_bytes,
        "largestCollectionBytes": max(len(text.encode("utf-8")) for text in outputs.values()),
        "patternRoutesPreserved": len(replacements),
    }
    if args.apply:
        for path, text in outputs.items():
            path.write_text(text, encoding="utf-8", newline="\n")
        index_path.write_text(updated_index, encoding="utf-8", newline="\n")
        for path in source_paths:
            path.unlink()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

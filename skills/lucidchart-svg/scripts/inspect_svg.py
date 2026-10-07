#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect SVG dependencies and geometry, or prepare a byte-preserving upload copy."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
MAX_BYTES = 50 * 1024 * 1024
VECTOR_TAGS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "use"}
UNITS = {"": 1, "px": 1, "pt": 96 / 72, "pc": 16, "in": 96, "cm": 96 / 2.54, "mm": 96 / 25.4, "q": 96 / 101.6}
URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I | re.S)


class SvgError(ValueError):
    pass


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def dimension(value: str | None) -> float | None:
    match = re.fullmatch(r"\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s*([a-z]*)\s*", value or "", re.I)
    if not match or match[2].lower() not in UNITS:
        return None
    result = float(match[1]) * UNITS[match[2].lower()]
    return result if math.isfinite(result) and result > 0 else None


def inspect(path: Path) -> tuple[bytes, dict]:
    if path.stat().st_size > MAX_BYTES:
        raise SvgError("SVG exceeds the 50 MiB inspection limit.")
    data = path.read_bytes()
    # Reject declarations before XML parsing; normal SVGs need neither DTDs nor entities.
    # XML may be UTF-16/32, so strip NUL padding for this declaration guard.
    declaration_bytes = data.replace(b"\x00", b"")
    if re.search(br"<!\s*(?:DOCTYPE|ENTITY)\b", declaration_bytes, re.I):
        raise SvgError("DTD/entity declarations are unsupported; preserve the original and obtain a declaration-free SVG.")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise SvgError("Input is not well-formed SVG XML.") from error
    if root.tag != f"{{{SVG_NS}}}svg":
        raise SvgError("Input must have an SVG root in the http://www.w3.org/2000/svg namespace.")
    view_box = None
    raw_box = root.get("viewBox")
    if raw_box is not None:
        try:
            view_box = [float(item) for item in re.split(r"[\s,]+", raw_box.strip())]
        except ValueError as error:
            raise SvgError("viewBox must contain four finite numbers.") from error
        if len(view_box) != 4 or not all(math.isfinite(item) for item in view_box) or min(view_box[2:]) <= 0:
            raise SvgError("viewBox must contain finite x, y, positive width, and positive height.")
    width = dimension(root.get("width"))
    height = dimension(root.get("height"))
    flags: set[str] = set()
    warnings: set[str] = set()
    dependencies: set[str] = set()
    fragments: set[str] = set()
    if re.search(br"<\?\s*xml-stylesheet\b", declaration_bytes, re.I):
        flags.add("external-stylesheet-instruction")
    ids: list[str] = []
    labels: list[str] = []
    tags: Counter[str] = Counter()
    embedded_raster = 0

    def check_resource(value: str) -> None:
        nonlocal embedded_raster
        value = value.strip()
        if value.startswith("#"):
            fragments.add(value[1:])
            return
        if not value:
            return
        if re.match(r"data:image/(?:png|jpeg|gif|webp);base64,", value, re.I):
            embedded_raster += 1
            warnings.add("embedded-raster-image")
        elif value.lower().startswith("data:"):
            flags.add("unsupported-data-resource")
        else:
            dependencies.add(value)
            flags.add("external-resource")

    for node in root.iter():
        tag = local_name(node.tag)
        tags[tag] += 1
        if node.get("id"):
            ids.append(node.get("id", ""))
        if tag == "text":
            labels.append("".join(node.itertext()).strip())
        if tag == "script":
            flags.add("script")
        if tag in {"foreignObject", "filter", "mask", "clipPath", "animate", "animateTransform", "animateMotion", "set"}:
            warnings.add(tag)
        if tag == "foreignObject":
            flags.add("foreignObject-needs-review")
        # Animation can mutate a harmless href into a remote/active URL after inspection.
        if tag in {"animate", "set"}:
            dynamic_key = local_name(node.get("attributeName", "")).lower()
            if dynamic_key in {"href", "src", "style"} or dynamic_key.startswith("on"):
                flags.add("dynamic-resource")
        for attribute, value in node.attrib.items():
            key = local_name(attribute)
            if key.lower().startswith("on"):
                flags.add("event-handler")
            if key.lower() in {"href", "src"}:
                check_resource(value)
            if key.lower() == "base":
                flags.add("external-base")
            if key.lower() == "style" or "url(" in value.lower():
                for match in URL_RE.finditer(value):
                    check_resource(match[2])
        if tag == "style" or node.get("style"):
            css = (node.text or "") if tag == "style" else node.get("style", "")
            if "\\" in css or "/*" in css:
                flags.add("css-needs-review")
            if re.search(r"@import\b|expression\s*\(", css, re.I):
                flags.add("active-css")
            for match in URL_RE.finditer(css):
                check_resource(match[2])
            if re.search(r"@font-face\b|font-family\s*:", css, re.I):
                warnings.add("font-dependency-review")
        if node.get("font-family"):
            warnings.add("font-dependency-review")
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicates:
        warnings.add("duplicate-ids")
    missing_fragments = sorted(fragments - set(ids))
    if missing_fragments:
        warnings.add("unresolved-fragment-references")
    has_geometry = view_box is not None or (width is not None and height is not None)
    if not has_geometry:
        flags.add("missing-usable-dimensions")
    report = {
        "schema_version": 1, "source": str(path), "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data), "valid_svg": True, "view_box": view_box,
        "width_px": width, "height_px": height, "element_counts": dict(sorted(tags.items())),
        "vector_element_count": sum(tags[tag] for tag in VECTOR_TAGS),
        "embedded_raster_resource_count": embedded_raster,
        "labels": labels, "ids": ids, "duplicate_ids": duplicates,
        "unresolved_fragment_references": missing_fragments,
        "external_resources": sorted(dependencies), "blocking_flags": sorted(flags),
        "portability_warnings": sorted(warnings), "ready_for_upload": not flags,
        "safe_to_render_offline": not flags,
        "native_editability": "unknown; SVG geometry is not a native graph contract",
    }
    return data, report


def save(path: Path, data: bytes, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb" if overwrite else "xb") as handle:
        handle.write(data)


def main() -> int:
    # Windows pipe encodings may default to cp1252 even for valid UTF-8 SVG labels.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect", "prepare"):
        item = sub.add_parser(command)
        item.add_argument("input", type=Path)
        item.add_argument("--report", type=Path)
        item.add_argument("--overwrite", action="store_true", help="Replace existing output/report files; never the source.")
        if command == "prepare":
            item.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        paths = [path.resolve() for path in [args.input, args.report, getattr(args, "output", None)] if path is not None]
        if len(paths) != len(set(paths)):
            raise SvgError("Source, output, and report paths must be distinct.")
        for path in [args.report, getattr(args, "output", None)]:
            if path and path.exists() and not args.overwrite:
                raise SvgError("An output already exists; choose a new path or use --overwrite.")
        data, report = inspect(args.input)
        if args.report:
            save(args.report, (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), args.overwrite)
        if args.command == "prepare":
            if not report["ready_for_upload"]:
                raise SvgError("SVG requires deliberate repair before upload: " + ", ".join(report["blocking_flags"]))
            save(args.output, data, args.overwrite)
            report["prepared_output"] = str(args.output)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, SvgError) as error:
        print(f"SVG inspection failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

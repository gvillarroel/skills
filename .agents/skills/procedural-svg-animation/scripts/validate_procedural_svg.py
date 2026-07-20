#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Validate standalone procedural SVG artifacts and their audit contract."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_ROOT / "assets" / "pattern-specs.json"
SVG_NS = "http://www.w3.org/2000/svg"
XML_NS = "http://www.w3.org/XML/1998/namespace"

REQUIRED_ROOT_METADATA = (
    "data-procedural-svg-version",
    "data-pattern-id",
    "data-example-id",
    "data-family",
    "data-renderer",
    "data-variant",
    "data-seed",
    "data-palette",
    "data-motion",
    "data-motion-engine",
    "data-duration-ms",
    "data-loop",
    "data-loop-contract",
    "data-reduced-motion-fallback",
    "data-driver",
    "data-technique",
    "data-deterministic",
    "data-standalone",
    "data-parameter-hash",
)
MOTION_TAGS = {"animate", "animateMotion", "animateTransform", "set"}
DRAWING_TAGS = {"circle", "ellipse", "line", "path", "polygon", "polyline", "rect", "text", "use"}
CSS_URL_START = re.compile(r"(?<![-_A-Za-z0-9])url\s*\(", re.IGNORECASE)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
NONFINITE = re.compile(r"(?<![A-Za-z])(?:nan|[-+]?inf(?:inity)?)(?![A-Za-z])", re.IGNORECASE)
PATTERN_ID = re.compile(r"procedural-svg-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
CLOCK_VALUE = re.compile(r"([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*(ms|s|min|h)?\Z", re.IGNORECASE)
CSS_TIME = re.compile(r"(?<![-_A-Za-z0-9.])([-+]?(?:\d+(?:\.\d*)?|\.\d+))\s*(ms|s)\b", re.IGNORECASE)
SVG_NUMBER = re.compile(r"[-+]?(?:(?:\d+(?:\.\d*)?)|(?:\.\d+))(?:[eE][-+]?\d+)?")
NUMERIC_GEOMETRY_ATTRIBUTES = {
    "x", "y", "x1", "y1", "x2", "y2", "cx", "cy", "r", "rx", "ry",
    "width", "height", "pathLength", "stroke-width", "opacity", "fill-opacity",
    "stroke-opacity", "stdDeviation", "scale", "surfaceScale", "specularConstant",
    "specularExponent", "z", "baseFrequency",
}


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def load_catalog() -> dict[str, dict[str, object]]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    entries = data.get("patterns")
    if not isinstance(entries, list):
        raise ValueError("Bundled pattern catalog is missing its patterns array.")
    result: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ValueError("Bundled pattern catalog contains an invalid entry.")
        result[str(entry["id"])] = entry
    return result


def parse_number(value: str, label: str, errors: list[str]) -> float | None:
    try:
        number = float(value)
    except ValueError:
        errors.append(f"{label} must be numeric; found {value!r}.")
        return None
    if not math.isfinite(number):
        errors.append(f"{label} must be finite; found {value!r}.")
        return None
    return number


def validate_finite_geometry(elements: list[ET.Element], errors: list[str]) -> None:
    """Parse serialized drawing numbers instead of relying only on NaN/Inf scanning."""

    for element_index, element in enumerate(elements):
        tag = local_name(element.tag)
        for raw_name, raw_value in element.attrib.items():
            name = local_name(raw_name)
            if name in NUMERIC_GEOMETRY_ATTRIBUTES:
                stripped = raw_value.replace(",", " ").replace("%", " ").replace("px", " ")
                tokens = stripped.split()
                if not tokens:
                    errors.append(f"<{tag}> #{element_index + 1} has empty numeric attribute {name!r}.")
                    continue
                for token in tokens:
                    if not SVG_NUMBER.fullmatch(token):
                        errors.append(
                            f"<{tag}> #{element_index + 1} has malformed numeric {name} value {raw_value!r}."
                        )
                        break
                    if not math.isfinite(float(token)):
                        errors.append(
                            f"<{tag}> #{element_index + 1} has non-finite numeric {name} value {raw_value!r}."
                        )
                        break
            elif name == "points":
                tokens = SVG_NUMBER.findall(raw_value)
                remainder = SVG_NUMBER.sub("", raw_value).replace(",", "").strip()
                if remainder or len(tokens) < 4 or len(tokens) % 2:
                    errors.append(f"<{tag}> #{element_index + 1} has malformed points data.")
            elif name == "d":
                remainder = SVG_NUMBER.sub("", raw_value)
                remainder = re.sub(r"[MmZzLlHhVvCcSsQqTtAa,\s]", "", remainder)
                if remainder:
                    errors.append(f"<{tag}> #{element_index + 1} has malformed path data near {remainder[:24]!r}.")


def clock_value_ms(value: str) -> float | None:
    match = CLOCK_VALUE.fullmatch(value.strip())
    if not match:
        return None
    number = float(match.group(1))
    unit = (match.group(2) or "s").lower()
    scale = {"ms": 1.0, "s": 1000.0, "min": 60000.0, "h": 3600000.0}[unit]
    return number * scale


def split_css_top_level(value: str) -> list[str]:
    """Split a CSS comma list without splitting function arguments or strings."""

    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif quote:
            if character == quote:
                quote = None
        elif character in {'"', "'"}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")" and depth:
            depth -= 1
        elif character == "," and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    parts.append(value[start:].strip())
    return [part for part in parts if part]


def normalized_animation_value(value: str) -> str:
    return " ".join(value.replace(",", " ").split())


def rotation_endpoints_close(start: str, finish: str) -> bool:
    try:
        first = [float(value) for value in normalized_animation_value(start).split()]
        last = [float(value) for value in normalized_animation_value(finish).split()]
    except ValueError:
        return False
    if not first or len(first) != len(last):
        return False
    if any(not math.isclose(a, b, rel_tol=0.0, abs_tol=1e-7) for a, b in zip(first[1:], last[1:])):
        return False
    turns = (last[0] - first[0]) / 360.0
    return math.isclose(turns, round(turns), rel_tol=0.0, abs_tol=1e-7)


def validate_css_keyframe_contract(
    elements: list[ET.Element],
    style_text: str,
    errors: list[str],
) -> None:
    """Require explicit closed endpoints or a verified periodic dash phase."""

    keyframe_pattern = re.compile(r"@keyframes\s+([-_A-Za-z0-9]+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", re.IGNORECASE)
    periodic_names = {"psvg-conveyor", "psvg-trim"}
    keyframe_blocks = dict(keyframe_pattern.findall(CSS_COMMENT.sub("", style_text)))
    for name, block in keyframe_blocks.items():
        if name in periodic_names:
            continue
        selectors = [match.group(1) for match in re.finditer(r"([^{}]+)\{[^{}]*\}", block)]
        explicitly_closed = any(
            re.search(r"(?:^|,)\s*(?:from|0%)\s*(?:,|$)", selector, re.IGNORECASE)
            and re.search(r"(?:^|,)\s*(?:to|100%)\s*(?:,|$)", selector, re.IGNORECASE)
            for selector in selectors
        )
        if not explicitly_closed:
            errors.append(
                f"CSS @keyframes {name!r} must declare identical start/end state in one selector group."
            )

    for index, element in enumerate(elements):
        style = element.get("style") or ""
        if "psvg-conveyor" not in style and "psvg-trim" not in style:
            continue
        dasharray = element.get("stroke-dasharray") or ""
        offset_delta = 1.0
        if "psvg-trim" in style and not dasharray:
            trim_block = keyframe_blocks.get("psvg-trim", "")
            dash_match = re.search(r"stroke-dasharray\s*:\s*([^;}]+)", trim_block, re.IGNORECASE)
            offsets = [
                float(value)
                for value in re.findall(
                    r"stroke-dashoffset\s*:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+))",
                    trim_block,
                    re.IGNORECASE,
                )
            ]
            if dash_match:
                dasharray = dash_match.group(1)
            if len(offsets) >= 2:
                offset_delta = abs(offsets[-1] - offsets[0])
        try:
            dash_period = sum(float(value) for value in re.findall(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", dasharray))
        except ValueError:
            dash_period = 0.0
        if dash_period <= 0:
            errors.append(f"Periodic dash animation #{index + 1} requires a numeric stroke-dasharray.")
            continue
        cycles = offset_delta / dash_period
        if not math.isclose(cycles, round(cycles), rel_tol=0.0, abs_tol=1e-7):
            errors.append(
                f"Periodic dash animation #{index + 1} has dash period {dash_period:g}; "
                f"the keyframe offset delta {offset_delta:g} must be an integer number of periods."
            )


def validate_loop_contract(
    elements: list[ET.Element],
    master_duration_ms: int,
    errors: list[str],
) -> tuple[int, int]:
    """Validate declared SMIL and inline-CSS periods against the master loop."""

    smil_count = 0
    css_count = 0
    for index, element in enumerate(elements):
        tag = local_name(element.tag)
        label = f"<{tag}> #{index + 1}"
        if tag in MOTION_TAGS:
            smil_count += 1
            duration_value = element.get("dur")
            duration_ms = clock_value_ms(duration_value or "")
            if duration_ms is None:
                errors.append(f"{label} must use a numeric SMIL dur for a declared loop.")
            elif not math.isclose(duration_ms, master_duration_ms, rel_tol=0.0, abs_tol=0.01):
                errors.append(
                    f"{label} duration {duration_value!r} must equal master duration "
                    f"{master_duration_ms} ms."
                )
            if (element.get("repeatCount") or "").strip().lower() != "indefinite":
                errors.append(f"{label} must set repeatCount='indefinite' for a declared loop.")
            for begin_part in (element.get("begin") or "0s").split(";"):
                begin_ms = clock_value_ms(begin_part)
                if begin_ms is not None and begin_ms > 0.01:
                    errors.append(
                        f"{label} numeric begin {begin_part.strip()!r} must be zero or negative."
                    )
            if tag == "animateMotion":
                key_points = [part.strip() for part in (element.get("keyPoints") or "").split(";") if part.strip()]
                try:
                    closes_path = len(key_points) >= 2 and math.isclose(
                        float(key_points[0]), float(key_points[-1]), rel_tol=0.0, abs_tol=1e-9
                    )
                except ValueError:
                    closes_path = False
                if not closes_path:
                    errors.append(
                        f"{label} must provide numeric keyPoints whose first and last values match."
                    )
            elif tag in {"animate", "animateTransform"}:
                values = [part.strip() for part in (element.get("values") or "").split(";") if part.strip()]
                if len(values) >= 2 and normalized_animation_value(values[0]) != normalized_animation_value(values[-1]):
                    errors.append(f"{label} values must repeat the first state at the loop endpoint.")
                elif not values and element.get("from") is not None and element.get("to") is not None:
                    start, finish = element.get("from", ""), element.get("to", "")
                    closes = normalized_animation_value(start) == normalized_animation_value(finish)
                    if tag == "animateTransform" and (element.get("type") or "").lower() == "rotate":
                        closes = rotation_endpoints_close(start, finish)
                    if not closes:
                        errors.append(f"{label} from/to endpoints do not close at the master loop.")

        style = element.get("style") or ""
        if not style.strip():
            continue
        declarations: dict[str, str] = {}
        for declaration in style.split(";"):
            if ":" not in declaration:
                continue
            name, value = declaration.split(":", 1)
            declarations[name.strip().lower()] = value.strip()
        animation_values: list[str] = []
        shorthand = declarations.get("animation")
        if shorthand and not re.match(r"none(?:\s*!important)?\Z", shorthand, re.IGNORECASE):
            animation_values.extend(split_css_top_level(shorthand))
        duration_declaration = declarations.get("animation-duration")
        if duration_declaration:
            animation_values.extend(split_css_top_level(duration_declaration))
        for animation_value in animation_values:
            times = CSS_TIME.findall(animation_value)
            if not times:
                errors.append(
                    f"{label} inline CSS animation {animation_value!r} must expose a numeric period."
                )
                continue
            number, unit = times[0]
            duration_ms = float(number) * (1.0 if unit.lower() == "ms" else 1000.0)
            css_count += 1
            if duration_ms <= 0:
                errors.append(f"{label} inline CSS animation period must be positive.")
                continue
            ratio = master_duration_ms / duration_ms
            if ratio < 1 or not math.isclose(ratio, round(ratio), rel_tol=0.0, abs_tol=1e-9):
                errors.append(
                    f"{label} inline CSS period {duration_ms:g} ms must divide master "
                    f"duration {master_duration_ms} ms."
                )
    return smil_count, css_count


def expected_parameter_hash(root: ET.Element, pattern_id: str) -> str | None:
    try:
        payload = {
            "pattern": pattern_id,
            "seed": int(root.get("data-seed", "")),
            "width": int(float(root.get("width", ""))),
            "height": int(float(root.get("height", ""))),
            "durationMs": int(root.get("data-duration-ms", "")),
            "palette": root.get("data-palette", ""),
            "motion": root.get("data-motion", ""),
        }
    except ValueError:
        return None
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def direct_child(root: ET.Element, tag_name: str) -> ET.Element | None:
    for child in root:
        if local_name(child.tag) == tag_name:
            return child
    return None


def text_content(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(part.strip() for part in element.itertext() if part.strip()).strip()


def count_xml_stylesheet_instructions(xml_text: str) -> int:
    count = 0
    for _event, instruction in ET.iterparse(io.StringIO(xml_text), events=("pi",)):
        target = (instruction.text or "").split(None, 1)[0].lower()
        if target == "xml-stylesheet":
            count += 1
    return count


def css_urls(css_text: str) -> list[str]:
    """Return CSS url() payloads while tolerating quotes, whitespace, and escapes."""

    text = CSS_COMMENT.sub("", css_text)
    values: list[str] = []
    cursor = 0
    while match := CSS_URL_START.search(text, cursor):
        index = match.end()
        while index < len(text) and text[index].isspace():
            index += 1
        quote = text[index] if index < len(text) and text[index] in {'"', "'"} else None
        if quote:
            index += 1
        start = index
        escaped = False
        payload: list[str] = []
        closed = False
        while index < len(text):
            character = text[index]
            if escaped:
                payload.append(character)
                escaped = False
            elif character == "\\":
                payload.append(character)
                escaped = True
            elif quote and character == quote:
                index += 1
                while index < len(text) and text[index].isspace():
                    index += 1
                if index < len(text) and text[index] == ")":
                    closed = True
                    index += 1
                break
            elif not quote and character == ")":
                closed = True
                index += 1
                break
            else:
                payload.append(character)
            index += 1
        if closed:
            values.append("".join(payload).strip())
            cursor = index
        else:
            # Malformed CSS is handled by browsers as an invalid declaration; do not
            # let the scanner loop forever or reinterpret later text as a new URL.
            cursor = max(match.end(), start + 1)
    return values


def media_blocks(css_text: str, feature: str) -> list[str]:
    """Extract balanced @media blocks that mention a requested media feature."""

    blocks: list[str] = []
    start_pattern = re.compile(r"@media\b[^{}]*" + re.escape(feature) + r"[^{}]*\{", re.IGNORECASE)
    text = CSS_COMMENT.sub("", css_text)
    for match in start_pattern.finditer(text):
        opening = match.end() - 1
        depth = 0
        quote: str | None = None
        escaped = False
        for index in range(opening, len(text)):
            character = text[index]
            if escaped:
                escaped = False
                continue
            if character == "\\":
                escaped = True
                continue
            if quote:
                if character == quote:
                    quote = None
                continue
            if character in {'"', "'"}:
                quote = character
            elif character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[opening + 1 : index])
                    break
    return blocks


def has_smil_reduced_motion_contract(elements: list[ET.Element], style_text: str) -> bool:
    class_sets = [set((element.get("class") or "").split()) for element in elements]
    has_motion_layer = any("psvg-motion-layer" in classes for classes in class_sets)
    has_reduced_layer = any("psvg-reduced-layer" in classes for classes in class_sets)
    if not (has_motion_layer and has_reduced_layer):
        return False
    for block in media_blocks(style_text, "prefers-reduced-motion"):
        hides_motion = re.search(
            r"\.psvg-motion-layer\b[^{}]*\{[^{}]*\bdisplay\s*:\s*none\b[^{}]*\}",
            block,
            re.IGNORECASE,
        )
        shows_reduced = re.search(
            r"\.psvg-reduced-layer\b[^{}]*\{[^{}]*\bdisplay\s*:\s*(?!none\b)[-_A-Za-z]+\b[^{}]*\}",
            block,
            re.IGNORECASE,
        )
        if hides_motion and shows_reduced:
            return True
    return False


def inspect_references(elements: list[ET.Element], ids: set[str], errors: list[str]) -> tuple[int, int]:
    reference_count = 0
    external_count = 0
    for element in elements:
        tag = local_name(element.tag)
        if tag == "script":
            errors.append("Executable <script> elements are forbidden.")
        for raw_name, raw_value in element.attrib.items():
            name = local_name(raw_name)
            value = raw_value.strip()
            if name.lower().startswith("on"):
                errors.append(f"Inline event handler {name!r} is forbidden on <{tag}>.")
            if name in {"href", "src"}:
                reference_count += 1
                if value.startswith("#"):
                    target = value[1:]
                    if not target or target not in ids:
                        errors.append(f"Broken internal reference {value!r} on <{tag}>.")
                else:
                    external_count += 1
                    errors.append(f"External resource reference {value!r} on <{tag}> is forbidden.")
            for target in css_urls(value):
                reference_count += 1
                if target.startswith("#"):
                    if target[1:] not in ids:
                        errors.append(f"Broken internal paint/filter reference {target!r} on <{tag}>.")
                else:
                    external_count += 1
                    errors.append(f"External CSS/SVG URL {target!r} on <{tag}> is forbidden.")
    return reference_count, external_count


def validate_one(
    path: Path,
    catalog: dict[str, dict[str, object]],
    *,
    require_motion: bool,
    require_standalone: bool,
    expect_pattern_id: str | None,
    expect_seed: int | None,
    expect_palette: str | None,
    expect_motion: str | None,
    min_elements: int,
    max_bytes: int | None,
) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    metadata: dict[str, str] = {}
    counts: dict[str, int] = {
        "elements": 0,
        "drawingElements": 0,
        "textElements": 0,
        "ids": 0,
        "references": 0,
        "externalReferences": 0,
        "smilElements": 0,
        "cssKeyframes": 0,
        "scriptElements": 0,
        "foreignObjectElements": 0,
        "xmlBaseAttributes": 0,
        "xmlStylesheetInstructions": 0,
        "loopSmilAnimations": 0,
        "loopInlineCssAnimations": 0,
    }
    resolved = path.resolve()
    if not path.exists():
        errors.append(f"SVG file does not exist: {resolved}")
        return {"ok": False, "path": str(resolved), "errors": errors, "warnings": warnings, "metadata": metadata, "counts": counts}
    if not path.is_file():
        errors.append(f"SVG path is not a file: {resolved}")
        return {"ok": False, "path": str(resolved), "errors": errors, "warnings": warnings, "metadata": metadata, "counts": counts}

    byte_size = path.stat().st_size
    if max_bytes is not None and byte_size > max_bytes:
        errors.append(f"SVG is {byte_size} bytes, above --max-bytes {max_bytes}.")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        errors.append(f"SVG is not valid UTF-8: {error}")
        return {"ok": False, "path": str(resolved), "bytes": byte_size, "errors": errors, "warnings": warnings, "metadata": metadata, "counts": counts}

    lower = raw.lower()
    if "<!doctype" in lower or "<!entity" in lower:
        errors.append("DOCTYPE and ENTITY declarations are forbidden in standalone procedural SVG.")
    if NONFINITE.search(raw):
        errors.append("SVG contains a NaN or infinite numeric token.")
    if "@import" in lower:
        errors.append("CSS @import is forbidden.")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as error:
        errors.append(f"XML parse failed: {error}")
        return {"ok": False, "path": str(resolved), "bytes": byte_size, "errors": errors, "warnings": warnings, "metadata": metadata, "counts": counts}

    counts["xmlStylesheetInstructions"] = count_xml_stylesheet_instructions(raw)
    if counts["xmlStylesheetInstructions"]:
        errors.append("xml-stylesheet processing instructions are forbidden in standalone procedural SVG.")

    if local_name(root.tag) != "svg":
        errors.append(f"Root element must be <svg>; found <{local_name(root.tag)}>.")
    namespace = root.tag.split("}", 1)[0][1:] if root.tag.startswith("{") else ""
    if namespace != SVG_NS:
        errors.append(f"Root SVG namespace must be {SVG_NS!r}; found {namespace!r}.")

    for key in REQUIRED_ROOT_METADATA:
        value = root.get(key)
        if value is None or not value.strip():
            errors.append(f"Root is missing non-empty {key}.")
        else:
            metadata[key] = value.strip()

    pattern_id = metadata.get("data-pattern-id", "")
    if pattern_id and not PATTERN_ID.fullmatch(pattern_id):
        errors.append(f"Invalid canonical procedural pattern ID: {pattern_id!r}.")
    catalog_entry = catalog.get(pattern_id)
    if pattern_id and catalog_entry is None:
        errors.append(f"Pattern ID is not present in the bundled catalog: {pattern_id!r}.")
    if catalog_entry is not None:
        expected_pairs = {
            "data-family": str(catalog_entry.get("family")),
            "data-renderer": str(catalog_entry.get("renderer")),
            "data-variant": str(catalog_entry.get("variant")),
            "data-driver": str(catalog_entry.get("driver")),
            "data-technique": str(catalog_entry.get("technique")),
        }
        for key, expected in expected_pairs.items():
            if metadata.get(key) != expected:
                errors.append(f"{key} must match catalog value {expected!r}; found {metadata.get(key)!r}.")
        local_id = pattern_id.removeprefix("procedural-svg-")
        if metadata.get("data-example-id") != local_id:
            errors.append(f"data-example-id must be {local_id!r}; found {metadata.get('data-example-id')!r}.")

    if metadata.get("data-procedural-svg-version") != "1":
        errors.append("data-procedural-svg-version must be '1'.")
    if metadata.get("data-deterministic") != "true":
        errors.append("data-deterministic must be 'true'.")
    if metadata.get("data-standalone") != "true":
        errors.append("data-standalone must be 'true'.")
    if metadata.get("data-palette") not in {"colorset1", "colorset2"}:
        errors.append("data-palette must be colorset1 or colorset2.")
    if metadata.get("data-motion") not in {"full", "reduced"}:
        errors.append("data-motion must be full or reduced.")
    if metadata.get("data-motion-engine") not in {"css", "smil", "mixed", "static"}:
        errors.append("data-motion-engine must be css, smil, mixed, or static.")
    if metadata.get("data-loop") not in {"true", "false"}:
        errors.append("data-loop must be true or false.")
    if metadata.get("data-motion") == "full" and metadata.get("data-loop") != "true":
        errors.append("Full-motion output must declare data-loop='true'.")
    if metadata.get("data-motion") == "reduced" and metadata.get("data-loop") != "false":
        errors.append("Reduced-motion output must declare data-loop='false'.")
    expected_loop_contract = "master-phase" if metadata.get("data-motion") == "full" else "static"
    if metadata.get("data-loop-contract") != expected_loop_contract:
        errors.append(
            f"data-loop-contract must be {expected_loop_contract!r} for "
            f"{metadata.get('data-motion')!r} motion."
        )
    expected_fallback = "layered" if metadata.get("data-motion") == "full" else "static"
    if metadata.get("data-reduced-motion-fallback") != expected_fallback:
        errors.append(
            f"data-reduced-motion-fallback must be {expected_fallback!r} for "
            f"{metadata.get('data-motion')!r} motion."
        )
    parameter_hash = metadata.get("data-parameter-hash", "")
    if not re.fullmatch(r"[0-9a-f]{64}", parameter_hash):
        errors.append("data-parameter-hash must be a lowercase SHA-256 hex digest.")
    calculated_parameter_hash = expected_parameter_hash(root, pattern_id)
    if calculated_parameter_hash is not None and parameter_hash != calculated_parameter_hash:
        errors.append(
            f"data-parameter-hash does not match root build inputs; expected {calculated_parameter_hash}."
        )

    seed_text = metadata.get("data-seed")
    if seed_text is not None:
        try:
            int(seed_text)
        except ValueError:
            errors.append(f"data-seed must be an integer; found {seed_text!r}.")
    duration_text = metadata.get("data-duration-ms")
    if duration_text is not None:
        try:
            duration = int(duration_text)
            if duration <= 0:
                raise ValueError
        except ValueError:
            errors.append(f"data-duration-ms must be a positive integer; found {duration_text!r}.")

    if expect_pattern_id is not None and pattern_id != expect_pattern_id:
        errors.append(f"Expected pattern ID {expect_pattern_id!r}; found {pattern_id!r}.")
    if expect_seed is not None and seed_text != str(expect_seed):
        errors.append(f"Expected seed {expect_seed}; found {seed_text!r}.")
    if expect_palette is not None and metadata.get("data-palette") != expect_palette:
        errors.append(f"Expected palette {expect_palette!r}; found {metadata.get('data-palette')!r}.")
    if expect_motion is not None and metadata.get("data-motion") != expect_motion:
        errors.append(f"Expected motion {expect_motion!r}; found {metadata.get('data-motion')!r}.")

    title = direct_child(root, "title")
    desc = direct_child(root, "desc")
    if not text_content(title):
        errors.append("Root must contain a non-empty direct <title>.")
    if not text_content(desc):
        errors.append("Root must contain a non-empty direct <desc>.")
    title_id = title.get("id") if title is not None else None
    desc_id = desc.get("id") if desc is not None else None
    labelled_by = (root.get("aria-labelledby") or "").split()
    if not title_id or title_id not in labelled_by:
        errors.append("aria-labelledby must reference the root <title> ID.")
    if not desc_id or desc_id not in labelled_by:
        errors.append("aria-labelledby must reference the root <desc> ID.")
    if root.get("role") != "img":
        errors.append("Root role must be 'img'.")

    view_box = (root.get("viewBox") or "").replace(",", " ").split()
    if len(view_box) != 4:
        errors.append(f"viewBox must contain four numeric values; found {root.get('viewBox')!r}.")
    else:
        values = [parse_number(value, f"viewBox[{index}]", errors) for index, value in enumerate(view_box)]
        if values[2] is not None and values[2] <= 0:
            errors.append("viewBox width must be positive.")
        if values[3] is not None and values[3] <= 0:
            errors.append("viewBox height must be positive.")
    for dimension in ("width", "height"):
        value = root.get(dimension)
        if value is None:
            errors.append(f"Root is missing {dimension}.")
        else:
            number = parse_number(value, dimension, errors)
            if number is not None and number <= 0:
                errors.append(f"Root {dimension} must be positive.")

    elements = list(root.iter())
    validate_finite_geometry(elements, errors)
    counts["elements"] = len(elements)
    counts["drawingElements"] = sum(local_name(element.tag) in DRAWING_TAGS for element in elements)
    counts["textElements"] = sum(local_name(element.tag) == "text" for element in elements)
    counts["scriptElements"] = sum(local_name(element.tag) == "script" for element in elements)
    counts["foreignObjectElements"] = sum(
        local_name(element.tag).lower() == "foreignobject" for element in elements
    )
    counts["xmlBaseAttributes"] = sum(
        f"{{{XML_NS}}}base" in element.attrib for element in elements
    )
    if counts["foreignObjectElements"]:
        errors.append("<foreignObject> elements are forbidden in standalone procedural SVG.")
    if counts["xmlBaseAttributes"]:
        errors.append("xml:base attributes are forbidden in standalone procedural SVG.")
    if counts["elements"] < min_elements:
        errors.append(f"Expected at least {min_elements} SVG elements; found {counts['elements']}.")
    if counts["drawingElements"] < 4:
        errors.append("Readable base state requires at least four drawing elements.")
    if counts["textElements"] < 3:
        errors.append("Readable base state requires at least three visible text elements.")

    id_values = [element.get("id") for element in elements if element.get("id")]
    duplicates = sorted(value for value, count in Counter(id_values).items() if count > 1)
    if duplicates:
        errors.append(f"Duplicate SVG IDs: {', '.join(duplicates)}.")
    ids = set(id_values)
    counts["ids"] = len(ids)
    reference_count, external_count = inspect_references(elements, ids, errors)
    counts["references"] = reference_count
    counts["externalReferences"] = external_count

    style_text = "\n".join(text_content(element) for element in elements if local_name(element.tag) == "style")
    style_reference_count = 0
    style_external_count = 0
    for target in css_urls(style_text):
        style_reference_count += 1
        if target.startswith("#"):
            if not target[1:] or target[1:] not in ids:
                errors.append(f"Broken internal paint/filter reference {target!r} in <style> text.")
        else:
            style_external_count += 1
            errors.append(f"External CSS/SVG URL {target!r} in <style> text is forbidden.")
    counts["references"] += style_reference_count
    counts["externalReferences"] += style_external_count
    counts["smilElements"] = sum(local_name(element.tag) in MOTION_TAGS for element in elements)
    counts["cssKeyframes"] = len(re.findall(r"@keyframes\s+[-_A-Za-z0-9]+", style_text))
    css_motion = counts["cssKeyframes"] > 0 and bool(
        re.search(r"\banimation\s*:\s*(?!none\b)[^;}]+", raw, re.IGNORECASE)
    )
    has_motion = counts["smilElements"] > 0 or css_motion
    if require_motion and not has_motion:
        errors.append("No SMIL or CSS keyframe motion was detected, but --require-motion was requested.")
    if metadata.get("data-motion") == "full" and not has_motion:
        errors.append("Full-motion output must contain SMIL or CSS keyframe motion.")
    detected_engine = "static"
    if counts["smilElements"] > 0 and css_motion:
        detected_engine = "mixed"
    elif counts["smilElements"] > 0:
        detected_engine = "smil"
    elif css_motion:
        detected_engine = "css"
    if metadata.get("data-motion-engine") != detected_engine:
        errors.append(
            f"data-motion-engine must match detected engine {detected_engine!r}; "
            f"found {metadata.get('data-motion-engine')!r}."
        )
    if metadata.get("data-motion") == "reduced" and has_motion:
        warnings.append("Reduced-motion output retains dormant motion definitions; verify the frozen state visually.")
    if metadata.get("data-loop") == "true" and duration_text is not None:
        try:
            master_duration_ms = int(duration_text)
        except ValueError:
            master_duration_ms = 0
        if master_duration_ms > 0:
            loop_smil_count, loop_css_count = validate_loop_contract(
                elements, master_duration_ms, errors
            )
            validate_css_keyframe_contract(elements, style_text, errors)
            counts["loopSmilAnimations"] = loop_smil_count
            counts["loopInlineCssAnimations"] = loop_css_count
    if (
        metadata.get("data-motion") == "full"
        and counts["smilElements"] > 0
        and not has_smil_reduced_motion_contract(elements, style_text)
    ):
        errors.append(
            "Full-motion SVGs with SMIL must include .psvg-motion-layer and "
            ".psvg-reduced-layer elements plus a prefers-reduced-motion rule that "
            "hides the motion layer and shows the reduced layer."
        )
    standalone = (
        metadata.get("data-standalone") == "true"
        and counts["externalReferences"] == 0
        and counts["scriptElements"] == 0
        and counts["foreignObjectElements"] == 0
        and counts["xmlBaseAttributes"] == 0
        and counts["xmlStylesheetInstructions"] == 0
    )
    if require_standalone and not standalone:
        errors.append("Artifact does not satisfy the required standalone contract.")

    return {
        "ok": not errors,
        "path": str(resolved),
        "bytes": byte_size,
        "errors": errors,
        "warnings": warnings,
        "metadata": metadata,
        "title": text_content(title),
        "description": text_content(desc),
        "counts": counts,
        "hasMotion": has_motion,
        "standalone": standalone,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate standalone procedural SVG artifacts.")
    parser.add_argument("svg", type=Path, nargs="+", help="One or more SVG paths to validate.")
    parser.add_argument("--require-motion", action="store_true", help="Require SMIL or CSS keyframe motion.")
    parser.add_argument("--require-standalone", action="store_true", help="Require the explicit no-script, no-network standalone contract.")
    parser.add_argument(
        "--expect-pattern-id",
        "--expected-pattern-id",
        "--expect-id",
        "--expected-id",
        dest="expect_pattern_id",
        help="Expected canonical procedural-svg-* ID.",
    )
    parser.add_argument("--expect-seed", "--expected-seed", dest="expect_seed", type=int, help="Expected deterministic integer seed.")
    parser.add_argument("--expect-palette", "--expected-palette", dest="expect_palette", choices=("colorset1", "colorset2"))
    parser.add_argument("--expect-motion", "--expected-motion", dest="expect_motion", choices=("full", "reduced"))
    parser.add_argument("--min-elements", type=int, default=12, help="Minimum total XML element count.")
    parser.add_argument("--max-bytes", type=int, help="Optional maximum artifact byte size.")
    parser.add_argument("--report", type=Path, help="Exact JSON report output path.")
    parser.add_argument("--json", action="store_true", help="Print the complete JSON report.")
    return parser


def write_report(path: Path, report: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.min_elements < 1:
        parser.error("--min-elements must be at least 1.")
    if args.max_bytes is not None and args.max_bytes < 1:
        parser.error("--max-bytes must be at least 1.")
    if args.expect_pattern_id is not None and not PATTERN_ID.fullmatch(args.expect_pattern_id):
        parser.error("--expect-pattern-id must use canonical procedural-svg-* lowercase hyphen-case.")
    if args.report is not None:
        report_path = args.report.expanduser().resolve()
        input_paths = {path.expanduser().resolve() for path in args.svg}
        if report_path in input_paths:
            parser.error(f"--report path collides with an input SVG: {report_path}")
    try:
        catalog = load_catalog()
        results = [
            validate_one(
                path,
                catalog,
                require_motion=args.require_motion,
                require_standalone=args.require_standalone,
                expect_pattern_id=args.expect_pattern_id,
                expect_seed=args.expect_seed,
                expect_palette=args.expect_palette,
                expect_motion=args.expect_motion,
                min_elements=args.min_elements,
                max_bytes=args.max_bytes,
            )
            for path in args.svg
        ]
    except (OSError, ValueError, json.JSONDecodeError) as error:
        report = {"ok": False, "error": f"Validator setup failed: {error}", "results": []}
        if args.report:
            write_report(args.report, report)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(report["error"], file=sys.stderr)
        return 1

    report: dict[str, object] = {
        "ok": all(bool(result["ok"]) for result in results),
        "count": len(results),
        "passed": sum(bool(result["ok"]) for result in results),
        "failed": sum(not bool(result["ok"]) for result in results),
        "results": results,
    }
    if args.report:
        write_report(args.report, report)
        report["report"] = str(args.report.resolve())
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for result in results:
            status = "PASS" if result["ok"] else "FAIL"
            print(f"{status} {result['path']}")
            for error in result["errors"]:
                print(f"  error: {error}")
            for warning in result["warnings"]:
                print(f"  warning: {warning}")
        print(f"Validated {report['passed']}/{report['count']} procedural SVG artifacts.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

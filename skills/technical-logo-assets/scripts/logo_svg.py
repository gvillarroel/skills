#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Vector-only SVG inspection and conservative, geometry-preserving logo variants."""

from __future__ import annotations

import base64
import hashlib
import math
import re
import struct
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter


SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
SHAPES = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "use"}
VARIANTS = ("original", "color", "grayscale", "mono-black", "mono-white", "adaptive")
PERMISSIVE_LICENSES = {"MIT", "Apache-2.0", "BSD-3-Clause", "CC0-1.0", "CC-BY-3.0", "CC-BY-4.0"}
PAINT_RE = re.compile(r"(?i)(?:^|[;{])\s*(fill|stroke|color|stop-color)\s*:\s*([^;}]+)")
URL_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.I | re.S)


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def data_svg(href: str) -> bytes:
    header, separator, value = href.partition(",")
    if not separator or not header.lower().startswith("data:image/svg+xml"):
        raise ValueError("Raster or external image: an embedded image must be SVG")
    if ";base64" in header.lower():
        return base64.b64decode(value, validate=True)
    return urllib.parse.unquote_to_bytes(value)


def inspect_font(payload: bytes) -> None:
    """Accept embedded outline fonts, never a bitmap disguised as a font data URI."""
    if len(payload) < 12 or payload[:4] not in {b"\x00\x01\x00\x00", b"OTTO", b"true"}:
        raise ValueError("Embedded font must be an inspectable TrueType/OpenType outline font")
    count = struct.unpack_from(">H", payload, 4)[0]
    if len(payload) < 12 + count * 16:
        raise ValueError("Truncated embedded font table directory")
    tables = {payload[12 + index * 16:16 + index * 16] for index in range(count)}
    if not tables & {b"glyf", b"CFF ", b"CFF2"} or tables & {b"CBDT", b"CBLC", b"EBDT", b"EBLC", b"sbix"}:
        raise ValueError("Embedded font has no verified outlines or contains bitmap glyph tables")


def inspect_vector(payload: bytes, depth: int = 0) -> dict:
    """Inspect actual nested content, not just the filename or MIME label."""
    if depth > 12 or len(payload) > 25_000_000:
        raise ValueError("SVG nesting or size exceeds the inspection limit")
    if b"<!ENTITY" in payload.upper():
        raise ValueError("Entity declarations are not permitted in logo SVGs")
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as error:
        raise ValueError(f"Invalid SVG XML: {error}") from error
    if root.tag != f"{{{SVG_NS}}}svg":
        raise ValueError("Expected an SVG root in the SVG namespace")
    shapes = 0
    nested = 0
    text_nodes = 0
    font_embedded = False
    paints: set[str] = set()
    ids = []
    references: set[str] = set()
    for node in root.iter():
        tag = local_name(node.tag)
        if tag in {"script", "foreignObject", "animate", "animateTransform", "set"}:
            raise ValueError(f"Active or non-SVG content is not permitted: {tag}")
        if tag in SHAPES:
            shapes += 1
        if tag in {"text", "tspan"}:
            text_nodes += 1
        if node.get("id"):
            ids.append(node.get("id"))
        for key, value in node.attrib.items():
            name = local_name(key)
            if name.lower().startswith("on"):
                raise ValueError("SVG event handlers are not permitted")
            if name == "href":
                if tag in {"image", "feImage"}:
                    result = inspect_vector(data_svg(value), depth + 1)
                    shapes += result["shapeCount"]
                    nested += result["embeddedSvgCount"] + 1
                    paints.update(result["paints"])
                    font_embedded |= result["embeddedFont"]
                elif not value.startswith("#"):
                    raise ValueError("External SVG references are not permitted")
                else:
                    references.add(value[1:])
            if name in {"fill", "stroke", "stop-color"}:
                paints.add(value.strip())
            if name == "filter" and not value.startswith("url(#") and value != "none":
                raise ValueError("External or CSS filters are not permitted")
        css = node.text or "" if tag == "style" else node.get("style", "")
        if "@import" in css.lower():
            raise ValueError("External CSS imports are not permitted")
        for match in URL_RE.finditer(css):
            resource = match.group(2).strip()
            if resource.startswith("#"):
                references.add(resource[1:])
                continue
            if tag == "style" and resource.startswith("data:font/") and ";base64," in resource:
                inspect_font(base64.b64decode(resource.split(";base64,", 1)[1], validate=True))
                font_embedded = True
                continue
            raise ValueError("External or raster CSS resources are not permitted")
        for match in PAINT_RE.finditer(css):
            if match.group(1).lower() != "color":
                paints.add(match.group(2).strip())
        for name in ("fill", "stroke", "clip-path", "mask", "filter"):
            value = node.get(name, "")
            for match in URL_RE.finditer(value):
                if not match.group(2).startswith("#"):
                    raise ValueError("Nonlocal paint or clipping reference")
                references.add(match.group(2)[1:])
    duplicate_ids = sorted(value for value, count in Counter(ids).items() if count > 1)
    if set(duplicate_ids) & references:
        raise ValueError("Ambiguous referenced duplicate SVG IDs inside one source")
    if text_nodes and not font_embedded:
        raise ValueError("Visible text requires an embedded vector font or outlined glyphs")
    if not shapes:
        raise ValueError("SVG contains no drawable vector geometry")
    dimensions(root)
    return {"vectorOnly": True, "shapeCount": shapes, "embeddedSvgCount": nested,
            "embeddedFont": font_embedded, "paints": sorted(paints), "unreferencedDuplicateIds": duplicate_ids}


def dimensions(root: ET.Element) -> str:
    value = root.get("viewBox")
    if value:
        try:
            numbers = [float(part) for part in re.split(r"[\s,]+", value.strip())]
        except ValueError as error:
            raise ValueError("Invalid SVG viewBox") from error
        if len(numbers) != 4 or not all(math.isfinite(n) for n in numbers) or min(numbers[2:]) <= 0:
            raise ValueError("SVG viewBox must have positive finite dimensions")
        return value
    sizes = []
    for name in ("width", "height"):
        match = re.fullmatch(r"([0-9.]+)(?:px)?", root.get(name, ""))
        if not match or not math.isfinite(float(match.group(1))) or float(match.group(1)) <= 0:
            raise ValueError("SVG needs a viewBox or finite pixel dimensions")
        sizes.append(match.group(1))
    return f"0 0 {sizes[0]} {sizes[1]}"


def normalize_color(value: str) -> str:
    value = value.strip().lower()
    named = {"black": "#000000", "white": "#ffffff", "gray": "#808080", "grey": "#808080"}
    value = named.get(value, value)
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(char * 2 for char in value[1:])
    return value


def declarations(value: str) -> dict[str, str]:
    result = {}
    for part in value.split(";"):
        if not part.strip():
            continue
        key, separator, val = part.partition(":")
        if not separator or "!important" in val.lower():
            raise ValueError("Complex CSS needs an upstream monochrome source")
        result[key.strip().lower()] = val.strip()
    return result


def flatten_simple_styles(root: ET.Element) -> None:
    """Resolve a deliberately small CSS subset, rejecting ambiguous selectors."""
    rules = []
    style_nodes = []
    for parent in root.iter():
        for node in parent:
            if local_name(node.tag) != "style":
                continue
            css = re.sub(r"/\*.*?\*/", "", node.text or "", flags=re.S)
            if "@" in css or re.sub(r"[^{}]+\{[^{}]*\}", "", css).strip():
                raise ValueError("Complex CSS needs an upstream monochrome source")
            for selector_group, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
                for selector in selector_group.split(","):
                    selector = selector.strip()
                    if not re.fullmatch(r"(?:\.[\w-]+|#[\w-]+|[a-zA-Z][\w-]*)", selector):
                        raise ValueError("Complex CSS selector needs an upstream monochrome source")
                    specificity = 100 if selector.startswith("#") else 10 if selector.startswith(".") else 1
                    rules.append((specificity, len(rules), selector, declarations(body)))
            style_nodes.append((parent, node))
    for node in root.iter():
        for _, _, selector, props in sorted(rules):
            match = (selector[1:] in node.get("class", "").split() if selector.startswith(".") else
                     node.get("id") == selector[1:] if selector.startswith("#") else
                     local_name(node.tag) == selector)
            if match:
                node.attrib.update(props)
        if node.get("style"):
            node.attrib.update(declarations(node.attrib.pop("style")))
        node.attrib.pop("class", None)
    for parent, node in style_nodes:
        parent.remove(node)


def monochrome_root(payload: bytes) -> ET.Element:
    inspect_vector(payload)
    root = ET.fromstring(payload)
    rejected = {"linearGradient", "radialGradient", "pattern", "filter", "mask", "text", "tspan", "image", "feImage"}
    if any(local_name(node.tag) in rejected for node in root.iter()):
        raise ValueError("Complex paint, masks, effects, images, or text require an upstream monochrome source")
    flatten_simple_styles(root)
    colors: set[str] = set()

    def visit(node: ET.Element, fill: str = "black", stroke: str = "none", in_clip: bool = False, color: str = "currentColor") -> None:
        fill = node.get("fill", fill)
        stroke = node.get("stroke", stroke)
        color = node.get("color", color)
        in_clip |= local_name(node.tag) == "clipPath"
        if local_name(node.tag) in SHAPES and not in_clip and node.get("display") != "none":
            for paint in ((stroke,) if local_name(node.tag) == "line" else (fill, stroke)):
                normalized = normalize_color(paint)
                if normalized == "currentcolor":
                    normalized = normalize_color(color)
                if normalized in {"none", "transparent"}:
                    continue
                if normalized.startswith(("url(", "var(")) or normalized in {"inherit", "context-fill", "context-stroke"}:
                    raise ValueError("Unresolved paint cannot be safely recolored")
                colors.add(normalized)
        for child in node:
            visit(child, fill, stroke, in_clip, color)

    visit(root)
    if len(colors) != 1:
        raise ValueError("Multiple paints could encode cutouts; do not collapse them into a silhouette")
    return root


def palette_kind(payload: bytes) -> str:
    try:
        root = monochrome_root(payload)
    except ValueError:
        return "multicolor-or-effects"
    paints = {normalize_color(node.get(key, "")) for node in root.iter() for key in ("fill", "stroke")}
    paints -= {"", "none", "transparent"}
    if not paints or paints <= {"currentcolor", "#000000", "#ffffff"}:
        return "monochrome-original"
    return "single-brand-color"


def prefix_ids(root: ET.Element, prefix: str) -> None:
    mapping = {node.get("id"): prefix + node.get("id") for node in root.iter() if node.get("id")}
    seen: dict[str, int] = {}
    for node in root.iter():
        if node.get("id"):
            original_id = node.get("id")
            seen[original_id] = seen.get(original_id, 0) + 1
            suffix = f"-{seen[original_id]}" if seen[original_id] > 1 else ""
            node.set("id", mapping[original_id] + suffix)
        for key, value in list(node.attrib.items()):
            if local_name(key) == "href" and value.startswith("#") and value[1:] in mapping:
                node.set(key, "#" + mapping[value[1:]])
            else:
                node.set(key, URL_RE.sub(lambda match: f"url(#{mapping.get(match.group(2)[1:], match.group(2)[1:])})" if match.group(2).startswith("#") else match.group(0), value))


def metadata_attributes(item: dict, variant: str, source_hash: str, mode: str) -> dict[str, str]:
    return {"data-logo-id": item["id"], "data-logo-variant": variant, "data-color-mode": mode,
            "data-vector-only": "true", "data-recolorable": "true" if variant == "adaptive" else "false",
            "data-source-sha256": source_hash, "data-license": item["licenseId"]}


def outer_root(item: dict, variant: str, source_hash: str, mode: str) -> ET.Element:
    root = ET.Element(f"{{{SVG_NS}}}svg", {"width": "256", "height": "256", "viewBox": "0 0 256 256",
                          "preserveAspectRatio": "xMidYMid meet", "role": "img",
                          **metadata_attributes(item, variant, source_hash, mode)})
    ET.SubElement(root, f"{{{SVG_NS}}}title").text = f"{item['title']} — {variant}"
    ET.SubElement(root, f"{{{SVG_NS}}}metadata", {**metadata_attributes(item, variant, source_hash, mode),
                                              "data-provider": item["provider"]})
    return root


def wrapped_variant(item: dict, payload: bytes, variant: str = "color", grayscale: bool = False) -> bytes:
    inspect_vector(payload)
    mode = "grayscale" if grayscale else palette_kind(payload)
    root = outer_root(item, variant, digest(payload), mode)
    image_attributes = {"x": "16", "y": "16", "width": "224", "height": "224", "preserveAspectRatio": "xMidYMid meet",
                        "href": "data:image/svg+xml;base64," + base64.b64encode(payload).decode("ascii")}
    if grayscale:
        filter_id = "gray-" + digest(item["id"].encode())[:16]
        defs = ET.SubElement(root, f"{{{SVG_NS}}}defs")
        effect = ET.SubElement(defs, f"{{{SVG_NS}}}filter", {"id": filter_id, "color-interpolation-filters": "sRGB"})
        ET.SubElement(effect, f"{{{SVG_NS}}}feColorMatrix", {"type": "saturate", "values": "0"})
        image_attributes["filter"] = f"url(#{filter_id})"
    ET.SubElement(root, f"{{{SVG_NS}}}image", image_attributes)
    return ET.tostring(root, encoding="utf-8") + b"\n"


def painted_variant(item: dict, payload: bytes, variant: str, paint: str) -> bytes:
    source = monochrome_root(payload)
    source.set("viewBox", dimensions(source))
    prefix_ids(source, "logo-" + digest((item["id"] + variant).encode())[:16] + "-")
    original_fill = source.get("fill", "black")
    source.attrib.update({"x": "16", "y": "16", "width": "224", "height": "224", "preserveAspectRatio": "xMidYMid meet",
                          "fill": original_fill if normalize_color(original_fill) in {"none", "transparent"} else paint})
    for node in source.iter():
        node.attrib.pop("color", None)
        for key in ("fill", "stroke"):
            if node.get(key) and normalize_color(node.get(key)) not in {"none", "transparent"}:
                node.set(key, paint)
    mode = "currentColor" if variant == "adaptive" else "black" if variant == "mono-black" else "white" if variant == "mono-white" else "single-brand-color"
    root = outer_root(item, variant, digest(payload), mode)
    root.append(source)
    result = ET.tostring(root, encoding="utf-8") + b"\n"
    inspect_vector(result)
    return result


def embedded_source(wrapper: bytes) -> bytes:
    root = ET.fromstring(wrapper)
    image = root.find(f"{{{SVG_NS}}}image")
    if image is None:
        raise ValueError("Original wrapper has no direct embedded source")
    return data_svg(image.get("href") or image.get(f"{{{XLINK_NS}}}href") or "")

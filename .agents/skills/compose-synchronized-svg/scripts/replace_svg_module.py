#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Safely replace one marked content region in a synchronized SVG module."""

from __future__ import annotations

import argparse
import collections
import html
import json
import math
import os
import re
import stat
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterator


sys.dont_write_bytecode = True

SVG_NS = "http://www.w3.org/2000/svg"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ROLE_SELECTOR_RE = re.compile(r"^\[data-role=(?:'([^']+)'|\"([^\"]+)\")\]$")
URL_FUNCTION_RE = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE)
REMOTE_SCHEME_RE = re.compile(r"(?:https?|ftp|file|javascript):|(?<!:)//", re.IGNORECASE)
SAFE_DATA_IMAGE_RE = re.compile(r"^data:image/(?:png|jpe?g|gif|webp|avif);", re.IGNORECASE)
XML_DECLARATION_RE = re.compile(
    rb"^[ \t\r\n]*<\?xml[ \t\r\n]+(?P<body>[^?]*)\?>[ \t\r\n]*", re.IGNORECASE
)


class ReplacementError(ValueError):
    """Describe an input that cannot be replaced safely."""


class JsonArgumentParser(argparse.ArgumentParser):
    """Return command-line failures in the same JSON format as runtime failures."""

    def error(self, message: str) -> None:
        print(json.dumps({"ok": False, "error": f"argument error: {message}"}, indent=2))
        raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = JsonArgumentParser(
        description="Replace one scaffold-marked SVG module content region after strict validation."
    )
    parser.add_argument("svg", type=Path, help="Source synchronized SVG")
    parser.add_argument("fragment", type=Path, help="UTF-8 SVG fragment to insert")
    parser.add_argument("--module", required=True, help="Lowercase hyphen-case module ID")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--in-place", action="store_true", help="Atomically update the source SVG")
    destination.add_argument("--output", type=Path, help="Atomically write the exact output path")
    return parser.parse_args()


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def namespace(name: str) -> str | None:
    if not name.startswith("{"):
        return None
    return name[1:].split("}", 1)[0]


def parse_xml(data: bytes, label: str, *, comments: bool = False) -> ET.Element:
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=comments))
        return ET.fromstring(data, parser=parser)
    except ET.ParseError as exc:
        raise ReplacementError(f"{label} is not well-formed XML: {exc}") from exc


def element_nodes(root: ET.Element) -> Iterator[ET.Element]:
    for element in root.iter():
        if isinstance(element.tag, str):
            yield element


def parse_finite_decimal(raw: str | None, label: str) -> Decimal:
    if raw is None:
        raise ReplacementError(f"{label} is missing")
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ReplacementError(f"{label} must be numeric") from exc
    if not value.is_finite():
        raise ReplacementError(f"{label} must be finite")
    return value


def parse_revision(raw: str | None, label: str) -> int:
    if raw is None or not re.fullmatch(r"0|[1-9][0-9]*", raw):
        raise ReplacementError(f"{label} must be a non-negative integer")
    return int(raw)


def fmt_number(value: float) -> str:
    if not math.isfinite(value):
        raise ReplacementError("planned module shell contains a non-finite number")
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def planned_shell_contract(planned_module: dict[str, Any], module_id: str) -> dict[str, str]:
    """Reconstruct the exact scaffold shell from the embedded module plan."""

    region = planned_module.get("region")
    if (
        not isinstance(region, list)
        or len(region) != 4
        or any(not isinstance(item, (int, float)) or isinstance(item, bool) for item in region)
    ):
        raise ReplacementError(f"planned module {module_id!r} region must be [x, y, width, height]")
    x, y, width, height = (float(item) for item in region)
    if not all(math.isfinite(item) for item in (x, y, width, height)) or width <= 0 or height <= 0:
        raise ReplacementError(f"planned module {module_id!r} region must contain finite positive dimensions")

    question = planned_module.get("question")
    claim = planned_module.get("claim")
    if not isinstance(question, str) or not question.strip() or not isinstance(claim, str) or not claim.strip():
        raise ReplacementError(f"planned module {module_id!r} needs question and claim text")
    question_width = max(28, min(96, int((width - 48) / 6.2)))
    claim_width = max(24, min(74, int((width - 48) / 8.6)))
    question_lines = textwrap.wrap(question, width=question_width, break_long_words=False)[:2] or [question]
    claim_lines = textwrap.wrap(claim, width=claim_width, break_long_words=False)[:3] or [claim]
    claim_y = 74 + 14 * (len(question_lines) - 1)
    content_top = float(claim_y + 20 * (len(claim_lines) - 1) + 32)
    content_height = height - content_top
    if content_height <= 0:
        raise ReplacementError(f"planned module {module_id!r} has no positive content body")

    top = fmt_number(content_top)
    return {
        "moduleTransform": f"translate({fmt_number(x)} {fmt_number(y)})",
        "contentTop": top,
        "contentTransform": f"translate(0 {top})",
        "contentOrigin": f"0 {top}",
        "contentWidth": fmt_number(width),
        "contentHeight": fmt_number(content_height),
    }


def require_shell_attribute(element: ET.Element, name: str, expected: str, label: str) -> None:
    actual = element.get(name)
    if actual != expected:
        raise ReplacementError(
            f"{label} shell attribute {name!r} must equal {expected!r}; received {actual!r}"
        )


def validate_reference(value: str, label: str) -> None:
    stripped = value.strip()
    if not stripped:
        return
    if SAFE_DATA_IMAGE_RE.match(stripped):
        return
    if REMOTE_SCHEME_RE.search(stripped):
        raise ReplacementError(f"{label} contains a remote or executable reference")
    for match in URL_FUNCTION_RE.finditer(stripped):
        target = match.group(2).strip()
        if not target.startswith("#"):
            raise ReplacementError(f"{label} contains a non-local url() reference")


def validate_fragment(fragment: bytes) -> tuple[ET.Element, bytes]:
    if not fragment:
        raise ReplacementError("fragment is empty")
    content = fragment[3:] if fragment.startswith(b"\xef\xbb\xbf") else fragment
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReplacementError("fragment must be valid UTF-8") from exc

    declaration = XML_DECLARATION_RE.match(content)
    if declaration:
        encoding = re.search(rb"\bencoding\s*=\s*([\"'])(.*?)\1", declaration.group("body"), re.IGNORECASE)
        if encoding and encoding.group(2).lower().replace(b"_", b"-") not in {b"utf-8", b"utf8"}:
            raise ReplacementError("fragment XML declaration must use UTF-8 encoding")
        content = content[declaration.end() :]

    lowered = content.lower()
    if b"<?" in content:
        raise ReplacementError("fragment must not contain processing instructions")
    if b"<!doctype" in lowered or b"<!entity" in lowered:
        raise ReplacementError("fragment must not contain a document type or entity declaration")
    if b"sync-content-start:" in lowered or b"sync-content-end:" in lowered:
        raise ReplacementError("fragment must not declare synchronization content markers")

    wrapped = b'<svg xmlns="http://www.w3.org/2000/svg">' + content + b"</svg>"
    document_root = parse_xml(wrapped, "fragment")
    if document_root.text and document_root.text.strip():
        raise ReplacementError("fragment must contain SVG elements, not top-level text")
    top_level = [child for child in document_root if isinstance(child.tag, str)]
    if len(top_level) != 1:
        raise ReplacementError("fragment shell must contain exactly one top-level module-content <g>")
    for child in document_root:
        if child.tail and child.tail.strip():
            raise ReplacementError("fragment must not contain top-level text between elements")

    fragment_root = top_level[0]
    if namespace(fragment_root.tag) != SVG_NS or local_name(fragment_root.tag) != "g":
        raise ReplacementError("fragment shell root must be an SVG <g> element")
    if fragment_root.get("class") != "module-content":
        raise ReplacementError("fragment shell root class must equal 'module-content'")

    ids: list[str] = []
    for element in element_nodes(fragment_root):
        if namespace(element.tag) != SVG_NS:
            raise ReplacementError(f"fragment element {local_name(element.tag)!r} is not in the SVG namespace")
        tag = local_name(element.tag).lower()
        if tag in {"script", "style"}:
            raise ReplacementError(f"fragment must not contain <{tag}> elements")
        if element.get("data-placeholder") == "true":
            raise ReplacementError("fragment still contains data-placeholder=\"true\"")
        if set(element.get("class", "").split()) & {"module-placeholder", "placeholder-mark", "placeholder-value"}:
            raise ReplacementError("fragment still contains scaffold placeholder classes")
        element_id = element.get("id")
        if element_id is not None:
            ids.append(element_id)
        for raw_name, value in element.attrib.items():
            name = local_name(raw_name).lower()
            if name == "style":
                raise ReplacementError("fragment must not contain style attributes")
            if name.startswith("on"):
                raise ReplacementError(f"fragment must not contain event attribute {name!r}")
            validate_reference(value, f"attribute {name!r}")
            if name in {"href", "src"}:
                target = value.strip()
                if target and not target.startswith("#") and not SAFE_DATA_IMAGE_RE.match(target):
                    raise ReplacementError(f"attribute {name!r} must use a local #id or embedded raster image")

    duplicates = sorted(item for item, count in collections.Counter(ids).items() if count > 1)
    if duplicates:
        raise ReplacementError(f"fragment contains duplicate IDs: {duplicates}")
    return fragment_root, content


def find_plan(root: ET.Element) -> dict[str, Any]:
    metadata = [
        element
        for element in element_nodes(root)
        if local_name(element.tag) == "metadata" and element.get("id") == "sync-composition-plan"
    ]
    if len(metadata) != 1:
        raise ReplacementError("source SVG must contain exactly one sync-composition-plan metadata element")
    raw = "".join(metadata[0].itertext()).strip()
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ReplacementError(f"embedded composition plan is not valid JSON: {exc}") from exc
    if not isinstance(plan, dict):
        raise ReplacementError("embedded composition plan must be a JSON object")
    return plan


def find_module(root: ET.Element, module_id: str) -> ET.Element:
    modules = [
        element
        for element in element_nodes(root)
        if local_name(element.tag) == "g" and element.get("data-module-id") == module_id
    ]
    if len(modules) != 1:
        raise ReplacementError(f"source SVG must contain exactly one module group for {module_id!r}")
    module = modules[0]
    if module.get("data-placeholder") != "true":
        raise ReplacementError(f"module {module_id!r} is not marked data-placeholder=\"true\"")
    return module


def marker_nodes(
    root: ET.Element,
    module: ET.Element,
    module_id: str,
) -> tuple[ET.Element, ET.Element, ET.Element]:
    start_text = f"sync-content-start:{module_id}"
    end_text = f"sync-content-end:{module_id}"
    starts = [element for element in root.iter() if element.tag is ET.Comment and (element.text or "").strip() == start_text]
    ends = [element for element in root.iter() if element.tag is ET.Comment and (element.text or "").strip() == end_text]
    if len(starts) != 1 or len(ends) != 1:
        raise ReplacementError(f"module {module_id!r} must have exactly one start marker and one end marker")

    parents = {child: parent for parent in root.iter() for child in parent}
    start_parent = parents.get(starts[0])
    end_parent = parents.get(ends[0])
    if start_parent is None or start_parent is not end_parent:
        raise ReplacementError(f"module {module_id!r} markers must share one XML parent")

    cursor: ET.Element | None = start_parent
    belongs_to_module = False
    while cursor is not None:
        if cursor is module:
            belongs_to_module = True
            break
        cursor = parents.get(cursor)
    if not belongs_to_module:
        raise ReplacementError(f"module {module_id!r} markers are not inside its module group")

    children = list(start_parent)
    if children.index(starts[0]) >= children.index(ends[0]):
        raise ReplacementError(f"module {module_id!r} end marker precedes its start marker")
    return starts[0], ends[0], start_parent


def module_plan(plan: dict[str, Any], module_id: str) -> dict[str, Any]:
    modules = plan.get("modules")
    if not isinstance(modules, list):
        raise ReplacementError("embedded plan modules must be an array")
    matches = [item for item in modules if isinstance(item, dict) and item.get("id") == module_id]
    if len(matches) != 1:
        raise ReplacementError(f"embedded plan must contain exactly one module definition for {module_id!r}")
    return matches[0]


def validate_content_shell(
    element: ET.Element,
    contract: dict[str, str],
    module_id: str,
    *,
    expected_class: str,
    label: str,
) -> None:
    if namespace(element.tag) != SVG_NS or local_name(element.tag) != "g":
        raise ReplacementError(f"{label} shell must be an SVG <g>")
    require_shell_attribute(element, "class", expected_class, label)
    require_shell_attribute(element, "transform", contract["contentTransform"], label)
    require_shell_attribute(element, "data-module-content-for", module_id, label)
    require_shell_attribute(element, "data-content-origin", contract["contentOrigin"], label)
    require_shell_attribute(element, "data-content-width", contract["contentWidth"], label)
    require_shell_attribute(element, "data-content-height", contract["contentHeight"], label)
    if element.get("data-bind") is not None or element.get("data-role") is not None:
        raise ReplacementError(f"{label} shell must not carry a data binding")


def validate_source_module_shell(
    module: ET.Element,
    planned_module: dict[str, Any],
    module_id: str,
    start_marker: ET.Element,
    end_marker: ET.Element,
    marker_parent: ET.Element,
) -> dict[str, str]:
    contract = planned_shell_contract(planned_module, module_id)
    require_shell_attribute(module, "id", f"module-{module_id}", "source module")
    require_shell_attribute(module, "class", "sync-module", "source module")
    require_shell_attribute(module, "transform", contract["moduleTransform"], "source module")
    require_shell_attribute(module, "data-content-top", contract["contentTop"], "source module")
    asset_type = planned_module.get("assetType")
    if not isinstance(asset_type, str):
        raise ReplacementError(f"planned module {module_id!r} assetType must be a string")
    require_shell_attribute(module, "data-asset-type", asset_type, "source module")

    frames = [
        child
        for child in module
        if isinstance(child.tag, str)
        and local_name(child.tag) == "rect"
        and child.get("class") == "module-frame"
    ]
    if len(frames) != 1:
        raise ReplacementError("source module shell must contain exactly one direct module-frame rect")
    require_shell_attribute(frames[0], "width", contract["contentWidth"], "source module frame")
    planned_height = fmt_number(float(planned_module["region"][3]))
    require_shell_attribute(frames[0], "height", planned_height, "source module frame")

    if marker_parent is not module:
        raise ReplacementError("source module shell requires content markers as direct children")
    children = list(module)
    start_index = children.index(start_marker)
    end_index = children.index(end_marker)
    between = [child for child in children[start_index + 1 : end_index] if isinstance(child.tag, str)]
    if len(between) != 1:
        raise ReplacementError("source module content shell must contain exactly one placeholder <g>")
    validate_content_shell(
        between[0],
        contract,
        module_id,
        expected_class="module-content module-placeholder",
        label="source module content",
    )
    return contract


def validate_fragment_shell(
    fragment_root: ET.Element,
    contract: dict[str, str],
    module_id: str,
) -> None:
    validate_content_shell(
        fragment_root,
        contract,
        module_id,
        expected_class="module-content",
        label="fragment module-content",
    )


def binding_contracts(
    module: ET.Element,
    planned_module: dict[str, Any],
    root_revision: int,
) -> dict[str, tuple[str, str, Decimal, int]]:
    bindings = planned_module.get("bindings")
    if not isinstance(bindings, list) or not bindings:
        raise ReplacementError("planned module must contain at least one binding")

    contracts: dict[str, tuple[str, str, Decimal, int]] = {}
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            raise ReplacementError(f"planned binding {index} must be an object")
        selector = binding.get("selector")
        match = ROLE_SELECTOR_RE.fullmatch(selector) if isinstance(selector, str) else None
        if not match:
            raise ReplacementError(f"planned binding {index} must use a local data-role selector")
        role = match.group(1) or match.group(2)
        value = binding.get("value")
        channel = binding.get("channel")
        if not isinstance(value, str) or not isinstance(channel, str):
            raise ReplacementError(f"planned binding {index} needs string value and channel fields")
        if role in contracts:
            raise ReplacementError(f"planned module repeats data-role {role!r}")

        targets = [element for element in element_nodes(module) if element.get("data-role") == role]
        if not targets:
            raise ReplacementError(f"source module role {role!r} has no current binding target")
        currents: set[Decimal] = set()
        revisions: set[int] = set()
        for target in targets:
            if target.get("data-bind") != value or target.get("data-channel") != channel:
                raise ReplacementError(f"source module role {role!r} does not match its plan binding")
            currents.add(parse_finite_decimal(target.get("data-current-value"), f"source role {role!r} data-current-value"))
            revisions.add(parse_revision(target.get("data-sync-revision"), f"source role {role!r} data-sync-revision"))
        if len(currents) != 1 or len(revisions) != 1:
            raise ReplacementError(f"source module role {role!r} has inconsistent current state")
        revision = next(iter(revisions))
        if revision != root_revision:
            raise ReplacementError(f"source module role {role!r} revision differs from the root revision")
        contracts[role] = (value, channel, next(iter(currents)), revision)
    return contracts


def validate_fragment_bindings(
    fragment_root: ET.Element,
    contracts: dict[str, tuple[str, str, Decimal, int]],
) -> None:
    fragment_elements = [element for element in element_nodes(fragment_root) if element is not fragment_root]
    for role, (value, channel, current, revision) in contracts.items():
        targets = [element for element in fragment_elements if element.get("data-role") == role]
        if not targets:
            raise ReplacementError(f"fragment does not resolve planned data-role {role!r}")
        for target in targets:
            if target.get("data-bind") != value:
                raise ReplacementError(f"fragment role {role!r} data-bind must equal {value!r}")
            if target.get("data-channel") != channel:
                raise ReplacementError(f"fragment role {role!r} data-channel must equal {channel!r}")
            actual_current = parse_finite_decimal(
                target.get("data-current-value"), f"fragment role {role!r} data-current-value"
            )
            actual_revision = parse_revision(
                target.get("data-sync-revision"), f"fragment role {role!r} data-sync-revision"
            )
            if actual_current != current:
                raise ReplacementError(f"fragment role {role!r} data-current-value differs from the source state")
            if actual_revision != revision:
                raise ReplacementError(f"fragment role {role!r} data-sync-revision differs from the source state")

    for element in fragment_elements:
        if element.get("data-bind") is None:
            continue
        role = element.get("data-role")
        if role not in contracts:
            raise ReplacementError(f"fragment contains undeclared bound data-role {role!r}")


def comment_span(data: bytes, kind: str, module_id: str) -> tuple[int, int]:
    pattern = re.compile(
        rb"<!--[ \t\r\n]*sync-content-"
        + kind.encode("ascii")
        + rb":"
        + re.escape(module_id.encode("ascii"))
        + rb"[ \t\r\n]*-->"
    )
    matches = list(pattern.finditer(data))
    if len(matches) != 1:
        raise ReplacementError(f"raw SVG must contain exactly one {kind} marker for module {module_id!r}")
    return matches[0].span()


def start_tags(data: bytes) -> Iterator[tuple[int, int, bytes]]:
    """Yield XML start tags while skipping comments, CDATA, declarations, and end tags."""

    cursor = 0
    length = len(data)
    while cursor < length:
        start = data.find(b"<", cursor)
        if start < 0:
            return
        if data.startswith(b"<!--", start):
            end = data.find(b"-->", start + 4)
            if end < 0:
                return
            cursor = end + 3
            continue
        if data.startswith(b"<![CDATA[", start):
            end = data.find(b"]]>", start + 9)
            if end < 0:
                return
            cursor = end + 3
            continue
        if data.startswith(b"<?", start):
            end = data.find(b"?>", start + 2)
            if end < 0:
                return
            cursor = end + 2
            continue
        if data.startswith((b"</", b"<!"), start):
            end = data.find(b">", start + 2)
            if end < 0:
                return
            cursor = end + 1
            continue

        quote: int | None = None
        end = start + 1
        while end < length:
            byte = data[end]
            if quote is None and byte in (34, 39):
                quote = byte
            elif quote == byte:
                quote = None
            elif quote is None and byte == 62:
                break
            end += 1
        if end >= length:
            return
        yield start, end + 1, data[start : end + 1]
        cursor = end + 1


def attribute_value(tag: bytes, name: str) -> str | None:
    pattern = re.compile(
        rb"(?<![A-Za-z0-9_.:-])"
        + re.escape(name.encode("ascii"))
        + rb"[ \t\r\n]*=[ \t\r\n]*([\"'])(.*?)\1",
        re.DOTALL,
    )
    matches = list(pattern.finditer(tag))
    if not matches:
        return None
    if len(matches) != 1:
        raise ReplacementError(f"module start tag repeats attribute {name!r}")
    try:
        return html.unescape(matches[0].group(2).decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ReplacementError("module start tag is not valid UTF-8") from exc


def remove_placeholder_attribute(data: bytes, module_id: str, before_offset: int) -> bytes:
    module_tags: list[tuple[int, int, bytes]] = []
    for start, end, tag in start_tags(data):
        name_match = re.match(rb"<([A-Za-z_][A-Za-z0-9_.:-]*)", tag)
        if not name_match or name_match.group(1).split(b":")[-1] != b"g":
            continue
        if attribute_value(tag, "data-module-id") == module_id:
            module_tags.append((start, end, tag))
    if len(module_tags) != 1:
        raise ReplacementError(f"raw SVG must contain exactly one module start tag for {module_id!r}")
    start, end, tag = module_tags[0]
    if end > before_offset:
        raise ReplacementError(f"module {module_id!r} start tag must precede its content markers")

    pattern = re.compile(
        rb"[ \t\r\n]+data-placeholder[ \t\r\n]*=[ \t\r\n]*([\"'])true\1"
    )
    matches = list(pattern.finditer(tag))
    if len(matches) != 1:
        raise ReplacementError(f"module {module_id!r} start tag must contain one data-placeholder=\"true\"")
    absolute_start = start + matches[0].start()
    absolute_end = start + matches[0].end()
    return data[:absolute_start] + data[absolute_end:]


def reject_duplicate_document_ids(root: ET.Element) -> None:
    ids = [element.get("id") for element in element_nodes(root) if element.get("id") is not None]
    duplicates = sorted(item for item, count in collections.Counter(ids).items() if count > 1)
    if duplicates:
        raise ReplacementError(f"resulting SVG contains duplicate IDs: {duplicates}")


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, stat.S_IMODE(mode))
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def replace(args: argparse.Namespace) -> dict[str, Any]:
    if not ID_RE.fullmatch(args.module):
        raise ReplacementError("--module must be lowercase hyphen-case")

    source_path = args.svg.resolve()
    fragment_path = args.fragment.resolve()
    if not source_path.is_file():
        raise ReplacementError(f"source SVG does not exist: {source_path}")
    if not fragment_path.is_file():
        raise ReplacementError(f"fragment does not exist: {fragment_path}")
    if source_path == fragment_path:
        raise ReplacementError("source SVG and fragment must be different files")

    target_path = source_path if args.in_place else args.output.resolve()
    if not args.in_place and target_path == source_path:
        raise ReplacementError("use --in-place when the output path is the source SVG")
    if target_path == fragment_path:
        raise ReplacementError("output path must not overwrite the fragment")

    source = source_path.read_bytes()
    fragment = fragment_path.read_bytes()
    source_root = parse_xml(source, "source SVG", comments=True)
    if local_name(source_root.tag) != "svg" or namespace(source_root.tag) != SVG_NS:
        raise ReplacementError("source document root must be an SVG element in the SVG namespace")

    plan = find_plan(source_root)
    planned_module = module_plan(plan, args.module)
    module = find_module(source_root, args.module)
    start_marker, end_marker, marker_parent = marker_nodes(source_root, module, args.module)
    shell_contract = validate_source_module_shell(
        module,
        planned_module,
        args.module,
        start_marker,
        end_marker,
        marker_parent,
    )
    root_revision = parse_revision(source_root.get("data-state-revision"), "root data-state-revision")
    contracts = binding_contracts(module, planned_module, root_revision)

    fragment_root, fragment_content = validate_fragment(fragment)
    validate_fragment_shell(fragment_root, shell_contract, args.module)
    validate_fragment_bindings(fragment_root, contracts)

    start_start, start_end = comment_span(source, "start", args.module)
    end_start, _ = comment_span(source, "end", args.module)
    if start_end > end_start:
        raise ReplacementError(f"module {args.module!r} raw end marker precedes its start marker")

    with_fragment = source[:start_end] + fragment_content + source[end_start:]
    candidate = remove_placeholder_attribute(with_fragment, args.module, start_start)
    candidate_root = parse_xml(candidate, "resulting SVG", comments=True)
    reject_duplicate_document_ids(candidate_root)
    resulting_modules = [
        element
        for element in element_nodes(candidate_root)
        if local_name(element.tag) == "g" and element.get("data-module-id") == args.module
    ]
    if len(resulting_modules) != 1 or resulting_modules[0].get("data-placeholder") is not None:
        raise ReplacementError("resulting module did not remove data-placeholder exactly once")

    atomic_write(target_path, candidate, source_path.stat().st_mode)
    return {
        "ok": True,
        "source": str(source_path),
        "fragment": str(fragment_path),
        "output": str(target_path),
        "module": args.module,
        "bindingCount": len(contracts),
        "inputBytes": len(source),
        "fragmentBytes": len(fragment),
        "insertedBytes": len(fragment_content),
        "outputBytes": len(candidate),
        "inPlace": bool(args.in_place),
        "removedPlaceholder": True,
    }


def main() -> int:
    args = parse_args()
    try:
        result = replace(args)
    except (OSError, ReplacementError) as exc:
        result = {"ok": False, "error": str(exc)}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

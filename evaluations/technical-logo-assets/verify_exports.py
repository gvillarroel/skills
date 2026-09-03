#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate technical-logo-assets evaluation exports without trusting the agent."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


FORBIDDEN_ELEMENTS = {"audio", "foreignobject", "iframe", "script", "video"}
URL_ATTRIBUTES = {"href", "src"}
PAINT_RE = re.compile(r"(?:fill|stroke)\s*:\s*([^;]+)", re.IGNORECASE)


def local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1].lower()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_svg_tree(root: ET.Element, prefix: str, errors: list[str]) -> tuple[list[str], int]:
    """Reject raster, external, and active resources, including nested SVG data images."""
    paints: list[str] = []
    embedded_vector_images = 0
    for element in root.iter():
        tag = local_name(element.tag)
        require(tag not in FORBIDDEN_ELEMENTS, f"{prefix}: forbidden <{tag}> element", errors)
        for attribute, value in element.attrib.items():
            attribute_name = local_name(attribute)
            lower_value = value.strip().lower()
            require(not attribute_name.startswith("on"), f"{prefix}: active event attribute {attribute_name}", errors)
            if attribute_name in URL_ATTRIBUTES:
                if tag == "image" and lower_value.startswith("data:image/svg+xml;base64,"):
                    try:
                        nested_bytes = base64.b64decode(value.split(",", 1)[1], validate=True)
                        nested_root = ET.fromstring(nested_bytes)
                    except (ValueError, ET.ParseError) as exc:
                        errors.append(f"{prefix}: invalid embedded vector SVG: {exc}")
                    else:
                        embedded_vector_images += 1
                        nested_paints, nested_images = scan_svg_tree(nested_root, prefix, errors)
                        paints.extend(nested_paints)
                        embedded_vector_images += nested_images
                else:
                    require(
                        lower_value.startswith("#"),
                        f"{prefix}: external or non-vector embedded resource in {attribute_name}",
                        errors,
                    )
            if attribute_name in {"fill", "stroke"} and lower_value not in {"", "none"}:
                paints.append(lower_value)
            if attribute_name == "style":
                paints.extend(match.group(1).strip().lower() for match in PAINT_RE.finditer(value))
    return paints, embedded_vector_images


def validate_svg(
    path: Path,
    *,
    logo_id: str,
    variant: str,
    requested_variant: str,
    color: str | None,
    license_id: str,
    errors: list[str],
) -> dict[str, object]:
    prefix = path.name
    raw = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        errors.append(f"{prefix}: invalid SVG XML: {exc}")
        return {"path": str(path), "validXml": False}

    require(local_name(root.tag) == "svg", f"{prefix}: root is not svg", errors)
    require(root.get("width") == "256", f"{prefix}: width is not 256", errors)
    require(root.get("height") == "256", f"{prefix}: height is not 256", errors)
    require(root.get("viewBox") == "0 0 256 256", f"{prefix}: unexpected viewBox", errors)
    require(
        root.get("preserveAspectRatio") == "xMidYMid meet",
        f"{prefix}: preserveAspectRatio is not xMidYMid meet",
        errors,
    )
    require(root.get("data-logo-id") == logo_id, f"{prefix}: wrong data-logo-id", errors)
    require(root.get("data-logo-variant") == variant, f"{prefix}: wrong data-logo-variant", errors)
    require(root.get("data-vector-only") == "true", f"{prefix}: not labeled vector-only", errors)

    paints, embedded_vector_images = scan_svg_tree(root, prefix, errors)

    lower_raw = raw.lower()
    require(
        re.search(r"data:image/(?!svg\+xml)", lower_raw) is None,
        f"{prefix}: embedded raster payload",
        errors,
    )
    require("javascript:" not in lower_raw, f"{prefix}: javascript URL", errors)

    if color is not None:
        require(root.get("data-color-value", "").lower() == color, f"{prefix}: wrong data-color-value", errors)
        require(color in lower_raw, f"{prefix}: requested fixed color missing", errors)
        require("currentcolor" not in lower_raw, f"{prefix}: fixed export still contains currentColor", errors)
    if variant == "mono-white":
        require(bool(paints), f"{prefix}: no paint values found", errors)
        invalid_paints = sorted({paint for paint in paints if paint not in {"#fff", "#ffffff"}})
        require(not invalid_paints, f"{prefix}: non-white paint values {invalid_paints}", errors)

    provenance_path = path.with_suffix(".provenance.json")
    license_path = path.with_suffix(".license.txt")
    require(provenance_path.is_file(), f"{prefix}: missing provenance sidecar", errors)
    require(license_path.is_file(), f"{prefix}: missing license sidecar", errors)
    provenance: dict[str, object] = {}
    if provenance_path.is_file():
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        source = provenance.get("source", {})
        require(provenance.get("id") == logo_id, f"{prefix}: provenance id mismatch", errors)
        require(provenance.get("variant") == variant, f"{prefix}: provenance variant mismatch", errors)
        require(
            provenance.get("requestedVariant") == requested_variant,
            f"{prefix}: provenance requestedVariant mismatch",
            errors,
        )
        require(provenance.get("vectorOnly") is True, f"{prefix}: provenance not vector-only", errors)
        require(provenance.get("svgSha256") == sha256(path), f"{prefix}: provenance SVG digest mismatch", errors)
        require(isinstance(source, dict) and source.get("licenseId") == license_id, f"{prefix}: license id mismatch", errors)
        require(
            isinstance(source, dict) and bool(source.get("sourceSha256")),
            f"{prefix}: missing source SHA-256",
            errors,
        )
        if color is not None:
            require(provenance.get("color") == color, f"{prefix}: provenance color mismatch", errors)
    if license_path.is_file():
        license_text = license_path.read_text(encoding="utf-8")
        require(len(license_text.strip()) >= 100, f"{prefix}: license sidecar is too short", errors)
        if license_id == "MIT":
            require("MIT License" in license_text, f"{prefix}: MIT license text missing", errors)
        if license_id == "CC-BY-ND-2.0":
            require("Attribution-NoDerivs 2.0" in license_text, f"{prefix}: CC-BY-ND text missing", errors)

    return {
        "path": str(path),
        "validXml": True,
        "id": logo_id,
        "variant": variant,
        "requestedVariant": requested_variant,
        "licenseId": license_id,
        "sha256": sha256(path),
        "elementCount": sum(1 for _ in root.iter()),
        "paintCount": len(paints),
        "embeddedVectorImageCount": embedded_vector_images,
    }


def validate_contract(deliverable: Path, errors: list[str]) -> list[dict[str, object]]:
    expected = {
        "lambda-choice.json",
        "python-blue.license.txt",
        "python-blue.provenance.json",
        "python-blue.svg",
    }
    actual = {path.name for path in deliverable.iterdir() if path.is_file()}
    require(actual == expected, f"contract: output set mismatch: {sorted(actual ^ expected)}", errors)
    results = [
        validate_svg(
            deliverable / "python-blue.svg",
            logo_id="devicon-python",
            variant="custom-color",
            requested_variant="adaptive",
            color="#007298",
            license_id="MIT",
            errors=errors,
        )
    ]
    choice = json.loads((deliverable / "lambda-choice.json").read_text(encoding="utf-8"))
    require(isinstance(choice, list) and len(choice) == 1, "contract: Lambda choice is not one result", errors)
    if isinstance(choice, list) and len(choice) == 1:
        item = choice[0]
        require(item.get("id") == "aws-compute-lambda", "contract: wrong Lambda id", errors)
        require(item.get("variant") == "adaptive", "contract: wrong requested Lambda variant", errors)
        require(item.get("available") is False, "contract: restricted Lambda variant marked available", errors)
        require(item.get("path") is None, "contract: restricted Lambda variant has a path", errors)
        require(item.get("reason") == "license-no-derivatives", "contract: wrong Lambda refusal reason", errors)
        require(item.get("licenseId") == "CC-BY-ND-2.0", "contract: wrong Lambda license", errors)
        require(item.get("recolorable") is False, "contract: Lambda incorrectly recolorable", errors)
    return results


def validate_naturalistic(deliverable: Path, errors: list[str]) -> list[dict[str, object]]:
    expected = {
        "kubernetes-white.license.txt",
        "kubernetes-white.provenance.json",
        "kubernetes-white.svg",
        "lambda-color.license.txt",
        "lambda-color.provenance.json",
        "lambda-color.svg",
        "python-red.license.txt",
        "python-red.provenance.json",
        "python-red.svg",
        "selection-notes.md",
    }
    actual = {path.name for path in deliverable.iterdir() if path.is_file()}
    require(actual == expected, f"naturalistic: output set mismatch: {sorted(actual ^ expected)}", errors)
    results = [
        validate_svg(
            deliverable / "python-red.svg",
            logo_id="devicon-python",
            variant="custom-color",
            requested_variant="adaptive",
            color="#9e1b32",
            license_id="MIT",
            errors=errors,
        ),
        validate_svg(
            deliverable / "kubernetes-white.svg",
            logo_id="devicon-kubernetes",
            variant="mono-white",
            requested_variant="mono-white",
            color=None,
            license_id="MIT",
            errors=errors,
        ),
        validate_svg(
            deliverable / "lambda-color.svg",
            logo_id="aws-compute-lambda",
            variant="color",
            requested_variant="color",
            color=None,
            license_id="CC-BY-ND-2.0",
            errors=errors,
        ),
    ]
    notes = (deliverable / "selection-notes.md").read_text(encoding="utf-8").lower()
    for token in (
        "devicon-python",
        "devicon-kubernetes",
        "aws-compute-lambda",
        "license-no-derivatives",
        "cc-by-nd-2.0",
        "currentcolor",
        "inlined",
        "provenance.json",
        "license.txt",
    ):
        require(token in notes, f"naturalistic: selection notes omit {token}", errors)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--case", choices=("contract", "naturalistic"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    deliverable = workspace / "deliverable"
    errors: list[str] = []
    require(deliverable.is_dir(), f"missing deliverable directory: {deliverable}", errors)
    results: list[dict[str, object]] = []
    if deliverable.is_dir():
        results = (
            validate_contract(deliverable, errors)
            if args.case == "contract"
            else validate_naturalistic(deliverable, errors)
        )

    report = {
        "schemaVersion": 1,
        "case": args.case,
        "ok": not errors,
        "workspace": str(workspace),
        "svgResults": results,
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

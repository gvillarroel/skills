#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#   "numpy>=2.0",
#   "opencv-python-headless>=4.10",
#   "pillow>=11.0",
#   "vtracer==0.6.15",
# ]
# ///
"""Create a provenance-rich, palette-locked SVG with the OSS VTracer backend."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
from typing import Any
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image
import vtracer


SKILL_ROOT = Path(__file__).resolve().parents[1]
VECTORIZE_ART_PATH = Path(__file__).with_name("vectorize_art.py")
SVG_NS = "http://www.w3.org/2000/svg"
PATTERN_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-f]{6}$")


def load_vectorize_art() -> Any:
    spec = importlib.util.spec_from_file_location(
        "vectorize_art_shared", VECTORIZE_ART_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load shared vectorizer helpers: {VECTORIZE_ART_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VA = load_vectorize_art()


class VTracerError(RuntimeError):
    """Raised when the VTracer pipeline cannot satisfy the SVG contract."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def quantized_source_raster(
    rgb: np.ndarray,
    *,
    mode: str,
    colors: int,
    smoothing: float,
    palette_method: str,
    colorset_name: str,
) -> tuple[np.ndarray, dict[str, Any]]:
    contract = VA.load_colorset_contract()
    colorset = contract["colorsets"][colorset_name]

    if mode == "ink":
        mask = VA.prepare_ink_mask(rgb, smoothing)
        background = str(colorset["roles"]["background"]).lower()
        ink = str(colorset["ink"]).lower()
        source_background = "#ffffff"
        source_ink = "#111111"
        quantized = np.empty((*mask.shape, 3), dtype=np.uint8)
        quantized[:] = VA.parse_hex_color(source_background)
        quantized[mask > 0] = VA.parse_hex_color(source_ink)
        return quantized, {
            "background": background,
            "layers": [{"source": "#111111", "target": ink}],
            "source_colors": [source_background, source_ink],
            "target_colors": [background, ink],
        }

    processed = VA.preprocess_color(rgb, mode, smoothing)
    labels, value_to_color, counts_by_value = VA.quantize(
        processed, colors, palette_method
    )
    ordered_values = sorted(
        value_to_color,
        key=lambda value: (-counts_by_value[value], value_to_color[value]),
    )
    background_value = ordered_values[0]
    background = VA.rgb_hex(value_to_color[background_value])
    layers = [
        {
            "id": f"color-{index}",
            "fill": VA.rgb_hex(value_to_color[value]),
            "pixel_count": counts_by_value[value],
        }
        for index, value in enumerate(ordered_values[1:], start=1)
    ]
    mapped_background, mapped_layers, colorset_record = VA.apply_colorset(
        background,
        layers,
        mode=mode,
        colorset_name=colorset_name,
    )
    mapping = colorset_record["mapping"]
    quantized = np.empty((*labels.shape, 3), dtype=np.uint8)
    for value, source_color in value_to_color.items():
        quantized[labels == value] = source_color
    return quantized, {
        "background": mapped_background,
        "layers": mapping[1:],
        "source_colors": [entry["source"] for entry in mapping],
        "target_colors": [entry["target"] for entry in mapping],
    }


def normalize_svg(
    raw_path: Path,
    *,
    output_path: Path,
    pattern_id: str,
    title: str,
    description: str,
    mode: str,
    colorset_name: str,
    width: int,
    height: int,
    rights: dict[str, Any],
    composition_sha256: str,
    palette_contract_sha256: str,
    parameters: dict[str, Any],
    source_colors: list[str],
    target_colors: list[str],
) -> tuple[int, list[str]]:
    try:
        root = ET.parse(raw_path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise VTracerError(f"VTracer emitted malformed SVG: {exc}") from exc
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise VTracerError("VTracer output does not have an SVG root")

    contract = VA.load_colorset_contract()
    allowed_tokens = [
        str(value).lower()
        for value in contract["colorsets"][colorset_name]["allowed"]
    ]
    allowed = set(allowed_tokens)
    normalized_sources = [value.lower() for value in source_colors]
    normalized_targets = [value.lower() for value in target_colors]
    target_by_source = dict(zip(normalized_sources, normalized_targets, strict=True))
    fills: set[str] = set()
    path_count = 0
    path_records: list[tuple[ET.Element, str, int, int]] = []
    for element in root.iter():
        local_name = element.tag.rsplit("}", 1)[-1]
        if local_name in {"image", "script", "foreignObject"}:
            raise VTracerError(f"VTracer output contains forbidden <{local_name}>")
        fill = element.get("fill")
        source_token = ""
        if fill:
            normalized = fill.lower()
            if HEX_COLOR_RE.fullmatch(normalized):
                source_token = VA.nearest_token(normalized, normalized_sources)
                normalized = target_by_source[source_token]
            element.set("fill", normalized)
            fills.add(normalized)
        if local_name == "path":
            path_count += 1
            path_data = element.get("d", "").strip()
            if not path_data or not re.match(r"^[Mm]\s*[-+\d.]", path_data):
                raise VTracerError("VTracer emitted an invalid editable path")
            path_records.append((element, source_token, len(path_data), path_count))
    if mode != "ink":
        anchor_role = "primary" if colorset_name == "colorset1" else "secondary"
        anchor = str(
            contract["colorsets"][colorset_name]["roles"][anchor_role]
        ).lower()
        if anchor not in fills:
            background_source = normalized_sources[0]
            candidates = [
                record for record in path_records if record[1] != background_source
            ] or path_records
            anchor_path = max(
                candidates,
                key=lambda record: (record[2], -record[3]),
            )[0]
            anchor_path.set("fill", anchor)
            fills = {
                str(element.get("fill", "")).lower()
                for element in root.iter()
                if HEX_COLOR_RE.fullmatch(str(element.get("fill", "")).lower())
            }
    unexpected = sorted(fills - allowed)
    if unexpected:
        raise VTracerError(
            f"VTracer emitted colors outside {colorset_name}: {unexpected}"
        )
    if path_count == 0:
        raise VTracerError("VTracer emitted no editable paths")

    root.set("viewBox", f"0 0 {width} {height}")
    root.set("role", "img")
    root.set("data-pattern-id", pattern_id)
    root.set("data-mode", mode)
    root.set("data-tile", "none")
    root.set("data-colorset", colorset_name)
    root.set("data-variation-seed", "0")
    root.set("data-source-sha256", rights["input_sha256"])
    root.set("data-vectorizer", "vtracer-0.6.15")
    root.attrib.pop("version", None)

    metadata = {
        "pattern_id": pattern_id,
        "pipeline": {
            "mode": mode,
            "backend": "vtracer-0.6.15",
            "tile": "none",
            "colorset": colorset_name,
            "palette_contract_sha256": palette_contract_sha256,
            "parameters": parameters,
            "variation": {
                "seed": 0,
                "crop_scale": 1.0,
                "crop_x": 0.5,
                "crop_y": 0.5,
                "rotation": 0.0,
                "flow_strength": 0.0,
                "flow_frequency": 1.0,
                "composition_sha256": composition_sha256,
            },
        },
        "source": rights,
    }
    title_element = ET.Element(f"{{{SVG_NS}}}title")
    title_element.text = title
    description_element = ET.Element(f"{{{SVG_NS}}}desc")
    description_element.text = description
    metadata_element = ET.Element(f"{{{SVG_NS}}}metadata")
    metadata_element.text = json.dumps(
        metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    root.insert(0, metadata_element)
    root.insert(0, description_element)
    root.insert(0, title_element)

    ET.register_namespace("", SVG_NS)
    ET.indent(root, space="  ")
    body = ET.tostring(root, encoding="unicode", short_empty_elements=True)
    VA.atomic_write_text(
        output_path,
        '<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n",
    )
    return path_count, sorted(fills)


def vectorize(args: argparse.Namespace) -> dict[str, Any]:
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if not input_path.is_file():
        raise VTracerError(f"Input image does not exist: {input_path}")
    if output_path.suffix.lower() != ".svg":
        raise VTracerError("Output path must end in .svg")
    pattern_id = args.pattern_id or VA.infer_pattern_id(output_path)
    if not PATTERN_ID_RE.fullmatch(pattern_id):
        raise VTracerError("Pattern ID must be lowercase hyphen-case")
    if not 2 <= args.colors <= 12:
        raise VTracerError("--colors must be between 2 and 12")
    if not 0 <= args.smoothing <= 1:
        raise VTracerError("--smoothing must be between 0 and 1")
    if not 4 <= args.filter_speckle <= 128:
        raise VTracerError("--filter-speckle must be between 4 and 128")

    rights = VA.validate_rights(
        input_path=input_path,
        source_manifest=args.source_manifest.resolve()
        if args.source_manifest
        else None,
        source_id=args.source_id,
        rights_basis=args.rights_basis,
        source_url=args.source_url,
    )
    rgb, source_size = VA.load_image(
        input_path,
        args.max_dimension,
        VA.parse_hex_color("#ffffff"),
    )
    quantized, mapping = quantized_source_raster(
        rgb,
        mode=args.mode,
        colors=args.colors,
        smoothing=args.smoothing,
        palette_method=args.palette_method,
        colorset_name=args.colorset,
    )
    height, width = quantized.shape[:2]
    quantized_bytes = quantized.tobytes(order="C")
    composition_sha256 = sha256_bytes(quantized_bytes)
    palette_contract_sha256 = VA.sha256_path(VA.DEFAULT_COLORSET_CONTRACT)
    parameters = {
        "colors": args.colors,
        "smoothing": args.smoothing,
        "palette_method": args.palette_method,
        "max_dimension": args.max_dimension,
        "filter_speckle": args.filter_speckle,
        "curve_mode": args.curve_mode,
        "hierarchical": "cutout",
        "color_mapping": mapping,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="vtracer-art-") as temporary:
        temporary_root = Path(temporary)
        mapped_path = temporary_root / "mapped.png"
        raw_path = temporary_root / "raw.svg"
        Image.fromarray(quantized).save(mapped_path, format="PNG", optimize=False)
        try:
            vtracer.convert_image_to_svg_py(
                str(mapped_path),
                str(raw_path),
                colormode="color",
                hierarchical="cutout",
                mode=args.curve_mode,
                filter_speckle=args.filter_speckle,
                color_precision=8,
                layer_difference=16,
                corner_threshold=60,
                length_threshold=4.0,
                max_iterations=10,
                splice_threshold=45,
                path_precision=2,
            )
        except Exception as exc:
            raise VTracerError(f"VTracer conversion failed: {exc}") from exc

        source_title = str(rights.get("title") or pattern_id.replace("-", " ").title())
        title = args.title or f"{source_title} — {args.colorset}"
        description = args.description or (
            f"Editable VTracer SVG reinterpretation of {source_title}, reduced to "
            f"the exact {args.colorset} palette from an open source image."
        )
        path_count, fills = normalize_svg(
            raw_path,
            output_path=output_path,
            pattern_id=pattern_id,
            title=title,
            description=description,
            mode=args.mode,
            colorset_name=args.colorset,
            width=width,
            height=height,
            rights=rights,
            composition_sha256=composition_sha256,
            palette_contract_sha256=palette_contract_sha256,
            parameters=parameters,
            source_colors=mapping["source_colors"],
            target_colors=mapping["target_colors"],
        )

    report = {
        "schema_version": 1,
        "ok": True,
        "input": str(args.input),
        "input_sha256": rights["input_sha256"],
        "output": str(args.output),
        "output_sha256": VA.sha256_path(output_path),
        "pattern_id": pattern_id,
        "mode": args.mode,
        "tile": "none",
        "colorset": args.colorset,
        "palette_contract_sha256": palette_contract_sha256,
        "variation_seed": 0,
        "composition_sha256": composition_sha256,
        "parameters": parameters,
        "source_width": source_size[0],
        "source_height": source_size[1],
        "vector_width": width,
        "vector_height": height,
        "render_width": width,
        "render_height": height,
        "palette": fills,
        "path_count": path_count,
        "output_bytes": output_path.stat().st_size,
        "rights": rights,
        "backend": "vtracer-0.6.15",
    }
    if args.report:
        VA.atomic_write_json(args.report.resolve(), report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Map a rights-verified raster to an exact colorset and trace the "
            "result with the open source VTracer backend."
        )
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--mode", choices=("organic", "ink", "stain", "collage"), default="collage")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), required=True)
    parser.add_argument("--colors", type=int, default=8)
    parser.add_argument("--smoothing", type=float, default=0.42)
    parser.add_argument(
        "--palette-method",
        choices=("median-cut", "max-coverage"),
        default="median-cut",
    )
    parser.add_argument("--max-dimension", type=int, default=640)
    parser.add_argument("--filter-speckle", type=int, default=16)
    parser.add_argument("--curve-mode", choices=("polygon", "spline"), default="spline")
    parser.add_argument("--pattern-id")
    parser.add_argument("--title")
    parser.add_argument("--description")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--source-id")
    parser.add_argument(
        "--rights-basis",
        choices=("user-owned", "public-domain", "cc0", "cc-by", "cc-by-sa"),
    )
    parser.add_argument("--source-url")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    report = vectorize(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (VTracerError, VA.VectorizeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)

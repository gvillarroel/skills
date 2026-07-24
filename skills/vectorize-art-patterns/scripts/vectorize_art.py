#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "numpy>=2.0",
#   "opencv-python-headless>=4.10",
#   "pillow>=11.0",
# ]
# ///
"""Simplify raster artwork into deterministic, editable SVG paths."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from typing import Any, Iterable
from xml.sax.saxutils import escape, quoteattr

import cv2
import numpy as np
from PIL import Image, ImageOps


PATTERN_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COLORSET_CONTRACT = SKILL_ROOT / "assets" / "palettes" / "colorsets.json"
COLORSET_NAMES = ("colorset1", "colorset2")
ALLOWED_MANIFEST_LICENSES = (
    "Public-Domain",
    "CC0-",
    "CC-BY-",
    "CC-BY-SA-",
)
MODE_DEFAULTS = {
    "organic": {
        "colors": 7,
        "smoothing": 0.62,
        "detail": 0.50,
        "palette_method": "max-coverage",
    },
    "ink": {
        "colors": 2,
        "smoothing": 0.42,
        "detail": 0.68,
        "palette_method": "median-cut",
    },
    "stain": {
        "colors": 6,
        "smoothing": 0.78,
        "detail": 0.38,
        "palette_method": "max-coverage",
    },
    "collage": {
        "colors": 8,
        "smoothing": 0.30,
        "detail": 0.62,
        "palette_method": "median-cut",
    },
}


class VectorizeError(RuntimeError):
    """Raised when vectorization cannot satisfy the output contract."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(8):
            try:
                os.replace(temp_name, path)
                break
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(0.05 * (attempt + 1))
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_write_text(
        path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    )


def parse_hex_color(value: str) -> tuple[int, int, int]:
    if not HEX_COLOR_RE.fullmatch(value):
        raise VectorizeError(f"Expected a six-digit hex color, received: {value}")
    return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))


def rgb_hex(color: Iterable[int]) -> str:
    red, green, blue = (max(0, min(255, int(value))) for value in color)
    return f"#{red:02x}{green:02x}{blue:02x}"


def load_colorset_contract(
    path: Path = DEFAULT_COLORSET_CONTRACT,
) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VectorizeError(f"Cannot read colorset contract {path}: {exc}") from exc
    if payload.get("schemaVersion") != 1 or not isinstance(
        payload.get("colorsets"), dict
    ):
        raise VectorizeError("Unsupported or malformed colorset contract")
    for name in COLORSET_NAMES:
        colorset = payload["colorsets"].get(name)
        if not isinstance(colorset, dict):
            raise VectorizeError(f"Colorset contract is missing {name}")
        allowed = colorset.get("allowed")
        roles = colorset.get("roles")
        art_sequence = colorset.get("artSequence")
        background_candidates = colorset.get("backgroundCandidates")
        if (
            not isinstance(allowed, list)
            or not allowed
            or not isinstance(roles, dict)
            or not isinstance(art_sequence, list)
            or not art_sequence
            or not isinstance(background_candidates, list)
            or not background_candidates
        ):
            raise VectorizeError(f"Colorset contract fields are incomplete for {name}")
        normalized_allowed = [str(value).lower() for value in allowed]
        if (
            len(normalized_allowed) != len(set(normalized_allowed))
            or any(not HEX_COLOR_RE.fullmatch(value) for value in normalized_allowed)
        ):
            raise VectorizeError(f"Colorset {name} allowed tokens are invalid")
        allowed_set = set(normalized_allowed)
        referenced = [
            *(str(value).lower() for value in roles.values()),
            *(str(value).lower() for value in art_sequence),
            *(str(value).lower() for value in background_candidates),
            str(colorset.get("ink", "")).lower(),
        ]
        if any(value not in allowed_set for value in referenced):
            raise VectorizeError(f"Colorset {name} references a disallowed token")
    return payload


def rgb_to_lab(colors: list[str]) -> np.ndarray:
    rgb = np.asarray(
        [[parse_hex_color(color) for color in colors]],
        dtype=np.uint8,
    )
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[0].astype(np.float64)


def nearest_token(
    source: str,
    candidates: list[str],
) -> str:
    if not candidates:
        raise VectorizeError("Colorset mapping exhausted every candidate token")
    values = rgb_to_lab([source, *candidates])
    distances = np.sum((values[1:] - values[0]) ** 2, axis=1)
    best = min(
        range(len(candidates)),
        key=lambda index: (float(distances[index]), candidates[index]),
    )
    return candidates[best]


def apply_colorset(
    background: str,
    layers: list[dict[str, Any]],
    *,
    mode: str,
    colorset_name: str,
) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    contract = load_colorset_contract()
    colorset = contract["colorsets"][colorset_name]
    allowed = {str(value).lower() for value in colorset["allowed"]}
    source_colors = [background, *(str(layer["fill"]) for layer in layers)]

    if mode == "ink":
        mapped_background = str(colorset["roles"]["background"]).lower()
        mapped_layers = [dict(layer) for layer in layers]
        mapped_layers[0]["fill"] = str(colorset["ink"]).lower()
    else:
        background_candidates = [
            str(value).lower() for value in colorset["backgroundCandidates"]
        ]
        mapped_background = nearest_token(background, background_candidates)
        candidates = [
            str(value).lower()
            for value in colorset["artSequence"]
            if str(value).lower() != mapped_background
        ]
        mapped_layers = [dict(layer) for layer in layers]
        fixed_assignments: dict[int, str] = {}
        if mapped_layers:
            if colorset_name == "colorset1":
                anchor_index = max(
                    range(len(mapped_layers)),
                    key=lambda index: (
                        max(parse_hex_color(str(mapped_layers[index]["fill"])))
                        - min(parse_hex_color(str(mapped_layers[index]["fill"]))),
                        int(mapped_layers[index].get("pixel_count", 0)),
                        -index,
                    ),
                )
                anchor_role = "primary"
            else:
                anchor_index = max(
                    range(len(mapped_layers)),
                    key=lambda index: (
                        int(mapped_layers[index].get("pixel_count", 0)),
                        max(parse_hex_color(str(mapped_layers[index]["fill"])))
                        - min(parse_hex_color(str(mapped_layers[index]["fill"]))),
                        -index,
                    ),
                )
                anchor_role = "secondary"
            anchor = str(colorset["roles"][anchor_role]).lower()
            fixed_assignments[anchor_index] = anchor
            if anchor in candidates:
                candidates.remove(anchor)

        for index, layer in enumerate(mapped_layers):
            if index in fixed_assignments:
                layer["fill"] = fixed_assignments[index]
                continue
            available = candidates or [
                str(value).lower()
                for value in colorset["artSequence"]
                if str(value).lower() != mapped_background
            ]
            target = nearest_token(str(layer["fill"]), available)
            layer["fill"] = target
            if target in candidates:
                candidates.remove(target)

    mapped_colors = [
        mapped_background,
        *(str(layer["fill"]).lower() for layer in mapped_layers),
    ]
    unexpected = sorted(set(mapped_colors) - allowed)
    if unexpected:
        raise VectorizeError(
            f"Colorset mapping produced disallowed tokens: {unexpected}"
        )
    mapping = [
        {"source": source, "target": target}
        for source, target in zip(source_colors, mapped_colors, strict=True)
    ]
    return (
        mapped_background,
        mapped_layers,
        {
            "name": colorset_name,
            "contract_sha256": sha256_path(DEFAULT_COLORSET_CONTRACT),
            "mapping": mapping,
        },
    )


def infer_pattern_id(output: Path) -> str:
    candidate = re.sub(r"[^a-z0-9]+", "-", output.stem.lower()).strip("-")
    return candidate or "vectorized-art"


def validate_rights(
    *,
    input_path: Path,
    source_manifest: Path | None,
    source_id: str | None,
    rights_basis: str | None,
    source_url: str | None,
) -> dict[str, Any]:
    digest = sha256_path(input_path)
    if source_manifest or source_id:
        if not source_manifest or not source_id:
            raise VectorizeError(
                "--source-manifest and --source-id must be supplied together"
            )
        try:
            payload = json.loads(source_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VectorizeError(
                f"Cannot read source manifest {source_manifest}: {exc}"
            ) from exc
        if payload.get("schema_version") != 1 or not isinstance(
            payload.get("assets"), list
        ):
            raise VectorizeError("Unsupported or malformed source manifest")
        record = next(
            (item for item in payload["assets"] if item.get("id") == source_id),
            None,
        )
        if not record:
            raise VectorizeError(f"Source ID not found in manifest: {source_id}")
        license_name = str(record.get("license") or "")
        if "-ND" in license_name.upper() or "-NC" in license_name.upper():
            raise VectorizeError(
                "Manifest license does not permit unrestricted derivative output: "
                f"{license_name}"
            )
        if not any(
            license_name == prefix or license_name.startswith(prefix)
            for prefix in ALLOWED_MANIFEST_LICENSES
        ):
            raise VectorizeError(
                f"Manifest license does not permit derivative output: {license_name}"
            )
        if record.get("transformation_allowed") is not True:
            raise VectorizeError(
                "Manifest does not explicitly allow transformation for this asset"
            )
        if record.get("sha256") != digest:
            raise VectorizeError(
                f"Input SHA-256 does not match manifest record {source_id}"
            )
        expected = (source_manifest.parent / str(record.get("filename"))).resolve()
        if expected != input_path.resolve():
            raise VectorizeError(
                "Input path does not match the manifest filename for the source ID"
            )
        return {
            "basis": "source-manifest",
            "source_id": source_id,
            "license": license_name,
            "license_url": record.get("license_url", ""),
            "source_url": record.get("source_page", ""),
            "attribution": record.get("attribution", ""),
            "attribution_required": bool(record.get("attribution_required")),
            "share_alike": bool(record.get("share_alike")),
            "input_sha256": digest,
        }

    if rights_basis is None:
        raise VectorizeError(
            "Rights evidence is required. Use a verified source manifest or "
            "--rights-basis for a user-provided file."
        )
    if rights_basis != "user-owned" and not source_url:
        raise VectorizeError(
            "--source-url is required for public-domain or Creative Commons input"
        )
    return {
        "basis": rights_basis,
        "source_id": "",
        "license": {
            "user-owned": "User-authorized",
            "public-domain": "Public-Domain",
            "cc0": "CC0-1.0",
            "cc-by": "CC-BY",
            "cc-by-sa": "CC-BY-SA",
        }[rights_basis],
        "license_url": "",
        "source_url": source_url or "",
        "attribution": "",
        "attribution_required": rights_basis in {"cc-by", "cc-by-sa"},
        "share_alike": rights_basis == "cc-by-sa",
        "input_sha256": digest,
    }


def load_image(
    path: Path, max_dimension: int, background: tuple[int, int, int]
) -> tuple[np.ndarray, tuple[int, int]]:
    try:
        with Image.open(path) as raw:
            raw.load()
            source_size = raw.size
            if (
                source_size[0] <= 0
                or source_size[1] <= 0
                or source_size[0] * source_size[1] > 100_000_000
            ):
                raise VectorizeError(
                    f"Unsafe input dimensions: {source_size[0]}x{source_size[1]}"
                )
            image = ImageOps.exif_transpose(raw).convert("RGBA")
    except VectorizeError:
        raise
    except Exception as exc:
        raise VectorizeError(f"Cannot decode raster input {path}: {exc}") from exc

    base = Image.new("RGBA", image.size, (*background, 255))
    base.alpha_composite(image)
    rgb_image = base.convert("RGB")
    scale = min(1.0, max_dimension / max(rgb_image.size))
    if scale < 1.0:
        resized = (
            max(1, int(round(rgb_image.width * scale))),
            max(1, int(round(rgb_image.height * scale))),
        )
        rgb_image = rgb_image.resize(resized, Image.Resampling.LANCZOS)
    return np.asarray(rgb_image, dtype=np.uint8), source_size


def sha256_array(array: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def compose_variation(
    rgb: np.ndarray,
    *,
    seed: int,
    crop_scale: float,
    crop_x: float,
    crop_y: float,
    rotation: float,
    flow_strength: float,
    flow_frequency: float,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Apply a deterministic crop, affine turn, and organic displacement field."""
    height, width = rgb.shape[:2]
    crop_width = max(4, min(width, int(round(width * crop_scale))))
    crop_height = max(4, min(height, int(round(height * crop_scale))))
    x0 = int(round((width - crop_width) * crop_x))
    y0 = int(round((height - crop_height) * crop_y))
    cropped = rgb[y0 : y0 + crop_height, x0 : x0 + crop_width]
    composed = cv2.resize(
        cropped,
        (width, height),
        interpolation=cv2.INTER_LANCZOS4,
    )

    if abs(rotation) > 1e-9:
        matrix = cv2.getRotationMatrix2D(
            ((width - 1) / 2.0, (height - 1) / 2.0),
            rotation,
            1.0,
        )
        composed = cv2.warpAffine(
            composed,
            matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )

    if flow_strength > 1e-9:
        grid_x, grid_y = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
        )
        normalized_x = grid_x / max(1.0, float(width - 1))
        normalized_y = grid_y / max(1.0, float(height - 1))
        phase = math.fmod(seed * 2.399963229728653, math.tau)
        diagonal = normalized_x * 0.63 + normalized_y * 0.37
        counter = normalized_x * 0.41 - normalized_y * 0.79
        displacement_x = flow_strength * (
            np.sin(math.tau * flow_frequency * normalized_y + phase)
            + 0.5
            * np.sin(
                math.tau * flow_frequency * 0.71 * diagonal + phase * 1.7
            )
        ) / 1.5
        displacement_y = flow_strength * (
            np.cos(math.tau * flow_frequency * normalized_x - phase * 0.71)
            + 0.5
            * np.sin(
                math.tau * flow_frequency * 0.53 * counter + phase * 1.3
            )
        ) / 1.5
        composed = cv2.remap(
            composed,
            (grid_x + displacement_x).astype(np.float32),
            (grid_y + displacement_y).astype(np.float32),
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REFLECT_101,
        )

    record = {
        "seed": seed,
        "crop_scale": crop_scale,
        "crop_x": crop_x,
        "crop_y": crop_y,
        "rotation": rotation,
        "flow_strength": flow_strength,
        "flow_frequency": flow_frequency,
        "composition_sha256": sha256_array(composed),
    }
    return composed, record


def odd_kernel(value: float, minimum: int = 3, maximum: int = 15) -> int:
    integer = int(round(value))
    integer = max(minimum, min(maximum, integer))
    return integer if integer % 2 else integer + 1


def preprocess_color(rgb: np.ndarray, mode: str, smoothing: float) -> np.ndarray:
    cv2.setNumThreads(1)
    if mode == "organic":
        sigma_color = 25 + 85 * smoothing
        sigma_space = 3 + 13 * smoothing
        result = cv2.bilateralFilter(
            rgb, d=0, sigmaColor=sigma_color, sigmaSpace=sigma_space
        )
        if smoothing >= 0.72:
            result = cv2.medianBlur(result, 3)
        return result
    if mode == "stain":
        result = cv2.bilateralFilter(
            rgb,
            d=0,
            sigmaColor=35 + 65 * smoothing,
            sigmaSpace=5 + 12 * smoothing,
        )
        kernel = odd_kernel(3 + 10 * smoothing)
        return cv2.GaussianBlur(result, (kernel, kernel), 0)
    if mode == "collage":
        kernel = 3 if smoothing < 0.55 else 5
        result = cv2.medianBlur(rgb, kernel)
        if smoothing > 0.60:
            result = cv2.bilateralFilter(
                result, d=0, sigmaColor=35, sigmaSpace=4
            )
        return result
    raise VectorizeError(f"Unsupported color mode: {mode}")


def quantize(
    rgb: np.ndarray, color_count: int, palette_method: str
) -> tuple[
    np.ndarray,
    dict[int, tuple[int, int, int]],
    dict[int, int],
]:
    image = Image.fromarray(rgb)
    method = {
        "median-cut": Image.Quantize.MEDIANCUT,
        "max-coverage": Image.Quantize.MAXCOVERAGE,
    }[palette_method]
    quantized = image.quantize(
        colors=color_count,
        method=method,
        dither=Image.Dither.NONE,
    )
    labels = np.asarray(quantized, dtype=np.uint8)
    raw_palette = quantized.getpalette()
    if raw_palette is None:
        raise VectorizeError("Pillow did not return a palette")
    active_values = sorted(int(value) for value in np.unique(labels))
    colors = {
        value: tuple(raw_palette[value * 3 : value * 3 + 3])
        for value in active_values
    }
    counts = {
        value: int(np.count_nonzero(labels == value)) for value in active_values
    }
    return labels, colors, counts


def prepare_mask(
    labels: np.ndarray,
    palette_index: int,
    mode: str,
    smoothing: float,
) -> np.ndarray:
    mask = np.where(labels == palette_index, 255, 0).astype(np.uint8)
    if mode in {"organic", "stain"}:
        blur_kernel = odd_kernel(3 + 8 * smoothing, maximum=13)
        mask = cv2.GaussianBlur(mask, (blur_kernel, blur_kernel), 0)
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        morph_size = 3 if smoothing < 0.72 else 5
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (morph_size, morph_size)
        )
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        if smoothing >= 0.60:
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    elif mode == "collage":
        mask = cv2.medianBlur(mask, 3)
    return mask


def prepare_ink_mask(rgb: np.ndarray, smoothing: float) -> np.ndarray:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    kernel = odd_kernel(3 + 8 * smoothing, maximum=11)
    blurred = cv2.GaussianBlur(gray, (kernel, kernel), 0)
    block_size = odd_kernel(
        19 + min(rgb.shape[0], rgb.shape[1]) * 0.025, minimum=15, maximum=61
    )
    mask = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block_size,
        5,
    )
    ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, ellipse)


def contour_points(
    contour: np.ndarray, epsilon: float
) -> list[tuple[float, float]]:
    approximation = cv2.approxPolyDP(contour, epsilon, True)
    points = [
        (float(point[0][0]), float(point[0][1])) for point in approximation
    ]
    deduplicated: list[tuple[float, float]] = []
    for point in points:
        if not deduplicated or point != deduplicated[-1]:
            deduplicated.append(point)
    if len(deduplicated) > 1 and deduplicated[0] == deduplicated[-1]:
        deduplicated.pop()
    return deduplicated


def format_number(value: float) -> str:
    if abs(value - round(value)) < 0.005:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def closed_curve_path(points: list[tuple[float, float]], curved: bool) -> str:
    if len(points) < 3:
        return ""
    commands = [
        f"M {format_number(points[0][0])} {format_number(points[0][1])}"
    ]
    if not curved or len(points) < 5:
        commands.extend(
            f"L {format_number(x)} {format_number(y)}" for x, y in points[1:]
        )
        commands.append("Z")
        return " ".join(commands)

    count = len(points)
    for index in range(count):
        previous = points[(index - 1) % count]
        current = points[index]
        following = points[(index + 1) % count]
        after = points[(index + 2) % count]
        control_one = (
            current[0] + (following[0] - previous[0]) / 6.0,
            current[1] + (following[1] - previous[1]) / 6.0,
        )
        control_two = (
            following[0] - (after[0] - current[0]) / 6.0,
            following[1] - (after[1] - current[1]) / 6.0,
        )
        commands.append(
            "C "
            f"{format_number(control_one[0])} {format_number(control_one[1])} "
            f"{format_number(control_two[0])} {format_number(control_two[1])} "
            f"{format_number(following[0])} {format_number(following[1])}"
        )
    commands.append("Z")
    return " ".join(commands)


def trace_mask(
    mask: np.ndarray,
    *,
    detail: float,
    min_area: float,
    curved: bool,
) -> tuple[str, int, int]:
    contours, _hierarchy = cv2.findContours(
        mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE
    )
    epsilon = 0.25 + (1.0 - detail) * 2.75
    retained: list[tuple[float, int, int, np.ndarray]] = []
    for contour in contours:
        area = abs(float(cv2.contourArea(contour)))
        if area < min_area:
            continue
        x, y, _width, _height = cv2.boundingRect(contour)
        retained.append((-area, y, x, contour))
    retained.sort(key=lambda item: (item[0], item[1], item[2]))

    path_parts: list[str] = []
    point_count = 0
    for _negative_area, _y, _x, contour in retained:
        points = contour_points(contour, epsilon)
        path = closed_curve_path(points, curved=curved)
        if path:
            path_parts.append(path)
            point_count += len(points)
    return " ".join(path_parts), len(path_parts), point_count


def build_layers(
    rgb: np.ndarray,
    *,
    mode: str,
    colors: int,
    smoothing: float,
    detail: float,
    min_area: float,
    background: tuple[int, int, int],
    palette_method: str,
) -> tuple[str, list[dict[str, Any]], dict[str, int]]:
    if mode == "ink":
        mask = prepare_ink_mask(rgb, smoothing)
        path_data, contours, points = trace_mask(
            mask,
            detail=detail,
            min_area=min_area,
            curved=True,
        )
        if not path_data:
            raise VectorizeError(
                "Ink pipeline produced no retained contours; lower --min-area"
            )
        return (
            rgb_hex(background),
            [
                {
                    "id": "ink",
                    "fill": "#111111",
                    "path": path_data,
                    "pixel_count": int(np.count_nonzero(mask)),
                    "contour_count": contours,
                    "point_count": points,
                }
            ],
            {"contour_count": contours, "point_count": points},
        )

    processed = preprocess_color(rgb, mode, smoothing)
    labels, value_to_color, counts_by_value = quantize(
        processed, colors, palette_method
    )
    active_values = sorted(value_to_color)
    ordered_values = sorted(
        active_values,
        key=lambda value: (-counts_by_value[value], value_to_color[value]),
    )
    background_value = ordered_values[0]
    background_hex = rgb_hex(value_to_color[background_value])
    layers: list[dict[str, Any]] = []
    total_contours = 0
    total_points = 0
    curved = mode != "collage"
    for layer_number, palette_value in enumerate(ordered_values[1:], start=1):
        mask = prepare_mask(labels, palette_value, mode, smoothing)
        path_data, contour_count, point_count = trace_mask(
            mask,
            detail=detail,
            min_area=min_area,
            curved=curved,
        )
        if not path_data:
            continue
        layers.append(
            {
                "id": f"color-{layer_number}",
                "fill": rgb_hex(value_to_color[palette_value]),
                "path": path_data,
                "pixel_count": counts_by_value[palette_value],
                "contour_count": contour_count,
                "point_count": point_count,
            }
        )
        total_contours += contour_count
        total_points += point_count
    if not layers:
        raise VectorizeError(
            "Color pipeline produced no retained vector layers; lower --min-area "
            "or increase --colors"
        )
    return background_hex, layers, {
        "contour_count": total_contours,
        "point_count": total_points,
    }


def render_group(
    background: str,
    layers: list[dict[str, Any]],
    width: int,
    height: int,
    outline: float,
) -> str:
    lines = [
        f'<rect width="{width}" height="{height}" fill="{background}"/>',
        '<g id="vector-layers">',
    ]
    for layer in layers:
        stroke = ""
        if outline > 0:
            stroke = (
                f' stroke="{background}" stroke-opacity="0.28" '
                f'stroke-width="{format_number(outline)}" '
                'stroke-linejoin="round"'
            )
        lines.append(
            f'  <path id="{escape(layer["id"])}" fill="{layer["fill"]}" '
            f'fill-rule="evenodd"{stroke} d={quoteattr(layer["path"])}/>'
        )
    lines.append("</g>")
    return "\n".join(lines)


def render_svg(
    *,
    pattern_id: str,
    title: str,
    description: str,
    width: int,
    height: int,
    tile: str,
    mode: str,
    colors: int,
    smoothing: float,
    detail: float,
    min_area: float,
    max_dimension: int,
    palette_method: str,
    colorset: str,
    palette_contract_sha256: str,
    background: str,
    layers: list[dict[str, Any]],
    rights: dict[str, Any],
    outline: float,
    variation: dict[str, Any],
) -> str:
    metadata = {
        "schema_version": 1,
        "pattern_id": pattern_id,
        "pipeline": {
            "mode": mode,
            "colors": colors,
            "smoothing": smoothing,
            "detail": detail,
            "min_area": min_area,
            "max_dimension": max_dimension,
            "palette_method": palette_method,
            "colorset": colorset,
            "palette_contract_sha256": palette_contract_sha256,
            "tile": tile,
            "outline": outline,
            "variation": variation,
        },
        "source": rights,
    }
    metadata_text = escape(
        json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    )
    group_markup = render_group(background, layers, width, height, outline)
    if tile == "none":
        view_width, view_height = width, height
        body = group_markup
    else:
        tile_width = width if tile == "repeat" else width * 2
        tile_height = height if tile == "repeat" else height * 2
        uses = ['<use href="#source-tile"/>']
        if tile == "mirror":
            uses.extend(
                (
                    f'<use href="#source-tile" transform="translate({width * 2} 0) scale(-1 1)"/>',
                    f'<use href="#source-tile" transform="translate(0 {height * 2}) scale(1 -1)"/>',
                    f'<use href="#source-tile" transform="translate({width * 2} {height * 2}) scale(-1 -1)"/>',
                )
            )
        body = "\n".join(
            (
                "<defs>",
                '  <g id="source-tile">',
                "\n".join(f"    {line}" for line in group_markup.splitlines()),
                "  </g>",
                f'  <pattern id="{pattern_id}-pattern" patternUnits="userSpaceOnUse" '
                f'width="{tile_width}" height="{tile_height}">',
                "\n".join(f"    {line}" for line in uses),
                "  </pattern>",
                "</defs>",
                f'<rect width="{tile_width}" height="{tile_height}" '
                f'fill="url(#{pattern_id}-pattern)"/>',
            )
        )
        view_width, view_height = tile_width, tile_height

    return "\n".join(
        (
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {view_width} {view_height}" '
            f'role="img" data-pattern-id="{pattern_id}" data-mode="{mode}" '
            f'data-tile="{tile}" data-colorset="{colorset}" '
            f'data-variation-seed="{variation["seed"]}" '
            f'data-source-sha256="{rights["input_sha256"]}">',
            f"  <title>{escape(title)}</title>",
            f"  <desc>{escape(description)}</desc>",
            f"  <metadata>{metadata_text}</metadata>",
            "\n".join(f"  {line}" for line in body.splitlines()),
            "</svg>",
            "",
        )
    )


def vectorize(args: argparse.Namespace) -> dict[str, Any]:
    input_path = args.input.resolve()
    output_path = args.output.resolve()
    if not input_path.is_file():
        raise VectorizeError(f"Input image does not exist: {input_path}")
    if output_path.suffix.lower() != ".svg":
        raise VectorizeError("Output path must end in .svg")
    pattern_id = args.pattern_id or infer_pattern_id(output_path)
    if not PATTERN_ID_RE.fullmatch(pattern_id):
        raise VectorizeError("Pattern ID must be lowercase hyphen-case")
    if not 2 <= args.colors <= 16:
        raise VectorizeError("--colors must be between 2 and 16")
    if not 0.0 <= args.smoothing <= 1.0:
        raise VectorizeError("--smoothing must be between 0 and 1")
    if not 0.0 <= args.detail <= 1.0:
        raise VectorizeError("--detail must be between 0 and 1")
    if not 4 <= args.max_dimension <= 2400:
        raise VectorizeError("--max-dimension must be between 4 and 2400")
    if args.min_area <= 0:
        raise VectorizeError("--min-area must be positive")
    if args.outline < 0 or args.outline > 8:
        raise VectorizeError("--outline must be between 0 and 8")
    if args.variation_seed < 0 or args.variation_seed > 2_147_483_647:
        raise VectorizeError("--variation-seed must be between 0 and 2147483647")
    if not 0.35 <= args.crop_scale <= 1.0:
        raise VectorizeError("--crop-scale must be between 0.35 and 1")
    if not 0.0 <= args.crop_x <= 1.0 or not 0.0 <= args.crop_y <= 1.0:
        raise VectorizeError("--crop-x and --crop-y must be between 0 and 1")
    if not -180.0 <= args.rotation <= 180.0:
        raise VectorizeError("--rotation must be between -180 and 180")
    if not 0.0 <= args.flow_strength <= 64.0:
        raise VectorizeError("--flow-strength must be between 0 and 64")
    if not 0.25 <= args.flow_frequency <= 8.0:
        raise VectorizeError("--flow-frequency must be between 0.25 and 8")

    background_rgb = parse_hex_color(args.background)
    rights = validate_rights(
        input_path=input_path,
        source_manifest=args.source_manifest.resolve()
        if args.source_manifest
        else None,
        source_id=args.source_id,
        rights_basis=args.rights_basis,
        source_url=args.source_url,
    )
    rgb, source_size = load_image(
        input_path, args.max_dimension, background_rgb
    )
    rgb, variation = compose_variation(
        rgb,
        seed=args.variation_seed,
        crop_scale=args.crop_scale,
        crop_x=args.crop_x,
        crop_y=args.crop_y,
        rotation=args.rotation,
        flow_strength=args.flow_strength,
        flow_frequency=args.flow_frequency,
    )
    height, width = rgb.shape[:2]
    background, layers, trace_stats = build_layers(
        rgb,
        mode=args.mode,
        colors=args.colors,
        smoothing=args.smoothing,
        detail=args.detail,
        min_area=args.min_area,
        background=background_rgb,
        palette_method=args.palette_method,
    )
    colorset_name = args.colorset or "source"
    palette_contract_sha256 = ""
    colorset_mapping: list[dict[str, str]] = []
    if args.colorset:
        background, layers, colorset_record = apply_colorset(
            background,
            layers,
            mode=args.mode,
            colorset_name=args.colorset,
        )
        palette_contract_sha256 = colorset_record["contract_sha256"]
        colorset_mapping = colorset_record["mapping"]
    title = args.title or pattern_id.replace("-", " ").title()
    description = args.description or (
        f"Editable {args.mode} SVG simplification derived from a rights-verified "
        f"raster artwork using {colorset_name} colors."
    )
    svg = render_svg(
        pattern_id=pattern_id,
        title=title,
        description=description,
        width=width,
        height=height,
        tile=args.tile,
        mode=args.mode,
        colors=args.colors,
        smoothing=args.smoothing,
        detail=args.detail,
        min_area=args.min_area,
        max_dimension=args.max_dimension,
        palette_method=args.palette_method,
        colorset=colorset_name,
        palette_contract_sha256=palette_contract_sha256,
        background=background,
        layers=layers,
        rights=rights,
        outline=args.outline,
        variation=variation,
    )
    atomic_write_text(output_path, svg)
    output_digest = sha256_path(output_path)
    render_width = width if args.tile != "mirror" else width * 2
    render_height = height if args.tile != "mirror" else height * 2
    report = {
        "schema_version": 1,
        "ok": True,
        "input": str(args.input),
        "input_sha256": rights["input_sha256"],
        "output": str(args.output),
        "output_sha256": output_digest,
        "pattern_id": pattern_id,
        "mode": args.mode,
        "tile": args.tile,
        "palette_method": args.palette_method,
        "colorset": colorset_name,
        "palette_contract_sha256": palette_contract_sha256,
        "colorset_mapping": colorset_mapping,
        "variation": variation,
        "composition_sha256": variation["composition_sha256"],
        "parameters": {
            "colors": args.colors,
            "smoothing": args.smoothing,
            "detail": args.detail,
            "min_area": args.min_area,
            "max_dimension": args.max_dimension,
            "palette_method": args.palette_method,
            "outline": args.outline,
            "variation": variation,
        },
        "source_width": source_size[0],
        "source_height": source_size[1],
        "vector_width": width,
        "vector_height": height,
        "render_width": render_width,
        "render_height": render_height,
        "palette": [background] + [layer["fill"] for layer in layers],
        "path_count": len(layers),
        "contour_count": trace_stats["contour_count"],
        "point_count": trace_stats["point_count"],
        "output_bytes": output_path.stat().st_size,
        "rights": rights,
    }
    if args.report:
        atomic_write_json(args.report.resolve(), report)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Simplify a rights-verified raster artwork into editable SVG paths."
        )
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_DEFAULTS),
        default="organic",
    )
    parser.add_argument("--colors", type=int)
    parser.add_argument("--smoothing", type=float)
    parser.add_argument("--detail", type=float)
    parser.add_argument(
        "--palette-method",
        choices=("median-cut", "max-coverage"),
    )
    parser.add_argument(
        "--colorset",
        choices=COLORSET_NAMES,
        help="Map every visible SVG color to the selected bundled colorset.",
    )
    parser.add_argument("--min-area", type=float, default=18.0)
    parser.add_argument("--max-dimension", type=int, default=900)
    parser.add_argument(
        "--tile", choices=("none", "repeat", "mirror"), default="none"
    )
    parser.add_argument("--pattern-id")
    parser.add_argument("--title")
    parser.add_argument("--description")
    parser.add_argument("--background", default="#ffffff")
    parser.add_argument("--outline", type=float, default=0.0)
    parser.add_argument(
        "--variation-seed",
        type=int,
        default=0,
        help="Deterministic seed for organic coordinate displacement.",
    )
    parser.add_argument("--crop-scale", type=float, default=1.0)
    parser.add_argument("--crop-x", type=float, default=0.5)
    parser.add_argument("--crop-y", type=float, default=0.5)
    parser.add_argument("--rotation", type=float, default=0.0)
    parser.add_argument("--flow-strength", type=float, default=0.0)
    parser.add_argument("--flow-frequency", type=float, default=1.0)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--source-manifest", type=Path)
    parser.add_argument("--source-id")
    parser.add_argument(
        "--rights-basis",
        choices=("user-owned", "public-domain", "cc0", "cc-by", "cc-by-sa"),
    )
    parser.add_argument("--source-url")
    return parser


def apply_mode_defaults(args: argparse.Namespace) -> argparse.Namespace:
    defaults = MODE_DEFAULTS[args.mode]
    if args.colors is None:
        args.colors = defaults["colors"]
    if args.smoothing is None:
        args.smoothing = defaults["smoothing"]
    if args.detail is None:
        args.detail = defaults["detail"]
    if args.palette_method is None:
        args.palette_method = defaults["palette_method"]
    return args


def main(argv: list[str] | None = None) -> int:
    args = apply_mode_defaults(build_parser().parse_args(argv))
    report = vectorize(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VectorizeError as exc:
        print(f"[vectorize-art-patterns] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)

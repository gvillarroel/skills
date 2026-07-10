#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Validate awsome-videos asset, composition, and visual-review contracts."""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import re
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageStat


sys.dont_write_bytecode = True

ASSET_KINDS = {
    "code-capture",
    "diagram",
    "illustration",
    "logo",
    "raster",
    "screenshot",
    "svg",
    "texture",
    "three-d",
    "ui-capture",
    "video",
}
READY_STATUSES = {"approved", "ready", "verified"}
RIGHTS_STATUSES = {
    "fair-use",
    "licensed",
    "official-source",
    "owned",
    "project-generated",
    "public-domain",
    "user-provided",
}
SPECIALIST_ASSET_SKILLS = {
    "browser:control-in-app-browser",
    "d3-animated-svg",
    "echarts-animated-svg",
    "imagegen",
    "mermaid-animated-svg",
    "plantuml-colorset-renderer",
    "playwright",
    "repo-native",
    "threejs-animated-3d",
}
RENDERER_SKILLS = {
    "html-d3-anime-video-workflow",
    "manim-svg-video",
    "slidev-video",
    "threejs-animated-3d",
}
REVIEW_CHECKS = {
    "clipping",
    "contrast",
    "focalClarity",
    "overlap",
    "safeAreas",
    "sourceProof",
    "typography",
}
SCENE_EVIDENCE_PHASES = {"first", "hold", "emphasis", "final"}
TRANSITION_EVIDENCE_PHASES = {"before", "midpoint", "after"}
COMPOSITION_MOTION_PHASES = {"entrance", "hold", "emphasis", "exit"}
PLACEHOLDER_RE = re.compile(
    r"\b(?:tbd|todo|placeholder|replace[- ]?me|lorem ipsum|pending visual|generic asset|source-bound visual)\b",
    re.IGNORECASE,
)
BEAT_ID_RE = re.compile(r"^b\d{2,}$")
RASTER_SUFFIXES = {".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
SUPPORTED_ASSET_SUFFIXES = RASTER_SUFFIXES | {".svg", ".mp4", ".webm", ".mov", ".m4v", ".glb", ".gltf"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate asset provenance, per-scene composition, seam coverage, and reviewed frame evidence."
    )
    parser.add_argument("--asset-manifest", required=True, type=Path)
    parser.add_argument("--composition-plan", required=True, type=Path)
    parser.add_argument("--visual-review", type=Path)
    parser.add_argument("--video", type=Path)
    parser.add_argument("--brief", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--min-assets", type=int, default=1)
    parser.add_argument("--min-scenes", type=int, default=1)
    parser.add_argument("--require-ready-assets", action="store_true")
    parser.add_argument("--require-specialist-routing", action="store_true")
    parser.add_argument("--require-source-routing", action="store_true")
    parser.add_argument("--require-reviewed-scenes", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def read_json(path: Path, label: str, failures: list[str]) -> dict[str, Any]:
    if not path.is_file():
        failures.append(f"{label} missing: {path}")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        failures.append(f"{label} is not valid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        failures.append(f"{label} root is not an object")
        return {}
    return data


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty(value: Any, *, minimum: int = 3) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum and not PLACEHOLDER_RE.search(value)


def url_like(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def project_path(project_root: Path, raw: Any, label: str, failures: list[str]) -> Path | None:
    if not nonempty(raw, minimum=1):
        failures.append(f"{label} path is missing or placeholder text")
        return None
    candidate = Path(str(raw))
    if candidate.is_absolute() or candidate.drive:
        failures.append(f"{label} path must be project-root-relative: {raw}")
        return None
    root = project_root.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        failures.append(f"{label} path escapes the project root: {raw}")
        return None
    return resolved


def inspect_raster(path: Path, *, min_width: int = 1, min_height: int = 1) -> dict[str, Any]:
    failures: list[str] = []
    try:
        with Image.open(path) as source:
            image = source.convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "failures": [f"image could not be opened: {exc}"]}
    width, height = image.size
    if width < min_width or height < min_height:
        failures.append(f"image dimensions {width}x{height} are below required {min_width}x{min_height}")
    sample_width = min(320, width)
    sample_height = max(1, round(height * sample_width / max(width, 1)))
    sample = image.resize((sample_width, sample_height))
    stddev = float(ImageStat.Stat(sample.convert("L")).stddev[0])
    colors = sample.getcolors(maxcolors=sample_width * sample_height + 1)
    color_count = len(colors) if colors is not None else sample_width * sample_height
    if stddev < 3.0:
        failures.append(f"image luminance variation is too low: {stddev:.2f} < 3.00")
    if color_count < 16:
        failures.append(f"image color diversity is too low: {color_count} < 16")
    return {
        "ok": not failures,
        "failures": failures,
        "width": width,
        "height": height,
        "luminanceStddev": stddev,
        "colorCount": color_count,
    }


def compare_evidence_to_video(
    video_path: Path,
    timestamp: float,
    evidence_path: Path,
    *,
    max_mean_difference: float = 0.04,
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(video_path),
                "-ss",
                f"{timestamp:.3f}",
                "-frames:v",
                "1",
                "-f",
                "image2pipe",
                "-vcodec",
                "png",
                "pipe:1",
            ],
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "failures": [f"ffmpeg frame extraction failed: {exc}"]}
    if completed.returncode != 0 or not completed.stdout:
        detail = completed.stderr.decode("utf-8", errors="ignore").strip()
        return {
            "ok": False,
            "failures": [f"ffmpeg could not extract candidate-video frame at {timestamp:.3f}s: {detail}"],
        }
    try:
        with Image.open(BytesIO(completed.stdout)) as extracted_source:
            extracted = extracted_source.convert("RGB").resize((160, 90))
        with Image.open(evidence_path) as evidence_source:
            evidence = evidence_source.convert("RGB").resize((160, 90))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "failures": [f"frame comparison image decode failed: {exc}"]}
    difference = ImageChops.difference(extracted, evidence)
    mean_difference = sum(ImageStat.Stat(difference).mean) / (3 * 255)
    failures: list[str] = []
    if mean_difference > max_mean_difference:
        failures.append(
            f"evidence does not match candidate video at {timestamp:.3f}s: "
            f"mean difference {mean_difference:.4f} > {max_mean_difference:.4f}"
        )
    return {
        "ok": not failures,
        "failures": failures,
        "timestamp": timestamp,
        "meanDifference": mean_difference,
        "maxMeanDifference": max_mean_difference,
    }


def inspect_svg(path: Path) -> dict[str, Any]:
    failures: list[str] = []
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ET.ParseError) as exc:
        return {"ok": False, "failures": [f"SVG could not be parsed: {exc}"]}
    tag = root.tag.rsplit("}", 1)[-1]
    if tag != "svg":
        failures.append("root element is not svg")
    view_box = root.attrib.get("viewBox")
    width = root.attrib.get("width")
    height = root.attrib.get("height")
    if not view_box and not (width and height):
        failures.append("SVG lacks viewBox or explicit width/height")
    geometry_count = sum(
        1
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] in {"circle", "ellipse", "image", "line", "path", "polygon", "polyline", "rect", "text", "use"}
    )
    if geometry_count < 2:
        failures.append("SVG has fewer than two drawable elements")
    return {
        "ok": not failures,
        "failures": failures,
        "viewBox": view_box,
        "width": width,
        "height": height,
        "geometryCount": geometry_count,
    }


def inspect_video_asset(path: Path, technical: dict[str, Any]) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=codec_name,width,height,duration:format=duration",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "failures": [f"ffprobe video inspection failed: {exc}"]}
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "unknown ffprobe error"
        return {"ok": False, "failures": [f"video could not be decoded by ffprobe: {detail}"]}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        return {"ok": False, "failures": [f"ffprobe returned invalid JSON: {exc}"]}
    streams = payload.get("streams") if isinstance(payload, dict) else None
    if not isinstance(streams, list) or not streams or not isinstance(streams[0], dict):
        return {"ok": False, "failures": ["video has no decodable video stream"]}
    stream = streams[0]
    failures: list[str] = []
    codec = str(stream.get("codec_name", "")).strip()
    width = stream.get("width")
    height = stream.get("height")
    if not codec:
        failures.append("video stream codec is missing")
    if not isinstance(width, int) or width <= 0 or not isinstance(height, int) or height <= 0:
        failures.append("video stream dimensions are missing or invalid")
    else:
        target_width = technical.get("targetWidth")
        target_height = technical.get("targetHeight")
        if isinstance(target_width, int) and width < target_width:
            failures.append(f"video width {width} is below targetWidth {target_width}")
        if isinstance(target_height, int) and height < target_height:
            failures.append(f"video height {height} is below targetHeight {target_height}")
    raw_duration = stream.get("duration")
    if raw_duration in (None, "N/A") and isinstance(payload.get("format"), dict):
        raw_duration = payload["format"].get("duration")
    try:
        duration = float(raw_duration)
    except (TypeError, ValueError):
        duration = 0.0
    if duration <= 0:
        failures.append("video duration is missing or non-positive")
    return {
        "ok": not failures,
        "failures": failures,
        "codec": codec,
        "width": width,
        "height": height,
        "durationSeconds": duration,
    }


def inspect_gltf_document(document: Any) -> dict[str, Any]:
    failures: list[str] = []
    if not isinstance(document, dict):
        return {"ok": False, "failures": ["glTF root is not an object"]}
    asset = document.get("asset")
    version = str(asset.get("version", "")).strip() if isinstance(asset, dict) else ""
    if not version.startswith("2."):
        failures.append("glTF asset.version must be 2.x")
    scenes = document.get("scenes")
    nodes = document.get("nodes")
    meshes = document.get("meshes")
    if not isinstance(scenes, list) or not scenes:
        failures.append("glTF needs at least one scene")
    if not isinstance(nodes, list) or not nodes:
        failures.append("glTF needs at least one node")
    if not isinstance(meshes, list) or not meshes:
        failures.append("glTF needs at least one mesh")
    default_scene = document.get("scene", 0)
    if isinstance(scenes, list) and scenes and (
        not isinstance(default_scene, int) or default_scene < 0 or default_scene >= len(scenes)
    ):
        failures.append("glTF default scene index is invalid")
    return {
        "ok": not failures,
        "failures": failures,
        "version": version,
        "sceneCount": len(scenes) if isinstance(scenes, list) else 0,
        "nodeCount": len(nodes) if isinstance(nodes, list) else 0,
        "meshCount": len(meshes) if isinstance(meshes, list) else 0,
    }


def inspect_gltf(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"ok": False, "failures": [f"glTF JSON could not be parsed: {exc}"]}
    return inspect_gltf_document(document)


def inspect_glb(path: Path) -> dict[str, Any]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        return {"ok": False, "failures": [f"GLB could not be read: {exc}"]}
    if len(payload) < 20:
        return {"ok": False, "failures": ["GLB is too small for a header and JSON chunk"]}
    magic, version, declared_length = struct.unpack_from("<III", payload, 0)
    failures: list[str] = []
    if magic != 0x46546C67:
        failures.append("GLB magic header is invalid")
    if version != 2:
        failures.append("GLB version must be 2")
    if declared_length != len(payload):
        failures.append(f"GLB declared length {declared_length} does not match file size {len(payload)}")
    chunk_length, chunk_type = struct.unpack_from("<II", payload, 12)
    if chunk_type != 0x4E4F534A:
        failures.append("GLB first chunk must be JSON")
    chunk_end = 20 + chunk_length
    if chunk_length <= 0 or chunk_end > len(payload):
        failures.append("GLB JSON chunk length is invalid")
        document_result = {"ok": False, "failures": []}
    else:
        try:
            document = json.loads(payload[20:chunk_end].decode("utf-8").rstrip(" \t\r\n\x00"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"GLB JSON chunk could not be parsed: {exc}")
            document_result = {"ok": False, "failures": []}
        else:
            document_result = inspect_gltf_document(document)
            failures.extend(document_result.get("failures", []))
    return {
        "ok": not failures,
        "failures": failures,
        "version": version,
        "declaredLength": declared_length,
        "jsonChunkLength": chunk_length,
        "document": document_result,
    }


def inspect_asset(path: Path, technical: dict[str, Any]) -> dict[str, Any]:
    if not path.is_file():
        return {"ok": False, "failures": [f"asset file missing: {path}"]}
    if path.stat().st_size < 256:
        return {"ok": False, "failures": [f"asset file is implausibly small: {path.stat().st_size} bytes"]}
    suffix = path.suffix.lower()
    if suffix in RASTER_SUFFIXES:
        return inspect_raster(
            path,
            min_width=int(technical.get("targetWidth", 1) or 1),
            min_height=int(technical.get("targetHeight", 1) or 1),
        )
    if suffix == ".svg":
        return inspect_svg(path)
    if suffix in {".mp4", ".webm", ".mov", ".m4v"}:
        return inspect_video_asset(path, technical)
    if suffix == ".gltf":
        return inspect_gltf(path)
    if suffix == ".glb":
        return inspect_glb(path)
    return {"ok": False, "failures": [f"unsupported asset format: {suffix or '<none>'}"]}


def parse_time_range(value: Any) -> tuple[float, float] | None:
    if not isinstance(value, str) or "-" not in value:
        return None

    def parse_token(token: str) -> float:
        clean = token.strip().lower().removesuffix("s")
        if ":" in clean:
            minutes, seconds = clean.split(":", 1)
            return float(minutes) * 60 + float(seconds)
        return float(clean)

    try:
        start_text, end_text = value.split("-", 1)
        start = parse_token(start_text)
        end = parse_token(end_text)
    except (TypeError, ValueError):
        return None
    if start < 0 or end <= start:
        return None
    return start, end


def brief_beat_contract(path: Path | None, failures: list[str]) -> list[dict[str, str]]:
    if path is None:
        return []
    if not path.is_file():
        failures.append(f"brief missing: {path}")
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        headers = [cell.strip().lower() for cell in line.strip().strip("|").split("|")]
        required_headers = {"time", "beat id", "scene id"}
        if not required_headers.issubset(set(headers)):
            continue
        if index + 1 >= len(lines) or not re.fullmatch(
            r"\s*\|(?:\s*:?-+:?\s*\|)+\s*", lines[index + 1]
        ):
            continue
        indexes = {name: headers.index(name) for name in required_headers}
        rows: list[dict[str, str]] = []
        for raw_row in lines[index + 2 :]:
            if not raw_row.strip().startswith("|"):
                break
            cells = [cell.strip() for cell in raw_row.strip().strip("|").split("|")]
            if len(cells) <= max(indexes.values()):
                break
            row = {name: cells[column] for name, column in indexes.items()}
            if not BEAT_ID_RE.fullmatch(row["beat id"]):
                failures.append(f"brief has invalid Beat ID: {row['beat id']}")
            if not re.fullmatch(r"s\d{2,}", row["scene id"]):
                failures.append(f"brief has invalid Scene ID: {row['scene id']}")
            if parse_time_range(row["time"]) is None:
                failures.append(f"brief has invalid time range for {row['beat id']}")
            rows.append(row)
        if rows:
            if len({row["beat id"] for row in rows}) != len(rows):
                failures.append("brief Beat IDs are not unique")
            if len({row["scene id"] for row in rows}) != len(rows):
                failures.append("brief Scene IDs are not unique")
            return rows
    failures.append("brief timed beat table must include explicit Time, Beat ID, and Scene ID columns")
    return []


def validate_completed_source_outputs(
    output_paths: list[Path],
    scene_count: int,
    failures: list[str],
    route_index: int,
) -> None:
    json_documents: list[tuple[Path, dict[str, Any]]] = []
    for output_path in output_paths:
        if not output_path.is_file() or output_path.suffix.lower() != ".json":
            continue
        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            json_documents.append((output_path, payload))

    source_candidates = [
        (path, payload)
        for path, payload in json_documents
        if payload.get("schemaVersion") == 1 and isinstance(payload.get("facts"), list)
    ]
    shot_candidates = [
        (path, payload)
        for path, payload in json_documents
        if payload.get("version") == 1 and isinstance(payload.get("shots"), list)
    ]
    if len(source_candidates) != 1 or len(shot_candidates) != 1:
        failures.append(
            f"skillRouting[{route_index}] completed source route must output exactly one schema-v1 "
            "source package and one version-1 shot contract"
        )
        return

    source_path, source = source_candidates[0]
    shot_path, shot_contract = shot_candidates[0]
    source_status = str(source.get("status", "")).strip().lower()
    if source_status not in {"approved", "complete", "frozen", "ready", "verified"}:
        failures.append(
            f"skillRouting[{route_index}] source package is not frozen/verified: {source_path.name}"
        )
    facts = source.get("facts", [])
    if len(facts) != scene_count:
        failures.append(
            f"skillRouting[{route_index}] source package fact count {len(facts)} does not match scene count {scene_count}"
        )
    fact_ids: set[str] = set()
    fact_beats: dict[str, str] = {}
    fact_times: dict[str, str] = {}
    for fact_index, fact in enumerate(facts):
        if not isinstance(fact, dict):
            failures.append(f"skillRouting[{route_index}] source fact {fact_index} is not an object")
            continue
        fact_id = str(fact.get("id", "")).strip()
        beat_id = str(fact.get("beatId", "")).strip()
        if not re.fullmatch(r"f\d{2,}", fact_id) or fact_id in fact_ids:
            failures.append(f"skillRouting[{route_index}] source fact {fact_index} has invalid/duplicate id")
        fact_ids.add(fact_id)
        if not BEAT_ID_RE.fullmatch(beat_id):
            failures.append(f"skillRouting[{route_index}] source fact {fact_id or fact_index} has invalid beatId")
        if parse_time_range(fact.get("time")) is None:
            failures.append(f"skillRouting[{route_index}] source fact {fact_id or fact_index} has invalid time")
        if not nonempty(fact.get("claim"), minimum=20):
            failures.append(f"skillRouting[{route_index}] source fact {fact_id or fact_index} has a thin claim")
        source_url = str(fact.get("sourceUrl", "")).strip()
        if not url_like(source_url):
            failures.append(f"skillRouting[{route_index}] source fact {fact_id or fact_index} lacks a concrete URL")
        else:
            host = (urlparse(source_url).hostname or "").lower()
            if host.endswith(".invalid") or host in {"example.com", "www.example.com"}:
                failures.append(
                    f"skillRouting[{route_index}] source fact {fact_id or fact_index} uses a placeholder domain"
                )
        rights = str(fact.get("rightsStatus", "")).strip().lower()
        if rights not in RIGHTS_STATUSES:
            failures.append(f"skillRouting[{route_index}] source fact {fact_id or fact_index} rights are unverified")
        verification = str(fact.get("verificationStatus", "")).strip().lower()
        if verification not in {"approved", "complete", "frozen", "verified"}:
            failures.append(
                f"skillRouting[{route_index}] source fact {fact_id or fact_index} verification is incomplete"
            )
        fact_beats[fact_id] = beat_id
        fact_times[fact_id] = str(fact.get("time", ""))

    shots = shot_contract.get("shots", [])
    if len(shots) != scene_count:
        failures.append(
            f"skillRouting[{route_index}] shot count {len(shots)} does not match scene count {scene_count}"
        )
    shot_ids: set[str] = set()
    referenced_facts: set[str] = set()
    for shot_index, shot in enumerate(shots):
        if not isinstance(shot, dict):
            failures.append(f"skillRouting[{route_index}] shot {shot_index} is not an object")
            continue
        shot_id = str(shot.get("id", "")).strip()
        beat_id = str(shot.get("beatId", "")).strip()
        if not re.fullmatch(r"s\d{2,}", shot_id) or shot_id in shot_ids:
            failures.append(f"skillRouting[{route_index}] shot {shot_index} has invalid/duplicate id")
        shot_ids.add(shot_id)
        if not BEAT_ID_RE.fullmatch(beat_id):
            failures.append(f"skillRouting[{route_index}] shot {shot_id or shot_index} has invalid beatId")
        if parse_time_range(shot.get("time")) is None:
            failures.append(f"skillRouting[{route_index}] shot {shot_id or shot_index} has invalid time")
        if not nonempty(shot.get("job"), minimum=12) or not nonempty(shot.get("viewerTask"), minimum=12):
            failures.append(f"skillRouting[{route_index}] shot {shot_id or shot_index} has thin intent")
        asset_ids = shot.get("assetIds")
        if not isinstance(asset_ids, list) or not any(nonempty(item, minimum=3) for item in asset_ids):
            failures.append(f"skillRouting[{route_index}] shot {shot_id or shot_index} lacks asset IDs")
        source_fact_ids = shot.get("sourceFactIds")
        if not isinstance(source_fact_ids, list) or not source_fact_ids:
            failures.append(f"skillRouting[{route_index}] shot {shot_id or shot_index} lacks sourceFactIds")
            source_fact_ids = []
        shot_status = str(shot.get("status", "")).strip().lower()
        if shot_status not in {"approved", "complete", "frozen", "ready", "verified"}:
            failures.append(f"skillRouting[{route_index}] shot {shot_id or shot_index} remains incomplete")
        for raw_fact_id in source_fact_ids:
            fact_id = str(raw_fact_id)
            referenced_facts.add(fact_id)
            if fact_id not in fact_ids:
                failures.append(
                    f"skillRouting[{route_index}] shot {shot_id or shot_index} references unknown fact {fact_id}"
                )
                continue
            if fact_beats.get(fact_id) != beat_id:
                failures.append(
                    f"skillRouting[{route_index}] shot {shot_id or shot_index} beat disagrees with fact {fact_id}"
                )
            if fact_times.get(fact_id, "").replace(" ", "") != str(shot.get("time", "")).replace(" ", ""):
                failures.append(
                    f"skillRouting[{route_index}] shot {shot_id or shot_index} timing disagrees with fact {fact_id}"
                )
    if referenced_facts != fact_ids:
        failures.append(f"skillRouting[{route_index}] shot contract does not cover every frozen fact")
    if source.get("videoId") != shot_contract.get("videoId"):
        failures.append(f"skillRouting[{route_index}] source and shot videoId values disagree")


def validate_skill_routing(
    routes: Any,
    project_root: Path,
    failures: list[str],
    *,
    require_specialist: bool,
    require_source: bool,
    require_complete: bool,
    scene_count: int,
) -> dict[str, Any]:
    if not isinstance(routes, list):
        failures.append("asset manifest skillRouting is missing or not a list")
        routes = []
    normalized: list[dict[str, Any]] = []
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            failures.append(f"skillRouting[{index}] is not an object")
            continue
        stage = str(route.get("stage", "")).strip()
        skill = str(route.get("skill", "")).strip()
        if not nonempty(stage) or not nonempty(skill):
            failures.append(f"skillRouting[{index}] needs non-placeholder stage and skill")
        if not nonempty(route.get("reason"), minimum=12):
            failures.append(f"skillRouting[{index}] reason is missing or too thin")
        if not nonempty(route.get("output"), minimum=3):
            failures.append(f"skillRouting[{index}] output is missing")
        status = str(route.get("status", "")).strip().lower()
        if status not in {"complete", "planned", "skipped"}:
            failures.append(f"skillRouting[{index}] has invalid status: {status or '<missing>'}")
        if status == "skipped" and not nonempty(route.get("fallbackReason"), minimum=12):
            failures.append(f"skillRouting[{index}] skipped without a concrete fallbackReason")
        if require_complete and status == "complete":
            raw_output_paths = route.get("outputPaths")
            if not isinstance(raw_output_paths, list) or not raw_output_paths:
                failures.append(f"skillRouting[{index}] complete route needs non-empty outputPaths")
                raw_output_paths = []
            expected_output_paths = {
                Path(str(item)).as_posix()
                for item in raw_output_paths
                if nonempty(item, minimum=3)
            }
            if len(expected_output_paths) != len(raw_output_paths):
                failures.append(f"skillRouting[{index}] outputPaths contains invalid or duplicate paths")
            resolved_output_paths: list[Path] = []
            for output_index, raw_output_path in enumerate(raw_output_paths):
                resolved_output = project_path(
                    project_root,
                    raw_output_path,
                    f"skillRouting[{index}] outputPaths[{output_index}]",
                    failures,
                )
                if resolved_output is not None:
                    resolved_output_paths.append(resolved_output)
            proof_path = project_path(
                project_root,
                route.get("proof"),
                f"skillRouting[{index}] proof",
                failures,
            )
            if proof_path is not None:
                if not proof_path.is_file():
                    failures.append(f"skillRouting[{index}] proof missing: {proof_path}")
                elif proof_path.suffix.lower() != ".json":
                    failures.append(f"skillRouting[{index}] proof must be a JSON report")
                else:
                    try:
                        proof_data = json.loads(proof_path.read_text(encoding="utf-8"))
                    except json.JSONDecodeError as exc:
                        failures.append(f"skillRouting[{index}] proof is invalid JSON: {exc}")
                    else:
                        if not isinstance(proof_data, dict) or proof_data.get("ok") is False or proof_data.get("passed") is False or (
                            proof_data.get("ok") is not True and proof_data.get("passed") is not True
                        ):
                            failures.append(f"skillRouting[{index}] proof does not carry a passing status")
                        elif proof_data.get("schemaVersion") != 1:
                            failures.append(f"skillRouting[{index}] proof schemaVersion must be 1")
                        else:
                            for field, expected in [
                                ("stage", stage),
                                ("skill", skill),
                                ("output", route.get("output")),
                            ]:
                                if proof_data.get(field) != expected:
                                    failures.append(
                                        f"skillRouting[{index}] proof {field} does not match the route"
                                    )
                            artifacts = proof_data.get("artifacts")
                            if not isinstance(artifacts, list) or not artifacts:
                                failures.append(f"skillRouting[{index}] proof artifacts is missing or empty")
                                artifacts = []
                            observed_paths: set[str] = set()
                            for artifact_index, artifact in enumerate(artifacts):
                                if not isinstance(artifact, dict):
                                    failures.append(
                                        f"skillRouting[{index}] proof artifacts[{artifact_index}] is not an object"
                                    )
                                    continue
                                raw_path = artifact.get("path")
                                normalized_path = Path(str(raw_path)).as_posix()
                                observed_paths.add(normalized_path)
                                artifact_path = project_path(
                                    project_root,
                                    raw_path,
                                    f"skillRouting[{index}] proof artifact {artifact_index}",
                                    failures,
                                )
                                declared_digest = artifact.get("sha256")
                                if not isinstance(declared_digest, str) or not re.fullmatch(
                                    r"[0-9a-f]{64}", declared_digest
                                ):
                                    failures.append(
                                        f"skillRouting[{index}] proof artifact {artifact_index} sha256 is invalid"
                                    )
                                if artifact_path is not None:
                                    if not artifact_path.is_file():
                                        failures.append(
                                            f"skillRouting[{index}] proof artifact missing: {artifact_path}"
                                        )
                                    elif sha256_file(artifact_path) != declared_digest:
                                        failures.append(
                                            f"skillRouting[{index}] proof artifact {artifact_index} sha256 is stale"
                                        )
                            if observed_paths != expected_output_paths:
                                failures.append(
                                    f"skillRouting[{index}] proof artifacts do not exactly match outputPaths"
                                )
            if skill == "source-to-video-director":
                validate_completed_source_outputs(resolved_output_paths, scene_count, failures, index)
        normalized.append(route)

    if require_specialist:
        composition = [item for item in normalized if item.get("skill") == "scene-composition-director"]
        renderers = [item for item in normalized if item.get("skill") in RENDERER_SKILLS]
        transitions = [item for item in normalized if item.get("skill") == "scene-transition-director"]
        if not composition:
            failures.append("specialist routing requires scene-composition-director")
        if len(renderers) != 1:
            failures.append(f"specialist routing requires exactly one renderer owner, found {len(renderers)}")
        if scene_count > 1 and not transitions:
            failures.append("multi-scene work requires scene-transition-director routing")
        if require_complete:
            incomplete = [
                str(item.get("skill"))
                for item in [*composition, *renderers, *transitions]
                if item.get("status") != "complete"
            ]
            if incomplete:
                failures.append("finished specialist routes are not complete: " + ", ".join(incomplete))
    if require_source and not any(item.get("skill") == "source-to-video-director" for item in normalized):
        failures.append("source routing requires source-to-video-director")
    if require_source and require_complete:
        source_routes = [item for item in normalized if item.get("skill") == "source-to-video-director"]
        if source_routes and any(item.get("status") != "complete" for item in source_routes):
            failures.append("source-to-video-director route is not complete")
    if require_complete:
        planned_routes = [str(item.get("skill")) for item in normalized if item.get("status") == "planned"]
        if planned_routes:
            failures.append("finished skill routes remain planned: " + ", ".join(planned_routes))
    return {
        "count": len(normalized),
        "completeCount": sum(1 for item in normalized if item.get("status") == "complete"),
        "skippedCount": sum(1 for item in normalized if item.get("status") == "skipped"),
        "skills": sorted({str(item.get("skill")) for item in normalized if item.get("skill")}),
    }


def validate_asset_manifest(
    data: dict[str, Any],
    project_root: Path,
    failures: list[str],
    warnings: list[str],
    *,
    min_assets: int,
    require_ready: bool,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, set[str]], dict[str, set[str]]]:
    if data.get("schemaVersion") != 1:
        failures.append("asset manifest schemaVersion must be 1")
    canvas = data.get("canvas")
    if not isinstance(canvas, dict):
        failures.append("asset manifest canvas is missing or not an object")
        canvas = {}
    for field in ["width", "height"]:
        if not isinstance(canvas.get(field), int) or canvas.get(field, 0) <= 0:
            failures.append(f"asset manifest canvas.{field} must be a positive integer")
    if not nonempty(canvas.get("aspectRatio"), minimum=3):
        failures.append("asset manifest canvas.aspectRatio is missing")

    raw_assets = data.get("assets")
    if not isinstance(raw_assets, list):
        failures.append("asset manifest assets is missing or not a list")
        raw_assets = []
    if len(raw_assets) < min_assets:
        failures.append(f"asset manifest needs at least {min_assets} assets, found {len(raw_assets)}")

    assets: dict[str, dict[str, Any]] = {}
    scene_assets: dict[str, set[str]] = {}
    beat_assets: dict[str, set[str]] = {}
    inspections: dict[str, Any] = {}
    producer_skills: set[str] = set()
    for index, asset in enumerate(raw_assets):
        label = f"assets[{index}]"
        if not isinstance(asset, dict):
            failures.append(f"{label} is not an object")
            continue
        asset_id = str(asset.get("id", "")).strip()
        if not re.fullmatch(r"[a-z][a-z0-9-]*", asset_id):
            failures.append(f"{label}.id must be stable lowercase hyphen-case")
            asset_id = f"invalid-{index}"
        if asset_id in assets:
            failures.append(f"duplicate asset id: {asset_id}")
        assets[asset_id] = asset
        kind = str(asset.get("kind", "")).strip()
        if kind not in ASSET_KINDS:
            failures.append(f"asset {asset_id} has unsupported kind: {kind or '<missing>'}")
        if not nonempty(asset.get("claim"), minimum=12):
            failures.append(f"asset {asset_id} needs a concrete claim or mechanism purpose")
        output_path = project_path(project_root, asset.get("output"), f"asset {asset_id} output", failures)
        if output_path is not None and output_path.suffix.lower() not in SUPPORTED_ASSET_SUFFIXES:
            failures.append(
                f"asset {asset_id} output uses unsupported visual/media extension: {output_path.suffix or '<none>'}"
            )

        origin = asset.get("origin")
        if not isinstance(origin, dict):
            failures.append(f"asset {asset_id} origin is missing or not an object")
            origin = {}
        origin_type = str(origin.get("type", "")).strip()
        origin_uri = str(origin.get("uri", "")).strip()
        if origin_type not in {"captured", "external", "generated", "local", "user-provided"}:
            failures.append(f"asset {asset_id} has invalid origin.type: {origin_type or '<missing>'}")
        if not nonempty(origin_uri, minimum=4):
            failures.append(f"asset {asset_id} origin.uri is missing or placeholder text")
        if origin_type in {"captured", "external"} and not url_like(origin_uri):
            failures.append(f"asset {asset_id} external/captured origin.uri must be an http(s) URL")
        rights = str(origin.get("rightsStatus", "")).strip()
        if rights not in RIGHTS_STATUSES:
            failures.append(f"asset {asset_id} has invalid or missing origin.rightsStatus")
        if rights in {"fair-use", "licensed", "official-source"} and not nonempty(origin.get("attribution"), minimum=4):
            failures.append(f"asset {asset_id} needs attribution for rightsStatus={rights}")

        producer = asset.get("producer")
        if not isinstance(producer, dict):
            failures.append(f"asset {asset_id} producer is missing or not an object")
            producer = {}
        producer_skill = str(producer.get("skill", "")).strip()
        producer_skills.add(producer_skill)
        if producer_skill not in SPECIALIST_ASSET_SKILLS:
            failures.append(f"asset {asset_id} producer.skill is unsupported: {producer_skill or '<missing>'}")
        if not nonempty(producer.get("method"), minimum=12):
            failures.append(f"asset {asset_id} producer.method is missing or too thin")
        if producer_skill == "repo-native" and not nonempty(producer.get("fallbackReason"), minimum=12):
            failures.append(f"asset {asset_id} repo-native fallback lacks fallbackReason")

        technical = asset.get("technical")
        if not isinstance(technical, dict):
            failures.append(f"asset {asset_id} technical is missing or not an object")
            technical = {}
        for field in ["targetWidth", "targetHeight"]:
            if not isinstance(technical.get(field), int) or technical.get(field, 0) <= 0:
                failures.append(f"asset {asset_id} technical.{field} must be a positive integer")
        if not nonempty(technical.get("aspectRatio"), minimum=3):
            failures.append(f"asset {asset_id} technical.aspectRatio is missing")
        max_upscale = technical.get("maxUpscale")
        if not isinstance(max_upscale, (int, float)) or max_upscale <= 0 or max_upscale > 1.25:
            failures.append(f"asset {asset_id} technical.maxUpscale must be > 0 and <= 1.25")
        if not nonempty(technical.get("crop"), minimum=8):
            failures.append(f"asset {asset_id} technical.crop is missing or too thin")

        uses = asset.get("uses")
        if not isinstance(uses, list) or not uses:
            failures.append(f"asset {asset_id} needs at least one scene use")
            uses = []
        for use_index, use in enumerate(uses):
            if not isinstance(use, dict):
                failures.append(f"asset {asset_id} uses[{use_index}] is not an object")
                continue
            scene_id = str(use.get("sceneId", "")).strip()
            beat_id = str(use.get("beatId", "")).strip()
            if not re.fullmatch(r"s\d{2,}", scene_id):
                failures.append(f"asset {asset_id} use has invalid sceneId: {scene_id or '<missing>'}")
            if not BEAT_ID_RE.fullmatch(beat_id):
                failures.append(f"asset {asset_id} use has invalid beatId: {beat_id or '<missing>'}")
            if not nonempty(use.get("role"), minimum=4) or not nonempty(use.get("fit"), minimum=4):
                failures.append(f"asset {asset_id} use {scene_id or use_index} needs role and fit")
            scene_assets.setdefault(scene_id, set()).add(asset_id)
            beat_assets.setdefault(beat_id, set()).add(asset_id)

        quality_checks = asset.get("qualityChecks")
        if not isinstance(quality_checks, list) or len([item for item in quality_checks if nonempty(item, minimum=10)]) < 3:
            failures.append(f"asset {asset_id} needs at least three concrete qualityChecks")
        status = str(asset.get("status", "")).strip().lower()
        if status not in {"approved", "planned", "ready", "verified"}:
            failures.append(f"asset {asset_id} has invalid status: {status or '<missing>'}")
        if require_ready:
            if status not in READY_STATUSES:
                failures.append(f"asset {asset_id} is not ready: status={status or '<missing>'}")
            if origin_type in {"captured", "external"}:
                host = (urlparse(origin_uri).hostname or "").lower()
                if host.endswith(".invalid") or host in {"example.com", "www.example.com"}:
                    failures.append(f"asset {asset_id} still uses a placeholder source domain: {host}")
                attribution = str(origin.get("attribution", ""))
                if re.search(r"\b(?:replace with|placeholder|tbd|todo)\b", attribution, flags=re.IGNORECASE):
                    failures.append(f"asset {asset_id} still uses placeholder attribution")
            if output_path is not None:
                inspection = inspect_asset(output_path, technical)
                inspections[asset_id] = inspection
                for finding in inspection.get("failures", []):
                    failures.append(f"asset {asset_id}: {finding}")
                actual_hash = sha256_file(output_path)
                declared_hash = asset.get("sha256")
                inspections[asset_id]["sha256"] = actual_hash
                if not isinstance(declared_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", declared_hash):
                    failures.append(f"asset {asset_id} sha256 is missing or invalid")
                elif actual_hash != declared_hash:
                    failures.append(f"asset {asset_id} sha256 does not match its output file")
            producer_report = project_path(
                project_root,
                producer.get("report"),
                f"asset {asset_id} producer report",
                failures,
            )
            if producer_report is not None:
                if not producer_report.is_file():
                    failures.append(f"asset {asset_id} producer report missing: {producer_report}")
                elif producer_report.suffix.lower() != ".json":
                    failures.append(f"asset {asset_id} producer report must be a JSON report")
                else:
                    try:
                        report_data = json.loads(producer_report.read_text(encoding="utf-8"))
                    except json.JSONDecodeError as exc:
                        failures.append(f"asset {asset_id} producer report is invalid JSON: {exc}")
                    else:
                        if not isinstance(report_data, dict) or report_data.get("ok") is False or report_data.get("passed") is False or (
                            report_data.get("ok") is not True and report_data.get("passed") is not True
                        ):
                            failures.append(f"asset {asset_id} producer report does not carry a passing status")
                        elif report_data.get("schemaVersion") != 1:
                            failures.append(f"asset {asset_id} producer report schemaVersion must be 1")
                        else:
                            expected_report_fields = {
                                "assetId": asset_id,
                                "skill": producer_skill,
                                "output": asset.get("output"),
                                "sha256": asset.get("sha256"),
                            }
                            for report_field, expected_value in expected_report_fields.items():
                                if report_data.get(report_field) != expected_value:
                                    failures.append(
                                        f"asset {asset_id} producer report {report_field} does not match the manifest"
                                    )
                            report_checks = report_data.get("checks")
                            if not isinstance(report_checks, list) or len(report_checks) < 3:
                                failures.append(
                                    f"asset {asset_id} producer report needs at least three structured checks"
                                )
                            else:
                                for check_index, check in enumerate(report_checks):
                                    if not isinstance(check, dict) or check.get("passed") is not True or not all(
                                        nonempty(check.get(field), minimum=6)
                                        for field in ["name", "method", "finding"]
                                    ):
                                        failures.append(
                                            f"asset {asset_id} producer report check {check_index} is incomplete"
                                        )
        elif output_path is not None and not output_path.exists():
            warnings.append(f"planned asset output does not exist yet: {asset.get('output')}")

    return (
        {
            "assetCount": len(assets),
            "producerSkills": sorted(skill for skill in producer_skills if skill),
            "readyAssetCount": sum(
                1 for item in assets.values() if str(item.get("status", "")).lower() in READY_STATUSES
            ),
            "inspections": inspections,
        },
        assets,
        scene_assets,
        beat_assets,
    )


def validate_bounds(bounds: Any, scene_id: str, failures: list[str]) -> dict[str, Any]:
    if not isinstance(bounds, list) or not bounds:
        failures.append(f"scene {scene_id} objectBounds is missing or empty")
        return {"focalArea": None}
    focal_area: float | None = None
    object_ids: set[str] = set()
    for index, item in enumerate(bounds):
        if not isinstance(item, dict):
            failures.append(f"scene {scene_id} objectBounds[{index}] is not an object")
            continue
        object_id = str(item.get("id", "")).strip()
        if not re.fullmatch(r"[a-z][a-z0-9-]*", object_id):
            failures.append(
                f"scene {scene_id} objectBounds[{index}].id must be stable lowercase hyphen-case"
            )
        elif object_id in object_ids:
            failures.append(f"scene {scene_id} objectBounds has duplicate id: {object_id}")
        else:
            object_ids.add(object_id)
        values = [item.get(key) for key in ["x", "y", "width", "height"]]
        if not all(isinstance(value, (int, float)) for value in values):
            failures.append(f"scene {scene_id} objectBounds[{index}] needs numeric x/y/width/height")
            continue
        x, y, width, height = [float(value) for value in values]
        if x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1.0001 or y + height > 1.0001:
            failures.append(f"scene {scene_id} objectBounds[{index}] falls outside normalized frame bounds")
        if item.get("role") == "focal":
            focal_area = width * height
    if focal_area is None:
        failures.append(f"scene {scene_id} objectBounds has no role=focal object")
    elif focal_area < 0.05:
        failures.append(f"scene {scene_id} focal object is too small: {focal_area:.3f} < 0.050 frame area")
    return {"focalArea": focal_area}


def spatial_layout_signature(bounds: Any) -> str | None:
    if not isinstance(bounds, list) or not bounds:
        return None
    parts: list[str] = []
    for item in bounds:
        if not isinstance(item, dict):
            continue
        values = [item.get(key) for key in ["x", "y", "width", "height"]]
        if not all(isinstance(value, (int, float)) for value in values):
            continue
        x, y, width, height = [float(value) for value in values]
        role = str(item.get("role", "object")).strip().lower() or "object"
        # Tenths-of-frame bins ignore cosmetic coordinate jitter while preserving meaningful layout changes.
        quantized = [round(value * 10) for value in [x, y, width, height]]
        parts.append(f"{role}:{','.join(str(value) for value in quantized)}")
    return "|".join(sorted(parts)) if parts else None


def validate_composition_plan(
    data: dict[str, Any],
    failures: list[str],
    *,
    min_scenes: int,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, set[str]], dict[str, set[str]]]:
    if data.get("version") != 1:
        failures.append("composition plan version must be 1")
    if not nonempty(data.get("format"), minimum=3):
        failures.append("composition plan format is missing")
    direction = data.get("videoDirection")
    if not isinstance(direction, dict):
        failures.append("composition plan videoDirection is missing or not an object")
        direction = {}
    for field in [
        "alignmentMode",
        "edgeCornerPolicy",
        "paletteTypeSource",
        "rhythm",
        "safeZones",
    ]:
        if not nonempty(direction.get(field), minimum=8):
            failures.append(f"composition plan videoDirection.{field} is missing or too thin")
    negative = direction.get("negativeList")
    if not isinstance(negative, list) or len([item for item in negative if nonempty(item, minimum=6)]) < 3:
        failures.append("composition plan videoDirection.negativeList needs at least three concrete exclusions")

    raw_scenes = data.get("scenes")
    if not isinstance(raw_scenes, list):
        failures.append("composition plan scenes is missing or not a list")
        raw_scenes = []
    if len(raw_scenes) < min_scenes:
        failures.append(f"composition plan needs at least {min_scenes} scenes, found {len(raw_scenes)}")

    scenes: dict[str, dict[str, Any]] = {}
    scene_assets: dict[str, set[str]] = {}
    beat_scenes: dict[str, set[str]] = {}
    bounds_info: dict[str, Any] = {}
    compositions: set[str] = set()
    armatures: set[str] = set()
    spatial_layouts: set[str] = set()
    for index, scene in enumerate(raw_scenes):
        label = f"scenes[{index}]"
        if not isinstance(scene, dict):
            failures.append(f"{label} is not an object")
            continue
        scene_id = str(scene.get("id", "")).strip()
        if not re.fullmatch(r"s\d{2,}", scene_id):
            failures.append(f"{label}.id must use stable sNN form")
            scene_id = f"invalid-{index}"
        if scene_id in scenes:
            failures.append(f"duplicate composition scene id: {scene_id}")
        scenes[scene_id] = scene
        for field, minimum in {
            "sceneJob": 8,
            "viewerTask": 8,
            "compositionChoice": 4,
            "choiceRationale": 18,
            "focal": 6,
            "armature": 5,
            "alignmentGrid": 8,
            "edgePolicy": 5,
            "cornerPolicy": 5,
            "layout": 12,
            "hierarchy": 12,
        }.items():
            if not nonempty(scene.get(field), minimum=minimum):
                failures.append(f"scene {scene_id} {field} is missing or too thin")
        compositions.add(str(scene.get("compositionChoice", "")).strip())
        armatures.add(str(scene.get("armature", "")).strip())
        if parse_time_range(scene.get("duration")) is None:
            failures.append(f"scene {scene_id} duration must be a valid increasing time range")

        rejected = scene.get("rejectedAlternatives")
        if not isinstance(rejected, list) or len([item for item in rejected if nonempty(item, minimum=6)]) < 2:
            failures.append(f"scene {scene_id} rejectedAlternatives needs at least two concrete options")
        anchors = scene.get("armatureAnchors")
        if not isinstance(anchors, list) or len([item for item in anchors if nonempty(item, minimum=5)]) < 2:
            failures.append(f"scene {scene_id} armatureAnchors needs at least two concrete anchors")

        roles = scene.get("roles")
        if not isinstance(roles, dict) or len(roles) < 2:
            failures.append(f"scene {scene_id} roles needs at least two named roles")
        safe_zones = scene.get("safeZones")
        if not isinstance(safe_zones, dict) or not safe_zones:
            failures.append(f"scene {scene_id} safeZones is missing or not an object")
        text_region = scene.get("textRegion")
        if not isinstance(text_region, dict):
            failures.append(f"scene {scene_id} textRegion is missing or not an object")
            text_region = {}
        if not nonempty(text_region.get("placement"), minimum=8):
            failures.append(f"scene {scene_id} textRegion.placement is missing or too thin")
        if not isinstance(text_region.get("maxLineCharacters"), int) or not 16 <= text_region.get(
            "maxLineCharacters", 0
        ) <= 64:
            failures.append(f"scene {scene_id} textRegion.maxLineCharacters must be 16..64")
        for text_field in ["contrastTreatment", "clearance"]:
            if not nonempty(text_region.get(text_field), minimum=12):
                failures.append(f"scene {scene_id} textRegion.{text_field} is missing or too thin")
        depth = scene.get("depthLayers")
        if not isinstance(depth, list) or len([item for item in depth if nonempty(item, minimum=4)]) < 3:
            failures.append(f"scene {scene_id} needs at least three concrete depthLayers")
        phases = scene.get("motionPhases")
        if not isinstance(phases, list) or len(phases) != 4:
            failures.append(f"scene {scene_id} needs exactly entrance/hold/emphasis/exit motion phases")
        else:
            phase_names: set[str] = set()
            for phase_index, phase in enumerate(phases):
                if not isinstance(phase, dict) or not all(
                    nonempty(phase.get(field), minimum=4) for field in ["name", "cue", "visualChange", "motionVerb"]
                ):
                    failures.append(f"scene {scene_id} motionPhases[{phase_index}] is incomplete")
                elif isinstance(phase, dict):
                    phase_names.add(str(phase.get("name", "")).strip().lower())
            if phase_names != COMPOSITION_MOTION_PHASES:
                failures.append(f"scene {scene_id} motion phase names must be entrance/hold/emphasis/exit")
        if not nonempty(scene.get("reducedMotion"), minimum=20):
            failures.append(f"scene {scene_id} reducedMotion is missing or too thin")
        outgoing_seam = scene.get("outgoingSeam")
        if not isinstance(outgoing_seam, dict):
            failures.append(f"scene {scene_id} outgoingSeam is missing or not an object")
            outgoing_seam = {}
        next_scene_id = None
        if index + 1 < len(raw_scenes) and isinstance(raw_scenes[index + 1], dict):
            next_scene_id = str(raw_scenes[index + 1].get("id", "")).strip()
        expected_seam_id = f"{scene_id}__{next_scene_id}" if next_scene_id else "end"
        if outgoing_seam.get("seamId") != expected_seam_id:
            failures.append(f"scene {scene_id} outgoingSeam.seamId must be {expected_seam_id}")
        if outgoing_seam.get("fromScene") != scene_id or outgoing_seam.get("toScene") != next_scene_id:
            failures.append(f"scene {scene_id} outgoingSeam from/to scene binding is invalid")
        expected_seam_type = "transition" if next_scene_id else "end"
        if outgoing_seam.get("type") != expected_seam_type:
            failures.append(f"scene {scene_id} outgoingSeam.type must be {expected_seam_type}")
        for seam_field in ["persistentElement", "attentionHandoff", "beforeState", "afterState"]:
            if not nonempty(outgoing_seam.get(seam_field), minimum=12):
                failures.append(f"scene {scene_id} outgoingSeam.{seam_field} is missing or too thin")
        checks = scene.get("validationChecks")
        if not isinstance(checks, list) or len(checks) < 2:
            failures.append(f"scene {scene_id} needs at least two structured validationChecks")
        else:
            for check_index, check in enumerate(checks):
                if not isinstance(check, dict) or not all(
                    nonempty(check.get(field), minimum=5) for field in ["method", "target", "passCriterion"]
                ):
                    failures.append(f"scene {scene_id} validationChecks[{check_index}] is incomplete")
        contract = scene.get("validationContract")
        if not isinstance(contract, dict):
            failures.append(f"scene {scene_id} validationContract is missing or not an object")
            contract = {}
        for contract_field in [
            "alignment",
            "safeZones",
            "edgePolicy",
            "boxPadding",
            "grayscaleHierarchy",
            "focalHierarchy",
        ]:
            if not nonempty(contract.get(contract_field), minimum=8):
                failures.append(
                    f"scene {scene_id} validationContract.{contract_field} is missing or too thin"
                )
        proof_artifacts = contract.get("verificationArtifacts")
        if not isinstance(proof_artifacts, list) or len(
            [item for item in proof_artifacts if nonempty(item, minimum=5)]
        ) < 2:
            failures.append(
                f"scene {scene_id} validationContract.verificationArtifacts needs at least two paths"
            )
        asset_ids = scene.get("assetIds")
        if not isinstance(asset_ids, list) or not asset_ids:
            failures.append(f"scene {scene_id} assetIds is missing or empty")
            asset_ids = []
        scene_assets[scene_id] = {str(item) for item in asset_ids if nonempty(item, minimum=2)}
        beat_ids = scene.get("beatIds")
        if not isinstance(beat_ids, list) or not beat_ids:
            failures.append(f"scene {scene_id} beatIds is missing or empty")
            beat_ids = []
        for beat_id in beat_ids:
            beat = str(beat_id)
            if not BEAT_ID_RE.fullmatch(beat):
                failures.append(f"scene {scene_id} has invalid beatId: {beat}")
            beat_scenes.setdefault(beat, set()).add(scene_id)
        raw_bounds = scene.get("objectBounds")
        bounds_info[scene_id] = validate_bounds(raw_bounds, scene_id, failures)
        spatial_signature = spatial_layout_signature(raw_bounds)
        if spatial_signature:
            spatial_layouts.add(spatial_signature)

    if len(scenes) >= 6 and len({item for item in compositions if item}) < 3:
        failures.append("multi-scene composition plan needs at least three distinct composition choices")
    if len(scenes) >= 6 and len({item for item in armatures if item}) < 3:
        failures.append("multi-scene composition plan needs at least three distinct armatures")
    if len(scenes) >= 6 and len(spatial_layouts) < 3:
        failures.append(
            "multi-scene composition plan needs at least three materially distinct spatial layouts from objectBounds"
        )
    return (
        {
            "sceneCount": len(scenes),
            "compositionChoiceCount": len({item for item in compositions if item}),
            "armatureCount": len({item for item in armatures if item}),
            "spatialLayoutCount": len(spatial_layouts),
            "bounds": bounds_info,
        },
        scenes,
        scene_assets,
        beat_scenes,
    )


def validate_seams(
    assets: dict[str, dict[str, Any]],
    manifest_scene_assets: dict[str, set[str]],
    manifest_beat_assets: dict[str, set[str]],
    scenes: dict[str, dict[str, Any]],
    composition_scene_assets: dict[str, set[str]],
    composition_beat_scenes: dict[str, set[str]],
    brief_rows: list[dict[str, str]],
    failures: list[str],
) -> dict[str, Any]:
    asset_ids = set(assets)
    scene_ids = set(scenes)
    unknown_manifest_scenes = sorted(set(manifest_scene_assets) - scene_ids)
    unknown_composition_assets = sorted(
        {asset for values in composition_scene_assets.values() for asset in values} - asset_ids
    )
    orphan_assets = sorted(asset_ids - {asset for values in composition_scene_assets.values() for asset in values})
    scenes_without_assets = sorted(
        scene_id
        for scene_id in scene_ids
        if not manifest_scene_assets.get(scene_id) or not composition_scene_assets.get(scene_id)
    )
    inconsistent_scene_links = sorted(
        scene_id
        for scene_id in scene_ids
        if manifest_scene_assets.get(scene_id, set()) != composition_scene_assets.get(scene_id, set())
    )
    for item in unknown_manifest_scenes:
        failures.append(f"asset manifest references unknown composition scene: {item}")
    for item in unknown_composition_assets:
        failures.append(f"composition plan references unknown asset: {item}")
    for item in orphan_assets:
        failures.append(f"asset is never used by the composition plan: {item}")
    for item in scenes_without_assets:
        failures.append(f"scene has no complete asset binding: {item}")
    for item in inconsistent_scene_links:
        failures.append(f"scene asset IDs disagree between manifest and composition plan: {item}")

    expected_beats = (
        {row["beat id"] for row in brief_rows}
        if brief_rows
        else set(composition_beat_scenes)
    )
    manifest_beats = set(manifest_beat_assets)
    composition_beats = set(composition_beat_scenes)
    missing_manifest_beats = sorted(expected_beats - manifest_beats)
    missing_composition_beats = sorted(expected_beats - composition_beats)
    extra_manifest_beats = sorted(manifest_beats - expected_beats)
    extra_composition_beats = sorted(composition_beats - expected_beats)
    for label, values in [
        ("asset manifest missing beat coverage", missing_manifest_beats),
        ("composition plan missing beat coverage", missing_composition_beats),
        ("asset manifest has unknown beats", extra_manifest_beats),
        ("composition plan has unknown beats", extra_composition_beats),
    ]:
        if values:
            failures.append(label + ": " + ", ".join(values))
    expected_scene_order = [row["scene id"] for row in brief_rows] if brief_rows else list(scenes)
    actual_scene_order = list(scenes)
    if actual_scene_order != expected_scene_order:
        failures.append(
            "composition scene order does not match brief Scene ID order: "
            + ", ".join(actual_scene_order)
        )
    beat_scene_mismatches: list[str] = []
    timing_mismatches: list[str] = []
    for row in brief_rows:
        beat_id = row["beat id"]
        scene_id = row["scene id"]
        if composition_beat_scenes.get(beat_id) != {scene_id}:
            beat_scene_mismatches.append(f"{beat_id}->{scene_id}")
        scene = scenes.get(scene_id, {})
        if str(scene.get("duration", "")).replace(" ", "") != row["time"].replace(" ", ""):
            timing_mismatches.append(f"{scene_id}:{row['time']}")
    if beat_scene_mismatches:
        failures.append(
            "composition Beat ID to Scene ID mapping disagrees with brief: "
            + ", ".join(beat_scene_mismatches)
        )
    if timing_mismatches:
        failures.append(
            "composition scene timing disagrees with brief: " + ", ".join(timing_mismatches)
        )
    return {
        "expectedBeatIds": sorted(expected_beats),
        "missingManifestBeatIds": missing_manifest_beats,
        "missingCompositionBeatIds": missing_composition_beats,
        "unknownManifestSceneIds": unknown_manifest_scenes,
        "unknownCompositionAssetIds": unknown_composition_assets,
        "orphanAssetIds": orphan_assets,
        "scenesWithoutAssets": scenes_without_assets,
        "inconsistentSceneAssetLinks": inconsistent_scene_links,
        "expectedSceneOrder": expected_scene_order,
        "actualSceneOrder": actual_scene_order,
        "briefBeatSceneMismatches": beat_scene_mismatches,
        "briefTimingMismatches": timing_mismatches,
    }


def validate_review(
    data: dict[str, Any],
    project_root: Path,
    scenes: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    expected_digests: dict[str, str | None],
    video: Path | None,
    failures: list[str],
    *,
    required: bool,
) -> dict[str, Any]:
    if not data:
        if required:
            failures.append("reviewed visual evidence is required but visual review is missing")
        return {"required": required, "sceneReviewCount": 0}
    if data.get("schemaVersion") != 1:
        failures.append("visual review schemaVersion must be 1")
    digests = data.get("inputDigests")
    if not isinstance(digests, dict):
        failures.append("visual review inputDigests is missing or not an object")
        digests = {}
    if required:
        for key, expected in expected_digests.items():
            if expected and digests.get(key) != expected:
                failures.append(f"visual review digest is stale or missing for {key}")
    if not nonempty(data.get("reviewer"), minimum=4):
        failures.append("visual review reviewer is missing")
    if not nonempty(data.get("reviewMethod"), minimum=20):
        failures.append("visual review reviewMethod is missing or too thin")
    contact_sheet_path = project_path(project_root, data.get("contactSheet"), "visual review contactSheet", failures)
    if required and contact_sheet_path is not None:
        result = inspect_raster(contact_sheet_path, min_width=320, min_height=180)
        for finding in result.get("failures", []):
            failures.append(f"visual review contact sheet: {finding}")
    playback = data.get("fullSpeedPlayback")
    if not isinstance(playback, dict):
        failures.append("visual review fullSpeedPlayback is missing or not an object")
        playback = {}
    if required and playback.get("reviewed") is not True:
        failures.append("visual review must confirm full-speed playback was reviewed")
    if required and not nonempty(playback.get("notes"), minimum=20):
        failures.append("visual review fullSpeedPlayback.notes is missing or too thin")
    candidate_video = data.get("candidateVideo")
    review_video_path: Path | None = None
    if not isinstance(candidate_video, dict):
        candidate_video = {}
        if required:
            failures.append("visual review candidateVideo is missing or not an object")
    if required:
        review_video_path = project_path(
            project_root,
            candidate_video.get("path"),
            "visual review candidateVideo",
            failures,
        )
        expected_video = video.resolve() if video is not None else None
        if review_video_path is not None:
            if not review_video_path.is_file():
                failures.append(f"visual review candidate video missing: {review_video_path}")
            else:
                actual_video_hash = sha256_file(review_video_path)
                if candidate_video.get("sha256") != actual_video_hash:
                    failures.append("visual review candidateVideo.sha256 is stale or invalid")
            if expected_video is not None and review_video_path.resolve() != expected_video:
                failures.append("visual review candidateVideo.path does not match the delivered video")

    raw_scene_reviews = data.get("scenes")
    if not isinstance(raw_scene_reviews, list):
        failures.append("visual review scenes is missing or not a list")
        raw_scene_reviews = []
    reviewed: dict[str, dict[str, Any]] = {}
    evidence_frame_count = 0
    scene_evidence_frame_count = 0
    transition_evidence_frame_count = 0
    evidence_paths: set[str] = set()
    evidence_hashes: dict[str, str] = {}
    scene_intervals = {
        scene_id: parse_time_range(scene.get("duration"))
        for scene_id, scene in scenes.items()
        if isinstance(scene, dict)
    }
    video_frame_matches: list[dict[str, Any]] = []
    for index, review in enumerate(raw_scene_reviews):
        if not isinstance(review, dict):
            failures.append(f"visual review scenes[{index}] is not an object")
            continue
        scene_id = str(review.get("sceneId", "")).strip()
        if scene_id in reviewed:
            failures.append(f"duplicate visual review sceneId: {scene_id}")
        reviewed[scene_id] = review
        if scene_id not in scenes:
            failures.append(f"visual review references unknown scene: {scene_id}")
        if review.get("compositionId") != scene_id:
            failures.append(f"visual review scene {scene_id} compositionId must match sceneId")
        review_assets = {str(item) for item in review.get("assetIds", []) if isinstance(item, str)}
        expected_assets = set(scenes.get(scene_id, {}).get("assetIds", []))
        if review_assets != expected_assets:
            failures.append(f"visual review scene {scene_id} assetIds do not match composition plan")
        unknown = sorted(review_assets - set(assets))
        if unknown:
            failures.append(f"visual review scene {scene_id} has unknown assets: {', '.join(unknown)}")
        frames = review.get("evidenceFrames")
        if not isinstance(frames, list) or not frames:
            if required:
                failures.append(f"visual review scene {scene_id} lacks evidenceFrames")
            frames = []
        phase_records: dict[str, tuple[float, Path]] = {}
        for frame_index, frame in enumerate(frames):
            if not isinstance(frame, dict):
                failures.append(f"visual review scene {scene_id} evidenceFrames[{frame_index}] is not an object")
                continue
            phase = str(frame.get("phase", "")).strip().lower()
            timestamp = frame.get("timestamp")
            if phase not in SCENE_EVIDENCE_PHASES or not isinstance(timestamp, (int, float)):
                failures.append(f"visual review scene {scene_id} evidence frame needs phase and numeric timestamp")
            frame_path = project_path(
                project_root,
                frame.get("path"),
                f"visual review scene {scene_id} evidence frame",
                failures,
            )
            raw_frame_path = str(frame.get("path", ""))
            if raw_frame_path in evidence_paths:
                failures.append(f"visual review reuses one evidence frame across scenes: {raw_frame_path}")
            evidence_paths.add(raw_frame_path)
            if required and frame_path is not None:
                result = inspect_raster(frame_path, min_width=320, min_height=180)
                for finding in result.get("failures", []):
                    failures.append(f"visual review scene {scene_id} evidence frame: {finding}")
                if frame_path.is_file():
                    actual_frame_hash = sha256_file(frame_path)
                    if frame.get("sha256") != actual_frame_hash:
                        failures.append(f"visual review scene {scene_id} evidence frame sha256 is stale or invalid")
                    if actual_frame_hash is not None:
                        previous_path = evidence_hashes.get(actual_frame_hash)
                        if previous_path is not None:
                            failures.append(
                                f"visual review reuses an evidence-frame hash for {raw_frame_path}; first used by {previous_path}"
                            )
                        else:
                            evidence_hashes[actual_frame_hash] = raw_frame_path
                if frame_path.is_file() and isinstance(timestamp, (int, float)) and phase in SCENE_EVIDENCE_PHASES:
                    if phase in phase_records:
                        failures.append(f"visual review scene {scene_id} duplicates evidence phase {phase}")
                    phase_records[phase] = (float(timestamp), frame_path)
                    if review_video_path is not None and review_video_path.is_file():
                        match = compare_evidence_to_video(review_video_path, float(timestamp), frame_path)
                        match.update({"kind": "scene", "sceneId": scene_id, "phase": phase})
                        video_frame_matches.append(match)
                        for finding in match.get("failures", []):
                            failures.append(f"visual review scene {scene_id} {phase}: {finding}")
            evidence_frame_count += 1
            scene_evidence_frame_count += 1
        if required and (set(phase_records) != SCENE_EVIDENCE_PHASES or len(frames) != len(SCENE_EVIDENCE_PHASES)):
            missing_phases = sorted(SCENE_EVIDENCE_PHASES - set(phase_records))
            failures.append(
                f"visual review scene {scene_id} must provide exactly first/hold/emphasis/final evidence"
                + (f"; missing {', '.join(missing_phases)}" if missing_phases else "")
            )
        if required and set(phase_records) == SCENE_EVIDENCE_PHASES:
            ordered_timestamps = [phase_records[name][0] for name in ["first", "hold", "emphasis", "final"]]
            if not all(left < right for left, right in zip(ordered_timestamps, ordered_timestamps[1:])):
                failures.append(
                    f"visual review scene {scene_id} timestamps must increase first < hold < emphasis < final"
                )
            interval = scene_intervals.get(scene_id)
            if interval is None:
                failures.append(f"visual review scene {scene_id} has no valid composition time interval")
            elif not all(interval[0] <= timestamp < interval[1] for timestamp in ordered_timestamps):
                failures.append(
                    f"visual review scene {scene_id} evidence timestamps must stay inside "
                    f"{interval[0]:g}-{interval[1]:g}s"
                )
        checks = review.get("checks")
        if not isinstance(checks, dict):
            failures.append(f"visual review scene {scene_id} checks is missing or not an object")
            checks = {}
        if required:
            missing_checks = sorted(REVIEW_CHECKS - set(checks))
            if missing_checks:
                failures.append(f"visual review scene {scene_id} missing checks: {', '.join(missing_checks)}")
            failed_checks = sorted(key for key in REVIEW_CHECKS if checks.get(key) != "pass")
            if failed_checks:
                failures.append(f"visual review scene {scene_id} has unresolved checks: {', '.join(failed_checks)}")
            if review.get("status") != "approved":
                failures.append(f"visual review scene {scene_id} status is not approved")
            if not nonempty(review.get("finding"), minimum=20):
                failures.append(f"visual review scene {scene_id} finding is missing or too thin")
            if not nonempty(review.get("correction"), minimum=20):
                failures.append(f"visual review scene {scene_id} correction is missing or too thin")

    missing_scene_reviews = sorted(set(scenes) - set(reviewed))
    if required and missing_scene_reviews:
        failures.append("visual review is missing scenes: " + ", ".join(missing_scene_reviews))
    transitions = data.get("transitions")
    if not isinstance(transitions, list):
        transitions = []
        if required and len(scenes) > 1:
            failures.append("visual review transitions is missing or not a list")
    if required and len(scenes) > 1:
        ordered_scene_ids = list(scenes)
        expected_pairs = list(zip(ordered_scene_ids, ordered_scene_ids[1:]))
        expected_transition_count = len(expected_pairs)
        if len(transitions) < expected_transition_count:
            failures.append(
                f"visual review needs at least {expected_transition_count} transition evidence entries, found {len(transitions)}"
            )
        observed_pairs: set[tuple[str, str]] = set()
        for index, transition in enumerate(transitions):
            if not isinstance(transition, dict):
                failures.append(f"visual review transitions[{index}] is not an object")
                continue
            for field in ["fromScene", "toScene"]:
                if transition.get(field) not in scenes:
                    failures.append(f"visual review transition {index} has unknown {field}")
            pair = (str(transition.get("fromScene", "")), str(transition.get("toScene", "")))
            observed_pairs.add(pair)
            expected_id = f"{pair[0]}__{pair[1]}"
            if transition.get("id") != expected_id:
                failures.append(f"visual review transition {index} id must be {expected_id}")
            if transition.get("status") != "pass" or not nonempty(transition.get("finding"), minimum=20):
                failures.append(f"visual review transition {index} lacks passing, substantive evidence")
            transition_frames = transition.get("evidenceFrames")
            if not isinstance(transition_frames, list):
                failures.append(f"visual review transition {index} evidenceFrames is missing or not a list")
                transition_frames = []
            transition_phase_records: dict[str, tuple[float, Path]] = {}
            for frame_index, frame in enumerate(transition_frames):
                if not isinstance(frame, dict):
                    failures.append(
                        f"visual review transition {index} evidenceFrames[{frame_index}] is not an object"
                    )
                    continue
                phase = str(frame.get("phase", "")).strip().lower()
                timestamp = frame.get("timestamp")
                if phase not in TRANSITION_EVIDENCE_PHASES or not isinstance(timestamp, (int, float)):
                    failures.append(
                        f"visual review transition {index} evidence frame needs before/midpoint/after phase and numeric timestamp"
                    )
                frame_path = project_path(
                    project_root,
                    frame.get("path"),
                    f"visual review transition {index} evidence frame",
                    failures,
                )
                raw_frame_path = str(frame.get("path", ""))
                if raw_frame_path in evidence_paths:
                    failures.append(f"visual review reuses one evidence frame: {raw_frame_path}")
                evidence_paths.add(raw_frame_path)
                if frame_path is not None:
                    result = inspect_raster(frame_path, min_width=320, min_height=180)
                    for finding in result.get("failures", []):
                        failures.append(f"visual review transition {index} frame: {finding}")
                    if frame_path.is_file():
                        actual_frame_hash = sha256_file(frame_path)
                        if frame.get("sha256") != actual_frame_hash:
                            failures.append(f"visual review transition {index} frame sha256 is stale or invalid")
                        if actual_frame_hash is not None:
                            previous_path = evidence_hashes.get(actual_frame_hash)
                            if previous_path is not None:
                                failures.append(
                                    f"visual review reuses an evidence-frame hash for {raw_frame_path}; "
                                    f"first used by {previous_path}"
                                )
                            else:
                                evidence_hashes[actual_frame_hash] = raw_frame_path
                    if frame_path.is_file() and isinstance(timestamp, (int, float)) and phase in TRANSITION_EVIDENCE_PHASES:
                        if phase in transition_phase_records:
                            failures.append(f"visual review transition {index} duplicates evidence phase {phase}")
                        transition_phase_records[phase] = (float(timestamp), frame_path)
                        if review_video_path is not None and review_video_path.is_file():
                            match = compare_evidence_to_video(review_video_path, float(timestamp), frame_path)
                            match.update({"kind": "transition", "transitionId": expected_id, "phase": phase})
                            video_frame_matches.append(match)
                            for finding in match.get("failures", []):
                                failures.append(f"visual review transition {index} {phase}: {finding}")
                evidence_frame_count += 1
                transition_evidence_frame_count += 1
            if set(transition_phase_records) != TRANSITION_EVIDENCE_PHASES or len(transition_frames) != len(
                TRANSITION_EVIDENCE_PHASES
            ):
                failures.append(
                    f"visual review transition {index} must provide exactly before/midpoint/after evidence"
                )
            if set(transition_phase_records) == TRANSITION_EVIDENCE_PHASES:
                before = transition_phase_records["before"][0]
                midpoint = transition_phase_records["midpoint"][0]
                after = transition_phase_records["after"][0]
                if not before < midpoint < after:
                    failures.append(
                        f"visual review transition {index} timestamps must increase before < midpoint < after"
                    )
                from_interval = scene_intervals.get(pair[0])
                to_interval = scene_intervals.get(pair[1])
                if from_interval is None or to_interval is None:
                    failures.append(f"visual review transition {index} lacks valid adjacent scene intervals")
                else:
                    seam = from_interval[1]
                    if abs(to_interval[0] - seam) > 0.001:
                        failures.append(
                            f"visual review transition {index} scene intervals do not share one seam"
                        )
                    if not (from_interval[0] <= before < seam < after < to_interval[1]):
                        failures.append(
                            f"visual review transition {index} evidence must straddle the {seam:g}s seam "
                            "with before in the outgoing scene and after in the incoming scene"
                        )
                    if before < midpoint < after and (
                        midpoint < max(from_interval[0], seam - 1.0)
                        or midpoint > min(to_interval[1], seam + 1.0)
                    ):
                        failures.append(
                            f"visual review transition {index} midpoint must remain within one second of the {seam:g}s seam"
                        )
        missing_pairs = [pair for pair in expected_pairs if pair not in observed_pairs]
        extra_pairs = sorted(observed_pairs - set(expected_pairs))
        if missing_pairs:
            failures.append(
                "visual review missing adjacent transition pairs: "
                + ", ".join(f"{left}->{right}" for left, right in missing_pairs)
            )
        if extra_pairs:
            failures.append(
                "visual review contains non-adjacent transition pairs: "
                + ", ".join(f"{left}->{right}" for left, right in extra_pairs)
            )
    blockers = data.get("unresolvedBlockers")
    if required and (not isinstance(blockers, list) or blockers):
        failures.append("visual review unresolvedBlockers must be an empty list")
    if required and data.get("overallStatus") != "approved":
        failures.append("visual review overallStatus must be approved")
    return {
        "required": required,
        "sceneReviewCount": len(reviewed),
        "missingSceneReviews": missing_scene_reviews,
        "evidenceFrameCount": evidence_frame_count,
        "sceneEvidenceFrameCount": scene_evidence_frame_count,
        "transitionEvidenceFrameCount": transition_evidence_frame_count,
        "transitionReviewCount": len(transitions),
        "uniqueEvidenceHashCount": len(evidence_hashes),
        "videoFrameMatchCount": len(video_frame_matches),
        "videoFrameMatches": video_frame_matches,
        "overallStatus": data.get("overallStatus"),
    }


def validate(args: argparse.Namespace) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    project_root = (args.project_root or args.asset_manifest.parent.parent).resolve()
    asset_data = read_json(args.asset_manifest, "asset manifest", failures)
    composition_data = read_json(args.composition_plan, "composition plan", failures)
    review_data = (
        read_json(args.visual_review, "visual review", failures)
        if args.visual_review is not None
        else {}
    )
    brief_rows = brief_beat_contract(args.brief, failures)

    asset_info, assets, manifest_scene_assets, manifest_beat_assets = validate_asset_manifest(
        asset_data,
        project_root,
        failures,
        warnings,
        min_assets=args.min_assets,
        require_ready=args.require_ready_assets,
    )
    composition_info, scenes, composition_scene_assets, composition_beat_scenes = validate_composition_plan(
        composition_data,
        failures,
        min_scenes=args.min_scenes,
    )
    routing_info = validate_skill_routing(
        asset_data.get("skillRouting"),
        project_root,
        failures,
        require_specialist=args.require_specialist_routing,
        require_source=args.require_source_routing,
        require_complete=args.require_ready_assets,
        scene_count=len(scenes),
    )
    if args.require_specialist_routing:
        producer_skills = set(asset_info.get("producerSkills", []))
        if not producer_skills.intersection(SPECIALIST_ASSET_SKILLS - {"repo-native"}):
            failures.append("specialist routing requires at least one non-fallback specialist asset producer")
    seam_info = validate_seams(
        assets,
        manifest_scene_assets,
        manifest_beat_assets,
        scenes,
        composition_scene_assets,
        composition_beat_scenes,
        brief_rows,
        failures,
    )
    source_digests = {
        "assetManifestSha256": sha256_file(args.asset_manifest),
        "compositionPlanSha256": sha256_file(args.composition_plan),
    }
    input_digests = {
        **source_digests,
        "visualReviewSha256": sha256_file(args.visual_review) if args.visual_review is not None else None,
        "videoSha256": sha256_file(args.video) if args.video is not None else None,
    }
    review_info = validate_review(
        review_data,
        project_root,
        scenes,
        assets,
        source_digests,
        args.video,
        failures,
        required=args.require_reviewed_scenes,
    )
    return {
        "schemaVersion": 1,
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
        "projectRoot": str(project_root),
        "inputDigests": input_digests,
        "assetManifest": asset_info,
        "compositionPlan": composition_info,
        "skillRouting": routing_info,
        "seams": seam_info,
        "visualReview": review_info,
    }


def main() -> int:
    args = parse_args()
    result = validate(args)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(result, indent=2))
    elif result["ok"]:
        print(
            "PASS awsome-videos visual contract: "
            f"{result['assetManifest']['assetCount']} assets, "
            f"{result['compositionPlan']['sceneCount']} scenes"
        )
    else:
        print("FAIL awsome-videos visual contract")
        for failure in result["failures"]:
            print(f"- {failure}")
        for warning in result.get("warnings", []):
            print(f"WARN {warning}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

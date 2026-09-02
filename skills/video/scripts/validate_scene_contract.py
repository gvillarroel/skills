#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate a mixed-media video scene contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
KINDS = {"gif", "html", "raster", "svg", "video"}
FIT_MODES = {"contain", "cover", "none", "stretch"}
OVERFLOW_MODES = {"allow", "hidden", "visible"}
CLOCK_MODES = {"autonomous", "master", "static"}
TRACK_PROPERTIES = {"opacity", "rotate", "scale", "state", "translateX", "translateY"}
INTERACTION_CHANNELS = {"camera-follow", "data-state", "handoff", "highlight", "reveal", "signal"}
PORT_ANCHORS = {"bottom", "center", "left", "right", "top"}
PRODUCER_SKILLS = {
    "animated-svg-to-gif",
    "browser:control-in-app-browser",
    "d3",
    "echarts-animated-svg",
    "imagegen",
    "mermaid",
    "plantuml-colorset-renderer",
    "playwright",
    "repo-native",
    "slidev-animejs",
    "slidev-echarts",
    "threejs-animated-3d",
    "user-provided",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a mixed-media video scene contract.")
    parser.add_argument("contract", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--require-files", action="store_true")
    parser.add_argument("--require-hashes", action="store_true")
    parser.add_argument("--require-producer-reports", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty(value: Any, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def project_path(root: Path, raw: Any, label: str, failures: list[str]) -> Path | None:
    if not nonempty(raw):
        failures.append(f"{label} is missing")
        return None
    relative = Path(str(raw))
    if relative.is_absolute() or relative.drive:
        failures.append(f"{label} must be project-relative")
        return None
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        failures.append(f"{label} escapes the project root")
        return None
    return resolved


def validate_id(value: Any, label: str, failures: list[str]) -> str:
    result = str(value or "").strip()
    if not ID_RE.fullmatch(result):
        failures.append(f"{label} must be lowercase hyphen-case")
    return result


def validate_bounds(value: Any, label: str, overflow: str, failures: list[str]) -> None:
    if not isinstance(value, dict):
        failures.append(f"{label} must be an object")
        return
    values = [value.get(field) for field in ("x", "y", "width", "height")]
    if not all(number(item) for item in values):
        failures.append(f"{label} needs numeric x/y/width/height")
        return
    x, y, width, height = [float(item) for item in values]
    if width <= 0 or height <= 0:
        failures.append(f"{label} width and height must be positive")
    if overflow != "allow" and (x < 0 or y < 0 or x + width > 1.000001 or y + height > 1.000001):
        failures.append(f"{label} falls outside normalized canvas bounds")


def validate_contract(
    data: Any,
    project_root: Path,
    *,
    require_files: bool = False,
    require_hashes: bool = False,
    require_producer_reports: bool = False,
) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    root = project_root.resolve()
    if not isinstance(data, dict):
        return {"ok": False, "passed": False, "failures": ["contract root must be an object"], "warnings": []}

    if data.get("schemaVersion") != 1:
        failures.append("schemaVersion must be 1")
    scene_id = validate_id(data.get("id"), "id", failures)

    canvas = data.get("canvas")
    if not isinstance(canvas, dict):
        failures.append("canvas must be an object")
        canvas = {}
    width = canvas.get("width")
    height = canvas.get("height")
    fps = canvas.get("fps")
    duration = canvas.get("durationSeconds")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        failures.append("canvas.width must be a positive integer")
        width = 1
    if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
        failures.append("canvas.height must be a positive integer")
        height = 1
    if not number(fps) or float(fps) <= 0:
        failures.append("canvas.fps must be positive")
    if not number(duration) or float(duration) <= 0:
        failures.append("canvas.durationSeconds must be positive")
        duration = 0.0
    divisor = math.gcd(int(width), int(height))
    expected_ratio = f"{int(width) // divisor}:{int(height) // divisor}"
    if canvas.get("aspectRatio") != expected_ratio:
        failures.append(f"canvas.aspectRatio must equal the reduced ratio {expected_ratio}")
    if not nonempty(canvas.get("background")):
        failures.append("canvas.background is missing")
    safe_area = canvas.get("safeArea")
    if not isinstance(safe_area, dict):
        failures.append("canvas.safeArea must be an object")
        safe_area = {}
    safe_values: dict[str, int] = {}
    for edge in ("top", "right", "bottom", "left"):
        value = safe_area.get(edge)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            failures.append(f"canvas.safeArea.{edge} must be a non-negative integer")
            value = 0
        safe_values[edge] = value
    if safe_values["left"] + safe_values["right"] >= int(width):
        failures.append("horizontal safe areas consume the canvas")
    if safe_values["top"] + safe_values["bottom"] >= int(height):
        failures.append("vertical safe areas consume the canvas")

    master_clock = data.get("masterClock")
    if not isinstance(master_clock, dict) or master_clock.get("mode") != "deterministic":
        failures.append("masterClock.mode must be deterministic")

    raw_elements = data.get("elements")
    if not isinstance(raw_elements, list) or not raw_elements:
        failures.append("elements must be a non-empty list")
        raw_elements = []
    elements: dict[str, dict[str, Any]] = {}
    element_ports: dict[str, set[str]] = {}
    producer_skills: set[str] = set()
    source_paths: dict[str, str] = {}
    for index, element in enumerate(raw_elements):
        label = f"elements[{index}]"
        if not isinstance(element, dict):
            failures.append(f"{label} must be an object")
            continue
        element_id = validate_id(element.get("id"), f"{label}.id", failures)
        if element_id in elements:
            failures.append(f"duplicate element id: {element_id}")
        elements[element_id] = element
        validate_id(element.get("assetId"), f"{label}.assetId", failures)
        producer = str(element.get("producerSkill") or "").strip()
        producer_skills.add(producer)
        if producer not in PRODUCER_SKILLS:
            failures.append(f"{label}.producerSkill is unsupported: {producer or '<missing>'}")
        if producer == "repo-native" and not nonempty(element.get("fallbackReason"), 12):
            failures.append(f"{label} repo-native fallback requires fallbackReason")
        kind = str(element.get("kind") or "").strip()
        if kind not in KINDS:
            failures.append(f"{label}.kind is unsupported: {kind or '<missing>'}")
        fit = str(element.get("fit") or "").strip()
        if fit not in FIT_MODES:
            failures.append(f"{label}.fit is unsupported: {fit or '<missing>'}")
        overflow = str(element.get("overflow") or "").strip()
        if overflow not in OVERFLOW_MODES:
            failures.append(f"{label}.overflow is unsupported: {overflow or '<missing>'}")
            overflow = "hidden"
        validate_bounds(element.get("bounds"), f"{label}.bounds", overflow, failures)
        if not isinstance(element.get("zIndex"), int) or isinstance(element.get("zIndex"), bool):
            failures.append(f"{label}.zIndex must be an integer")
        if not nonempty(element.get("background")):
            failures.append(f"{label}.background is missing")
        clock = str(element.get("clock") or "").strip()
        if clock not in CLOCK_MODES:
            failures.append(f"{label}.clock is unsupported: {clock or '<missing>'}")
        if clock == "autonomous" and not nonempty(element.get("clockAdapter"), 8):
            failures.append(f"{label} autonomous clock requires clockAdapter")
        if kind == "gif":
            playback = element.get("playback")
            if not isinstance(playback, dict) or playback.get("mode") not in {"container", "decoded"}:
                failures.append(f"{label} GIF requires playback.mode decoded or container")
            elif playback.get("mode") == "decoded" and clock != "master":
                failures.append(f"{label} decoded GIF must use clock=master")
            elif playback.get("mode") == "container":
                warnings.append(f"{label} uses nondeterministic container GIF playback")
        raw_src = element.get("src")
        resolved = project_path(root, raw_src, f"{label}.src", failures)
        source_paths[element_id] = str(raw_src or "")
        if resolved is not None:
            if require_files and not resolved.is_file():
                failures.append(f"{label}.src does not exist: {resolved}")
            declared_hash = str(element.get("sha256") or "")
            if require_hashes and not HASH_RE.fullmatch(declared_hash):
                failures.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
            if resolved.is_file() and HASH_RE.fullmatch(declared_hash) and sha256_file(resolved) != declared_hash:
                failures.append(f"{label}.sha256 does not match {raw_src}")
        report_path = project_path(root, element.get("validationReport"), f"{label}.validationReport", failures)
        if require_producer_reports and report_path is not None:
            if not report_path.is_file():
                failures.append(f"{label}.validationReport does not exist: {report_path}")
            else:
                try:
                    report = json.loads(report_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    failures.append(f"{label}.validationReport is invalid: {exc}")
                else:
                    if not isinstance(report, dict) or (report.get("ok") is not True and report.get("passed") is not True):
                        failures.append(f"{label}.validationReport does not carry a passing status")
        elif not nonempty(element.get("validationReport")):
            warnings.append(f"{label}.validationReport is not declared")
        intrinsic = element.get("intrinsic")
        if not isinstance(intrinsic, dict) or not (
            (number(intrinsic.get("width")) and number(intrinsic.get("height")))
            or nonempty(intrinsic.get("viewBox"), 3)
        ):
            failures.append(f"{label}.intrinsic needs width/height or viewBox")
        raw_ports = element.get("ports", [])
        if not isinstance(raw_ports, list):
            failures.append(f"{label}.ports must be a list")
            raw_ports = []
        ports: set[str] = set()
        for port_index, port in enumerate(raw_ports):
            port_label = f"{label}.ports[{port_index}]"
            if not isinstance(port, dict):
                failures.append(f"{port_label} must be an object")
                continue
            port_id = validate_id(port.get("id"), f"{port_label}.id", failures)
            if port_id in ports:
                failures.append(f"{label} has duplicate port id: {port_id}")
            ports.add(port_id)
            has_coordinates = number(port.get("x")) and number(port.get("y"))
            has_selector = nonempty(port.get("selector"))
            if has_coordinates == has_selector:
                failures.append(f"{port_label} needs either normalized x/y or selector, but not both")
            if has_coordinates and not (0 <= float(port["x"]) <= 1 and 0 <= float(port["y"]) <= 1):
                failures.append(f"{port_label} normalized coordinates must be within 0..1")
            if has_selector and port.get("anchor") not in PORT_ANCHORS:
                failures.append(f"{port_label}.anchor must be one of {', '.join(sorted(PORT_ANCHORS))}")
        element_ports[element_id] = ports
        states = element.get("states", [])
        if not isinstance(states, list) or any(not ID_RE.fullmatch(str(item)) for item in states):
            failures.append(f"{label}.states must be a list of lowercase hyphen-case IDs")
        elif len(set(states)) != len(states):
            failures.append(f"{label}.states contains duplicates")

    raw_events = data.get("events", [])
    if not isinstance(raw_events, list):
        failures.append("events must be a list")
        raw_events = []
    events: dict[str, float] = {}
    for index, event in enumerate(raw_events):
        label = f"events[{index}]"
        if not isinstance(event, dict):
            failures.append(f"{label} must be an object")
            continue
        event_id = validate_id(event.get("id"), f"{label}.id", failures)
        if event_id in events:
            failures.append(f"duplicate event id: {event_id}")
        at = event.get("at")
        if not number(at) or not (0 <= float(at) <= float(duration)):
            failures.append(f"{label}.at must fit the scene duration")
            at = 0.0
        events[event_id] = float(at)

    raw_tracks = data.get("tracks", [])
    if not isinstance(raw_tracks, list):
        failures.append("tracks must be a list")
        raw_tracks = []
    track_ids: set[str] = set()
    for index, track in enumerate(raw_tracks):
        label = f"tracks[{index}]"
        if not isinstance(track, dict):
            failures.append(f"{label} must be an object")
            continue
        track_id = validate_id(track.get("id"), f"{label}.id", failures)
        if track_id in track_ids:
            failures.append(f"duplicate track id: {track_id}")
        track_ids.add(track_id)
        element_id = str(track.get("elementId") or "")
        if element_id not in elements:
            failures.append(f"{label}.elementId references unknown element: {element_id or '<missing>'}")
        prop = str(track.get("property") or "")
        if prop not in TRACK_PROPERTIES:
            failures.append(f"{label}.property is unsupported: {prop or '<missing>'}")
        if prop in {"translateX", "translateY"} and track.get("unit") not in {"normalized", "pixels"}:
            failures.append(f"{label}.unit must be normalized or pixels")
        keyframes = track.get("keyframes")
        if not isinstance(keyframes, list) or not keyframes:
            failures.append(f"{label}.keyframes must be a non-empty list")
            continue
        previous_at = -1.0
        declared_states = set(elements.get(element_id, {}).get("states", []))
        for frame_index, frame in enumerate(keyframes):
            frame_label = f"{label}.keyframes[{frame_index}]"
            if not isinstance(frame, dict) or not number(frame.get("at")):
                failures.append(f"{frame_label}.at must be numeric")
                continue
            at = float(frame["at"])
            if at < previous_at or not (0 <= at <= float(duration)):
                failures.append(f"{frame_label}.at must be ordered and fit the scene duration")
            previous_at = at
            value = frame.get("value")
            if prop == "state":
                if value not in declared_states:
                    failures.append(f"{frame_label}.value is not declared in element states")
            elif not number(value):
                failures.append(f"{frame_label}.value must be numeric")
            elif prop == "opacity" and not (0 <= float(value) <= 1):
                failures.append(f"{frame_label}.value for opacity must be within 0..1")
            elif prop == "scale" and float(value) <= 0:
                failures.append(f"{frame_label}.value for scale must be positive")

    raw_interactions = data.get("interactions")
    if not isinstance(raw_interactions, list):
        failures.append("interactions must be a list")
        raw_interactions = []
    interaction_ids: set[str] = set()
    cross_producer_count = 0
    for index, interaction in enumerate(raw_interactions):
        label = f"interactions[{index}]"
        if not isinstance(interaction, dict):
            failures.append(f"{label} must be an object")
            continue
        interaction_id = validate_id(interaction.get("id"), f"{label}.id", failures)
        if interaction_id in interaction_ids:
            failures.append(f"duplicate interaction id: {interaction_id}")
        interaction_ids.add(interaction_id)
        if interaction.get("channel") not in INTERACTION_CHANNELS:
            failures.append(f"{label}.channel is unsupported")
        if not nonempty(interaction.get("type"), 3):
            failures.append(f"{label}.type is missing")
        if not nonempty(interaction.get("meaning"), 12):
            failures.append(f"{label}.meaning is missing or too thin")
        start = interaction.get("start")
        end = interaction.get("end")
        if not number(start) or not number(end) or not (0 <= float(start) < float(end) <= float(duration)):
            failures.append(f"{label} start/end must form a positive window inside the scene")
        endpoints: list[tuple[str, str]] = []
        for endpoint_name in ("source", "target"):
            endpoint = interaction.get(endpoint_name)
            if not isinstance(endpoint, dict):
                failures.append(f"{label}.{endpoint_name} must be an object")
                continue
            element_id = str(endpoint.get("element") or "")
            port_id = str(endpoint.get("port") or "")
            if element_id not in elements:
                failures.append(f"{label}.{endpoint_name}.element is unknown: {element_id or '<missing>'}")
            elif port_id not in element_ports.get(element_id, set()):
                failures.append(f"{label}.{endpoint_name}.port is unknown for {element_id}: {port_id or '<missing>'}")
            endpoints.append((element_id, port_id))
        if len(endpoints) == 2:
            if endpoints[0] == endpoints[1]:
                failures.append(f"{label} source and target must differ")
            source_producer = str(elements.get(endpoints[0][0], {}).get("producerSkill") or "")
            target_producer = str(elements.get(endpoints[1][0], {}).get("producerSkill") or "")
            if source_producer and target_producer and source_producer != target_producer:
                cross_producer_count += 1
        for field in ("emits", "consumes"):
            values = interaction.get(field, [])
            if not isinstance(values, list):
                failures.append(f"{label}.{field} must be a list")
                continue
            unknown = [str(item) for item in values if str(item) not in events]
            if unknown:
                failures.append(f"{label}.{field} references unknown events: {', '.join(unknown)}")
        checks = interaction.get("validationChecks")
        if not isinstance(checks, list) or not any(nonempty(item, 8) for item in checks):
            failures.append(f"{label}.validationChecks needs at least one concrete check")
        connector = interaction.get("connector")
        if interaction.get("channel") in {"handoff", "signal"}:
            if not isinstance(connector, dict):
                failures.append(f"{label}.connector is required for visible handoff/signal interactions")
            else:
                if connector.get("path") not in {"curve", "straight"}:
                    failures.append(f"{label}.connector.path must be curve or straight")
                if not number(connector.get("width")) or float(connector.get("width")) <= 0:
                    failures.append(f"{label}.connector.width must be positive")
                if not isinstance(connector.get("zIndex"), int):
                    failures.append(f"{label}.connector.zIndex must be an integer")
                if not nonempty(connector.get("color")):
                    failures.append(f"{label}.connector.color is missing")

    if len(producer_skills) > 1 and not raw_interactions:
        warnings.append("scene uses multiple producers but declares no cross-element interactions")

    report = {
        "schemaVersion": 1,
        "ok": not failures,
        "passed": not failures,
        "sceneId": scene_id,
        "failures": failures,
        "warnings": warnings,
        "summary": {
            "width": width,
            "height": height,
            "aspectRatio": expected_ratio,
            "durationSeconds": duration,
            "elementCount": len(elements),
            "producerSkills": sorted(skill for skill in producer_skills if skill),
            "trackCount": len(raw_tracks),
            "eventCount": len(events),
            "interactionCount": len(raw_interactions),
            "crossProducerInteractionCount": cross_producer_count,
            "sourcePaths": source_paths,
        },
    }
    return report


def main() -> int:
    args = parse_args()
    try:
        data = json.loads(args.contract.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report = {"schemaVersion": 1, "ok": False, "passed": False, "failures": [f"contract missing: {args.contract}"], "warnings": []}
    except json.JSONDecodeError as exc:
        report = {"schemaVersion": 1, "ok": False, "passed": False, "failures": [f"invalid JSON: {exc}"], "warnings": []}
    else:
        report = validate_contract(
            data,
            args.project_root,
            require_files=args.require_files,
            require_hashes=args.require_hashes,
            require_producer_reports=args.require_producer_reports,
        )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    if args.json:
        print(json.dumps(report, indent=2))
    elif report.get("ok"):
        summary = report.get("summary", {})
        print(
            "PASS video scene contract: "
            f"{summary.get('elementCount', 0)} elements, "
            f"{summary.get('interactionCount', 0)} interactions, "
            f"{summary.get('width')}x{summary.get('height')}"
        )
    else:
        for failure in report.get("failures", []):
            print(f"FAIL: {failure}", file=sys.stderr)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

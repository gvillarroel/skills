#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0"]
# ///
"""Build a deterministic browser compositor from a video scene contract."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
from io import BytesIO
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageSequence


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE = SKILL_DIR / "assets" / "templates" / "composite-scene-template.html"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import validate_scene_contract  # noqa: E402


ID_ATTRIBUTE_RE = re.compile(r"\bid\s*=\s*([\"'])([^\"']+)\1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a deterministic mixed-media HTML scene.")
    parser.add_argument("contract", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument("--allow-missing-hashes", action="store_true")
    parser.add_argument("--require-producer-reports", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def namespace_svg(svg: str, prefix: str) -> tuple[str, dict[str, str]]:
    identifiers = list(dict.fromkeys(match.group(2) for match in ID_ATTRIBUTE_RE.finditer(svg)))
    mapping = {identifier: f"{prefix}__{identifier}" for identifier in identifiers}
    if not mapping:
        return svg, mapping

    def replace_id(match: re.Match[str]) -> str:
        quote = match.group(1)
        identifier = match.group(2)
        return f"id={quote}{mapping.get(identifier, identifier)}{quote}"

    result = ID_ATTRIBUTE_RE.sub(replace_id, svg)
    for original, namespaced in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        escaped = re.escape(original)
        result = re.sub(rf"url\(\s*#{escaped}\s*\)", f"url(#{namespaced})", result)
        result = re.sub(
            rf"((?:href|xlink:href)\s*=\s*[\"'])#{escaped}([\"'])",
            rf"\1#{namespaced}\2",
            result,
        )
        result = re.sub(rf"(?<![\w-])#{escaped}(?![\w-])", f"#{namespaced}", result)
        result = re.sub(rf"(?<![\w-]){escaped}\.(?=[a-zA-Z])", f"{namespaced}.", result)
    return result, mapping


def rewrite_selector(selector: str, mapping: dict[str, str]) -> str:
    result = selector
    for original, namespaced in sorted(mapping.items(), key=lambda item: len(item[0]), reverse=True):
        result = re.sub(rf"(?<![\w-])#{re.escape(original)}(?![\w-])", f"#{namespaced}", result)
    return result


def gif_payload(path: Path) -> dict[str, Any]:
    frames: list[str] = []
    durations: list[int] = []
    with Image.open(path) as source:
        fallback_duration = int(source.info.get("duration", 100) or 100)
        for frame in ImageSequence.Iterator(source):
            duration = max(10, int(frame.info.get("duration", fallback_duration) or fallback_duration))
            image = frame.convert("RGBA")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            frames.append("data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii"))
            durations.append(duration)
        width, height = source.size
    if not frames:
        raise ValueError(f"GIF contains no frames: {path}")
    return {
        "type": "gif-frames",
        "frames": frames,
        "durationsMs": durations,
        "totalMs": sum(durations),
        "width": width,
        "height": height,
    }


def relative_url(asset_path: Path, output: Path) -> str:
    return Path(os.path.relpath(asset_path, output.parent)).as_posix()


def build_payloads(scene: dict[str, Any], project_root: Path, output: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    payloads: dict[str, Any] = {}
    assets: list[dict[str, Any]] = []
    for element in scene["elements"]:
        asset_path = (project_root / element["src"]).resolve()
        digest = sha256_file(asset_path)
        element["sha256"] = digest
        url = relative_url(asset_path, output)
        kind = element["kind"]
        payload: dict[str, Any] = {"type": kind, "url": url, "sha256": digest}
        if kind == "svg":
            raw_svg = asset_path.read_text(encoding="utf-8")
            namespaced_svg, mapping = namespace_svg(raw_svg, element["id"])
            payload.update({"type": "svg", "content": namespaced_svg, "idNamespace": mapping})
            for port in element.get("ports", []):
                if isinstance(port.get("selector"), str):
                    port["runtimeSelector"] = rewrite_selector(port["selector"], mapping)
        elif kind == "html":
            # Inline local HTML so the parent compositor and the child renderer
            # share an origin under file:// deterministic capture. Keep the URL
            # as the base for any relative assets referenced by the child page.
            payload["content"] = asset_path.read_text(encoding="utf-8")
        elif kind == "gif" and element.get("playback", {}).get("mode") == "decoded":
            payload.update(gif_payload(asset_path))
            payload["url"] = url
            payload["sha256"] = digest
        elif kind == "gif":
            payload["type"] = "raster"
        payloads[element["id"]] = payload
        assets.append(
            {
                "elementId": element["id"],
                "assetId": element["assetId"],
                "producerSkill": element["producerSkill"],
                "kind": kind,
                "path": element["src"],
                "sha256": digest,
                "payloadType": payload["type"],
            }
        )
    return payloads, assets


def build(args: argparse.Namespace) -> dict[str, Any]:
    if args.output.exists() and not args.force:
        raise FileExistsError(f"output exists; pass --force to overwrite: {args.output}")
    project_root = args.project_root.resolve()
    scene = json.loads(args.contract.read_text(encoding="utf-8"))
    validation = validate_scene_contract.validate_contract(
        scene,
        project_root,
        require_files=True,
        require_hashes=not args.allow_missing_hashes,
        require_producer_reports=args.require_producer_reports,
    )
    if not validation.get("ok"):
        raise ValueError("scene contract failed validation: " + "; ".join(validation.get("failures", [])))
    scene = copy.deepcopy(scene)
    payloads, assets = build_payloads(scene, project_root, args.output.resolve())
    template = TEMPLATE.read_text(encoding="utf-8")
    html = template.replace("__VIDEO_SCENE_JSON__", safe_json(scene)).replace(
        "__VIDEO_PAYLOAD_JSON__", safe_json(payloads)
    )
    if "__VIDEO_SCENE_JSON__" in html or "__VIDEO_PAYLOAD_JSON__" in html:
        raise RuntimeError("renderer template placeholders were not fully replaced")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html, encoding="utf-8", newline="\n")
    report = {
        "schemaVersion": 1,
        "ok": True,
        "passed": True,
        "sceneId": scene["id"],
        "contract": str(args.contract),
        "output": str(args.output),
        "outputSha256": sha256_file(args.output),
        "canvas": scene["canvas"],
        "assets": assets,
        "interactionCount": len(scene.get("interactions", [])),
        "trackCount": len(scene.get("tracks", [])),
        "warnings": validation.get("warnings", []),
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def main() -> int:
    args = parse_args()
    try:
        report = build(args)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        report = {"schemaVersion": 1, "ok": False, "passed": False, "failures": [str(exc)]}
    if args.json:
        print(json.dumps(report, indent=2))
    elif report.get("ok"):
        print(f"PASS video composite scene: {report['output']}")
    else:
        for failure in report.get("failures", []):
            print(f"FAIL: {failure}", file=sys.stderr)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

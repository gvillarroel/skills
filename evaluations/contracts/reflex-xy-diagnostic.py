#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check the XY diagnostic's outputs, failure reporting, and bundle boundary.

Run with a Python environment containing xy==0.0.8:
  uv run --script evaluations/contracts/reflex-xy-diagnostic.py \
    --python PATH/TO/python --workspace projects/reflex-xy/artifacts/diagnostic-review

All diagnostic invocations use a copied skill. The missing-package case uses
Python -I -S to remove the installed package search surface in a fresh process.
This is deterministic evaluator evidence, not an agent forward test.
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(directory: Path) -> dict[str, str]:
    return {path.relative_to(directory).as_posix(): digest(path) for path in sorted(directory.rglob("*")) if path.is_file()}


def execute(command: list[str], workspace: Path) -> dict:
    process = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
    return {"command": command, "returncode": process.returncode, "stdout": process.stdout, "stderr": process.stderr}


def check_png(path: Path) -> dict:
    """Validate every PNG chunk CRC and the actual compressed scanline payload."""
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "Missing PNG signature"
    cursor, chunks, compressed = 8, [], bytearray()
    header = None
    while cursor < len(data):
        length = struct.unpack_from(">I", data, cursor)[0]
        kind = data[cursor + 4:cursor + 8]
        body = data[cursor + 8:cursor + 8 + length]
        assert len(body) == length, "Truncated PNG chunk"
        crc = struct.unpack_from(">I", data, cursor + 8 + length)[0]
        assert binascii.crc32(kind + body) & 0xFFFFFFFF == crc, "Invalid PNG chunk CRC"
        chunks.append(kind.decode("ascii"))
        if kind == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            compressed.extend(body)
        cursor += 12 + length
        if kind == b"IEND":
            break
    assert cursor == len(data) and chunks[-1] == "IEND", "Incomplete PNG stream"
    assert header is not None, "Missing PNG dimensions"
    width, height, depth, color, compression, filtering, interlace = header
    assert (width, height) == (640, 360), "Unexpected PNG dimensions"
    assert depth == 8 and color in {2, 6} and compression == filtering == interlace == 0, "Unexpected PNG encoding"
    pixels = zlib.decompress(compressed)
    channels = {2: 3, 6: 4}[color]
    stride = 1 + width * channels
    assert len(pixels) == height * stride, "PNG scanline payload size mismatch"
    assert all(pixels[row * stride] <= 4 for row in range(height)), "Invalid PNG row filter"
    assert len(set(pixels)) > 32, "PNG pixel stream is nearly constant"
    return {"dimensions": [width, height], "chunk_types": chunks, "decoded_scanline_bytes": len(pixels), "scanline_byte_values": len(set(pixels))}


def inspect_success(report_path: Path, output_dir: Path) -> dict:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report.get("schema_version") == 1 and report.get("passed") is True
    assert report.get("backend") == "native" and report.get("xy_version") == "0.0.8"
    assert report.get("png_dimensions") == [640, 360]
    assert report.get("memory", {}).get("backend") == "native"
    assert set(report["files"]) == {"chart.html", "chart.svg", "chart.png"}
    for name, recorded in report["files"].items():
        path = output_dir / name
        assert Path(recorded["path"]).resolve() == path.resolve()
        assert path.stat().st_size == recorded["bytes"] > 0
        assert digest(path) == recorded["sha256"], f"Hash mismatch for {name}"
    svg = ET.parse(output_dir / "chart.svg").getroot()
    assert svg.tag.rsplit("}", 1)[-1] == "svg"
    text = " ".join(svg.itertext())
    assert all(label in text for label in ("XY environment probe", "Sample", "Value"))
    shapes = sum(node.tag.rsplit("}", 1)[-1] in {"path", "rect", "circle", "line", "polyline"} for node in svg.iter())
    assert shapes >= 8, "SVG lacks chart geometry"
    html = (output_dir / "chart.html").read_text(encoding="utf-8")
    assert "<script" in html and "XY environment probe" in html
    return {"report": report, "png": check_png(output_dir / "chart.png"), "svg_shapes": shapes}


def run(skill: Path, workspace: Path, python: Path) -> dict:
    workspace.mkdir(parents=True, exist_ok=False)
    bundle = workspace / "source" / skill.name
    shutil.copytree(skill, bundle, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules"))
    frozen = snapshot(bundle)
    script = bundle / "scripts/diagnose.py"
    cases = {}

    for name, directory, report in (
        ("reject_output_inside_bundle", bundle / "assets/rejected", workspace / "rejected-output-report.json"),
        ("reject_report_inside_bundle", workspace / "external-output", bundle / "references/rejected.json"),
        ("reject_report_chart_collision", workspace / "collision", workspace / "collision/chart.png"),
    ):
        result = execute([str(python), "-I", "-B", str(script), "--output-dir", str(directory), "--report", str(report)], workspace)
        assert result["returncode"] == 2 and "error:" in result["stderr"], f"Path rejection failed: {name}: {result}"
        assert not report.exists() and not directory.exists(), f"Rejected path wrote output: {name}"
        cases[name] = result

    output_dir, report_path = workspace / "native-output", workspace / "native.json"
    success = execute([str(python), "-I", "-B", str(script), "--output-dir", str(output_dir), "--report", str(report_path)], workspace)
    assert success["returncode"] == 0, f"Native diagnostic failed: {success}"
    cases["native_success"] = {"execution": success, "independent_inspection": inspect_success(report_path, output_dir)}

    missing_output, missing_report = workspace / "missing-output", workspace / "missing.json"
    missing = execute([str(python), "-I", "-S", "-B", str(script), "--output-dir", str(missing_output), "--report", str(missing_report)], workspace)
    assert missing["returncode"] == 1, f"Missing-package case returned unexpected status: {missing}"
    failure = json.loads(missing_report.read_text(encoding="utf-8"))
    assert failure.get("passed") is False and failure.get("schema_version") == 1
    assert failure.get("error", {}).get("type") == "ModuleNotFoundError" and "xy" in failure["error"]["message"]
    assert not missing_output.exists() and "files" not in failure
    cases["missing_dependency"] = {"execution": missing, "report": failure, "isolation": "Fresh Python -I -S process; site packages and ambient Python paths disabled."}
    assert snapshot(bundle) == frozen, "The copied skill payload changed"
    return {"passed": True, "skill": skill.name, "cases": cases, "copied_payload_unchanged": True, "copied_payload_sha256": hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path("skills/reflex-xy"))
    parser.add_argument("--workspace", type=Path, required=True, help="A new output directory that does not already exist.")
    parser.add_argument("--python", type=Path, default=Path(sys.executable), help="Python environment with the pinned XY installed.")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    if workspace.exists():
        parser.error("Use a new workspace so previous evidence cannot be overwritten.")
    if workspace.is_relative_to(args.skill_dir.resolve()):
        parser.error("The evaluator workspace must be outside the skill bundle.")
    try:
        report = run(args.skill_dir.resolve(), workspace, args.python.resolve())
    except Exception as error:
        report = {"passed": False, "error": {"type": type(error).__name__, "message": str(error)}}
    workspace.mkdir(parents=True, exist_ok=True)
    destination = workspace / "diagnostic-check.json"
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "report": str(destination), "cases": list(report.get("cases", {}))}, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///
"""Regression tests for mixed-media scene validation and compositor builds."""

from __future__ import annotations

import argparse
import copy
import hashlib
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import build_composite_scene  # noqa: E402
import validate_scene_contract  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test video scene contracts.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_svg(path: Path, label: str, color: str) -> None:
    path.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" style="max-width:320px" viewBox="0 0 320 180">
  <defs><clipPath id="clip"><rect width="320" height="180"/></clipPath></defs>
  <g id="node" clip-path="url(#clip)">
    <rect x="20" y="30" width="280" height="120" fill="{color}"/>
    <text x="160" y="98" text-anchor="middle" font-size="24" fill="#ffffff">{label}</text>
  </g>
</svg>\n''',
        encoding="utf-8",
        newline="\n",
    )


def write_gif(path: Path, color_a: str, color_b: str) -> None:
    frames: list[Image.Image] = []
    for index, color in enumerate((color_a, color_b, color_a)):
        image = Image.new("RGBA", (160, 100), color)
        draw = ImageDraw.Draw(image)
        draw.rectangle((12 + index * 22, 35, 52 + index * 22, 75), fill="#ffffff")
        frames.append(image)
    buffer = BytesIO()
    frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:], duration=[100, 140, 180], loop=0)
    path.write_bytes(buffer.getvalue())


def write_html(path: Path) -> None:
    path.write_text(
        '''<!doctype html>
<html>
<head><meta charset="utf-8"><style>html,body{margin:0;background:transparent}#clock{color:#b20d30}</style></head>
<body><output id="clock">0.00</output><script>
window.setVideoState = async (state) => { document.body.dataset.state = state || ""; };
window.renderVideoFrame = async (seconds) => { document.querySelector("#clock").textContent = seconds.toFixed(2); };
</script></body>
</html>
''',
        encoding="utf-8",
        newline="\n",
    )


def producer_report(path: Path) -> None:
    path.write_text(json.dumps({"schemaVersion": 1, "ok": True}, indent=2) + "\n", encoding="utf-8")


def element(
    element_id: str,
    asset_id: str,
    producer: str,
    kind: str,
    src: str,
    digest: str,
    report: str,
    bounds: dict[str, float],
    ports: list[dict[str, object]],
    *,
    states: list[str] | None = None,
    playback: dict[str, object] | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {
        "id": element_id,
        "assetId": asset_id,
        "producerSkill": producer,
        "kind": kind,
        "src": src,
        "sha256": digest,
        "validationReport": report,
        "intrinsic": {"viewBox": "0 0 320 180"} if kind == "svg" else {"width": 160, "height": 100},
        "background": "transparent",
        "bounds": bounds,
        "zIndex": 10,
        "fit": "contain",
        "overflow": "hidden",
        "clock": "master" if kind in {"gif", "html"} else "static",
        "ports": ports,
        "states": states or [],
    }
    if playback is not None:
        result["playback"] = playback
    return result


def run_tests() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="video-scene-contract-") as temporary:
        root = Path(temporary)
        assets = root / "artifacts" / "assets"
        reports = root / "artifacts" / "reviews"
        assets.mkdir(parents=True)
        reports.mkdir(parents=True)
        plantuml = assets / "architecture.svg"
        mermaid = assets / "state.svg"
        gif_a = assets / "result.gif"
        gif_b = assets / "alert.gif"
        html_overlay = assets / "clock-overlay.html"
        write_svg(plantuml, "PlantUML", "#343434")
        write_svg(mermaid, "Mermaid", "#b20d30")
        write_gif(gif_a, "#1d3557", "#457b9d")
        write_gif(gif_b, "#6a4c93", "#ff595e")
        write_html(html_overlay)
        report_paths = {}
        for name in ("plantuml", "mermaid", "gif-a", "gif-b", "html-overlay"):
            report_path = reports / f"{name}.json"
            producer_report(report_path)
            report_paths[name] = report_path.relative_to(root).as_posix()

        contract = {
            "schemaVersion": 1,
            "id": "mixed-tool-scene",
            "canvas": {
                "width": 960,
                "height": 540,
                "aspectRatio": "16:9",
                "fps": 12,
                "durationSeconds": 7,
                "background": "#f4f4f4",
                "safeArea": {"top": 24, "right": 32, "bottom": 24, "left": 32},
            },
            "masterClock": {"mode": "deterministic", "loop": False},
            "elements": [
                element(
                    "plantuml-diagram",
                    "architecture-svg",
                    "plantuml-colorset-renderer",
                    "svg",
                    plantuml.relative_to(root).as_posix(),
                    sha(plantuml),
                    report_paths["plantuml"],
                    {"x": 0.04, "y": 0.08, "width": 0.40, "height": 0.40},
                    [{"id": "service-out", "selector": "#node", "anchor": "right"}],
                ),
                element(
                    "mermaid-diagram",
                    "state-svg",
                    "mermaid",
                    "svg",
                    mermaid.relative_to(root).as_posix(),
                    sha(mermaid),
                    report_paths["mermaid"],
                    {"x": 0.56, "y": 0.08, "width": 0.40, "height": 0.40},
                    [{"id": "queue-in", "selector": "#node", "anchor": "left"}, {"id": "result-out", "x": 0.5, "y": 1.0}],
                    states=["idle", "processing"],
                ),
                element(
                    "result-gif",
                    "result-gif-asset",
                    "animated-svg-to-gif",
                    "gif",
                    gif_a.relative_to(root).as_posix(),
                    sha(gif_a),
                    report_paths["gif-a"],
                    {"x": 0.18, "y": 0.60, "width": 0.26, "height": 0.28},
                    [{"id": "result-center", "x": 0.5, "y": 0.5}],
                    playback={"mode": "decoded", "loop": True, "offsetSeconds": 0},
                ),
                element(
                    "alert-gif",
                    "alert-gif-asset",
                    "animated-svg-to-gif",
                    "gif",
                    gif_b.relative_to(root).as_posix(),
                    sha(gif_b),
                    report_paths["gif-b"],
                    {"x": 0.56, "y": 0.60, "width": 0.26, "height": 0.28},
                    [{"id": "alert-center", "x": 0.5, "y": 0.5}],
                    playback={"mode": "decoded", "loop": True, "offsetSeconds": 0.08},
                ),
                element(
                    "clock-overlay",
                    "clock-overlay-asset",
                    "d3",
                    "html",
                    html_overlay.relative_to(root).as_posix(),
                    sha(html_overlay),
                    report_paths["html-overlay"],
                    {"x": 0.02, "y": 0.02, "width": 0.20, "height": 0.08},
                    [{"id": "clock-center", "x": 0.5, "y": 0.5}],
                ),
            ],
            "events": [
                {"id": "job-arrived", "at": 2.0},
                {"id": "result-ready", "at": 4.2},
                {"id": "alert-ready", "at": 6.2},
            ],
            "tracks": [
                {"id": "mermaid-state", "elementId": "mermaid-diagram", "property": "state", "keyframes": [{"at": 0, "value": "idle"}, {"at": 2, "value": "processing"}]},
                {"id": "result-reveal", "elementId": "result-gif", "property": "opacity", "keyframes": [{"at": 0, "value": 0}, {"at": 3.2, "value": 0}, {"at": 4.2, "value": 1, "easing": "ease-out"}]},
                {"id": "alert-reveal", "elementId": "alert-gif", "property": "opacity", "keyframes": [{"at": 0, "value": 0}, {"at": 5.2, "value": 0}, {"at": 6.2, "value": 1, "easing": "ease-out"}]},
            ],
            "interactions": [
                {
                    "id": "service-to-queue",
                    "type": "message-transfer",
                    "channel": "signal",
                    "source": {"element": "plantuml-diagram", "port": "service-out"},
                    "target": {"element": "mermaid-diagram", "port": "queue-in"},
                    "start": 1.0,
                    "end": 2.0,
                    "emits": ["job-arrived"],
                    "consumes": [],
                    "meaning": "The architecture service delivers one job into the state machine.",
                    "connector": {"path": "curve", "color": "#b20d30", "width": 4, "zIndex": 30, "persistAfter": False},
                    "validationChecks": ["Signal starts at service-out and lands at queue-in before processing state."],
                },
                {
                    "id": "queue-to-result",
                    "type": "state-result",
                    "channel": "handoff",
                    "source": {"element": "mermaid-diagram", "port": "result-out"},
                    "target": {"element": "result-gif", "port": "result-center"},
                    "start": 3.2,
                    "end": 4.2,
                    "emits": ["result-ready"],
                    "consumes": ["job-arrived"],
                    "meaning": "The processing state resolves into the first animated result.",
                    "connector": {"path": "curve", "color": "#1d3557", "width": 4, "zIndex": 31, "persistAfter": False},
                    "validationChecks": ["Result GIF becomes visible when the handoff reaches its center port."],
                },
                {
                    "id": "result-to-alert",
                    "type": "result-escalation",
                    "channel": "signal",
                    "source": {"element": "result-gif", "port": "result-center"},
                    "target": {"element": "alert-gif", "port": "alert-center"},
                    "start": 5.2,
                    "end": 6.2,
                    "emits": ["alert-ready"],
                    "consumes": ["result-ready"],
                    "meaning": "The first animated result escalates into the alert animation.",
                    "connector": {"path": "straight", "color": "#6a4c93", "width": 4, "zIndex": 32, "persistAfter": False},
                    "validationChecks": ["Alert GIF appears after the result-to-alert signal completes."],
                },
            ],
        }

        positive = validate_scene_contract.validate_contract(
            contract,
            root,
            require_files=True,
            require_hashes=True,
            require_producer_reports=True,
        )
        output = root / "src" / "index.html"
        report_path = reports / "compositor-build.json"
        build_args = argparse.Namespace(
            contract=root / "source" / "scene-contract.json",
            output=output,
            project_root=root,
            allow_missing_hashes=False,
            require_producer_reports=True,
            report=report_path,
            force=True,
            json=True,
        )
        build_args.contract.parent.mkdir(parents=True)
        build_args.contract.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
        build_report = build_composite_scene.build(build_args) if positive.get("ok") else {"ok": False}
        html = output.read_text(encoding="utf-8") if output.is_file() else ""
        renderer_report_path = reports / "renderer-contract.json"
        renderer_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "check_renderer_contract.py"),
                str(output),
                "--video-id",
                "mixed-tool-scene",
                "--duration",
                "7",
                "--width",
                "960",
                "--height",
                "540",
                "--output",
                str(renderer_report_path),
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        renderer_report = (
            json.loads(renderer_report_path.read_text(encoding="utf-8"))
            if renderer_report_path.is_file()
            else {"ok": False, "stderr": renderer_run.stderr}
        )
        video_path = root / "artifacts" / "videos" / "mixed-tool-scene.mp4"
        contact_sheet = reports / "contact-sheet.jpg"
        quality_report = reports / "quality-report.json"
        motion_report = reports / "motion-report.json"
        capture_manifest = reports / "capture-manifest.json"
        render_state_report = reports / "render-state.json"
        render_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "render_concept_video.py"),
                str(output),
                str(video_path),
                "--video-id",
                "mixed-tool-scene",
                "--duration",
                "7",
                "--fps",
                "12",
                "--capture-fps",
                "2",
                "--width",
                "960",
                "--height",
                "540",
                "--audio",
                "none",
                "--contact-sheet",
                str(contact_sheet),
                "--quality-report",
                str(quality_report),
                "--motion-report",
                str(motion_report),
                "--capture-manifest",
                str(capture_manifest),
                "--render-state-report",
                str(render_state_report),
                "--force",
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        video_validation_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "check_video_artifact.py"),
                str(video_path),
                "--expect-width",
                "960",
                "--expect-height",
                "540",
                "--expect-fps",
                "12",
                "--expect-duration",
                "7",
                "--duration-tolerance",
                "0.1",
                "--min-size-bytes",
                "10000",
                "--contact-sheet",
                str(contact_sheet),
                "--quality-report",
                str(quality_report),
                "--motion-report",
                str(motion_report),
                "--capture-manifest",
                str(capture_manifest),
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        ) if render_run.returncode == 0 else subprocess.CompletedProcess([], 1, "", render_run.stderr)

        bad_port = copy.deepcopy(contract)
        bad_port["interactions"][0]["target"]["port"] = "missing-port"
        bad_port_report = validate_scene_contract.validate_contract(bad_port, root)
        bad_ratio = copy.deepcopy(contract)
        bad_ratio["canvas"]["aspectRatio"] = "4:3"
        bad_ratio_report = validate_scene_contract.validate_contract(bad_ratio, root)
        bad_gif_clock = copy.deepcopy(contract)
        bad_gif_clock["elements"][2]["clock"] = "autonomous"
        bad_gif_clock_report = validate_scene_contract.validate_contract(bad_gif_clock, root)

        tests = {
            "positiveContract": positive.get("ok") is True,
            "crossProducerInteractions": positive.get("summary", {}).get("crossProducerInteractionCount") == 2,
            "build": build_report.get("ok") is True and output.is_file() and report_path.is_file(),
            "browserRenderer": renderer_run.returncode == 0 and renderer_report.get("ok") is True,
            "mp4Render": render_run.returncode == 0 and video_path.is_file(),
            "mp4Validation": video_validation_run.returncode == 0,
            "svgIdNamespacing": "plantuml-diagram__node" in html and "mermaid-diagram__node" in html,
            "svgMaxWidthReset": 'visual.style.maxWidth = "none"' in html,
            "gifMasterClockPayload": html.count('"type":"gif-frames"') == 2,
            "htmlMasterClockPayload": '"type":"html"' in html and '"content":' in html and "visual.srcdoc" in html,
            "unknownPortRejected": bad_port_report.get("ok") is False and any("missing-port" in item for item in bad_port_report.get("failures", [])),
            "wrongRatioRejected": bad_ratio_report.get("ok") is False and any("reduced ratio" in item for item in bad_ratio_report.get("failures", [])),
            "autonomousDecodedGifRejected": bad_gif_clock_report.get("ok") is False and any("decoded GIF must use clock=master" in item for item in bad_gif_clock_report.get("failures", [])),
        }
        return {
            "schemaVersion": 1,
            "ok": all(tests.values()),
            "passed": all(tests.values()),
            "tests": tests,
            "positiveSummary": positive.get("summary"),
            "diagnostics": {
                "renderer": {"stdout": renderer_run.stdout, "stderr": renderer_run.stderr},
                "render": {"stdout": render_run.stdout, "stderr": render_run.stderr},
                "videoValidation": {
                    "stdout": video_validation_run.stdout,
                    "stderr": video_validation_run.stderr,
                },
            }
            if not all(tests.values())
            else {},
        }


def main() -> int:
    args = parse_args()
    report = run_tests()
    if args.json:
        print(json.dumps(report, indent=2))
    elif report["ok"]:
        print(f"PASS video scene contract tests: {sum(report['tests'].values())}/{len(report['tests'])}")
    else:
        for name, passed in report["tests"].items():
            if not passed:
                print(f"FAIL: {name}", file=sys.stderr)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

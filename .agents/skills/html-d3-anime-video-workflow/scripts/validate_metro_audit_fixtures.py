#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=10.0.0", "playwright>=1.45.0"]
# ///

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import audit_metro_semantic_density as semantic_density
from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Metro audit positive and negative fixtures for zero-padding, grayscale hierarchy, and text dependence."
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    parser.add_argument("--workdir", type=Path, help="Optional directory to keep generated fixtures and reports.")
    parser.add_argument("--install-browser", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    return parser.parse_args()


def source_package(output_id: str = "fixture") -> dict[str, Any]:
    return {
        "outputId": output_id,
        "visualPattern": "fixture",
        "sourceFacts": ["Fixture proves zero-padding geometry and grayscale hierarchy."],
        "strategyAnchors": ["zero internal padding", "grayscale hierarchy levels"],
        "title": "Metro Fixture Title",
        "checkedDate": "2026-07-04",
        "durationSeconds": 2.0,
        "format": {"width": 320, "height": 240, "fps": 6},
    }


def rendered_fixture_html(
    *,
    padded: bool = False,
    weak_gray: bool = False,
    untagged_inset: bool = False,
    transform_offgrid: bool = False,
    css_rounded: bool = False,
    no_stroke_parent_inset: bool = False,
    small_inset: bool = False,
    tiny_gray_swatches: bool = False,
    title_band: bool = False,
    text_heavy: bool = False,
    text_dense: bool = False,
    dominant_text_box: bool = False,
    ellipsized_text: bool = False,
    text_only_motion: bool = False,
    red_dominant: bool = False,
) -> str:
    gray_levels = ["#ffffff", "#f7f7f7", "#cfcfcf", "#696969"] if not weak_gray else ["#ffffff", "#f7f7f7"]
    fill_x = 12 if padded else 0
    fill_y = 12 if padded else 0
    fill_h = 104 if padded else 128
    third_panel_gray = 0 if weak_gray or tiny_gray_swatches else 2
    fourth_panel_gray = 1 if weak_gray or tiny_gray_swatches else 3
    css_rules = ["html, body { font-family: 'Open Sans', Arial, sans-serif; }"]
    if css_rounded:
        css_rules.append("#stage rect { rx: 8px; ry: 8px; }")
    css = f"<style>{' '.join(css_rules)}</style>"
    return f"""<!doctype html>
<html>
<body>
{css}
<svg id="stage" width="320" height="240" viewBox="0 0 320 240" data-edge-style="square" data-box-interior-policy="zero" data-internal-padding-px="0" data-gray-levels="{','.join(gray_levels)}"></svg>
<script>
const NS = "http://www.w3.org/2000/svg";
const stage = document.getElementById("stage");
const PACKAGE = {{ visualPattern: "fixture" }};
const grayLevels = {json.dumps(gray_levels)};
let drawTarget = stage;
function grayLevel(index) {{ return grayLevels[Math.max(0, Math.min(grayLevels.length - 1, index))]; }}
function snapToGrid(value) {{ return Math.round(Number(value) / 4) * 4; }}
function normalizeSvgAttrs(name, attrs) {{
  if (name === "rect") {{
    for (const key of ["x", "y", "width", "height"]) {{
      if (attrs[key] !== undefined) attrs[key] = snapToGrid(attrs[key]);
    }}
    attrs.rx = 0;
    attrs.ry = 0;
  }}
  return attrs;
}}
function el(name, attrs) {{
  attrs = normalizeSvgAttrs(name, attrs);
  const node = document.createElementNS(NS, name);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  drawTarget.appendChild(node);
  return node;
}}
function textEl(text, attrs) {{
  const node = el("text", attrs);
  node.textContent = text;
  return node;
}}
window.renderConceptFrame = function renderConceptFrame(videoId, seconds) {{
  stage.replaceChildren();
  drawTarget = stage;
  if ({str(transform_offgrid).lower()}) {{
    const group = document.createElementNS(NS, "g");
    group.setAttribute("transform", "translate(2 0)");
    stage.appendChild(group);
    drawTarget = group;
  }}
  if (PACKAGE.visualPattern === "fixture") {{
    const dynamicWidth = Math.max(32, Math.min(112, 32 + Math.round(seconds * 40 / 4) * 4));
    if ({str(untagged_inset).lower()}) {{
      el("rect", {{ x: 0, y: 0, width: 160, height: 128, rx: 0, fill: grayLevel(0), stroke: "#cfcfcf" }});
      el("rect", {{ x: 16, y: 16, width: 128, height: 96, rx: 0, fill: grayLevel(2), stroke: "#cfcfcf" }});
      el("rect", {{ x: 160, y: 0, width: 96, height: 128, rx: 0, fill: grayLevel(1), stroke: "#cfcfcf" }});
      el("rect", {{ x: 0, y: 128, width: 256, height: 112, rx: 0, fill: grayLevel(3), stroke: "#cfcfcf" }});
      return {{ videoId, seconds, visualPattern: "fixture", visibleMechanismCount: 4 }};
    }}
    if ({str(no_stroke_parent_inset).lower()}) {{
      el("rect", {{ x: 0, y: 0, width: 160, height: 128, rx: 0, fill: grayLevel(0) }});
      el("rect", {{ x: 16, y: 16, width: 128, height: 96, rx: 0, fill: grayLevel(2) }});
      el("rect", {{ x: 160, y: 0, width: 96, height: 128, rx: 0, fill: grayLevel(1), stroke: "#cfcfcf" }});
      el("rect", {{ x: 0, y: 128, width: 256, height: 112, rx: 0, fill: grayLevel(3), stroke: "#cfcfcf" }});
      return {{ videoId, seconds, visualPattern: "fixture", visibleMechanismCount: 4 }};
    }}
    if ({str(small_inset).lower()}) {{
      el("rect", {{ x: 0, y: 0, width: 96, height: 48, rx: 0, fill: grayLevel(0), stroke: "#cfcfcf" }});
      el("rect", {{ x: 8, y: 8, width: 80, height: 32, rx: 0, fill: grayLevel(2), stroke: "#cfcfcf" }});
      el("rect", {{ x: 96, y: 0, width: 96, height: 48, rx: 0, fill: grayLevel(1), stroke: "#cfcfcf" }});
      el("rect", {{ x: 0, y: 48, width: 192, height: 192, rx: 0, fill: grayLevel(3), stroke: "#cfcfcf" }});
      return {{ videoId, seconds, visualPattern: "fixture", visibleMechanismCount: 4 }};
    }}
    el("rect", {{ x: 0, y: 0, width: 128, height: 128, rx: 0, fill: grayLevel(0), stroke: "#cfcfcf", "data-box-id": "box-a", "data-zone-id": "zone-a", "data-zone-role": "mechanism" }});
    el("rect", {{ x: 128, y: 0, width: 128, height: 128, rx: 0, fill: grayLevel(1), stroke: "#cfcfcf", "data-zone-id": "zone-b", "data-zone-role": "metric" }});
    el("rect", {{ x: 0, y: 128, width: 128, height: 112, rx: 0, fill: grayLevel({third_panel_gray}), stroke: "#cfcfcf", "data-zone-id": "zone-c", "data-zone-role": "state" }});
    el("rect", {{ x: 128, y: 128, width: 128, height: 112, rx: 0, fill: grayLevel({fourth_panel_gray}), stroke: "#cfcfcf", "data-zone-id": "zone-d", "data-zone-role": "evidence" }});
    if ({str(red_dominant).lower()}) {{
      el("rect", {{ x: 0, y: 0, width: 256, height: 128, rx: 0, fill: "#9e1b32", stroke: "#6d1222", "data-zone-id": "zone-red", "data-zone-role": "bad-red-surface" }});
    }}
    el("rect", {{ x: {fill_x}, y: {fill_y}, width: {64 if text_only_motion else "dynamicWidth"}, height: {fill_h}, rx: 0, fill: "#9e1b32", "data-fill-for": "box-a", "data-fill-axis": "x-progress", "data-zone-id": "zone-e", "data-zone-role": "active-route" }});
    for (let x = 0; x <= 240; x += 16) {{
      el("line", {{ x1: x, y1: 0, x2: x, y2: 240, stroke: "#b5b5b5", "stroke-width": 1, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
    }}
    for (let y = 0; y <= 224; y += 16) {{
      el("line", {{ x1: 0, y1: y, x2: 256, y2: y, stroke: "#9c9c9c", "stroke-width": 1, "stroke-linecap": "butt", "stroke-linejoin": "miter" }});
    }}
    if ({str(title_band).lower()}) {{
      textEl("Metro Fixture Title", {{ x: 8, y: 42, "font-size": 32, "font-family": "Arial", fill: "#333e48" }});
    }}
    if ({str(text_heavy).lower()}) {{
      for (let i = 0; i < 8; i += 1) {{
        textEl("explanatory paragraph line " + (i + 1), {{ x: 16, y: 92 + i * 18, "font-size": 20, "font-family": "Arial", fill: "#333e48" }});
      }}
    }}
    if ({str(dominant_text_box).lower()}) {{
      textEl("Dominant label", {{ x: 20, y: 132, "font-size": 34, "font-family": "Arial", fill: "#333e48" }});
    }}
    if ({str(ellipsized_text).lower()}) {{
      textEl("Metric value...", {{ x: 24, y: 176, "font-size": 16, "font-family": "Arial", fill: "#333e48" }});
    }}
    if ({str(text_only_motion).lower()}) {{
      textEl("changing label " + Math.round(seconds * 12), {{ x: 24 + Math.round(seconds * 16), y: 84, "font-size": 28, "font-family": "Arial", fill: "#333e48" }});
    }}
    if ({str(text_dense).lower()}) {{
      for (let i = 0; i < 30; i += 1) {{
        textEl("tag" + i, {{ x: 8 + (i % 5) * 60, y: 72 + Math.floor(i / 5) * 18, "font-size": 9, "font-family": "Arial", fill: "#333e48" }});
      }}
    }}
    if ({str(tiny_gray_swatches).lower()}) {{
      el("rect", {{ x: 260, y: 0, width: 4, height: 4, rx: 0, fill: grayLevel(2), stroke: "#cfcfcf" }});
      el("rect", {{ x: 264, y: 0, width: 4, height: 4, rx: 0, fill: grayLevel(3), stroke: "#cfcfcf" }});
    }}
  }}
  return {{ videoId, seconds, visualPattern: "fixture", visibleMechanismCount: 4 }};
}};
</script>
</body>
</html>
"""


def composition_fixture_html(*, gap: bool = False, padding: bool = False) -> str:
    css = ".grid{display:grid;gap:24px}" if gap else ""
    if padding:
        css += ".bad{padding:12px}"
    return f"""<!doctype html>
<style>{css}</style>
<svg id="stage" data-edge-style="square" data-box-interior-policy="zero" data-internal-padding-px="0" data-gray-levels="#ffffff,#f7f7f7,#e7e7e7,#cfcfcf">
  <rect x="0" y="0" width="128" height="128" rx="0" fill="#ffffff"/>
  <rect x="128" y="0" width="128" height="128" rx="0" fill="#f7f7f7"/>
  <rect x="0" y="128" width="128" height="128" rx="0" fill="#e7e7e7"/>
  <rect x="128" y="128" width="128" height="128" rx="0" fill="#cfcfcf"/>
</svg>
"""


def composition_dynamic_rounding_fixture_html() -> str:
    return """<!doctype html>
<svg id="stage" data-edge-style="square" data-box-interior-policy="zero" data-internal-padding-px="0" data-gray-levels="#ffffff,#f7f7f7,#e7e7e7,#cfcfcf">
</svg>
<script>
const masonryRequired = true;
function el(name, attrs) {}
el("rect", { x: 0, y: 0, width: 128, height: 128, rx: masonryRequired ? 0 : 14, fill: "#ffffff" });
el("rect", { x: 128, y: 0, width: 128, height: 128, rx: 0, fill: "#f7f7f7" });
el("rect", { x: 0, y: 128, width: 128, height: 128, rx: 0, fill: "#e7e7e7" });
el("rect", { x: 128, y: 128, width: 128, height: 128, rx: 0, fill: "#cfcfcf" });
</script>
"""


def masonry_fixture_html(*, weak: bool = False, label_heavy: bool = False) -> str:
    modules = (
        [
            (0, 0, 80, 80, 0, 1),
            (80, 0, 80, 80, 1, 1),
            (160, 0, 80, 80, 2, 1),
        ]
        if weak
        else [
            (0, 0, 96, 96, 0, 1),
            (96, 0, 80, 48, 1, 2),
            (176, 0, 80, 144, 2, 3),
            (96, 48, 80, 96, 1, 4),
            (0, 96, 96, 128, 3, 2),
            (96, 144, 160, 80, 4, 3),
            (256, 0, 64, 112, 2, 4),
            (256, 112, 64, 112, 4, 1),
        ]
    )
    gray = {
        1: "#f7f7f7",
        2: "#e7e7e7",
        3: "#cfcfcf",
        4: "#9c9c9c",
    }
    module_json = json.dumps(
        [
            {"x": x, "y": y, "width": width, "height": height, "zone": zone, "gray": gray_level}
            for x, y, width, height, zone, gray_level in modules
        ]
    )
    gray_json = json.dumps(gray)
    reveal_expression = (
        "modules.length"
        if weak
        else "Math.max(1, Math.min(modules.length, Math.ceil((seconds / 1.75) * modules.length)))"
    )
    label_heavy_js = str(label_heavy).lower()
    weak_js = str(weak).lower()
    return f"""<!doctype html>
<html>
<body>
<svg id="stage" width="320" height="240" viewBox="0 0 320 240" data-edge-style="square" data-box-interior-policy="zero" data-internal-padding-px="0" data-gray-levels="#ffffff,#f7f7f7,#e7e7e7,#cfcfcf,#9c9c9c,#696969">
</svg>
<script>
const NS = "http://www.w3.org/2000/svg";
const stage = document.getElementById("stage");
const modules = {module_json};
const gray = {gray_json};
function draw(seconds) {{
  stage.replaceChildren();
  const reveal = {reveal_expression};
  for (let index = 0; index < reveal; index++) {{
    const module = modules[index];
    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("x", module.x);
    rect.setAttribute("y", module.y);
    rect.setAttribute("width", module.width);
    rect.setAttribute("height", module.height);
    rect.setAttribute("rx", "0");
    rect.setAttribute("fill", gray[module.gray]);
    rect.setAttribute("stroke", "#696969");
    rect.setAttribute("data-masonry-module", "true");
    rect.setAttribute("data-masonry-wall", "true");
    rect.setAttribute("data-masonry-order", String(index));
    rect.setAttribute("data-zone-id", `zone-${{module.zone}}`);
    rect.setAttribute("data-zone-role", "masonry fixture");
    if (!{weak_js} && index === 0) rect.setAttribute("data-box-id", "masonry-fixture-module-0");
    stage.appendChild(rect);
    if (!{weak_js} && index === 0) {{
      const fill = document.createElementNS(NS, "rect");
      fill.setAttribute("x", module.x);
      fill.setAttribute("y", module.y);
      fill.setAttribute("width", module.width);
      fill.setAttribute("height", module.height);
      fill.setAttribute("rx", "0");
      fill.setAttribute("fill", gray[module.gray]);
      fill.setAttribute("data-fill-for", "masonry-fixture-module-0");
      fill.setAttribute("data-fill-axis", "full-module");
      stage.appendChild(fill);
    }}
    if ({label_heavy_js}) {{
      const text = document.createElementNS(NS, "text");
      text.setAttribute("x", module.x + 6);
      text.setAttribute("y", module.y + 18);
      text.setAttribute("font-size", "10");
      text.setAttribute("font-weight", "650");
      text.setAttribute("fill", "#333e48");
      text.textContent = `label-${{index}}`;
      stage.appendChild(text);
    }}
  }}
}}
window.renderConceptFrame = function renderConceptFrame(videoId, seconds) {{
  draw(seconds);
  return {{ videoId, seconds, visualPattern: "masonry-fixture", visibleMechanismCount: 4 }};
}};
draw(0);
</script>
</body>
</html>
"""


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"manifestReadError": str(exc)}
    return data if isinstance(data, dict) else {"manifestReadError": "Manifest root is not an object."}


def encode_fixture_video(frames_dir: Path, output: Path, *, fps: int = 6) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for MP4 composition fixtures.")
    output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            ffmpeg,
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "frame-%03d.png"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            output.as_posix(),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg fixture encoding failed.")


def make_video_composition_fixture(path: Path, *, slide_like: bool, red_dominant: bool = False) -> None:
    frames_dir = path.parent / f"{path.stem}-frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    width, height = 640, 360
    gray = ["#f5f5f5", "#e7e7e7", "#cfcfcf", "#9c9c9c", "#696969"]
    red = "#9e1b32"
    light_red = "#ffccd5"
    for frame in range(36):
        phase = frame / 35
        img = Image.new("RGB", (width, height), "#f5f5f5")
        draw = ImageDraw.Draw(img)
        if red_dominant:
            draw.rectangle((0, 0, width, height), fill="#e7e7e7")
            draw.rectangle((40, 40, 600, 220), fill=red, outline="#6d1222", width=4)
            draw.rectangle((40, 224, 600, 316), fill=light_red, outline=red, width=4)
            draw.line((64, 328, 576, 328), fill="#696969", width=8)
            draw.rectangle((64 + int(phase * 480), 316, 104 + int(phase * 480), 340), fill="#696969")
            img.save(frames_dir / f"frame-{frame:03d}.png")
            continue
        if slide_like:
            draw.rectangle((0, 0, width, 82), fill="#e7e7e7")
            draw.rectangle((132, 116, 508, 154), outline=red, width=3, fill="#ffffff")
            draw.rectangle((180, 184, 460, 208), fill=light_red, outline=red, width=2)
            for index in range(4):
                x = 220 + index * 54 + int(math.sin(phase * math.pi * 2 + index) * 8)
                draw.rectangle((x, 246, x + 36, 268), fill=gray[2 + index % 2], outline="#696969")
            draw.line((160, 304, 480, 304), fill=red, width=4)
            draw.rectangle((232 + int(phase * 96), 296, 258 + int(phase * 96), 312), fill=red)
        else:
            modules = [
                (16, 16, 128, 104, 1),
                (448, 16, 176, 104, 2),
                (16, 224, 176, 104, 3),
                (400, 224, 224, 104, 2),
                (144, 16, 144, 72, 2),
                (288, 16, 160, 144, 3),
                (16, 120, 192, 104, 2),
                (208, 88, 80, 136, 4),
                (288, 160, 160, 64, 1),
                (448, 120, 176, 104, 4),
                (192, 224, 208, 104, 1),
            ]
            reveal = max(4, min(len(modules), 4 + int(phase * (len(modules) - 3))))
            for index, (x, y, w, h, shade) in enumerate(modules[:reveal]):
                draw.rectangle((x, y, x + w, y + h), fill=gray[shade], outline="#696969", width=2)
            route_x = int(48 + phase * 520)
            draw.line((32, 180, 608, 180), fill=red, width=3)
            draw.rectangle((route_x - 12, 168, route_x + 12, 192), fill=red)
            draw.rectangle((400, 40, 608, 50), fill=red)
        img.save(frames_dir / f"frame-{frame:03d}.png")
    encode_fixture_video(frames_dir, path)


def finding_codes(report: dict[str, Any]) -> list[str]:
    findings = report.get("findings") if isinstance(report.get("findings"), list) else []
    return sorted(str(item.get("code")) for item in findings if isinstance(item, dict) and item.get("code"))


def kill_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if sys.platform.startswith("win"):
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            text=True,
            capture_output=True,
            check=False,
        )
        return
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
    except ProcessLookupError:
        return


def run_with_timeout(command: list[str], timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    popen_kwargs: dict[str, Any] = {
        "text": True,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }
    if sys.platform.startswith("win"):
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    process = subprocess.Popen(command, **popen_kwargs)
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        kill_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            stdout = exc.output if isinstance(exc.output, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        raise subprocess.TimeoutExpired(command, timeout_seconds, output=stdout, stderr=stderr) from exc
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def run_case(
    *,
    name: str,
    command: list[str],
    manifest: Path,
    expect_pass: bool,
    expected_codes: list[str] | None,
    timeout_seconds: int,
) -> dict[str, Any]:
    attempts = 0
    timeout_error = ""
    result: subprocess.CompletedProcess[str] | None = None
    for attempt in range(2):
        attempts = attempt + 1
        try:
            result = run_with_timeout(command, timeout_seconds)
            break
        except subprocess.TimeoutExpired as exc:
            timeout_error = str(exc)
            if attempt == 1:
                report = read_json(manifest)
                codes = finding_codes(report)
                expected_codes = expected_codes or []
                manifest_passed = report.get("passed") is True
                if expect_pass:
                    passed = manifest_passed
                else:
                    passed = report.get("passed") is False and all(code in codes for code in expected_codes)
                return {
                    "name": name,
                    "passed": passed,
                    "expectPass": expect_pass,
                    "returnCode": None,
                    "manifest": manifest.as_posix(),
                    "manifestPassed": report.get("passed"),
                    "codes": codes,
                    "expectedCodes": expected_codes,
                    "attempts": attempts,
                    "timeoutExpired": True,
                    "timeoutError": timeout_error,
                }
    if result is None:
        return {
            "name": name,
            "passed": False,
            "expectPass": expect_pass,
            "returnCode": None,
            "manifest": manifest.as_posix(),
            "manifestPassed": None,
            "codes": [],
            "expectedCodes": expected_codes or [],
            "attempts": attempts,
            "timeoutExpired": True,
            "timeoutError": timeout_error or "Command did not produce a result.",
        }
    report = read_json(manifest)
    codes = finding_codes(report)
    manifest_passed = report.get("passed") is True
    expected_codes = expected_codes or []
    if expect_pass:
        passed = result.returncode == 0 and manifest_passed
    else:
        passed = result.returncode != 0 and manifest_passed is False and all(code in codes for code in expected_codes)
    return {
        "name": name,
        "passed": passed,
        "expectPass": expect_pass,
        "returnCode": result.returncode,
        "manifest": manifest.as_posix(),
        "manifestPassed": report.get("passed"),
        "codes": codes,
        "expectedCodes": expected_codes,
        "attempts": attempts,
        "timeoutExpired": False,
        "stdoutTail": result.stdout[-1000:],
        "stderrTail": result.stderr[-1000:],
    }


def semantic_masonry_contract_cases() -> list[dict[str, Any]]:
    args = argparse.Namespace(
        require_metro_pattern_mix=True,
        min_mix_patterns=6,
        min_mix_used_patterns=3,
        min_mix_functional_zones=5,
        min_mix_motion_systems=4,
        min_mix_camera_events=3,
        min_mix_transitions=3,
        min_mix_transition_types=3,
        require_modular_transition=True,
        require_mix_anti_pattern_risk=[],
        min_source_gray_levels=4,
    )

    def zone(index: int, *, pattern: str = "masonry-wall", armature: str = "masonry wall") -> dict[str, Any]:
        return {
            "id": f"zone-{index}",
            "role": "fixture",
            "pattern": pattern,
            "armature": armature,
            "boxModel": {"cornerRadius": 0, "internalPaddingPx": 0, "gridPx": 4},
        }

    base_mix: dict[str, Any] = {
        "passed": True,
        "selected": {
            "helperPattern": "systems-flow",
            "primaryPattern": "dependency-map",
            "secondaryPattern": "attention-matrix-tiles",
            "supportPatterns": ["masonry-wall", "flow-tokens"],
        },
        "patternIdsNamed": [
            "systems-flow",
            "dependency-map",
            "attention-matrix-tiles",
            "masonry-wall",
            "flow-tokens",
            "swimlane-handoff",
        ],
        "patternsUsedInBeats": [{"id": "systems-flow"}, {"id": "masonry-wall"}, {"id": "dependency-map"}],
        "patternDetails": [{"id": "masonry-wall"}],
        "functionalZones": [zone(index) for index in range(5)],
        "semanticMotionSystems": [{"id": f"motion-{index}"} for index in range(4)],
        "cameraPath": [{"id": f"camera-{index}"} for index in range(3)],
        "transitionContracts": [
            {"type": "camera-pan"},
            {"type": "tile-morph"},
            {"type": "masonry-construction"},
        ],
        "antiPatternRisks": [],
        "metroConstraints": {"cornerRadius": 0, "internalBoxPaddingPx": 0, "minimumGrayLevels": 4},
        "textBudget": {"visibleTextRole": "functional-labels-only"},
        "masonryContract": {"required": True, "patternIncluded": True, "transitionIncluded": True},
    }
    wrapper = {"contract": {"pattern": "systems-flow"}}
    source = {"visualPattern": "systems-flow"}

    def run_mix_case(name: str, mix: dict[str, Any], expected_codes: list[str]) -> dict[str, Any]:
        findings, evidence = semantic_density.pattern_mix_findings(mix, wrapper, source, args)
        codes = sorted(str(item.get("code")) for item in findings if isinstance(item, dict) and item.get("code"))
        passed = all(code in codes for code in expected_codes) and (bool(expected_codes) == bool(codes))
        return {
            "name": name,
            "passed": passed,
            "codes": codes,
            "expectedCodes": expected_codes,
            "masonryContract": evidence.get("masonryContract"),
        }

    missing_pattern = copy.deepcopy(base_mix)
    missing_pattern["patternIdsNamed"] = [
        "systems-flow",
        "dependency-map",
        "attention-matrix-tiles",
        "flow-tokens",
        "swimlane-handoff",
        "token-boxes",
    ]
    missing_pattern["selected"]["supportPatterns"] = ["flow-tokens"]
    missing_pattern["patternsUsedInBeats"] = [{"id": "systems-flow"}, {"id": "dependency-map"}, {"id": "flow-tokens"}]
    missing_pattern["patternDetails"] = [{"id": "dependency-map"}]
    for item in missing_pattern["functionalZones"]:
        item["pattern"] = "dependency-map"
        item["armature"] = "route map"

    missing_transition = copy.deepcopy(base_mix)
    missing_transition["transitionContracts"] = [
        {"type": "camera-pan"},
        {"type": "tile-morph"},
        {"type": "masked-reframe"},
    ]

    false_pattern_flag = copy.deepcopy(base_mix)
    false_pattern_flag["masonryContract"]["patternIncluded"] = False

    return [
        run_mix_case("semantic-masonry-contract-good-passes", base_mix, []),
        run_mix_case("semantic-masonry-missing-pattern-fails", missing_pattern, ["missing-required-masonry-pattern"]),
        run_mix_case(
            "semantic-masonry-missing-transition-fails",
            missing_transition,
            ["missing-required-masonry-transition"],
        ),
        run_mix_case("semantic-masonry-false-pattern-flag-fails", false_pattern_flag, ["missing-required-masonry-pattern"]),
    ]


def semantic_source_anchor_binding_cases() -> list[dict[str, Any]]:
    args = argparse.Namespace(
        min_source_visual_mechanisms=3,
        min_source_anchors=4,
        min_source_visual_zones=4,
        min_source_gray_levels=4,
        require_source_anchor_map=True,
        min_source_zone_anchor_coverage_ratio=1.0,
        min_source_binding_anchor_coverage_ratio=1.0,
        min_source_anchored_zone_ratio=1.0,
        min_rendered_source_anchor_coverage_ratio=1.0,
        min_state_source_anchor_coverage_ratio=1.0,
        min_source_anchor_visual_binding_coverage_ratio=1.0,
    )
    anchors = ["bounded queue", "retry branch", "dead-letter path", "feedback limit"]
    zones = [
        {
            "id": f"zone-{index + 1}",
            "role": f"role-{index + 1}",
            "sourceAnchors": [anchor],
            "boxModel": {"cornerRadius": 0, "internalPaddingPx": 0, "gridPx": 4},
        }
        for index, anchor in enumerate(anchors)
    ]
    bindings = [
        {
            "id": f"binding-{index + 1}",
            "sourceAnchor": anchor,
            "zoneId": zones[index]["id"],
            "zoneRole": zones[index]["role"],
            "mechanismId": f"mechanism-{index + 1}",
            "stateKey": ["queueSlots", "retryVisible", "deadLetterVisible", "feedbackVisible"][index],
        }
        for index, anchor in enumerate(anchors)
    ]
    good_source: dict[str, Any] = {
        "visualPattern": "systems-flow",
        "visualMechanisms": ["queue fills", "retry splits", "dead letter isolates", "feedback throttles"],
        "strategyAnchors": anchors,
        "visualZones": zones,
        "semanticBindings": bindings,
        "visualPolicy": {
            "edgeStyle": "square",
            "boxInteriorPolicy": "zero",
            "internalPaddingPx": 0,
            "grayLevels": ["#ffffff", "#e7e7e7", "#cfcfcf", "#696969"],
        },
    }

    def run_source_case(name: str, source: dict[str, Any], expected_codes: list[str]) -> dict[str, Any]:
        findings, evidence = semantic_density.source_package_findings(source, args)
        codes = sorted(str(item.get("code")) for item in findings if isinstance(item, dict) and item.get("code"))
        return {
            "name": name,
            "passed": all(code in codes for code in expected_codes) and (bool(expected_codes) == bool(codes)),
            "codes": codes,
            "expectedCodes": expected_codes,
            "bindingEvidence": evidence.get("sourceAnchorBinding"),
        }

    missing_bindings = copy.deepcopy(good_source)
    for zone in missing_bindings["visualZones"]:
        zone["sourceAnchors"] = []
    missing_bindings["semanticBindings"] = []

    rendered = {"sourceAnchors": anchors, "semanticBindings": [binding["id"] for binding in bindings]}
    state_samples = [{"state": {"activeSourceAnchors": [anchor]}} for anchor in anchors]
    binding_findings, binding_evidence = semantic_density.semantic_binding_findings(
        good_source,
        rendered,
        state_samples,
        args,
    )
    binding_codes = sorted(str(item.get("code")) for item in binding_findings if isinstance(item, dict) and item.get("code"))
    scrambled_state_samples = [{"state": {"activeSourceAnchors": ["bounded queue"]}}]
    scrambled_findings, scrambled_evidence = semantic_density.semantic_binding_findings(
        good_source,
        {"sourceAnchors": ["bounded queue", "retry branch"]},
        scrambled_state_samples,
        args,
    )
    scrambled_codes = sorted(str(item.get("code")) for item in scrambled_findings if isinstance(item, dict) and item.get("code"))

    return [
        run_source_case("semantic-source-anchor-map-good-passes", good_source, []),
        run_source_case(
            "semantic-source-anchor-map-missing-bindings-fails",
            missing_bindings,
            [
                "missing-semantic-bindings",
                "source-binding-anchor-coverage-too-low",
                "source-zone-anchor-coverage-too-low",
                "source-zones-missing-anchor-bindings",
            ],
        ),
        {
            "name": "semantic-binding-coverage-good-passes",
            "passed": not binding_codes and binding_evidence.get("sourceAnchorVisualBindingCoverage") == 1.0,
            "codes": binding_codes,
            "expectedCodes": [],
            "bindingEvidence": binding_evidence,
        },
        {
            "name": "semantic-density-role-scramble-fails",
            "passed": "semantic-binding-coverage-too-low" in scrambled_codes,
            "codes": scrambled_codes,
            "expectedCodes": ["semantic-binding-coverage-too-low"],
            "bindingEvidence": scrambled_evidence,
        },
    ]


def run_validation(workdir: Path, *, install_browser: bool, timeout_seconds: int) -> dict[str, Any]:
    source = workdir / "source-package.json"
    write_json(source, source_package())
    source_masonry = workdir / "source-package-masonry.json"
    masonry_source_package = source_package("masonry-fixture")
    masonry_source_package["masonryLayout"] = {"required": True, "moduleCount": 8, "transitionType": "masonry-construction"}
    write_json(source_masonry, masonry_source_package)
    html_good = workdir / "rendered-good.html"
    html_masonry_good = workdir / "rendered-masonry-good.html"
    html_masonry_bad = workdir / "rendered-masonry-bad.html"
    html_masonry_label_heavy = workdir / "rendered-masonry-label-heavy.html"
    html_bad_padding = workdir / "rendered-bad-padding.html"
    html_bad_untagged_inset = workdir / "rendered-bad-untagged-inset.html"
    html_bad_no_stroke_untagged_inset = workdir / "rendered-bad-no-stroke-untagged-inset.html"
    html_bad_small_inset = workdir / "rendered-bad-small-inset.html"
    html_bad_transform_offgrid = workdir / "rendered-bad-transform-offgrid.html"
    html_bad_css_rounded = workdir / "rendered-bad-css-rounded.html"
    html_bad_tiny_gray_swatches = workdir / "rendered-bad-tiny-gray-swatches.html"
    html_bad_gray = workdir / "rendered-bad-gray.html"
    html_bad_title_band = workdir / "rendered-bad-title-band.html"
    html_bad_text_heavy = workdir / "rendered-bad-text-heavy.html"
    html_bad_text_dense = workdir / "rendered-bad-text-dense.html"
    html_bad_dominant_text = workdir / "rendered-bad-dominant-text.html"
    html_bad_ellipsized_text = workdir / "rendered-bad-ellipsized-text.html"
    html_bad_text_only_motion = workdir / "rendered-bad-text-only-motion.html"
    html_bad_red_dominant = workdir / "rendered-bad-red-dominant.html"
    html_bad_font = workdir / "rendered-bad-font.html"
    video_composition_good = workdir / "video-composition-good.mp4"
    video_composition_slide_like = workdir / "video-composition-slide-like.mp4"
    video_composition_red_dominant = workdir / "video-composition-red-dominant.mp4"
    html_gap = workdir / "composition-gap.html"
    html_bad_padding_source = workdir / "composition-bad-padding.html"
    html_bad_dynamic_rounding = workdir / "composition-bad-dynamic-rounding.html"
    write_text(html_good, rendered_fixture_html())
    write_text(html_masonry_good, masonry_fixture_html())
    write_text(html_masonry_bad, masonry_fixture_html(weak=True))
    write_text(html_masonry_label_heavy, masonry_fixture_html(label_heavy=True))
    write_text(html_bad_padding, rendered_fixture_html(padded=True))
    write_text(html_bad_untagged_inset, rendered_fixture_html(untagged_inset=True))
    write_text(html_bad_no_stroke_untagged_inset, rendered_fixture_html(no_stroke_parent_inset=True))
    write_text(html_bad_small_inset, rendered_fixture_html(small_inset=True))
    write_text(html_bad_transform_offgrid, rendered_fixture_html(transform_offgrid=True))
    write_text(html_bad_css_rounded, rendered_fixture_html(css_rounded=True))
    write_text(html_bad_tiny_gray_swatches, rendered_fixture_html(tiny_gray_swatches=True))
    write_text(html_bad_gray, rendered_fixture_html(weak_gray=True))
    write_text(html_bad_title_band, rendered_fixture_html(title_band=True))
    write_text(html_bad_text_heavy, rendered_fixture_html(text_heavy=True))
    write_text(html_bad_text_dense, rendered_fixture_html(text_dense=True))
    write_text(html_bad_dominant_text, rendered_fixture_html(dominant_text_box=True))
    write_text(html_bad_ellipsized_text, rendered_fixture_html(ellipsized_text=True))
    write_text(html_bad_text_only_motion, rendered_fixture_html(text_only_motion=True))
    write_text(html_bad_red_dominant, rendered_fixture_html(red_dominant=True))
    write_text(html_bad_font, rendered_fixture_html().replace("Open Sans", "Segoe UI"))
    write_text(html_gap, composition_fixture_html(gap=True))
    write_text(html_bad_padding_source, composition_fixture_html(padding=True))
    write_text(html_bad_dynamic_rounding, composition_dynamic_rounding_fixture_html())
    make_video_composition_fixture(video_composition_good, slide_like=False)
    make_video_composition_fixture(video_composition_slide_like, slide_like=True)
    make_video_composition_fixture(video_composition_red_dominant, slide_like=False, red_dominant=True)

    rendered_base = [
        sys.executable,
        str(SCRIPT_DIR / "audit_metro_rendered_frames.py"),
        "--source-package",
        source.as_posix(),
        "--samples",
        "3",
        "--min-shared-edge-ratio",
        "0.25",
    ]
    if not install_browser:
        rendered_base.append("--no-install-browser")

    mute_base = [
        sys.executable,
        str(SCRIPT_DIR / "audit_metro_mute_test.py"),
        "--source-package",
        source.as_posix(),
        "--samples",
        "4",
    ]
    if not install_browser:
        mute_base.append("--no-install-browser")

    cases = [
        run_case(
            name="tonal-open-sans-good-passes",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_tonal_style.py"),
                "--html",
                html_good.as_posix(),
                "--source-package",
                source.as_posix(),
                "--output",
                (workdir / "tonal-open-sans-good.json").as_posix(),
            ],
            manifest=workdir / "tonal-open-sans-good.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="tonal-wrong-font-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_tonal_style.py"),
                "--html",
                html_bad_font.as_posix(),
                "--source-package",
                source.as_posix(),
                "--output",
                (workdir / "tonal-bad-font.json").as_posix(),
            ],
            manifest=workdir / "tonal-bad-font.json",
            expect_pass=False,
            expected_codes=["wrong-metro-font-stack"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="composition-gap-gutter-passes",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_composition.py"),
                "--html",
                html_gap.as_posix(),
                "--output",
                (workdir / "composition-gap.json").as_posix(),
            ],
            manifest=workdir / "composition-gap.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="composition-padding-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_composition.py"),
                "--html",
                html_bad_padding_source.as_posix(),
                "--output",
                (workdir / "composition-bad-padding.json").as_posix(),
            ],
            manifest=workdir / "composition-bad-padding.json",
            expect_pass=False,
            expected_codes=["box-padding-signals"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="composition-dynamic-rounded-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_composition.py"),
                "--html",
                html_bad_dynamic_rounding.as_posix(),
                "--output",
                (workdir / "composition-bad-dynamic-rounding.json").as_posix(),
            ],
            manifest=workdir / "composition-bad-dynamic-rounding.json",
            expect_pass=False,
            expected_codes=["rounded-borders"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-good-passes",
            command=[
                *rendered_base,
                "--html",
                html_good.as_posix(),
                "--output",
                (workdir / "rendered-good.json").as_posix(),
            ],
            manifest=workdir / "rendered-good.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="mp4-composition-good-passes",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_video_composition.py"),
                "--video",
                video_composition_good.as_posix(),
                "--report",
                (workdir / "video-composition-good.json").as_posix(),
                "--min-spatial-change-pairs",
                "2",
            ],
            manifest=workdir / "video-composition-good.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="mp4-composition-slide-like-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_video_composition.py"),
                "--video",
                video_composition_slide_like.as_posix(),
                "--report",
                (workdir / "video-composition-slide-like.json").as_posix(),
            ],
            manifest=workdir / "video-composition-slide-like.json",
            expect_pass=False,
            expected_codes=["contact-sheet-slide-like-composition"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="mp4-composition-red-dominant-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_video_composition.py"),
                "--video",
                video_composition_red_dominant.as_posix(),
                "--report",
                (workdir / "video-composition-red-dominant.json").as_posix(),
            ],
            manifest=workdir / "video-composition-red-dominant.json",
            expect_pass=False,
            expected_codes=["mp4-red-area-too-dominant"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="mp4-composition-missing-video-writes-report",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_video_composition.py"),
                "--video",
                (workdir / "missing-video.mp4").as_posix(),
                "--report",
                (workdir / "video-composition-missing.json").as_posix(),
            ],
            manifest=workdir / "video-composition-missing.json",
            expect_pass=False,
            expected_codes=["mp4-missing-video"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-masonry-good-passes",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_rendered_frames.py"),
                "--source-package",
                source_masonry.as_posix(),
                "--samples",
                "3",
                "--min-shared-edge-ratio",
                "0.25",
                "--html",
                html_masonry_good.as_posix(),
                "--output",
                (workdir / "rendered-masonry-good.json").as_posix(),
                "--no-install-browser",
            ],
            manifest=workdir / "rendered-masonry-good.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-masonry-missing-modules-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_rendered_frames.py"),
                "--source-package",
                source_masonry.as_posix(),
                "--samples",
                "3",
                "--min-shared-edge-ratio",
                "0.25",
                "--html",
                html_masonry_bad.as_posix(),
                "--output",
                (workdir / "rendered-masonry-bad.json").as_posix(),
                "--no-install-browser",
            ],
            manifest=workdir / "rendered-masonry-bad.json",
            expect_pass=False,
            expected_codes=[
                "rendered-missing-masonry-modules",
                "rendered-weak-masonry-size-variety",
                "rendered-static-masonry-construction",
                "rendered-weak-masonry-construction-growth",
            ],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-masonry-label-heavy-fails",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "audit_metro_rendered_frames.py"),
                "--source-package",
                source_masonry.as_posix(),
                "--samples",
                "3",
                "--min-shared-edge-ratio",
                "0.25",
                "--html",
                html_masonry_label_heavy.as_posix(),
                "--output",
                (workdir / "rendered-masonry-label-heavy.json").as_posix(),
                "--no-install-browser",
            ],
            manifest=workdir / "rendered-masonry-label-heavy.json",
            expect_pass=False,
            expected_codes=["rendered-masonry-too-many-text-elements"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-padding-geometry-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_padding.as_posix(),
                "--output",
                (workdir / "rendered-bad-padding.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-padding.json",
            expect_pass=False,
            expected_codes=["rendered-internal-padding-geometry", "rendered-internal-padding-too-large"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-untagged-inset-padding-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_untagged_inset.as_posix(),
                "--output",
                (workdir / "rendered-bad-untagged-inset.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-untagged-inset.json",
            expect_pass=False,
            expected_codes=["rendered-untagged-inset-rect-padding"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-no-stroke-untagged-inset-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_no_stroke_untagged_inset.as_posix(),
                "--output",
                (workdir / "rendered-bad-no-stroke-untagged-inset.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-no-stroke-untagged-inset.json",
            expect_pass=False,
            expected_codes=["rendered-untagged-inset-rect-padding"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-small-inset-padding-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_small_inset.as_posix(),
                "--output",
                (workdir / "rendered-bad-small-inset.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-small-inset.json",
            expect_pass=False,
            expected_codes=["rendered-untagged-inset-rect-padding"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-transformed-offgrid-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_transform_offgrid.as_posix(),
                "--output",
                (workdir / "rendered-bad-transform-offgrid.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-transform-offgrid.json",
            expect_pass=False,
            expected_codes=["rendered-offgrid-rect-edges"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-css-rounded-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_css_rounded.as_posix(),
                "--output",
                (workdir / "rendered-bad-css-rounded.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-css-rounded.json",
            expect_pass=False,
            expected_codes=["rendered-rounded-rects"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-tiny-gray-swatches-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_tiny_gray_swatches.as_posix(),
                "--output",
                (workdir / "rendered-bad-tiny-gray-swatches.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-tiny-gray-swatches.json",
            expect_pass=False,
            expected_codes=[
                "rendered-insufficient-gray-hierarchy",
                "rendered-median-insufficient-gray-hierarchy",
                "rendered-final-insufficient-gray-hierarchy",
            ],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-weak-gray-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_gray.as_posix(),
                "--output",
                (workdir / "rendered-bad-gray.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-gray.json",
            expect_pass=False,
            expected_codes=["rendered-insufficient-gray-hierarchy", "rendered-median-insufficient-gray-hierarchy"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-title-band-text-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_title_band.as_posix(),
                "--output",
                (workdir / "rendered-bad-title-band.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-title-band.json",
            expect_pass=False,
            expected_codes=["rendered-title-band-text"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-text-area-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_text_heavy.as_posix(),
                "--output",
                (workdir / "rendered-bad-text-heavy.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-text-heavy.json",
            expect_pass=False,
            expected_codes=["rendered-text-area-too-high"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-dominant-text-box-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_dominant_text.as_posix(),
                "--output",
                (workdir / "rendered-bad-dominant-text.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-dominant-text.json",
            expect_pass=False,
            expected_codes=["rendered-dominant-text-box"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-mark-to-text-density-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_text_dense.as_posix(),
                "--output",
                (workdir / "rendered-bad-text-dense.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-text-dense.json",
            expect_pass=False,
            expected_codes=["weak-rendered-mark-to-text-density"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-ellipsized-text-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_ellipsized_text.as_posix(),
                "--output",
                (workdir / "rendered-bad-ellipsized-text.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-ellipsized-text.json",
            expect_pass=False,
            expected_codes=["rendered-ellipsized-text"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="rendered-red-dominant-surface-fails",
            command=[
                *rendered_base,
                "--html",
                html_bad_red_dominant.as_posix(),
                "--output",
                (workdir / "rendered-bad-red-dominant.json").as_posix(),
            ],
            manifest=workdir / "rendered-bad-red-dominant.json",
            expect_pass=False,
            expected_codes=["rendered-red-rect-area-too-high"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="mute-test-good-passes",
            command=[
                *mute_base,
                "--html",
                html_good.as_posix(),
                "--output",
                (workdir / "mute-test-good.json").as_posix(),
            ],
            manifest=workdir / "mute-test-good.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="mute-test-text-only-motion-fails",
            command=[
                *mute_base,
                "--html",
                html_bad_text_only_motion.as_posix(),
                "--output",
                (workdir / "mute-test-bad-text-only-motion.json").as_posix(),
            ],
            manifest=workdir / "mute-test-bad-text-only-motion.json",
            expect_pass=False,
            expected_codes=["mute-test-hidden-motion-too-weak", "mute-test-hidden-change-ratio-too-low"],
            timeout_seconds=timeout_seconds,
        ),
        run_case(
            name="suite-output-only-derives-children",
            command=[
                sys.executable,
                str(SCRIPT_DIR / "run_metro_audit_suite.py"),
                "--html",
                html_good.as_posix(),
                "--source-package",
                source.as_posix(),
                "--output",
                (workdir / "suite-output-only.json").as_posix(),
                "--no-install-browser",
                "--audit-timeout-seconds",
                str(timeout_seconds),
            ],
            manifest=workdir / "suite-output-only.json",
            expect_pass=True,
            expected_codes=None,
            timeout_seconds=timeout_seconds * 3,
        ),
    ]
    cases.extend(semantic_masonry_contract_cases())
    cases.extend(semantic_source_anchor_binding_cases())
    child_reports = [
        "metro-style-audit.json",
        "metro-composition-audit.json",
        "metro-rendered-frame-audit.json",
        "metro-mute-test-audit.json",
    ]
    suite_children_exist = all((workdir / name).exists() for name in child_reports)
    if not suite_children_exist:
        cases.append(
            {
                "name": "suite-output-only-child-reports-exist",
                "passed": False,
                "missing": [name for name in child_reports if not (workdir / name).exists()],
            }
        )
    return {"passed": all(case.get("passed") is True for case in cases), "workdir": workdir.as_posix(), "cases": cases}


def main() -> int:
    args = parse_args()
    if args.workdir:
        workdir = args.workdir
        workdir.mkdir(parents=True, exist_ok=True)
        report = run_validation(workdir, install_browser=args.install_browser, timeout_seconds=args.timeout_seconds)
    else:
        with tempfile.TemporaryDirectory(prefix="metro-audit-fixtures-") as temp:
            report = run_validation(Path(temp), install_browser=args.install_browser, timeout_seconds=args.timeout_seconds)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

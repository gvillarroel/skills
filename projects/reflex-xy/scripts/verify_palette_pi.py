#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Independently inspect paired-palette Pi outputs and scoped bundle profiles.

Run with the project Python or uv, --run <run-id> (repeat), and/or --audit.
The canonical repository colorsets, not an agent-authored manifest, define paints.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
PYTHON = ROOT / "projects/reflex-xy/artifacts/runtime/.venv/Scripts/python.exe"
OUTPUT = ROOT / "projects/reflex-xy/artifacts/pi-palette-verification"
EXPECTED_RECORDS = [
    {"group": "North", "x": 1, "y": 5}, {"group": "South", "x": 2, "y": 3},
    {"group": "East", "x": 3, "y": 8}, {"group": "North", "x": 4, "y": 7},
    {"group": "South", "x": 5, "y": 6}, {"group": "East", "x": 6, "y": 9},
]
ORDER = ["North", "South", "East"]
PALETTES = json.loads((ROOT / "docs/colorsets.json").read_text(encoding="utf-8"))["colorsets"]


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def color(value):
    value = value.strip().lower()
    if value in {"none", "transparent", "currentcolor", "inherit"} or value.startswith("url("):
        return None
    if value in {"black", "white"}:
        return {"black": "#000000", "white": "#ffffff"}[value]
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(channel * 2 for channel in value[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return value
    match = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if match:
        channels = re.split(r"[\s,/]+", match.group(1).strip())
        if len(channels) == 4 and float(channels[3]) == 0:
            return None
        return "#" + "".join(f"{round(float(c[:-1]) * 2.55) if c.endswith('%') else round(float(c)):02x}" for c in channels[:3])
    return value


def inspect_svg(path, selected, naturalistic):
    root = ET.parse(path).getroot()
    paints, labels, circles, geometry = Counter(), [], [], []
    ignored = {"fill", "stroke", "style", "stop-color", "color"}
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        styles = {**node.attrib, **dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", node.get("style", "")))}
        for key in ("fill", "stroke", "stop-color", "color", "flood-color"):
            if key in styles and (paint := color(styles[key])) is not None:
                paints[paint] += 1
        if tag == "text":
            labels.append("".join(node.itertext()).strip())
        if tag == "circle":
            circles.append({"x": float(node.get("cx")), "y": float(node.get("cy")),
                            "radius": float(node.get("r")), "fill": color(node.get("fill")),
                            "opacity": float(node.get("fill-opacity", "1")),
                            "stroke_width": float(node.get("stroke-width", "0"))})
        geometry.append([tag, {key: value for key, value in node.attrib.items() if key not in ignored},
                         "".join(node.itertext()).strip() if tag == "text" else ""])
    extra = sorted(set(paints) - set(PALETTES[selected]["allowed"]))
    check(not extra, f"{path.name}: off-palette SVG paints {extra}")
    data_circles = []
    if naturalistic:
        largest = max(circle["radius"] for circle in circles)
        data_circles = [point for point in circles if point["radius"] == largest]
        expected = dict(zip(ORDER, PALETTES[selected]["solidSequence"][:3]))
        check(len(data_circles) == 6, f"Expected six data points, found {len(data_circles)}")
        check(Counter(point["fill"] for point in data_circles) == Counter({c: 2 for c in expected.values()}),
              "SVG data-point color counts do not match the group mapping")
        ordered = sorted(data_circles, key=lambda point: point["x"])
        left, right = ordered[0]["x"], ordered[-1]["x"]
        top, bottom = min(point["y"] for point in ordered), max(point["y"] for point in ordered)
        for point, record in zip(ordered, EXPECTED_RECORDS):
            check(point["fill"] == expected[record["group"]], "SVG assigned a group paint to the wrong record")
            expected_x = left + (record["x"] - 1) / 5 * (right - left)
            expected_y = bottom - (record["y"] - 3) / 6 * (bottom - top)
            check(abs(point["x"] - expected_x) < 0.05 and abs(point["y"] - expected_y) < 0.05,
                  "SVG point geometry does not preserve original x/y values")
        check(all(point["opacity"] == 1 and point["stroke_width"] == 0 for point in data_circles),
              "Data markers are not opaque borderless solids")
        for label in ["Regional sample comparison", "Input", "Response", *ORDER]:
            check(label in labels, f"Missing native label {label!r}")
    return {"path": str(path.relative_to(ROOT)), "sha256": digest(path), "paints": dict(paints),
            "labels": labels, "dataCircles": data_circles, "geometry": geometry,
            "dimensions": [int(float(root.get("width"))), int(float(root.get("height")))]}


def nested_values(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from nested_values(child)
    if isinstance(value, list):
        for child in value:
            yield from nested_values(child)


def inspect_source(workspace):
    source = (workspace / "app.py").read_text(encoding="utf-8")
    check(re.search(r'dependencies\s*=\s*\[\s*[\"\x27]xy==0\.0\.8[\"\x27]', source),
          "app.py lacks the requested PEP 723 xy==0.0.8 pin")
    literals = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.List, ast.Tuple, ast.Dict)):
            try:
                literals.append(ast.literal_eval(node))
            except (ValueError, TypeError):
                pass
    check(EXPECTED_RECORDS in literals, "Original six row records are not preserved in editable source")
    check(ORDER in literals or tuple(ORDER) in literals, "Stable North/South/East category order is missing")
    manifest = json.loads((workspace / "results/palettes.json").read_text(encoding="utf-8"))
    values = list(nested_values(manifest))
    mappings = {}
    for selected in ("colorset1", "colorset2"):
        expected = dict(zip(ORDER, PALETTES[selected]["solidSequence"][:3]))
        check(expected in values, f"Manifest does not record actual expected {selected} mapping")
        check(PALETTES[selected] in values, f"Manifest does not record selected {selected} contract")
        mappings[selected] = expected
    return {"sha256": digest(workspace / "app.py"), "records": EXPECTED_RECORDS,
            "categoryOrder": ORDER, "mappings": mappings}


def inspect_browser(browser, path, selected, svg, output, naturalistic):
    context = browser.new_context(viewport={"width": 1200, "height": 800}, device_scale_factor=1)
    blocked, errors = [], []
    context.route("**/*", lambda route: (blocked.append(route.request.url), route.abort())
                  if route.request.url.startswith(("http://", "https://")) else route.continue_())
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(path.resolve().as_uri(), wait_until="load")
    page.locator(".xy canvas").first.wait_for(state="visible")
    page.wait_for_timeout(300)
    target = page.locator(".xy").first
    screen = target.screenshot()
    (output / f"{selected}.png").write_bytes(screen)
    with Image.open(io.BytesIO(screen)) as image:
        rgb = image.convert("RGB")
        counts = Counter(rgb.get_flattened_data())
    expected = PALETTES[selected]["solidSequence"][:3] if naturalistic else None
    exact_counts = {}
    if expected:
        for fill in expected:
            pixel = tuple(int(fill[i:i + 2], 16) for i in (1, 3, 5))
            exact_counts[fill] = counts[pixel]
            check(counts[pixel] > 50, f"No substantial actual browser paint for {fill}")
    chrome = target.evaluate("""root => {
        const grab = node => {const s=getComputedStyle(node); return {
            color:s.color, background:s.backgroundColor, border:s.borderColor, shadow:s.boxShadow};};
        return {root:grab(root), modebar:grab(root.querySelector('[data-xy-slot="modebar"]')),
                tooltip:grab(root.querySelector('[data-xy-slot="tooltip"]'))};
    }""")
    for role in ("root", "modebar", "tooltip"):
        for key in ("color", "background", "border"):
            paint = color(chrome[role][key])
            check(paint is None or paint in PALETTES[selected]["allowed"], f"Off-palette browser {role}.{key}: {paint}")
    legend_overlap = []
    if naturalistic:
        box = target.bounding_box()
        legend = page.locator('[data-xy-slot="legend"]').first.bounding_box()
        if legend:
            for point in svg["dataCircles"]:
                x, y, radius = box["x"] + point["x"], box["y"] + point["y"], point["radius"]
                if (x + radius > legend["x"] and x - radius < legend["x"] + legend["width"] and
                        y + radius > legend["y"] and y - radius < legend["y"] + legend["height"]):
                    legend_overlap.append(point)
    # Actually open a point tooltip when point positions are known. Search a
    # small local neighborhood because native/browser text metrics can differ.
    tooltip_open = False
    if svg["dataCircles"]:
        box = target.bounding_box()
        point = svg["dataCircles"][0]
        for dx, dy in ((0, 0), (-4, 0), (4, 0), (0, -4), (0, 4)):
            page.mouse.move(box["x"] + point["x"] + dx, box["y"] + point["y"] + dy)
            page.wait_for_timeout(70)
            tooltip_open = page.locator('[data-xy-slot="tooltip"]').first.is_visible()
            if tooltip_open:
                break
        check(tooltip_open, "A real data point did not open its browser tooltip")
        page.screenshot(path=str(output / f"{selected}-tooltip.png"))
    check(not blocked, f"HTML requested external network: {blocked}")
    check(not errors, f"Browser page errors: {errors}")
    result = {"chrome": chrome, "exactPixelCounts": exact_counts, "tooltipOpened": tooltip_open,
              "blockedRequests": blocked, "pageErrors": errors, "legendPointOverlaps": legend_overlap}
    context.close()
    return result


def verify_run(run_id, browser):
    run = ROOT / "evaluations/runs" / run_id
    workspace = run / "workspace"
    output = OUTPUT / run_id
    output.mkdir(parents=True, exist_ok=True)
    naturalistic = "naturalistic" in run_id
    result_path = run / "evaluation-result.json"
    check(result_path.is_file(), f"Run is not complete yet: {run_id}")
    harness = json.loads(result_path.read_text(encoding="utf-8"))
    report = {"runId": run_id, "harness": harness, "artifactPassed": False, "errors": []}
    try:
        if naturalistic:
            report["source"] = inspect_source(workspace)
        reports = {}
        for selected, stem in (("colorset1", "cs1"), ("colorset2", "cs2")):
            base = workspace / "results" / stem
            svg_path = base.with_suffix(".svg") if naturalistic else base / "chart.svg"
            html_path = base.with_suffix(".html") if naturalistic else base / "chart.html"
            svg = inspect_svg(svg_path, selected, naturalistic)
            reports[selected] = {"svg": svg,
                                 "browser": inspect_browser(browser, html_path, selected, svg, output, naturalistic)}
        report["variants"] = reports
        report["visualPassed"] = not any(variant["browser"]["legendPointOverlaps"] for variant in reports.values())
        check(reports["colorset1"]["svg"]["geometry"] == reports["colorset2"]["svg"]["geometry"],
              "Paired palettes changed the native geometry or labels")
        if naturalistic:
            # Recreate generated source and resources elsewhere; preserve the
            # agent's outputs and the immutable observed skill payload.
            rerun = output / "rerun"
            if not rerun.exists():
                shutil.copytree(workspace, rerun, ignore=shutil.ignore_patterns("results", "__pycache__"))
            execute = subprocess.run([str(PYTHON), "app.py"], cwd=rerun,
                                     text=True, encoding="utf-8", capture_output=True, timeout=90)
            report["rerun"] = {"returnCode": execute.returncode, "stdout": execute.stdout, "stderr": execute.stderr}
            check(execute.returncode == 0, "Editable app.py could not regenerate outputs")
            for selected, stem in (("colorset1", "cs1"), ("colorset2", "cs2")):
                regenerated = inspect_svg(rerun / "results" / f"{stem}.svg", selected, True)
                check(regenerated["sha256"] == reports[selected]["svg"]["sha256"], "Source rerun changed SVG bytes")
        report["artifactPassed"] = True
    except Exception as error:
        report["errors"].append(f"{type(error).__name__}: {error}")
    # A good artifact never erases a strict runtime/model/read-surface failure.
    report["passed"] = report["artifactPassed"] and report.get("visualPassed", False) and bool(harness.get("passed"))
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runId": run_id, "harnessPassed": harness.get("passed"),
                      "artifactPassed": report["artifactPassed"], "visualPassed": report.get("visualPassed"),
                      "errors": report["errors"]}))
    return report


def audit_profiles():
    spec = importlib.util.spec_from_file_location("pi_helper", ROOT / "scripts/run-pi-skill-eval.py")
    helper = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = helper
    spec.loader.exec_module(helper)
    audit = OUTPUT / ("payload-audit-" + uuid.uuid4().hex[:8])
    report = {"sourceCurrent": helper.snapshot_digest(helper.snapshot_tree(ROOT / "skills/reflex-xy")),
              "profiles": {}}
    for profile in ("source", "runtime", "full"):
        target = audit / profile / "skills/reflex-xy"
        helper.copy_skill_only(ROOT / "skills/reflex-xy", target, "runtime" if profile == "runtime" else "full")
        snapshot = helper.snapshot_tree(target)
        command = ["uv", "run", "--script", str(ROOT / "scripts/validate-skills.py"),
                   "--root", str(audit / profile), "--skill", str(target), "--profile", profile]
        env = {**os.environ, "UV_CACHE_DIR": str(ROOT / "projects/reflex-xy/cache/uv")}
        result = subprocess.run(command, cwd=ROOT, env=env, text=True, encoding="utf-8", capture_output=True, timeout=90)
        report["profiles"][profile] = {"fileCount": len(snapshot), "payloadSha256": helper.snapshot_digest(snapshot),
                                       "files": snapshot, "validatorReturnCode": result.returncode,
                                       "validatorOutput": result.stdout + result.stderr}
    report["sourceFinal"] = helper.snapshot_digest(helper.snapshot_tree(ROOT / "skills/reflex-xy"))
    report["passed"] = all(p["validatorReturnCode"] == 0 for p in report["profiles"].values())
    (audit / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audit": str(audit), "passed": report["passed"],
                      "profiles": {key: {field: value[field] for field in ("fileCount", "payloadSha256", "validatorReturnCode")}
                                   for key, value in report["profiles"].items()}}))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", default=[])
    parser.add_argument("--audit", action="store_true")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if args.audit:
        audit_profiles()
    if args.run:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, channel="msedge")
            try:
                for run_id in args.run:
                    verify_run(run_id, browser)
            finally:
                browser.close()

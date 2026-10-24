#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow==13.0.0", "playwright==1.64.1"]
# ///
"""Independent artifact and trace evaluation for the predeclared XY atlas cohort."""
from __future__ import annotations
import argparse
import ast
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "projects/reflex-xy/artifacts/atlas-pi"
PLAN = json.loads((OUT / "plan.json").read_text(encoding="utf-8"))
FROZEN = json.loads((OUT / "runtime-freeze.json").read_text(encoding="utf-8"))["digest"]
PALETTES = json.loads((ROOT / "docs/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
spec = importlib.util.spec_from_file_location("original_xy_contract", ROOT / "evaluations/contracts/reflex-xy.py")
BASE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BASE)
# The evaluator's own probe arguments must not reach an application's CLI.
BASE.RUNTIME_PROBE = BASE.RUNTIME_PROBE.replace(
    "    runpy.run_path(str(target), run_name='__main__')",
    "    sys.argv = [str(target)]\n    runpy.run_path(str(target), run_name='__main__')",
)


def check(value, message):
    if not value:
        raise AssertionError(message)


def command(argv, cwd=ROOT, timeout=300):
    done = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    result = {"command": [str(v) for v in argv], "returncode": done.returncode,
              "stdout": done.stdout[-16000:], "stderr": done.stderr[-16000:]}
    check(done.returncode == 0, "Independent command failed: " + json.dumps(result))
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_color(value):
    value = value.strip().lower()
    if value in {"none", "transparent", "currentcolor", "inherit"} or value.startswith("url("):
        return None
    if value in {"black", "white"}:
        return {"black": "#000000", "white": "#ffffff"}[value]
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(c * 2 for c in value[1:])
    match = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if match:
        channels = re.split(r"[\s,/]+", match.group(1).strip())
        if len(channels) == 4 and float(channels[3]) == 0:
            return None
        return "#" + "".join(f"{round(float(c)):02x}" for c in channels[:3])
    return value


def svg_inspect(path, palette, labels):
    root = ET.parse(path).getroot()
    check(root.tag.rsplit("}", 1)[-1] == "svg", "Native artifact is not SVG XML")
    paints = Counter()
    for node in root.iter():
        styles = {**node.attrib, **dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", node.get("style", "")))}
        for key in ("fill", "stroke", "stop-color", "color"):
            if key in styles and (paint := normalize_color(styles[key])) is not None:
                paints[paint] += 1
    extra = sorted(set(paints) - set(PALETTES[palette]["allowed"]))
    check(not extra, f"{path.name} has off-palette authored paints: {extra}")
    text = " ".join(" ".join(node.itertext()) for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "text")
    for label in labels:
        check(label in text, f"Missing native chart label {label!r}")
    return {"sha256": digest(path), "paints": dict(paints), "text": text,
            "dimensions": [float(root.get("width")), float(root.get("height"))],
            "viewBox": root.get("viewBox")}


CANONICAL_PROBE = r'''
import functools
import json
from pathlib import Path
import runpy
import sys
import xy

target, destination = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(target.parent))
captured=[]

def capture(chart, method, arguments, keywords):
    fig=getattr(chart,'_figure',None)
    if fig is None:
        return
    traces=[]
    for trace in fig.traces:
        item={'kind':trace.kind}
        for name in ('x','y','base','x0','x1','y0','y1'):
            col=getattr(trace,name,None)
            if col is not None:
                item[name]=col.values.tolist()
        cc=getattr(trace,'color_ch',None)
        item['color']={'mode':'style','constant':trace.style.get('color')}
        if cc is not None:
            item['color']={'mode':cc.mode,'constant':getattr(cc,'constant',None)}
            for attribute in ('codes','rgba'):
                value=getattr(cc,attribute,None)
                if value is not None:
                    item['color'][attribute]=value.tolist()
            if cc.mode=='categorical':
                item['color']['palette']=cc.colors
        traces.append(item)
    path=arguments[0] if arguments else keywords.get('path')
    captured.append({'chart_identity':id(chart),'method':method,'path':str(path) if path is not None else None,
                     'title':fig.title,'traces':traces})

for method in ('to_html','to_svg','write_image','to_image','to_png'):
    original=getattr(xy.Chart,method)
    def wrapper(original=original,method=method):
        @functools.wraps(original)
        def wrapped(chart,*arguments,**keywords):
            result=original(chart,*arguments,**keywords)
            capture(chart,method,arguments,keywords)
            return result
        return wrapped
    setattr(xy.Chart,method,wrapper())
sys.argv=[str(target)]
runpy.run_path(str(target),run_name='__main__')
destination.write_text(json.dumps(captured,indent=2)+'\n',encoding='utf-8')
'''


def points_from_trace(trace):
    points = []
    for a, b in (("x", "y"), ("x", "base"), ("x0", "y0"), ("x1", "y1")):
        if a in trace and b in trace:
            points.extend(zip(trace[a], trace[b]))
    if all(name in trace for name in ("x0", "x1", "y0", "y1")):
        # Rectangular interval compositions carry the sample at their center.
        for x0, x1, y0, y1 in zip(trace["x0"], trace["x1"], trace["y0"], trace["y1"]):
            points.extend([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)])
    return [(float(a), float(b)) for a, b in points if a is not None and b is not None and math.isfinite(float(a)) and math.isfinite(float(b))]


def check_naturalistic_data(run, evidence):
    workspace = run / "workspace"
    meta = BASE.metadata((workspace / "app.py").read_text(encoding="utf-8"))
    probe, data = evidence / "canonical-probe.py", evidence / "canonical-chart-data.json"
    header = '#!/usr/bin/env -S uv run --script\n# /// script\n# requires-python = ' + json.dumps(meta.get("requires-python", ">=3.11")) + '\n# dependencies = ' + json.dumps(meta.get("dependencies", [])) + '\n# ///\n'
    probe.write_text(header + CANONICAL_PROBE, encoding="utf-8")
    execution = command(["uv", "run", "--script", str(probe), str(workspace / "app.py"), str(data)], workspace)
    charts = json.loads(data.read_text(encoding="utf-8"))
    expected = BASE.prompt_records((run / "prompt.md").read_text(encoding="utf-8"), "naturalistic")
    target = Counter((float(r["humidity_pct"]), float(r["response_ms"])) for r in expected)
    correct = []
    for chart in charts:
        points, paints = [], {}
        for trace in chart["traces"]:
            if trace["kind"] != "scatter":
                continue
            for index, (x, y) in enumerate(zip(trace.get("x", []), trace.get("y", []))):
                point = (float(x), float(y)); points.append(point)
                encoding = trace["color"]
                if encoding["mode"] == "categorical":
                    paint = encoding["palette"][encoding["codes"][index] % len(encoding["palette"])]
                elif encoding["mode"] == "direct_rgba":
                    paint = "#" + "".join(f"{round(v * 255):02x}" for v in encoding["rgba"][index][:3])
                else:
                    paint = encoding.get("constant")
                paints[point] = normalize_color(paint) if paint is not None else None
        if Counter(points) != target:
            continue
        per_room = {room: {paints[(float(row["humidity_pct"]), float(row["response_ms"]))] for row in expected if row["room"] == room} for room in ("Atrium", "Lab", "Store")}
        check(all(len(values) == 1 and None not in values for values in per_room.values()), "Room colors vary or are unresolved within a category")
        check(len(set.union(*per_room.values())) == 3, "Different rooms share an indistinguishable category color")
        correct.append({"path": chart["path"], "points": len(points), "room_colors": {room: list(values)[0] for room, values in per_room.items()}})
    check(correct, "Actual exported XY scatter coordinates do not preserve the twelve source observations")
    return {"execution": execution, "correct_exports": correct, "evidence": str(data)}


def inspect_generalization(run, evidence):
    workspace = run / "workspace"
    result = {"case": "generalization", "checks": {}, "findings": []}
    checks = result["checks"]
    try:
        attempt = next(a for a in PLAN["attempts"] if a["run_id"] == run.name)
        check(all((workspace / p).is_file() and (workspace / p).stat().st_size for p in attempt["outputs"]), "A required exact artifact is missing or empty")
        checks["original_outputs"] = {p: {"sha256": digest(workspace / p), "bytes": (workspace / p).stat().st_size} for p in attempt["outputs"]}
        source = (workspace / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        meta = BASE.metadata(source)
        check("xy==0.0.8" in meta.get("dependencies", []), "PEP 723 metadata must declare xy==0.0.8")
        imports = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
        imports += [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        check(any(n == "xy" or n.startswith("xy.") for n in imports), "The source does not use Python XY")
        expected = BASE.prompt_records((run / "prompt.md").read_text(encoding="utf-8"), "generalization")
        uv = shutil.which("uv")
        checks["regeneration"] = command([uv, "run", "--script", "app.py"], workspace)
        checks["source_records"] = BASE.inspect_runtime_records(uv, workspace, meta, expected, evidence / "records-check.json")
        probe = evidence / "canonical-probe.py"
        data = evidence / "canonical-chart-data.json"
        header = '#!/usr/bin/env -S uv run --script\n# /// script\n# requires-python = ' + json.dumps(meta.get("requires-python", ">=3.11")) + '\n# dependencies = ' + json.dumps(meta.get("dependencies", [])) + '\n# ///\n'
        probe.write_text(header + CANONICAL_PROBE, encoding="utf-8")
        checks["canonical_execution"] = command([uv, "run", "--script", str(probe), str(workspace / "app.py"), str(data)], workspace)
        charts = json.loads(data.read_text(encoding="utf-8"))
        required_points = [(float(row["elapsed_h"]), float(row[field])) for row in expected for field in ("center", "lower", "upper")]
        valid = []
        for chart in charts:
            points = [p for trace in chart["traces"] for p in points_from_trace(trace)]
            if all(any(abs(x - px) < 1e-7 and abs(y - py) < 1e-7 for px, py in points) for x, y in required_points):
                valid.append(chart)
        check(valid, "Exported XY geometry does not contain all supplied x/center/lower/upper values")
        for relative in ("results/cs1/interval.html", "results/cs2/interval.html"):
            matching = [c for c in valid if c["path"] and Path(c["path"]).as_posix().replace('\\', '/').endswith(relative)]
            check(matching, f"No correct exported canonical data for {relative}")
        checks["actual_data"] = {"required_vertices": len(required_points), "valid_exports": len(valid), "evidence": str(data)}
        labels = ["Sensor interval estimates", "Elapsed time (h)", "Response (units)", "Fictional observations"]
        native, browsers = {}, {}
        for suffix, palette in (("cs1", "colorset1"), ("cs2", "colorset2")):
            html = workspace / f"results/{suffix}/interval.html"
            svg = workspace / f"results/{suffix}/interval.svg"
            native[suffix] = svg_inspect(svg, palette, labels[:3])
            check(BASE.inspect_html(html)["scripts"] > 0, "HTML lacks an interactive runtime")
            browsers[suffix] = BASE.inspect_browser(html, labels, evidence / f"{suffix}-browser.png", None)
            check(not browsers[suffix]["blocked_remote_requests"], "The delivered HTML attempted a network request")
        check(native["cs1"]["dimensions"] == native["cs2"]["dimensions"], "The paired SVG dimensions differ")
        check(native["cs1"]["paints"] != native["cs2"]["paints"], "The requested two color treatments are visually identical")
        checks["native"] = native
        checks["browser"] = browsers
        notes = (workspace / "notes.md").read_text(encoding="utf-8").lower()
        check(any(w in notes for w in ("fictional", "synthetic")), "Notes omit the fictional data status")
        check(any(w in notes for w in ("supplied", "provided", "measurement range", "measurement bound")), "Notes omit the supplied-boundary meaning")
        check(any(w in notes for w in ("offline", "standalone", "snapshot")), "Notes omit the offline delivery boundary")
        checks["notes"] = {"bytes": len(notes.encode()), "manual_review": "Confirm supplied intervals, truthful checks, and no offline Python callback claim."}
        checks["final_outputs"] = {p: {"sha256": digest(workspace / p), "bytes": (workspace / p).stat().st_size} for p in attempt["outputs"]}
    except Exception as error:
        result["findings"].append(f"{type(error).__name__}: {error}")
    result["passed"] = not result["findings"]
    return result


def inspect_contract(run, evidence):
    result = {"case": "contract", "checks": {}, "findings": []}
    try:
        workspace = run / "workspace"
        prompt = (run / "prompt.md").read_text(encoding="utf-8")
        original = workspace / "results/original.svg"
        repaired = workspace / "results/repaired.svg"
        expected = re.search(r"```xml\n(.*?)```", prompt, re.S).group(1)
        check(original.read_text(encoding="utf-8") == expected, "The original evidence differs from the prompt fixture")
        before = digest(original)
        root = ET.parse(repaired).getroot()
        children = list(root)
        check(children[0].text == "Line symbol evidence", "The title changed")
        check(children[1].attrib == {"d": "M 20 30 L 40 50", "fill": "none", "stroke": "#9e1b32", "stroke-width": "2"}, "The repaired line geometry or paint changed")
        check(children[2].attrib == {"cx": "100", "cy": "50", "r": "8", "fill": "#007298"}, "The solid circle changed")
        report = json.loads((workspace / "results/repair.json").read_text(encoding="utf-8"))
        check(report["repairedPaths"] == 1 and report["validSvgXml"] is True, "The helper report is incorrect")
        replay = evidence / "repaired-replay.svg"
        execution = command(["uv", "run", "--script", "skills/reflex-xy/scripts/xy_svg_compat.py", "--input", "results/original.svg", "--output", str(replay)], workspace)
        check(digest(original) == before, "The original evidence was mutated")
        check(ET.tostring(ET.parse(replay).getroot()) == ET.tostring(root), "The helper does not reproduce the delivered repair")
        result["checks"] = {"original_sha256": before, "repaired_sha256": digest(repaired), "repair_report": report, "replay": execution}
    except Exception as error:
        result["findings"].append(f"{type(error).__name__}: {error}")
    result["passed"] = not result["findings"]
    return result


def inspect(attempt):
    run = ROOT / "evaluations/runs" / attempt["run_id"]
    evidence = OUT / attempt["run_id"]
    evidence.mkdir(exist_ok=True)
    case = attempt["case"]
    if case == "generalization":
        result = inspect_generalization(run, evidence)
    elif case == "contract":
        result = inspect_contract(run, evidence)
    else:
        result = BASE.inspect(run, case, evidence / "independent-check.json", None)
        if case == "naturalistic" and result["passed"]:
            try:
                result["checks"]["actual_scatter_data"] = check_naturalistic_data(run, evidence)
            except Exception as error:
                result["findings"].append(f"Actual data check: {type(error).__name__}: {error}")
                result["passed"] = False
    result["run_id"] = run.name
    try:
        manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
        result["frozen_digest_matches"] = manifest["skill"]["payloadSha256"] == FROZEN
        result["strict"] = json.loads((run / "evaluation-result.json").read_text(encoding="utf-8"))
        result["integrity"] = json.loads((run / "skill-integrity-check.json").read_text(encoding="utf-8"))
        trace_path = evidence / "read-surface.json"
        argv = ["uv", "run", "--script", "scripts/summarize-pi-json-events.py", str(run / "events.jsonl"), "--output", str(trace_path), "--require-model", "gpt-5.6-sol", "--fail-on-invalid-json", "--fail-on-tool-error"]
        # Retain a failing summary rather than converting its exit status into an evaluator exception.
        done = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        result["trace_summary_execution"] = {"returncode": done.returncode, "stdout": done.stdout[-8000:], "stderr": done.stderr[-8000:]}
        result["trace_summary"] = json.loads(trace_path.read_text(encoding="utf-8"))
    except Exception as error:
        result["findings"].append(f"Harness evidence error: {type(error).__name__}: {error}")
        result["passed"] = False
    result["artifact_passed"] = result["passed"]
    result["joint_before_manual"] = bool(result["artifact_passed"] and result.get("frozen_digest_matches") and result.get("integrity", {}).get("passed") and result.get("strict", {}).get("passed") and result.get("trace_summary_execution", {}).get("returncode") == 0)
    result["manual_review_pending"] = case != "contract"
    (evidence / "independent-check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run.name, "artifact_passed": result["artifact_passed"], "joint_before_manual": result["joint_before_manual"], "findings": result["findings"]}), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", help="Declared run ID; repeat, or omit for all completed attempts")
    args = parser.parse_args()
    selected = [a for a in PLAN["attempts"] if not args.run or a["run_id"] in args.run]
    selected = [a for a in selected if (ROOT / "evaluations/runs" / a["run_id"] / "evaluation-result.json").is_file()]
    results = [inspect(a) for a in selected]
    (OUT / "independent-progress.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

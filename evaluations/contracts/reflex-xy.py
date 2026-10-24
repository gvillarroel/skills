#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.51"]
# ///
"""Independently execute and inspect isolated reflex-xy evaluation artifacts.

Run with: uv run --script evaluations/contracts/reflex-xy.py RUN --case CASE
          --output RUN/independent-check.json

This evaluator checks observable exports and original input records. It does not
import the evaluated skill or require its templates, variable names, or helpers.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import tomllib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright


CASE_OUTPUTS = {
    "contract": ["artifacts/probe/chart.html", "artifacts/probe/chart.svg", "artifacts/probe/chart.png", "artifacts/probe.json"],
    "naturalistic": ["app.py", "results/cloud.html", "results/cloud.svg"],
    "generalization": ["app.py", "results/trend.html", "results/trend.png"],
    "boundary": ["design.md", "app.py", "results/selection.html"],
}

CASE_TEXT = {
    "naturalistic": ["Sensor response by humidity", "Humidity (%)", "Response (ms)", "Atrium", "Lab", "Store"],
    "generalization": ["Reservoir level in March", "Observation date", "Level (m)"],
    "boundary": ["Offline selection snapshot"],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nested_values(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from nested_values(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            yield from nested_values(child)


def prompt_records(prompt: str, case: str) -> list[dict[str, Any]]:
    if case == "contract":
        return []
    blocks = re.findall(r"```json\s*(.*?)\s*```", prompt, flags=re.S)
    if case == "boundary":
        blocks = re.findall(r"`(\[\{.*?\}\])`", prompt, flags=re.S)
    matches = [json.loads(block) for block in blocks]
    rows = next((item for item in matches if isinstance(item, list) and item and isinstance(item[0], dict)), None)
    if rows is None:
        raise ValueError("The case prompt has no complete source record array.")
    return rows


def metadata(source: str) -> dict[str, Any]:
    lines = source.splitlines()
    start = next((index for index, line in enumerate(lines) if line.strip() == "# /// script"), None)
    if start is None:
        raise ValueError("app.py has no PEP 723 script block.")
    end = next((index for index in range(start + 1, len(lines)) if lines[index].strip() == "# ///"), None)
    if end is None:
        raise ValueError("app.py has an unterminated PEP 723 script block.")
    body = "\n".join(line[2:] if line.startswith("# ") else line[1:] for line in lines[start + 1:end])
    return tomllib.loads(body)


def retains_records(values: list[Any], expected: list[dict[str, Any]]) -> bool:
    if any(isinstance(value, list) and value == expected for value in values):
        return True
    # A column-oriented literal is also a faithful source representation.
    keys = list(expected[0])
    for value in values:
        if isinstance(value, dict) and set(value) == set(keys):
            columns = [value[key] for key in keys]
            if all(isinstance(column, (list, tuple)) and len(column) == len(expected) for column in columns):
                rows = [dict(zip(keys, row)) for row in zip(*columns)]
                if rows == expected:
                    return True
    return False


RUNTIME_PROBE = r'''
import datetime
import json
import runpy
import sys
from pathlib import Path

target = Path(sys.argv[1]).resolve()
target_filename = str(target)
destination = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(target.parent))
found = []
seen = set()

def canonical(value):
    if isinstance(value, datetime.datetime):
        return value.date().isoformat() if value.time() == datetime.time() else value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, float) and value != value:
        return None
    if isinstance(value, dict):
        return {str(key): canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(type(value).__name__)

def collect(value, location):
    try:
        module = type(value).__module__
        if module.startswith('pandas.') and hasattr(value, 'to_dict'):
            value = value.to_dict(orient='records')
        elif module.startswith('polars.') and hasattr(value, 'to_dicts'):
            value = value.to_dicts()
        elif module.startswith('pyarrow.') and hasattr(value, 'to_pylist'):
            value = value.to_pylist()
        if not isinstance(value, (list, tuple, dict, str)):
            return
        if isinstance(value, str):
            if not value.lstrip().startswith(('[', '{')):
                return
            value = json.loads(value)
        if len(value) > 10000:
            return
        value = canonical(value)
        serialized = json.dumps(value, sort_keys=True, allow_nan=False)
        if serialized not in seen:
            seen.add(serialized)
            found.append({'location': location, 'value': value})
    except Exception:
        pass

def profile(frame, event, argument):
    if event == 'return' and frame.f_code.co_filename == target_filename:
        for name, value in list(frame.f_locals.items()):
            if not name.startswith('__'):
                collect(value, frame.f_code.co_name + ':' + name)
        collect(argument, frame.f_code.co_name + ':return')

sys.setprofile(profile)
try:
    runpy.run_path(str(target), run_name='__main__')
finally:
    sys.setprofile(None)
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(found, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
'''


def inspect_runtime_records(uv: str, workspace: Path, meta: dict[str, Any], expected: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    probe = output.parent / (output.stem + "-runtime-probe.py")
    data = output.parent / (output.stem + "-runtime-data.json")
    header = "#!/usr/bin/env -S uv run --script\n# /// script\n"
    header += "# requires-python = " + json.dumps(meta.get("requires-python", ">=3.11")) + "\n"
    header += "# dependencies = " + json.dumps(meta.get("dependencies", [])) + "\n# ///\n"
    probe.parent.mkdir(parents=True, exist_ok=True)
    probe.write_text(header + RUNTIME_PROBE, encoding="utf-8")
    command = [uv, "run", "--script", str(probe.resolve()), str((workspace / "app.py").resolve()), str(data.resolve())]
    execution = execute(command, workspace)
    observations = json.loads(data.read_text(encoding="utf-8"))
    candidates = [nested for observation in observations for nested in nested_values(observation["value"])]
    if not retains_records(candidates, expected):
        raise ValueError("Executing app.py did not expose the complete original records in a data table or record sequence, including order and missing values.")
    return {"records": len(expected), "original_records_preserved": True, "inspected_values": len(observations), "evidence": str(data), "execution": execution}


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[dict[str, str]] = []
        self.active: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self.active = {key: value or "" for key, value in attrs}
            self.active["body"] = ""

    def handle_data(self, data: str) -> None:
        if self.active is not None:
            self.active["body"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.active is not None:
            self.scripts.append(self.active)
            self.active = None


def inspect_html(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    parser = ScriptCollector()
    parser.feed(text)
    json_values: list[Any] = []
    for script in parser.scripts:
        try:
            json_values.extend(nested_values(json.loads(script["body"])))
        except (ValueError, TypeError):
            pass
    xy_evidence = bool(re.search(r"xy|reflex", text, flags=re.I))
    if not parser.scripts:
        raise ValueError(f"{path.name} contains no interactive script.")
    if not xy_evidence:
        raise ValueError(f"{path.name} contains no xy runtime evidence.")
    return {"bytes": path.stat().st_size, "scripts": len(parser.scripts), "embedded_json_values": len(json_values)}


def inspect_svg(path: Path, labels: list[str]) -> dict[str, Any]:
    root = ET.parse(path).getroot()
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise ValueError(f"{path.name} is not an SVG document.")
    text = " ".join(" ".join(element.itertext()) for element in root.iter() if element.tag.rsplit("}", 1)[-1] == "text")
    normalized = " ".join(text.split())
    absent = [label for label in labels if label not in normalized]
    if absent:
        raise ValueError(f"{path.name} misses visible chart labels: {absent}")
    marks = [element for element in root.iter() if element.tag.rsplit("}", 1)[-1] in {"path", "circle", "rect", "line", "polygon", "polyline"}]
    if len(marks) < 8:
        raise ValueError(f"{path.name} has too few graphical elements for a chart.")
    return {"graphic_elements": len(marks), "text": normalized, "viewBox": root.get("viewBox")}


def inspect_png(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        image.load()
        if image.format != "PNG":
            raise ValueError(f"{path.name} is not a PNG image.")
        rgb = image.convert("RGB")
        width, height = rgb.size
        deviation = max(ImageStat.Stat(rgb).stddev)
        colors = len(rgb.resize((120, 120)).getcolors(14400) or [])
        if width < 320 or height < 220 or deviation < 5 or colors < 20:
            raise ValueError(f"{path.name} is too small or nearly blank: {width}x{height}, colors={colors}, stddev={deviation:.2f}.")
        return {"width": width, "height": height, "sample_colors": colors, "stddev": round(deviation, 3)}


def launch_browser(playwright, executable: str | None):
    attempts = [{"executable_path": executable}] if executable else [{}, {"channel": "msedge"}, {"channel": "chrome"}]
    errors = []
    for options in attempts:
        try:
            return playwright.chromium.launch(headless=True, args=["--allow-file-access-from-files"], **options)
        except Exception as error:
            errors.append(str(error).splitlines()[0])
    raise RuntimeError("No runnable Chromium browser was found: " + "; ".join(errors))


def inspect_browser(path: Path, labels: list[str], screenshot: Path, executable: str | None) -> dict[str, Any]:
    with sync_playwright() as playwright:
        browser = launch_browser(playwright, executable)
        context = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        page = context.new_page()
        remote: list[str] = []
        errors: list[str] = []

        def route_request(route):
            if route.request.url.startswith(("https://", "http://")):
                remote.append(route.request.url)
                route.abort()
            else:
                route.continue_()

        context.route("**/*", route_request)
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(path.resolve().as_uri(), wait_until="load", timeout=60000)
        page.wait_for_function("() => document.querySelector('svg, canvas') !== null", timeout=45000)
        page.wait_for_timeout(1500)
        text = " ".join(page.evaluate("""() => {
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            const visible = [];
            while (walker.nextNode()) {
                const node = walker.currentNode;
                const parent = node.parentElement;
                if (!parent || !node.textContent.trim() || parent.closest('script,style,template,noscript')) continue;
                const style = getComputedStyle(parent);
                if (style.visibility === 'hidden' || style.visibility === 'collapse' || parseFloat(style.fontSize) === 0) continue;
                let excluded = false;
                for (let ancestor = parent; ancestor; ancestor = ancestor.parentElement) {
                    const inherited = getComputedStyle(ancestor);
                    if (inherited.display === 'none' || parseFloat(inherited.opacity) === 0) {
                        excluded = true;
                        break;
                    }
                }
                if (excluded) continue;
                const range = document.createRange();
                range.selectNodeContents(node);
                if ([...range.getClientRects()].some(rect => rect.width > 0 && rect.height > 0)) {
                    visible.push(node.textContent);
                }
            }
            return visible.join(' ');
        }""").split())
        missing = [label for label in labels if label not in text]
        if missing:
            raise ValueError(f"Offline browser render misses visible labels: {missing}")
        if errors:
            raise ValueError(f"Offline browser JavaScript errors: {errors[:3]}")
        surfaces = page.locator("svg, canvas").count()
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot), full_page=True)
        page.mouse.move(480, 350)
        page.mouse.click(480, 350)
        page.wait_for_timeout(250)
        if errors:
            raise ValueError(f"Chart pointer interaction raised JavaScript errors: {errors[:3]}")
        context.close()
        browser.close()
    image = inspect_png(screenshot)
    return {"offline": True, "blocked_remote_requests": remote, "javascript_errors": errors, "surfaces": surfaces, "visible_text": text, "screenshot": str(screenshot), "image": image}


def check_boundary(text: str) -> dict[str, Any]:
    lower = text.lower()
    required_concepts = {
        "standalone delivery": ("offline", "standalone", "self-contained", "snapshot"),
        "Python callback": ("callback", "python handler", "python function"),
        "live execution": ("live", "kernel", "server", "backend", "notebook"),
        "tested status": ("tested", "verified", "executed", "checked"),
        "constraint": ("cannot", "can't", "won't", "does not", "do not", "will not", "requires", "require"),
    }
    missing = [name for name, words in required_concepts.items() if not any(word in lower for word in words)]
    if missing:
        raise ValueError(f"design.md omits required delivery concepts: {missing}")
    return {"words": len(text.split()), "delivery_concepts_present": list(required_concepts), "manual_review": "Confirm that the prose never claims an offline Python callback ran."}


def execute(command: list[str], workspace: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
    result = {"command": command, "returncode": completed.returncode, "stdout": completed.stdout[-12000:], "stderr": completed.stderr[-12000:]}
    if completed.returncode:
        raise ValueError("Regeneration failed: " + json.dumps(result))
    return result


def inspect(run: Path, case: str, output: Path, executable: str | None) -> dict[str, Any]:
    workspace = run / "workspace" if (run / "workspace").is_dir() else run
    prompt_path = run / "prompt.md" if (run / "prompt.md").is_file() else workspace.parent / "prompt.md"
    prompt = prompt_path.read_text(encoding="utf-8")
    result: dict[str, Any] = {"case": case, "workspace": str(workspace.resolve()), "checks": {}, "findings": []}
    checks = result["checks"]
    try:
        required = CASE_OUTPUTS[case]
        absent = [relative for relative in required if not (workspace / relative).is_file() or (workspace / relative).stat().st_size == 0]
        if absent:
            raise ValueError(f"Missing or empty exact outputs: {absent}")
        checks["initial_outputs"] = {relative: {"bytes": (workspace / relative).stat().st_size, "sha256": sha256(workspace / relative)} for relative in required}
        uv = shutil.which("uv")
        if not uv:
            raise RuntimeError("uv is required for independent regeneration.")
        if case == "contract":
            checks["regeneration"] = execute([uv, "run", "--script", "skills/reflex-xy/scripts/diagnose.py", "--output-dir", "artifacts/probe", "--report", "artifacts/probe.json"], workspace)
            report = json.loads((workspace / "artifacts/probe.json").read_text(encoding="utf-8"))
            if report.get("passed") is not True:
                raise ValueError("The regenerated diagnostic report does not have passed: true.")
            if report.get("xy_version") != "0.0.8" or report.get("backend") != "native":
                raise ValueError("The regenerated report did not observe native xy 0.0.8.")
            for name in ("chart.html", "chart.svg", "chart.png"):
                exported = workspace / "artifacts/probe" / name
                stated = report.get("files", {}).get(name, {})
                if stated.get("bytes") != exported.stat().st_size or stated.get("sha256") != sha256(exported):
                    raise ValueError(f"Diagnostic report bytes or SHA-256 differ from actual {name}.")
            checks["native_report"] = report
        else:
            source = (workspace / "app.py").read_text(encoding="utf-8")
            tree = ast.parse(source, filename="app.py")
            compile(tree, "app.py", "exec")
            meta = metadata(source)
            if "xy==0.0.8" not in meta.get("dependencies", []):
                raise ValueError("app.py must declare xy==0.0.8 in PEP 723 dependencies.")
            imports = [name.name for node in ast.walk(tree) if isinstance(node, ast.Import) for name in node.names]
            imports.extend(node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom))
            if not any(name == "xy" or name.startswith("xy.") for name in imports):
                raise ValueError("app.py does not import Python xy.")
            expected = prompt_records(prompt, case)
            checks["source"] = {"compiled": True, "xy_version": "0.0.8", "records": len(expected)}
            checks["regeneration"] = execute([uv, "run", "--script", "app.py"], workspace)
            checks["runtime_records"] = inspect_runtime_records(uv, workspace, meta, expected, output)
        labels = CASE_TEXT.get(case, [])
        for relative in required:
            path = workspace / relative
            if path.suffix == ".html":
                checks["html"] = inspect_html(path)
                screenshot = output.parent / (output.stem + "-browser.png")
                checks["browser"] = inspect_browser(path, labels, screenshot, executable)
            elif path.suffix == ".svg":
                checks["svg"] = inspect_svg(path, labels)
            elif path.suffix == ".png":
                checks["png"] = inspect_png(path)
        if case == "boundary":
            checks["design"] = check_boundary((workspace / "design.md").read_text(encoding="utf-8"))
        if case in {"naturalistic", "generalization"}:
            visible = checks["browser"]["visible_text"].lower()
            if "synthetic" not in visible and "fictional" not in visible:
                raise ValueError("The rendered HTML has no visible synthetic-data note.")
        if case == "generalization":
            visible = checks["browser"]["visible_text"].lower()
            if not any(word in visible for word in ("missing", "no measurement", "no observation", "not measured")):
                raise ValueError("The rendered HTML does not explain the missing measurement.")
        checks["final_outputs"] = {relative: {"bytes": (workspace / relative).stat().st_size, "sha256": sha256(workspace / relative)} for relative in required}
    except Exception as error:
        result["findings"].append(f"{type(error).__name__}: {error}")
    result["passed"] = not result["findings"]
    result["manual_review"] = "Inspect the screenshot and exported chart for readable layout, truthful data mapping, and native interaction quality. Boundary prose also requires semantic review."
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, help="Isolated run directory, or its workspace.")
    parser.add_argument("--case", choices=CASE_OUTPUTS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--browser-executable", help="Optional Chromium, Edge, or Chrome executable.")
    args = parser.parse_args()
    result = inspect(args.run.resolve(), args.case, args.output.resolve(), args.browser_executable)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "case": args.case, "findings": result["findings"], "output": str(args.output)}, ensure_ascii=False))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

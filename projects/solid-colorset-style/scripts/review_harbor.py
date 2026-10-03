#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52"]
# ///
"""Check computed Harbor badge contrast and numeric gutters on actual SVG output."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "projects/solid-colorset-style/artifacts"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    spec = importlib.util.spec_from_file_location("harbor_fixture", ROOT / "skills/harbor-author-evaluation-datasets/scripts/test_consolidate_harbor_reports.py")
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    source = fixture.report()
    source["jobs"] = [fixture.report(f"run-{index}")["jobs"][0] for index in range(24)]
    first = source["jobs"][0]["summary"]
    first.update(erroredTrials=1, verifierFailedTrials=0)
    last = source["jobs"][-1]["summary"]
    last.update(passedTrials=2, verifierFailedTrials=0, passRate=1.0,
                reward=fixture.metric(2, 2.0))
    folder = ART / "harbor-browser"
    folder.mkdir(parents=True, exist_ok=True)
    input_path = folder / "final-report.json"
    input_path.write_text(json.dumps(source) + "\n", encoding="utf-8")
    command = [sys.executable, "skills/harbor-author-evaluation-datasets/scripts/consolidate_harbor_reports.py",
               str(input_path), "--output-dir", str(folder / "comparison"), "--overwrite"]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    states = []
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch()
            page = browser.new_page(viewport={"width": 1700, "height": 1100})
            for name in ("quality-comparison.svg", "resource-comparison.svg", "efficiency-frontier.svg"):
                artifact = folder / "comparison" / name
                page.goto(f"http://127.0.0.1:{server.server_port}/" + artifact.relative_to(ROOT).as_posix())
                state = page.evaluate(r'''() => {
                  const text = [...document.querySelectorAll('text')];
                  const nonBinary = text.filter(n => !['rgb(0, 0, 0)','rgb(255, 255, 255)'].includes(getComputedStyle(n).fill)).map(n => n.textContent);
                  const badges = [...document.querySelectorAll('.on-error')].map(n => ({text:n.textContent,paint:getComputedStyle(n).fill}));
                  const marks = [...document.querySelectorAll('rect[height="24"][fill]')].filter(n => n.getAttribute('fill') !== '#e7e7e7');
                  const values = [...document.querySelectorAll('text.value')];
                  const overlaps = [];
                  for(const a of values)for(const b of marks){const x=a.getBoundingClientRect(),y=b.getBoundingClientRect();if(Math.min(x.right,y.right)>Math.max(x.left,y.left)&&Math.min(x.bottom,y.bottom)>Math.max(x.top,y.top))overlaps.push(a.textContent)}
                  const circles = [...document.querySelectorAll('circle')];
                  return {nonBinary,badges,overlaps,circleColors:[...new Set(circles.map(n => getComputedStyle(n).fill))],outlinedCircles:circles.filter(n=>getComputedStyle(n).stroke!=='none').length};
                }''')
                state["artifact"] = artifact.relative_to(ROOT).as_posix()
                states.append(state)
                page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
                screenshots = ART / "screenshots"
                screenshots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(screenshots / ("harbor-" + name + ".png")))
            browser.close()
    finally:
        server.shutdown()
    findings = [row for row in states if row["nonBinary"] or row["overlaps"] or row["outlinedCircles"] or any(badge["paint"] != "rgb(255, 255, 255)" for badge in row["badges"])]
    if len(states[0]["badges"]) != 1 or len(states[2]["circleColors"]) != 24:
        findings.append({"error": "Badge or maximum category capacity was not exercised"})
    report = {"date": "2026-10-03", "passed": not findings, "command": command,
              "states": states, "findings": findings, "scope": "Actual CSS cascade, 24 unique borderless categories, and non-overlapping numeric labels; one explicit error badge and a 100 percent row."}
    target = ROOT / "evaluations/solid-colorset-style/harbor-browser-20261003.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": report["passed"], "states": len(states), "findings": findings}, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()

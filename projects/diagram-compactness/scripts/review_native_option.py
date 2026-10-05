#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Render a trial's native option and requalify actual browser resize states."""
from functools import partial
from http.server import ThreadingHTTPServer
import argparse
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

from review_native_deck import SpaHandler, SNAPSHOT

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run_id")
args = parser.parse_args()
workspace = ROOT / "evaluations/runs" / args.run_id / "workspace"
workspace.resolve().relative_to(ROOT)
out = ROOT / "projects/diagram-compactness/artifacts/reviews" / args.run_id / "independent-native"
out.mkdir(parents=True, exist_ok=True)
assert (workspace / "node_modules/echarts/dist/echarts.esm.mjs").is_file()
server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SpaHandler, directory=str(workspace)))
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
result = {"run": args.run_id, "states": [], "pageErrors": []}
try:
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda error: result["pageErrors"].append(str(error)))
        page.goto(f"http://127.0.0.1:{server.server_port}/deliverables/graph-option.json")
        page.evaluate("document.body.innerHTML='<div id=chart style=\"width:640px;height:360px\"></div>'")
        page.evaluate("""async () => {
          const echarts=await import('/node_modules/echarts/dist/echarts.esm.mjs');
          const helpers=await import('/skills/slidev-echarts/assets/templates/echarts-colorsets.mjs');
          const option=await (await fetch('/deliverables/graph-option.json')).json();
          window.chart=echarts.init(document.getElementById('chart'),null,{renderer:'svg'});
          window.original=option;window.clearance=helpers.insetGraphArrowRoutes;
          window.settle=async()=>{await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));chart.getZr().refreshImmediately();return clearance(chart,3)};
          chart.setOption(structuredClone(option));
        }""")
        for name, width, height in [("delivery", 640, 360), ("resized", 800, 450), ("restored", 640, 360)]:
            page.evaluate("([w,h])=>{const el=document.getElementById('chart');el.style.width=w+'px';el.style.height=h+'px';chart.resize({width:w,height:h});chart.setOption(structuredClone(original),true)}", [width, height])
            helper = page.evaluate("settle()")
            repeat = page.evaluate("settle()")
            proof = page.evaluate(SNAPSHOT.replace("length>=6", "length>=3"))
            proof.update({"state": name, "helper": helper, "repeat": repeat})
            result["states"].append(proof)
            page.screenshot(path=str(out / f"live-option-{name}.png"), animations="disabled")
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=10)
result["findings"] = []
for state in result["states"]:
    if len(state["graphs"]) != 1:
        result["findings"].append({"state": state["state"], "issue": "Missing live graph"})
    if state["repeat"]["adjustedEdges"]:
        result["findings"].append({"state": state["state"], "issue": "Unstable repeated inset"})
    for graph in state["graphs"]:
        if graph["textOverlaps"] or len(graph["nodes"]) != 3 or len(graph["heads"]) != 2:
            result["findings"].append({"state": state["state"], "issue": "Incorrect live text/body/head geometry"})
        for head in graph["heads"]:
            if head["gap"] < 2.4:
                result["findings"].append({"state": state["state"], "issue": "Head overlaps body", "head": head})
result["ok"] = not result["pageErrors"] and not result["findings"]
(out / "live-option-browser.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps({"ok": result["ok"], "run": args.run_id, "pageErrors": result["pageErrors"], "findings": result["findings"]}))
raise SystemExit(0 if result["ok"] else 1)

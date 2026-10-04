#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55"]
# ///
"""Review actual isolated categorical SVG or Three.js browser surfaces."""
from __future__ import annotations
import argparse
import functools
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from validate_artifacts import EXPECTED, LABELS, contrast, text_on


SVG_PROBE = r'''({labels,selector='svg'}) => {
 const hex = value => { const m=value.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)$/); return m?'#'+m.slice(1).map(c=>Number(c).toString(16).padStart(2,'0')).join(''):value.toLowerCase(); };
 const svg=document.querySelector(selector);
 const textNodes=Array.from(svg?.querySelectorAll('text,foreignObject')||[]);
 const shapes=Array.from(svg?.querySelectorAll('rect,circle,ellipse,polygon,path')||[]).filter(e=>!e.closest('defs,clipPath,mask')&&e.getBoundingClientRect().width*e.getBoundingClientRect().height>300);
 const rows=labels.map((label,index)=>{
   const text=textNodes.find(e=>e.textContent.trim()===label);
   if(!text)return {index,label,error:'missing actual label'};
   const b=text.getBoundingClientRect(),point={x:b.x+b.width/2,y:b.y+b.height/2};
   const candidates=shapes.filter(e=>{const cs=getComputedStyle(e),b=e.getBoundingClientRect();if(cs.fill==='none'||point.x<b.x||point.x>b.right||point.y<b.y||point.y>b.bottom)return false;
     if(typeof e.isPointInFill==='function'){const p=new DOMPoint(point.x,point.y).matrixTransform(e.getScreenCTM().inverse());return e.isPointInFill(p);}return true;});
   const body=candidates.at(-1);if(!body)return {index,label,error:'no painted body under label'};
   const cs=getComputedStyle(body),labelElement=text.tagName==='foreignObject'?(text.querySelector('*')||text):text,ls=getComputedStyle(labelElement);
   return {index,label,fill:hex(cs.fill),text:hex(text.tagName==='foreignObject'?ls.color:ls.fill),stroke:hex(cs.stroke),strokeWidth:Number.parseFloat(cs.strokeWidth),opacity:Number(cs.opacity)*Number(cs.fillOpacity),bounds:{x:b.x,y:b.y,width:b.width,height:b.height},bodyTag:body.tagName};
 });
 const paints=Array.from(svg?.querySelectorAll('rect,circle,ellipse,polygon,path')||[]).filter(e=>!e.closest('defs,clipPath,mask')).map(e=>{const cs=getComputedStyle(e);return {tag:e.tagName,fill:hex(cs.fill),stroke:hex(cs.stroke),opacity:Number(cs.opacity)*Number(cs.fillOpacity),area:e.getBoundingClientRect().width*e.getBoundingClientRect().height};});
 return {rows,paints,svgCount:document.querySelectorAll('svg').length,overflow:document.documentElement.scrollWidth>innerWidth+1};
}'''


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    run = root / "evaluations/runs" / args.run_id
    manifest = json.loads((run / "run-manifest.json").read_text(encoding="utf-8"))
    workspace = run / "workspace"
    skill = manifest["skill"]["name"]
    artifacts = run / "browser-review"
    artifacts.mkdir(exist_ok=True)
    handler = functools.partial(QuietHandler, directory=str(workspace))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    findings, surfaces = [], []
    contract = (workspace / "contract.json").is_file()
    white = [paint for paint in EXPECTED if paint != "#ffffff"]
    dark = [paint for paint in EXPECTED if paint != "#000000"]
    group_labels = [f"Group {i}" for i in range(17)]
    routes = []
    if skill == "d3":
        routes = [{"file": "contract.html", "labels": group_labels, "canvas": canvas, "selector": f"svg[data-canvas='{canvas}']"} for canvas in ("#ffffff", "#000000")] if contract else [{"file": "priority.html", "labels": LABELS, "canvas": "#ffffff"}]
    elif skill == "mermaid":
        routes = [{"file": "priority.svg", "labels": group_labels if contract else LABELS, "canvas": "#ffffff"}]
    elif skill in {"echarts-animated-svg", "slidev-echarts"}:
        routes = [{"file": file, "labels": group_labels, "canvas": canvas} for file, canvas in (("priority.white.static.svg", "#ffffff"), ("priority.dark.static.svg", "#000000"))] if contract else [{"file": "priority.static.svg", "labels": LABELS, "canvas": "#ffffff"}]
    elif skill == "threejs-animated-3d":
        routes = [{"file": "priority.html"}]
    elif skill == "plantuml-colorset-renderer":
        routes = [{"file": "renders/priority.svg", "labels": ["Intake", "Review", "Record", "Archive"], "expected": ["#9e1b32", "#9e1b32", "#333e48", "#4f4f4f"]}]
        if (workspace / "renders/layers.svg").is_file():
            routes.append({"file": "renders/layers.svg", "labels": ["Business", "Application", "Technology", "Motivation", "Strategy", "Physical", "Implementation"], "expected": EXPECTED[:7]})
    elif skill in {"procedural-svg-animation", "compose-synchronized-svg", "vectorize-art-patterns"}:
        routes = [{"file": "bailly.svg" if skill == "vectorize-art-patterns" else "priority.svg", "labels": []}]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=True)
        for viewport in ({"width": 1440, "height": 900}, {"width": 390, "height": 844}):
            for route in routes:
                page = browser.new_page(viewport=viewport, reduced_motion="reduce")
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"http://127.0.0.1:{server.server_port}/{route['file']}", wait_until="networkidle")
                page.wait_for_timeout(300)
                if skill == "threejs-animated-3d":
                    page.wait_for_function("window.__threeRuntimeSceneReady === true")
                    state = page.evaluate("() => {window.__threeRuntimeScene.renderAt(0); return window.__threeRuntimeScene.inspect();}")
                    colors = state.get("materialColors", [])
                    solids = [paint for paint in EXPECTED if paint not in {"#ffffff", "#9e1b32"}]
                    expected = ["#9e1b32"] + [solids[index % len(solids)] for index in range(state.get("tokenCount", 0))]
                    if colors != expected:
                        findings.append({"viewport": viewport, "message": "actual hub/token materials differ from reserved-primary category order", "observed": colors, "expected": expected})
                    if state.get("decorativeOutlineCount") != 0:
                        findings.append({"viewport": viewport, "message": "native material scene has decorative edge meshes"})
                    if any(paint != "#ffffff" for paint in state.get("lightColors", [])):
                        findings.append({"viewport": viewport, "message": "scene lighting tints category materials"})
                else:
                    state = page.evaluate(SVG_PROBE, {"labels": route["labels"], "selector": route.get("selector", "svg")})
                    solids = route.get("expected", dark if route.get("canvas") == "#000000" else white)
                    for row in state["rows"]:
                        index = row["index"]
                        expected = solids[index % len(solids)]
                        if "error" in row:
                            findings.append({"viewport": viewport, **row})
                            continue
                        if row["fill"] != expected or row["text"] != text_on(expected) or row["opacity"] != 1:
                            findings.append({"viewport": viewport, "message": "actual body/inside-text/opacity differ from priority", **row, "expectedFill": expected, "expectedText": text_on(expected)})
                        if index < len(solids) and row["stroke"] != "none" and row["strokeWidth"] > 0:
                            findings.append({"viewport": viewport, "message": "first-cycle decorative outline", **row})
                        if index >= len(solids) and (row["stroke"] == "none" or row["strokeWidth"] <= 0 or contrast(expected, row["stroke"]) < 3):
                            findings.append({"viewport": viewport, "message": "overflow variant lacks a readable boundary", **row})
                if errors:
                    findings.append({"viewport": viewport, "message": "browser page errors", "errors": errors})
                screenshot = artifacts / f"{viewport['width']}-{len(surfaces)}.png"
                page.screenshot(path=str(screenshot), full_page=False, animations="disabled", timeout=15000)
                surfaces.append({"viewport": viewport, "route": route["file"], "state": state, "errors": errors, "screenshot": str(screenshot.relative_to(run))})
                page.close()
        browser.close()
    server.shutdown()
    result = {"schemaVersion": 1, "runId": args.run_id, "skill": skill, "payloadSha256": manifest["skill"]["payloadSha256"], "passed": bool(surfaces) and not findings, "surfaces": surfaces, "findings": findings, "directScreenshotReviewPending": True}
    output = run / "browser-review.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runId": args.run_id, "passed": result["passed"], "surfaceCount": len(surfaces), "findings": findings, "output": str(output)}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

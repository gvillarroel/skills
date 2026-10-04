#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55"]
# ///
"""Review actual isolated categorical SVG or Three.js browser surfaces."""
from __future__ import annotations
import argparse
import functools
import hashlib
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
 const shapes=Array.from(svg?.querySelectorAll('rect,circle,ellipse,polygon,path')||[]).filter(e=>{if(e.closest('defs,clipPath,mask'))return false;const b=e.getBBox(),m=e.getCTM(),area=b.width*b.height;return area>300||area*Math.abs(m.a*m.d-m.b*m.c)>300;});
 const rows=labels.map((label,index)=>{
   const text=textNodes.find(e=>e.textContent.trim()===label);
   if(!text)return {index,label,error:'missing actual label'};
   const b=text.getBoundingClientRect(),point={x:b.x+b.width/2,y:b.y+b.height/2};
   const candidates=shapes.filter(e=>{const cs=getComputedStyle(e),b=e.getBoundingClientRect();if(cs.fill==='none'||point.x<b.x||point.x>b.right||point.y<b.y||point.y>b.bottom)return false;
     if(typeof e.isPointInFill==='function'){const p=new DOMPoint(point.x,point.y).matrixTransform(e.getScreenCTM().inverse());return e.isPointInFill(p);}return true;});
   const body=candidates.at(-1);if(!body)return {index,label,error:'no painted body under label'};
   const cs=getComputedStyle(body),labelElement=text.tagName==='foreignObject'?(text.querySelector('*')||text):text,ls=getComputedStyle(labelElement);
   const bb=body.getBoundingClientRect();
   return {index,label,fill:hex(cs.fill),text:hex(text.tagName==='foreignObject'?ls.color:ls.fill),stroke:hex(cs.stroke),strokeWidth:Number.parseFloat(cs.strokeWidth),opacity:Number(cs.opacity)*Number(cs.fillOpacity),bounds:{x:b.x,y:b.y,width:b.width,height:b.height},bodyBounds:{x:bb.x,y:bb.y,width:bb.width,height:bb.height},bodyTag:body.tagName};
 });
 const paints=Array.from(svg?.querySelectorAll('rect,circle,ellipse,polygon,path')||[]).filter(e=>!e.closest('defs,clipPath,mask')).map(e=>{const cs=getComputedStyle(e);return {tag:e.tagName,fill:hex(cs.fill),stroke:hex(cs.stroke),opacity:Number(cs.opacity)*Number(cs.fillOpacity),area:e.getBoundingClientRect().width*e.getBoundingClientRect().height};});
 const nativePaths=Array.from(svg?.querySelectorAll('path[ecmeta_series_index][ecmeta_data_index]')||[]).filter(e=>getComputedStyle(e).fill!=='none');
 const graphBodies=nativePaths.filter(e=>{const b=e.getBoundingClientRect();return b.width*b.height>300;});
 const arrowHeads=nativePaths.filter(e=>{const b=e.getBoundingClientRect();return b.width*b.height>0&&b.width*b.height<=300;}).map(head=>{
   const h=head.getBoundingClientRect(),sourceIndex=head.getAttribute('ecmeta_data_index');
   const comparisons=graphBodies.filter(body=>body.getAttribute('ecmeta_data_index')!==sourceIndex).map(body=>{const b=body.getBoundingClientRect(),dx=Math.max(b.x-h.right,h.x-b.right,0),dy=Math.max(b.y-h.bottom,h.y-b.bottom,0);return {targetIndex:Number(body.getAttribute('ecmeta_data_index')),clearance:Math.hypot(dx,dy),wholeHeadBoundsInsideBodyBounds:h.x>=b.x&&h.right<=b.right&&h.y>=b.y&&h.bottom<=b.bottom,targetBounds:{x:b.x,y:b.y,width:b.width,height:b.height}};});
   const cs=getComputedStyle(head);
   return {sourceIndex:Number(sourceIndex),fill:hex(cs.fill),opacity:Number(cs.opacity)*Number(cs.fillOpacity),headBounds:{x:h.x,y:h.y,width:h.width,height:h.height},closestTarget:comparisons.sort((a,b)=>a.clearance-b.clearance)[0]};
 });
 const arrowShafts=Array.from(svg?.querySelectorAll('path[ecmeta_series_index][ecmeta_data_index]')||[]).filter(e=>getComputedStyle(e).fill==='none').map(e=>{const cs=getComputedStyle(e);return {stroke:hex(cs.stroke),opacity:Number(cs.opacity)*Number(cs.strokeOpacity),strokeWidth:Number.parseFloat(cs.strokeWidth)};});
 const sb=svg.getBoundingClientRect();
 return {rows,paints,arrowHeads,arrowShafts,svgBounds:{x:sb.x,y:sb.y,width:sb.width,height:sb.height},svgCount:document.querySelectorAll('svg').length,overflow:document.documentElement.scrollWidth>innerWidth+1};
}'''


BOXPLOT_PROBE = r'''({values}) => {
 const hex=value=>{const m=value.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return m?'#'+m.slice(1).map(c=>Number(c).toString(16).padStart(2,'0')).join(''):value.toLowerCase();};
 const primitives=Array.from(document.querySelectorAll('svg path,svg rect,svg polygon,svg polyline,svg line')).filter(e=>!e.closest('defs,clipPath,mask'));
 const inkAt=(x,y)=>{let ink='none';for(const e of primitives){const cs=getComputedStyle(e),p=new DOMPoint(x,y).matrixTransform(e.getScreenCTM().inverse());if(cs.fill!=='none'&&typeof e.isPointInFill==='function'&&e.isPointInFill(p))ink=hex(cs.fill);if(cs.stroke!=='none'&&typeof e.isPointInStroke==='function'&&e.isPointInStroke(p))ink=hex(cs.stroke);}return ink;};
 return {boxes:Array.from(document.querySelectorAll('path[ecmeta_series_index][ecmeta_data_index]')).filter(e=>getComputedStyle(e).fill!=='none').map(e=>{const cs=getComputedStyle(e),b=e.getBoundingClientRect(),series=Number(e.getAttribute('ecmeta_series_index')),dataIndex=Number(e.getAttribute('ecmeta_data_index')),stats=values[series][dataIndex],medianY=b.y+(stats[4]-stats[2])/(stats[4]-stats[0])*b.height,medianSamples=[.25,.5,.75].map(fraction=>({x:b.x+b.width*fraction,y:medianY,paint:inkAt(b.x+b.width*fraction,medianY)}));return {series,dataIndex,fill:hex(cs.fill),stroke:hex(cs.stroke),opacity:Number(cs.opacity)*Number(cs.fillOpacity),area:b.width*b.height,path:e.getAttribute('d'),medianSamples};})};
}'''


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    parser.add_argument("--semantic-role-review", action="store_true", help="Supplemental post-sampling review for a same-role native Mermaid chain; preserves the original indexed oracle record.")
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
        if (workspace / "boxplot.white.static.svg").is_file():
            routes.extend({"file": file, "canvas": canvas, "boxplot": True} for file, canvas in (("boxplot.white.static.svg", "#ffffff"), ("boxplot.dark.static.svg", "#000000")))
    elif skill == "threejs-animated-3d":
        routes = [{"file": "priority.html"}]
    elif skill == "plantuml-colorset-renderer":
        routes = [{"file": "renders/svg/priority.svg", "labels": ["Intake", "Review", "Record", "Archive"], "expected": ["#9e1b32", "#9e1b32", "#333e48", "#4f4f4f"]}]
        if (workspace / "renders/svg/layers.svg").is_file():
            routes.append({"file": "renders/svg/layers.svg", "labels": ["Business", "Application", "Technology", "Motivation", "Strategy", "Physical", "Implementation"], "expected": EXPECTED[:7]})
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
                elif route.get("boxplot"):
                    state = page.evaluate(BOXPLOT_PROBE, {"values": [[[1,2,3,4,5],[2,3,4,5,6]],[[2,3,4,5,6],[3,4,5,6,7]]]})
                    boxes = state["boxes"]
                    if [(box["series"], box["dataIndex"]) for box in boxes] != [(0, 0), (0, 1), (1, 0), (1, 1)]:
                        findings.append({"viewport": viewport, "message": "native default boxplot bodies are missing or reordered", "boxes": boxes})
                    for box in boxes:
                        expected = EXPECTED[box["series"]]
                        if box["fill"] != expected or box["stroke"] != expected or box["opacity"] != 1 or box["area"] <= 300 or "Z" not in box["path"]:
                            findings.append({"viewport": viewport, "message": "native default boxplot category body or semantic statistical strokes differ", **box, "expectedFill": expected})
                        if any(sample["paint"] != text_on(expected) for sample in box["medianSamples"]):
                            findings.append({"viewport": viewport, "message": "native boxplot median is not visible in independent maximum-contrast black/white ink", **box, "expectedMedianInk": text_on(expected)})
                    state["hoverMedianObservations"] = []
                    for box in boxes:
                        body = page.locator(f'path[ecmeta_series_index="{box["series"]}"][ecmeta_data_index="{box["dataIndex"]}"]')
                        bounds = body.bounding_box()
                        if bounds is None:
                            findings.append({"viewport": viewport, "message": "native boxplot hover body has no bounds", **box})
                            continue
                        page.mouse.move(bounds["x"] + bounds["width"] * .25, bounds["y"] + bounds["height"] * .4)
                        page.wait_for_timeout(50)
                        hovered = page.evaluate(BOXPLOT_PROBE, {"values": [[[1,2,3,4,5],[2,3,4,5,6]],[[2,3,4,5,6],[3,4,5,6,7]]]})
                        observation = next((row for row in hovered["boxes"] if row["series"] == box["series"] and row["dataIndex"] == box["dataIndex"]), None)
                        state["hoverMedianObservations"].append(observation)
                        if observation is None or observation["fill"] not in EXPECTED or observation["opacity"] != 1 or observation["path"] != box["path"] or any(sample["paint"] != text_on(observation["fill"]) for sample in observation["medianSamples"]):
                            findings.append({"viewport": viewport, "message": "native boxplot hover median loses qualified ink or changes native statistical geometry", "resting": box, "hovered": observation})
                        page.mouse.move(0, 0)
                else:
                    state = page.evaluate(SVG_PROBE, {"labels": route["labels"], "selector": route.get("selector", "svg")})
                    if skill == "d3" and not contract and state["overflow"]:
                        findings.append({"viewport": viewport, "message": "naturalistic offline catalogue overflows its requested responsive viewport"})
                    if skill in {"echarts-animated-svg", "slidev-echarts"}:
                        if not state["arrowHeads"]:
                            findings.append({"viewport": viewport, "message": "native directed graph arrowhead is absent"})
                        for head in state["arrowHeads"]:
                            nearest = head.get("closestTarget")
                            if nearest is None or nearest["clearance"] < 3:
                                findings.append({"viewport": viewport, "message": "full native graph arrowhead lacks three-pixel two-dimensional target clearance", **head})
                            if head["opacity"] != 1 or contrast(head["fill"], route["canvas"]) < 3:
                                findings.append({"viewport": viewport, "message": "actual native graph arrowhead lacks opaque three-to-one canvas contrast", **head})
                        if not state["arrowShafts"]:
                            findings.append({"viewport": viewport, "message": "actual native graph arrow shaft is absent"})
                        for shaft in state["arrowShafts"]:
                            if shaft["opacity"] != 1 or shaft["strokeWidth"] <= 0 or contrast(shaft["stroke"], route["canvas"]) < 3:
                                findings.append({"viewport": viewport, "message": "actual native graph arrow shaft lacks opaque three-to-one canvas contrast", **shaft})
                    solids = route.get("expected", dark if route.get("canvas") == "#000000" else white)
                    first_used = []
                    for row in state["rows"]:
                        index = row["index"]
                        expected = row.get("fill") if args.semantic_role_review else solids[index % len(solids)]
                        if "error" in row:
                            findings.append({"viewport": viewport, **row})
                            continue
                        if skill == "d3" and not contract:
                            body, svg_bounds = row["bodyBounds"], state["svgBounds"]
                            if body["x"] < svg_bounds["x"] - 1 or body["y"] < svg_bounds["y"] - 1 or body["x"] + body["width"] > svg_bounds["x"] + svg_bounds["width"] + 1 or body["y"] + body["height"] > svg_bounds["y"] + svg_bounds["height"] + 1:
                                findings.append({"viewport": viewport, "message": "requested responsive catalogue clips a native tile outside its SVG viewport", **row, "svgBounds": svg_bounds})
                        if args.semantic_role_review:
                            if expected not in EXPECTED:
                                findings.append({"viewport": viewport, "message": "semantic role uses paint outside Colorset 1", **row})
                                continue
                            if expected not in first_used:
                                first_used.append(expected)
                        if row["fill"] != expected or row["text"] != text_on(expected) or row["opacity"] != 1:
                            findings.append({"viewport": viewport, "message": "actual body/inside-text/opacity differ from priority", **row, "expectedFill": expected, "expectedText": text_on(expected)})
                        if index < len(solids) and row["stroke"] != "none" and row["strokeWidth"] > 0 and (not args.semantic_role_review or row["stroke"] != row["fill"]):
                            findings.append({"viewport": viewport, "message": "first-cycle decorative outline", **row})
                        if not args.semantic_role_review and index >= len(solids) and (row["stroke"] == "none" or row["strokeWidth"] <= 0 or contrast(expected, row["stroke"]) < 3):
                            findings.append({"viewport": viewport, "message": "overflow variant lacks a readable boundary", **row})
                    if args.semantic_role_review and first_used != solids[:len(first_used)]:
                        findings.append({"viewport": viewport, "message": "first use of distinct semantic role paints differs from priority", "firstUsed": first_used})
                if errors:
                    findings.append({"viewport": viewport, "message": "browser page errors", "errors": errors})
                screenshot = artifacts / f"{viewport['width']}-{len(surfaces)}.png"
                page.screenshot(path=str(screenshot), full_page=False, animations="disabled", timeout=15000)
                surfaces.append({"viewport": viewport, "route": route["file"], "state": state, "errors": errors, "screenshot": str(screenshot.relative_to(run))})
                page.close()
        browser.close()
    server.shutdown()
    result = {"schemaVersion": 2, "runId": args.run_id, "skill": skill, "reviewerSha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "payloadSha256": manifest["skill"]["payloadSha256"], "reviewMode": "supplemental-post-sampling-semantic-reuse" if args.semantic_role_review else "literal-indexed-slot", "passed": bool(surfaces) and not findings, "surfaces": surfaces, "findings": findings, "directScreenshotReviewPending": True}
    output = run / ("semantic-role-review.json" if args.semantic_role_review else "browser-review-v2.json")
    if output.exists():
        previous = output.with_name(output.stem + ".previous.json")
        if not previous.exists():
            previous.write_bytes(output.read_bytes())
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runId": args.run_id, "passed": result["passed"], "surfaceCount": len(surfaces), "findingCount": len(findings), "output": str(output)}))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

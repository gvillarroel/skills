#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Inspect a built native ECharts Slidev deck at real click/resize states."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import importlib.util
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('native_qualification', ROOT / 'skills/slidev-echarts/scripts/qualify_concept_graph.py')
ORACLE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ORACLE)


class SpaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not Path(self.translate_path(self.path)).exists() and not self.path.startswith("/assets/"):
            self.path = "/"
        super().do_GET()

    def log_message(self, *args):
        pass


SNAPSHOT = """() => {
  const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
  const opacity=e=>{let a=1;for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);a*=Number(s.opacity);if(s.display==='none'||s.visibility==='hidden')return 0}return a};
  const graphs=[...document.querySelectorAll('svg')].filter(e=>e.getBoundingClientRect().width>250&&opacity(e)>.01&&e.querySelectorAll('text').length>=6);
  return {url:location.href,viewport:{width:innerWidth,height:innerHeight},graphs:graphs.map(svg=>{
    const inverse=svg.getScreenCTM().inverse(),quad=e=>{const b=e.getBBox(),m=inverse.multiply(e.getScreenCTM());return [[b.x,b.y],[b.x+b.width,b.y],[b.x+b.width,b.y+b.height],[b.x,b.y+b.height]].map(([x,y])=>[m.a*x+m.c*y+m.e,m.b*x+m.d*y+m.f])};
    const bounds=e=>{const r=rect(e),s=rect(svg);return {x:r.x-s.x,y:r.y-s.y,width:r.width,height:r.height}};
    const pathEls=[...svg.querySelectorAll('path')];
    const nodes=pathEls.filter(e=>{const b=e.getBBox();return getComputedStyle(e).fill!=='none'&&b.width<=3&&b.height<=3&&opacity(e)>.01&&!e.getAttribute('d').startsWith('M0 0L')}).map(e=>({bounds:bounds(e),quad:quad(e),fill:getComputedStyle(e).fill}));
    const gap=(a,b)=>Math.hypot(Math.max(b.x-a.x-a.width,a.x-b.x-b.width,0),Math.max(b.y-a.y-a.height,a.y-b.y-b.height,0));
    const heads=pathEls.filter(e=>e.getAttribute('d').startsWith('M0 0L')&&opacity(e)>.01).map(e=>({bounds:bounds(e),gap:Math.min(...nodes.map(n=>gap(bounds(e),n.bounds))),opacity:opacity(e),fill:getComputedStyle(e).fill}));
    const labels=[...svg.querySelectorAll('text')].filter(e=>opacity(e)>.01).map(e=>({text:e.textContent,bounds:bounds(e),quad:quad(e),fontSize:parseFloat(getComputedStyle(e).fontSize),opacity:opacity(e)}));
    const shafts=pathEls.filter(e=>getComputedStyle(e).fill==='none'&&parseFloat(getComputedStyle(e).strokeWidth)>0&&opacity(e)>.01).map(e=>{const m=inverse.multiply(e.getScreenCTM()),length=e.getTotalLength(),points=[];for(let i=0;i<=240;i++){const p=e.getPointAtLength(length*i/240);points.push([m.a*p.x+m.c*p.y+m.e,m.b*p.x+m.d*p.y+m.f])}return {points,width:parseFloat(getComputedStyle(e).strokeWidth)}});
    const headQuads=pathEls.filter(e=>e.getAttribute('d').startsWith('M0 0L')&&opacity(e)>.01).map(quad);
    const overlaps=[];
    for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){const a=labels[i].bounds,b=labels[j].bounds,w=Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x),h=Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y);if(w>1&&h>1)overlaps.push({a:labels[i].text,b:labels[j].text,width:w,height:h})}
    return {bounds:rect(svg),viewBox:svg.getAttribute('viewBox'),labels,nodes,heads,shafts,headQuads,textOverlaps:overlaps};
  }),buttons:[...document.querySelectorAll('button')].filter(e=>opacity(e)>.01).map(e=>({text:e.textContent.trim(),title:e.getAttribute('title'),'aria-label':e.getAttribute('aria-label')}))};
}"""


RELATIONSHIPS = {'Retest': ('Review', 'Analyze'), 'Failed sample': ('Analyze', 'Quarantine')}


def attribute_caption_roles(graph: dict) -> None:
    """Conservatively associate this known prompt's glyphs with directed routes."""
    def rectangle(quad):
        x, y = min(p[0] for p in quad), min(p[1] for p in quad)
        return x, y, max(p[0] for p in quad), max(p[1] for p in quad)

    def distance(point, rect):
        return (max(rect[0] - point[0], point[0] - rect[2], 0) ** 2 + max(rect[1] - point[1], point[1] - rect[3], 0) ** 2) ** .5

    node_roles = {}
    for word in ['Receive', 'Barcode', 'Analyze', 'Review', 'Archive', 'Quarantine']:
        matches = [label for label in graph['labels'] if label['text'] == word]
        if len(matches) != 1:
            continue
        center = [sum(p[axis] for p in matches[0]['quad']) / 4 for axis in [0, 1]]
        bodies = [rectangle(node['quad']) for node in graph['nodes'] if distance(center, rectangle(node['quad'])) < .1]
        if len(bodies) == 1:
            node_roles[word] = bodies[0]
    for label in graph['labels']:
        label['relationshipRole'] = None
        if label['text'] not in RELATIONSHIPS:
            continue
        source, target = RELATIONSHIPS[label['text']]
        if source not in node_roles or target not in node_roles:
            continue
        routes = [shaft for shaft in graph['shafts'] if distance(shaft['points'][0], node_roles[source]) < 4 and distance(shaft['points'][-1], node_roles[target]) <= 25]
        if len(routes) != 1:
            continue
        center = [sum(p[axis] for p in label['quad']) / 4 for axis in [0, 1]]
        nearest = None
        points = routes[0]['points']
        for i, (a, b) in enumerate(zip(points, points[1:])):
            dx, dy = b[0] - a[0], b[1] - a[1]
            denominator = dx * dx + dy * dy
            t = max(0, min(1, ((center[0] - a[0]) * dx + (center[1] - a[1]) * dy) / denominator)) if denominator else 0
            gap = ((center[0] - a[0] - t * dx) ** 2 + (center[1] - a[1] - t * dy) ** 2) ** .5
            if nearest is None or gap < nearest[0]:
                nearest = (gap, (i + t) / (len(points) - 1))
        if nearest and nearest[0] <= 64 and .1 < nearest[1] < .95 and all(distance(center, body) > 1 for body in node_roles.values()):
            label['relationshipRole'] = {'source': source, 'target': target, 'anchorDistance': nearest[0], 'routeFraction': nearest[1]}


def caption_presence_findings(labels: list[dict]) -> list[dict]:
    """Require complete visible relationship words before any clearance check."""
    findings = []
    for required, (source, target) in RELATIONSHIPS.items():
        matching = [label for label in labels if label.get('text') == required and label.get('relationshipRole') and label['relationshipRole']['source'] == source and label['relationshipRole']['target'] == target]
        if not matching:
            findings.append({'issue': 'Required complete relationship caption is missing, hidden or unattributed', 'caption': required})
        elif not any(label.get('fontSize', 0) >= 14 and label.get('opacity', 0) >= .99 for label in matching):
            findings.append({'issue': 'Required caption is unreadable at settled font or opacity', 'caption': required})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--clicks", type=int, default=2, help="The deck's declared click count.")
    parser.add_argument("--deck", type=Path, help="An evaluator-owned byte-identical rebuild of retained deck sources.")
    args = parser.parse_args()
    workspace = ROOT / "evaluations/runs" / args.run_id / "workspace"
    workspace.resolve().relative_to(ROOT)
    deck = args.deck.resolve() if args.deck else workspace / 'deck'
    deck.resolve().relative_to(ROOT)
    dist = deck / 'dist'
    assert (dist / "index.html").is_file(), "The trial did not retain a completed Slidev build"
    out = ROOT / "projects/diagram-compactness/artifacts/reviews" / args.run_id / "independent-deck"
    out.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SpaHandler, directory=str(dist)))
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    result = {"run": args.run_id, 'deck': str(deck), 'nativeDefaultScreenshots': True, "states": [], "pageErrors": []}
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 800})
            context.grant_permissions(["screen-wake-lock"], origin=origin)
            page = context.new_page()
            page.on("pageerror", lambda error: result["pageErrors"].append(str(error)))
            page.goto(origin + "/1", wait_until="networkidle")
            page.wait_for_timeout(1200)
            for name in ["initial", *[f"click-{i}" for i in range(1, args.clicks + 1)], "replay", "resized", "reduced-motion"]:
                if name.startswith("click"):
                    page.keyboard.press("ArrowRight")
                elif name == "replay":
                    replay = page.get_by_role("button", name="Replay", exact=False)
                    if replay.count():
                        replay.first.click()
                        result["replayClicked"] = True
                    else:
                        for _ in range(args.clicks):
                            page.keyboard.press("ArrowLeft")
                        for _ in range(args.clicks):
                            page.keyboard.press("ArrowRight")
                        result["replayViaClickNavigation"] = True
                elif name == "resized":
                    page.set_viewport_size({"width": 1024, "height": 768})
                elif name == "reduced-motion":
                    page.emulate_media(reduced_motion="reduce")
                page.wait_for_timeout(800)
                page.evaluate('document.fonts.ready')
                page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
                proof = page.evaluate(SNAPSHOT)
                proof["state"] = name
                page.screenshot(path=str(out / f"{name}.png"))
                result["states"].append(proof)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
    result["findings"] = []
    for state in result["states"]:
        if len(state["graphs"]) != 1:
            result["findings"].append({"state": state["state"], "issue": "Expected one visible native graph", "count": len(state["graphs"])})
        for graph in state["graphs"]:
            attribute_caption_roles(graph)
            for finding in caption_presence_findings(graph['labels']):
                result['findings'].append({'state': state['state'], **finding})
            graph['captionClearance'] = []
            for label in graph['labels']:
                if label['text'] in ['Retest', 'Failed sample']:
                    gap = min((ORACLE.segment_quad_distance(a, b, label['quad']) - shaft['width'] / 2 for shaft in graph['shafts'] for a, b in zip(shaft['points'], shaft['points'][1:])), default=None)
                    head_gap = min((ORACLE.segment_quad_distance(head[i], head[(i+1)%4], label['quad']) for head in graph['headQuads'] for i in range(4)), default=None)
                    graph['captionClearance'].append({'label': label['text'], 'minimumShaftPaintGap': gap, 'completeHeadGap': head_gap})
                    if gap is None or gap < .75 or head_gap is None or head_gap < .75:
                        result['findings'].append({'state': state['state'], 'issue': 'Actual caption glyph meets a shaft or complete head', 'detail': graph['captionClearance'][-1]})
            del graph['shafts']
            if graph["textOverlaps"]:
                result["findings"].append({"state": state["state"], "issue": "Text overlap", "detail": graph["textOverlaps"]})
            canvas = graph["bounds"]
            for record in [*graph["labels"], *graph["nodes"], *graph["heads"]]:
                b = record["bounds"]
                if b["x"] < -.5 or b["y"] < -.5 or b["x"] + b["width"] > canvas["width"] + .5 or b["y"] + b["height"] > canvas["height"] + .5:
                    result["findings"].append({"state": state["state"], "issue": "Clipped native envelope", "detail": record})
            for head in graph["heads"]:
                if head["gap"] < 2.4:
                    result["findings"].append({"state": state["state"], "issue": "Head overlaps a body", "detail": head})
    result["ok"] = not result["pageErrors"] and not result["findings"]
    (out / "browser.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"run": args.run_id, "ok": result["ok"], "pageErrors": result["pageErrors"], "findings": result["findings"], "review": str(out)}))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

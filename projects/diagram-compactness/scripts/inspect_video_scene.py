#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Independently capture exact-scale scene states and painted label/route bounds."""
import argparse
import json
import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument("run_id")
args = parser.parse_args()
root = Path(__file__).resolve().parents[3]
workspace = root / "evaluations/runs" / args.run_id / "workspace"
scene = json.loads((workspace / "source/scene-contract.json").read_text(encoding="utf-8"))
canvas = scene["canvas"]
out = root / "projects/diagram-compactness/artifacts/reviews/video" / args.run_id
out.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("independent_arrow_quality", root/"skills/video/scripts/arrow_quality.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
times = {0, canvas["durationSeconds"] - .001}
for interaction in scene["interactions"]:
    begin, end = interaction["start"], interaction["end"]
    times.update([begin, begin + (end - begin) * .5, end - .002, min(canvas["durationSeconds"] - .001, end + .02)])
with sync_playwright() as api:
    browser = api.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": canvas["width"], "height": canvas["height"]})
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    page.goto((workspace / "src/index.html").as_uri())
    samples = []
    for index, seconds in enumerate(sorted(times)):
        state = page.evaluate("arg => window.renderConceptFrame(arg.id, arg.t)", {"id": scene["id"], "t": seconds})
        geometry = page.evaluate("""() => {
          const rect = e => {const b=e.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height};};
          const texts=[...document.querySelectorAll('svg text')].filter(e => +getComputedStyle(e).opacity > .01)
            .map(e=>({text:e.textContent,font:getComputedStyle(e).fontSize,...rect(e)}));
          const arrows=[...document.querySelectorAll('.interaction-overlay')].map(e=>({id:e.dataset.interactionId,
            visible:+getComputedStyle(e).opacity>.01,
            parts:[...e.querySelectorAll('path,circle')].map(p=>({head:p.hasAttribute('data-arrow-head'),
              shaft:p.hasAttribute('data-arrow-shaft'),pulse:p.hasAttribute('data-relationship-pulse'),
              opacity:+getComputedStyle(p).opacity,...rect(p)}))}));
          const clipped=texts.filter(b=>b.x<-.5||b.y<-.5||b.x+b.width>innerWidth+.5||b.y+b.height>innerHeight+.5);
          const overlaps=[];for(let i=0;i<texts.length;i++)for(let j=i+1;j<texts.length;j++){
            const a=texts[i],b=texts[j];if(a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y)overlaps.push([a.text,b.text]);
          }
          const nodes=[...document.querySelectorAll('.video-element')].map(e=>e.getBoundingClientRect());
          const intersects=(a,b)=>a.left<b.right-.1&&a.right>b.left+.1&&a.top<b.bottom-.1&&a.bottom>b.top+.1;
          const clearance=(a,b)=>Math.hypot(Math.max(b.left-a.right,a.left-b.right,0),Math.max(b.top-a.bottom,a.top-b.bottom,0));
          const visible=e=>+getComputedStyle(e).opacity>.01&&+getComputedStyle(e.parentNode).opacity>.01;
          const pulses=[...document.querySelectorAll('[data-relationship-pulse]')].filter(visible);
          const heads=[...document.querySelectorAll('[data-arrow-head]')].filter(visible);
          let routeNodeCollisions=0;
          for(const path of document.querySelectorAll('[data-arrow-shaft]')){
            const m=path.getScreenCTM(),length=path.getTotalLength();
            for(let at=0;at<=length;at+=2){const p=path.getPointAtLength(at),q=new DOMPoint(p.x,p.y).matrixTransform(m);
              routeNodeCollisions+=nodes.filter(b=>q.x>b.left+.1&&q.x<b.right-.1&&q.y>b.top+.1&&q.y<b.bottom-.1).length;}
          }
          return {texts,arrows,clipped,overlaps,routeNodeCollisions,visibleHeadCount:heads.length,
            tokenNodeCollisions:pulses.reduce((s,e)=>s+nodes.filter(b=>intersects(e.getBoundingClientRect(),b)).length,0),
            headNodeCollisions:heads.reduce((s,e)=>s+nodes.filter(b=>intersects(e.getBoundingClientRect(),b)).length,0),
            minimumTokenClearance:pulses.length?Math.min(...pulses.flatMap(e=>nodes.map(b=>clearance(e.getBoundingClientRect(),b)))):null};
        }""")
        page.screenshot(path=str(out / f"state-{index:02d}.png"), animations="disabled")
        samples.append({"seconds": seconds, "state": state, "geometry": geometry})
    held_audit = page.evaluate(module.ARROW_AUDIT, {"selector":"#stage"})
    browser.close()
report = {"run": args.run_id, "canvas": canvas, "pageErrors": errors, "samples": samples,
          "labelGeometryPass": not errors and all(not row["geometry"]["clipped"] and not row["geometry"]["overlaps"] for row in samples),
          "motionGeometryPass": not errors and all(not row["geometry"]["routeNodeCollisions"] and not row["geometry"]["tokenNodeCollisions"] and not row["geometry"]["headNodeCollisions"] and (row["geometry"]["minimumTokenClearance"] is None or row["geometry"]["minimumTokenClearance"] >= 2.8) for row in samples),
          "heldArrowAudit":held_audit,
          "requiresManualReview": "Inspect complete heads, source/target attachment, shared lanes and closest token approaches in screenshots."}
(out / "independent-scene.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"run": args.run_id, "states": len(samples), "labelGeometryPass": report["labelGeometryPass"], "motionGeometryPass":report["motionGeometryPass"],"heldHeads":held_audit["headCount"],"arrowIssues":held_audit["issues"], "pageErrors": errors, "folder": str(out)}))

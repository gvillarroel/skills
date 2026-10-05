#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Independently inspect final native SVGs, replay and laptop resizing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = """() => {
  const svg=document.querySelector('svg'), v=svg.viewBox.baseVal;
  const bounds=e=>{const r=e.getBoundingClientRect(),s=svg.getBoundingClientRect();return {x:r.x-s.x,y:r.y-s.y,width:r.width,height:r.height}};
  const labels=[...svg.querySelectorAll('text')].map(e=>({text:e.textContent,bounds:bounds(e),fontSize:parseFloat(getComputedStyle(e).fontSize),opacity:Number(getComputedStyle(e).opacity)}));
  const native=[...svg.querySelectorAll('path')];
  const nodes=native.filter(e=>{const b=e.getBBox();return getComputedStyle(e).fill!=='none'&&b.width<=3&&b.height<=3&&!e.getAttribute('d').startsWith('M0 0L')}).map(e=>({index:e.getAttribute('ecmeta_data_index'),bounds:bounds(e)}));
  const gap=(a,b)=>Math.hypot(Math.max(b.x-a.x-a.width,a.x-b.x-b.width,0),Math.max(b.y-a.y-a.height,a.y-b.y-b.height,0));
  const heads=[...svg.querySelectorAll('path[d^="M0 0L"]')].map(e=>({index:e.getAttribute('ecmeta_data_index'),bounds:bounds(e),gap:Math.min(...nodes.map(n=>gap(bounds(e),n.bounds))),opacity:Number(getComputedStyle(e).opacity),fill:getComputedStyle(e).fill}));
  const overlaps=[];
  for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
    const a=labels[i].bounds,b=labels[j].bounds,w=Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x),h=Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y);
    if(w>1&&h>1)overlaps.push({a:labels[i].text,b:labels[j].text,width:w,height:h});
  }
  return {width:v.width||parseFloat(svg.getAttribute('width')),height:v.height||parseFloat(svg.getAttribute('height')),labels,nodes,heads,textOverlaps:overlaps};
}"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_id")
    parser.add_argument("--file", default="workflow.static.svg")
    parser.add_argument("--animated", default="workflow.animated.svg")
    parser.add_argument("--static-only", action="store_true")
    args = parser.parse_args()
    workspace = ROOT / "evaluations/runs" / args.run_id / "workspace"
    workspace.resolve().relative_to(ROOT)
    out = ROOT / "projects/diagram-compactness/artifacts/reviews" / args.run_id / "independent-native"
    out.mkdir(parents=True, exist_ok=True)
    paths = [("static", workspace / "deliverables" / args.file)]
    if not args.static_only:
        paths.append(("animated", workspace / "deliverables" / args.animated))
    result = {"run": args.run_id, "states": [], "pageErrors": []}
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda error: result["pageErrors"].append(str(error)))
        for kind, path in paths:
            source = path.read_text(encoding="utf-8")
            ET.fromstring(source)
            page.set_content("<!doctype html><style>body{margin:0;background:white}button{display:block}</style><button id='replay'>Replay</button>" + source + "<script>document.querySelector('button').onclick=()=>{const s=document.querySelector('svg');s.classList.remove('easv-playing');void s.getBoundingClientRect();s.classList.add('easv-playing')}</script>")
            page.evaluate("const s=document.querySelector('svg'),v=s.viewBox.baseVal;s.style.width=(v.width||parseFloat(s.getAttribute('width')))+'px';s.style.height=(v.height||parseFloat(s.getAttribute('height')))+'px';s.style.position='relative';s.style.left='0px';s.style.top='0px'")
            page.evaluate("document.fonts.ready")
            page.evaluate("document.getAnimations().forEach(a=>a.finish())")
            for state in ["settled", "replay-1", "replay-2", "resized", "reduced-motion"]:
                if state.startswith("replay"):
                    page.get_by_role("button", name="Replay", exact=True).click()
                    page.evaluate("document.getAnimations().forEach(a=>a.finish())")
                elif state == "resized":
                    page.set_viewport_size({"width": 1024, "height": 768})
                elif state == "reduced-motion":
                    page.emulate_media(reduced_motion="reduce")
                proof = page.evaluate(SNAPSHOT)
                proof.update({"kind": kind, "state": state})
                result["states"].append(proof)
                assert not proof["textOverlaps"], (kind, state, proof["textOverlaps"])
                for record in [*proof["labels"], *proof["nodes"], *proof["heads"]]:
                    b = record["bounds"]
                    assert b["x"] >= -.3 and b["y"] >= -.3 and b["x"] + b["width"] <= proof["width"] + .3 and b["y"] + b["height"] <= proof["height"] + .3, (kind, state, record)
                    assert record.get("opacity", 1) >= .99, (kind, state, record)
                for head in proof["heads"]:
                    assert head["gap"] >= 2.4, (kind, state, head)
                page.locator("svg").screenshot(path=str(out / f"{kind}-{state}.png"), animations="disabled")
            page.emulate_media(reduced_motion="no-preference")
            page.set_viewport_size({"width": 1280, "height": 800})
        browser.close()
    assert not result["pageErrors"], result["pageErrors"]
    result["ok"] = True
    (out / "browser.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "run": args.run_id, "states": len(result["states"]), "review": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

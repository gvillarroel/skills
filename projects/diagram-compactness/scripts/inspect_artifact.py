#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Capture a local visual and report rendered text intersections independently."""
from pathlib import Path
import argparse
import json
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("input", type=Path)
parser.add_argument("--name", required=True)
parser.add_argument("--width", type=int, default=1280)
parser.add_argument("--height", type=int, default=800)
args = parser.parse_args()
source = args.input.resolve()
source.relative_to(root)
out = root / "projects/diagram-compactness/artifacts/reviews" / args.name
out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": args.width, "height": args.height})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    if source.suffix.lower() == ".svg":
        page.set_content("<!doctype html><style>body{margin:0;background:white}</style>" +
                         source.read_text(encoding="utf-8"), wait_until="load")
    else:
        page.goto(source.as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(1600)
    result = page.evaluate("""() => {
      const all=[...document.querySelectorAll('svg text,svg foreignObject')];
      const labels=all.map((e,i)=>{const b=e.getBoundingClientRect(),c=getComputedStyle(e);
        return {i,text:e.textContent.trim(),x:b.x,y:b.y,w:b.width,h:b.height,
          fill:c.fill,color:c.color,fontSize:c.fontSize,opacity:c.opacity};})
        .filter(e=>e.text&&e.w>0&&e.h>0&&Number(e.opacity)>0);
      const overlaps=[];
      for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++){
        const a=labels[i],b=labels[j],w=Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x),
          h=Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y);
        if(w>1&&h>1)overlaps.push({a:a.text,b:b.text,width:w,height:h});
      }
      return {labels,overlaps,svgs:[...document.querySelectorAll('svg')].map(e=>({
        viewBox:e.getAttribute('viewBox'),width:e.getAttribute('width'),height:e.getAttribute('height')}))};
    }""")
    result.update({"input": source.relative_to(root).as_posix(), "pageErrors": errors,
                   "scope": "Rendered text intersections only; inspect arrows, attachment and routing visually."})
    page.screenshot(path=str(out / "preview.png"), full_page=True,
                    animations="disabled", timeout=20000)
    (out / "geometry.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    browser.close()
print(json.dumps({"screenshot": str(out / "preview.png"), "labelCount": len(result["labels"]),
                  "overlaps": result["overlaps"], "pageErrors": errors}))

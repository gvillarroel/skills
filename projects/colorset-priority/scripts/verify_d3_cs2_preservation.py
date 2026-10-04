#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Compare CS2 gallery paint, geometry and labels against a Git baseline renderer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
IDS = ["treemap", "circle-pack", "radial-hierarchy", "task-overlap-dense", "streamgraph", "voronoi",
       "icicle", "chord", "sunburst", "mirrored-beeswarm", "flowchart-dag", "state-machine", "er-schema",
       "tangled-tree", "tanglegram", "task-overlap", "venn-3", "venn-5", "venn-7",
       "overlap-3-rosette", "overlap-5-rosette", "overlap-7-flower", "overlap-3-chain", "overlap-5-cluster", "overlap-7-bridge"]
SNAPSHOT = r'''ids => Object.fromEntries(ids.map(id=>{
  const svg=document.getElementById(id);svg.pauseAnimations?.();svg.setCurrentTime?.(10);window.D3SolidStyle?.normalize(svg);
  return [id,[...svg.querySelectorAll('rect,circle,ellipse,polygon,path,line,text')].filter(node=>!node.closest('defs')).map(node=>{
    const style=getComputedStyle(node);
    const geometry=Object.fromEntries(['x','y','width','height','cx','cy','r','rx','ry','x1','x2','y1','y2','d','points','transform','text-anchor','dy'].filter(key=>node.hasAttribute(key)).map(key=>[key,node.getAttribute(key)]));
    return {tag:node.tagName,geometry,fill:style.fill,stroke:style.stroke,strokeWidth:style.strokeWidth,alpha:style.fillOpacity,opacity:style.opacity,blend:style.mixBlendMode,
      text:node.tagName==='text'?node.textContent:null,id:node.dataset.setId??node.dataset.taskId??null,memberships:node.dataset.memberships??null};
  })];
}))'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="HEAD")
    parser.add_argument("--artifacts", type=Path, default=ROOT / "projects/colorset-priority/artifacts/d3-cs2-preservation")
    args = parser.parse_args()
    artifacts = args.artifacts.resolve()
    if not artifacts.is_relative_to(ROOT) or artifacts.is_relative_to(ROOT / "skills"):
        parser.error("Artifacts must be inside this repository and outside skill bundles")
    artifacts.mkdir(parents=True, exist_ok=True)
    renderer_path = "skills/d3/assets/examples/d3-animated-svg/gallery.js"
    baseline = subprocess.check_output(["git", "show", f"{args.baseline_ref}:{renderer_path}"], cwd=ROOT)
    baseline_file = artifacts / "baseline-gallery.js"
    baseline_file.write_bytes(baseline)
    gallery = ROOT / "skills/d3/assets/examples/d3-animated-svg-colorset2/index.html"
    source = gallery.read_text(encoding="utf-8")
    def absolute(match: re.Match) -> str:
        key, value = match.group(1), match.group(2)
        target = baseline_file.as_uri() if value.endswith("d3-animated-svg/gallery.js") else urljoin(gallery.as_uri(), value)
        return f'{key}="{target}"'
    html = re.sub(r'(src|href)="([^"#][^"]*)"', absolute, source)
    baseline_html = artifacts / "baseline-index.html"
    baseline_html.write_text(html, encoding="utf-8")
    snapshots = []
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**({} if Path(playwright.chromium.executable_path).exists() else {"channel":"msedge"}))
        for url in [baseline_html.as_uri(), gallery.as_uri()]:
            page = browser.new_page(viewport={"width":1440,"height":1100}, reduced_motion="reduce")
            page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto(url,wait_until="load",timeout=120000)
            page.wait_for_timeout(650)
            snapshots.append(page.evaluate(SNAPSHOT,IDS))
            page.close()
        browser.close()
    differences=[]
    for identity in IDS:
        old,new=snapshots[0][identity],snapshots[1][identity]
        if old!=new:
            differences.append({"id":identity,"baselineCount":len(old),"currentCount":len(new),
                "changedMarks":[{"index":index,"baseline":a,"current":b} for index,(a,b) in enumerate(zip(old,new)) if a!=b]})
    report={"passed":not differences and not errors,"baselineRef":args.baseline_ref,
        "baselineRendererSHA256":hashlib.sha256(baseline).hexdigest(),
        "currentRendererSHA256":hashlib.sha256((ROOT/renderer_path).read_bytes()).hexdigest(),
        "ids":IDS,"browserErrors":errors,"differences":differences}
    (artifacts/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    assert report["passed"], {"browserErrors":errors,"changedIds":[entry["id"] for entry in differences]}
    print(json.dumps({"passed":True,"ids":IDS,"report":str(artifacts/"report.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

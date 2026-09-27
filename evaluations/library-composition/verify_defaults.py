#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independently render and compare the D3/Three.js composition defaults."""

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "projects/library-composition/artifacts"
D3 = ROOT / "skills/d3"
THREE = ROOT / "skills/threejs-animated-3d"
PALETTES = json.loads((D3 / "assets/palettes/colorsets.json").read_text())["colorsets"]


def run(script, *args):
    result = subprocess.run([sys.executable, str(script), *map(str, args)], cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stdout + result.stderr)


def build_samples():
    current = OUT / "current"
    current.mkdir(parents=True, exist_ok=True)
    for name, extra in (("flow", []), ("flow-spacious", ["--height", 300, "--node-padding-y", 18]), ("flow-long", ["--width", 1100])):
        labels = ["Initial assessment", "Independent verification", "Release approval"] if name == "flow-long" else ["Draft", "Review", "Publish"]
        args = ["--kind", "flow", "--output", current / f"{name}.html", "--decision-output", current / f"{name}.json", "--title", "Release flow", "--description", "Three ordered stages.", "--route", "flow", "--colorset", "colorset1", "--pattern-id", "d3-flow-spine", "--svg-id", "flow", "--reason", "Ordered stages", "--force", *extra]
        for label in labels:
            args += ["--flow-node", label]
        for index in range(2):
            args += ["--link", f"{labels[index]}->{labels[index+1]}", "--link-value", str(12 - index * 4)]
        run(D3 / "scripts/build_contract_artifact.py", *args)
    for name, extra in (("three", []), ("three-extended", ["--colorset", "colorset2"]), ("three-spacious", ["--density", "comfortable"]), ("three-title", ["--title", "A long scene heading that wraps safely on mobile"]), ("three-many", ["--token-count", 12])):
        run(THREE / "scripts/build_standalone_threejs.py", current / f"{name}.html", "--force", *extra)
    for pattern in ("operational-dashboard", "inline-bar-table", "context-window-matrix", "animated-network", "blank"):
        for colorset in ("colorset1", "colorset2"):
            name = "dashboard" if pattern == "operational-dashboard" and colorset == "colorset1" else f"{pattern}-{colorset}"
            run(D3 / "scripts/create_d3_svg_starter.py", "--out", current / name, "--pattern", pattern, "--title", "Operations review", "--colorset", colorset, "--force")
    (current / "stages.html").write_text((D3 / "assets/templates/self-contained-animated-svg.html").read_text(), encoding="utf-8")
    run(D3 / "scripts/build_critical_queue_backpressure.py", current / "queue.html")
    run(D3 / "scripts/build_kinetic_type.py", current / "type.html", "--text", "SIGNAL")


SVG_PROBE = r"""() => {
 const svg=document.querySelector('svg'), b=svg.getBoundingClientRect();
 const hex=v=>{const m=v.match(/^rgb\((\d+), (\d+), (\d+)\)$/);return m?'#'+m.slice(1).map(n=>(+n).toString(16).padStart(2,'0')).join(''):v};
 const paints=new Set();
 for(const e of svg.querySelectorAll('rect,path,circle,line,polygon,polyline,text,tspan')){
   const s=getComputedStyle(e); if(s.display==='none'||+s.opacity===0||e.closest('defs'))continue;
   for(const p of ['fill','stroke']){const c=hex(s[p]);if(c!=='none'&&c!=='transparent')paints.add(c)}
 }
 const nodes=[...svg.querySelectorAll('g.flow-node')].map(g=>{
  const r=g.querySelector('rect'),t=g.querySelector('text'), rb=r.getBBox(),tb=t.getBBox();
  return {height:rb.height,width:rb.width,font:getComputedStyle(t).fontSize,paddingY:(rb.height-tb.height)/2,
  fits:tb.x>=rb.x-.5&&tb.x+tb.width<=rb.x+rb.width+.5&&tb.y>=rb.y-.5&&tb.y+tb.height<=rb.y+rb.height+.5};
 });
 const stages=[...svg.querySelectorAll('g.stage')].map(g=>{const r=g.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}});
 return {viewBox:svg.getAttribute('viewBox'),width:b.width,height:b.height,paints:[...paints].sort(),nodes,stages,
  overflow:document.documentElement.scrollWidth-innerWidth,colorset:svg.dataset.colorset||document.body.dataset.colorset,
  pagePadding:getComputedStyle(document.querySelector('.page')||document.body).padding};
}"""


def verify():
    records = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge")
        paths = sorted((OUT / "current").glob("*.html")) + sorted((OUT / "current").glob("*/index.html"))
        paths += [OUT / "baseline" / path for path in ("flow.html", "three.html", "stages.html", "dashboard/index.html")]
        for path in paths:
            baseline = "baseline" in path.parts
            is_three = path.stem.startswith("three")
            for width in (1280, 390):
                context = browser.new_context(viewport={"width": width, "height": 844}, has_touch=width < 600)
                context.route("https://**", lambda route: route.abort())
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(path.as_uri())
                page.wait_for_timeout(1300)
                name = path.parent.name if path.stem == "index" else path.stem
                screenshot = path.parent / f"{path.stem}-{width}.png"
                if is_three:
                    page.wait_for_function("window.__threeRuntimeSceneReady===true")
                    data = page.evaluate("""() => ({stage:document.querySelector('.stage').getBoundingClientRect().toJSON(),buttonHeight:document.querySelector('button').getBoundingClientRect().height,statusPadding:getComputedStyle(document.querySelector('.status')).padding,overflow:document.documentElement.scrollWidth-innerWidth,composition:window.__threeRuntimeScene.inspect?.()})""")
                    if not baseline:
                        frames = page.evaluate("""() => {const api=window.__threeRuntimeScene;return Array.from({length:41},(_,i)=>{api.renderAt(i*.5);return api.inspect().tokenBounds.every(p=>Math.abs(p[0])<=1&&Math.abs(p[1])<=1&&p[2]>-1&&p[2]<1)})}""")
                        assert all(frames), (name, width, "clipped token envelope")
                        data["framesInBounds"] = len(frames)
                        data["composition"].pop("tokenBounds", None)
                        data["composition"].pop("tokenCenters", None)
                        cs = data["composition"]["colorset"]
                        materials = set(data["composition"]["materialColors"])
                        assert materials <= set(PALETTES[cs]["allowed"])
                        assert "#ffccd5" not in materials
                        assert set(data["composition"]["lightColors"]) == {"#ffffff"}
                        assert data["buttonHeight"] >= (44 if width < 600 else 32)
                elif name != "type":
                    data = page.evaluate(SVG_PROBE)
                    # The queue illustration is an older full-color pattern; check
                    # its removed soft-red surface without claiming colorset1.
                    if not baseline and name != "queue":
                        cs = data["colorset"]
                        assert cs in PALETTES, (name, cs)
                        assert set(data["paints"]) <= set(PALETTES[cs]["allowed"]), (name, data["paints"])
                    if not baseline:
                        assert "#ffccd5" not in data["paints"], name
                        if name == "stages":
                            assert len(data["stages"]) == 3
                            assert all(a["x"] + a["width"] < b["x"] for a, b in zip(data["stages"], data["stages"][1:]))
                        assert all(n["fits"] for n in data["nodes"]), (name, data["nodes"])
                        if data["nodes"]:
                            assert all(n["font"] == "16px" for n in data["nodes"])
                            if name == "flow-spacious":
                                assert data["viewBox"].endswith("300") and all(n["paddingY"] == 18 for n in data["nodes"])
                            else:
                                assert all(6 <= n["paddingY"] <= 8 for n in data["nodes"])
                else:
                    data = {"overflow": page.evaluate("document.documentElement.scrollWidth-innerWidth")}
                if not baseline:
                    assert not errors, (name, errors)
                    assert data["overflow"] <= 1, (name, width, data["overflow"])
                page.screenshot(path=str(screenshot), full_page=True)
                records.append({"name": name, "baseline": baseline, "viewport": width, "path": str(path.relative_to(ROOT)), "screenshot": str(screenshot.relative_to(ROOT)), **data})
                context.close()
        browser.close()
    (OUT / "comparison.json").write_text(json.dumps({"passed": True, "records": records}, indent=2) + "\n")
    print(json.dumps({"passed": True, "renders": len(records), "report": str(OUT / "comparison.json")}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()
    if not args.skip_build:
        build_samples()
    verify()

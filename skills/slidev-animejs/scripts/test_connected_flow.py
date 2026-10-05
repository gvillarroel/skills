#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Check native labels, route/head attribution, actual motion, clicks and replay."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright
from scaffold_connected_flow import scaffold, validate_config
from capture_deck import SpaHandler

CONFIG = {"id": "handoff-test", "title": "Order handoff", "labels": ["Order", "Pick", "Pack", "Dispatch"], "branch": {"at": 1, "label": "Inventory check"}, "return": {"source": 2, "target": 1, "label": "missing item"}}
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--workdir", type=Path, default=Path.cwd() / "connected-flow-test")
args = parser.parse_args()
deck = args.workdir / "deck"
args.workdir.mkdir(parents=True, exist_ok=True)
for invalid in ({**CONFIG, "labels": ["same", "same"]}, {**CONFIG, "return": {"source": 1, "target": 2}}, {**CONFIG, "branch": {"at": 9, "label": "Check"}}):
    try:
        validate_config(invalid)
        raise AssertionError("Invalid topology was accepted")
    except ValueError:
        pass
scaffold(CONFIG, deck, force=True)
pack = Path(__file__).resolve().parents[1] / "assets/templates/slidev-svg-asset-pack"
for part in ("components", "lib", "assets"):
    shutil.copytree(pack / part, deck / part, dirs_exist_ok=True)
with (deck / "slides.md").open("a", encoding="utf-8") as slide:
    slide.write('\n---\nclicks: 2\n---\n\n# Timeline machine\n\n<SvgAssetSlide asset="timeline-machine" :step="$clicks" />\n')
npm = "npm.cmd" if os.name == "nt" else "npm"
for command in ([npm, "install", "--prefer-offline"], [npm, "run", "build"]):
    proc = subprocess.run(command, cwd=deck, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (args.workdir / ("install.log" if "install" in command else "build.log")).write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if proc.returncode:
        raise RuntimeError(f"{command} failed: {proc.stderr[-2000:]}")
with socket.socket() as channel:
    channel.bind(("127.0.0.1", 0))
    port = channel.getsockname()[1]
origin = f"http://127.0.0.1:{port}"
server = ThreadingHTTPServer(('127.0.0.1', port), partial(SpaHandler, directory=str((deck / 'dist').resolve())))
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    for _ in range(50):
        try:
            urlopen(origin, timeout=.5).close()
            break
        except OSError:
            time.sleep(.1)
    with sync_playwright() as runtime:
        options = {} if Path(runtime.chromium.executable_path).is_file() else {"channel": "msedge"}
        browser = runtime.chromium.launch(**options)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        context.grant_permissions(["screen-wake-lock"], origin=origin)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(origin, wait_until="networkidle")
        flow = page.locator('.slidev-page-1 .connected-flow')
        flow.locator('[data-node="main-0"]').wait_for()
        page.wait_for_function("document.querySelector('.connected-flow')?.dataset.ready==='true'")
        report = flow.evaluate("""root=>{
          const svg=root.querySelector('svg'), s=svg.getBoundingClientRect(), nodes=[...root.querySelectorAll('.flow-node')];
          const inside=(p,r)=>p.x>r.x&&p.x<r.right&&p.y>r.y&&p.y<r.bottom;
          const hit=[], labels=[...root.querySelectorAll('.route-labels text')].map(t=>t.getBoundingClientRect());
          for(const path of root.querySelectorAll('[data-route]')){
            const length=path.getTotalLength(), m=path.getScreenCTM();
            for(let d=0;d<=length;d+=2){const p=path.getPointAtLength(d).matrixTransform(m);for(const node of nodes)if(inside(p,node.querySelector('rect').getBoundingClientRect()))hit.push([path.dataset.route,node.dataset.node,d]);for(const label of labels)if(inside(p,label))hit.push(['label',path.dataset.route,d]);}
            const p=path.getPointAtLength(length), prev=path.getPointAtLength(length-.5), dx=p.x-prev.x,dy=p.y-prev.y,n=Math.hypot(dx,dy),ux=dx/n,uy=dy/n;
            for(const q of [p,new DOMPoint(p.x-10*ux+5*uy,p.y-10*uy-5*ux),new DOMPoint(p.x-10*ux-5*uy,p.y-10*uy+5*ux)]){
              const screen=q.matrixTransform(m);for(const node of nodes)if(inside(screen,node.querySelector('rect').getBoundingClientRect()))hit.push(['head',path.dataset.route,node.dataset.node]);for(const label of labels)if(inside(screen,label))hit.push(['head-label',path.dataset.route]);
            }
          }
          return {parcelFill:getComputedStyle(root.querySelector('.parcel')).fill,width:svg.getAttribute('width'),height:svg.getAttribute('height'),onScreen:s.x>=0&&s.right<=innerWidth&&s.y>=0&&s.bottom<=innerHeight,routes:[...root.querySelectorAll('[data-route]')].map(p=>({id:p.dataset.route,source:p.dataset.source,target:p.dataset.target})),hit,labels:nodes.map(n=>{const t=n.querySelector('text'),r=n.querySelector('rect').getBoundingClientRect(),b=t.getBoundingClientRect();return {text:t.textContent,font:getComputedStyle(t).fontSize,fit:b.x>=r.x+3&&b.right<=r.right-3&&b.y>=r.y+3&&b.bottom<=r.bottom-3}})};
        }""")
        assert report["onScreen"] and float(report["width"]) < 700, report
        assert report["parcelFill"] == "rgb(158, 27, 50)", report
        assert len(report["routes"]) == 6 and not report["hit"], report
        assert all(t["font"] == "18px" and t["fit"] for t in report["labels"]), report
        observed = set()
        motion = []
        for state in (1, 2):
            page.keyboard.press('ArrowRight')
            page.wait_for_timeout(80)
            assert flow.get_attribute('data-click-state') == str(state)
            for _ in range(60):
                sample = flow.evaluate("""root=>{
                  const token=root.querySelector('.parcel'),id=token.dataset.motionRoute;if(token.getAttribute('opacity')!=='1'||!id)return null;
                  const b=token.getBoundingClientRect(),path=root.querySelector(`[data-route="${id}"]`),m=path.getScreenCTM();
                  let nearest=Infinity;for(let d=0;d<path.getTotalLength();d+=1){const p=path.getPointAtLength(d).matrixTransform(m);nearest=Math.min(nearest,Math.hypot(p.x-(b.x+b.width/2),p.y-(b.y+b.height/2)));}
                  const overlaps=[...root.querySelectorAll('.flow-node rect')].filter(n=>{const r=n.getBoundingClientRect();return b.x<r.right&&b.right>r.x&&b.y<r.bottom&&b.bottom>r.y}).length;
                  const end=path.getPointAtLength(path.getTotalLength()).matrixTransform(m);
                  return {route:id,nearest,overlaps,headDistance:Math.hypot(end.x-(b.x+b.width/2),end.y-(b.y+b.height/2))};
                }""")
                if sample:
                    observed.add(sample["route"])
                    motion.append(sample)
                    assert sample["nearest"] < 2 and not sample["overlaps"] and sample["headDistance"] > 15, sample
                page.wait_for_timeout(100)
            page.screenshot(path=str(args.workdir / f"click-{state}.png"))
        assert observed == {r["id"] for r in report["routes"]}, observed
        flow.get_by_role('button', name='Replay').click()
        page.wait_for_timeout(250)
        assert flow.locator('.parcel').get_attribute('opacity') == '1'
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_timeout(100)
        assert flow.locator('.parcel').get_attribute('opacity') == '0'
        assert flow.locator('[data-route]').count() == 6
        page.screenshot(path=str(args.workdir / 'reduced.png'))
        page.emulate_media(reduced_motion='no-preference')
        page.evaluate('document.activeElement?.blur()')
        page.keyboard.press('ArrowRight')
        page.locator('.slidev-page-2 .machine-signal').first.wait_for()
        machine = page.locator('.slidev-page-2 .svg-asset-stage')
        for state in range(3):
            if state:
                page.keyboard.press('ArrowRight')
                page.wait_for_timeout(100)
            for _ in range(20):
                paint = machine.evaluate("""root=>{
                  const r=root.getBoundingClientRect();
                  const bounds=[...root.querySelectorAll('.machine-signal,.machine-gear')].map(e=>{const b=e.getBoundingClientRect();return {inside:b.x>=r.x&&b.right<=r.right&&b.y>=r.y&&b.bottom<=r.bottom,pivot:getComputedStyle(e).transformBox}});
                  const bases=[...root.querySelectorAll('.machine-cable-base')], cables=[...root.querySelectorAll('.machine-cable')];
                  return {bounds,baseCount:bases.length,basePaint:bases.map(b=>({dash:getComputedStyle(b).strokeDasharray,opacity:getComputedStyle(b).opacity})),baseComplete:bases.every((b,i)=>b.getAttribute('d')===cables[i].getAttribute('d')&&getComputedStyle(b).strokeDasharray==='none'&&Number(getComputedStyle(b).opacity)>=.8)};
                }""")
                assert all(b['inside'] and b['pivot']=='fill-box' for b in paint['bounds']), paint
                assert paint['baseCount']==2 and paint['baseComplete'], paint
                page.wait_for_timeout(100)
        page.reload(wait_until='networkidle')
        page.locator('.slidev-page-2 .machine-signal').first.wait_for()
        assert page.locator('.slidev-page-2 .machine-cable-base').count()==2
        assert not errors, errors
        (args.workdir / 'browser.json').write_text(json.dumps({"geometry":report,"motion":motion,"observedRoutes":sorted(observed),"pageErrors":errors},indent=2),encoding='utf-8')
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=10)
print(json.dumps({"passed":True,"routes":6,"nodeFontPx":18,"workdir":str(args.workdir)}))

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Rebuild one isolated Slidev artifact and capture actual navigation states."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

class SpaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not Path(self.translate_path(self.path)).exists() and not self.path.startswith('/assets/'):
            self.path = '/'
        super().do_GET()

    def log_message(self, *args):
        pass

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("run_id")
parser.add_argument("--skip-build", action="store_true")
parser.add_argument("--deck", type=Path)
args = parser.parse_args()
workspace = ROOT / "evaluations/runs" / args.run_id / "workspace"
workspace.resolve().relative_to(ROOT)
deck = args.deck or workspace / "deck"
out = ROOT / "projects/diagram-compactness/artifacts/reviews" / args.run_id
out.mkdir(parents=True, exist_ok=True)
result = {"run": args.run_id}
if not args.skip_build:
    if not (deck / 'node_modules/.bin/slidev.cmd').exists() and not (deck / 'node_modules/.bin/slidev').exists():
        install = subprocess.run(['npm.cmd', 'install', '--prefer-offline'], cwd=deck, capture_output=True, text=True, encoding='utf-8', errors='replace')
        (out / 'install.log').write_text(install.stdout + install.stderr, encoding='utf-8')
        result['installExitCode'] = install.returncode
        if install.returncode:
            print(json.dumps(result))
            raise SystemExit(1)
    build = subprocess.run(["npm.cmd", "run", "build"], cwd=deck, capture_output=True, text=True, encoding="utf-8", errors="replace")
    (out / "build.log").write_text(build.stdout + build.stderr, encoding="utf-8")
    result["buildExitCode"] = build.returncode
    if build.returncode:
        print(json.dumps(result))
        raise SystemExit(1)
with socket.socket() as channel:
    channel.bind(("127.0.0.1", 0))
    port = channel.getsockname()[1]
server = ThreadingHTTPServer(('127.0.0.1', port), partial(SpaHandler, directory=str((deck / 'dist').resolve())))
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
try:
    for _ in range(50):
        try:
            with urlopen(f"http://127.0.0.1:{port}/", timeout=.5) as response:
                if response.status == 200:
                    break
        except OSError:
            time.sleep(.1)
    with sync_playwright() as runtime:
        options = {} if Path(runtime.chromium.executable_path).is_file() else {"channel": "msedge"}
        browser = runtime.chromium.launch(args=['--disable-gpu'], **options)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        origin = f"http://127.0.0.1:{port}"
        context.grant_permissions(["screen-wake-lock"], origin=origin)
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
        page.wait_for_timeout(1800)
        snapshots=[]
        for state in range(3):
            if state:
                page.keyboard.press("ArrowRight")
                page.wait_for_timeout(900)
            page.screenshot(path=str(out / f"state-{state}.png"), timeout=20000)
            snapshot = page.evaluate("""() => {
              const visible=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&getComputedStyle(e).visibility!=='hidden'&&getComputedStyle(e).display!=='none'};
              const stages=[...document.querySelectorAll('svg')].filter(e=>visible(e)&&e.getBoundingClientRect().width>250);
              return {url:location.href,flows:[...document.querySelectorAll('.connected-flow')].filter(visible).map(root=>({parcelFill:getComputedStyle(root.querySelector('.parcel')).fill,routes:[...root.querySelectorAll('[data-route]')].map(p=>({id:p.dataset.route,source:p.dataset.source,target:p.dataset.target,d:p.getAttribute('d')})),head:root.querySelector('marker')?.outerHTML})),svgs:stages.map(e=>({viewBox:e.getAttribute('viewBox'),width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,labels:[...e.querySelectorAll('text')].map(t=>({text:t.textContent,font:getComputedStyle(t).fontSize,fill:getComputedStyle(t).fill,display:getComputedStyle(t).display,opacity:getComputedStyle(t).opacity,visibility:getComputedStyle(t).visibility,markup:t.outerHTML,bounds:{x:t.getBoundingClientRect().x,y:t.getBoundingClientRect().y,width:t.getBoundingClientRect().width,height:t.getBoundingClientRect().height}})),paths:e.querySelectorAll('path,line,polyline').length})),bodyText:document.body.innerText.slice(0,1500),buttons:[...document.querySelectorAll('button')].filter(visible).map(e=>({text:e.textContent.trim(),title:e.getAttribute('title'),'aria-label':e.getAttribute('aria-label')}))};
            }""")
            snapshot["state"] = state
            samples = []
            for sample in range(12):
                samples.append(page.evaluate("""() => {
                  const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}};
                  return [...document.querySelectorAll('.machine-signal,.machine-block,.machine-gear,.parcel')].map(e=>{
                    const svg=e.ownerSVGElement,style=getComputedStyle(e),r=rect(e),s=rect(svg);
                    return {kind:e.getAttribute('class'),bounds:r,svgBounds:s,transform:style.transform,transformOrigin:style.transformOrigin,transformBox:style.transformBox,inside:r.x>=s.x&&r.y>=s.y&&r.right<=s.right&&r.bottom<=s.bottom};
                  });
                }"""))
                page.wait_for_timeout(150)
            snapshot["motionSamples"] = samples
            page.screenshot(path=str(out / f"settled-{state}.png"), timeout=20000)
            snapshots.append(snapshot)
        replay = page.get_by_role("button", name="Replay", exact=False)
        if replay.count():
            replay.first.click()
            page.wait_for_timeout(700)
            page.screenshot(path=str(out / "replay.png"), timeout=20000)
            result["replayClicked"] = True
        else:
            result["replayClicked"] = False
            page.reload(wait_until="networkidle")
            page.wait_for_timeout(700)
            page.screenshot(path=str(out / "replay-reload.png"), timeout=20000)
            result["replayReloaded"] = True
        page.emulate_media(reduced_motion="reduce")
        page.screenshot(path=str(out / "reduced.png"), timeout=20000)
        result.update({"states":snapshots,"pageErrors":errors,"screenshots":str(out)})
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=10)
(out / "browser.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
print(json.dumps({"run":args.run_id,"buildExitCode":result.get("buildExitCode"),"pageErrors":result.get("pageErrors"),"review":str(out)}))
raise SystemExit(1 if result.get("pageErrors") else 0)

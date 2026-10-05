#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Check actual timeline-machine native clicks and paint in the exported fixture."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
html = ROOT / 'projects/slidev-animejs-validation/artifacts/html'
out = ROOT / 'projects/diagram-compactness/artifacts/reviews/anime-fixture'
out.mkdir(parents=True, exist_ok=True)

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(html)))
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
origin = f'http://127.0.0.1:{server.server_address[1]}'
report = {'patternId':'slidev-animejs-timeline-machine','publishedUrl':'https://gvillarroel.github.io/skills/examples/slidev-animejs/#/20','states':[],'pageErrors':[]}
try:
    urlopen(origin, timeout=5).close()
    with sync_playwright() as runtime:
        options = {} if Path(runtime.chromium.executable_path).is_file() else {'channel':'msedge'}
        browser = runtime.chromium.launch(**options)
        context = browser.new_context(viewport={'width':1280,'height':800})
        context.grant_permissions(['screen-wake-lock'], origin=origin)
        page = context.new_page()
        page.on('pageerror', lambda error:report['pageErrors'].append(str(error)))
        page.goto(origin + '/#/20', wait_until='networkidle')
        selector = '.slidev-page-20 [data-pattern-id="slidev-animejs-timeline-machine"].svg-asset-slide'
        page.locator(selector).wait_for()
        for state in range(3):
            if state:
                page.keyboard.press('ArrowRight')
                page.wait_for_timeout(200)
            frame = {'state':state,'url':page.url,'samples':[]}
            if '/20' not in page.url:
                frame['leftTimelineSlide'] = True
                report['states'].append(frame)
                break
            page.screenshot(path=str(out / f'state-{state}.png'))
            for sample in range(35):
                frame['samples'].append(page.locator(selector).evaluate("""root=>{
                  const box=e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,right:b.right,bottom:b.bottom,width:b.width,height:b.height}};
                  const stage=root.querySelector('.svg-asset-stage'),s=box(stage), bases=[...root.querySelectorAll('.machine-cable-base')],cables=[...root.querySelectorAll('.machine-cable')];
                  return {stage:s,onScreen:s.x>=0&&s.right<=innerWidth&&s.y>=0&&s.bottom<=innerHeight,baseCount:bases.length,complete:bases.every((b,i)=>b.getAttribute('d')===cables[i].getAttribute('d')&&getComputedStyle(b).strokeDasharray==='none'&&Number(getComputedStyle(b).opacity)>=.8),movers:[...root.querySelectorAll('.machine-signal,.machine-gear,.machine-block')].map(e=>{const b=box(e);return{kind:e.getAttribute('class'),bounds:b,inside:b.x>=s.x&&b.right<=s.right&&b.y>=s.y&&b.bottom<=s.bottom,pivot:getComputedStyle(e).transformBox}})};
                }"""))
                if sample in (5,20,34):
                    page.screenshot(path=str(out / f'state-{state}-motion-{sample}.png'))
                page.wait_for_timeout(100)
            report['states'].append(frame)
        page.reload(wait_until='networkidle')
        if '/20' in page.url:
            page.locator(selector).wait_for()
            page.wait_for_timeout(300)
            report['replayBaseCount'] = page.locator(selector+' .machine-cable-base').count()
            page.screenshot(path=str(out / 'replay.png'))
            page.emulate_media(reduced_motion='reduce')
            page.screenshot(path=str(out / 'reduced.png'))
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=10)
report['passed'] = (len(report['states'])==3 and not report['pageErrors'] and report.get('replayBaseCount')==2 and all(not s.get('leftTimelineSlide') and all(f['onScreen'] and f['baseCount']==2 and f['complete'] and all(m['inside'] for m in f['movers']) for f in s['samples']) for s in report['states']))
(out / 'browser.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'passed':report['passed'],'pageErrors':report['pageErrors'],'urls':[s['url'] for s in report['states']],'review':str(out)}))
raise SystemExit(0 if report['passed'] else 1)

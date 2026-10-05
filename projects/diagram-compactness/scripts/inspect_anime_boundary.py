#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Independently inspect the six-main-node Anime routing boundary."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--deck', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, required=True)
args = parser.parse_args()
ROOT = Path(__file__).resolve().parents[3]
deck = args.deck.resolve()
deck.relative_to(ROOT)
out = args.output_dir.resolve()
out.relative_to(ROOT)
out.mkdir(parents=True, exist_ok=True)

class SpaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if not Path(self.translate_path(self.path)).exists() and not self.path.startswith('/assets/'):
            self.path = '/'
        super().do_GET()

    def log_message(self, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SpaHandler, directory=str(deck / 'dist')))
server.daemon_threads = True
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
origin = f'http://127.0.0.1:{server.server_address[1]}'
report = {'pageErrors': [], 'motion': [], 'observedRoutes': []}
try:
    urlopen(origin, timeout=5).close()
    with sync_playwright() as runtime:
        options = {} if Path(runtime.chromium.executable_path).is_file() else {'channel': 'msedge'}
        browser = runtime.chromium.launch(**options)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        context.grant_permissions(['screen-wake-lock'], origin=origin)
        page = context.new_page()
        page.on('pageerror', lambda error: report['pageErrors'].append(str(error)))
        page.goto(origin, wait_until='networkidle')
        flow = page.locator('.slidev-page-1 .connected-flow')
        page.wait_for_function("document.querySelector('.connected-flow')?.dataset.ready==='true'")
        flow.locator('svg').wait_for(state='visible')
        page.wait_for_timeout(500)
        report['geometry'] = flow.evaluate("""root=>{
          const svg=root.querySelector('svg'), frame=svg.getBoundingClientRect(), nodes=[...root.querySelectorAll('.flow-node')];
          const inside=(p,r)=>p.x>r.x&&p.x<r.right&&p.y>r.y&&p.y<r.bottom;
          const distance=(p,r)=>Math.hypot(Math.max(r.x-p.x,0,p.x-r.right),Math.max(r.y-p.y,0,p.y-r.bottom));
          const labels=[...root.querySelectorAll('.route-labels text')].map(t=>t.getBoundingClientRect()), hit=[], attribution=[], routes=[];
          for(const path of root.querySelectorAll('[data-route]')){
            const length=path.getTotalLength(),m=path.getScreenCTM(),scale=Math.hypot(m.a,m.b);
            routes.push({id:path.dataset.route,source:path.dataset.source,target:path.dataset.target,d:path.getAttribute('d')});
            for(const [role,d] of [['source',0],['target',length]]){
              const p=path.getPointAtLength(d).matrixTransform(m),id=path.dataset[role],intended=nodes.find(n=>n.dataset.node===id),gap=distance(p,intended.querySelector('rect').getBoundingClientRect())/scale;
              const nearest=nodes.every(n=>n===intended||distance(p,n.querySelector('rect').getBoundingClientRect())>distance(p,intended.querySelector('rect').getBoundingClientRect()));
              attribution.push({route:path.dataset.route,role,gap,nearest});
            }
            for(let d=0;d<=length;d+=2){const p=path.getPointAtLength(d).matrixTransform(m);for(const n of nodes)if(inside(p,n.querySelector('rect').getBoundingClientRect()))hit.push(['stroke-node',path.dataset.route,n.dataset.node]);for(const label of labels)if(inside(p,label))hit.push(['stroke-label',path.dataset.route]);}
            const p=path.getPointAtLength(length),prev=path.getPointAtLength(length-.5),dx=p.x-prev.x,dy=p.y-prev.y,n=Math.hypot(dx,dy),ux=dx/n,uy=dy/n;
            for(const q of [p,new DOMPoint(p.x-10*ux+5*uy,p.y-10*uy-5*ux),new DOMPoint(p.x-10*ux-5*uy,p.y-10*uy+5*ux)]){
              const screen=q.matrixTransform(m);if(!inside(screen,frame))hit.push(['head-frame',path.dataset.route]);for(const node of nodes)if(inside(screen,node.querySelector('rect').getBoundingClientRect()))hit.push(['head-node',path.dataset.route,node.dataset.node]);for(const label of labels)if(inside(screen,label))hit.push(['head-label',path.dataset.route]);
            }
          }
          return {width:svg.getAttribute('width'),height:svg.getAttribute('height'),viewBox:svg.getAttribute('viewBox'),onScreen:frame.x>=0&&frame.right<=innerWidth&&frame.y>=0&&frame.bottom<=innerHeight,parcelFill:getComputedStyle(root.querySelector('.parcel')).fill,routes,attribution,hit,labels:nodes.map(n=>{const t=n.querySelector('text'),r=n.querySelector('rect').getBoundingClientRect(),b=t.getBoundingClientRect();return {text:t.textContent,font:getComputedStyle(t).fontSize,fit:b.x>=r.x+3&&b.right<=r.right-3&&b.y>=r.y+3&&b.bottom<=r.bottom-3}})};
        }""")
        geometry = report['geometry']
        assert geometry['onScreen'] and float(geometry['width']) <= 850, geometry
        assert geometry['parcelFill'] == 'rgb(158, 27, 50)', geometry
        assert len(geometry['routes']) == 8 and not geometry['hit'], geometry
        assert len(geometry['labels']) == 7 and all(n['font'] == '18px' and n['fit'] for n in geometry['labels']), geometry
        assert all(a['nearest'] and 3.5 <= a['gap'] <= 7.5 for a in geometry['attribution']), geometry
        page.screenshot(path=str(out / 'state-0.png'))
        observed = set()
        for state in (1, 2):
            page.keyboard.press('ArrowRight')
            page.wait_for_timeout(100)
            assert flow.get_attribute('data-click-state') == str(state)
            for _ in range(75):
                sample = flow.evaluate("""root=>{
                  const token=root.querySelector('.parcel'),id=token.dataset.motionRoute;if(token.getAttribute('opacity')!=='1'||!id)return null;
                  const b=token.getBoundingClientRect(),path=root.querySelector(`[data-route="${id}"]`),m=path.getScreenCTM(),svg=root.querySelector('svg').getBoundingClientRect();
                  let nearest=Infinity;for(let d=0;d<path.getTotalLength();d+=1){const p=path.getPointAtLength(d).matrixTransform(m);nearest=Math.min(nearest,Math.hypot(p.x-(b.x+b.width/2),p.y-(b.y+b.height/2)));}
                  const overlaps=[...root.querySelectorAll('.flow-node rect,.route-labels text')].filter(e=>{const r=e.getBoundingClientRect();return b.x<r.right&&b.right>r.x&&b.y<r.bottom&&b.bottom>r.y}).length;
                  const end=path.getPointAtLength(path.getTotalLength()).matrixTransform(m);
                  return {route:id,nearest,overlaps,inside:b.x>=svg.x&&b.right<=svg.right&&b.y>=svg.y&&b.bottom<=svg.bottom,headDistance:Math.hypot(end.x-(b.x+b.width/2),end.y-(b.y+b.height/2))};
                }""")
                if sample:
                    if sample['route'] not in observed:
                        page.screenshot(path=str(out / f"motion-{sample['route']}.png"))
                    observed.add(sample['route'])
                    report['motion'].append(sample)
                    assert sample['nearest'] < 2 and not sample['overlaps'] and sample['inside'] and sample['headDistance'] > 15, sample
                page.wait_for_timeout(100)
            page.screenshot(path=str(out / f'state-{state}.png'))
        assert observed == {r['id'] for r in geometry['routes']}, observed
        flow.get_by_role('button', name='Replay').click()
        page.wait_for_timeout(250)
        assert flow.locator('.parcel').get_attribute('opacity') == '1'
        assert flow.locator('.parcel').get_attribute('data-motion-route') == 'return'
        page.screenshot(path=str(out / 'replay.png'))
        page.emulate_media(reduced_motion='reduce')
        page.wait_for_timeout(100)
        assert flow.locator('.parcel').get_attribute('opacity') == '0'
        assert flow.locator('[data-route]').count() == 8
        page.screenshot(path=str(out / 'reduced.png'))
        assert not report['pageErrors'], report['pageErrors']
        report['observedRoutes'] = sorted(observed)
        report['passed'] = True
        browser.close()
finally:
    server.shutdown()
    server.server_close()
    thread.join(timeout=10)
    (out / 'browser.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'passed': report.get('passed', False), 'width': report['geometry']['width'], 'height': report['geometry']['height'], 'routes': len(report['observedRoutes']), 'motionSamples': len(report['motion'])}))

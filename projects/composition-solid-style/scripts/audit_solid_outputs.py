#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Inspect actual composed/animated paint and record responsive screenshots."""
import http.server,threading,json,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/composition-solid-style/artifacts/browser';OUT.mkdir(parents=True,exist_ok=True)
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
CHECK=r'''({kind}) => {
  const hex = rgb => {const match=rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);return match?'#'+match.slice(1).map(v=>Number(v).toString(16).padStart(2,'0')).join(''):rgb.toLowerCase();};
  const category = kind==='video'?'[data-surface-style="solid"]':kind==='poster'?'[data-node-box="true"][fill]:not([fill="none"]),[data-name-panel="true"], [data-period-label="true"]':kind==='hierarchy'?'#map .mark':'[data-dependency-node],.structural-node circle[fill]:not([fill="none"]),.world-module-node-core,.district-hub';
  const marks=[...document.querySelectorAll(category)].filter(el=>getComputedStyle(el).fill!=='none');
  const outlines=marks.filter(el=>el.dataset.categoryStyle!=='overflow'&&getComputedStyle(el).stroke!=='none'&&Number.parseFloat(getComputedStyle(el).strokeWidth)>0).map(el=>el.id||el.getAttribute('data-dependency-node')||el.tagName);
  const texts=kind==='poster'?[...document.querySelectorAll('text[data-owner]')].filter(t=>t.getAttribute('data-background')&&t.getAttribute('data-owner')!=='page'):kind==='hierarchy'?[...document.querySelectorAll('#map .label,#map .center-text')]:kind==='compose'?[...document.querySelectorAll('text')].filter(t=>(t.getAttribute('fill')||'').startsWith('var(--on-value')):[...document.querySelectorAll('svg text')].filter(t=>t.style.fill);
  const nonBinary=texts.filter(t=>!['#000000','#ffffff'].includes(hex(getComputedStyle(t).fill))).map(t=>t.textContent.slice(0,40));
  return {markCount:marks.length,textCount:texts.length,overflowCount:marks.filter(el=>el.dataset.categoryStyle==='overflow').length,outlines,nonBinary,ok:marks.length>0&&outlines.length===0&&nonBinary.length===0};
}'''
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1600,'height':1000})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    cases=[('compose','skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/inference-pulse.svg'),('compose','skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/heatwave-tree.svg'),('hierarchy','skills/hierarchy-lens/assets/examples/hierarchy-lens/analytical.html')]
    cases += [('poster',f'skills/usefulcharts-style/assets/examples/usefulcharts-style/{stem}.svg') for stem in ['aurelian-families','atlas-of-inquiry','five-regional-histories']]
    for kind,path in cases:
        page.goto(base+path);page.wait_for_timeout(250)
        if kind=='compose':page.evaluate('() => {svgSync.pause();svgSync.pauseCamera();svgSync.reset();}')
        result=page.evaluate(CHECK,{'kind':kind});result.update(path=path,kind=kind)
        page.screenshot(path=str(OUT/(Path(path).stem+'.png')),full_page=False,animations='disabled',timeout=10000)
        results.append(result)
    page.goto(base+'skills/video/assets/examples/ai-concept-videos/index.html')
    page.wait_for_function('typeof window.renderConceptFrame === "function"')
    ids=page.evaluate('AI_CONCEPTS.map(c=>c.id)')
    for cid in ids:
        for time in [0,12,24,48,80,110,119]:
            page.evaluate('([cid,time])=>renderConceptFrame(cid,time,{capture:true})',[cid,time])
            r=page.evaluate(CHECK,{'kind':'video'});r.update(kind='video',concept=cid,time=time);results.append(r)
        if cid==ids[0]:page.screenshot(path=str(OUT/'video-llm.png'))
    # Responsive gallery chrome must stay navigable after its border change.
    page.set_viewport_size({'width':500,'height':850});page.reload();page.wait_for_function('typeof window.renderConceptFrame === "function"');page.screenshot(path=str(OUT/'video-mobile.png'))
    browser.close()
server.shutdown()
report={'states':len(results),'errors':errors,'results':results,'passed':not errors and all(r['ok'] for r in results)}
(OUT/'audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'states':report['states'],'errors':errors,'failures':[r for r in results if not r['ok']],'passed':report['passed']},indent=2))
if not report['passed']:raise SystemExit(1)

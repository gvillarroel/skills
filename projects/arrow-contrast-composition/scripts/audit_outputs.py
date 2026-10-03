#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "Pillow>=11,<13"]
# ///
"""Audit actual arrow paint in delivery/focus/zoom/movie states; retain every finding."""
import functools,http.server,threading,json,sys,importlib.util,copy
from pathlib import Path
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/arrow-contrast-composition/artifacts/browser';OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}/'
results=[];errors=[]
def inspect(page,label,**state):
    r=page.evaluate(ARROW_AUDIT,{'selector':'#concept-svg' if state.get('kind')=='video' else 'svg'});r.update(label=label,**state);results.append(r)
    (OUT/'latest.json').write_text(json.dumps({'states':len(results),'errors':errors,'results':results},indent=2)+'\n',encoding='utf-8')
    return r
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1600,'height':1200});page.on('pageerror',lambda e:errors.append(str(e)))
    for stem in ['inference-pulse','heatwave-tree']:
        path=f'skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/{stem}.svg'
        page.goto(base+path);page.wait_for_function('typeof window.svgSync === "object"');page.evaluate('() => {svgSync.pause();svgSync.pauseCamera();}')
        page.wait_for_timeout(220);inspect(page,stem,kind='compose',state='resting')
        page.screenshot(path=str(OUT/(stem+'-resting.png')))
        plan=page.evaluate('svgSync.getPlan()')
        for focus in (plan.get('focusGroups') or [])[:2]:
            page.evaluate('id=>svgSync.setFocus(id)',focus['id']);page.wait_for_timeout(220);inspect(page,stem,kind='compose',state='focus-'+focus['id'])
        if plan.get('world'):
            for anchor in plan['navigation']['anchors'][:3]:
                page.evaluate('id=>svgSync.navigateTo(id,{updateHash:false})',anchor['id']);page.wait_for_timeout(220);inspect(page,stem,kind='compose',state='zoom-'+anchor['id'])
        page.emulate_media(reduced_motion='reduce');page.reload();page.wait_for_function('typeof window.svgSync === "object"');page.evaluate('() => {svgSync.pause();svgSync.pauseCamera();}');inspect(page,stem,kind='compose',state='reduced-motion');page.emulate_media(reduced_motion='no-preference')
    for stem in ['aurelian-families','atlas-of-inquiry','five-regional-histories']:
        page.goto(base+f'skills/usefulcharts-style/assets/examples/usefulcharts-style/{stem}.svg');page.evaluate('document.fonts.ready')
        vb=page.evaluate('(()=>{const b=document.querySelector("svg").viewBox.baseVal;return [b.width,b.height]})()')
        page.set_viewport_size({'width':int(vb[0]),'height':int(vb[1])});inspect(page,stem,kind='poster',state='native-scale');page.screenshot(path=str(OUT/(stem+'.png')))
    page.set_viewport_size({'width':1920,'height':1080})
    page.goto(base+'projects/arrow-contrast-composition/artifacts/hyperframes/index.html');page.wait_for_function('typeof window.explainer === "object"')
    for time,rate in [(0,0),(4,2),(6,4),(8,5),(12,1),(16,5)]:
        page.evaluate('([time,rate])=>{explainer.seek(time);explainer.setInputs({rate});}',[time,rate]);inspect(page,'flow-and-storage',kind='hyperframes',time=time,rate=rate)
    page.screenshot(path=str(OUT/'hyperframes-maximum.png'))
    page.set_viewport_size({'width':1600,'height':1200})
    page.goto(base+'skills/video/assets/examples/ai-concept-videos/index.html');page.wait_for_function('typeof window.renderConceptFrame === "function"')
    ids=page.evaluate('AI_CONCEPTS.map(c=>c.id)')
    for cid in ids:
        for time in [1,6,14,24,36,48,72,80,96,110,119]:
            page.evaluate('([cid,time])=>renderConceptFrame(cid,time,{capture:true})',[cid,time]);inspect(page,cid,kind='video',time=time)
        if cid==ids[0]:page.screenshot(path=str(OUT/'video-llm.png'))
    browser.close()
server.shutdown()
summary={'states':len(results),'errors':errors,'shafts':sum(r['shaftCount'] for r in results),'heads':sum(r['headCount'] for r in results),
         'failures':[{'label':r['label'],**{k:r[k] for k in ['kind','state','time','rate'] if k in r},'issues':r['issues']} for r in results if r['issues']]}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({**summary,'failures':[{'label':f['label'],'issueCount':len(f['issues']),'kinds':sorted({i['kind'] for i in f['issues']})} for f in summary['failures']]},indent=2))
raise SystemExit(bool(summary['failures'] or errors))

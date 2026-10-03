#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inventory enabled Hierarchy Lens navigation glyphs; no diagram arrows are authored."""
import json,functools,http.server,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-composition/artifacts/hierarchy-controls';OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
js=r'''()=>{const rgba=s=>{const c=document.createElement('canvas').getContext('2d');c.fillStyle=s;c.fillRect(0,0,1,1);return [...c.getImageData(0,0,1,1).data]},lum=c=>c.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0),records=[];for(const e of document.querySelectorAll('button')){if(!/[←→↑↓]/.test(e.textContent)||e.disabled||!e.getBoundingClientRect().width||!e.getBoundingClientRect().height)continue;const css=getComputedStyle(e);let bg=[255,255,255],a=1;for(let n=e;n;n=n.parentElement){const s=getComputedStyle(n),p=rgba(s.backgroundColor);a*=+s.opacity;if(p[3]===255){bg=p.slice(0,3);break}}const paint=rgba(css.color),ink=bg.map((v,i)=>v*(1-a*paint[3]/255)+paint[i]*a*paint[3]/255),x=lum(bg),y=lum(ink);records.push({id:e.id||e.getAttribute('aria-label'),text:e.textContent,background:bg,paint:ink,ratio:(Math.max(x,y)+.05)/(Math.min(x,y)+.05)});}return records;}'''
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1500,'height':1000})
 for name in ['index','radial','organic','analytical']:
  page.goto(f'http://127.0.0.1:{server.server_port}/skills/hierarchy-lens/assets/examples/hierarchy-lens/{name}.html');page.wait_for_timeout(100)
  if page.locator('#info').count():page.locator('#info').click()
  for state in ['resting','hover','keyboard-focus']:
   for e in page.locator('button').all():
    if e.is_visible() and e.is_enabled() and any(c in e.inner_text() for c in '←→↑↓'):
     if state=='hover':e.hover()
     if state=='keyboard-focus':e.focus()
     r=page.evaluate(js);assert r and min(x['ratio'] for x in r)>=3,(name,state,r);results.append({'page':name,'state':state,'neutralTokensAvailableIn':['colorset1','colorset2'],'records':r})
 browser.close()
server.shutdown();assert results;(OUT/'results.json').write_text(json.dumps({'passed':True,'cases':results,'scope':'Enabled readable navigation glyphs only; disabled controls are inactive affordances. No hierarchy diagram connector arrows exist.'},indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'cases':len(results),'minimum':min(x['ratio'] for r in results for x in r['records'])}))

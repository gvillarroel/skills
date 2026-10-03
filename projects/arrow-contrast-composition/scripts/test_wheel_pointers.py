#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inspect existing probability-wheel selector glyphs at readable settled times."""
import functools,http.server,threading,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-composition/artifacts/wheel-pointers';OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1200});page.goto(f'http://127.0.0.1:{server.server_port}/skills/video/assets/examples/ai-concept-videos/index.html');page.wait_for_function('typeof renderConceptFrame==="function"')
 for cid in page.evaluate('AI_CONCEPTS.map(c=>c.id)'):
  for t in range(12,115,4):
   page.evaluate('([cid,t])=>renderConceptFrame(cid,t,{capture:true})',[cid,t])
   count=page.evaluate(r'''()=>{let count=0;for(const p of document.querySelectorAll('#concept-svg path')){if(p.closest('[data-arrow-id]'))continue;const s=getComputedStyle(p),d=p.getAttribute('d'),n=(d?.match(/-?\d+(?:\.\d+)?/g)||[]).map(Number);if(n.length!==6||!d.trim().endsWith('Z')||s.stroke!=='rgb(255, 255, 255)'||!['rgb(158, 27, 50)','rgb(158, 27, 50)'].includes(s.fill)||n[1]<=n[3]||n[3]!==n[5]||Math.abs(n[2]+n[4]-2*n[0])>.01)continue;let a=1;for(let e=p;e;e=e.parentElement)a*=+getComputedStyle(e).opacity;if(a<.9)continue;const circle=p.nextElementSibling,isTip=circle?.tagName==='circle'&&Math.abs(+circle.getAttribute('cx')-n[0])<.01&&Math.abs(+circle.getAttribute('cy')-n[1])<.01;const g=document.createElementNS('http://www.w3.org/2000/svg','g');p.before(g);g.dataset.arrowId='wheel-pointer-'+count++;g.append(p);p.dataset.arrowHead='true';if(isTip){g.append(circle);circle.dataset.arrowHead='true';}}return count;}''')
   if not count:continue
   r=page.evaluate(ARROW_AUDIT,{'selector':'#concept-svg'});assert not r['issues'],(cid,t,r['issues']);results.append({'id':cid,'time':t,'pointers':count,'audit':r});page.screenshot(path=str(OUT/(cid+f'-{t}.png')))
 browser.close()
server.shutdown();assert results,'No readable wheel pointers were tested';(OUT/'results.json').write_text(json.dumps({'passed':True,'cases':results},indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'cases':len(results),'pointers':sum(r['pointers'] for r in results)}))

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Check clear gutter geometry, arrival bearing and actual paint in both palettes."""
import http.server,threading,functools,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-composition/artifacts/video-template';OUT.mkdir(parents=True,exist_ok=True)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();url=f'http://127.0.0.1:{server.server_port}/'
palettes=json.loads((ROOT/'skills/video/assets/palettes/colorsets.json').read_text(encoding='utf-8'))['colorsets'];results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':640,'height':220})
 page.goto(url+'skills/video/assets/examples/ai-concept-videos/index.html');page.wait_for_function('typeof renderConceptFrame==="function"')
 page.evaluate("async url=>{const library=await import(url);window.arrowLibrary=library;window.wrapper=function wrapper(node){return {append(tag){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);node.appendChild(e);return wrapper(e);},attr(key,value){node.setAttribute(key,value);return this;},node(){return node;}}};}",url+'skills/video/assets/templates/svg-arrows.js')
 for mode in ['colorset1','colorset2']:
  page.evaluate('({allowed,color})=>{document.body.innerHTML=\'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="220" viewBox="0 0 640 220"><rect width="640" height="220" fill="#ffffff"/><rect x="20" y="70" width="70" height="50" fill="#9e1b32"/><rect x="480" y="70" width="70" height="50" fill="#333e48"/><rect x="260" y="50" width="80" height="100" fill="#333e48"/></svg>\';document.body.style.margin=\'0\';const svg=document.querySelector(\'svg\');arrowLibrary.drawArrow(svg,{x:55,y:95},{x:515,y:95},color,1,4,12);arrowLibrary.finishArrows(svg,{allowed,canvas:\'#ffffff\'});}',{'allowed':palettes[mode]['allowed'],'color':'#e8002a' if mode=='colorset1' else '#f1c319'})
  report=page.evaluate(ARROW_AUDIT);assert not report['issues'],report
  geometry=page.evaluate("()=>{const g=document.querySelector('[data-arrow-id]'),h=g.querySelector('[data-arrow-head]'),p=h.getPointAtLength(0),shaft=g.querySelector('[data-arrow-shaft]'),end=shaft.getPointAtLength(shaft.getTotalLength()),previous=shaft.getPointAtLength(Math.max(0,shaft.getTotalLength()-2));return {tip:{x:p.x,y:p.y},bearing:{x:end.x-previous.x,y:end.y-previous.y},paint:g.dataset.arrowPaint,declared:g.dataset.arrowPoints,svg:document.querySelector('svg').outerHTML};}")
  assert geometry['tip']['x']<480 and abs(geometry['tip']['y']-95)<.01,geometry
  assert geometry['bearing']['x']>1.9 and abs(geometry['bearing']['y'])<.01,geometry
  (OUT/(mode+'.svg')).write_text(geometry.pop('svg'),encoding='utf-8');page.screenshot(path=str(OUT/(mode+'.png')));results.append({'palette':mode,'geometry':geometry,'audit':report})
 browser.close()
server.shutdown();(OUT/'results.json').write_text(json.dumps({'passed':True,'results':results},indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'cases':len(results)}))

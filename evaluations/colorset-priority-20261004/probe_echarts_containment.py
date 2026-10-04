#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55"]
# ///
"""Diagnose native SVG symbol containment without changing sampled outputs."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
run = root / 'evaluations/runs/20261004-cs1-priority-echarts-animated-svg-contract-contracts-luna-r2-1'
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    page.goto((run / 'workspace/priority.white.static.svg').as_uri())
    page.wait_for_timeout(500)
    result = page.evaluate(r'''() => {
      const label=Array.from(document.querySelectorAll('text')).find(e=>e.textContent==='Group 0'),b=label.getBoundingClientRect(),point={x:b.x+b.width/2,y:b.y+b.height/2};
      return {point,label:label.outerHTML,shapes:Array.from(document.querySelectorAll('path,rect')).slice(0,22).map(e=>{const b=e.getBoundingClientRect(),local=e.getBBox(),m=e.getScreenCTM(),p=new DOMPoint(point.x,point.y).matrixTransform(m.inverse()),cs=getComputedStyle(e);return {html:e.outerHTML,fill:cs.fill,b:{x:b.x,y:b.y,width:b.width,height:b.height},native:{x:local.x,y:local.y,width:local.width,height:local.height},matrix:{a:m.a,b:m.b,c:m.c,d:m.d,e:m.e,f:m.f},pointLocal:{x:p.x,y:p.y},isPointInFill:e.isPointInFill?.(p)};})};
    }''')
    browser.close()
output=run/'native-containment-probe.json'
output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))

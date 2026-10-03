#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Inspect the equipment direction glyph at explicit SMIL delivery times."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-custom/artifacts'
records=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge',args=['--enable-webgl','--use-gl=angle','--use-angle=swiftshader']);page=browser.new_page(viewport={'width':1280,'height':900})
 for palette in ('colorset1','colorset2'):
  page.goto((OUT/'data'/f'pid-{palette}.html').as_uri());page.wait_for_timeout(2500)
  page.evaluate(Path(__file__).with_name('glyph_audit.ts').read_text(encoding='utf-8'))
  for second in (3.1,4.8,6.2):
   page.locator('svg').evaluate('(svg,t)=>{svg.pauseAnimations();svg.setCurrentTime(t)}',second)
   page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
   records.append({'palette':palette,'second':second,'glyphs':page.evaluate('window.auditDirectionalGlyphs()')})
 browser.close()
(OUT/'data/pid-glyph-times.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,indent=2))

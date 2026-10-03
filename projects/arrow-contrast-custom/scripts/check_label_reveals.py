#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Verify readable final label ink without altering hidden/reveal/semantic alpha."""
import importlib.util,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-custom/artifacts/data'
spec=importlib.util.spec_from_file_location('adapter',ROOT/'skills/d3/scripts/colorset_adapter.py');adapter=importlib.util.module_from_spec(spec);spec.loader.exec_module(adapter)
source='''<html><body><svg viewBox="0 0 760 140" width="1140">
<g id="smil" opacity="0"><animate attributeName="opacity" values="0;1" begin="2s" dur="2s" fill="freeze"/><rect x="10" y="20" width="90" height="90" fill="#9e1b32"/><text x="55" y="70" text-anchor="middle">SMIL</text></g>
<g id="css" style="opacity:0;animation:reveal 2s linear 2s forwards"><rect x="130" y="20" width="90" height="90" fill="#9e1b32"/><text x="175" y="70" text-anchor="middle">CSS</text></g>
<g id="wa" opacity="0"><rect x="250" y="20" width="90" height="90" fill="#9e1b32"/><text x="295" y="70" text-anchor="middle">WA</text></g>
<g id="hidden" opacity="0"><rect x="370" y="20" width="90" height="90" fill="#9e1b32"/><text x="415" y="70" text-anchor="middle">Hidden</text></g>
<g id="semantic" data-opacity-role="semantic" opacity=".3"><rect x="490" y="20" width="90" height="90" fill="#9e1b32"/><text x="535" y="70" text-anchor="middle">Alpha</text></g>
<g id="growing" data-text-backing="circle"><circle cx="660" cy="65" r="45" fill="#9e1b32"><animate attributeName="r" from="5" to="45" begin="2s" dur="2s" fill="freeze"/></circle><text x="660" y="70" text-anchor="middle">Growing</text></g>
</svg><style>@keyframes reveal{from{opacity:0}to{opacity:1}}</style></body></html>'''
path=OUT/'label-reveals.html';path.write_text(adapter.adapt_artifact(source,'colorset2'),encoding='utf-8')
rows=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge');page=browser.new_page();page.goto(path.as_uri());page.wait_for_function('window.D3SolidStyle')
 page.evaluate('''() => {window.labelAnimation=document.querySelector('#wa').animate([{opacity:0},{opacity:1}],{duration:2000,delay:2000,fill:'forwards'});window.labelAnimation.pause();window.labelAnimation.currentTime=0;D3SolidStyle.normalize(document.querySelector('svg'));}''')
 for second in (0,1,4.1):
  page.evaluate('''time => {const svg=document.querySelector('svg');svg.pauseAnimations();svg.setCurrentTime(time);labelAnimation.currentTime=time*1000;for(const animation of document.querySelector('#css').getAnimations()){animation.pause();animation.currentTime=time*1000;}}''',second)
  page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  actual=page.locator('svg>g').evaluate_all("es=>es.map(e=>({id:e.id,alpha:+getComputedStyle(e).opacity,text:getComputedStyle(e.querySelector('text')).fill,radius:e.querySelector('circle')?.r.animVal.value}))")
  indexed={r['id']:r for r in actual}
  assert all(indexed[key]['text']=='rgb(255, 255, 255)' for key in ('smil','css','wa','growing')),actual
  assert indexed['hidden']['alpha']==0 and indexed['semantic']['alpha']==.3,actual
  assert indexed['semantic']['text']=='rgb(0, 0, 0)',actual
  assert all(indexed[key]['alpha']==(0 if second<2 else 1) for key in ('smil','css','wa')),actual
  rows.append({'second':second,'passed':True,'groups':actual})
 browser.close()
report={'date':'2026-10-03','passed':True,'rows':rows}
(ROOT/'evaluations/arrow-contrast-custom/label-reveals-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'stateCount':len(rows),'groupChecks':18}))

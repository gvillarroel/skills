#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Retain focused label backing candidates and settled bowtie shaft diagnostics."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-custom/artifacts/data'
rows=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge');page=browser.new_page(viewport={'width':1440,'height':1100})
 page.goto((ROOT/'skills/d3/assets/examples/d3-animated-svg-colorset2/index.html').as_uri());page.wait_for_function("document.querySelectorAll('svg[data-fill-style=\"solid-first\"]').length>200");page.wait_for_timeout(4500)
 card=page.locator('[data-example="process-control-loop"]');card.scroll_into_view_if_needed();card.locator('[data-expand]').focus();page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
 labels=card.locator('[data-instrument-id] text').evaluate_all('''es=>es.map(text=>{const box=text.getBoundingClientRect(),center=new DOMPoint(box.x+box.width/2,box.y+box.height/2);return {instrument:text.closest('[data-instrument-id]').dataset.instrumentId,text:text.textContent,paint:getComputedStyle(text).fill,bounds:box.toJSON(),backings:[...text.closest('svg').querySelectorAll('rect,circle,ellipse,polygon,path')].filter(shape=>{try{return shape.isPointInFill(center.matrixTransform(shape.getScreenCTM().inverse()))}catch{return false}}).map(shape=>({class:shape.getAttribute('class'),fill:getComputedStyle(shape).fill,alpha:getComputedStyle(shape).opacity,bounds:shape.getBoundingClientRect().toJSON()}))}})''')
 rows.append({'phase':'focused','labels':labels})
 page.evaluate(Path(__file__).with_name('arrow_audit.ts').read_text(encoding='utf-8'))
 for second in (3.1,4.8,6.2,7,8,9):
  page.locator('[data-example="bowtie-barriers"] svg').evaluate('(svg,t)=>{svg.pauseAnimations();svg.setCurrentTime(t)}',second);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
  arrows=[a for a in page.evaluate('window.auditRenderedArrows()') if 'bowtie-barriers' in a['pattern'] and a['shaftMinimumContrast']<3]
  rows.append({'second':second,'lowBowtie':[{k:v for k,v in a.items() if k not in ('shaftSamples','headSamples')}|{'lowSamples':[s for s in a['shaftSamples'] if s['contrast']<3]} for a in arrows]})
 browser.close()
(OUT/'gallery-diagnostics.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows,indent=2))

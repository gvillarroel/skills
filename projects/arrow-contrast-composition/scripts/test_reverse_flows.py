#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inspect negative flow markers from actual compiled/composed assets in both palettes."""
import sys,json,copy
from pathlib import Path
from types import SimpleNamespace
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'skills/compose-synchronized-svg/scripts'))
import test_synchronized_svg_tools as tests
import compile_synchronized_svg_plan as compiler
import compose_synchronized_svg as composer
OUT=ROOT/'projects/arrow-contrast-composition/artifacts/reverse-flows';OUT.mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1200})
 for mode in ['editorial','colorset2']:
  brief=tests.SynchronizedSvgToolTests().tiny_edge_brief();brief['theme']={'preset':mode}
  service=next(m for m in brief['modules'] if m['id']=='service-mix');service['assetType']='comparison-table';service.pop('stackTotal',None)
  next(m for m in brief['derived'] if m['id']=='origin-rate')['compute']={'op':'multiply','args':[{'ref':'request-rate'},-.5]}
  next(m for m in brief['derived'] if m['id']=='edge-served-rate')['compute']={'op':'subtract','args':[{'ref':'request-rate'},{'ref':'origin-rate'}]}
  plan,_=compiler.compile_brief(brief);spec=OUT/(mode+'.json');spec.write_text(json.dumps(plan),encoding='utf-8');svg=OUT/(mode+'.svg');composer.compose(SimpleNamespace(spec=spec,output=svg,report=None,force=True))
  page.goto(svg.as_uri());page.wait_for_function('typeof svgSync==="object"');page.evaluate('()=>{svgSync.pause();svgSync.pauseCamera();}')
  for state in ['resting','focus','reduced-motion']:
   if state=='focus':page.evaluate('id=>svgSync.setFocus(id)',plan['focusGroups'][0]['id'])
   if state=='reduced-motion':page.emulate_media(reduced_motion='reduce');page.reload();page.wait_for_function('typeof svgSync==="object"');page.evaluate('()=>{svgSync.pause();svgSync.pauseCamera();}')
   r=page.evaluate(ARROW_AUDIT);assert any('request-flow' in (x['id'] or '') or x['kind']=='head' for x in r['records']),r;assert not r['issues'],r['issues'];results.append({'palette':mode,'state':state,**r})
  page.screenshot(path=str(OUT/(mode+'.png')));page.emulate_media(reduced_motion='no-preference')
 browser.close()
(OUT/'results.json').write_text(json.dumps({'passed':True,'states':results},indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'states':len(results)}))

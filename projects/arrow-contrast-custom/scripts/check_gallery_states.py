#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Inspect actual D3 direction marks in focused and expanded reading views."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];rows=[];errors=[]
parser=argparse.ArgumentParser();parser.add_argument('--items',nargs='+',default=['flowchart-dag','sequence-lifelines','state-machine','process-control-loop','bowtie-barriers','vector-field']);args=parser.parse_args()
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge');page=browser.new_page(viewport={'width':1440,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)))
 for gallery in ('d3-animated-svg-cs1','d3-animated-svg-colorset2'):
  page.goto((ROOT/'skills/d3/assets/examples'/gallery/'index.html').as_uri());page.wait_for_function("document.querySelectorAll('svg[data-fill-style=\"solid-first\"]').length>200");page.wait_for_timeout(4500)
  for helper in ('arrow_audit.ts','glyph_audit.ts','label_audit.ts'):page.evaluate(Path(__file__).with_name(helper).read_text(encoding='utf-8'))
  for item in args.items:
   card=page.locator(f'[data-example="{item}"]');card.scroll_into_view_if_needed();button=card.locator('[data-expand]');button.focus()
   for state in ('focus','expanded','fit'):
    if state!='focus':button.click()
    page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    prefix='d3-'+item+'-'
    arrows=[a for a in page.evaluate('window.auditRenderedArrows()') if a['pattern'].startswith(prefix)]
    glyphs=[g for g in page.evaluate('window.auditDirectionalGlyphs()') if g['pattern'].startswith(prefix)]
    ports=[a['targetPortAudit'] for a in arrows if a['targetPortAudit']]
    failures=[a['owner'] for a in arrows if a['headContrast']<3 or a['shaftMinimumContrast']<3 or a['headHidden'] or a['unresolved'] or a['targetPortAudit'] and not a['targetPortAudit']['passed']]
    glyph_failures=[g['role'] for g in glyphs if min(g.get('contrast',21),g.get('headContrast',21),g.get('shaftContrast',21))<3]
    labels=page.evaluate('window.auditInstrumentLabels()') if item=='process-control-loop' else []
    callouts=page.evaluate('window.auditCalloutLabels()') if item=='bowtie-barriers' else []
    label_failures=[label.get('instrumentId',label.get('calloutId')) for label in labels+callouts if not label['passed']]
    rows.append({'gallery':gallery,'item':item,'state':state,'markerArrowCount':len(arrows),'glyphCount':len(glyphs),'targetPorts':ports,'instrumentLabels':labels,'calloutLabels':callouts,'failures':failures+glyph_failures+label_failures,'passed':not failures and not glyph_failures and not label_failures and (item!='bowtie-barriers' or len(callouts)==2) and len(arrows)+len(glyphs)>0})
 browser.close()
report={'date':'2026-10-03','passed':all(r['passed'] for r in rows) and not errors,'stateCount':len(rows),'errors':errors,'rows':rows}
stem='bowtie-states' if args.items==['bowtie-barriers'] else 'gallery-states'
(ROOT/f'evaluations/arrow-contrast-custom/{stem}-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if not report['passed']:print(json.dumps([r for r in rows if not r['passed']],indent=2))
raise SystemExit(0 if report['passed'] else 1)

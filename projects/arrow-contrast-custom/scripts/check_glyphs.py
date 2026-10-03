#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Retain independently inspected D3 direction symbols in both palettes."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=('before','after'),default='after');args=parser.parse_args()
records=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge')
 page=browser.new_page(viewport={'width':1440,'height':1000})
 for gallery in ('d3-animated-svg-cs1','d3-animated-svg-colorset2','pid-colorset1','pid-colorset2'):
  path=ROOT/'skills/d3/assets/examples'/gallery/'index.html' if gallery.startswith('d3-') else ROOT/'projects/arrow-contrast-custom/artifacts/data'/f'{gallery}.html'
  page.goto(path.as_uri())
  page.wait_for_function("document.querySelectorAll('svg[data-fill-style=\"solid-first\"]').length>"+('200' if gallery.startswith('d3-') else '0'))
  page.wait_for_timeout(3000);page.evaluate(Path(__file__).with_name('glyph_audit.ts').read_text(encoding='utf-8'))
  rows=page.evaluate('window.auditDirectionalGlyphs()')
  records.append({'gallery':gallery,'glyphCount':len(rows),'lowContrastCount':sum(min(r.get('contrast',21),r.get('headContrast',21),r.get('shaftContrast',21))<3 for r in rows),'rows':rows})
 browser.close()
report={'phase':args.phase,'records':records}
(ROOT/f'evaluations/arrow-contrast-custom/glyphs-{args.phase}-20261003.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps([{k:v for k,v in r.items() if k!='rows'} for r in records],indent=2))

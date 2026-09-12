#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Compare a complete institutional candidate with its baseline and reference."""

import argparse
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
NS={'s':'http://www.w3.org/2000/svg'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--svg',type=Path,required=True);p.add_argument('--before',default='0be67c64');p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    base='skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry'
    old=json.loads(subprocess.check_output(['git','show',args.before+':'+base+'.json'],cwd=ROOT))
    new=json.loads(args.source.read_text(encoding='utf-8'))
    (args.output/'before.svg').write_bytes(subprocess.check_output(['git','show',args.before+':'+base+'.svg'],cwd=ROOT))
    (args.output/'after.svg').write_bytes(args.svg.read_bytes())
    core=lambda data:[{k:n.get(k) for k in ('id','label','founded','group','icon','size','detail_size','icon_width')} for n in data['nodes']]
    edges=lambda data:[{k:e[k] for k in ('id','source','target','kind')} for e in data['edges']]
    notes=lambda data:{n['id']:n.get('research_note',n.get('detail','')) for n in data['nodes']}
    checks=dict(identities_dates_categories_illustrations_type=core(old)==core(new),typed_edges=edges(old)==edges(new),
        complete_research_notes=notes(old)==notes(new),groups=old['groups']==new['groups'])
    assert all(checks.values()),checks
    ref=ROOT/'projects/usefulcharts-style/artifacts/images/reference-denominations.png'
    page=args.output/'comparison.html'
    page.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Institutional composition comparison</title><style>
body{font:17px/1.5 Arial;background:#eee9dc;color:#252923;margin:24px}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}h2{font-size:18px}img{width:100%;height:auto;display:block}p{max-width:1250px}figure{margin:0}</style>
<h1>Institutional history: reference, baseline and chapter candidate</h1><p>Private, unblinded author critique. Images retain their natural aspect ratios at equal width. The candidate is an editorial edition of fictional source material: it prints 33 of 133 nonempty research notes and retains all complete notes in the editable source. It is not a demonstration that the same printed content fits a smaller page. The reference artwork is not redistributed.</p><main>'''+''.join(
        '<figure><h2>'+label+'</h2><img src="'+path.resolve().as_uri()+'"></figure>' for label,path in
        [('UsefulCharts official reference',ref),('Previously published · '+args.before,args.output/'before.svg'),('Chapter candidate',args.output/'after.svg')])+'</main></html>',encoding='utf-8')
    with sync_playwright() as pw:
        browser=pw.chromium.launch();tab=browser.new_page(viewport={'width':1800,'height':1100});tab.goto(page.resolve().as_uri())
        tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)');tab.screenshot(path=str(args.output/'comparison.png'),full_page=True)
        tab.goto((args.output/'after.svg').resolve().as_uri());tab.evaluate('document.fonts.ready')
        tab.locator('svg').first.screenshot(path=str(args.output/'after.png'))
        tab.set_viewport_size({'width':1620,'height':1000});tab.screenshot(path=str(args.output/'opening.png'))
        tab.evaluate('window.scrollTo(0,Math.max(0,document.documentElement.scrollHeight-1100))');tab.screenshot(path=str(args.output/'closing.png'))
        browser.close()
    metadata=lambda path:json.loads(ET.parse(path).getroot().find('s:metadata[@id="chart-data"]',NS).text)
    a,b=metadata(args.output/'before.svg'),metadata(args.output/'after.svg')
    result=dict(status='pass',checks=checks,before=args.before,node_count=len(new['nodes']),edge_count=len(new['edges']),
        printed_notes_before=sum(bool(n.get('detail')) for n in old['nodes']),printed_notes_after=sum(bool(n.get('detail')) for n in new['nodes']),
        before_canvas=a['canvas'],after_canvas=b['canvas'],before_crossings=len(a['crossings']),after_crossings=len(b['crossings']),
        after_svg_sha256=hashlib.sha256(args.svg.read_bytes()).hexdigest(),after_png_sha256=hashlib.sha256((args.output/'after.png').read_bytes()).hexdigest(),
        limit='Source preservation and route counts are diagnostics. Visual parity is not established; the printed content is an explicit editorial selection.')
    (args.output/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))


if __name__=='__main__':main()

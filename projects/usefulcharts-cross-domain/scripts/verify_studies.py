#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "pymupdf>=1.25"]
# ///
"""Validate final files independently of the panel and calendar layout helpers."""
from pathlib import Path
import hashlib
import json
import math
import re
import pymupdf
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def check():
    summary=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for case in ['bsd','instruments','mars']:
            folder=ROOT/'artifacts/revision-2'/case
            source=json.loads((folder/'source.json').read_text(encoding='utf-8'))
            original=json.loads((ROOT/'data'/f'{case}.json').read_text(encoding='utf-8'))
            assert source['nodes']==original['nodes'] and source['edges']==original['edges'],case+' changed factual inventory'
            report=json.loads((folder/'browser.json').read_text(encoding='utf-8'))
            assert report['status']=='pass',case+' browser audit failed'
            page=browser.new_page(viewport=dict(width=1500,height=1000))
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto((folder/'poster.html').resolve().as_uri());page.evaluate('document.fonts.ready')
            page.locator('#full').click()
            width=page.locator('#paper').bounding_box()['width']
            assert abs(width-report['canvas'][0])<1,case+' full-detail zoom'
            page.locator('#plus').click()
            assert abs(page.locator('#paper').bounding_box()['width']-width*1.25)<1
            page.locator('#fit').click()
            followed=0
            links=page.locator('[data-portal-id][data-line="0"]')
            for index in range(min(6,links.count())):
                link=links.nth(index);expected=link.get_attribute('href');link.click()
                assert page.evaluate('location.hash')==expected
                assert page.locator('[id="'+expected[1:]+'"]').count()==1
                followed+=1
            dates=spans=0
            if case=='mars':
                plotted=page.evaluate('''() => ({marks:[...document.querySelectorAll('[data-date-owner]')].map(e=>{const b=e.getBBox();return {owner:e.dataset.dateOwner,type:e.dataset.dateType,year:+e.dataset.year,x:b.x+b.width/2}}),spans:[...document.querySelectorAll('[data-span-owner]')].map(e=>({owner:e.dataset.spanOwner,start:+e.dataset.start,end:+e.dataset.end,a:e.getPointAtLength(0).x,b:e.getPointAtLength(e.getTotalLength()).x}))})''')
                by={n['id']:n for n in original['nodes']}
                expected=[]
                for n in by.values():
                    for field,kind in [('launch','launch'),('arrival','encounter'),('outcome','outcome')]:
                        if n[field] is not None:expected.append((n['id'],kind,n[field]))
                actual=[(m['owner'],m['type'],m['year']) for m in plotted['marks']]
                assert sorted(expected)==sorted(actual),'Date inventory changed'
                # Derive scale from the delivered specification; read real path
                # geometry rather than trusting the renderer's x data attribute.
                sx=source['scale'];calendar=lambda year:sx['left']+(year-sx['start'])*sx['pixels_per_year']
                assert all(abs(m['x']-calendar(m['year']))<.02 for m in plotted['marks'])
                wanted=sorted((n['id'],s['start'],s['end']) for n in by.values() for s in n['spans'])
                assert wanted==sorted((s['owner'],s['start'],s['end']) for s in plotted['spans'])
                assert all(abs(s['a']-calendar(s['start']))<.02 and abs(s['b']-calendar(s['end']))<.02 for s in plotted['spans'])
                dates=len(actual);spans=len(wanted)
                lay=json.loads((folder/'layout.json').read_text())['layout'];pocket=lay['context_pocket']
                for b in lay['boxes']:
                    assert pocket['x']+pocket['w']<=b['x'] or pocket['x']>=b['x']+b['w'] or pocket['y']+pocket['h']<=b['y'] or pocket['y']>=b['y']+b['h'],'Context occupies a mission footprint'
            assert not errors,errors
            page.close()
            with pymupdf.open(folder/'poster.pdf') as pdf:
                assert len(pdf)==1
                actual_rect=pdf[0].rect
                assert abs(actual_rect.width-report['canvas'][0]*.75)<1 and abs(actual_rect.height-report['canvas'][1]*.75)<1
                norm=lambda text:''.join(text.split())
                content=norm(pdf[0].get_text())
                missing=[n['label'] for n in original['nodes'] if norm(n['label']) not in content]
                assert not missing,dict(case=case,missing=missing)
                fonts=pdf[0].get_fonts();pdf_text=True
            summary.append(dict(case=case,status='pass',records=len(source['nodes']),relations=len(source['edges']),
                min_contrast=report['min_contrast'],text_count=len(report['texts']),canvas=report['canvas'],
                actual_calendar_marks=dates,component_intervals=spans,portal_clicks=followed,
                pdf_pages=1,pdf_record_labels_preserved=pdf_text,fonts=len(fonts),
                svg_sha256=hashlib.sha256((folder/'poster.svg').read_bytes()).hexdigest()))
        browser.close()
    target=ROOT/'artifacts/reviews/independent-checks.json';target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':check()

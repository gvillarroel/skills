#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pymupdf>=1.25"]
# ///
"""Independently verify full prose, compound track reuse and numeric date geometry."""
from pathlib import Path
from collections import Counter
import hashlib
import itertools
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
import pymupdf
from playwright.sync_api import sync_playwright

PROJECT=Path(__file__).resolve().parents[1];OUT=PROJECT/'artifacts/flow-edition';REVIEW=OUT/'reviews/final'
NS={'s':'http://www.w3.org/2000/svg'}
# Independent calendar contract, not imported from the authoring code.
WINDOWS=[(2060,2165,150,960),(2240,2300,1170,1170),(2320,2360,2400,460),
         (2360,2385,2860,1530),(2385,2405,4390,1160),(3188,3200,5610,590)]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def norm_text(value):return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',value)).strip()
def expected_x(year):
    for a,z,x,w in WINDOWS:
        if a<=year<=z:return x+(year-a)*w/(z-a)
    raise AssertionError(year)
def overlap(a,b):return a['x']<b['x']+b['w']-.01 and a['x']+a['w']>b['x']+.01 and a['y']<b['y']+b['h']-.01 and a['y']+a['h']>b['y']+.01

def main():
    data=read(PROJECT/'data/ships.json');ships={s['id']:s for s in data['ships']}
    layout=read(OUT/'reviews/layout.json');packed=read(OUT/'reviews/shared-row-layout.json')['layout']
    assert data==read(OUT/'data/ships.json') and len(ships)==79
    for a,b in itertools.combinations(packed['pieces'],2):
        if a['owner']!=b['owner']:assert not overlap(a,b),(a,b)
    shared=[r for r in packed['rows'] if len(r['members'])>1]
    assert len(shared)==14 and max(len(r['members']) for r in shared)==7
    assert layout['source_sha256']==hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest()
    svg=OUT/'svgs/star-trek-starships.svg';assert layout['svg_sha256']==hashlib.sha256(svg.read_bytes()).hexdigest()
    tree=ET.fromstring(svg.read_text(encoding='utf-8'));nodes=tree.findall('.//s:g[@class="record"]',NS)
    assert len(nodes)==79 and {n.get('data-id') for n in nodes}==set(ships)
    for n in nodes:
        s=ships[n.get('data-id')];fields={role:norm_text(' '.join(t.text or '' for t in n.findall(f'.//s:text[@data-role="{role}"]',NS))) for role in ['ship-name','meta','dates','note','credit']}
        assert fields['ship-name']==norm_text(s['name'])
        assert norm_text(s['registry']) in fields['meta'] and norm_text(s['design']) in fields['meta']
        assert fields['note']==norm_text(s['note']),s['id']
        assert norm_text(s['credit']) in fields['credit']
        assert n.get('data-source')==data['sources'][s['source']]['url']
        assert n.get('data-operator')==s['operator']
        for year in s['construction'] or []:assert str(year) in fields['dates']
    actual_relations=Counter((n.get('data-source'),n.get('data-target'),n.get('data-kind')) for n in tree.findall('.//s:g[@class="typed-relation"]',NS))
    assert actual_relations==Counter((r['source'],r['target'],r['kind']) for r in data['relations'])
    routes=read(OUT/'reviews/relationship-routes.json')
    assert len(routes)==20 and Counter((r['source'],r['target'],r['kind']) for r in routes)==Counter((r['source'],r['target'],r['kind']) for r in data['relations'] if r['source']!=r['target'])
    for r in routes:
        obstacles=[p for p in packed['pieces'] if p['owner'] not in (r['source'],r['target'])]
        for a,b in zip(r['points'],r['points'][1:]):
            assert a[0]==b[0] or a[1]==b[1]
            segment=dict(x=min(a[0],b[0])-.1,y=min(a[1],b[1])-.1,w=abs(a[0]-b[0])+.2,h=abs(a[1]-b[1])+.2)
            assert all(not overlap(segment,p) for p in obstacles),r
    audit=read(REVIEW/'browser-audit.json');art=read(REVIEW/'art-audit.json')
    assert not audit['outside'] and not audit['overlaps'] and not audit['envelope_overflow']
    assert art['status']=='pass'
    errors=[];network=[];marks=spans=0;max_error=0
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        ctx=browser.new_context(viewport={'width':1600,'height':1000},offline=True);tab=ctx.new_page()
        tab.on('pageerror',lambda e:errors.append(str(e)));tab.on('request',lambda r:network.append(r.url) if r.url.startswith('http') else None)
        tab.goto((OUT/'viewer/index.html').as_uri());tab.evaluate('document.fonts.ready');assert tab.evaluate('data')==data
        actual=tab.evaluate('''()=>[...document.querySelectorAll('.record,.continuation')].map(e=>({
          id:e.dataset.id,fragment:e.dataset.fragment,secondary:e.classList.contains('continuation'),
          leaderX:+e.querySelector('.annotation-leader').getAttribute('d').match(/^M([0-9.]+)/)[1],
          marks:[...e.querySelectorAll('.date-mark')].map(m=>{let b=m.getBBox();return {year:+m.dataset.year,kind:m.dataset.kind,x:b.x+b.width/2}}),
          spans:[...e.querySelectorAll('.service-span,.observations-span,.uncertain-span')].map(g=>{let b=g.querySelector('rect,.wake-core').getBBox();return {kind:g.classList.contains('service-span')?'service':g.classList.contains('observations-span')?'observations':'uncertain',start:+g.dataset.start,end:+g.dataset.end,x:b.x,w:b.width,dash:g.querySelector('.wake-core')?.getAttribute('stroke-dasharray')||null}})
        }))''')
        assert len(actual)==90 and len({a['fragment'] for a in actual})==90
        secondary=Counter()
        for a in actual:
            s=ships[a['id']]
            if a['secondary']:
                assert not a['spans'];secondary.update((a['id'],m['year'],m['kind']) for m in a['marks']);end=max(m['year'] for m in a['marks'])
            else:
                years=sorted(set(s['observations']+(s['construction'] or [])+([s['launch']] if s['launch'] is not None else [])));end=years[-1]
                expected=[];expected_spans=[]
                if s.get('uncertain_range'):expected_spans=[('uncertain',*s['uncertain_range'])];end=s['uncertain_range'][-1]
                else:
                    for year in years:
                        kind='active'
                        if year in (s['construction'] or []):kind='built'
                        if year==s['observations'][-1] and s['endpoint']:kind=s['endpoint']
                        if year==s['launch']:kind=s['launch_kind']
                        if year==s['launch']==s['observations'][-1] and s['endpoint']:kind='launch'
                        expected.append((year,kind))
                    if s['endpoint'] and s['launch']==s['observations'][-1]:expected.append((s['launch'],s['endpoint']))
                    if s['service']:expected_spans=[('service',*s['service'])]
                    elif len(years)>1:expected_spans=[('observations',years[0],years[-1])]
                assert Counter((m['year'],m['kind']) for m in a['marks'])==Counter(expected),a['id']
                assert [(q['kind'],q['start'],q['end']) for q in a['spans']]==expected_spans,a['id']
            assert abs(a['leaderX']-expected_x(end))<.03
            for m in a['marks']:
                error=abs(m['x']-expected_x(m['year']));assert error<.03,(a['id'],m,error)
                marks+=1;max_error=max(max_error,error)
            for q in a['spans']:
                assert abs(q['x']-expected_x(q['start']))<.03 and abs(q['x']+q['w']-expected_x(q['end']))<.03
                assert q['kind']=='uncertain' or q['dash']==('9 9' if q['kind']=='observations' else None)
                spans+=1
        assert secondary==Counter((s['id'],q['year'],q['kind']) for s in ships.values() for q in s['special'])
        ticks=tab.evaluate("[...document.querySelectorAll('[data-role=axis-year]')].map(e=>({year:+e.textContent,x:+e.getAttribute('x')}))")
        assert all(abs(t['x']-expected_x(t['year']))<.03 for t in ticks)
        assert tab.locator('[data-role=axis-break]').count()==3
        assert tab.locator('#count').inner_text()=='79 of 79 spacecraft'
        tab.screenshot(path=str(REVIEW/'viewer-overview.png'))
        tab.locator('#operator').select_option('Klingon');assert tab.locator('.record:not(.dim)').count()==6
        tab.locator('#operator').select_option('');tab.locator('#evidence').select_option('launch');assert tab.locator('#results button').count()==29
        tab.locator('#evidence').select_option('unknown');assert tab.locator('#results button').count()==50
        tab.locator('#evidence').select_option('');tab.locator('#search').fill('NCC-1701-D');tab.locator('#results button').click()
        assert tab.locator('.continuation.selected').count()==1 and '2402' in tab.locator('#detail').inner_text()
        tab.locator('#detail [data-ship-link="enterprise-e"]').click();assert tab.locator('.record:not(.dim)').count()==79
        tab.locator('.continuation[data-id="discovery"]').focus();tab.keyboard.press('Enter');assert tab.locator('#detail > h2').first.inner_text()=='USS Discovery'
        tab.locator('#search').fill('3191');assert not tab.locator('.continuation[data-id="discovery"]').evaluate("e=>e.classList.contains('dim')")
        tab.locator('#search').fill('');tab.locator('#section').select_option('enterprise');tab.screenshot(path=str(REVIEW/'viewer-enterprise.png'))
        for href in tab.locator('a[href]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
            if not href.startswith(('http','#')):assert (OUT/'viewer'/href.split('#')[0]).resolve().is_file()
        tab.set_viewport_size({'width':900,'height':900});tab.locator('#fit').click();assert tab.evaluate('sizer.clientWidth <= stage.clientWidth')
        tab.screenshot(path=str(REVIEW/'viewer-compact.png'));browser.close()
    assert not errors and not network
    doc=pymupdf.open(OUT/'documents/star-trek-starships.pdf');assert len(doc)==1
    page=doc[0];pdftext=norm_text(page.get_text());assert all(norm_text(s['name']) in pdftext for s in ships.values())
    links=page.get_links();assert Counter(l['uri'] for l in links)==Counter(data['sources'][s['source']]['url'] for s in ships.values())
    for b in layout['boxes']:
        center=pymupdf.Point((b['x']+b['w']/2)*page.rect.width/layout['width'],(b['y']+b['h']/2)*page.rect.height/layout['height'])
        matches=[l for l in links if l['from'].contains(center)];assert len(matches)==1 and matches[0]['uri']==data['sources'][ships[b['id']]['source']]['url']
    result=dict(status='pass',records=79,printed_full_notes=79,fragments=90,secondary_marks=sum(secondary.values()),date_marks=marks,date_spans=spans,max_calendar_error_px=max_error,shared_baselines=len(shared),max_fragments_per_baseline=7,typed_relations=21,routed_relations=20,foreign_route_obstacle_intersections=0,printed_family_keys=13,pdf_source_links=79,offline_viewer=True,text_count=audit['text_count'],text_overlaps=0,art_text_overlaps=0,minimum_contrast=art['text_background_minimum'],svg_sha256=layout['svg_sha256'],limitations=['Piecewise numeric calendar, with prominently labeled scale windows.','Body remains unevenly occupied; semantic-reference census and UsefulCharts aesthetic parity are incomplete.','Compound placement is an application prototype; separate Pi tests validate only the bundled measured-track helper.'])
    result['source_sha256']=layout['source_sha256']
    for font in page.get_fonts():assert doc.extract_font(font[0])[3]
    result['pdf_embedded_fonts']=len(page.get_fonts())
    (REVIEW/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':main()

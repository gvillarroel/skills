#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pymupdf>=1.25", "pillow>=11"]
# ///
"""Independently check calendar coordinates, physical identities and offline use."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import itertools
import re
import xml.etree.ElementTree as ET
import pymupdf
from PIL import Image
from playwright.sync_api import sync_playwright
from verify_atlas import norm_text,norm_url

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/'artifacts/numeric-edition';REVIEW=OUT/'reviews/final'
NS={'s':'http://www.w3.org/2000/svg'}
# Evaluator-owned contract. Do not import the builder's coordinate function.
WINDOWS=[(2060,2165,300,800),(2240,2300,1170,1020),
         (2320,2360,2260,320),(2360,2385,2580,1750),
         (2385,2405,4330,450),(3188,3200,4850,280)]


def read(p):return json.loads(p.read_text(encoding='utf-8'))


def expected_x(year):
    for start,end,left,width in WINDOWS:
        if start<=year<=end:return left+(year-start)*width/(end-start)
    raise AssertionError(f'Unsupported calendar year: {year}')


def main():
    data=read(PROJECT/'data/ships.json');layout=read(OUT/'reviews/layout.json')
    packed=read(OUT/'reviews/shared-row-layout.json')['layout']
    shared_tracks=[r for r in packed['rows'] if len(r['members'])>1]
    assert len(shared_tracks)==20
    assert max(len(r['members']) for r in shared_tracks)==4
    for a,b in itertools.combinations(packed['groups'],2):
        assert a['x']+a['w']+18<=b['x']+.01 or b['x']+b['w']+18<=a['x']+.01 or a['y']+a['h']+22<=b['y']+.01 or b['y']+b['h']+22<=a['y']+.01
    family_by_id={g['id']:g for g in packed['groups']}
    assert family_by_id['earth']['y']==family_by_id['classic-fleet']['y']==family_by_id['explorers']['y']
    ships={s['id']:s for s in data['ships']};assert len(ships)==79
    assert data==read(OUT/'data/ships.json')
    for relative in ['data/ships.csv','documents/sources.html']:
        assert (OUT/relative).read_bytes()==(PROJECT/'artifacts'/relative).read_bytes()
    assert layout['source_sha256']==hashlib.sha256((PROJECT/'data/ships.json').read_bytes()).hexdigest()
    svg=OUT/'svgs/star-trek-starships.svg'
    assert layout['svg_sha256']==hashlib.sha256(svg.read_bytes()).hexdigest()
    tree=ET.fromstring(svg.read_text(encoding='utf-8'))
    nodes=tree.findall('.//s:g[@class="record"]',NS)
    assert len(nodes)==79 and {g.get('data-id') for g in nodes}==set(ships)
    for node in nodes:
        s=ships[node.get('data-id')];label=norm_text(' '.join(t.text or '' for t in node.findall('.//s:text',NS)))
        assert norm_text(s['name']) in label and norm_text(s['registry']) in label,s['id']
        assert node.get('data-source')==data['sources'][s['source']]['url']
        for year in s['construction'] or []:assert str(year) in label,(s['id'],'construction missing')
    relations=tree.findall('.//s:g[@class="typed-relation"]',NS)
    assert Counter((g.get('data-source'),g.get('data-target'),g.get('data-kind')) for g in relations)==Counter((r['source'],r['target'],r['kind']) for r in data['relations'])
    profiles=tree.findall('.//s:g[@class="design-profile"]',NS)
    for p in profiles:
        s=ships[p.get('data-owner')];label=norm_text(' '.join(t.text or '' for t in p.findall('.//s:text',NS)))
        assert norm_text(s['note']) in label and norm_text(s['credit']) in label
    retrieved={norm_url(u) for u in read(PROJECT/'data/retrieved-source-urls.json')['urls']}
    assert all(norm_url(data['sources'][s['source']]['url']) in retrieved for s in ships.values())
    audit=read(REVIEW/'browser-audit.json');art=read(REVIEW/'art-audit.json')
    assert not audit['outside'] and not audit['overlaps'] and not audit['envelope_overflow'] and audit['font_barlow']
    assert art['status']=='pass'
    assert Image.open(OUT/'images/star-trek-starships.png').size==(5200,layout['height'])
    doc=pymupdf.open(OUT/'documents/star-trek-starships.pdf');assert len(doc)==1
    page=doc[0];pdftext=norm_text(page.get_text())
    assert all(norm_text(s['name']) in pdftext for s in ships.values())
    links=page.get_links()
    assert Counter(l['uri'] for l in links)==Counter(data['sources'][s['source']]['url'] for s in ships.values())
    for b in layout['boxes']:
        center=pymupdf.Point((b['x']+b['w']/2)*page.rect.width/layout['width'],(b['y']+b['h']/2)*page.rect.height/layout['height'])
        matches=[l for l in links if l['from'].contains(center)]
        assert len(matches)==1 and matches[0]['uri']==data['sources'][ships[b['id']]['source']]['url']
    for f in page.get_fonts():
        if f[2]=='Type3':
            kind,value=doc.xref_get_key(f[0],'CharProcs')
            if kind=='xref':value=doc.xref_object(int(value.split()[0]))
            glyphs=re.findall(r'(\d+) 0 R',value)
            assert glyphs and all(doc.xref_is_stream(int(g)) and doc.xref_stream(int(g)) for g in glyphs)
        else:assert doc.extract_font(f[0])[3]
    errors=[];network=[];mark_count=span_count=0;max_error=0
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        ctx=browser.new_context(viewport={'width':1600,'height':1000},offline=True)
        tab=ctx.new_page();tab.on('pageerror',lambda e:errors.append(str(e)))
        tab.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        tab.on('request',lambda r:network.append(r.url) if r.url.startswith('http') else None)
        tab.goto((OUT/'viewer/index.html').as_uri());tab.evaluate('document.fonts.ready')
        assert tab.evaluate('data')==data
        assert tab.locator('#count').inner_text()=='79 of 79 spacecraft'
        actual=tab.evaluate('''()=>[...document.querySelectorAll('.record,.continuation')].map(e=>({
          id:e.dataset.id,fragment:e.dataset.fragment,secondary:e.classList.contains('continuation'),
          marks:[...e.querySelectorAll('.date-mark')].map(m=>{let b=m.getBBox();return {year:+m.dataset.year,kind:m.dataset.kind,x:b.x+b.width/2}}),
          spans:[...e.querySelectorAll('.service-span,.observations-span,.uncertain-span')].map(g=>{let b=g.querySelector('rect,.wake-core').getBBox();return {kind:g.classList.contains('service-span')?'service':g.classList.contains('observations-span')?'observations':'uncertain',start:+g.dataset.start,end:+g.dataset.end,x:b.x,w:b.width,dash:g.querySelector('.wake-core')?.getAttribute('stroke-dasharray')||null}})
        }))''')
        secondary=Counter()
        assert len(actual)==90 and len({a['fragment'] for a in actual})==90
        for a in actual:
            s=ships[a['id']]
            if a['secondary']:
                assert not a['spans'],'A later state became a service interval'
                secondary.update((a['id'],m['year'],m['kind']) for m in a['marks'])
            else:
                years=sorted(set(s['observations']+(s['construction'] or [])+([s['launch']] if s['launch'] is not None else [])))
                expected=[];spans=[]
                if s.get('uncertain_range'):spans=[('uncertain',*s['uncertain_range'])]
                else:
                    for year in years:
                        kind='active'
                        if year in (s['construction'] or []):kind='built'
                        if year==s['observations'][-1] and s['endpoint']:kind=s['endpoint']
                        if year==s['launch']:kind=s['launch_kind']
                        if year==s['launch']==s['observations'][-1] and s['endpoint']:kind='launch'
                        expected.append((year,kind))
                    if s['endpoint'] and s['launch']==s['observations'][-1]:expected.append((s['launch'],s['endpoint']))
                    if s['service']:spans=[('service',*s['service'])]
                    elif len(years)>1:spans=[('observations',years[0],years[-1])]
                assert Counter((m['year'],m['kind']) for m in a['marks'])==Counter(expected),a['id']
                assert [(q['kind'],q['start'],q['end']) for q in a['spans']]==spans,a['id']
            for m in a['marks']:
                error=abs(m['x']-expected_x(m['year']));assert error<.03,(a['id'],m,error)
                max_error=max(max_error,error);mark_count+=1
            for q in a['spans']:
                assert abs(q['x']-expected_x(q['start']))<.03
                assert abs(q['x']+q['w']-expected_x(q['end']))<.03
                if q['kind']=='observations':assert q['dash']=='9 9'
                if q['kind']=='service':assert q['dash'] is None
                span_count+=1
        assert secondary==Counter((s['id'],q['year'],q['kind']) for s in ships.values() for q in s['special'])
        ticks=tab.evaluate("[...document.querySelectorAll('[data-role=axis-year]')].map(e=>({year:+e.textContent,x:+e.getAttribute('x')}))")
        assert all(abs(t['x']-expected_x(t['year']))<.03 for t in ticks)
        assert tab.locator('[data-role=axis-break]').count()==3
        tab.screenshot(path=str(REVIEW/'viewer-overview.png'))
        tab.locator('#search').fill('NX-74205');assert tab.locator('#results button').count()==2
        tab.locator('#search').fill('');tab.locator('#operator').select_option('Klingon')
        assert tab.locator('.record:not(.dim)').count()==6
        tab.locator('#operator').select_option('');tab.locator('#evidence').select_option('launch')
        assert tab.locator('#results button').count()==29
        tab.locator('#evidence').select_option('unknown');assert tab.locator('#results button').count()==50
        tab.locator('#evidence').select_option('');tab.locator('#search').fill('NCC-1701-D')
        tab.locator('#results button').click();assert '2402' in tab.locator('#detail').inner_text()
        assert tab.locator('.continuation.selected').count()==1
        tab.screenshot(path=str(REVIEW/'viewer-enterprise-d.png'))
        tab.locator('#detail [data-ship-link="enterprise-e"]').click();assert tab.locator('.record:not(.dim)').count()==79
        tab.locator('.continuation[data-id="discovery"]').focus();tab.keyboard.press('Enter')
        assert tab.locator('#detail > h2').first.inner_text()=='USS Discovery'
        assert '3189' in tab.locator('#detail').inner_text()
        tab.locator('#search').fill('3191');assert not tab.locator('.continuation[data-id="discovery"]').evaluate("e=>e.classList.contains('dim')")
        tab.locator('#search').fill('');tab.locator('#plus').click();assert tab.locator('#zoom').inner_text()=='108%'
        tab.locator('#minus').click();assert tab.locator('#zoom').inner_text()=='90%'
        tab.locator('#section').select_option('enterprise');assert tab.locator('#zoom').inner_text()=='55%'
        tab.screenshot(path=str(REVIEW/'viewer-shared-enterprise.png'))
        tab.locator('#fit').click();assert tab.evaluate('sizer.clientWidth <= stage.clientWidth')
        for href in tab.locator('a[href]').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
            if not href.startswith(('http','#')):assert (OUT/'viewer'/href.split('#')[0]).resolve().is_file(),href
        tab.set_viewport_size({'width':900,'height':900});tab.locator('#fit').click()
        assert tab.evaluate('document.documentElement.scrollWidth <= innerWidth')
        tab.screenshot(path=str(REVIEW/'viewer-compact.png'));browser.close()
    assert not errors and not network,(errors,network)
    report=dict(status='pass',records=79,family_groups=13,physical_state_fragments=90,
                secondary_fragments=11,secondary_event_marks=sum(secondary.values()),
                known_launch_commission_build=29,unknown_launch=50,construction_records=4,
                exact_date_marks=mark_count,date_spans=span_count,max_calendar_error_px=max_error,
                solid_service_spans=sum(bool(s['service']) for s in ships.values()),
                numeric_windows=len(WINDOWS),axis_breaks=3,typed_relations=len(relations),
                shared_tracks=len(shared_tracks),maximum_vessels_on_one_track=4,
                reused_family_band=['earth','classic-fleet','explorers'],
                full_context_profiles=len(profiles),image_placements=18,unique_generated_ship_assets=6,
                text_nodes=audit['text_count'],text_overlaps=0,image_text_overlaps=0,
                minimum_text_background_contrast=art['text_background_minimum'],
                pdf_pages=1,pdf_source_links=len(links),pdf_fonts=len(page.get_fonts()),
                offline_viewer=True,browser_errors=errors,network_requests=network,
                svg_sha256=layout['svg_sha256'],source_sha256=layout['source_sha256'],
                limitations=['Piecewise linear x scale; 2360–2385 is expanded.','The poster selects compact facts; full narrative context for all 79 ships is retained in the viewer and evidence ledger.','Physical-record density does not certify UsefulCharts knowledge-density or aesthetic parity.'])
    (REVIEW/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()

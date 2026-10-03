#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2", "pypdf>=5,<7"]
# ///
"""Check all revision-three facts and exact calendar positions, then export PDFs."""
import hashlib
import io
import json
import re
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pypdf import PdfReader,PdfWriter
from pypdf.generic import RectangleObject
from artwork import ROOT,REPO,tag,render
from playwright.sync_api import sync_playwright

SOURCES={c:REPO/'projects/usefulcharts-cross-domain/data'/f'{c}.json' for c in ['instruments','bsd']}
SOURCES.update(mars=REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/mars/source.json',starships=REPO/'projects/star-trek-starships/data/ships.json',civilizations=REPO/'projects/star-trek-canonical-timeline/data/timeline.json')
def normalize(text):return ' '.join(unicodedata.normalize('NFKC',str(text)).split())
def nodes(source):return source.get('nodes') or source.get('ships') or [n for k in ['events','origins','future','branches'] for n in source[k]]
def intersects(a,b):return a['x']<b['x']+b['w']-.8 and a['x']+a['w']>b['x']+.8 and a['y']<b['y']+b['h']-.8 and a['y']+a['h']>b['y']+.8
def main():
    output=ROOT/'artifacts/revision-3';results=[]
    for case in sys.argv[1:] or SOURCES:
        out=output/case;source=json.loads((out/'source.json').read_text(encoding='utf-8'));expected=json.loads(SOURCES[case].read_text(encoding='utf-8'));root=ET.parse(out/'poster.svg').getroot();layout=json.loads((out/'layout.json').read_text());issues=[]
        if source!=expected:issues.append('Source inventory differs')
        groups={e.get('data-record-id') or e.get('data-id'):e for e in root.iter(tag('g')) if e.get('data-record-id') or (e.get('class')=='record' and e.get('data-id'))}
        for n in nodes(source):
            e=groups.get(n['id'])
            if e is None:issues.append('Missing record '+n['id']);continue
            printed=normalize(' '.join(''.join(t.itertext()) for t in e.iter(tag('text'))))
            fields=['name','note','credit','design','registry'] if case=='starships' else ['label','detail','credit','date' if case=='civilizations' else 'date_label']
            for field in fields:
                if n.get(field) and normalize(n[field]) not in printed:issues.append(dict(type='missing-printed-field',record=n['id'],field=field))
        if case in ['bsd','instruments']:
            observed={(e.get('data-source'),e.get('data-target'),e.get('data-kind')) for e in root.iter() if e.get('data-source') and e.get('data-target')}
            required={(e['source'],e['target'],e['kind']) for e in source['edges']}
            if observed!=required:issues.append('Typed edge inventory differs')
        # Independent calendar values are derived from raw source plus the
        # declared scale. SVG marker geometry is read in the browser below.
        expected_dates=[]
        if case=='mars':
            for n in nodes(source):
                for key,kind in [('launch','launch'),('arrival','arrival'),('outcome','loss')]:
                    if n.get(key) is not None:expected_dates.append((n['id'],kind,n[key],105+(n[key]-1960)*85))
        elif case=='civilizations':
            for n in source['events']:
                s=next(s for s in layout['segments'] if s['start']<=n['year']<=s['end']);x=s['x']+(n['year']-s['start'])/(s['end']-s['start'])*s['width'];expected_dates.append((n['id'],'anchor',n['year'],x))
        elif case=='starships':
            original=ET.parse(ROOT/'artifacts/revision-2/starships/poster.svg').getroot()
            def signatures(tree):
                result=[]
                for record in tree.iter(tag('g')):
                    if record.get('data-fragment'):
                        for mark in record.iter():
                            if mark.get('class')=='date-mark':
                                # All baseline symbols are centered in X; retain
                                # each child X geometry while allowing Y to move.
                                result.append((record.get('data-fragment'),mark.get('data-year'),mark.get('data-kind')))
                return sorted(result)
            if signatures(root)!=signatures(original):issues.append('Ship date identity differs')
            for m in layout['marks']:expected_dates.append((m['owner'],m['kind'],m['year'],m['x']))
        render(out,layout['detail'])
        with sync_playwright() as pw:
            b=pw.chromium.launch();page=b.new_page();page.set_content('<style>body{margin:0}</style>'+(out/'poster.svg').read_text(encoding='utf-8'));page.evaluate('document.fonts.ready')
            browser=page.evaluate('''() => ({texts:[...document.querySelectorAll('text')].map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,y:b.y,w:b.width,h:b.height,owner:e.closest('[data-record-id],.record,.continuation')?.dataset.recordId||e.closest('.record,.continuation')?.dataset.id||null}}),marks:[...document.querySelectorAll('[data-date-owner],g.date-mark')].map(e=>{const b=e.getBBox();return {owner:e.dataset.dateOwner||e.closest('[data-id]')?.dataset.id,kind:e.dataset.kind||'anchor',year:+e.dataset.year,x:b.x+b.width/2}})})''');b.close()
        (out/'browser-measurements.json').write_text(json.dumps(browser,indent=2)+'\n')
        actual_dates=sorted((m['owner'],m['kind'],m['year'],m['x']) for m in browser['marks'])
        differences=[dict(expected=e,actual=a) for e,a in zip(sorted(expected_dates),actual_dates) if e[:3]!=a[:3] or abs(e[3]-a[3])>.05]
        if differences or len(expected_dates)!=len(actual_dates):issues.append(dict(type='date-x-mismatch',expected=len(expected_dates),actual=len(actual_dates),differences=differences[:12]))
        spans=[]
        if case=='mars':
            for n in nodes(source):
                for i,s in enumerate(n['spans']):
                    e=root.find(".//*[@id='span-"+n['id']+'-'+str(i)+"']");numbers=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',e.get('d')))) if e is not None else []
                    if not numbers or abs(numbers[0]-(105+(s['start']-1960)*85))>.05 or abs(numbers[2]-(105+(s['end']-1960)*85))>.05:issues.append('Operation span differs '+n['id'])
                    spans.append(s)
        info=json.loads((out/'render.json').read_text());issues.extend(info['image_text_overlaps']);issues.extend(info['errors']);w,h=info['canvas']
        for t in browser['texts']:
            if t['x']<-.8 or t['y']<-.8 or t['x']+t['w']>w+.8 or t['y']+t['h']>h+.8:issues.append(dict(type='text-outside-canvas',text=t['text']))
        text_collisions=[]
        for i,a in enumerate(browser['texts']):
            for b in browser['texts'][i+1:]:
                if intersects(a,b):text_collisions.append([a['text'],b['text']])
        issues.extend(dict(type='text-text',texts=pair) for pair in text_collisions)
        for route in layout.get('routes',[]):
            for a,b in zip(route['points'],route['points'][1:]):
                segment=dict(x=min(a[0],b[0])-1,y=min(a[1],b[1])-1,w=abs(a[0]-b[0])+2,h=abs(a[1]-b[1])+2)
                for t in browser['texts']:
                    if intersects(segment,t):issues.append(dict(type='route-text',route=route.get('id',route.get('source')),text=t['text']))
                for a in info['images']:
                    if intersects(segment,a):issues.append(dict(type='route-image',route=route.get('id',route.get('source')),image=a['id']))
        writer=PdfWriter();writer.append(PdfReader(out/'poster.pdf'));boxes={b['id']:b for b in layout['boxes']};link_count=0
        for n in nodes(source):
            ref=source.get('sources',{}).get(n.get('source'),{});url=n.get('source_url') or ref.get('url');box=boxes.get(n['id'])
            if not url or box is None:issues.append('Missing source link '+n['id']);continue
            writer.add_uri(0,url,RectangleObject([box['x']*.75,(h-box['y']-box['h'])*.75,(box['x']+box['w'])*.75,(h-box['y'])*.75]),border=[0,0,0]);link_count+=1
        buffer=io.BytesIO();writer.write(buffer);(out/'poster.pdf').write_bytes(buffer.getvalue());pdf=PdfReader(out/'poster.pdf');pdftext=normalize(pdf.pages[0].extract_text())
        for n in nodes(source):
            for field in ['label','detail','credit'] if case!='starships' else ['name','note','credit']:
                if n.get(field) and normalize(n[field]) not in pdftext:issues.append(dict(type='pdf-text-extraction',record=n['id'],field=field))
        if len(pdf.pages)!=1:issues.append('PDF page count differs')
        subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1900','-png',str(out/'poster.pdf'),str(out/'pdf-preview')],check=True,capture_output=True)
        before=ET.parse(ROOT/'artifacts/revision-2'/case/'poster.svg').getroot();area=float(before.get('width'))*float(before.get('height'))
        result=dict(case=case,status='pass' if not issues else 'fail',records=len(nodes(source)),canvas=[w,h],area_change_percent=round((w*h/area-1)*100,2),record_density_change_percent=round((area/(w*h)-1)*100,2),dates=len(expected_dates),operation_spans=len(spans),pdf_source_links=link_count,illustrations=len(info['images']),findings=issues,reference_density_status='pending',hashes={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['poster.svg','poster.pdf','poster.png','preview.png','detail.png','source.json']})
        (out/'verification.json').write_text(json.dumps(result,indent=2)+'\n');results.append(result);print(json.dumps({k:result[k] for k in ['case','status','area_change_percent','findings']}))
    (output/'verification.json').write_text(json.dumps(results,indent=2)+'\n');return any(r['status']!='pass' for r in results)
if __name__=='__main__':raise SystemExit(main())

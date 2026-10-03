#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Independently inspect final panel-poster DOM geometry and its supplied source."""
from pathlib import Path
import argparse
import json
from playwright.sync_api import sync_playwright

INSPECT = r"""() => {
 const s=document.querySelector('svg'),v=s.viewBox.baseVal;
 const box=e=>{const b=e.getBBox();return {x:b.x,y:b.y,w:b.width,h:b.height}};
 const texts=[...s.querySelectorAll('text')].map(e=>({text:e.textContent,box:box(e),record:e.closest('[data-record-id]')?.dataset.recordId,role:e.dataset.role,size:parseFloat(getComputedStyle(e).fontSize),fill:getComputedStyle(e).fill,background:e.dataset.background}));
 const records=[...s.querySelectorAll('[data-record-id]')].map(e=>({id:e.dataset.recordId,box:box(e.querySelector('[data-record-box]')),fields:Object.fromEntries(['label','kicker','detail'].map(role=>[role,[...e.querySelectorAll(`[data-role="${role}"]`)].map(t=>t.textContent).join(' ')]))}));
 const links=[...s.querySelectorAll('[data-link-id]')].map(e=>({id:e.dataset.linkId,source:e.dataset.source,target:e.dataset.target,kind:e.dataset.kind}));
 const portals=[...s.querySelectorAll('[data-portal-id][data-line="0"]')].map(e=>({id:e.dataset.portalId,role:e.dataset.portalRole,owner:e.closest('[data-record-id]').dataset.recordId,href:e.getAttribute('href'),text:[...e.closest('[data-record-id]').querySelectorAll('[data-portal-id]')].filter(p=>p.dataset.portalId===e.dataset.portalId&&p.dataset.portalRole===e.dataset.portalRole).map(p=>p.textContent).join(' ')}));
 const images=[...s.querySelectorAll('[data-art-id]')].map(e=>{
   // A nested SVG's content bounds ignore its clipping viewport. Measure the
   // actual viewport rectangle in its parent's coordinate system instead.
   const nested=e.tagName.toLowerCase()==='svg';
   const b=nested?{x:e.x.baseVal.value,y:e.y.baseVal.value,width:e.width.baseVal.value,height:e.height.baseVal.value}:e.getBBox();
   const m=s.getScreenCTM().inverse().multiply((nested?e.parentElement:e).getScreenCTM());
   const points=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>new DOMPoint(x,y).matrixTransform(m));
   const xs=points.map(p=>p.x),ys=points.map(p=>p.y);return {id:e.dataset.artId,box:{x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)}};
 });
 return {canvas:[v.width,v.height],texts,records,links,portals,images,embedded:JSON.parse(s.querySelector('#poster-source').textContent)};
}"""

def intersects(a,b,p=0):
    return a['x']<b['x']+b['w']-p and a['x']+a['w']>b['x']+p and a['y']<b['y']+b['h']-p and a['y']+a['h']>b['y']+p

def audit(svg,source,png=None,pdf=None):
    expected=json.loads(source.read_text(encoding='utf-8-sig'))
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport=dict(width=1600,height=1000))
        page.set_content('<!doctype html><html><head><style>html,body{margin:0}svg{display:block}</style></head><body>'+svg.read_text(encoding='utf-8')+'</body></html>')
        page.evaluate('document.fonts.ready');data=page.evaluate(INSPECT)
        width,height=data['canvas'];page.set_viewport_size(dict(width=int(width),height=min(1200,int(height))))
        if png:page.locator('body > svg').screenshot(path=str(png))
        if pdf:
            page.add_style_tag(content='@page{margin:0}html,body{margin:0;padding:0}svg{display:block}')
            page.pdf(path=str(pdf),width=f'{width}px',height=f'{height}px',print_background=True)
        browser.close()
    issues=[]
    if data.pop('embedded')!=expected:issues.append(dict(type='source-changed'))
    by={n['id']:n for n in expected['nodes']};seen={n['id']:n for n in data['records']}
    if set(by)!=set(seen) or len(by)!=len(data['records']):issues.append(dict(type='record-inventory'))
    normalize=lambda value:' '.join(str(value).split())
    for i,n in by.items():
        for key,field in [('label','label'),('kicker','date_label' if 'date_label' in n else 'code'),('detail','detail')]:
            if normalize(seen.get(i,{}).get('fields',{}).get(key,''))!=normalize(n.get(field,'')):
                issues.append(dict(type='visible-field',record=i,field=field))
    links={e['id']:e for e in data['links']};portals=data['portals'];edge_ids=[e['id'] for e in expected['edges']]
    if set(links)|{e['id'] for e in portals} != set(edge_ids):issues.append(dict(type='relationship-inventory'))
    for e in expected['edges']:
        if e['id'] in links:
            if any(links[e['id']][k]!=e[k] for k in ('source','target','kind')):issues.append(dict(type='link-endpoint-or-type',id=e['id']))
        else:
            points=[a for a in portals if a['id']==e['id']]
            desired={('out',e['source'],'#record-'+e['target']),('in',e['target'],'#record-'+e['source'])}
            if len(points)!=2 or {(a['role'],a['owner'],a['href']) for a in points}!=desired:issues.append(dict(type='portal-pair',id=e['id']))
            types={'branch':'lineage','succession':'successor','influence':'contribution','uncertain':'uncertain link','contains':'contains'}
            numbers=[]
            for a in points:
                prefix,_,rest=normalize(a['text']).partition(' ');numbers.append(prefix)
                other=e['target'] if a['role']=='out' else e['source'];arrow='→' if a['role']=='out' else '←'
                wanted=f'{arrow} {by[other]["label"]} · {types[e["kind"]]}'
                if not prefix.isdigit() or normalize(rest)!=normalize(wanted):issues.append(dict(type='portal-visible-meaning',id=e['id']))
            if len(set(numbers))!=1:issues.append(dict(type='portal-number-pair',id=e['id']))
    all_text=normalize(' '.join(t['text'] for t in data['texts']))
    for field in ('position_semantics','reading_note','source_note'):
        if expected.get(field) and normalize(expected[field]) not in all_text:issues.append(dict(type='visible-note',field=field))
    from render_chart import contrast
    def hex_color(value):
        import re
        if value.startswith('#'):return value
        return '#'+''.join(f'{int(v):02x}' for v in re.findall(r'\d+',value)[:3])
    for i,t in enumerate(data['texts']):
        b=t['box'];ratio=contrast(hex_color(t['fill']),t['background']);t['contrast']=ratio
        if b['x']<0 or b['y']<0 or b['x']+b['w']>width+.5 or b['y']+b['h']>height+.5:issues.append(dict(type='text-outside',text=t['text']))
        if ratio<4.5 or t['size']<14:issues.append(dict(type='legibility',text=t['text']))
        for other in data['texts'][i+1:]:
            if intersects(b,other['box'],1):issues.append(dict(type='text-overlap',a=t['text'],b=other['text']))
    for i,a in enumerate(data['records']):
        for b in data['records'][i+1:]:
            if intersects(a['box'],b['box'],1):issues.append(dict(type='record-overlap',a=a['id'],b=b['id']))
    for art in data['images']:
        for t in data['texts']:
            if intersects(art['box'],t['box'],1):issues.append(dict(type='image-text-overlap',image=art['id'],text=t['text']))
    data.update(status='fail' if issues else 'pass',findings=issues,min_contrast=min(t['contrast'] for t in data['texts']),
                visual_review='Required. No reference-density or similarity claim follows from these checks.')
    return data

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('svg',type=Path);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--png',type=Path);p.add_argument('--pdf',type=Path)
    args=p.parse_args();report=audit(args.svg,args.source,args.png,args.pdf)
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],findings=len(report['findings']))))
    return report['status']!='pass'

if __name__=='__main__':raise SystemExit(main())

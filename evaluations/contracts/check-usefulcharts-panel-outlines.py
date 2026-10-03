#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inspect the museum forward outputs without importing the evaluated skill."""
from pathlib import Path
import argparse
import json
import re
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

def check(workspace,prompt):
    source=json.loads((workspace/'deliverables/source.json').read_text(encoding='utf-8-sig'))
    expected={}
    for line in prompt.read_text(encoding='utf-8').splitlines():
        m=re.match(r'- ([ABC][0-9]*): (.+)',line)
        if m:
            label,_,detail=m[2].partition('. Detail: ');expected[m[1]]=dict(label=label,detail=detail)
    def visible_code(n):
        if n.get('code',n.get('date_label')) is not None:return str(n.get('code',n.get('date_label')))
        prefix=re.match(r'^([ABC][0-9]*) (.+)$',n['label'])
        return prefix[1] if prefix else ''
    by={visible_code(n):n for n in source['nodes']}
    assert set(by)==set(expected) and len(source['nodes'])==32,'Exact classification inventory'
    for code,n in by.items():
        assert n['label'] in (expected[code]['label'],code+' '+expected[code]['label']) and n.get('detail','')==expected[code]['detail'],code+' field fidelity'
    ids={n['id']:code for code,n in by.items()}
    edges={(ids[e['source']],ids[e['target']],e['kind']) for e in source['edges']}
    wanted={(c[:-1],c,'contains') for c in expected if len(c)>1}|{('A22','C1','influence'),('B13','C23','uncertain')}
    assert edges==wanted and len(source['edges'])==31,'Complete typed relationship inventory'
    svg=workspace/'deliverables/poster.svg';tree=ET.parse(svg)
    ns={'s':'http://www.w3.org/2000/svg'}
    assert json.loads(tree.find('s:metadata',ns).text)==source,'SVG and delivered source differ'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page()
        page.goto(svg.resolve().as_uri());page.evaluate('document.fonts.ready')
        actual=page.evaluate('''() => {const s=document.querySelector('svg'),v=s.viewBox.baseVal;const text=[...s.querySelectorAll('text')].map(e=>{const b=e.getBBox();return {value:e.textContent,record:e.closest('[data-record-id]')?.dataset.recordId,role:e.dataset.role,x:b.x,y:b.y,w:b.width,h:b.height,size:parseFloat(getComputedStyle(e).fontSize)}});return {text,width:v.width,height:v.height,records:[...s.querySelectorAll('[data-record-id]')].map(e=>e.dataset.recordId)}}''')
        assert set(actual['records'])==set(ids) and len(actual['records'])==32
        for code,n in by.items():
            kicker=code if n.get('code',n.get('date_label')) is not None else ''
            for role,value in [('label',n['label']),('kicker',kicker),('detail',n.get('detail',''))]:
                rendered=' '.join(t['value'] for t in actual['text'] if t['record']==n['id'] and t['role']==role)
                assert ' '.join(rendered.split())==' '.join(value.split()),(code,role,rendered,value)
        for i,t in enumerate(actual['text']):
            assert t['size']>=14 and t['x']>=0 and t['y']>=0 and t['x']+t['w']<=actual['width']+.5 and t['y']+t['h']<=actual['height']+.5
            for u in actual['text'][i+1:]:
                assert not (t['x']<u['x']+u['w']-1 and t['x']+t['w']>u['x']+1 and t['y']<u['y']+u['h']-1 and t['y']+t['h']>u['y']+1),(t['value'],u['value'])
        browser.close()
    assert any('synthetic' in t['value'].lower() for t in actual['text']),'Visible synthetic provenance'
    return dict(status='pass',records=32,contains=29,cross_references=2,canvas=[actual['width'],actual['height']],
                visual_review='Evaluator must inspect PNG and prose; this does not certify an agent visual critique.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('workspace',type=Path);p.add_argument('--prompt',type=Path,default=Path('evaluations/pi-prompts/usefulcharts-panel-outlines-forward.md'))
    args=p.parse_args()
    try:result=check(args.workspace,args.prompt)
    except (AssertionError,KeyError,ValueError,OSError) as e:result=dict(status='fail',error=str(e))
    (args.workspace.parent/'independent-panel-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
    return result['status']!='pass'

if __name__=='__main__':raise SystemExit(main())

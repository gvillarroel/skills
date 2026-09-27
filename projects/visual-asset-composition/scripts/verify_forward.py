#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Inspect isolated outputs independently of the tested agent's self-reports."""
import argparse
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/visual-asset-composition/artifacts/forward-review'
BOUNDS="""() => {
  const svg=document.querySelector('svg');
  for(const a of svg.getAnimations({subtree:true})){try{a.finish()}catch{}}
  const root=svg.getBoundingClientRect();
  return [...svg.querySelectorAll('path,rect,circle,ellipse,line,polyline,polygon,text')].filter(e=>!e.closest('defs,clipPath,mask,pattern,symbol')).map(e=>{const b=e.getBoundingClientRect();return {tag:e.tagName,text:e.textContent,box:[b.x-root.x,b.y-root.y,b.width,b.height]}});
}"""


def selected(skill,kind):
    if skill=='d3': return 'd'
    if skill=='plantuml-colorset-renderer': return 'f'
    if skill=='procedural-svg-animation': return 'g'
    if skill=='echarts-animated-svg' and kind=='contract': return 'b'
    return 'a'


def inspect(browser,skill,kind,workspace,run_id):
    results=[]
    errors=[]
    if skill=='echarts-animated-svg':
        for motion in ['reduce','no-preference']:
            boxes=[]
            for name in ['input.svg','output.svg']:
                page=browser.new_page(reduced_motion=motion)
                page.set_content('<style>body{margin:0}svg{display:block}</style>'+ (workspace/name).read_text(encoding='utf-8'))
                boxes.append(page.evaluate(BOUNDS))
                if name=='output.svg': page.screenshot(path=str(OUT/f'{run_id}-{motion}.png'))
                page.close()
            assert len(boxes[0])==len(boxes[1])
            delta=max(abs(a-b) for x,y in zip(*boxes) for a,b in zip(x['box'],y['box']))
            assert delta<.15, delta
            assert [r['text'] for r in boxes[0]]==[r['text'] for r in boxes[1]]
            results.append({'motion':motion,'marks':len(boxes[0]),'maxDelta':delta})
        validation=json.loads((workspace/'validation.json').read_text(encoding="utf-8"))
        assert validation.get('ok',validation.get('passed',False)), validation
    elif skill=='plantuml-colorset-renderer':
        svg=ET.parse(workspace/'rendered/svg/diagram.svg').getroot()
        report=json.loads((workspace/'report.json').read_text(encoding="utf-8"))
        assert report['ok'] and report['failedDiagramCount']==0
        assert len(list(svg.iter()))>5
        rects=[float(e.get('height')) for e in svg.iter() if e.tag.endswith('}rect')]
        if kind=='boundary': assert any(abs(h-49.7988)<.01 for h in rects),rects
        if kind!='generalization': assert '#FFCCD5' not in (workspace/'rendered/svg/diagram.svg').read_text(encoding="utf-8").upper()
        page=browser.new_page(viewport={'width':800,'height':800})
        page.goto((workspace/'rendered/svg/diagram.svg').as_uri())
        page.screenshot(path=str(OUT/f'{run_id}.png'))
        page.close()
        results.append({'viewBox':svg.get('viewBox'),'rectHeights':rects,'colorset':report['colorset']})
    else:
        target=workspace/('studio.html' if skill=='d3' else 'gallery/index.html')
        for width in [390,1440]:
            page=browser.new_page(viewport={'width':width,'height':844 if width==390 else 1000},has_touch=width==390,reduced_motion='reduce')
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(target.as_uri())
            page.wait_for_timeout(250)
            overflow=page.evaluate('Math.max(0,document.documentElement.scrollWidth-innerWidth)')
            assert overflow<=1,overflow
            if skill=='d3':
                value=page.evaluate("""()=>{const p=document.querySelector('.studio-preview').getBoundingClientRect(),c=document.querySelector('.controls').getBoundingClientRect(),s=document.querySelector('#studio-logo');return {previewBottom:p.bottom,controlsTop:c.top,brand:document.querySelector('#brand').value,colorset:document.querySelector('#colorset').value,cards:document.querySelectorAll('.logo-card').length,marks:s.querySelectorAll('*').length,shortControls:[...document.querySelectorAll('button,select,input')].filter(e=>e.getBoundingClientRect().height<44).length}}""")
                assert value['cards']==90 and value['marks']>6,value
                brands={'contract':'ASTER','naturalistic':'LUMA','boundary':'NORTHLIGHT RESEARCH COLLECTIVE','generalization':'BRUMA'}
                assert value['brand']==brands[kind],value
                assert value['colorset']==('colorset2' if kind=='generalization' else 'colorset1')
                if width==390: assert value['previewBottom']<=value['controlsTop'] and value['previewBottom']<710 and value['shortControls']==0,value
            else:
                value=page.evaluate("""()=>({cards:document.querySelectorAll('[data-pattern-id].pattern-card').length,disclosure:!!document.querySelector('.family-browser'),collapsed:!document.querySelector('.family-browser')?.open,shortControls:[...document.querySelectorAll('button,select,input')].filter(e=>e.getBoundingClientRect().height>0&&e.getBoundingClientRect().height<44).length})""")
                manifest=json.loads((workspace/'gallery/manifest.json').read_text(encoding="utf-8"))
                assert manifest['patternCount']==66 and value['cards']==66 and value['disclosure'] and value['collapsed'],value
                assert len(list((workspace/'gallery').rglob('*.svg')))==66
                if width==390: assert value['shortControls']==0,value
                if kind=='generalization':
                    roots=[ET.parse(p).getroot() for p in (workspace/'gallery').rglob('*.svg')]
                    assert all(r.get('viewBox')=='0 0 800 500' for r in roots)
            page.screenshot(path=str(OUT/f'{run_id}-{width}.png'))
            results.append({'width':width,'overflow':overflow,**value})
            page.close()
    assert not errors,errors
    return results


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--complete',action='store_true')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    definitions=json.loads((ROOT/'evaluations/visual-asset-composition/cases.json').read_text(encoding="utf-8"))
    rows=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='msedge')
        for skill,cases in definitions.items():
            for kind in cases:
                for repeat in range(1,(3 if kind in ['naturalistic','generalization'] else 1)+1):
                    run_id=f'assets-{skill}-{kind}-20260927-{selected(skill,kind)}-{repeat}'
                    run=ROOT/'evaluations/runs'/run_id
                    result=run/'evaluation-result.json'
                    if not result.exists():
                        rows.append({'runId':run_id,'skill':skill,'case':kind,'missing':True,'passed':False})
                        continue
                    record=json.loads(result.read_text(encoding="utf-8"))
                    try:
                        checks=inspect(browser,skill,kind,run/'workspace',run_id)
                        row={'runId':run_id,'skill':skill,'case':kind,'passed':record['passed'],'artifactPassed':True,'checks':checks}
                    except Exception as error:
                        row={'runId':run_id,'skill':skill,'case':kind,'passed':False,'artifactPassed':False,'error':str(error)}
                    # Inspect the completed event surface with the repository's independent summarizer.
                    summary=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(run/'events.jsonl'),'--require-model','gpt-5.6-luna','--fail-on-invalid-json','--fail-on-tool-error'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
                    (OUT/f'{run_id}-events.json').write_text(summary.stdout,encoding='utf-8')
                    row['tracePassed']=summary.returncode==0
                    if summary.returncode==0:
                        event_summary=json.loads(summary.stdout)
                        row['readPaths']=[v['path'] for v in event_summary['readPaths']]
                    row['passed']=row['passed'] and row['tracePassed']
                    rows.append(row)
                    print(json.dumps({k:v for k,v in row.items() if k not in ['checks','readPaths']}),flush=True)
        browser.close()
    (OUT/'report.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    # Repeated naturalistic/generalization cases require two of three successes.
    failed=[]
    for skill,cases in definitions.items():
        for kind in cases:
            group=[r for r in rows if r['skill']==skill and r['case']==kind]
            if not args.complete and all(r.get('missing') for r in group):continue
            required=2 if kind in ['naturalistic','generalization'] else 1
            if sum(bool(r['passed']) for r in group)<required:failed.append([skill,kind])
    print(json.dumps({'reviewed':sum(not r.get('missing',False) for r in rows),'failedCases':failed}))
    return int(bool(failed))


if __name__=='__main__':raise SystemExit(main())

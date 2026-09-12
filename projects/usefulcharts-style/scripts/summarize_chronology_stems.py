#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain every mixed-chronology trial, exact source check and visual decision."""

import copy
import importlib.util
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def inspect_mixed(folder,contract):
    result=contract.inspect(folder)
    data=json.loads((folder/'workspace/result/source.json').read_text(encoding='utf-8'))
    root=ET.parse(folder/'workspace/result/poster.svg').getroot()
    stems={period['id'] for period in data['periods'] if period.get('treatment')=='stem'}
    visible={node.get('data-node-id') for node in root.findall('.//s:g[@data-node-id]',NS) if node.find('s:rect[@data-period-stem]',NS) is not None}
    if not stems or len(stems)==len(data['periods']) or stems!=visible:
        result['findings'].append('The requested selective mixture of stems and bands is absent or inconsistent.')
    result.update(status='fail' if result['findings'] else 'pass',stems=len(stems),full_bands=len(data['periods'])-len(stems),
        lane_weights=[lane.get('weight',1) for lane in data['lanes']])
    return result


def inspect_command(folder):
    workspace=folder/'workspace';load=lambda path:json.loads((workspace/path).read_text(encoding='utf-8'))
    source=load('draft.json');data=load('deliverables/brief.json');normalized=copy.deepcopy(data)
    for event in normalized['events']:event.pop('offset',None);event.pop('width',None)
    root=ET.parse(workspace/'deliverables/poster.svg').getroot();findings=[]
    if source!=normalized:findings.append('The helper changed a protected source field.')
    if load('deliverables/browser.json')['status']!='pass':findings.append('The source-backed browser audit failed.')
    expected={'early':(190,454.3,5),'ridge':(190,1298,4)}
    for nid,(y,h,w) in expected.items():
        stem=root.find(f'.//s:g[@data-node-id="{nid}"]/s:rect[@data-period-stem]',NS)
        if stem is None or any(abs(float(stem.get(key))-value)>.1 for key,value in [('y',y),('height',h),('width',w)]):findings.append(f'Wrong visible duration: {nid}')
    ridge=root.find('.//s:g[@data-node-id="ridge"]/s:rect[@data-node-box]',NS)
    expected_x=110+(1200-175)*1.4/2.4+20
    if abs(float(ridge.get('x'))-expected_x)>.1:findings.append('The weighted lane position is incorrect.')
    return dict(status='fail' if findings else 'pass',exact_source_preserved=source==normalized,visible_stems=2,findings=findings,
        limitation='Command control; no agent aesthetic judgement is required.')


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('regions_contract',root/'evaluations/contracts/verify-usefulcharts-regions.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    review_path=root/'evaluations/usefulcharts-style/chronology-stems-visual-reviews-20260912.json'
    reviews=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    runs=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v27*-20260912*')):
        load=lambda path:json.loads((folder/path).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        record=dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],expected_outputs=manifest['expectedOutputs'])
        if not (folder/'evaluation-result.json').exists():
            record['status']='running';runs.append(record);continue
        record['strict']=load('evaluation-result.json')
        checked=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True)
        surface=load('read-surface.json')
        record.update(read_surface_passed=checked.returncode==0,read_paths=[item['path'] for item in surface['readPaths']],read_bytes=surface['totalReadResultBytes'])
        try:artifact=inspect_mixed(folder,contract) if '-regions-' in folder.name else inspect_command(folder)
        except (FileNotFoundError,KeyError,ValueError) as error:artifact=dict(status='incomplete',findings=[str(error)])
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        record['independent_artifact']=artifact;errors=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                errors.extend(item['text'] for item in event.get('result',{}).get('content',[]) if item.get('type')=='text')
        record.update(tool_errors=errors,visual_review=reviews.get(folder.name,'Pending image review.'))
        runs.append(record)
    explorations=[]
    for folder in sorted((root/'projects/usefulcharts-style/artifacts/reviews').glob('chronology-stems-v27*')):
        if (folder/'attempts.json').exists():explorations.append(dict(stage=folder.name,attempts=json.loads((folder/'attempts.json').read_text(encoding='utf-8'))))
    report=dict(status='validating',runs=runs,explorations=explorations,visual_parity='Not established. Technical validity, visual critique and exact-source preservation are distinct claims.')
    output=root/'evaluations/usefulcharts-style/chronology-stems-summary-20260912.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(runs),strict_passes=sum(run.get('strict',{}).get('passed',False) for run in runs),running=sum(run.get('status')=='running' for run in runs),
        independent_passes=sum(run.get('independent_artifact',{}).get('status')=='pass' for run in runs))))


if __name__=='__main__':main()

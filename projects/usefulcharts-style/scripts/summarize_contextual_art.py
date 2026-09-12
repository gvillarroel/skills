#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain all contextual-art attempts, strict gates and direct visual critiques."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('art_contract',root/'evaluations/contracts/verify-usefulcharts-contextual-art.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    reviews_path=root/'evaluations/usefulcharts-style/contextual-art-visual-reviews-20260912.json'
    reviews=json.loads(reviews_path.read_text()) if reviews_path.exists() else {}
    runs=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v28*-20260912*')):
        load=lambda path:json.loads((folder/path).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        record=dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],expected_outputs=manifest['expectedOutputs'])
        if not (folder/'evaluation-result.json').exists():record['status']='running';runs.append(record);continue
        record['strict']=load('evaluation-result.json')
        result=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True)
        surface=load('read-surface.json')
        record.update(read_surface_passed=result.returncode==0,read_paths=[item['path'] for item in surface['readPaths']],read_bytes=surface['totalReadResultBytes'])
        try:artifact=contract.inspect(folder)
        except (FileNotFoundError,KeyError,ValueError) as error:artifact=dict(status='incomplete',findings=[str(error)])
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        record['independent_artifact']=artifact;errors=[];calls={}
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_start':calls[event['toolCallId']]=event.get('args',{})
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                errors.append(dict(arguments=calls.get(event['toolCallId']),messages=[item['text'] for item in event.get('result',{}).get('content',[]) if item.get('type')=='text']))
        record.update(tool_errors=errors,visual_review=reviews.get(folder.name,'Pending image review.'))
        preview=folder/('workspace/deliverables/poster.png' if '-contract-' in folder.name else 'workspace/result/poster.png')
        if preview.exists():record['preview_sha256']=hashlib.sha256(preview.read_bytes()).hexdigest()
        runs.append(record)
    explorations=[]
    for folder in sorted((root/'projects/usefulcharts-style/artifacts/reviews').glob('contextual-art-v28*')):
        if (folder/'outcomes.json').exists():
            outcomes=json.loads((folder/'outcomes.json').read_text())
            explorations.append(dict(stage=folder.name,attempts=[{k:v for k,v in item.items() if k not in ('placements','layout')} for item in outcomes]))
    gallery=root/'skills/usefulcharts-style/assets/examples/usefulcharts-style'
    source=json.loads((gallery/'five-regional-histories.json').read_text())
    svg=(gallery/'five-regional-histories.svg').read_bytes().replace(b'\r\n',b'\n')
    selected=(root/'projects/usefulcharts-style/artifacts/reviews/contextual-art-v28d/side-ship/poster.svg').read_bytes().replace(b'\r\n',b'\n')
    unchanged={}
    for name in ('aurelian-families','atlas-of-inquiry'):
        path='skills/usefulcharts-style/assets/examples/usefulcharts-style/'+name+'.svg'
        previous=subprocess.check_output(['git','show','c2131d54:'+path],cwd=root).replace(b'\r\n',b'\n')
        unchanged[name]=(root/path).read_bytes().replace(b'\r\n',b'\n')==previous
    mural=dict(periods=len(source['periods']),transitions=len(source['transitions']),events=len(source['events']),
        illustrations=sum(bool(e.get('icon')) for e in source['events']),svg_sha256=hashlib.sha256(svg).hexdigest(),
        selected_svg_matches=svg==selected,other_murals_unchanged=unchanged,
        source_sha256=hashlib.sha256(json.dumps(source,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        comparison=json.loads((root/'projects/usefulcharts-style/artifacts/reviews/contextual-art-final-comparison/comparison.json').read_text()))
    report=dict(status='validating',runs=runs,explorations=explorations,mural=mural,visual_parity='Not established. Improved local art composition does not establish broad parity.')
    receipt=root/'projects/usefulcharts-style/artifacts/reviews/contextual-art-publication-verification.json'
    if receipt.exists():
        published=json.loads(receipt.read_text())
        report['publication']=dict(status=published['status'],commit=published['commit'],workflow=published['workflow']['url'],url=published['url'],files_verified=len(published['files']))
    (root/'evaluations/usefulcharts-style/contextual-art-summary-20260912.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(runs),strict_passes=sum(run.get('strict',{}).get('passed',False) for run in runs),
        independent_passes=sum(run.get('independent_artifact',{}).get('status')=='pass' for run in runs),
        failures=[dict(id=run['id'],errors=run.get('tool_errors')) for run in runs if not run.get('strict',{}).get('passed')]),indent=2))


if __name__=='__main__':main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain every paragraph-composition exploration and isolated runtime attempt."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('note_contract',root/'evaluations/contracts/verify-usefulcharts-note-hierarchy.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    review_path=root/'evaluations/usefulcharts-style/note-hierarchy-visual-reviews-20260912.json'
    reviews=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else {}
    runs=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v29*-20260912*')):
        load=lambda path:json.loads((folder/path).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        record=dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],expected_outputs=manifest['expectedOutputs'])
        if not (folder/'evaluation-result.json').exists():record['status']='running';runs.append(record);continue
        record['strict']=load('evaluation-result.json')
        check=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True)
        surface=load('read-surface.json')
        record.update(read_surface_passed=check.returncode==0,read_paths=[item['path'] for item in surface['readPaths']],read_bytes=surface['totalReadResultBytes'])
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
        independent=folder/'evaluator-browser.json'
        if independent.exists():
            audit=json.loads(independent.read_text());record['evaluator_browser']=dict(status=audit['status'],findings=audit['findings'],composition_warnings=audit.get('composition_warnings',[]))
        runs.append(record)
    artifacts=root/'projects/usefulcharts-style/artifacts'
    explorations=[]
    for folder in sorted((artifacts/'reviews').glob('note-hierarchy-v29*')):
        outcomes=folder/'outcomes.json'
        if outcomes.exists():explorations.append(dict(stage=folder.name,attempts=json.loads(outcomes.read_text(encoding='utf-8'))))
    gallery=root/'skills/usefulcharts-style/assets/examples/usefulcharts-style'
    source=json.loads((gallery/'five-regional-histories.json').read_text(encoding='utf-8'));svg=(gallery/'five-regional-histories.svg').read_bytes().replace(b'\r\n',b'\n')
    selected=artifacts/'reviews/note-hierarchy-v29e/moderate-page'
    unchanged={}
    for name in ('aurelian-families','atlas-of-inquiry'):
        path='skills/usefulcharts-style/assets/examples/usefulcharts-style/'+name+'.svg'
        previous=subprocess.check_output(['git','show','5b2d3674:'+path],cwd=root).replace(b'\r\n',b'\n')
        unchanged[name]=(root/path).read_bytes().replace(b'\r\n',b'\n')==previous
    report=dict(status='validating',runs=runs,explorations=explorations,
        mural=dict(periods=len(source['periods']),transitions=len(source['transitions']),events=len(source['events']),
            paragraphs=sum(e.get('text_layout')=='paragraph' for e in source['events']),illustrations=sum(bool(e.get('icon')) for e in source['events']),
            svg_sha256=hashlib.sha256(svg).hexdigest(),selected_svg_matches=svg==(selected/'poster.svg').read_bytes().replace(b'\r\n',b'\n'),
            selected_png_matches=(artifacts/'images/note-hierarchy-final.png').read_bytes()==(selected/'poster.png').read_bytes(),
            png_sha256=hashlib.sha256((artifacts/'images/note-hierarchy-final.png').read_bytes()).hexdigest(),other_murals_unchanged=unchanged,
            source_sha256=hashlib.sha256(json.dumps(source,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
            comparison=json.loads((artifacts/'reviews/note-hierarchy-final-comparison/comparison.json').read_text())),
        previous_association_check=json.loads((artifacts/'reviews/note-hierarchy-previous-association.json').read_text())['composition_warnings'],
        visual_parity='Not established. Better paragraph hierarchy and local image groups do not resolve the repeated regional structure or prove broad parity.')
    receipt=artifacts/'reviews/note-hierarchy-publication-verification.json'
    if receipt.exists():
        published=json.loads(receipt.read_text());report['publication']=dict(status=published['status'],commit=published['commit'],workflow=published['workflow']['url'],url=published['url'],files_verified=len(published['files']))
    (root/'evaluations/usefulcharts-style/note-hierarchy-summary-20260912.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(runs),strict_passes=sum(run.get('strict',{}).get('passed',False) for run in runs),
        independent_passes=sum(run.get('independent_artifact',{}).get('status')=='pass' for run in runs),
        failures=[dict(id=run['id'],errors=run.get('tool_errors'),findings=run.get('independent_artifact',{}).get('findings')) for run in runs if not run.get('strict',{}).get('passed') or run.get('independent_artifact',{}).get('status')!='pass']),indent=2))


if __name__=='__main__':main()

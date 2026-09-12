#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain all isolated landmark attempts, errors, read surfaces and judgments."""

import importlib.util
import json
import subprocess
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('context_contract',root/'evaluations/contracts/verify-usefulcharts-family-landmarks.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    runs=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v*-*-20260912-*')):
        if not folder.name.startswith(('usefulcharts-v21-','usefulcharts-v22-','usefulcharts-v23-')):continue
        load=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        if not (folder/'evaluation-result.json').exists():
            runs.append(dict(id=folder.name,status='running',payload=manifest['skill']));continue
        result=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True)
        surface=load('read-surface.json');errors=[];images=[];invalid_lines=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            try:event=json.loads(line)
            except json.JSONDecodeError:
                invalid_lines.append(line[:200]);continue
            if event.get('type')!='tool_execution_end':continue
            blocks=event.get('result',{}).get('content',[])
            if event.get('isError'):errors.extend(c['text'] for c in blocks if c.get('type')=='text')
            images.extend(dict(mime=c.get('mimeType'),encoded_bytes=len(c.get('data',''))) for c in blocks if c.get('type')=='image')
        if '-family-' in folder.name:
            artifact=contract.inspect(folder,root)
        else:
            original=load('workspace/draft.json');resolved=load('workspace/result/source.json')
            by_id={n['id']:n for n in resolved['nodes']}
            same=set(by_id)=={n['id'] for n in original['nodes']} and all(all(by_id[n['id']].get(k)==v for k,v in n.items()) for n in original['nodes'])
            same=same and all(resolved.get(k)==v for k,v in original.items() if k not in ('layout','nodes','annotations'))
            annotations=lambda data:[{k:v for k,v in a.items() if k not in ('dx','dy')} for a in data['annotations']]
            same=same and annotations(original)==annotations(resolved)
            artifact=dict(status='pass' if same else 'fail',all_facts_preserved=same,
                placement=load('workspace/result/placement.json')['status'],browser=load('workspace/result/browser.json')['status'])
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        review=load('visual-review.json') if (folder/'visual-review.json').exists() else 'Command control only.' if '-contract-' in folder.name else 'Awaiting direct image review.'
        runs.append(dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],
            expected_outputs=manifest['expectedOutputs'],strict=load('evaluation-result.json'),independent_artifact=artifact,
            read_surface_passed=result.returncode==0,read_paths=[p['path'] for p in surface['readPaths']],
            tool_errors=errors,supported_image_results=images,visual_review=review))
        runs[-1]['invalid_event_lines']=invalid_lines
        if (folder/'expired-process-review.json').exists():runs[-1]['expired_process_review']=load('expired-process-review.json')
    report=dict(status='validating',runs=runs,visual_parity='Not established. Preserve the full dense-poster target and previous unresolved findings.')
    output=root/'evaluations/usefulcharts-style/context-landmarks-summary-20260912.json'
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(runs),strict_passes=sum(r.get('strict',{}).get('passed',False) for r in runs),
        running=sum(r.get('status')=='running' for r in runs))))


if __name__=='__main__':main()

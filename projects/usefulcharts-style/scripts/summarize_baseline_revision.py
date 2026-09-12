#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain every v18/v19 family trial, trace, independent check and visual verdict."""

import importlib.util
import json
import subprocess
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[3]
    spec=importlib.util.spec_from_file_location('family_contract',root/'evaluations/contracts/verify-usefulcharts-family-baselines.py')
    contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    results=[]
    for folder in sorted((root/'evaluations/runs').glob('usefulcharts-v*-20260912-*')):
        if not folder.name.startswith(('usefulcharts-v18-','usefulcharts-v19-')):continue
        load=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');model=manifest['pi']['model'].split('/')[-1]
        if not (folder/'evaluation-result.json').exists():
            results.append(dict(id=folder.name,status='running',payload=manifest['skill']));continue
        check=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True)
        surface=load('read-surface.json');errors=[];images=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')!='tool_execution_end':continue
            blocks=event.get('result',{}).get('content',[])
            if event.get('isError'):errors.extend(c['text'] for c in blocks if c.get('type')=='text')
            images.extend(dict(mime=c.get('mimeType'),bytes=len(c.get('data',''))) for c in blocks if c.get('type')=='image')
        if '-family-' in folder.name:
            artifact=contract.inspect(folder,root)
            if folder.name.startswith('usefulcharts-v18-'):
                visual={'1':'Readable names, but repetitive filled boxes and long lateral routes. Rejected as visual parity.',
                    '2':'Rejected: excessive 1450 by 2600 canvas, small repeated cards and very long vertical gaps.',
                    '3':'Compact but undersized names/dates and uniformly long nameplates. Rejected as visual parity.'}[folder.name[-1]]
            else:
                review=folder/'visual-review.json'
                visual=json.loads(review.read_text()) if review.exists() else 'Awaiting direct image review.'
        else:
            original=load('workspace/draft.json');resolved=load('workspace/deliverables/brief.json')
            by_id={n['id']:n for n in resolved['nodes']}
            same=all(all(by_id[n['id']].get(k)==v for k,v in n.items()) for n in original['nodes'])
            same=same and all(original[k]==resolved[k] for k in ['unions','edges','groups'])
            artifact=dict(status='pass' if same else 'fail',all_facts_preserved=same,
                spacing=load('workspace/deliverables/spacing.json')['status'],render=load('workspace/deliverables/layout.json')['status'])
            visual='Exact-command control only; no visual acceptance claim.'
        (folder/'independent-artifact.json').write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
        results.append(dict(id=folder.name,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],
            expected_outputs=manifest['expectedOutputs'],strict=load('evaluation-result.json'),independent_artifact=artifact,
            read_surface_passed=check.returncode==0,read_paths=[p['path'] for p in surface['readPaths']],
            tool_errors=errors,supported_image_results=images,visual_review=visual))
    report=dict(status='validating',runs=results,visual_parity='Not established. Keep strict execution, exact data and aesthetic findings separate.')
    output=root/'evaluations/usefulcharts-style/genealogy-baselines-summary-20260912.json'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(results),strict_passes=sum(r.get('strict',{}).get('passed',False) for r in results),
        running=sum(r.get('status')=='running' for r in results))))


if __name__=='__main__':main()

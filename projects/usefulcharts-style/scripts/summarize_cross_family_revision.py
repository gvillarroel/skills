#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect all cross-family attempts while retaining failures and prompt revisions."""

import json
import re
import subprocess
from pathlib import Path


def boundary_contract(folder):
    workspace=folder/'workspace';data=json.loads((workspace/'review/source.json').read_text(encoding='utf-8'))
    diagnostic=json.loads((workspace/'review/diagnostic.json').read_text(encoding='utf-8'))
    findings=[];people=data.get('nodes',data.get('people',[]));names={n['id']:n.get('label',n.get('name')) for n in people}
    if set(names.values())!={'Ada Vale','Bram Lake','Cora Vale'}:findings.append('Known person inventory changed.')
    years={'Ada Vale':1700,'Bram Lake':1702,'Cora Vale':1730}
    for person in people:
        name=names[person['id']]
        if name in years and not re.search(rf'\b{years[name]}\b',json.dumps(person)):findings.append(f'Birth year missing for {name}.')
    if diagnostic.get('status')!='needs-data' or diagnostic.get('missing_ids')!=['unknown-42']:findings.append('Missing-person diagnostic changed.')
    relations=json.dumps([data.get(key,[]) for key in ('unions','edges','relationships','parent_references')])
    if 'unknown-42' not in relations:findings.append('Unresolved parent reference was dropped.')
    bram=next((i for i,n in names.items() if n=='Bram Lake'),None)
    if bram and f'"{bram}"' in relations:findings.append('Bram was inserted into an unsupported relationship.')
    pairs=[]
    for union in data.get('unions',[]):pairs.extend((p,c) for p in union['partners'] for c in union.get('children',[]))
    for edge in data.get('edges',[]):pairs.append((edge['source'],edge['target']))
    for relationship in data.get('relationships',[])+data.get('parent_references',[]):
        child=relationship.get('child_id',relationship.get('child'))
        pairs.extend((p,child) for p in relationship.get('parent_ids',relationship.get('parents',[])))
    actual={(names.get(p,p),names.get(c,c)) for p,c in pairs}
    if actual!={('Ada Vale','Cora Vale'),('unknown-42','Cora Vale')}:findings.append('Exact supplied parentage changed.')
    if list(workspace.glob('review/*.svg')):findings.append('An unresolved final SVG was produced.')
    return dict(status='fail' if findings else 'pass',findings=findings)


def main():
    root=Path(__file__).resolve().parents[3]
    cases=[('cohorts','v11','gpt55',1),('transport','v11','gpt55',1),('boundary','v11','spark',1),
           ('cohorts','v12','gpt55',1),('transport','v12','gpt55',1),('contract','v12','spark',1)]
    cases += [(case,'v13','gpt55',i) for case in ('cohorts','transport') for i in range(1,4)]
    cases += [('contract','v13','spark',1)]+[('boundary','v13','spark',i) for i in range(1,4)]
    runs=[]
    for case,version,tag,index in cases:
        run_id=f'usefulcharts-{case}-{version}-20260911-{tag}-{index}'
        folder=root/'evaluations/runs'/run_id
        if not (folder/'evaluation-result.json').exists():raise RuntimeError(f'Unfinished required run: {run_id}')
        model='gpt-5.5' if tag=='gpt55' else 'gpt-5.3-codex-spark'
        summary=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),
            '--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],
            cwd=root,capture_output=True,text=True,check=False)
        load=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');events=load('read-surface.json');result=load('evaluation-result.json')
        if case in ('cohorts','transport') and version!='v11':
            check=subprocess.run(['uv','run','--script','evaluations/contracts/verify-usefulcharts-families.py',str(folder),
                '--case',case,'--output',str(folder/'independent-artifact.json')],cwd=root,capture_output=True,text=True,check=False)
            if check.returncode not in (0,1):raise RuntimeError(check.stderr or check.stdout)
            contract=load('independent-artifact.json')
        elif case=='boundary':contract=boundary_contract(folder)
        else:contract=dict(status='not-applicable',reason='See the authored baseline review or separate command-contract browser audit.')
        errors=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                errors.extend(c['text'] for c in event.get('result',{}).get('content',[]) if c.get('type')=='text')
        runs.append(dict(id=run_id,case=case,version=version,model=model,payload=manifest['skill'],prompt_sha256=manifest['prompt']['sha256'],
            expected_outputs=manifest['expectedOutputs'],duration_seconds=result['durationSeconds'],strict=result,
            independent_artifact=contract,read_summary_returncode=summary.returncode,
            read_paths=[p['path'] for p in events['readPaths']],total_read_bytes=events['totalReadResultBytes'],tool_errors=errors))
    output=root/'evaluations/usefulcharts-style/cross-family-revision-summary-20260911.json'
    report=dict(status='validating',runs=runs,visual_parity='Not established. Source and geometry checks do not grade resemblance.')
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(summary=str(output),completed_runs=len(runs),strict_passes=sum(r['strict']['passed'] for r in runs))))


if __name__=='__main__':main()

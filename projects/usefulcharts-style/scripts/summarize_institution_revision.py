#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect preserved institution-case run evidence without rewriting any output."""

import json
import subprocess
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[3]
    versions=[('v7','spark',1),('v8','spark',1)]+[('v9','spark',i) for i in range(1,4)]+[(v,'gpt55',i) for v in ('v10','v11') for i in range(1,4)]
    runs=[]
    for version,tag,index in versions:
        run_id=f'usefulcharts-institutions-{version}-20260911-{tag}-{index}'
        folder=root/'evaluations/runs'/run_id
        if not (folder/'evaluation-result.json').exists():continue
        model='gpt-5.5' if tag=='gpt55' else 'gpt-5.3-codex-spark'
        subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),'--require-model',model,
            '--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'read-surface.json')],cwd=root,capture_output=True,check=False)
        subprocess.run(['uv','run','--script','evaluations/contracts/verify-usefulcharts-institutions.py',str(folder),'--output',str(folder/'independent-contract.json')],cwd=root,capture_output=True,check=False)
        load=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=load('run-manifest.json');events=load('read-surface.json');result=load('evaluation-result.json');contract=load('independent-contract.json')
        errors=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                errors.extend(c['text'] for c in event.get('result',{}).get('content',[]) if c.get('type')=='text')
        runs.append(dict(id=run_id,model=model,payload=manifest['skill'],duration_seconds=result['durationSeconds'],strict=result,
            artifact_contract=contract,read_paths=[p['path'] for p in events['readPaths']],total_read_bytes=events['totalReadResultBytes'],tool_errors=errors,
            classification='See the authored evaluation; model capability, agent execution and visual judgment are separate.'))
    output=root/'evaluations/usefulcharts-style/institution-revision-summary-20260911.json'
    output.write_text(json.dumps(dict(status='validating',runs=runs,visual_parity='Not established by these checks.'),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(summary=str(output),completed_runs=len(runs),strict_passes=sum(r['strict']['passed'] for r in runs))))


if __name__=='__main__':main()

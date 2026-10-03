#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize observed validation outcomes without reproducing model reasoning."""
from pathlib import Path
import json
import hashlib
import subprocess
import re

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'evaluations/usefulcharts-style/cross-domain-runtime-summary-20260912.json'

def main():
    rows=[]
    run_ids=[f'20260912-usefulcharts-panel-outlines-{s}' for s in ['1','2','3','b1','b2','b3','luna-1','luna-2','luna-3']]
    for run_id in run_ids:
        folder=ROOT/'evaluations/runs'/run_id
        if not (folder/'evaluation-result.json').exists():continue
        read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        manifest=read('run-manifest.json');events=read('event-check.json');independent=read('independent-panel-check.json') if (folder/'independent-panel-check.json').exists() else None
        result=read('evaluation-result.json');image_reads=[];errors=[];commands=[]
        for call in events['calls']:
            if call['tool']=='read' and str(call.get('path','')).lower().endswith('.png'):image_reads.append(call['path'])
            if call.get('isError'):errors.append(dict(tool=call['tool'],path=call.get('path'),command_excerpt=(call.get('command') or '')[:350]))
            if call.get('command'):commands.append(call['command'])
        trace=subprocess.run(['uv','run','--script',str(ROOT/'scripts/summarize-pi-json-events.py'),str(folder/'events.jsonl'),
            '--require-model',manifest['pi']['model'].split('/')[-1],'--fail-on-invalid-json','--fail-on-tool-error','--output',str(folder/'trace-summary.json')],
            cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (folder/'trace-summary.log').write_text(trace.stdout+trace.stderr,encoding='utf-8')
        sensitive=[line for c in commands for line in c.splitlines() if re.search(r'write_|mkdir|\b(cp|mv|rm|cd)\b|open\(.+[\x22\x27][wa][\x22\x27]|/tmp/|[A-Z]:[\\/]',line)]
        rows.append(dict(run_id=run_id,model=manifest['pi']['model'],runtime=manifest['skill'],
            strict_pass=events['passed'],artifact_gate=read('artifact-check.json')['passed'],integrity=read('skill-integrity-check.json')['passed'],trace_summary_exit=trace.returncode,
            independent=independent,image_reads=image_reads,errors=errors,
            read_paths=[c['path'] for c in events['calls'] if c['tool']=='read'],command_count=len(commands),scope_sensitive_lines=sensitive,
            commands_sha256=hashlib.sha256(json.dumps(commands).encode()).hexdigest(),duration_seconds=result['durationSeconds'],
            raw_evidence='evaluations/runs/'+run_id))
    OUT.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for r in rows:print(json.dumps(dict(run=r['run_id'],model=r['model'],strict=r['strict_pass'],independent=r['independent']['status'] if r['independent'] else None,images=r['image_reads'],errors=len(r['errors']),runtime=r['runtime']['payloadSha256'])))

if __name__=='__main__':main()

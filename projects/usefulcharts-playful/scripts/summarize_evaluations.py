#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain compact evidence from all preregistered runs, including payload boundaries."""
from pathlib import Path
import hashlib
import json
import subprocess
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def main():
    expected=json.loads((ROOT/'artifacts/evaluation-input-hashes.json').read_text());summaries=[]
    run_ids=[f'20260913-usefulcharts-illustrated-luna-{n}' for n in [1,2,3]]+['20260913-usefulcharts-illustrated-spark-command','20260913-usefulcharts-illustrated-spark-final']
    for identifier in run_ids:
        folder=REPO/'evaluations/runs'/identifier;result=json.loads((folder/'evaluation-result.json').read_text());manifest=json.loads((folder/'run-manifest.json').read_text());events=json.loads((folder/'event-check.json').read_text());integrity=json.loads((folder/'skill-integrity-check.json').read_text())
        item=dict(run_id=identifier,strict_pass=result['passed'],model=manifest['pi']['model'],runtime_sha256=integrity['afterDigest'],runtime_files=manifest['skill']['fileCount'],runtime_unchanged=integrity['passed'],read_paths=[c['path'] for c in events['calls'] if c['tool']=='read'],tool_errors=sum(c['isError'] for c in events['calls']),duration_seconds=result['durationSeconds'])
        if 'luna' in identifier:
            verdict=json.loads((folder/'workspace/deliverables/verdicts.json').read_text(encoding='utf-8'));actual={name:hashlib.sha256((folder/'workspace/input'/name).read_bytes()).hexdigest() for name in expected};item['raw_inputs_unchanged']=actual==expected
            item['image_reads_verified']=all('input/'+name in item['read_paths'] for name in expected if name.endswith('.png'))
            item['verdicts']={c['id']:c['illustrated_brief_pass'] for c in verdict['candidates']};item['discrimination_pass']=item['verdicts']==dict(p=False,q=False,r=True)
            item['dimensions']={c['id']:c['dimensions'] for c in verdict['candidates']}
            assert item['raw_inputs_unchanged'] and item['image_reads_verified'] and item['discrimination_pass']
        assert item['strict_pass'] and item['runtime_unchanged'] and item['tool_errors']==0
        model=manifest['pi']['model'].split('/')[-1]
        check=subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(folder/'events.jsonl'),'--require-model',model,'--fail-on-invalid-json','--fail-on-tool-error'],cwd=REPO,text=True,encoding='utf-8',capture_output=True)
        assert check.returncode==0,check.stderr
        (folder/'verified-read-surface.txt').write_text(check.stdout,encoding='utf-8');summaries.append(item)
    target=REPO/'evaluations/usefulcharts-style/illustrated-discovery-20260913.json'
    target.write_text(json.dumps(dict(date='2026-09-13',visual_task='Three fixed museum candidates; text-only, header-only and body-integrated images',image_model_exception='Preregistered Luna high because direct image reading is required',runs=summaries,limits=['One development discrimination task repeated three times, not a held-out broad-domain production benchmark.','The three visual runs use the earlier runtime; a later viewport-auditor fix is covered by the final Spark control.','Final instrument captions incorporate optional visual criticism after the input freeze.','No reference-density or UsefulCharts stylistic-parity claim is supported.']),indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(runs=len(summaries),strict_passes=sum(r['strict_pass'] for r in summaries),visual_discrimination_passes=sum(r.get('discrimination_pass',False) for r in summaries),final_runtime=summaries[-1]['runtime_sha256'])))
if __name__=='__main__':main()

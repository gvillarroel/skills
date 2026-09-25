#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain both cohorts and independently grade the final decision release."""

import concurrent.futures
import json
import os
import subprocess
from pathlib import Path

root=Path(__file__).resolve().parents[3]
runs=root/'evaluations/runs'
reviews=root/'projects/hierarchy-lens/artifacts/reviews'
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(root/'projects/hierarchy-lens/artifacts/browser-cache')


def collect(run):
    manifest=json.loads((run/'run-manifest.json').read_text(encoding='utf-8'))
    result=json.loads((run/'evaluation-result.json').read_text(encoding='utf-8'))
    trace_path=run/'read-surface.json'
    subprocess.run(['uv','run','--script','scripts/summarize-pi-json-events.py',str(run/'events.jsonl'),'--require-model','gpt-5.6-luna','--fail-on-invalid-json','--fail-on-tool-error','--output',str(trace_path)],cwd=root,capture_output=True)
    trace=json.loads(trace_path.read_text(encoding='utf-8'))
    item={'runId':run.name,'cohort':'v2' if '-v2-' in run.name else 'initial','passed':result['passed'],
          'model':'gpt-5.6-luna','gates':result['gates'],'seconds':result['durationSeconds'],
          'payloadSha256':manifest['skill']['payloadSha256'],'runtimeFiles':manifest['skill']['fileCount'],
          'readPaths':[r['path'] for r in trace['readPaths']],'tracePassed':trace['passed'],'traceFindings':trace['findings']}
    if not result['passed']:
        findings=[]
        for filename in ['event-check.json','json-field-check.json']:
            path=run/filename
            if path.exists():findings.extend(json.loads(path.read_text(encoding='utf-8')).get('findings',[]))
        item['failureFindings']=findings
        if run.name in {'hierarchy-decisions-contract-20260925-luna-1','hierarchy-decisions-contract-20260925-luna-v2-1'}:
            item.update(classification='harness',reason='The exact-command scanner accepts only empty/bash/sh/shell fences; the initial text fence and the attempted powershell correction were not recognized. The agent ran the exact command and all artifact/JSON gates passed. A fresh shell-fence retry uses the unchanged final skill payload. Both rejected attempts remain failures.')
        elif run.name=='hierarchy-decisions-naturalistic-20260925-luna-3':
            item.update(classification='agent',reason='The agent retained the demonstration role priority despite the requested descending token priority. Added direct CLI overrides and an explicit report-to-request check to simplify the workflow.')
        elif run.name in {'hierarchy-decisions-generalization-20260925-luna-1','hierarchy-decisions-generalization-20260925-luna-2'}:
            item.update(classification='agent',reason='The agent omitted --cell-pixels 1 and produced four pixels per record. Trial 2 also attempted the same input/data-output path and recovered after a tool error. Both remain failures. The compact recipe now explicitly maps cell area to the required flag and avoids redundant input rewriting.')
        else:
            item.update(classification='unclassified',reason='Inspect the retained findings before release.')
    if result['passed'] and 'boundary' not in run.name:
        portfolio='generalization' in run.name
        folder=run/'workspace'/('results' if portfolio else 'deliverables')
        stem='portfolio' if portfolio else 'organization' if 'naturalistic' in run.name else 'map'
        source=folder/('source.json' if stem=='map' else stem+'.json')
        html=folder/(stem+'.html')
        command=['uv','run','--script','evaluations/contracts/check-hierarchy-lens.py',str(source),str(html)]
        command += ['--portfolio'] if portfolio else ['--count','430' if stem=='organization' else '73']
        oracle=subprocess.run(command,cwd=root,capture_output=True,text=True)
        item['sourceOraclePassed']=oracle.returncode==0
        raw=json.loads(source.read_text(encoding='utf-8'))
        build=json.loads((folder/'build.json').read_text(encoding='utf-8'))
        policy=build['composition']
        priority=next(d for d in raw['dimensions'] if d['key']==policy['priority']['key'])
        item['requestedPolicyPassed']=stem=='map' or priority['type']=='numeric' and priority['unit']=='tokens' and policy['priority']['direction']=='descending' and policy['eligibility']==('parent' if portfolio else 'generation')
        if portfolio:
            item['requestedPolicyPassed'] &= policy['weights']=={'parent':4,'affinity':3,'compactness':2,'radial':1} and policy['frontierWindow']==2 and build['minPixelsPerRecord']==build['maxPixelsPerRecord']==1
        elif stem=='organization':
            affinity=next(d for d in raw['dimensions'] if d['key']==policy['affinity'])
            item['requestedPolicyPassed'] &= affinity['label'].lower()=='role' and build['minPixelsPerRecord']==build['maxPixelsPerRecord']==4
        audit=reviews/(run.name+'-independent.json')
        browser=subprocess.run(['uv','run','--script','skills/hierarchy-lens/scripts/audit_decisions.py',str(html),'--report',str(audit)],cwd=root,capture_output=True,text=True)
        item['independentBrowserPassed']=browser.returncode==0
        if browser.returncode or oracle.returncode:item['independentFailure']=browser.stdout+browser.stderr+oracle.stdout+oracle.stderr
    return item


paths=[p.parent for p in sorted(runs.glob('hierarchy-decisions-*-20260925-luna-*/evaluation-result.json'))]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    collected=list(pool.map(collect,paths))
groups={}
for cohort in ['initial','v2']:
    groups[cohort]={}
    for case in ['contract','naturalistic','generalization','boundary']:
        rows=[r for r in collected if r['cohort']==cohort and f'-{case}-' in r['runId']]
        groups[cohort][case]={'runs':len(rows),'passes':sum(r['passed'] and r['tracePassed'] and r.get('sourceOraclePassed',True) and r.get('requestedPolicyPassed',True) and r.get('independentBrowserPassed',True) for r in rows)}
routing=json.loads((runs/'hierarchy-decisions-routing-20260925-luna-1/result.json').read_text(encoding='utf-8'))
local={}
for name in ['decisions-final-audit','decisions-5000-audit','decisions-numeric-audit','decision-preserved-organic','decision-preserved-radial','decision-preserved-analytical','decision-pages-navigation']:
    report=json.loads((reviews/(name+'.json')).read_text(encoding='utf-8'))
    local[name]={k:v for k,v in report.items() if k in {'ok','nodes','decisions','grid','pixelChecks','errors','seconds'}}
    if 'checks' in report:local[name]['checkCount']=len(report['checks'])
final=groups['v2'];payloads=sorted({r['payloadSha256'] for r in collected if r['cohort']=='v2'})
passed=final['contract']['passes']==1 and final['boundary']['passes']==1 and all(final[c]['runs']==3 and final[c]['passes']>=2 for c in ['naturalistic','generalization']) and len(payloads)==1 and routing['passed'] and all(r['ok'] for r in local.values()) and not any(r.get('classification')=='unclassified' for r in collected)
summary={'date':'2026-09-25','passed':passed,'cohorts':groups,'finalPayloads':payloads,'routing':routing,'local':local,'runs':collected}
(root/'evaluations/hierarchy-lens/decisions-20260925.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in {'runs','routing'}}))
raise SystemExit(0 if passed else 1)

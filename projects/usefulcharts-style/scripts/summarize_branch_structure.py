#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Retain chapter rejections and every isolated forward result without selection."""

import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'projects/usefulcharts-style/artifacts/reviews/institution-chapters-v30'


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def main():
    runs=[]
    for name in [f'usefulcharts-v30-branches-{n}-20260912' for n in (1,2,3)]+['usefulcharts-v30-contract-spark-20260912']:
        folder=ROOT/'evaluations/runs'/name;manifest=load(folder/'run-manifest.json');result=load(folder/'evaluation-result.json')
        events=load(folder/'event-check.json');failed=[]
        for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines():
            event=json.loads(line)
            if event.get('type')=='tool_execution_end' and event.get('isError'):
                failed.append(dict(id=event['toolCallId'],message='\n'.join(c.get('text','') for c in event.get('result',{}).get('content',[]) if c.get('type')=='text')))
        item=dict(id=name,model=manifest['pi']['model'],payload=manifest['skill'],prompt=manifest['prompt'],
            strict_pass=result['passed'],duration_seconds=result['durationSeconds'],expected_outputs=manifest['expectedOutputs'],
            event_findings=events['findings'],tool_errors=failed,integrity=load(folder/'skill-integrity-check.json'),
            event_check='evaluations/runs/'+name+'/event-check.json')
        if (folder/'independent-artifact.json').exists():item['artifact_contract']=load(folder/'independent-artifact.json')
        else:
            browser=load(folder/'workspace/result/browser.json')
            expected=json.loads(re.search(r'```json\s*(.*?)\s*```',(folder/'prompt.md').read_text(encoding='utf-8'),re.S).group(1))
            exact_source=expected==load(folder/'workspace/draft.json')
            item['artifact_contract']=dict(status='pass' if exact_source and browser['status']=='pass' and not browser.get('composition_warnings') else 'fail',
                exact_prompt_source=exact_source,scope='Exact prompt JSON comparison plus independent evaluator browser replay.')
        if (folder/'evaluator-browser.json').exists():
            browser=load(folder/'evaluator-browser.json');item['evaluator_browser']=dict(status=browser['status'],findings=browser['findings'],warnings=browser.get('composition_warnings',[]))
        runs.append(item)
    attempts=[]
    for name in ('edited','chapters','expanded','chapters-greedy','expanded-greedy','chapters-causal','expanded-causal',
                 'chapters-early','expanded-early','chapters-relaxed','expanded-relaxed','chapters-relaxed-feasible','expanded-relaxed-feasible'):
        folder=ART/name;item=dict(id=name)
        if (folder/'prototype.json').exists():item.update({k:v for k,v in load(folder/'prototype.json').items() if k!='layout'})
        else:item.update(status='fail',error='OSQP maximum iterations (OSQPException: 7); preserved driver, no accepted output.',evidence='Observed terminal output; the initial project driver did not catch this solver exception.')
        item['selected']=False;attempts.append(item)
    attempts.extend([
        dict(id='separate-runs',status='cancelled',selected=False,error='Author stopped the verified owned renderer process after prolonged routing; no finished output.',scope='No timed speedup claim; bounded per-search memoization was subsequently added.'),
        dict(id='cached-separate-runs',status='pass',selected=False,layout=load(ART/'cached-separate-runs/layout.json')),
        dict(id='chapters-routed',status='pass',selected=False,scope='Earlier influence proposal without strict unrelated-run reservation.',layout=load(ART/'chapters-routed/routing.json')['layout']),
        dict(id='final-influence',status='pass',selected=False,layout=load(ART/'final-influence/layout.json'))])
    old_review=load(ART/'chapters-relaxed-feasible/browser-shared-run-review.json')
    final_review=load(ART/'final-influence/browser.json')
    result=dict(date='2026-09-12',baseline='0be67c64c8f9ce74708b2d35fe355204004f21df',
        decision='Reject all new chapter compositions as gallery replacements. Promote routing correctness and the disclosed critique guidance only.',
        goal_status='active; visual parity is not established',prototype_attempts=attempts,forward_runs=runs,
        strict_passes=sum(r['strict_pass'] for r in runs),strict_total=len(runs),
        final_artifact_contracts_pass=sum(r['artifact_contract']['status']=='pass' for r in runs),
        model_exception='GPT-5.5 for three image-dependent naturalistic cases; default Spark exact command control.',
        case_scope='59 records and 65 edges selected from disclosed synthetic development material, with 15 supplied visible notes. Not blind, independent-subject, validation or holdout evidence.',
        full_comparison=load(ART/'comparison-final/comparison.json'),
        visible_unrelated_pairs_before=len(old_review['composition_warnings']),visible_unrelated_pairs_after=len(final_review['composition_warnings']),
        route_metrics_before=load(ART/'routes.json')['candidates'][0],route_metrics_after=load(ART/'final-routes.json')['candidates'][0],
        browser_controls=load(ART/'shared-run-controls/summary.json'),
        unit_tests=dict(total=151,passed=151,composition_tests=5,existing_suites=146),
        remaining_gaps=['Persistent large regional structures in the full mural.',
            'The candidate prints only 33 of 133 original research notes and still adds route complexity; it does not prove equal-information compaction.',
            'All three isolated 59-record posters retain large quiet upper fields, long repeated steps and a displaced late optical chapter.',
            'Generic small illustration panels and narrow typography variety remain visibly unlike the denser official reference.',
            'Run 2 still needed repairs after invalid structural side ports and stale absolute routes in a packed layout.'])
    for key in ('route_metrics_before','route_metrics_after'):
        result[key]={k:v for k,v in result[key].items() if k not in ('edges','longest','overlaps')}
    output=ROOT/'evaluations/usefulcharts-style/branch-structure-summary-20260912.json'
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(summary=str(output),attempts=len(attempts),strict_passes=result['strict_passes'],strict_total=len(runs),final_contracts=result['final_artifact_contracts_pass'],selected_compositions=0,
        runtime_payloads=sorted({r['payload']['payloadSha256'] for r in runs}))))


if __name__=='__main__':main()

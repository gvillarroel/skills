#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Join all retained polish attempts without substituting successes across bundles."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    root=Path.cwd()
    evidence=root/'evaluations/diagram-composition'
    manual=json.loads((evidence/'polish-manual-reviews-20260928.json').read_text())['reviews']
    records=[]
    for run in sorted((root/'evaluations/runs').glob('diagram-polish-20260928-*-*-*')):
        result_path=run/'evaluation-result.json'
        if not result_path.is_file():continue
        suffix=run.name.removeprefix('diagram-polish-20260928-')
        candidate,case,number=suffix.split('-')
        result=json.loads(result_path.read_text())
        manifest=json.loads((run/'run-manifest.json').read_text())
        artifact_path=evidence/f'polish-{suffix}-artifact.json'
        artifact=json.loads(artifact_path.read_text()) if artifact_path.is_file() else {}
        review=manual.get(suffix,{})
        records.append({'runId':run.name,'candidate':candidate,'case':case,'number':int(number),
                        'runtimePassed':result['passed'],'artifactPassed':artifact.get('ok') is True,
                        'manualPassed':review.get('passed') is True,'manualNotes':review.get('notes'),
                        'timedOut':result.get('timedOut',False),'durationSeconds':result.get('durationSeconds'),
                        'payloadSha256':manifest['skill']['payloadSha256'],'sourceSha256':artifact.get('sourceSha256'),
                        'jointPassed':result['passed'] and artifact.get('ok') is True and review.get('passed') is True})
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('pi_harness',root/'scripts/run-pi-skill-eval.py')
    harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
    current=harness.snapshot_digest(harness.snapshot_tree(root/'skills/diagram-composition'))
    selected=[r for r in records if r['candidate']==args.candidate]
    gates={}
    for case,count,minimum in (('contract',1,1),('naturalistic',3,2),('boundary',1,1),('generalization',3,2)):
        items=[r for r in selected if r['case']==case]
        gates[case]={'runs':len(items),'strictPasses':sum(r['runtimePassed'] for r in items),
                     'artifactPasses':sum(r['artifactPassed'] for r in items),'manualPasses':sum(r['manualPassed'] for r in items),
                     'jointPasses':sum(r['jointPassed'] for r in items),
                     'passed':len(items)==count and sum(r['jointPassed'] for r in items)>=minimum}
    frozen=bool(selected) and all(r['payloadSha256']==current for r in selected)
    handoff=json.loads((root/'projects/diagram-composition/artifacts/reviews/workspace-audit.json').read_text())
    output={'candidate':args.candidate,'payloadSha256':current,'frozenPayloadMatches':frozen,'gates':gates,
            'handoffArtifactPassed':handoff.get('ok') is True,
            'ok':frozen and all(g['passed'] for g in gates.values()) and handoff.get('ok') is True,
            'attemptCount':len(records),'attempts':records}
    args.output.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k!='attempts'}))
    return 0 if output['ok'] else 1


if __name__=='__main__':raise SystemExit(main())

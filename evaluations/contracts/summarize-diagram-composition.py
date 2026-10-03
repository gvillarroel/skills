#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect compact release evidence without copying model reasoning or raw traces."""

import argparse
import json
import subprocess
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    records = []
    for run in sorted((root / 'evaluations' / 'runs').glob('diagram-composition-20260928-*')):
        if not run.is_dir() or not (run / 'evaluation-result.json').is_file(): continue
        def read(name):
            path = run / name
            return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else None
        result, manifest, events = read('evaluation-result.json'), read('run-manifest.json'), read('event-check.json')
        summary_cmd = ['uv', 'run', '--script', str(root / 'scripts' / 'summarize-pi-json-events.py'),
            str(run / 'events.jsonl'), '--output', str(run / 'trace-summary.json'),
            '--require-model', manifest['pi']['model'].split('/')[-1], '--fail-on-invalid-json', '--fail-on-tool-error']
        summarizer = subprocess.run(summary_cmd, cwd=root, capture_output=True, text=True, encoding='utf-8', errors='replace')
        trace = read('trace-summary.json')
        case = next((c for c in ['contract','naturalistic','generalization','transfer','boundary'] if f'-{c}' in run.name), 'unknown')
        independent_path = run / 'independent-check.json'
        if (run / 'workspace' / 'out' / 'figure.svg').is_file():
            subprocess.run(['uv','run','--script',str(root/'evaluations/contracts/check-diagram-composition.py'),str(run),
                '--case',case,'--output',str(independent_path)], cwd=root, capture_output=True)
        records.append({'runId':run.name,'case':case,'model':manifest['pi']['model'],
            'piCommand':manifest['command'],'prompt':manifest['prompt'],
            'expectedOutputs':manifest.get('expectedOutputs',[]),
            'expectedJsonFields':manifest.get('expectedJsonFields',[]),
            'payload':manifest['skill'],'strictPassed':result['passed'],'durationSeconds':result.get('durationSeconds'),
            'gates':result.get('gates'),'traceSummaryPassed':summarizer.returncode == 0,
            'eventFindings':events.get('findings',[]) if events else [],
            'readPaths':[r.get('path') for r in (trace or {}).get('readPaths',[])],
            'independentArtifactCheck':read('independent-check.json'),'evaluatorBrowserAudit':read('evaluator-audit.json'),
            'manualArtifactReview':read('manual-review.json')})
    summary={'date':'2026-09-28','skill':'diagram-composition','runs':records,
             'manualReviewRecord':'validation-20260928.md','scope':'Completed runs only; retained failures are included.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'records':len(records),'strictPasses':sum(r['strictPassed'] for r in records),'output':str(args.output)}))


if __name__=='__main__':
    main()

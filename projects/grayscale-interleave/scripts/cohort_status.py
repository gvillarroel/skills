#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Summarize complete retained cohorts without cherry-picking repetitions."""
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--revision', choices=('r1','r2','r3','r4'))
parser.add_argument('--live', action='store_true', help='Report raw strict completions without claiming native acceptance.')
args = parser.parse_args()
out = ROOT / 'projects/grayscale-interleave/artifacts/reviews/forward-native'
for revision in ((args.revision,) if args.revision else ('r1','r2','r3','r4')):
    if args.live:
        rows = []
        for folder in (ROOT/'evaluations/runs').glob(f'gray-20261005-{revision}-*'):
            result = folder/'evaluation-result.json'
            if result.exists():
                manifest = json.loads((folder/'run-manifest.json').read_bytes())
                data = json.loads(result.read_bytes())
                rows.append({'skill': manifest['skill']['name'], 'family': 'naturalistic' if 'naturalistic' in folder.name else 'contract', 'passed': data['passed']})
        print(json.dumps({'revision': revision, 'scope': 'Raw strict completions; native acceptance is separate.',
                          'completedRuns': len(rows), 'strictPassed': sum(row['passed'] for row in rows),
                          'completedContracts': sum(row['family']=='contract' for row in rows),
                          'completedNaturalRuns': sum(row['family']=='naturalistic' for row in rows)}))
        continue
    path = out / f'{revision}-final-results.json'
    if not path.exists():
        path = out / f'{revision}-results.json'
    if not path.exists():
        continue
    rows = json.loads(path.read_bytes())
    summary = {}
    for row in rows:
        entry = summary.setdefault(row['skill'], {'contract':None,'naturalCount':0,'naturalPassed':0})
        if row['family'] == 'contract':
            entry['contract'] = row['passed']
        else:
            entry['naturalCount'] += 1
            entry['naturalPassed'] += row['passed']
    complete = {skill:row for skill,row in summary.items() if row['naturalCount']==3}
    failed = [skill for skill,row in complete.items() if row['naturalPassed']<2]
    accepted = [skill for skill,row in complete.items() if row['naturalPassed']>=2]
    print(json.dumps({'revision':revision,'observedRuns':len(rows),'completeNaturalCohorts':len(complete),
                      'acceptedNaturalOwners':accepted,'failedNaturalOwners':failed},indent=2))

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Read compact native development progress, without opening private results."""
from pathlib import Path
import json,statistics
REPO=Path(__file__).resolve().parents[3]
STUDY=REPO/'evaluations/runs/svg-brief-design-20260925-r2'
jobs=[]
for resultfile in sorted((STUDY/'search/development').glob('generation-*/harbor-jobs/*/result.json')):
    result=json.loads(resultfile.read_text());stats=result['stats']
    row={'job':resultfile.parent.name,'completed':stats['n_completed_trials'],'planned':result['n_total_trials'],'errors':stats['n_errored_trials'],'finished':bool(result.get('finished_at'))}
    if row['finished']:
        trials=[json.loads(p.read_text()) for p in resultfile.parent.glob('*/result.json')]
        values=[t['verifier_result']['rewards']['visual_similarity'] for t in trials if t.get('verifier_result') and not t.get('exception_info')]
        row['mean_visual']=statistics.mean(values) if len(values)==row['planned'] else None
        row['cases']=[{'task':t['task_name'].split('--')[0],'visual':(t.get('verifier_result') or {}).get('rewards',{}).get('visual_similarity'),'style':(t.get('verifier_result') or {}).get('rewards',{}).get('style_similarity'),'error':(t.get('exception_info') or {}).get('exception_type')} for t in trials]
    jobs.append(row)
print(json.dumps({'jobs':jobs,'archives':[str(p.relative_to(STUDY)) for p in (STUDY/'search/development').glob('generation-*/pareto-archive.json')]},indent=2))

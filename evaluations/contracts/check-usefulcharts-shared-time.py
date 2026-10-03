#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently grade fixed x, heading clearance, track reuse and owner identity."""
from pathlib import Path
import argparse
import itertools
import json
import re


def grade(run):
    forward='forward' in run.name
    expected=([('swift-first','swift','couriers',100,250,80),('swift-return','swift','couriers',400,530,80),('kestrel','kestrel','couriers',190,330,90),('atlas','atlas','freighters',580,740,85),('beacon','beacon','freighters',765,970,85)] if forward else [('alpha','alpha','survey',100,240,80),('beta','beta','survey',180,320,80),('alpha-return','alpha','survey',380,500,80),('gamma','gamma','cargo',550,750,80)])
    root=run/'workspace';out=json.loads((root/'deliverables/layout.json').read_text())
    boxes={b['id']:b for b in out['layout']['boxes']};groups={g['id']:g for g in out['layout']['groups']}
    source={r['id']:r for r in out['source']['records']}
    assert len(boxes)==len(out['layout']['boxes'])==len(expected)
    assert set(boxes)==set(source)=={r[0] for r in expected}
    for id,owner,family,left,right,height in expected:
        b=boxes[id];g=groups[family]
        assert (b['group'],b['x'],b['w'],b['h'])==(family,left,right-left,height)
        assert source[id]['owner']==owner
        assert b['y']>=g['y']+40 and b['y']+b['h']<=g['y']+g['h']
        assert g['x']<=b['x'] and b['x']+b['w']<=g['x']+g['w']
        assert g['w']>=160 or (not forward and family=='cargo' and g['w']>=150)
    for a,b in itertools.combinations(boxes.values(),2):
        assert a['x']+a['w']+12<=b['x'] or b['x']+b['w']+12<=a['x'] or a['y']+a['h']+10<=b['y'] or b['y']+b['h']+10<=a['y']
    for a,b in itertools.combinations(groups.values(),2):
        assert a['x']+a['w']+12<=b['x'] or b['x']+b['w']+12<=a['x'] or a['y']+a['h']+24<=b['y'] or b['y']+b['h']+24<=a['y']
    a,c=('swift-first','swift-return') if forward else ('alpha','alpha-return')
    assert boxes[a]['y']==boxes[c]['y'],'Nonoverlapping states did not reuse a track'
    assert len({g['y'] for g in groups.values()})==1,'Disjoint family pockets failed to share a band'
    return dict(fragments=len(boxes),owners=len({r['owner'] for r in source.values()}),groups=len(groups))


def main():
    p=argparse.ArgumentParser();p.add_argument('runs',nargs='+',type=Path);p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    rows=[]
    for run in args.runs:
        ev=json.loads((run/'evaluation-result.json').read_text());events=json.loads((run/'event-check.json').read_text())
        reads=[c['path'] for c in events['calls'] if c.get('tool')=='read' and c.get('path')]
        row=dict(run=run.name,strict=ev['passed'],reads=reads,reference_read=any(r.endswith('/references/shared-time-rows.md') for r in reads),helper_executed=any('scripts/pack_shared_rows.py ' in (c.get('command') or '') for c in events['calls']),event_findings=events['findings'])
        try:row.update(grade(run),artifact_pass=True)
        except (AssertionError,KeyError,FileNotFoundError,ValueError) as e:row.update(artifact_pass=False,error=str(e))
        row['outside_workspace_writes']=[c['command'] for c in events['calls'] if re.search(r'>\s*/tmp/',c.get('command') or '')]
        row['complete_measured_layout_pass']=row['strict'] and row['artifact_pass'] and row['helper_executed'] and not row['outside_workspace_writes']
        rows.append(row)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k not in {'reads','event_findings'}} for r in rows]))


if __name__=='__main__':main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check a synthetic handoff while a sibling track remains active."""
import argparse
import json
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('workspace',type=Path)
    args=parser.parse_args();root=args.workspace
    output=json.loads((root/'deliverables/layout.json').read_text())
    expected={
        'short':('survey-hull',60,200,80,'survey'),
        'long':('long-hull',80,900,70,'survey'),
        'return':('survey-hull',960,1150,60,'survey'),
        'beta':('freighter',230,440,90,'freight'),
        'gamma':('science-one',470,660,80,'science'),
        'delta':('science-two',500,820,95,'science')}
    source=output['source'];layout=output['layout'];boxes={b['id']:b for b in layout['boxes']}
    assert set(boxes)==set(expected)
    assert source['reuse_tracks'] is True and source['labels_in_footprints'] is True
    assert {k:source[k] for k in ['width','top','gap','track_gap','row_gap']}==dict(width=1200,top=40,gap=12,track_gap=16,row_gap=20)
    assert len(source['records'])==6
    membership={sid:g['id'] for g in source['groups'] for sid in g['members']}
    assert len(membership)==6
    for r in source['records']:
        owner,x0,x1,h,group=expected[r['id']];b=boxes[r['id']]
        assert (r['owner'],r['x0'],r['x1'],r['height'],membership[r['id']])==(owner,x0,x1,h,group)
        assert (b['x'],b['w'],b['h'],b['group'])==(x0,x1-x0,h,group)
        assert b['y']>=40
    assert len({boxes[k]['row'] for k in ['short','beta','gamma']})==1
    assert boxes['long']['row']!=boxes['beta']['row']
    assert layout['row_count']==3 and layout['cross_group_rows']>=1
    for i,a in enumerate(layout['boxes']):
        for b in layout['boxes'][i+1:]:
            assert (a['x']+a['w']+12<=b['x'] or b['x']+b['w']+12<=a['x'] or
                    a['y']+a['h']+16<=b['y'] or b['y']+b['h']+16<=a['y'])
    review=(root/'deliverables/review.md').read_text()
    assert len(review.strip())>100
    print(json.dumps(dict(status='pass',fragments=6,owners=5,tracks=3,handoff=['short','beta','gamma'],review_requires_manual_inspection=True)))

if __name__=='__main__':main()

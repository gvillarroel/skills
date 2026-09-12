#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Develop a chronology composition without changing its supplied history."""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path



def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[3]
    sys.path.insert(0,str(root/'skills/usefulcharts-style/scripts'))
    from pack_timeline_events import pack_events
    baseline=json.loads(subprocess.check_output(['git','show','47927dfb:skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json'],cwd=root))
    data=copy.deepcopy(baseline)
    major={'p0-river','p1-silver','p2-maritime','p3-voyage','p4-birch'}
    for period in data['periods']:
        old=period['bar_width'];width=max(20,min(50,old*.58))
        if period['id'] in major:width=50
        period.update(offset=period['offset']+(old-width)/2,bar_width=width,
            size=18 if period['id'] in major else 12 if old>=55 else 11)
        if period['id'] in ('p1-cairn','p1-union'):period['offset']-=50
    added={
        'event-2-6':('illustration-astrolabe-observation',95,65.43),
        'event-1-7':('illustration-clock-escapement',67,86.71),
        'event-3-6':('illustration-sextant-1904',65,62.32),
    }
    for event in data['events']:
        if event['id'] in added:
            event['icon'],event['art_width'],event['art_height']=added[event['id']]
        landmark=event['size']>12
        event.update(size=14.5 if landmark else 12.2,detail_size=11 if landmark else 10.7)
    data,placement=pack_events(data)
    decisions=placement['decisions']
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    (args.output/'placement-decisions.json').write_text(json.dumps(decisions,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(periods=len(data['periods']),events=len(data['events']),illustrated_events=sum(bool(e.get('icon')) for e in data['events']),output=str(args.output/'source.json'))))


if __name__=='__main__':main()

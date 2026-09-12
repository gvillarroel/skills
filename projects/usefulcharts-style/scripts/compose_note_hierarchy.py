#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Compare compact paragraph notes with distinct landmark headings."""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from pack_timeline_events import pack_events
from editorial_poster import EditorialPoster
from timeline_geometry import lane_geometry


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--phase',choices=('a','b','c','d','e'),default='a')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    path='skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json'
    baseline=json.loads(subprocess.check_output(['git','show','5b2d3674:'+path],cwd=ROOT))
    old_lanes=lane_geometry(baseline['lanes'],baseline['width']);outcomes=[]
    profiles=[('moderate-page',1680,2300)] if args.phase=='e' else [('original-page',1680,2400),('shorter-page',1680,2200),('balanced-page',1560,2200),('compact-page',1560,2100)]
    for name,width,height in profiles:
        folder=args.output/name;folder.mkdir();data=copy.deepcopy(baseline);data.update(width=width,height=height)
        lanes=lane_geometry(data['lanes'],width)
        for period in data['periods']:
            period['offset']=(period['offset']+period['bar_width']/2)/old_lanes[period['lane']][1]*lanes[period['lane']][1]-period['bar_width']/2
            if args.phase in ('c','d','e') and period['id'] in ('p3-voyage','p3-assembly'):period['offset']-=40
        for event in data['events']:
            if (event['size']<14 and not event.get('icon')) or (args.phase!='a' and event.get('icon')):event['text_layout']='paragraph'
            if args.phase!='a' and event.get('icon'):event['art_position']='auto'
            if args.phase in ('d','e') and event['id']=='event-3-6':event['art_position']='below'
            event['offset']=event['offset']/old_lanes[event['lane']][1]*lanes[event['lane']][1]
        (folder/'draft.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        try:
            data,placements=pack_events(data,max_width=200);svg,layout=EditorialPoster(data).render()
            (folder/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
            (folder/'poster.svg').write_text(svg,encoding='utf-8')
            outcome=dict(id=name,status='rendered',canvas=[width,height],paragraphs=sum(e.get('text_layout')=='paragraph' for e in data['events']),
                art_positions={e['id']:e.get('art_position','below') for e in data['events'] if e.get('icon')},composition_warnings=placements['composition_warnings'])
            (folder/'placements.json').write_text(json.dumps(placements,indent=2)+'\n',encoding='utf-8')
            (folder/'layout.json').write_text(json.dumps(layout,indent=2)+'\n',encoding='utf-8')
        except ValueError as error:outcome=dict(id=name,status='needs-layout',message=str(error))
        outcomes.append(outcome)
    (args.output/'outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n',encoding='utf-8');print(json.dumps(outcomes))


if __name__=='__main__':main()

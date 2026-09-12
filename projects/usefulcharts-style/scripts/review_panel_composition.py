#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare source facts, colored areas and routing against the published mural."""

import argparse
import json
import statistics
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}
PATH='skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry'


def facts(data):
    records=[]
    for node in data['nodes']:
        note=node.get('detail','')
        if node.get('detail_position')!='outside':note=note.removeprefix(str(node['founded'])).removeprefix(' · ')
        records.append((node['id'],node['label'],node['founded'],node['group'],note))
    return sorted(records),sorted((e['id'],e['source'],e['target'],e['kind']) for e in data['edges'])


def metrics(svg):
    root=ET.fromstring(svg);meta=json.loads(root.find('.//s:metadata[@id="chart-data"]',NS).text)
    areas=[]
    for node in root.findall('.//s:g[@data-node-id]',NS):
        if node.get('data-treatment') in ('plain','pill'):continue
        panel=node.find('s:rect[@data-name-panel]',NS)
        if panel is None:panel=node.find('s:rect[@data-node-box]',NS)
        areas.append(float(panel.get('width'))*float(panel.get('height')))
    lengths={e['id']:sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(e['points'],e['points'][1:])) for e in meta['routes']}
    return dict(colored_panel_area=sum(areas),median_colored_panel_area=statistics.median(areas),route_lengths=lengths)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='a377b870')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();repo=Path(__file__).resolve().parents[3]
    def prior(ext):return subprocess.check_output(['git','show',f'{args.before}:{PATH}.{ext}'],cwd=repo)
    before=json.loads(prior('json'));after=json.loads((repo/(PATH+'.json')).read_text(encoding='utf-8'))
    old=metrics(prior('svg'));new=metrics((repo/(PATH+'.svg')).read_bytes())
    changes=sorted((dict(id=k,before=v,after=new['route_lengths'][k],delta=new['route_lengths'][k]-v) for k,v in old['route_lengths'].items()),key=lambda e:e['delta'],reverse=True)
    retained=facts(before)==facts(after)
    result=dict(status='pass' if retained else 'fail',before_revision=args.before,exact_source_facts_preserved=retained,nodes=len(after['nodes']),edges=len(after['edges']),
        colored_panel_area_before=old['colored_panel_area'],colored_panel_area_after=new['colored_panel_area'],
        colored_panel_area_change_percent=100*(new['colored_panel_area']/old['colored_panel_area']-1),largest_route_increases=changes[:12],
        limitation='Source preservation and panel-area measurements do not establish visual parity. Route increases require inspection of their actual paths.')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));raise SystemExit(not retained)


if __name__=='__main__':main()

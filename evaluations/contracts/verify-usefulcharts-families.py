#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check exact small-family and parallel-transport task data."""

import argparse
import json
import re
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}
PEOPLE={
    'Alden':(1700,1767,'neutral'),'Mara':(1704,1776,'neutral'),'Ivo':(1733,1754,'neutral'),
    'Rowan':(1725,1790,'alder'),'Elise':(1727,1803,'alder'),'Cedric':(1753,1819,'alder'),
    'Nella':(1758,1831,'alder'),'Felix':(1754,1820,'alder'),'Anya':(1788,1851,'alder'),'Simon':(1787,1859,'alder'),
    'Vera':(1730,1801,'vey'),'Tomas':(1729,1795,'vey'),'Ines':(1757,1828,'vey'),'Oren':(1759,1790,'vey'),
    'Leda':(1783,1857,'vey'),'Remy':(1785,1844,'vey'),'June':(1811,1877,'vey'),'Leo':(1814,1882,'vey'),'Iris':(1813,1899,'vey')}
UNIONS=[(('Alden','Mara'),('Rowan','Vera','Ivo')),(('Rowan','Elise'),('Cedric','Nella')),
        (('Vera','Tomas'),('Ines','Oren')),(('Cedric','Ines'),('Leda','Remy')),
        (('Nella','Felix'),('Anya','Simon')),(('Leda','Simon'),('June','Leo','Iris'))]
PHASES={
    'Steam Era':(1900,1925,'rail'),'Electric Era':(1925,1950,'rail'),'Metro Era':(1950,1975,'rail'),
    'Regional Era':(1975,2000,'rail'),'Integrated Rail':(2000,2020,'rail'),
    'Ferry Guild':(1900,1920,'river'),'Motor Ferries':(1920,1945,'river'),'River Authority':(1945,1970,'river'),
    'Fast Ferries':(1970,1995,'river'),'Water Transit':(1995,2020,'river'),
    'Coach Routes':(1900,1930,'road'),'Motor Buses':(1930,1955,'road'),'City Transit':(1955,1980,'road'),
    'Busways':(1980,2000,'road'),'Electric Buses':(2000,2020,'road')}


def supported_preview_reads(run,preview):
    calls={};seen=[]
    for line in (run/'events.jsonl').read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event.get('type')=='tool_execution_start':calls[event['toolCallId']]=event.get('args',{}).get('path','').replace('\\','/')
        if event.get('type')=='tool_execution_end' and calls.get(event.get('toolCallId'),'').endswith(preview):
            content=event.get('result',{}).get('content',[])
            if any(c.get('type')=='image' for c in content) and not any('does not support images' in c.get('text','') for c in content):seen.append(event['toolCallId'])
    return len(seen)


def inspect(run,case):
    folder=run/'workspace'/('result' if case=='cohorts' else 'museum')
    names=('source.json','poster.svg','poster.png') if case=='cohorts' else ('data.json','timeline.svg','preview.png')
    data=json.loads((folder/names[0]).read_text(encoding='utf-8'))
    browser=json.loads((folder/'browser.json').read_text(encoding='utf-8'))
    root=ET.parse(folder/names[1]).getroot();findings=[]
    expected=PEOPLE if case=='cohorts' else PHASES
    records=data.get('nodes',[]) if case=='cohorts' else data.get('periods',[])
    by_name={n['label']:n for n in records};by_id={n['id']:n['label'] for n in records}
    if set(by_name)!=set(expected) or len(records)!=len(expected):findings.append('The exact named-record inventory differs from the task.')
    anchors={}
    for name,(a,b,category) in expected.items():
        if name not in by_name:continue
        node=by_name[name];group=node['group'];anchors.setdefault(category,group)
        if group!=anchors[category]:findings.append(f'Source category changed for {name}.')
        element=root.find(f'.//s:g[@data-node-id="{node["id"]}"]',NS)
        if element is None:
            findings.append(f'Visible record absent: {name}.');continue
        if element.get('data-group')!=group:findings.append(f'Visible category differs from source: {name}.')
        text=' '.join(t.text or '' for t in element.findall('s:text',NS))
        if any(not re.search(rf'\b{year}\b',text) for year in (a,b)):findings.append(f'Visible endpoint dates missing for {name}.')
        if case=='transport' and (node['start'],node['end'])!=(a,b):findings.append(f'Time interval changed for {name}.')
    if len(set(anchors.values()))!=3 or len(data['groups'])!=3:findings.append('The three declared categories are not preserved distinctly.')
    if case=='cohorts':
        def canonical(partners,children):return (tuple(sorted(partners)),tuple(sorted(children)))
        expected_unions=sorted(canonical(*u) for u in UNIONS)
        actual_unions=sorted(canonical([by_id.get(p,p) for p in u['partners']],[by_id.get(c,c) for c in u.get('children',[])]) for u in data.get('unions',[]))
        if expected_unions!=actual_unions or data.get('edges'):findings.append('The exact partnerships and their children differ from the task.')
        if 'schematic' not in ' '.join(root.itertext()).lower():findings.append('The schematic spacing note is absent.')
    else:
        if data.get('events') or data.get('transitions') or data.get('edges') or data.get('unions'):findings.append('Unprovided events or relationships were added to the phase comparison.')
        if len(data['lanes'])!=3 or data['time']['start']!=1900 or data['time']['end']!=2020:findings.append('The shared time range or three-lane structure changed.')
        lane_for={}
        y0,y1=browser['metadata']['time_y'];boxes={n['id']:n['box'] for n in browser['nodes']}
        for name,(a,b,network) in PHASES.items():
            if name not in by_name:continue
            node=by_name[name];lane_for.setdefault(network,node['lane'])
            if node['lane']!=lane_for[network]:findings.append(f'Network lane changed for {name}.')
            box=boxes[node['id']]
            if abs(box['y']-(y0+(a-1900)/120*(y1-y0)))>.1 or abs(box['h']-(b-a)/120*(y1-y0))>.1:findings.append(f'Drawn numeric interval differs for {name}.')
    visible=' '.join(t.text or '' for t in root.findall('.//s:text',NS)).lower()
    if 'synthetic' not in visible and 'fictional' not in visible:findings.append('Invented data is not identified on the poster.')
    if browser['status']!='pass':findings.append('Source-backed browser geometry audit fails.')
    preview=folder.relative_to(run/'workspace').as_posix()+'/'+names[2]
    reads=supported_preview_reads(run,preview)
    if not reads:findings.append('No supported final-preview image read appears in the trace.')
    fonts=[t['font'] for t in browser['texts'] if t['owner']!='page']
    return dict(run=run.name,case=case,status='fail' if findings else 'pass',findings=findings,
        canvas=browser['canvas'],record_count=len(records),preview_reads=reads,median_record_font=statistics.median(fonts),
        limitation='Data and geometry checks do not certify composition or visual parity; inspect the actual image separately.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('--case',choices=['cohorts','transport'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=inspect(args.run,args.case)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));raise SystemExit(result['status']!='pass')


if __name__=='__main__':main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check exact regional histories and supported image inspection."""

import argparse
from collections import Counter
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def prompt_contract(path):
    periods=[];events=[];edges=[]
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('| '):
            values=[p.strip() for p in line.split('|')[1:-1]]
            if len(values)!=5 or values[0] in ('ID','---'):continue
            if values[0].startswith('e'):
                nid,region,year,label,note=values;events.append(dict(id=nid,region=region,year=int(year),label=label,detail=note))
            else:
                nid,region,label,start,end=values;periods.append(dict(id=nid,region=region,label=label,start=int(start),end=int(end)))
        for label,kind in [('Divisions','division'),('Unions','union'),('Succession','succession')]:
            if line.startswith('- '+label+':'):
                edges.extend((source,target,kind) for source,target in re.findall(r'`([chp][1-4]) -> ([chp][1-4])`',line))
    assert len(periods)==12 and len(events)==18 and len(edges)==11
    assert len({p['id'] for p in periods})==12 and len({e['id'] for e in events})==18
    return periods,events,edges


def inspect(run):
    expected,notes,links=prompt_contract(run/'prompt.md');folder=run/'workspace/result'
    data=json.loads((folder/'source.json').read_text(encoding='utf-8'));svg=ET.parse(folder/'poster.svg').getroot()
    audit=json.loads((folder/'browser.json').read_text(encoding='utf-8'));findings=[]
    periods={p['id']:p for p in data['periods']};events={e['id']:e for e in data['events']}
    visible={n.get('data-node-id'):n for n in svg.findall('.//s:g[@data-node-id]',NS)}
    visible_events={n.get('data-event-id'):n for n in svg.findall('.//s:g[@data-event-id]',NS)}
    if len(data['periods'])!=12 or set(periods)!={p['id'] for p in expected} or set(visible)!=set(periods):findings.append('Period inventory changed.')
    if len(data['events'])!=18 or set(events)!={e['id'] for e in notes} or set(visible_events)!=set(events):findings.append('Event inventory changed.')
    regions={};lane_regions={}
    for row in expected:
        item=periods.get(row['id'])
        if item is None:continue
        for field in ('label','start','end'):
            if item[field]!=row[field]:findings.append(f'Changed period {field}: {row["id"]}')
        text=' '.join(' '.join(t.itertext()) for t in visible[row['id']].findall('.//s:text',NS))
        if row['label'] not in ' '.join(text.split()):findings.append(f'Missing visible period label: {row["id"]}')
        regions.setdefault(row['region'],set()).add(item['group']);lane_regions.setdefault(row['region'],set()).add(item['lane'])
    for mapping in (regions,lane_regions):
        if any(len(v)!=1 for v in mapping.values()) or len(set().union(*mapping.values()))!=3:findings.append('The three regional categories or lanes are inconsistent.')
    for row in notes:
        item=events.get(row['id']);el=visible_events.get(row['id'])
        if item is None or el is None:continue
        text=' '.join(' '.join(t.itertext()) for t in el.findall('.//s:text',NS));text=' '.join(text.split())
        if item['year']!=row['year'] or el.get('data-year')!=str(row['year']):findings.append(f'Changed event date: {row["id"]}')
        if any(row[field] not in text for field in ('label','detail')):findings.append(f'Missing event content: {row["id"]}')
        if item['lane'] not in lane_regions[row['region']]:findings.append(f'Changed event region: {row["id"]}')
    actual=Counter((e['source'],e['target'],e['kind']) for e in data.get('transitions',[]))
    if actual!=Counter(links):findings.append('Typed transitions changed.')
    svg_edges=Counter((e.get('data-source'),e.get('data-target'),e.get('data-kind')) for e in svg.findall('.//s:path[@data-edge-id]',NS))
    if svg_edges!=actual:findings.append('Visible transitions differ from the source.')
    clock=visible_events.get('ec2')
    if clock is None or not any(e.get('data-artwork') for e in clock.iter()):findings.append('The clockmaking illustration is missing.')
    if audit.get('status')!='pass' or audit.get('findings'):findings.append('The browser audit fails.')
    poster_text=' '.join(' '.join(t.itertext()) for t in svg.findall('.//s:text',NS)).lower()
    if not any(word in poster_text for word in ('fictional','synthetic','invented')):findings.append('The fictional-source note is missing.')
    paths={};images=[]
    for line in (run/'events.jsonl').read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event.get('type')=='tool_execution_start':paths[event['toolCallId']]=event.get('args',{}).get('path','').replace('\\','/')
        if event.get('type')!='tool_execution_end' or not paths.get(event.get('toolCallId'),'').endswith('result/poster.png'):continue
        content=event.get('result',{}).get('content',[])
        if any(c.get('type')=='image' for c in content) and not any('does not support images' in c.get('text','') for c in content):images.append(event['toolCallId'])
    if not images:findings.append('The trace lacks supported preview inspection.')
    return dict(status='fail' if findings else 'pass',periods=len(periods),events=len(events),transitions=sum(actual.values()),
        canvas=svg.get('viewBox'),supported_image_reads=len(images),findings=findings,
        limitation='Exact data and geometry do not establish visual parity; inspect the images separately.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path,nargs='?');parser.add_argument('--output',type=Path);parser.add_argument('--check-prompt',type=Path)
    args=parser.parse_args()
    if args.check_prompt:
        periods,events,edges=prompt_contract(args.check_prompt);print(json.dumps(dict(status='pass',periods=len(periods),events=len(events),transitions=len(edges))));return
    if not args.run or not args.output:parser.error('run and --output are required')
    result=inspect(args.run);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result));raise SystemExit(result['status']!='pass')


if __name__=='__main__':main()

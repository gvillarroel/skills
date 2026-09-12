#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the complete library-history source independently of the skill renderer."""

import argparse
import collections
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def records_from_prompt(prompt):
    records=[]
    for line in prompt.read_text(encoding='utf-8').splitlines():
        if not line.startswith('| '):continue
        fields=[p.strip() for p in line.split('|')[1:-1]]
        if len(fields)!=7 or fields[0] in ('ID','---'):continue
        nid,name,date,group,parents,influences,context=fields
        records.append(dict(id=nid,label=name,date=date,group=group,context=context,
            parents=[] if parents=='—' else parents.split(', '),influences=[] if influences=='—' else influences.split(', ')))
    assert len(records)==50,'The evaluation prompt must contain 50 complete records.'
    ids={r['id'] for r in records};assert len(ids)==len(records)
    for record in records:
        assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',record['id']),f'Invalid evaluation ID: {record["id"]}'
        assert set(record['parents']+record['influences'])<=ids
    return records


def inspect(run):
    records=records_from_prompt(run/'prompt.md');folder=run/'workspace/result'
    data=json.loads((folder/'source.json').read_text(encoding='utf-8'));root=ET.parse(folder/'poster.svg').getroot()
    browser=json.loads((folder/'browser.json').read_text(encoding='utf-8'))
    findings=[];nodes={n['id']:n for n in data['nodes']};categories={}
    visible={g.get('data-node-id'):g for g in root.findall('.//s:g[@data-node-id]',NS)}
    expected_ids={r['id'] for r in records}
    if set(nodes)!=expected_ids or set(visible)!=expected_ids:findings.append('The source or visible record inventory differs from the prompt.')
    for record in records:
        nid=record['id'];node=nodes.get(nid);element=visible.get(nid)
        if node is None or element is None:continue
        if node['label']!=record['label']:findings.append(f'Changed record name: {nid}')
        text=' '.join(' '.join(t.itertext()) for t in element.findall('.//s:text',NS));text=' '.join(text.split())
        for field in ('label','date','context'):
            if record[field] not in text:findings.append(f'Missing visible {field}: {nid}')
        categories.setdefault(record['group'],set()).add(node['group'])
    if any(len(v)!=1 for v in categories.values()) or len({next(iter(v)) for v in categories.values()})!=6:
        findings.append('The six source traditions are not consistently distinct.')
    expected=collections.Counter((r['id'],p,'influence' if kind=='influences' else 'branch') for r in records for kind in ('parents','influences') for p in r[kind])
    actual=collections.Counter((e['target'],e['source'],'influence' if e['kind']=='influence' else 'branch' if e['kind'] in ('branch','succession') else e['kind']) for e in data['edges'])
    if expected!=actual:findings.append('The typed relationship inventory differs from the source.')
    svg_edges=collections.Counter((e.get('data-target'),e.get('data-source'),e.get('data-kind')) for e in root.findall('.//s:path[@data-edge-id]',NS))
    if svg_edges!=collections.Counter((e['target'],e['source'],e['kind']) for e in data['edges']):findings.append('The visible relationship inventory differs from the edited source.')
    visible_text=' '.join(t.text or '' for t in root.findall('.//s:text',NS)).lower()
    if not any(word in visible_text for word in ('fictional','synthetic','invented')):findings.append('The visible synthetic-data note is missing.')
    if browser.get('status')!='pass' or browser.get('findings'):findings.append('The source-backed browser audit fails.')
    image_reads=[];paths={}
    for line in (run/'events.jsonl').read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event.get('type')=='tool_execution_start':paths[event['toolCallId']]=event.get('args',{}).get('path','').replace('\\','/')
        if event.get('type')!='tool_execution_end' or not paths.get(event.get('toolCallId'),'').endswith('result/poster.png'):continue
        content=event.get('result',{}).get('content',[])
        if any(c.get('type')=='image' for c in content) and not any('does not support images' in c.get('text','') for c in content):image_reads.append(event['toolCallId'])
    if not image_reads:findings.append('The final PNG has no supported image-reading result in the trace.')
    return dict(status='fail' if findings else 'pass',run=run.name,nodes=len(nodes),edges=sum(actual.values()),canvas=list(map(float,root.get('viewBox').split()[2:])),
        image_read_count=len(image_reads),external_content_nodes=len(root.findall('.//s:rect[@data-content-envelope]',NS)),findings=findings,
        limitation='This checks source meaning, supported preview inspection and geometry. Hierarchy and visual parity require a separate image review.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path,nargs='?');parser.add_argument('--output',type=Path);parser.add_argument('--check-prompt',type=Path)
    args=parser.parse_args()
    if args.check_prompt:
        records=records_from_prompt(args.check_prompt)
        print(json.dumps(dict(status='pass',records=len(records),relationships=sum(len(r['parents'])+len(r['influences']) for r in records))))
        return
    parser.error('run and --output are required') if not args.run or not args.output else None
    result=inspect(args.run);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result));raise SystemExit(result['status']!='pass')


if __name__=='__main__':main()

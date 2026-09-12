#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the disclosed branch-structure task without trusting the agent's review."""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def inspect(run):
    expected=json.loads(re.search(r'```json\s*(.*?)\s*```',(run/'prompt.md').read_text(encoding='utf-8'),re.S).group(1))
    folder=run/'workspace/result';data=json.loads((folder/'source.json').read_text(encoding='utf-8'))
    report=json.loads((folder/'browser.json').read_text(encoding='utf-8'));root=ET.parse(folder/'poster.svg').getroot();findings=[]
    actual={n['id']:n for n in data['nodes']}
    if set(actual)!={n['id'] for n in expected['nodes']}:findings.append('Record inventory differs.')
    for node in expected['nodes']:
        item=actual.get(node['id'],{})
        for field in ('label','founded','group','detail'):
            if item.get(field,'')!=node[field]:findings.append(f'{node["id"]}: changed {field}.')
        element=root.find(f'.//s:g[@data-node-id="{node["id"]}"]',NS)
        words=' '.join(t.text or '' for t in element.findall('s:text',NS)) if element is not None else ''
        norm=lambda text:' '.join(text.split()).casefold()
        if norm(node['label']) not in norm(words) or norm(node['detail']) not in norm(words):findings.append(node['id']+': missing visible source text.')
        if not re.search(rf'\b{node["founded"]}\b',words):findings.append(node['id']+': missing visible founding year.')
    fields=('id','source','target','kind')
    if sorted(tuple(e[k] for k in fields) for e in data['edges'])!=sorted(tuple(e[k] for k in fields) for e in expected['edges']):findings.append('Typed relationship inventory differs.')
    if data['groups']!=expected['groups']:findings.append('Supplied groups or colors changed.')
    if report['status']!='pass':findings.append('The browser audit fails.')
    if any(w['type']=='unrelated-shared-run' for w in report.get('composition_warnings',[])):findings.append('Unrelated visible shared runs remain.')
    titles={e.get('data-owner') for e in root.findall('.//s:text',NS)}
    if not set(actual)<=titles:findings.append('Some records have no editable text.')
    text=' '.join(root.find('s:desc',NS).itertext()).lower()
    if 'fiction' not in text and 'synthetic' not in text:findings.append('Fictional status is not identified.')
    artwork=root.findall('.//*[@data-artwork]',NS)
    if len(artwork)<2:findings.append('Fewer than two selected illustrations.')
    starts={};image_reads=[]
    for line in (run/'events.jsonl').read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event.get('type')=='tool_execution_start':starts[event['toolCallId']]=event.get('args',{}).get('path','').replace('\\','/')
        if event.get('type')=='tool_execution_end' and starts.get(event.get('toolCallId'),'').endswith('result/poster.png'):
            content=event.get('result',{}).get('content',[])
            if any(c.get('type')=='image' for c in content) and not any('does not support images' in c.get('text','') for c in content):image_reads.append(event['toolCallId'])
    if not image_reads:findings.append('No supported final PNG inspection in the trace.')
    return dict(status='fail' if findings else 'pass',run=run.name,node_count=len(actual),edge_count=len(data['edges']),
        canvas=report['canvas'],warnings=report.get('composition_warnings',[]),supported_final_image_reads=len(image_reads),findings=findings,
        scope='Disclosed development task; semantic and routing checks do not grade visual parity.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    try:result=inspect(args.run)
    except (OSError,ValueError,KeyError,AttributeError,ET.ParseError) as e:result=dict(status='fail',run=args.run.name,findings=[str(e)])
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
    return result['status']!='pass'


if __name__=='__main__':raise SystemExit(main())

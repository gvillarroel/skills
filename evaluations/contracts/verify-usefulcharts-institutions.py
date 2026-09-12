#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Evaluate the fictional institutions case independently of its renderer."""

import argparse
import json
import re
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}
RECORDS={
    'house of inquiry':('origin',[1120]),
    'makers guild':('mechanical',[1190]),
    'calendar office':('astronomical',[1210]),
    'balance college':('mechanical',[1274]),
    'clockmakers fellowship':('mechanical',[1301]),
    'pendulum circle':('mechanical',[1418,1497]),
    'standards bureau':('mechanical',[1480]),
    'mechanical academy':('mechanical',[1540]),
    'meridian observatory':('astronomical',[1360]),
    'transit house':('astronomical',[1461]),
    'star census':('astronomical',[1504]),
    'united observatories':('astronomical',[1572]),
    'instrument research house':('mechanical',[1635]),
    'open sky archive':('astronomical',[1894]),
}
LINKS=[('house of inquiry','makers guild'),('house of inquiry','calendar office'),
    ('makers guild','balance college'),('makers guild','clockmakers fellowship'),
    ('clockmakers fellowship','pendulum circle'),('balance college','standards bureau'),
    ('standards bureau','mechanical academy'),('clockmakers fellowship','mechanical academy'),
    ('calendar office','meridian observatory'),('meridian observatory','transit house'),
    ('meridian observatory','star census'),('transit house','united observatories'),
    ('star census','united observatories'),('mechanical academy','instrument research house'),
    ('united observatories','instrument research house'),('united observatories','open sky archive')]


def normalized(value):
    return re.sub(r'^the ','',re.sub(r'[^a-z0-9 ]','',value.lower())).strip()


def inspect(run):
    folder=run/'workspace/result'
    data=json.loads((folder/'source.json').read_text(encoding='utf-8'))
    browser=json.loads((folder/'browser.json').read_text(encoding='utf-8'))
    root=ET.parse(folder/'poster.svg').getroot()
    findings=[]
    by_name={normalized(n['label']):n for n in data['nodes']}
    if set(by_name)!=set(RECORDS):findings.append('Named record inventory differs from the prompt.')
    by_id={n['id']:name for name,n in by_name.items()}
    actual=[]
    for edge in data['edges']:
        pair=(by_id.get(edge['source']),by_id.get(edge['target']))
        actual.append(pair)
        influence=pair==('united observatories','instrument research house')
        if (edge['kind']=='influence')!=influence:findings.append(f'Wrong relationship type: {pair}')
    if sorted(actual)!=sorted(LINKS):findings.append('Relationship inventory differs from the prompt.')
    anchors={key:by_name[name]['group'] for key,name in [('origin','house of inquiry'),('mechanical','makers guild'),('astronomical','calendar office')] if name in by_name}
    if len(set(anchors.values()))!=3:findings.append('The three source categories are not distinct.')
    for name,(category,years) in RECORDS.items():
        if name not in by_name:continue
        node=by_name[name];element=root.find(f'.//s:g[@data-node-id="{node["id"]}"]',NS)
        if element is None:
            findings.append(f'Missing visible record: {name}');continue
        text=' '.join(t.text or '' for t in element.findall('s:text',NS))
        if any(not re.search(rf'\b{year}\b',text) for year in years):findings.append(f'Missing date: {name}')
        if node['group']!=anchors.get(category):findings.append(f'Family category changed: {name}')
        if name in ('mechanical academy','united observatories') and element.get('data-treatment') not in ('hero','emblem'):
            findings.append(f'Major merger lacks emphasis: {name}')
    if not root.findall('.//s:svg[@data-illustration-id="astrolabe-observation"]',NS):findings.append('Required observation illustration is absent.')
    credit=root.find('.//s:metadata[@data-artwork-source="astrolabe-observation.svg"]',NS)
    if credit is None or 'Pearson Scott Foresman' not in (credit.text or ''):findings.append('Illustration identity is absent.')
    if 'synthetic' not in ' '.join(root.itertext()).lower():findings.append('Synthetic status is not stated.')
    w,h=map(float,root.get('viewBox').split()[2:])
    if w*h>2_000_000:findings.append('Fourteen records occupy an excessively large canvas for this compact case.')
    node_ids={n['id'] for n in data['nodes']}
    fonts=[t['font'] for t in browser['texts'] if t['owner'] in node_ids]
    if statistics.median(fonts)<13:findings.append('Most record text is too small for the compact case.')
    if browser['status']!='pass':findings.append('The source-backed browser audit fails.')
    image_reads=[];omitted_images=[];tool_paths={}
    for line in (run/'events.jsonl').read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event.get('type')=='tool_execution_start':tool_paths[event['toolCallId']]=event.get('args',{}).get('path','').replace('\\','/')
        if event.get('type')=='tool_execution_end' and any(c.get('type')=='image' for c in event.get('result',{}).get('content',[])):
            if not tool_paths.get(event.get('toolCallId'),'').endswith('result/poster.png'):continue
            content=event['result']['content']
            omitted=any('does not support images' in c.get('text','') for c in content)
            (omitted_images if omitted else image_reads).append(event.get('toolCallId'))
    if not image_reads:findings.append('The trace has no supported image-reading result; omitted images and preview dimensions do not constitute visual inspection.')
    return dict(status='fail' if findings else 'pass',run=run.name,canvas=[w,h],node_count=len(data['nodes']),edge_count=len(data['edges']),image_read_count=len(image_reads),omitted_image_count=len(omitted_images),findings=findings,
        limitation='These checks cover this task contract. Visual quality and parity with a reference still require independent image review.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=inspect(args.run)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));raise SystemExit(result['status']!='pass')


if __name__=='__main__':main()

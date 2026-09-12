#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check all Silver Vale facts and visible relation semantics."""

import argparse
import collections
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def expected(prompt):
    people={};unions={}
    for line in prompt.read_text(encoding='utf-8').splitlines():
        columns=[s.strip() for s in line.strip('|').split('|')]
        if len(columns)==6 and re.fullmatch(r'p\d\d',columns[0]):
            key,name,birth,death,house,row=columns
            people[key]=dict(label=name,birth=None if birth=='unknown' else int(birth),death=int(death),house=house,row=int(row))
        elif len(columns)==3 and re.fullmatch(r'u\d\d',columns[0]):
            key,partners,children=columns
            unions[key]=dict(partners=partners.split(', '),children=[] if children=='none' else children.split(', '))
    assert len(people)==48 and len(unions)==21
    return people,unions


def inspect(run,repo):
    expected_people,expected_unions=expected(repo/'evaluations/pi-prompts/usefulcharts-family-baselines.md')
    folder=run/'workspace/result';failures=[]
    required=['source.json','poster.svg','poster.html','layout.json','browser.json','poster.png']
    missing=[name for name in required if not (folder/name).is_file()]
    if missing:return dict(status='fail',missing=missing)
    source=json.loads((folder/'source.json').read_text(encoding='utf-8-sig'))
    root=ET.parse(folder/'poster.svg').getroot();nodes=source.get('nodes',[])
    actual={n['id']:n for n in nodes};groups={g['id']:g for g in source.get('groups',[])}
    if len(nodes)!=48 or set(actual)!=set(expected_people):failures.append('Exact person inventory')
    numeric_dates=0
    for key,person in expected_people.items():
        node=actual.get(key,{})
        if node.get('label')!=person['label'] or node.get('row')!=person['row']:failures.append(f'{key}: name/generation')
        group=groups.get(node.get('group'),{}).get('label','')
        if re.sub(r'^House\s+','',group,flags=re.I)!=person['house']:failures.append(f'{key}: house')
        element=root.find(f'.//s:g[@data-node-id="{key}"]',NS)
        text=' '.join(element.itertext()) if element is not None else ''
        detail=str(node.get('detail',''))
        for field in ['birth','death']:
            value=person[field]
            if value is None:
                if node.get(field) is not None or 'unknown' not in text.lower():failures.append(f'{key}: unknown birth')
            else:
                if field in node and node[field]!=value:failures.append(f'{key}: changed numeric {field}')
                if str(value) not in detail or str(value) not in text:failures.append(f'{key}: missing visible {field}')
                if node.get(field)==value:numeric_dates+=1
    actual_unions={u['id']:u for u in source.get('unions',[])}
    if len(source.get('unions',[]))!=21 or set(actual_unions)!=set(expected_unions):failures.append('Exact union inventory')
    declared=collections.Counter()
    for key,union in expected_unions.items():
        supplied=actual_unions.get(key,{})
        if sorted(supplied.get('partners',[]))!=sorted(union['partners']):failures.append(f'{key}: partnership')
        for child in union['children']:declared[(key,child,'descent')]+=1
    declared[('p32','p48','uncertain')]+=1
    realized=collections.Counter((u['id'],child,'descent') for u in source.get('unions',[]) for child in u.get('children',[]))
    realized.update((e.get('source'),e.get('target'),e.get('kind')) for e in source.get('edges',[]))
    if realized!=declared:failures.append('Exact source relationship inventory')
    visible=collections.Counter((e.get('data-source'),e.get('data-target'),e.get('data-kind')) for e in root.findall('.//s:path[@data-edge-id]',NS))
    if visible!=declared:failures.append('Exact visible relationship inventory')
    if len(root.findall('.//s:g[@data-node-id]',NS))!=48:failures.append('Visible person count')
    uncertain=root.find('.//s:path[@data-kind="uncertain"]',NS)
    if uncertain is None or not uncertain.get('stroke-dasharray'):failures.append('Visible uncertainty treatment')
    visible_text=' '.join(' '.join(' '.join(text.itertext()) for text in root.findall('.//s:text',NS)).split())
    context={}
    for key,phrase in [('p05','Cedar archive'),('p11','Alder school'),('p41','Birch reading room')]:
        anchored=any(a.get('node')==key and phrase in a.get('label','') for a in source.get('annotations',[]))
        own=any(phrase in str(actual.get(key,{}).get(field,'')) for field in ['detail','label','date_label'])
        context[key]=dict(phrase=phrase,anchored=anchored,inside_person=own,visible=phrase in visible_text)
        if not context[key]['visible']:failures.append(f'{key}: visible context')
    # The evaluator reruns the browser against the supplied source. An agent's
    # own status field alone cannot satisfy this gate.
    command=['uv','run','--script',str(repo/'skills/usefulcharts-style/scripts/audit_chart.py'),str(folder/'poster.svg'),
        '--source',str(folder/'source.json'),'--report',str(run/'independent-browser.json')]
    check=subprocess.run(command,cwd=repo,capture_output=True,text=True)
    if check.returncode:failures.append('Independent browser audit')
    browser=json.loads((run/'independent-browser.json').read_text()) if (run/'independent-browser.json').exists() else {}
    return dict(status='pass' if not failures else 'fail',failures=failures,people=len(actual),unions=len(actual_unions),
        relationships=sum(declared.values()),numeric_source_dates=numeric_dates,context=context,
        canvas=root.get('viewBox'),browser_status=browser.get('status'),browser_findings=browser.get('findings'),
        visual_review='Required separately; these are fact and geometry checks.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path)
    parser.add_argument('--repo',type=Path,default=Path.cwd());parser.add_argument('--output',type=Path)
    args=parser.parse_args();report=inspect(args.run.resolve(),args.repo.resolve())
    if args.output:args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report));return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())

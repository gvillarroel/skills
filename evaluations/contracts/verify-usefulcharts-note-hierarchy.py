#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify mixed event typography, protected facts and image/date association."""

import argparse
import copy
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def inspect(run):
    control='-contract-' in run.name
    if control:
        folder=run/'workspace';draft=json.loads((folder/'draft.json').read_text(encoding='utf-8'))
        data=json.loads((folder/'deliverables/brief.json').read_text(encoding='utf-8'));normalized=copy.deepcopy(data)
        for event in normalized['events']:
            event.pop('offset',None);event.pop('width',None)
            if event['id']=='clock':event['art_position']='auto'
        result=dict(status='pass',findings=[])
        if normalized!=draft:result['findings'].append('Protected source fields changed.')
        folder=folder/'deliverables'
        if next(e for e in data['events'] if e['id']=='clock').get('art_position') in ('auto','above'):
            result['findings'].append('The clock was not resolved outside the preceding date band.')
    else:
        spec=importlib.util.spec_from_file_location('art_contract',Path(__file__).with_name('verify-usefulcharts-contextual-art.py'))
        contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
        result=contract.inspect(run);folder=run/'workspace/result'
        data=json.loads((folder/'source.json').read_text(encoding='utf-8'))
    root=ET.parse(folder/'poster.svg').getroot();browser=json.loads((folder/'browser.json').read_text(encoding='utf-8'))
    if browser['status']!='pass':result['findings'].append('The browser audit failed.')
    paragraphs=[event for event in data['events'] if event.get('text_layout')=='paragraph']
    if len(paragraphs)<(4 if control else 9):result['findings'].append('Ordinary notes do not use the requested running paragraphs.')
    if not control:
        for eid in ('ec5','eh3','ep5'):
            event=next(event for event in data['events'] if event['id']==eid)
            if event.get('text_layout','stacked')!='stacked':result['findings'].append('The requested landmark has no separate heading: '+eid)
    normalize=lambda value:' '.join(value.split())
    for event in paragraphs:
        group=root.find(f'.//s:g[@data-event-id="{event["id"]}"]',NS)
        lines=group.findall('s:text',NS) if group is not None else []
        runs=[run for line in lines for run in line.findall('s:tspan',NS)]
        if not runs or any(line.get('data-event-text-role')!='paragraph' for line in lines):result['findings'].append('Missing paragraph runs: '+event['id']);continue
        heading=event['label'].strip()
        if heading and heading[-1] not in '.?!:':heading+='.'
        actual=normalize(' '.join(''.join(line.itertext()) for line in lines))
        if actual!=normalize(heading+' '+event.get('detail','')):result['findings'].append('Paragraph words or order changed: '+event['id'])
        for run in runs:
            is_heading=run.get('data-event-run-role')=='heading'
            expected_size=event.get('size',10.5) if is_heading else event.get('detail_size',event.get('size',10.5)*.88)
            if abs(float(run.get('font-size'))-expected_size)>.02 or run.get('font-weight')!=('700' if is_heading else '400'):
                result['findings'].append('Paragraph type hierarchy changed: '+event['id'])
    # Read the actual viewports from SVG, not the skill's warning field.
    competing=[];y0=190;y1=data['height']-112
    scale=lambda year:y0+(year-data['time']['start'])/(data['time']['end']-data['time']['start'])*(y1-y0)
    for event in data['events']:
        group=root.find(f'.//s:g[@data-event-id="{event["id"]}"]',NS)
        art=group.find('s:svg[@data-illustration-id]',NS) if group is not None else None
        if art is None:continue
        ay=float(art.get('y'));bottom=ay+float(art.get('height'))
        others=[other['id'] for other in data['events'] if other['id']!=event['id'] and other['lane']==event['lane'] and ay<=scale(other['year'])<=bottom]
        if others:competing.append(dict(event=event['id'],others=others))
    if competing:result['findings'].append('An illustration shares another same-region event date band; inspect and repair ownership.')
    result.update(status='fail' if result['findings'] else 'pass',paragraphs=len(paragraphs),events=len(data['events']),competing_dates=competing,
        limitation='Source, type and date-band checks cannot establish perceived ownership or aesthetic parity; inspect the final image.')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=inspect(args.run)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));raise SystemExit(result['status']!='pass')


if __name__=='__main__':main()

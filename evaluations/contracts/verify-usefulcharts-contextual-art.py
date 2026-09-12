#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check supplied histories and actual illustration arrangements independently."""

import argparse
import copy
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

NS={'s':'http://www.w3.org/2000/svg'}


def inspect(run):
    if '-contract-' in run.name:
        folder=run/'workspace';source=json.loads((folder/'draft.json').read_text())
        data=json.loads((folder/'deliverables/brief.json').read_text());normalized=copy.deepcopy(data)
        for event in normalized['events']:event.pop('offset',None);event.pop('width',None)
        result=dict(status='pass',findings=[],exact_source_preserved=normalized==source)
        if normalized!=source:result['findings'].append('Protected source fields changed.')
        root=ET.parse(folder/'deliverables/poster.svg').getroot()
        browser=json.loads((folder/'deliverables/browser.json').read_text())
        if browser['status']!='pass':result['findings'].append('The browser audit failed.')
        expected={'clock':'clock-escapement','ship':'square-rigged-ship','bridge':'suspension-bridge','post':'stagecoach'}
    else:
        spec=importlib.util.spec_from_file_location('regions_contract',Path(__file__).with_name('verify-usefulcharts-regions.py'))
        contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
        result=contract.inspect(run);folder=run/'workspace/result'
        data=json.loads((folder/'source.json').read_text());root=ET.parse(folder/'poster.svg').getroot()
        expected={'ec2':'clock-escapement','ep1':'suspension-bridge','eh1':'stagecoach'}
    events={event['id']:event for event in data['events']};positions=[]
    for eid,image in expected.items():
        event=events.get(eid,{})
        el=root.find(f'.//s:g[@data-event-id="{eid}"]/s:svg[@data-illustration-id="{image}"]',NS)
        if el is None or event.get('icon')!='illustration-'+image:
            result['findings'].append('Missing contextual image: '+eid);continue
        use=el.find('s:use',NS)
        if use is None or use.get('href')!='#asset-illustration-'+image:result['findings'].append('Incorrect image symbol: '+eid)
        position=event.get('art_position','below');positions.append(position)
        group=root.find(f'.//s:g[@data-event-id="{eid}"]',NS);texts=group.findall('s:text',NS)
        if not texts:result['findings'].append('Missing visible note: '+eid);continue
        first_y=float(texts[0].get('y'))-float(texts[0].get('font-size'))
        last_y=float(texts[-1].get('y'));x=float(el.get('x'));y=float(el.get('y'));w=float(el.get('width'));h=float(el.get('height'))
        if position=='above' and y+h>first_y-4.8:result['findings'].append('Above image is not above the text: '+eid)
        if position=='below' and y<last_y+4.8:result['findings'].append('Below image is not below the text: '+eid)
        if position in ('left','right') and abs(y-first_y)>.12:result['findings'].append('Side image moved off the event date: '+eid)
        if position=='left' and x+w>=min(float(t.get('x')) for t in texts):result['findings'].append('Left image is not left of the note: '+eid)
        if position=='right' and x<=max(float(t.get('x')) for t in texts):result['findings'].append('Right image is not right of the note: '+eid)
    if len(set(positions))<2 or not any(p in ('left','right') for p in positions):result['findings'].append('The requested arrangement variety is absent.')
    result.update(status='fail' if result['findings'] else 'pass',art_positions=positions,illustrations_checked=len(expected))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=inspect(args.run)
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));raise SystemExit(result['status']!='pass')


if __name__=='__main__':main()

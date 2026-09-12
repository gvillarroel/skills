#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify the authored-history refinement without relying on its self-review."""

import argparse
import json
import re
import runpy
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect(run):
    base=runpy.run_path(str(Path(__file__).with_name('verify-usefulcharts-data-first-publishing.py')))
    result=base['inspect'](run)
    expected=json.loads(re.search(r'```json\s*(.*?)\s*```',(run/'prompt.md').read_text(encoding='utf-8'),re.S).group(1))
    folder=run/'workspace/result'
    data=json.loads((folder/'source.json').read_text(encoding='utf-8'))
    findings=result['findings']
    expected_files={'source.json','poster.svg','poster.html','layout.json','browser.json','poster.png','review.md'}
    if {path.name for path in folder.iterdir() if path.is_file()}!=expected_files:
        findings.append('The result directory differs from the exact requested artifact inventory.')
    if {n['id']:n for n in data['nodes']}!={n['id']:n for n in expected['nodes']}:
        findings.append('The supplied record fields, positions or type settings changed.')
    for field in ('width','height','font_size','source_note','reading_note'):
        if data.get(field)!=expected.get(field):findings.append('Changed supplied '+field+'.')
    edges=lambda values:{e['id']:{k:v for k,v in e.items() if k not in ('via','corridor_y')} for e in values}
    if edges(data['edges'])!=edges(expected['edges']):findings.append('Changed a supplied non-corridor relationship field.')
    root=ET.parse(folder/'poster.svg').getroot();ns={'s':'http://www.w3.org/2000/svg'}
    normalize=lambda text:' '.join(text.split())
    visible=lambda role:normalize(' '.join(''.join(node.itertext()) for node in root.findall(f'.//s:text[@data-inset-role="{role}"]',ns)))
    if visible('story')!='Two workshops combine in The Common Press in 1471. Later branches serve science, schools and public readers.':
        findings.append('Missing or changed exact contextual paragraph.')
    headings=visible('title')
    for heading in ('From workshops to readers','Institutions represented in this history'):
        if heading not in headings:findings.append('Missing contextual heading: '+heading)
    groups=root.findall('.//s:g[@data-count-group]',ns)
    if {group.get('data-count-group') for group in groups}!={g['id'] for g in expected['groups']}:
        findings.append('The overview does not expose every supplied category.')
    if len(root.findall('.//s:path[@data-count-mark]',ns))!=len(expected['nodes']):findings.append('The visible mark inventory differs from the institution count.')
    story=root.find('.//s:g[@data-inset-kind="story"]',ns)
    if story is None or story.find('.//*[@data-illustration-id="printing-press-bookman"]') is None:
        findings.append('The requested printing illustration is absent from the story.')
    independent=run/'independent-browser.json'
    if independent.exists():
        browser=json.loads(independent.read_text(encoding='utf-8'))
        if browser['findings'] or browser.get('composition_warnings'):findings.append('The evaluator browser replay contains findings or warnings.')
    result.update(status='fail' if findings else 'pass',counts=len(root.findall('.//s:path[@data-count-mark]',ns)),
                  scope='Naturalistic refinement of a disclosed authored development poster. Exact fields and visible inset content are checked; no blind visual-parity claim.')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:result=inspect(args.run)
    except (OSError,ValueError,KeyError,AttributeError,ET.ParseError) as error:result=dict(status='fail',findings=[str(error)])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
    return result['status']!='pass'


if __name__=='__main__':raise SystemExit(main())

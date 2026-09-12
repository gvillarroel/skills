#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently verify complete records, typography and visible branch titles."""

import argparse
import json
import re
import runpy
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect(run, browser_path):
    base = runpy.run_path(str(Path(__file__).with_name('verify-usefulcharts-data-first-publishing.py')))
    result = base['inspect'](run)
    expected = json.loads(re.search(r'```json\s*(.*?)\s*```', (run/'prompt.md').read_text(encoding='utf-8'), re.S).group(1))
    folder = run/'workspace/result'
    source = json.loads((folder/'source.json').read_text(encoding='utf-8-sig'))
    original = {node['id']:node for node in expected['nodes']}
    actual = {node['id']:node for node in source['nodes']}
    for nid, node in original.items():
        if any(actual.get(nid, {}).get(key) != value for key, value in node.items()):
            result['findings'].append(f'{nid}: changed a supplied record field.')
    for field in ('id', 'title', 'source_note', 'reading_note'):
        if source.get(field) != expected.get(field):
            result['findings'].append(f'Changed supplied {field}.')
    captions = {item['node']:item for item in source.get('annotations', [])}
    for caption in expected['annotations']:
        if any(captions.get(caption['node'], {}).get(key) != value for key, value in caption.items()):
            result['findings'].append(caption['node']+': changed or omitted its supplied family caption.')
    if len(captions) != len(expected['annotations']):
        result['findings'].append('The family-caption inventory differs.')
    root = ET.parse(folder/'poster.svg').getroot()
    ns = {'s':'http://www.w3.org/2000/svg'}
    visible_captions = {}
    for group in root.findall('.//s:g[@data-annotation-id]', ns):
        visible_captions[' '.join(' '.join(t.itertext()) for t in group.findall('s:text', ns))] = group
    normalize = lambda value: ' '.join(value.split())
    if not {normalize(item['label']) for item in expected['annotations']} <= {normalize(value) for value in visible_captions}:
        result['findings'].append('A supplied caption is missing from editable SVG text.')
    for text in root.findall('.//s:text', ns):
        if text.get('data-owner') not in original:
            continue
        role = text.get('data-content-role')
        minimum = 16 if role == 'name' else 12
        if float(text.get('font-size', '0')) < minimum:
            result['findings'].append(f'{text.get("data-owner")}: visible {role or "text"} is too small.')
    exact = {'source.json','poster.svg','poster.html','layout.json','browser.json','poster.png','review.md'}
    if {path.name for path in folder.iterdir()} != exact:
        result['findings'].append('The result directory does not contain exactly the seven requested deliverables.')
    if not browser_path.exists():
        result['findings'].append('Independent replay of the final source and SVG did not produce a report.')
    else:
        independent = json.loads(browser_path.read_text(encoding='utf-8'))
        if independent.get('status') != 'pass' or independent.get('findings') or independent.get('composition_warnings'):
            result['findings'].append('Independent replay of the delivered source and SVG fails or retains composition warnings.')
    result.update(version=2, status='fail' if result['findings'] else 'pass', caption_count=len(captions),
                  scope='Disclosed 70-record data-first development task with five supplied captions. No full-mural generalization or aesthetic-parity claim.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--browser-report', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.run, args.browser_report)
    except (OSError, ValueError, KeyError, AttributeError, ET.ParseError) as error:
        result = dict(status='fail', run=args.run.name, findings=[str(error)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))
    return result['status'] != 'pass'


if __name__ == '__main__':
    raise SystemExit(main())

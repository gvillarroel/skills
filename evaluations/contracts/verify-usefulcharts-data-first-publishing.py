#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently check the publishing source, visible content and selected artwork."""

import argparse
import json
import re
import runpy
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect(run):
    shared = runpy.run_path(str(Path(__file__).with_name('verify-usefulcharts-branch-structure.py')))
    result = shared['inspect'](run)
    expected = json.loads(re.search(r'```json\s*(.*?)\s*```', (run / 'prompt.md').read_text(encoding='utf-8'), re.S).group(1))
    source = json.loads((run / 'workspace/result/source.json').read_text(encoding='utf-8-sig'))
    actual = {n['id']: n for n in source['nodes']}
    root = ET.parse(run / 'workspace/result/poster.svg').getroot()
    ns = {'s': 'http://www.w3.org/2000/svg'}
    text_labels = {''.join(node.itertext()) for node in root.findall('.//s:text', ns)}
    if source['title'] != expected['title'] or root.find('s:title', ns).text != expected['title'] or expected['title'].upper() not in text_labels:
        result['findings'].append('The source or visible SVG title differs from the captured task.')
    for node in expected['nodes']:
        for field in ('icon', 'emphasis'):
            if field in node and actual.get(node['id'], {}).get(field) != node[field]:
                result['findings'].append(f'{node["id"]}: changed source {field}.')
        if node.get('icon'):
            group = root.find(f'.//s:g[@data-node-id="{node["id"]}"]', ns)
            if group is None or not group.findall('.//*[@data-artwork]'):
                result['findings'].append(node['id'] + ': supplied illustration is not visible in its record.')
    result['status'] = 'fail' if result['findings'] else 'pass'
    result['scope'] = 'Disclosed new-subject development task. Exact content and artifact checks do not grade aesthetic parity.'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = inspect(args.run)
    except (OSError, ValueError, KeyError, AttributeError, ET.ParseError) as error:
        result = dict(status='fail', run=args.run.name, findings=[str(error)])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))
    return result['status'] != 'pass'


if __name__ == '__main__':
    raise SystemExit(main())

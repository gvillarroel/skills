#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify complete family meaning and the three requested visible focal records."""

import argparse
import importlib.util
import json
import statistics
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect(run,repo):
    spec=importlib.util.spec_from_file_location('landmark_contract',Path(__file__).with_name('verify-usefulcharts-family-landmarks.py'))
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    report=checker.inspect(run,repo)
    if report.get('missing'):return report
    source=json.loads((run/'workspace/result/source.json').read_text(encoding='utf-8'))
    browser=json.loads((run/'independent-browser.json').read_text(encoding='utf-8'))
    root=ET.parse(run/'workspace/result/poster.svg').getroot();ns={'s':'http://www.w3.org/2000/svg'}
    nodes={n['id']:n for n in source['nodes']};focal={'p01','p05','p11'}
    font={key:max((t['font'] for t in browser['texts'] if t.get('owner')==key),default=0) for key in nodes}
    ordinary=statistics.median(font[key] for key in nodes if key not in focal)
    portraits={key for key,node in nodes.items() if str(node.get('icon','')).startswith('museum-')}
    if portraits!=focal:report['failures'].append('Exact three requested portrait owners')
    evidence=[]
    for key in sorted(focal):
        portrait=root.find(f'.//s:g[@data-node-id="{key}"]/s:svg[@data-artwork="public-domain-museum-image"]/s:image',ns)
        correct=portrait is not None and font[key]>ordinary
        if not correct:report['failures'].append(f'{key}: visible portrait and larger name')
        evidence.append(dict(node=key,icon=nodes[key].get('icon'),visible_image=portrait is not None,
            visible_max_type=font[key],ordinary_median_type=ordinary,icon_width=nodes[key].get('icon_width'),passed=correct))
    report.update(status='fail' if report['failures'] else 'pass',focal_people=evidence,
        page_notes=[t['text'] for t in browser['texts'] if t.get('owner')=='page' and t['box']['y']>browser['canvas'][1]*.9])
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path)
    parser.add_argument('--repo',type=Path,default=Path.cwd());parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=inspect(args.run.resolve(),args.repo.resolve())
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())

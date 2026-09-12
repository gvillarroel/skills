#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Preserve the full family contract and record visible name/date treatments."""

import argparse
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def inspect(run,repo):
    spec=importlib.util.spec_from_file_location('focal_contract',Path(__file__).with_name('verify-usefulcharts-family-emphasis.py'))
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    report=checker.inspect(run,repo)
    if report.get('missing'):return report
    source=json.loads((run/'workspace/result/source.json').read_text(encoding='utf-8'))
    root=ET.parse(run/'workspace/result/poster.svg').getroot();ns={'s':'http://www.w3.org/2000/svg'}
    paints={g['id']:g['color'].lower() for g in source['groups']};nodes=[]
    for node in source['nodes']:
        group=root.find(f'.//s:g[@data-node-id="{node["id"]}"]',ns)
        panel=group.find('s:rect[@data-name-panel]',ns)
        if panel is None:panel=group.find('s:rect[@data-node-box]',ns)
        colored=panel is not None and panel.attrib.get('fill','').lower()==paints[node['group']]
        if not colored:continue
        text=[t for t in group.findall('s:text',ns) if t.attrib.get('font-weight')=='700']
        dark=lambda t:t.attrib.get('fill','').startswith('#') and max(int(t.attrib['fill'][i:i+2],16) for i in (1,3,5))<=80
        nodes.append(dict(id=node['id'],has_portrait=bool(node.get('icon')),
            solid_name_and_date=group.find('s:rect[@data-content-envelope]',ns) is None,
            dark_name=bool(text) and all(dark(t) for t in text),
            visible_name_inks=sorted({t.attrib.get('fill') for t in text}),fill=panel.attrib.get('fill')))
    report['nameplate_observations']=dict(colored_people=len(nodes),
        solid_name_and_date=sum(n['solid_name_and_date'] for n in nodes),dark_names=sum(n['dark_name'] for n in nodes),
        people=nodes,limitation='Descriptive browser/SVG evidence; direct visual review remains required and these counts do not establish aesthetic equivalence.')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path)
    parser.add_argument('--repo',type=Path,default=Path.cwd());parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=inspect(args.run.resolve(),args.repo.resolve())
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Reproduce the genealogy revision using its promoted runtime placement helper."""

import argparse
import copy
import json
import sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--date-scale',type=float,default=3)
    args=parser.parse_args();root=Path(__file__).resolve().parents[3]
    sys.path.insert(0,str(root/'skills/usefulcharts-style/scripts'))
    from render_chart import text_width
    from space_family_branches import space_branches
    data=copy.deepcopy(json.loads(args.source.read_text(encoding='utf-8')))
    data.update(layout='cohorts',cohort_top=195,cohort_bottom=2590,
        cohort_weights={str(row):1.1 for row in range(1,6)})
    for node in data['nodes']:
        if node.get('style')=='plain':continue
        node.update(detail_position='outside',size=13.5 if node['row']==0 else 11.8,detail_size=9.1)
        if node.get('icon'):node['icon_width']=36 if node['row']==0 else 33
        node['width']=max(58,text_width(node['label'],node['size'],True)+14+node.get('icon_width',0),
            text_width(node.get('detail',''),node['detail_size'])+16)
    for annotation in data.get('annotations',[]):
        if annotation.get('kind')=='heading':annotation['dy']=35
    resolved,report=space_branches(data,date_scale=args.date_scale,local_labels=True)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'source.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
    (args.output/'composition.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',units=report['family_units'],shifted=report['shifted_units'])))


if __name__=='__main__':main()

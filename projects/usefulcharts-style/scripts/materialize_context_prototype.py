#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Transfer the reviewed publishing context into native editable inset fields."""

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster
from render_chart import viewer


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    original=json.loads((ROOT/'projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32/publishing-education-group/source.json').read_text(encoding='utf-8'))
    data=copy.deepcopy(original)
    data['insets']=data.pop('context_panels')
    for inset in data['insets']:
        if inset['kind']=='story':
            inset.update(source_nodes=['scribes','cutters','common','university','school','public'],art_width=90,art_height=152)
        else:
            inset['columns']=2
            inset['box'][3]=240
    assert data['nodes']==original['nodes'] and data['edges']==original['edges']
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    try:
        svg,report=EditorialPoster(data).render()
        (args.output/'poster.svg').write_text(svg,encoding='utf-8')
        (args.output/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
        (args.output/'layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report))
    except ValueError as error:
        record=dict(status='fail',error=str(error))
        (args.output/'failure.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(record))
        return 1
    return 0


if __name__=='__main__':raise SystemExit(main())

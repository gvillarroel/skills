#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Promote the complete reviewed institutional geometry into its acceptance source."""

import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
FIXTURE=ROOT/'skills/usefulcharts-style/assets/examples/usefulcharts-style'


def main():
    data=json.loads((ROOT/'projects/usefulcharts-style/artifacts/reviews/institution-stages-v26/compact-canonical/source.json').read_text(encoding='utf-8'))
    by_id={node['id']:node for node in data['nodes']}
    path=FIXTURE/'lineage_brief.py';text=path.read_text(encoding='utf-8');changed=[]
    def replace(match):
        fields=match.group().split('|');node=by_id[fields[0]];width=fields[3].split(',')[2]
        fields[3]=f'{node["x"]!r},{node["y"]!r},{width}';changed.append(node['id']);return '|'.join(fields)
    text=re.sub(r'^[a-z][a-z0-9-]*\|[^\n]+$',replace,text,flags=re.M)
    assert set(changed)==set(by_id)
    text=text.replace("x, y, width = map(int, position.split(','))","x, y, width = map(float, position.split(','))\n            width=int(width)")
    start=text.find("    corridors={'clockmakers-to-pendulum'")
    if start!=-1:
        end=text.index("    records['observatories']",start);text=text[:start]+text[end:]
    text=text.replace("    data.update(pattern_id='usefulcharts-branching-lineage',","    data.update(width=1620,height=2430,pattern_id='usefulcharts-branching-lineage',")
    text=text.replace('box=[78,178,398,409]','box=[70.2,172,358.2,368.1]')
    text=text.replace('box=[1248,178,460,396]','box=[1123.2,172,414,356.4]')
    injection="""    # The complete reviewed routes are acceptance geometry, not inferred history.
    corridors=json.loads((Path(__file__).with_name('lineage-corridors.json')).read_text(encoding='utf-8'))
    assert set(corridors)=={edge['id'] for edge in data['edges']}
    for edge in data['edges']:edge.update(corridors[edge['id']])
"""
    if "lineage-corridors.json" not in text:text=text.replace('    return data\n',injection+'    return data\n')
    path.write_text(text,encoding='utf-8')
    corridors={edge['id']:{key:edge[key] for key in ('via','source_port','target_port') if key in edge} for edge in data['edges']}
    (FIXTURE/'lineage-corridors.json').write_text(json.dumps(corridors,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(nodes=len(changed),edges=len(corridors),canvas=[data['width'],data['height']])))


if __name__=='__main__':main()

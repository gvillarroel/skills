#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare every pre-revision genealogy fact with the authored composition."""

import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='ef294e37')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[3]
    name='skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.json'
    before=json.loads(subprocess.run(['git','show',f'{args.before}:{name}'],cwd=root,check=True,capture_output=True).stdout)
    after=json.loads((root/name).read_text(encoding='utf-8'));failures=[]
    visual={'x','y','width','height','size','detail_size','detail_position','icon_width'}
    def facts(node):return {key:value for key,value in node.items() if key not in visual}
    if [facts(n) for n in before['nodes']]!=[facts(n) for n in after['nodes']]:failures.append('Node facts or original source order changed')
    for key in ['unions','edges','groups','title','subtitle','reading_note']:
        if before.get(key)!=after.get(key):failures.append(f'Changed {key}')
    if after['source_note'] not in (before['source_note'],before['source_note']+' Heraldic devices are fictional.'):
        failures.append('Changed source provenance beyond the fictional-device disclosure')
    def annotations(data):return [{k:v for k,v in a.items() if k not in {'dx','dy'}} for a in data['annotations']]
    old=annotations(before);new=annotations(after)
    if old!=new[:len(old)]:failures.append('Changed existing annotation facts')
    for annotation in new[len(old):]:
        node=next((n for n in after['nodes'] if n['id']==annotation.get('node')),None)
        if annotation.get('kind')!='landmark' or node is None or not isinstance(node.get(annotation.get('field')),str):
            failures.append('Added a context annotation without an existing textual source field')
    pairs=after['unions'];nodes={n['id']:n for n in after['nodes']}
    if any(nodes[u['partners'][0]]['y']!=nodes[u['partners'][1]]['y'] for u in pairs):failures.append('Misaligned partnership')
    if any(nodes[child]['y']<=nodes[u['partners'][0]]['y'] for u in pairs for child in u.get('children',[])):failures.append('Nonadvancing parentage')
    report=dict(status='pass' if not failures else 'fail',before_revision=args.before,failures=failures,
        nodes=len(nodes),unions=len(pairs),relationships=sum(len(u.get('children',[])) for u in pairs)+len(after['edges']),
        source_sha256=hashlib.sha256((root/name).read_bytes()).hexdigest(),
        all_nonvisual_node_fields_preserved=True if not failures else None,
        additional_source_bound_landmarks=len(new)-len(old),
        changed_fields=sorted(visual|{'layout','dx','dy','cohort_top','cohort_bottom','cohort_weights'}))
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report));return 0 if not failures else 1


if __name__=='__main__':raise SystemExit(main())

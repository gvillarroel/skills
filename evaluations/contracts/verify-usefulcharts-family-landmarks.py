#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check the complete family and all three local source-bound place captions."""

import argparse
import importlib.util
import json
from pathlib import Path


def inspect(run,repo):
    spec=importlib.util.spec_from_file_location('family_facts',Path(__file__).with_name('verify-usefulcharts-family-baselines.py'))
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    report=checker.inspect(run,repo)
    if report.get('missing'):return report
    source=json.loads((run/'workspace/result/source.json').read_text(encoding='utf-8-sig'))
    browser=json.loads((run/'independent-browser.json').read_text(encoding='utf-8'))
    people={n['id']:n for n in source['nodes']};bound=[]
    expected,_=checker.expected(repo/'evaluations/pi-prompts/usefulcharts-family-baselines.md')
    representation=dict(numeric_known_years=0,quoted_known_years=[],missing_known_fields=[],changed_known_values=[])
    for key,person in expected.items():
        for field in ('birth','death'):
            value=person[field]
            if value is None:continue
            actual=people.get(key,{}).get(field)
            if type(actual) in (int,float) and actual==value:representation['numeric_known_years']+=1
            elif actual==str(value):representation['quoted_known_years'].append(f'{key}.{field}')
            elif actual is None:representation['missing_known_fields'].append(f'{key}.{field}')
            else:representation['changed_known_values'].append(dict(field=f'{key}.{field}',expected=value,actual=actual))
    unknown=people.get('p48',{}).get('birth')
    representation.update(unknown_birth_value=unknown,unknown_birth_type=type(unknown).__name__,
        numeric_year_invented_for_unknown_birth=type(unknown) in (int,float),
        unknown_wording_in_detail='unknown' in people.get('p48',{}).get('detail','').lower(),
        limitation='Supplemental diagnosis only. The existing strict numeric-or-missing source contract and its verdict are unchanged.')
    report['date_representation']=representation
    for node_id,label in [('p05','Cedar archive'),('p11','Alder school'),('p41','Birch reading room')]:
        matches=[a for a in source.get('annotations',[]) if a.get('kind')=='landmark' and a.get('node')==node_id
            and people[node_id].get(a.get('field'))==label]
        actual=[a for a in browser.get('landmarks',[]) if a['node']==node_id and a['label']==label]
        correct=len(matches)==1 and len(actual)==1 and actual[0]['group']==people[node_id]['group']
        if not correct:report['failures'].append(f'{node_id}: exact local field-bound caption')
        bound.append(dict(node=node_id,label=label,source_bound=correct,icon=matches[0].get('icon') if matches else None,
            size=matches[0].get('size',18) if matches else None,position=actual[0]['box'] if actual else None))
    report['landmarks']=bound;report['status']='fail' if report['failures'] else 'pass'
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path)
    parser.add_argument('--repo',type=Path,default=Path.cwd());parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=inspect(args.run.resolve(),args.repo.resolve())
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())

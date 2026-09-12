#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Preserve dated histories while comparing contextual illustration placements."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SKILL=ROOT/'skills/usefulcharts-style'
sys.path.insert(0,str(SKILL/'scripts'))
from pack_timeline_events import pack_events
from editorial_poster import EditorialPoster


def promote_sources():
    folder=ROOT/'projects/usefulcharts-style/artifacts/images/transport-illustrations'
    target=SKILL/'assets/illustrations';manifest=json.loads((target/'provenance.json').read_text())
    revisions=[1104606496,985017969,1234287232]
    for record,revision in zip(json.loads((folder/'downloads.json').read_text()),revisions):
        content=(folder/record['file']).read_bytes()
        assert hashlib.sha256(content).hexdigest()==record['sha256']
        width,height=map(float,record['viewBox'].split()[2:])
        entry={k:record[k] for k in ('id','file','image_url','source_url','sha256','bytes','modified')}
        entry.update(title=record['source_title'][:-4],creator='Pearson Scott Foresman; vector rendition uploaded by AzaToth',
            source_revision=revision,width=width,height=height,mime_type='image/svg+xml',retrieved='2026-09-12',
            rights='Public-domain dedication by Pearson Scott Foresman, confirmed by Wikimedia VRTS ticket 2010061110041093.',
            date_note='Undated explanatory illustration; SVG uploaded on 2007-12-02. This upload date is not an invention date. Contextual art does not depict a fictional event.',
            background='Unmodified transparent SVG field, visually inspected on poster paper at large and placed sizes.')
        if not any(item['id']==entry['id'] for item in manifest['items']):manifest['items'].append(entry)
        shutil.copyfile(folder/record['file'],target/record['file'])
    (target/'provenance.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--promote-sources',action='store_true')
    parser.add_argument('--phase',choices=('a','b','c','d'),default='a')
    args=parser.parse_args()
    if args.promote_sources:promote_sources()
    args.output.mkdir(parents=True,exist_ok=False)
    source_path='skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories.json'
    baseline=json.loads(subprocess.check_output(['git','show','c2131d54:'+source_path],cwd=ROOT))
    trials=[
        ('below',{'event-2-1':('square-rigged-ship','below',102,99.61),'event-1-2':('suspension-bridge','below',124,76.31),'event-4-8':('stagecoach','below',125,51.88)}),
        ('varied',{'event-2-1':('square-rigged-ship','above',102,99.61),'event-1-2':('suspension-bridge','above',124,76.31),'event-4-8':('stagecoach','below',125,51.88)}),
        ('side-ship',{'event-2-1':('square-rigged-ship','left',78,76.17),'event-1-2':('suspension-bridge','above',140,86.15),'event-1-8':('stagecoach','below',138,57.27)}),
    ]
    if args.phase in ('b','c'):
        trials=[(name,{**{key:value for key,value in edits.items() if key not in ('event-4-8','event-1-8')},
            'event-1-8':('stagecoach','above',128,53.13)}) for name,edits in trials]
    if args.phase=='c':
        trials=[(name,{**edits,'event-1-7':('clock-escapement','above',67,86.71)}) for name,edits in trials]
    if args.phase=='d':
        trials=[(name,{key:value for key,value in edits.items() if key not in ('event-4-8','event-1-8')}) for name,edits in trials]
    outcomes=[]
    for name,edits in trials:
        folder=args.output/name;folder.mkdir()
        data=json.loads(json.dumps(baseline))
        for event in data['events']:
            if event['id'] in edits:
                art,position,width,height=edits[event['id']]
                event.update(icon='illustration-'+art,art_position=position,art_width=width,art_height=height)
        (folder/'draft.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        try:
            data,placements=pack_events(data,max_width=200)
            svg,report=EditorialPoster(data).render()
            (folder/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
            (folder/'poster.svg').write_text(svg,encoding='utf-8')
            result=dict(id=name,status='rendered',placements=placements,layout=report)
        except ValueError as error:result=dict(id=name,status='needs-layout',message=str(error))
        (folder/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');outcomes.append(result)
    (args.output/'outcomes.json').write_text(json.dumps(outcomes,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{k:v for k,v in item.items() if k not in ('placements','layout')} for item in outcomes]))


if __name__=='__main__':main()

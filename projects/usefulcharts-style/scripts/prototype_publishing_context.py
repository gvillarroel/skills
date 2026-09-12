#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Explore purposeful context pockets and a more compact education branch."""

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster
from render_chart import viewer, wrap
from route_influences import compose_influences


class ContextPoster(EditorialPoster):
    def draw_insets(self):
        super().draw_insets()
        for item in self.data.get('context_panels', []):
            x,y,w,h=item['box']
            self.add(f'<g data-context-panel="{item["id"]}">')
            if item['kind']=='story':
                self.text(x+w/2,y+17,item['title'],17,bold=True)
                self.artwork(item['icon'],x+5,y+42,90,152,self.ink)
                lines=wrap(item['text'],w-117,14)
                for i,line in enumerate(lines):self.text(x+112,y+54+i*17,line,14,anchor='start')
            elif item['kind']=='counts':
                self.text(x+w/2,y+17,item['title'],17,bold=True)
                for index,group in enumerate(self.groups.values()):
                    xx=x+(index%2)*(w/2);yy=y+46+(index//2)*43
                    count=sum(n['group']==group['id'] for n in self.data['nodes'])
                    self.text(xx+4,yy,group['label'],12,bold=True,anchor='start')
                    for i in range(count):
                        px=xx+5+i*10
                        self.add(f'<path d="M{px} {yy+14}l3.5 -4l3.5 4v7h-7Z" fill="{group["color"]}"/>')
                    self.text(xx+w/2-18,yy+21,str(count),12,anchor='end')
                self.text(x+w/2,y+h-2,'One symbol = one institution shown',10,self.muted)
            self.add('</g>')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile',choices=['context','context-education'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'driver.py').write_bytes(Path(__file__).read_bytes())
    baseline=json.loads((ROOT/'projects/usefulcharts-style/artifacts/reviews/local-stories-v31/publishing-final/source.json').read_text(encoding='utf-8'))
    data=copy.deepcopy(baseline)
    data.pop('_cohort_key',None);data['legend']=False
    data['context_panels']=[
        dict(id='workshop-roots',kind='story',box=[92,182,310,245],title='From workshops to readers',
             icon='illustration-printing-press-bookman',
             text='Two workshops combine in The Common Press in 1471. Later branches serve science, schools and public readers.'),
        dict(id='institution-counts',kind='counts',box=[1270,177,630,228],title='Institutions represented in this history')]
    if args.profile=='context-education':
        ys=dict(languages=849.43,normal=952.24,primer=1078.37,schoolatlas=1200.18,textbooks=1346.31,
                audio=1473.18,learning=1600.06,learningnet=1727.19)
        for node in data['nodes']:
            if node['id'] in ys:node['y']=ys[node['id']]
            if node['group']=='learning':node['x']+=30 if node['x']<1800 else 10
            if node['id'] in ('learning','learningnet'):node['x']=1762
            if node['id']=='audio':node['x']=1835
        for edge in data['edges']:
            for key in ('via','corridor_y','source_port','target_port'):edge.pop(key,None)
    (args.output/'draft.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    record=dict(profile=args.profile,full_source_preserved=True,source_edits='Added disclosed contextual copy and source-derived counts; all existing fact fields and type sizes are retained.')
    try:
        if args.profile=='context-education':
            data,routing=compose_influences(data,local_first=True)
            (args.output/'routing.json').write_text(json.dumps(routing,indent=2)+'\n',encoding='utf-8')
        svg,report=ContextPoster(data).render()
        (args.output/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        (args.output/'poster.svg').write_text(svg,encoding='utf-8')
        (args.output/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
        (args.output/'layout.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        record.update(status='pass',layout={k:v for k,v in report.items() if k!='resolved_layout'})
    except ValueError as error:
        record.update(status='fail',error=str(error))
    (args.output/'prototype.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record))
    return record['status']!='pass'


if __name__=='__main__':raise SystemExit(main())

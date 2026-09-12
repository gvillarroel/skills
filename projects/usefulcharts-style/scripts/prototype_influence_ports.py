#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare explicit lateral influence attachments without changing institutional facts."""

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster
from render_chart import compress, fmt, proper_cross, require, route_regions, segment_hits, viewer


def port(box, side):
    x,y,w,h=box
    position={'left':(x,y+h/2),'right':(x+w,y+h/2),'top':(x+w/2,y),'bottom':(x+w/2,y+h)}[side]
    normal={'left':(-1,0),'right':(1,0),'top':(0,-1),'bottom':(0,1)}[side]
    return position,tuple(position[k]+10*normal[k] for k in (0,1))


def score(path,segments):
    length=sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(path,path[1:]))
    crossings=sum(proper_cross(a,b,c,d) for a,b in zip(path,path[1:]) for c,d in segments)
    return length+24*(len(path)-2)+90*crossings


class LateralPoster(EditorialPoster):
    def build_routes(self):
        relations=self.relations
        self.relations=[edge for edge in relations if edge['kind']!='influence']
        super().build_routes()
        self.relations=relations
        obstacles=list(self.boxes.values())
        segments=[(a,b) for edge in self.routes for a,b in zip(edge['points'],edge['points'][1:])]
        world=(self.left-12,self.top-26,self.right+12,self.bottom+12)
        choices=[]
        for edge in relations:
            if edge['kind']!='influence':continue
            source,target=edge['source'],edge['target']
            candidates=[]
            for sp,tp in [('left','right'),('right','left'),('left','left'),('right','right'),('bottom','top')]:
                start,a=port(self.boxes[source],sp);end,b=port(self.boxes[target],tp)
                if any(x-7<p[0]<x+w+7 and y-7<p[1]<y+h+7 for p in (a,b) for x,y,w,h in obstacles):continue
                regions=[]
                for margin in (30,90,220,600,max(self.w,self.h)):
                    regions.append((max(world[0],min(a[0],b[0])-margin),max(world[1],min(a[1],b[1])-margin),
                        min(world[2],max(a[0],b[0])+margin),min(world[3],max(a[1],b[1])+margin)))
                try:path=compress([start]+route_regions(a,b,obstacles,regions,segments)+[end])
                except ValueError:continue
                if any(segment_hits(p,q,box,0) for p,q in zip(path,path[1:]) for box in obstacles):continue
                candidates.append((score(path,segments),sp,tp,path))
            require(candidates,f'No complete influence route for {edge["id"]}.')
            value,sp,tp,path=min(candidates,key=lambda result:result[0])
            edge.update(source_port=sp,target_port=tp)
            for collection in (self.data['edges'],self.source_data['edges']):
                match=next(e for e in collection if e['id']==edge['id']);match.update(source_port=sp,target_port=tp)
            group=edge.get('group',self.nodes[target]['group']);paint=self.groups[group]['color'];width=edge.get('weight',1.8)
            self.line(path,self.paper,width+2.4)
            self.line(path,paint,width,'1 5',extra=f'data-edge-id="{edge["id"]}" data-source="{source}" data-target="{target}" data-kind="influence" data-route-style="rounded" data-source-port="{sp}" data-target-port="{tp}"')
            x,y=path[-1];prev=path[-2];length=abs(x-prev[0])+abs(y-prev[1]);dx=(x-prev[0])/length;dy=(y-prev[1])/length
            points=[(x-6*dx+3*dy,y-6*dy-3*dx),(x,y),(x-6*dx-3*dy,y-6*dy+3*dx)]
            d='M '+' L '.join(f'{fmt(a)} {fmt(b)}' for a,b in points)
            self.add(f'<path d="{d}" fill="none" stroke="{paint}" stroke-width="1.5"/>')
            self.routes.append(dict(edge,points=path));segments.extend(zip(path,path[1:]))
            choices.append(dict(id=edge['id'],source_port=sp,target_port=tp,objective=value,candidate_count=len(candidates)))
        self.port_choices=choices


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    original=json.loads(args.source.read_text(encoding='utf-8'))
    poster=LateralPoster(copy.deepcopy(original));svg,report=poster.render();data=poster.source_data
    facts=lambda items:[{k:v for k,v in item.items() if k not in ('source_port','target_port')} for item in items]
    require(facts(data['edges'])==facts(original['edges']),'The route prototype changed a relationship.')
    require({k:v for k,v in data.items() if k!='edges'}=={k:v for k,v in original.items() if k!='edges'},'The route prototype changed a non-edge fact.')
    (args.output/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    (args.output/'poster.svg').write_text(svg,encoding='utf-8')
    (args.output/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
    driver=Path(__file__).read_bytes();(args.output/'driver.py').write_bytes(driver)
    report.update(source=str(args.source),driver_sha256=hashlib.sha256(driver).hexdigest(),all_facts_preserved=True,
        port_choices=poster.port_choices,scope='Project-only experiment. The unchanged canonical browser audit assumes top/bottom ports; lateral attachments need separate source-backed inspection.')
    (args.output/'prototype.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='port_choices'}))


if __name__=='__main__':main()

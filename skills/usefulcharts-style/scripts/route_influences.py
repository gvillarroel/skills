#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compose side attachments for influence in an authored institutional history."""

import argparse
import copy
import json
from pathlib import Path

from editorial_poster import EditorialPoster, attachment_port
from render_chart import compress, proper_cross, require, route_regions, segment_hits


def route_score(path,segments):
    length=sum(abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in zip(path,path[1:]))
    crossings=sum(proper_cross(a,b,c,d) for a,b in zip(path,path[1:]) for c,d in segments)
    return length+24*max(0,len(path)-2)+90*crossings


def compose_influences(source,replace_authored=False):
    """Return a complete editable brief; never mutate the supplied source."""
    require(source.get('design')=='editorial' and source.get('mode')=='lineage','Influence composition requires an editorial institutional lineage.')
    require(source.get('layout') not in ('auto','packed','cohorts'),
        'Resolve the first layout before composing influences: copy the reported node centers, measured widths and canvas into an authored brief.')
    selected={edge['id'] for edge in source.get('edges',[]) if edge['kind']=='influence' and
        (replace_authored or not any(key in edge for key in ('via','corridor_y','source_port','target_port')))}
    if not selected:return copy.deepcopy(source),dict(status='pass',selected=[],choices=[],changed=False)
    structural=copy.deepcopy(source)
    structural['edges']=[edge for edge in structural['edges'] if edge['id'] not in selected]
    poster=EditorialPoster(structural);poster.render()
    obstacles=list(poster.boxes.values())+poster.annotation_boxes
    for inset in source.get('insets',[]):obstacles.append(tuple(inset['box']))
    segments=[(a,b) for edge in poster.routes for a,b in zip(edge['points'],edge['points'][1:])]
    world=(poster.left-12,poster.top-26,poster.right+12,poster.bottom+12)
    routes={edge['id']:edge for edge in poster.routes};choices=[]
    for edge in source['edges']:
        if edge['id'] not in selected:continue
        reserved=[(a,b) for prior in routes.values() if not {edge['source'],edge['target']}&{prior['source'],prior['target']}
                  for a,b in zip(prior['points'],prior['points'][1:])]
        candidates=[]
        for sp,tp in [('left','right'),('right','left'),('left','left'),('right','right'),('bottom','top')]:
            start,a=attachment_port(poster.boxes[edge['source']],sp);end,b=attachment_port(poster.boxes[edge['target']],tp)
            if any(x-7<p[0]<x+w+7 and y-7<p[1]<y+h+7 for p in (a,b) for x,y,w,h in obstacles):continue
            regions=[(max(world[0],min(a[0],b[0])-margin),max(world[1],min(a[1],b[1])-margin),
                min(world[2],max(a[0],b[0])+margin),min(world[3],max(a[1],b[1])+margin))
                for margin in (30,90,220,600,max(poster.w,poster.h))]
            try:path=compress([start]+route_regions(a,b,obstacles,regions,segments,reserved=reserved)+[end])
            except ValueError:continue
            if any(segment_hits(p,q,box,0) for p,q in zip(path,path[1:]) for box in obstacles):continue
            candidates.append((route_score(path,segments),sp,tp,path))
        require(candidates,f'No complete influence route for {edge["id"]}; move its local group or author a corridor.')
        value,sp,tp,path=min(candidates,key=lambda result:result[0])
        routes[edge['id']]=dict(edge,source_port=sp,target_port=tp,points=path)
        segments.extend(zip(path,path[1:]));choices.append(dict(id=edge['id'],source_port=sp,target_port=tp,
            route_cost=value,candidate_count=len(candidates)))
    result=copy.deepcopy(source)
    for edge in result['edges']:
        route=routes[edge['id']]
        # Freeze structural corridors too: replay must not depend on a different
        # route order after adding the newly composed influences.
        edge.pop('corridor_y',None);edge['via']=[list(point) for point in route['points'][1:-1]]
        for key in ('source_port','target_port'):
            if key in route:edge[key]=route[key]
    _,layout=EditorialPoster(result).render()
    return result,dict(status='pass',selected=sorted(selected),choices=choices,changed=True,layout=layout,
        visual_review='Required. The route cost is a local geometric heuristic, not an aesthetic score.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--replace-authored',action='store_true',help='Recompose influences that already declare ports or corridors.')
    args=parser.parse_args()
    paths=[path.resolve() for path in (args.source,args.output,args.report)]
    require(len(set(paths))==3,'Input and output paths must be distinct.')
    result,report=compose_influences(json.loads(args.source.read_text(encoding='utf-8-sig')),args.replace_authored)
    for path,value in ((args.output,result),(args.report,report)):
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({key:value for key,value in report.items() if key!='choices'}))


if __name__=='__main__':main()

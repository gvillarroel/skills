#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate institutional context pockets and freeze the resulting corridors."""

import argparse
import copy
import json
import math
from pathlib import Path

from editorial_poster import EditorialPoster, attachment_port
from editorial_insets import CONTEXT_KINDS, inset_content
from render_chart import require, overlaps


def fit_pockets(source, radius=120):
    """Fit nearby inset pockets without moving records or changing readable type."""
    result=copy.deepcopy(source)
    baseline=copy.deepcopy(source)
    baseline['insets']=[item for item in baseline.get('insets',[]) if item.get('kind') not in CONTEXT_KINDS]
    poster=EditorialPoster(baseline);poster.graph_layout()
    occupied=list(poster.boxes.values())+poster.annotation_boxes
    occupied += [tuple(item['box']) for item in baseline['insets']]
    occupied += [tuple(cell['box']) for cell in baseline.get('_cohort_key',{}).get('cells',[])]
    for edge in baseline.get('edges',[]):
        for field,default in (('source','bottom'),('target','top')):
            _,point=attachment_port(poster.boxes[edge[field]],edge.get(field+'_port',default))
            occupied.append((point[0]-8,point[1]-8,16,16))
    changes=[]
    for index,item in enumerate(result.get('insets',[])):
        if item.get('kind') not in CONTEXT_KINDS:continue
        content=inset_content(item,result,measure_only=True)
        x,y,w,h=content['box'];before=list(item['box'])
        h=max(h,math.ceil(content['required_height']))
        require(w<=poster.w-96 and h<=poster.h-215,'The inset is larger than the printable field; choose a wider or simpler pocket without shrinking text.')
        # Exact obstacle boundaries complement the local grid, avoiding a
        # dependence on the accidental pixel phase of a narrow clear pocket.
        xs={x,48,poster.w-48-w};ys={y,130,poster.h-85-h}
        for offset in range(-radius,radius+1,10):xs.add(x+offset);ys.add(y+offset)
        for bx,by,bw,bh in occupied:
            xs.update((bx-w-6,bx+bw+6));ys.update((by-h-6,by+bh+6))
        choices=[(xx,yy,w,h) for xx in xs for yy in ys
                 if abs(xx-x)<=radius and abs(yy-y)<=radius and xx>=48 and yy>=130
                 and xx+w<=poster.w-48 and yy+h<=poster.h-85
                 and not any(overlaps((xx,yy,w,h),box,5) for box in occupied)]
        require(choices,'No clear inset pocket within 120 units; revise the proposed pocket or the surrounding composition.')
        selected=min(choices,key=lambda box:((box[0]-x)**2+(box[1]-y)**2,box[1],box[0]))
        item['box']=list(selected);occupied.append(selected)
        if item['box']!=before:changes.append(dict(id=item.get('id',f'inset-{index}'),before=before,after=item['box']))
    return result,changes


def compose_context(source, *, fit=False):
    require(source.get('design')=='editorial' and source.get('mode')=='lineage' and source.get('layout')=='authored',
            'Resolve the institutional branch composition to an authored brief before adding context insets.')
    require(not source.get('unions'), 'Institutional context composition does not reinterpret partnerships.')
    result=copy.deepcopy(source)
    adjustments=[]
    if fit:result,adjustments=fit_pockets(result)
    poster=EditorialPoster(copy.deepcopy(result));_,layout=poster.render()
    routes={edge['id']:edge for edge in poster.routes}
    for edge in result.get('edges',[]):
        edge.pop('corridor_y',None)
        edge['via']=[list(point) for point in routes[edge['id']]['points'][1:-1]]
    return result,dict(status='pass',node_count=layout['node_count'],edge_count=layout['edge_count'],canvas=layout['canvas'],
                       inset_count=len(result.get('insets',[])),pocket_adjustments=adjustments,
                       visual_review='Open the final PNG; clear pockets and exact counts do not establish visual parity.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    parser.add_argument('--fit-pockets',action='store_true',help='Measure complete inset height and search within 120 units of each proposed pocket; keep records and type unchanged.')
    args=parser.parse_args()
    require(len({p.resolve() for p in (args.source,args.output,args.report)})==3,'Source, output and report paths must be distinct.')
    result,report=compose_context(json.loads(args.source.read_text(encoding='utf-8-sig')),fit=args.fit_pockets)
    for path,data in ((args.output,result),(args.report,report)):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()

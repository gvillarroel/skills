#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Resolve local genealogical baselines from dated family units and full labels."""

import argparse
import copy
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np
import osqp
from scipy import sparse

from cohort_layout import place_cohorts, compact_cohort_defaults
from editorial_poster import EditorialPoster, measured_content, cohort_key
from render_chart import number, require, wrap, text_width
from editorial_landmarks import landmark_content


def fit_baselines(units, links, preferred, top, bottom, clearance=18):
    """Find the least-squares feasible baselines; never change family meaning."""
    require(math.isfinite(top) and math.isfinite(bottom) and bottom>top,'Use a finite positive vertical span.')
    require(math.isfinite(clearance) and clearance>=18,'Reserve at least 18 units around relationship attachments.')
    keys=sorted(units,key=lambda key:(units[key]['row'],key));index={key:i for i,key in enumerate(keys)}
    require(keys and all(math.isfinite(preferred[key]) for key in keys),'Each family unit needs a finite preferred baseline.')
    pairs={}
    for i,a in enumerate(keys):
        for b in keys[i+1:]:
            u,v=units[a],units[b]
            if u['row']==v['row']:continue
            required=[]
            for first in u['parts']:
                for second in v['parts']:
                    if min(first['right'],second['right'])+7<=max(first['left'],second['left']):continue
                    gutter=6 if 'label' in (first['kind'],second['kind']) else clearance
                    required.append(first['bottom']-second['top']+gutter)
            if required:pairs[(index[a],index[b])]=max(required)
    for a,b in links:
        require(a in units and b in units and units[a]['row']<units[b]['row'],'Family relationships must advance to a later generation.')
        # A lateral descent must leave below the whole parental unit before
        # approaching the child. A union midpoint alone underestimates this gap.
        gap=(units[a]['height']+units[b]['height'])/2+clearance
        pair=(index[a],index[b]);pairs[pair]=max(pairs.get(pair,0),gap)
    pairs=[(a,b,gap) for (a,b),gap in sorted(pairs.items())]
    earliest=[top]*len(keys)
    for a,b,gap in pairs:earliest[b]=max(earliest[b],earliest[a]+gap)
    require(max(earliest)<=bottom,f'The full genealogy needs {max(earliest)-top:.2f} vertical units; only {bottom-top:.2f} are available.')
    row=[];column=[];values=[]
    for i,(a,b,_) in enumerate(pairs):row.extend((i,i));column.extend((a,b));values.extend((-1.,1.))
    matrix=sparse.coo_matrix((values,(row,column)),shape=(len(pairs),len(keys))).tocsc()
    matrix=sparse.vstack((matrix,sparse.eye(len(keys),format='csc')),format='csc')
    lower=np.array([gap for _,_,gap in pairs]+[top]*len(keys),dtype=float)
    upper=np.array([np.inf]*len(pairs)+[bottom]*len(keys),dtype=float)
    solver=osqp.OSQP();solver.setup(P=sparse.eye(len(keys),format='csc'),q=-np.array([preferred[key] for key in keys]),
        A=matrix,l=lower,u=upper,eps_abs=1e-6,eps_rel=1e-9,max_iter=100000,polishing=True,verbose=False)
    solution=solver.solve(raise_error=True);values=solution.x
    violation=max([max(0,values[a]-values[b]+gap) for a,b,gap in pairs]+[top-min(values),max(values)-bottom,0])
    require(violation<=.001,'The baseline solver left an unresolved separation constraint.')
    return {key:float(value) for key,value in zip(keys,values)},dict(iterations=solution.info.iter,
        constraints=len(pairs),max_violation=float(violation))


def space_branches(source,date_field='birth',date_scale=None,local_labels=False,reserve_context=False):
    """Preserve records and source order while resolving an authored placement."""
    require(source.get('design')=='editorial' and source.get('mode')=='genealogy' and source.get('layout')=='cohorts',
        'Start from an editorial genealogy with layout: cohorts and explicit generations.')
    require(not any(e.get('via') or 'corridor_y' in e for e in source.get('edges',[])),
        'Remove absolute route coordinates before changing family baselines.')
    require(not source.get('insets'),'Compose fixed insets after resolving the family branches.')
    require(all(a.get('node') for a in source.get('annotations',[])),
        'Use person-anchored annotations; compose fixed annotations after resolving the family branches.')
    if date_scale is not None:require(math.isfinite(date_scale) and date_scale>=0,'Date scale must be finite and nonnegative.')
    prepared=copy.deepcopy(source)
    context={};name_widths={}
    if reserve_context:
        require('width' not in source and 'height' not in source,'Automatic context reservation measures its own canvas; omit explicit page dimensions.')
        for a in prepared.get('annotations',[]):
            if a.get('kind')!='landmark':continue
            require(a['node'] not in context,'Reserve one context landmark per person.')
            require(sum(other.get('node')==a['node'] for other in prepared['annotations'])==1,'Compose multiple captions on one person explicitly.')
            context[a['node']]=a
    if (len(prepared.get('nodes',[]))>30 or context) and 'width' not in prepared and 'height' not in prepared:
        # A medium family needs the same measured typography as a small family.
        # Explicit mural dimensions retain the user's chosen scale.
        prepared.setdefault('font_size',18)
        parents={child for union in prepared.get('unions',[]) for child in union.get('children',[])}
        parents.update(edge['target'] for edge in prepared.get('edges',[]) if edge['kind']!='influence')
        continuing={person for union in prepared.get('unions',[]) if union.get('children') for person in union['partners']}
        continuing.update(edge['source'] for edge in prepared.get('edges',[]) if edge['kind']!='influence')
        first=min(node['row'] for node in prepared['nodes'])
        for node in prepared['nodes']:
            founder=node['row']==first
            principal=node.get('emphasis') or (node['id'] in parents and node['id'] in continuing)
            node.setdefault('style','hero' if founder else 'card' if principal else 'plain')
            node.setdefault('size',22 if founder or node.get('emphasis') else prepared['font_size'])
            node.setdefault('detail_size',13)
            if node['style']!='plain':
                node.setdefault('detail_position','outside' if node.get('icon') or node.get('date_label') is not None else 'inside')
            icon=node.get('icon_width',44) if node.get('icon') else 0
            if icon:node.setdefault('icon_width',icon)
            node.setdefault('width',max(64,text_width(node['label'],node['size'],True)+14+icon,
                text_width(node.get('detail',''),node['detail_size'])+16))
        if context:
            for node in prepared['nodes']:
                if node['id'] not in context:continue
                content=landmark_content(context[node['id']],node)
                name_widths[node['id']]=node['width'];node['width']=max(node['width'],content['width'])
            def context_measure(node,width):
                names,details,height=measured_content(node,name_widths.get(node['id'],width),prepared['font_size'])
                if node['id'] in context:height+=landmark_content(context[node['id']],node)['height']+24
                return names,details,height
            prepared=compact_cohort_defaults(prepared,context_measure)
        else:prepared=compact_cohort_defaults(prepared,lambda n,w:measured_content(n,w,prepared['font_size']))
        if prepared.get('legend',True):
            key=cohort_key(prepared,prepared['width']);extra=max(0,key['height']-25)
            prepared['_cohort_key']=key
            prepared['cohort_top']+=extra;prepared['cohort_bottom']+=extra;prepared['height']+=extra
    poster=EditorialPoster(prepared);working=copy.deepcopy(poster.data)
    top=number(working.get('cohort_top',225),'cohort_top');bottom=number(working.get('cohort_bottom',poster.bottom-45),'cohort_bottom')
    nodes=place_cohorts(working,poster.node_content,poster.left,poster.right,top,bottom)
    for node in nodes:
        if node['id'] in name_widths:node['width']=name_widths[node['id']]
    by_id={n['id']:n for n in nodes};membership={};units={};dates=defaultdict(list)
    for union in working.get('unions',[]):
        key=union['id'];units[key]=dict(members=union['partners'],row=by_id[union['partners'][0]]['row'])
        for member in union['partners']:membership[member]=key
    for node in nodes:
        if node['id'] not in membership:
            key='person:'+node['id'];membership[node['id']]=key;units[key]=dict(members=[node['id']],row=node['row'])
    for key,unit in units.items():
        members=[by_id[i] for i in unit['members']]
        require(len({n['y'] for n in members})==1,'Partners require the same row_offset before baseline fitting.')
        unit.update(height=max(poster.node_content(n,n.get('width',82))[2] for n in members),center=members[0]['y'])
        unit['parts']=[]
        for node in members:
            width=node.get('width',82);height=poster.node_content(node,width)[2]
            unit['parts'].append(dict(left=node['x']-width/2,right=node['x']+width/2,top=-height/2,bottom=height/2,kind='node'))
        if len(members)==2:
            first,second=sorted(members,key=lambda n:n['x'])
            unit['parts'].append(dict(left=first['x']+first.get('width',82)/2,right=second['x']-second.get('width',82)/2,top=-2,bottom=2,kind='union'))
        known=[node[date_field] for node in members if node.get(date_field) is not None]
        require(all(type(value) in (int,float) and math.isfinite(value) for value in known),'Use numeric finite source dates; do not parse dates from formatted labels.')
        unit['date']=statistics.mean(known) if known else None
        if known:dates[unit['row']].append(unit['date'])
    annotations=copy.deepcopy(source.get('annotations',[]));moved_labels=[]
    for i,annotation in enumerate(annotations):
        require(annotation['node'] in by_id,'An annotation references an unknown person.')
        node=by_id[annotation['node']];unit=units[membership[node['id']]]
        if reserve_context and annotation.get('kind')=='landmark':
            content=landmark_content(annotation,node);width=content['width'];height=content['height']
            annotation.update(dx=0,dy=-(poster.node_content(node,node.get('width',82))[2]/2+24+height/2))
            x=node['x'];y=annotation['dy']
            unit['parts'].append(dict(left=x-width/2,right=x+width/2,top=y-height/2,bottom=y+height/2,kind='label'))
            moved_labels.append(i);continue
        if annotation.get('kind')!='pill':continue
        width=number(annotation.get('width',130),'annotation.width');size=number(annotation.get('size',13),'annotation.size')
        height=len(wrap(annotation['label'],width-10,size,True))*size*1.12+7
        if local_labels:
            annotation['dx']=max(48+width/2,min(node['x'],poster.w-48-width/2))-node['x']
            annotation['dy']=-max(35,poster.node_content(node,node.get('width',82))[2]/2+height/2+7)
            moved_labels.append(i)
        x=node['x']+annotation.get('dx',0);y=annotation.get('dy',0)
        unit['parts'].append(dict(left=x-width/2,right=x+width/2,top=y-height/2,bottom=y+height/2,kind='label'))
    known=[unit['date'] for unit in units.values() if unit['date'] is not None]
    if date_scale is None:date_scale=(bottom-top)/(max(known)-min(known)) if known and max(known)>min(known) else 0
    preferred={key:unit['center']+(unit['date']-statistics.median(dates[unit['row']]))*date_scale
        if unit['date'] is not None else unit['center'] for key,unit in units.items()}
    links={(union['id'],membership[child]) for union in working.get('unions',[]) for child in union.get('children',[])}
    links.update((edge['source'] if edge['source'] in units else membership[edge['source']],membership[edge['target']])
        for edge in working.get('edges',[]) if edge['kind']!='influence')
    positions,report=fit_baselines(units,links,preferred,top,bottom)
    for node in nodes:node['y']=round(positions[membership[node['id']]],3)
    result=copy.deepcopy(source)
    result.update(layout='authored',width=poster.w,height=poster.h,font_size=poster.font,
        nodes=[by_id[n['id']] for n in source['nodes']])
    if annotations:result['annotations']=annotations
    if '_cohort_key' in working:result['_cohort_key']=working['_cohort_key']
    report.update(status='pass',family_units=len(units),date_field=date_field,date_scale=date_scale,
        undated_units=[key for key,unit in units.items() if unit['date'] is None],moved_label_indices=moved_labels,
        shifted_units=sum(abs(positions[key]-unit['center'])>1 for key,unit in units.items()),
        max_displacement=max(abs(positions[key]-unit['center']) for key,unit in units.items()),
        reserved_context_count=len(context),
        limitation='Dates guide schematic placement, not an exact time scale. Render, audit against this resolved source, and inspect the complete poster.')
    return result,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--report',type=Path);parser.add_argument('--date-field',default='birth')
    parser.add_argument('--date-scale',type=float);parser.add_argument('--local-labels',action='store_true')
    parser.add_argument('--reserve-context',action='store_true')
    args=parser.parse_args()
    try:
        paths=[path.resolve() for path in (args.input,args.output,args.report) if path]
        require(len(paths)==len(set(paths)),'Input, resolved source and report paths must be distinct.')
        data,report=space_branches(json.loads(args.input.read_text(encoding='utf-8-sig')),args.date_field,args.date_scale,args.local_labels,args.reserve_context)
    except (ValueError,KeyError,osqp.OSQPException) as error:
        print(json.dumps(dict(status='needs-layout',message=str(error))));return 1
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='pass',units=report['family_units'],output=str(args.output))));return 0


if __name__=='__main__':raise SystemExit(main())

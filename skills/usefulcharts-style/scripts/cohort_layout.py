#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Place genealogical cohorts from declared partnerships and parentage."""

from __future__ import annotations

import copy
import math
from collections import defaultdict


def compact_cohort_defaults(data, measure):
    """Measure a small family before choosing its canvas and generation spacing."""
    result=copy.deepcopy(data)
    rows=defaultdict(list)
    partners={p for u in result.get('unions',[]) for p in u['partners']}
    for node in result['nodes']:
        if type(node.get('row')) is not int or node['row']<0:
            raise ValueError('Cohort nodes require a nonnegative integer row.')
        node.setdefault('width',138+(node.get('icon_width',44) if node.get('icon') else 0))
        node.setdefault('style','hero' if node.get('emphasis') else 'pill' if node['row']==0 else 'card' if node['id'] in partners else 'plain')
        rows[node['row']].append(node)
    gap=float(result.get('cohort_gap',30));partner_gap=float(result.get('partner_gap',24))
    widths=[]
    for row,nodes in rows.items():
        unions=sum(1 for u in result.get('unions',[]) if any(n['id']==u['partners'][0] for n in nodes))
        widths.append(sum(n['width'] for n in nodes)+unions*partner_gap+max(0,len(nodes)-unions-1)*gap)
    result.setdefault('width',max(1000,130+max(widths)))
    levels=sorted(rows)
    heights={row:max(measure(n,n['width'])[2] for n in rows[row]) for row in levels}
    weights=result.get('cohort_weights',{})
    distances=[]
    for before,after in zip(levels,levels[1:]):
        weight=float(weights.get(str(after),weights.get(after,1)))
        if not math.isfinite(weight) or weight<=0:
            raise ValueError('Cohort spacing weights must be finite and positive.')
        distances.append((heights[before]+heights[after])/2+76*weight)
    top=185+heights[levels[0]]/2
    natural_height=top+sum(distances)+heights[levels[-1]]/2+110
    result.setdefault('height',max(720,natural_height))
    result.setdefault('cohort_top',top)
    result.setdefault('cohort_bottom',result['height']-110-heights[levels[-1]]/2)
    # The packer accepts relative row weights. Include actual label heights so
    # a wrapped generation does not steal the next generation's connector gap.
    result['cohort_weights']={str(row):distance for row,distance in zip(levels[1:],distances)}
    result.setdefault('cohort_gap',gap)
    return result


def place_cohorts(data, measure, left, right, top, bottom):
    """Preserve entities/relations while allocating space to family units.

    Each node has an integer row. A partnership is one horizontal unit, not a
    person. Parent anchors determine ordering; repeated relaxation puts parents
    above their actual children and lets terminating branches release space.
    """
    nodes=copy.deepcopy(data['nodes']);by_id={n['id']:n for n in nodes}
    if len(by_id)!=len(nodes):raise ValueError('Duplicate node ID in cohort layout.')
    for n in nodes:
        if type(n.get('row')) is not int or n['row']<0:raise ValueError('Cohort nodes require a nonnegative integer row.')
    membership={};units={};parents=defaultdict(set);children=defaultdict(set)
    for u in data.get('unions',[]):
        if u['id'] in units or u['id'] in by_id:raise ValueError('Duplicate cohort union ID.')
        ids=u['partners']
        if len(ids)!=2 or len(set(ids))!=2 or any(i not in by_id for i in ids):raise ValueError('Cohort partnership requires two known, distinct people.')
        if any(i in membership for i in ids):raise ValueError('Multiple partnerships in one cohort need an authored placement or explicit identity aliases.')
        if by_id[ids[0]]['row']!=by_id[ids[1]]['row']:raise ValueError('Cohort partners must share a row.')
        units[u['id']]=dict(id=u['id'],members=ids,row=by_id[ids[0]]['row'])
        for i in ids:membership[i]=u['id']
    for n in nodes:
        if n['id'] not in membership:
            key='person:'+n['id'];membership[n['id']]=key
            units[key]=dict(id=key,members=[n['id']],row=n['row'])
    def connect(source,target):
        if source not in units or target not in by_id:raise ValueError('Cohort relation references an unknown entity.')
        child=membership[target]
        if units[source]['row']>=units[child]['row']:raise ValueError('Cohort parentage must advance to a later row.')
        parents[child].add(source);children[source].add(child)
    for u in data.get('unions',[]):
        for child in u.get('children',[]):connect(u['id'],child)
    for e in data.get('edges',[]):
        if e['kind']=='influence':continue
        source=e['source'] if e['source'] in units else membership.get(e['source'])
        connect(source,e['target'])
    rows=defaultdict(list);gap=float(data.get('cohort_gap',22));partner_gap=float(data.get('partner_gap',24))
    if not math.isfinite(gap) or gap<5 or not math.isfinite(partner_gap) or partner_gap<16:raise ValueError('Use a cohort gutter of at least 5 and a partnership gap of at least 16.')
    for u in units.values():
        widths=[float(by_id[i].get('width',82)) for i in u['members']]
        if any(not math.isfinite(w) or w<=0 for w in widths):raise ValueError('Cohort node widths must be finite and positive.')
        u['widths']=widths;u['width']=sum(widths)+(partner_gap if len(widths)==2 else 0)
        rows[u['row']].append(u['id'])
    levels=sorted(rows);center=(left+right)/2;positions={}
    def project(order,desired):
        total=sum(units[i]['width'] for i in order)+gap*(len(order)-1)
        if total>right-left:raise ValueError('A genealogical cohort exceeds page width; widen the canvas or compose that cohort explicitly.')
        xs=[]
        for j,key in enumerate(order):
            half=units[key]['width']/2
            minimum=left+half if not j else xs[-1]+units[order[j-1]]['width']/2+gap+half
            xs.append(max(minimum,desired[j]))
        for j in range(len(order)-1,-1,-1):
            half=units[order[j]]['width']/2
            maximum=right-half if j==len(order)-1 else xs[j+1]-units[order[j+1]]['width']/2-gap-half
            xs[j]=min(xs[j],maximum)
        # Translate the feasible packing toward its desired centroid. A forward
        # packing alone biases every group of siblings to the right.
        shift=sum(desired)/len(desired)-sum(xs)/len(xs)
        shift=max(left+units[order[0]]['width']/2-xs[0],min(shift,right-units[order[-1]]['width']/2-xs[-1]))
        xs=[x+shift for x in xs]
        return dict(zip(order,xs))
    for row in levels:
        keys=rows[row]
        desired={key:sum(positions[p] for p in parents[key])/len(parents[key]) if parents[key] else center for key in keys}
        keys.sort(key=lambda key:(desired[key],key))
        positions.update(project(keys,[desired[key] for key in keys]))
    for _ in range(8):
        for sequence,adjacent in ((levels[::-1],children),(levels,parents)):
            for row in sequence:
                keys=rows[row];desired=[]
                for key in keys:
                    linked=adjacent[key]
                    barycenter=sum(positions[i] for i in linked)/len(linked) if linked else positions[key]
                    desired.append(.6*barycenter+.4*positions[key])
                positions.update(project(keys,desired))
    weights=data.get('cohort_weights',{})
    intervals=[float(weights.get(str(row),weights.get(row,1))) for row in levels[1:]]
    if any(not math.isfinite(w) or w<=0 for w in intervals):raise ValueError('Cohort spacing weights must be finite and positive.')
    cumulative=[0]
    for weight in intervals:cumulative.append(cumulative[-1]+weight)
    result=[]
    for row in levels:
        y=top+(bottom-top)*cumulative[levels.index(row)]/max(1,cumulative[-1])
        for key in rows[row]:
            u=units[key];members=list(u['members'])
            # When both partners have declared parents, retain their left-to-
            # right ancestry order to reduce crossed marriage approaches.
            origins={}
            for person in members:
                origins[person]=[positions[v['id']] for v in data.get('unions',[]) if person in v.get('children',[])]
            if len(members)==2 and all(origins[i] for i in members):members.sort(key=lambda i:sum(origins[i])/len(origins[i]))
            cursor=positions[key]-u['width']/2
            for person in members:
                n=by_id[person];w=float(n.get('width',82));n['x']=round(cursor+w/2,3);n['y']=round(y+n.get('row_offset',0),3)
                # The caller measures true card height; the cohort only assigns
                # spatial centers and never changes relationships or wording.
                measure(n,w);result.append(n);cursor+=w+partner_gap
    return result


if __name__=='__main__':
    print('Use render_chart.py with genealogy layout: cohorts.')

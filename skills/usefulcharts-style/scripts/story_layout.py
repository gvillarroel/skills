#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compact relative story positions around measured records and attachment gaps."""

import copy
from render_chart import number,require


def solve_axis(nodes,dimensions,constraints,axis,available=None):
    """Use an ordered constraint graph, then place each center within its slack."""
    ordered=sorted(nodes,key=lambda n:(n[axis],n['id']))
    incoming={n['id']:{} for n in nodes};outgoing={n['id']:{} for n in nodes}
    for source,target,distance in constraints:
        incoming[target][source]=max(distance,incoming[target].get(source,0))
        outgoing[source][target]=max(distance,outgoing[source].get(target,0))
    lower={}
    for node in ordered:
        nid=node['id'];lower[nid]=max([dimensions[nid]/2]+[lower[s]+gap for s,gap in incoming[nid].items()])
    natural=max(lower[n['id']]+dimensions[n['id']]/2 for n in nodes)
    extent=natural if available is None else available
    require(extent>=natural-.01,f'The packed {axis} axis needs at least {natural:.1f} units; omit the fixed page dimension or enlarge it.')
    upper={}
    for node in reversed(ordered):
        nid=node['id'];upper[nid]=min([extent-dimensions[nid]/2]+[upper[t]-gap for t,gap in outgoing[nid].items()])
    first,last=ordered[0][axis],ordered[-1][axis];positions={}
    for node in ordered:
        nid=node['id'];lo=max([lower[nid]]+[positions[s]+gap for s,gap in incoming[nid].items()])
        preferred=extent/2 if last==first else dimensions[nid]/2+(extent-dimensions[nid])*(node[axis]-first)/(last-first)
        positions[nid]=max(lo,min(upper[nid],preferred))
    return positions,extent


def pack_stories(data,measure,top=190):
    """Treat x/y as relative composition hints; preserve facts and ordinal order."""
    result=copy.deepcopy(data);nodes=result['nodes'];ids={n['id'] for n in nodes}
    require(nodes and len(ids)==len(nodes),'Packed stories require distinct named records.')
    require(result.get('mode')=='lineage' and not result.get('unions'),'Packed stories support institutional lineages; use cohorts for partnerships.')
    require(not result.get('insets'),'Place insets with an authored layout, after compacting the story groups.')
    require(all(a.get('node') for a in result.get('annotations',[])),'Packed annotations must be anchored to a node; the category key is automatic.')
    widths={};heights={}
    for node in nodes:
        nid=node['id']
        require('x' in node and 'y' in node,f'Packed node {nid} needs relative x and y hints.')
        node['x']=number(node['x'],f'{nid}.x');node['y']=number(node['y'],f'{nid}.y')
        widths[nid]=number(node['width'],f'{nid}.width');heights[nid]=measure(node,widths[nid])[2]
    constraints={'x':[],'y':[]}
    for axis in ('x','y'):
        ordered=sorted(nodes,key=lambda n:(n[axis],n['id']))
        constraints[axis].extend((a['id'],b['id'],0) for a,b in zip(ordered,ordered[1:]))
    for i,a in enumerate(nodes):
        for b in nodes[i+1:]:
            dx,dy=abs(a['x']-b['x']),abs(a['y']-b['y'])
            require(dx or dy,f'Packed nodes {a["id"]} and {b["id"]} have identical hints; give them distinct relative positions.')
            gaps={'x':(widths[a['id']]+widths[b['id']])/2+28,'y':(heights[a['id']]+heights[b['id']])/2+34}
            axis='x' if dx/gaps['x']>dy/gaps['y'] else 'y'
            first,second=sorted((a,b),key=lambda n:(n[axis],n['id']))
            constraints[axis].append((first['id'],second['id'],gaps[axis]))
    by_id={n['id']:n for n in nodes}
    for edge in result.get('edges',[]):
        require(edge['source'] in ids and edge['target'] in ids,'Packed relationships require known records.')
        require(not edge.get('via') and 'corridor_y' not in edge,'Omit absolute routes while packing; compose them after inspecting the resolved layout.')
        if edge['kind']=='influence':continue
        source,target=by_id[edge['source']],by_id[edge['target']]
        require(source['y']<target['y'],f'Packed relationship {edge["id"]} needs its successor below its predecessor.')
        constraints['y'].append((source['id'],target['id'],(heights[source['id']]+heights[target['id']])/2+42))
    xs,natural_width=solve_axis(nodes,widths,constraints['x'],'x')
    width=result.get('width',max(1000,natural_width+130))
    xs,_=solve_axis(nodes,widths,constraints['x'],'x',width-130)
    ys,natural_height=solve_axis(nodes,heights,constraints['y'],'y')
    height=result.get('height',max(720,natural_height+top+100))
    ys,_=solve_axis(nodes,heights,constraints['y'],'y',height-top-100)
    for node in nodes:node.update(x=65+xs[node['id']],y=top+ys[node['id']])
    result.update(width=width,height=height,layout='packed')
    return result


if __name__=='__main__':print('Use render_chart.py with design: editorial, mode: lineage and layout: packed.')

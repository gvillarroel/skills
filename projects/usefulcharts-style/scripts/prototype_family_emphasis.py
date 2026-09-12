#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "shapely>=2,<3", "osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Compare complete family compositions while preserving every source record."""

import argparse
import copy
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
import space_family_branches as baselines
from editorial_poster import EditorialPoster
from place_context_landmarks import fit_landmarks, measure_graph
from editorial_landmarks import landmark_content
from render_chart import text_width, viewer


def spread_units(nodes,source,factor,left,right):
    """Spread complete partnerships; bound the expansion by the printable field."""
    by_id={n['id']:n for n in nodes};membership={};units={};rows=defaultdict(list)
    for union in source['unions']:
        units[union['id']]=[by_id[key] for key in union['partners']]
        membership.update({key:union['id'] for key in union['partners']})
    for node in nodes:
        if node['id'] not in membership:units['person:'+node['id']]=[node]
    for key,members in units.items():rows[members[0]['row']].append(key)
    evidence=[]
    for row,keys in rows.items():
        if not 1<=row<=6 or len(keys)<2:continue
        requested=1+(factor-1)*(7-row)/6
        box=lambda members:(min(n['x']-n['width']/2 for n in members),max(n['x']+n['width']/2 for n in members))
        bounds={key:box(units[key]) for key in keys}
        centers={key:sum(bounds[key])/2 for key in keys}
        center=(min(b[0] for b in bounds.values())+max(b[1] for b in bounds.values()))/2
        limits=[requested]
        for key,x in centers.items():
            half=(bounds[key][1]-bounds[key][0])/2
            if x>center:limits.append((right-half-center)/(x-center))
            elif x<center:limits.append((center-left-half)/(center-x))
        applied=max(1,min(limits))
        for key in keys:
            shift=(centers[key]-center)*(applied-1)
            for node in units[key]:node['x']=round(node['x']+shift,3)
        evidence.append(dict(row=row,requested=requested,applied=applied))
    return evidence


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='b910a022');parser.add_argument('--portrait',type=float,default=46)
    parser.add_argument('--spread',type=float,default=1);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--scope',choices=('all','founders','later'),default='all')
    parser.add_argument('--page-scale',type=float,default=1)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    name='skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.json'
    original=json.loads(subprocess.check_output(['git','show',f'{args.before}:{name}'],cwd=ROOT))
    draft=copy.deepcopy(original);draft['layout']='cohorts'
    for field in ('width','height','cohort_top','cohort_bottom'):draft[field]*=args.page_scale
    landmarks=[a for a in draft['annotations'] if a.get('kind')=='landmark']
    draft['annotations']=[a for a in draft['annotations'] if a.get('kind')!='landmark']
    emphasized=[]
    for node in draft['nodes']:
        if not node.get('icon'):continue
        assert node['role'] in ('house founder','landmark ruler')
        if args.scope=='founders' and node['row']>4:continue
        if args.scope=='later' and node['row']<=4:continue
        node['size']=15.5 if node['row']==0 else 13.3
        node['icon_width']=args.portrait+6 if node['row']==0 else args.portrait
        node['width']=max(text_width(node['label'],node['size'],True)+16+node['icon_width'],
            text_width(node['detail'],node['detail_size'])+16)
        emphasized.append(node['id'])
    ordinary=baselines.place_cohorts;expansion=[]
    def place(data,measure,left,right,top,bottom):
        nodes=ordinary(data,measure,left,right,top,bottom)
        expansion.extend(spread_units(nodes,data,args.spread,left,right))
        return nodes
    baselines.place_cohorts=place
    report=dict(before=args.before,portrait=args.portrait,spread=args.spread,scope=args.scope,page_scale=args.page_scale,emphasized=emphasized)
    try:
        resolved,spacing=baselines.space_branches(draft,date_scale=3,local_labels=True)
        stage_svg,stage_layout=EditorialPoster(resolved).render()
        (args.output/'composition-stage.svg').write_text(stage_svg,encoding='utf-8')
        (args.output/'composition-stage.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
        report['stage_only']=dict(omitted_landmarks=len(landmarks),layout=stage_layout)
        resolved['annotations'].extend(landmarks)
        (args.output/'resolved-before-context.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
        geometry,width,height=measure_graph(resolved,args.output);nodes={n['id']:n for n in resolved['nodes']}
        placement=[]
        for i,annotation in enumerate(resolved['annotations']):
            if annotation.get('kind')!='landmark':continue
            attempts=[]
            for style in ({},{'width':112,'art_position':'above'},{'width':112,'art_position':'beside'}):
                trial=copy.deepcopy(resolved);trial['annotations']=[annotation|style]
                try:
                    fitted,details=fit_landmarks(trial,geometry,nodes,width,height)
                    updated=fitted['annotations'][0];resolved['annotations'][i]=updated
                    node=nodes[updated['node']];content=landmark_content(updated,node)
                    x=node['x']+updated['dx'];y=node['y']+updated['dy'];w=content['width'];h=content['height']
                    geometry['rectangles'].append([x-w/2-3,y-h/2-3,x+w/2+3,y+h/2+3])
                    placement.append(dict(annotation=i,rejected=attempts,accepted=details['placements'][0],format=style));break
                except ValueError as error:attempts.append(dict(format=style,error=str(error)))
            else:raise ValueError(f'No readable format fits {annotation["node"]}.{annotation["field"]}; {attempts}')
        svg,layout=EditorialPoster(resolved).render()
        visual={'width','height','size','detail_size','detail_position','icon_width','x','y'}
        facts=lambda n:{k:v for k,v in n.items() if k not in visual}
        assert [facts(n) for n in original['nodes']]==[facts(n) for n in resolved['nodes']]
        assert all(original[key]==resolved[key] for key in ('unions','edges','groups','title','subtitle','source_note','reading_note'))
        annotation_facts=lambda d:[{k:v for k,v in a.items() if k not in ('dx','dy','width','art_position')} for a in d['annotations']]
        assert annotation_facts(original)==annotation_facts(resolved)
        (args.output/'source.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
        (args.output/'poster.svg').write_text(svg,encoding='utf-8')
        (args.output/'poster.html').write_text(viewer(svg,resolved['title']),encoding='utf-8')
        report.update(status='pass',spacing=spacing,placement=placement,layout=layout,expansion=expansion,all_source_facts_preserved=True)
    except (ValueError,AssertionError) as error:report.update(status='fail',error=str(error),expansion=expansion)
    (args.output/'prototype.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],error=report.get('error'),output=str(args.output),emphasized=len(emphasized))))
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())

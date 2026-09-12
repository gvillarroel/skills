#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "shapely>=2,<3", "osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Compare solid genealogical name/date groups without changing source facts."""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster
from render_chart import viewer, text_width
from space_family_branches import space_branches
from place_context_landmarks import fit_landmarks, measure_graph
from editorial_landmarks import landmark_content


def reflow(source, folder, compact_captions=False):
    landmarks=[a for a in source['annotations'] if a.get('kind')=='landmark']
    draft=copy.deepcopy(source);draft['layout']='cohorts'
    draft['annotations']=[a for a in draft['annotations'] if a.get('kind')!='landmark']
    resolved,spacing=space_branches(draft,date_scale=3,local_labels=True)
    stage,_=EditorialPoster(resolved).render()
    (folder/'composition-stage.svg').write_text(stage,encoding='utf-8')
    (folder/'composition-stage.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
    resolved['annotations'].extend(landmarks)
    (folder/'resolved-before-context.json').write_text(json.dumps(resolved,indent=2)+'\n',encoding='utf-8')
    geometry,width,height=measure_graph(resolved,folder);nodes={n['id']:n for n in resolved['nodes']}
    placements=[]
    for i,annotation in enumerate(resolved['annotations']):
        if annotation.get('kind')!='landmark':continue
        attempts=[]
        formats=[{},{'width':112,'art_position':'above'},{'width':112,'art_position':'beside'}]
        if compact_captions:
            label=nodes[annotation['node']][annotation['field']]
            width_needed=max(text_width(word,annotation['size']) for word in label.split())+20
            formats.append(dict(width=max(width_needed,annotation.get('art_size',32)+12),art_position='above'))
        for style in formats:
            trial=copy.deepcopy(resolved);trial['annotations']=[annotation|style]
            try:
                fitted,details=fit_landmarks(trial,geometry,nodes,width,height)
                updated=fitted['annotations'][0];resolved['annotations'][i]=updated
                node=nodes[updated['node']];content=landmark_content(updated,node)
                x=node['x']+updated['dx'];y=node['y']+updated['dy'];w=content['width'];h=content['height']
                geometry['rectangles'].append([x-w/2-3,y-h/2-3,x+w/2+3,y+h/2+3])
                placements.append(dict(annotation=i,rejected=attempts,accepted=details['placements'][0],format=style));break
            except ValueError as error:attempts.append(dict(format=style,error=str(error)))
        else:raise ValueError(f'No readable format fits {annotation["node"]}.{annotation["field"]}: {attempts}')
    return resolved,dict(spacing=spacing,placements=placements)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='5720173d')
    parser.add_argument('--include-portraits',action='store_true')
    parser.add_argument('--reflow',action='store_true')
    parser.add_argument('--compact-captions',action='store_true')
    parser.add_argument('--landmark-preference',nargs=3,action='append',default=[],metavar=('NODE','DX','DY'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    filename='skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.json'
    original=json.loads(subprocess.check_output(['git','show',f'{args.before}:{filename}'],cwd=ROOT))
    source=copy.deepcopy(original);changed=[]
    for node in source['nodes']:
        if node.get('style')=='plain':continue
        if node.get('icon') and not args.include_portraits:continue
        node['detail_position']='inside';changed.append(node['id'])
        if args.reflow and node.get('icon'):
            # Keep every date word beside an image, even when it is wider than
            # the name. Portrait identities remain unchanged.
            needed=max(text_width(word,node['detail_size']) for word in node['detail'].split())
            node['width']=max(node['width'],node['icon_width']+needed+16)
    for key,dx,dy in args.landmark_preference:
        matches=[a for a in source['annotations'] if a.get('kind')=='landmark' and a.get('node')==key]
        if len(matches)!=1:raise ValueError('A preference must identify exactly one existing landmark.')
        matches[0].update(dx=float(dx),dy=float(dy))
    report=dict(before=args.before,include_portraits=args.include_portraits,reflow=args.reflow,
        compact_captions=args.compact_captions,landmark_preferences=args.landmark_preference,changed_nodes=changed)
    (args.output/'draft.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
    try:
        if args.reflow:source,details=reflow(source,args.output,args.compact_captions);report.update(details)
        visual={'x','y','width','height','size','detail_size','detail_position','icon_width'}
        facts=lambda n:{k:v for k,v in n.items() if k not in visual}
        assert [facts(n) for n in original['nodes']]==[facts(n) for n in source['nodes']]
        assert all(original[key]==source[key] for key in ('unions','edges','groups','title','subtitle','source_note','reading_note'))
        annotations=lambda d:[{k:v for k,v in a.items() if k not in ('dx','dy','width','art_position')} for a in d['annotations']]
        assert annotations(original)==annotations(source)
        (args.output/'source.json').write_text(json.dumps(source,indent=2)+'\n',encoding='utf-8')
        svg,layout=EditorialPoster(source).render()
        (args.output/'poster.svg').write_text(svg,encoding='utf-8')
        (args.output/'poster.html').write_text(viewer(svg,source['title']),encoding='utf-8')
        report.update(status='pass',layout=layout,all_source_facts_preserved=True)
    except (ValueError,AssertionError) as error:report.update(status='fail',error=str(error))
    (args.output/'prototype.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],changed=len(changed),error=report.get('error'),output=str(args.output))))
    return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())

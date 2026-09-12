#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "shapely>=2,<3"]
# ///
"""Add source-bound editorial landmarks to the existing dense genealogy."""

import json
import sys
import copy
import argparse
import subprocess
from pathlib import Path


root=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(root/'skills/usefulcharts-style/scripts'))
from place_context_landmarks import measure_graph,fit_landmarks
from editorial_poster import EditorialPoster
from render_chart import viewer
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--before',default='caa49bf')
args=parser.parse_args()
source='skills/usefulcharts-style/assets/examples/usefulcharts-style/aurelian-families.json'
data=json.loads(subprocess.check_output(['git','show',f'{args.before}:{source}'],cwd=root));nodes={n['id']:n for n in data['nodes']}
artifacts=root/'projects/usefulcharts-style/artifacts'
geometry,width,height=measure_graph(data,artifacts/'data')
rejected=[];placed=[]
# These are orientation captions, not invented political events or reigns.
# Each source field stays visible verbatim and each device retains its category.
for desired,row in enumerate([6,11,17,21,27,32,36]):
    possible=[n for n in data['nodes'] if n.get('realm') and n['group']==f'g{desired}']
    for node in sorted(possible,key=lambda n:abs(n['row']-row)):
        if abs(node['row']-row)>10:continue
        a=dict(kind='landmark',node=node['id'],field='realm',width=146,size=17,
            icon='heraldry',art_size=32,art_position='beside',variant=desired,dx=-100,dy=-80,vertical_radius=170)
        trial=copy.deepcopy(data);trial['annotations']=[a]
        try:
            resolved,report=fit_landmarks(trial,geometry,nodes,width,height)
            a=resolved['annotations'][0];data['annotations'].append(a)
            placement=report['placements'][0];placement['annotation']=len(data['annotations'])-1
            placed.append(placement)
            x=node['x']+a['dx'];y=node['y']+a['dy'];w=placement['width'];h=placement['height']
            geometry['rectangles'].append([x-w/2-3,y-h/2-3,x+w/2+3,y+h/2+3])
            print(f'Placed {node["group"]}: {node["id"]}.{a["field"]}',flush=True);break
        except ValueError as error:rejected.append(dict(node=node['id'],field='realm',reason=str(error)))
    else:raise ValueError(f'No usable pocket for category {desired}')
output=artifacts/'data/landmarks-v21-resolved.json'
output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
svg,layout=EditorialPoster(data).render()
(artifacts/'svgs/landmarks-v21-aurelian-families.svg').write_text(svg,encoding='utf-8')
(artifacts/'reviews/landmarks-v21-viewer.html').write_text(viewer(svg,data['title']),encoding='utf-8')
(artifacts/'reviews/landmarks-v21-placement.json').write_text(json.dumps(dict(placements=placed,rejected=rejected,layout=layout),indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source':str(output),'landmarks':len(placed),'rejected':len(rejected)}))

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract a failed corridor and test clearance-preserving search coordinates."""

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
import render_chart
from editorial_poster import EditorialPoster


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('source',type=Path);parser.add_argument('--edge',required=True)
parser.add_argument('--before',default='b910a022');parser.add_argument('--minimize',action='store_true');args=parser.parse_args()
data=json.loads(args.source.read_text(encoding='utf-8'));data['annotations']=[]
poster=EditorialPoster(data)
try:poster.render()
except ValueError as error:print(str(error))
edge=next(e for e in poster.relations if e['id']==args.edge)
source,target=edge['source'],edge['target'];t=poster.boxes[target]
start=poster.unions[source]['point'] if source in poster.unions else (poster.boxes[source][0]+poster.boxes[source][2]/2,poster.boxes[source][1]+poster.boxes[source][3])
end=(t[0]+t[2]/2,t[1]);a=(start[0],start[1]+10);b=(end[0],end[1]-10)
world=(poster.left-12,poster.top-26,poster.right+12,poster.bottom+12)
bounds=(max(world[0],min(a[0],b[0])-90),max(world[1],min(a[1],b[1])-90),min(world[2],max(a[0],b[0])+90),min(world[3],max(a[1],b[1])+90))
nearby={key:box for key,box in poster.boxes.items() if box[0]-14<bounds[2] and box[0]+box[2]+14>bounds[0] and box[1]-14<bounds[3] and box[1]+box[3]+14>bounds[1]}
frozen=subprocess.check_output(['git','show',f'{args.before}:skills/usefulcharts-style/scripts/render_chart.py'],cwd=ROOT).decode('utf-8')
code=ast.get_source_segment(frozen,next(node for node in ast.parse(frozen).body if isinstance(node,ast.FunctionDef) and node.name=='route'))
old_namespace=vars(render_chart).copy();exec(compile(code,'<frozen-route>','exec'),old_namespace)
namespace=vars(render_chart).copy()
code=code.replace('xs.update((x - 14, x + w + 14))','xs.update((x - 8, x + w + 8, x - 14, x + w + 14))')
code=code.replace('ys.update((y - 14, y + h + 14))','ys.update((y - 8, y + h + 8, y - 14, y + h + 14))')
exec(compile(code,'<clearance-candidate>','exec'),namespace)
report=dict(before=args.before,start=a,end=b,bounds=bounds,boxes=nearby,attempts=[])
for name,route in [('original',old_namespace['route']),('clearance-grid',namespace['route'])]:
    try:report['attempts'].append(dict(name=name,status='pass',path=route(a,b,list(nearby.values()),bounds,[])))
    except ValueError as error:report['attempts'].append(dict(name=name,status='fail',error=str(error)))
if args.minimize:
    boxes=list(nearby.values())
    def succeeds(route,boxes):
        try:route(a,b,boxes,bounds,[]);return True
        except ValueError:return False
    for box in list(boxes):
        trial=[other for other in boxes if other is not box]
        if not succeeds(old_namespace['route'],trial) and succeeds(namespace['route'],trial):boxes=trial
    report['minimal_boxes']=boxes
output=args.source.parent/'corridor-investigation.json';output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))

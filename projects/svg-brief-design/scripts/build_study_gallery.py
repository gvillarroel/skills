#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==11.3.0", "numpy==2.2.6", "resvg-py==0.2.6", "scipy==1.16.2", "scikit-image==0.25.2", "defusedxml==0.7.1"]
# ///
"""Render native development outputs for review; never computes selection rewards."""
from pathlib import Path
import argparse,json,sys,textwrap
import numpy as np
from PIL import Image,ImageDraw,ImageFont

p=argparse.ArgumentParser();p.add_argument('--study',type=Path,required=True);p.add_argument('--benchmark',type=Path,required=True);p.add_argument('--generation',type=int,default=0)
args=p.parse_args()
sys.path.insert(0,str(args.benchmark/'scripts'))
from compare_svg_v1_1 import render

generation=args.study/f'search/development/generation-{args.generation:03d}'
jobs=list((generation/'harbor-jobs').iterdir())
records={r['native_task_id']:r for r in [json.loads(line) for line in (args.benchmark/'dataset-v1.1.jsonl').read_text(encoding='utf-8').splitlines()]}
byjob={}
for job in sorted(jobs):
    trials={}
    for resultfile in job.glob('*/result.json'):
        result=json.loads(resultfile.read_text());name=result['task_name']
        row=records[name];path=resultfile.parent/'artifacts'/row['output_path'].lstrip('/')
        if path.is_file():trials[name]={'artifact':path,'rewards':(result.get('verifier_result') or {}).get('rewards') or {},'error':(result.get('exception_info') or {}).get('exception_type')}
    if trials:byjob[job.name.split('-development-')[-1]]=trials
names=sorted(set(n for trials in byjob.values() for n in trials))
if not names:raise SystemExit('No native artifacts available yet')
out=generation/'review';out.mkdir(exist_ok=True)
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontfile,18);small=ImageFont.truetype(fontfile,14);title=ImageFont.truetype(fontfile,25)
columns=['reference']+list(byjob)
width=max(1050,330*len(columns));rowheight=325
sheet=Image.new('RGB',(width,125+rowheight*len(names)),'#edf2f2');draw=ImageDraw.Draw(sheet)
draw.text((22,18),'SVG Brief Design — development comparison',font=title,fill='#18383a')
draw.text((22,58),'Ground truth stays outside the skill. Scores come from preserved native Harbor trials.',font=small,fill='#486164')
cw=width/len(columns)
for col,label in enumerate(columns):draw.text((int(col*cw)+25,92),label,font=font,fill='#18383a')
rows=[]
for i,name in enumerate(names):
    row=records[name];y=120+i*rowheight
    draw.rectangle((12,y,width-12,y+rowheight-9),fill='white')
    draw.text((25,y+8),row['id']+' · '+row['family'],font=font,fill='#18383a')
    reference=args.benchmark/'datasets-v1.1/development'/name/'tests/reference.svg'
    for col,label in enumerate(columns):
        x=int(col*cw)
        item=None if label=='reference' else byjob[label].get(name)
        path=reference if label=='reference' else item['artifact'] if item else None
        if path is not None:
            try:
                ink,_=render(path.read_bytes());im=Image.fromarray(np.uint8((1-ink)*255)).convert('RGB')
                im.thumbnail((260,245));sheet.paste(im,(x+int((cw-im.width)/2),y+38))
            except Exception as exc:draw.text((x+20,y+100),type(exc).__name__,font=small,fill='#8b3131')
        if item:
            rewards=item['rewards'];score=rewards.get('visual_similarity')
            text=('ERROR: '+item['error']) if item['error'] else f"Visual {score:.3f} | Style {rewards.get('style_similarity',0):.3f}" if score is not None else 'No score'
            draw.text((x+20,y+287),text,font=small,fill='#355e55')
            rows.append({'task':row['id'],'candidate':label,'rewards':rewards,'error':item['error']})
sheet.save(out/'comparison.jpg',quality=95)
(out/'case-summary.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({'cases':len(names),'columns':columns,'comparison':str(out/'comparison.jpg')}))

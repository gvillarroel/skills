#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Extract actual current encoded reading poses and feature-demo progressions."""
import argparse
import json
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parent.parent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--id',action='append');args=parser.parse_args()
    data=json.loads((ROOT/'collection.json').read_text(encoding='utf-8'))
    for entry in data['videos']:
        if entry['role']!='current' or args.id and entry['id'] not in args.id:continue
        video=(ROOT/entry['video']).resolve();story=json.loads((ROOT/entry['story']).read_text(encoding='utf-8-sig'))
        scenes=story.get('scenes',story.get('beats'));cursor=0;poses=[]
        for scene in scenes:
            duration=scene.get('clipSeconds',scene.get('duration'));start=scene.get('start',cursor)
            for q in ([.12,.37,.62,.87,.98] if entry['id'] in ['photo-focus','focus-motion'] else [.65]):poses.append({'id':scene['id'],'at':start+duration*q})
            cursor=start+duration
        if entry['id']=='cuda':poses.extend([{'id':'gpu-original-color','at':sum(s['clipSeconds'] for s in scenes[:2])+21.0},{'id':'component-neutral-return','at':sum(s['clipSeconds'] for s in scenes[:6])+9.5}])
        poses.sort(key=lambda p:p['at']);folder=ROOT/'artifacts/polished'/entry['id'];folder.mkdir(parents=True,exist_ok=True)
        selection='+'.join('eq(n\\,'+str(round(p['at']*30))+')' for p in poses)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(video),'-vf','select='+selection,'-fps_mode','vfr',str(folder/'reading-%02d.png')],check=True)
        sheet=Image.new('RGB',(1920,((len(poses)+2)//3)*390),'white');draw=ImageDraw.Draw(sheet);font=ImageFont.load_default(size=18)
        for i,pose in enumerate(poses):
            x,y=i%3*640,i//3*390
            with Image.open(folder/f'reading-{i+1:02}.png') as im:sheet.paste(im.resize((640,360)),(x,y))
            draw.text((x+8,y+365),f"{pose['at']:.2f}s / {pose['id']}",fill='#333e48',font=font)
        sheet.save(folder/'contact.jpg',quality=95);(folder/'poses.json').write_text(json.dumps(poses,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'id':entry['id'],'scenes':len(scenes),'readingPoses':len(poses),'contact':str(folder/'contact.jpg')}),flush=True)


if __name__=='__main__':main()

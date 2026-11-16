#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3"]
# ///
"""Measure encoded content coverage before choosing conservative review limits."""
import json, subprocess
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent

def main():
 video=ROOT/'artifacts/videos/cuda-alexnet-final.mp4'
 out=ROOT/'artifacts/reviews/content-baseline';out.mkdir(parents=True,exist_ok=True)
 width,height=640,360;size=width*height*3
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-an','-sn','-vf',f'scale={width}:{height}','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 rows=[]
 while True:
  raw=proc.stdout.read(size)
  if not raw:break
  if len(raw)!=size:raise ValueError('Incomplete decoded frame')
  rgb=np.frombuffer(raw,np.uint8).reshape(height,width,3)
  gray=rgb.mean(axis=2);mask=gray<240;ys,xs=np.nonzero(mask)
  strong=gray<220
  rows.append({'frame':len(rows),'seconds':len(rows)/30,'ink240':float(mask.mean()),'ink220':float(strong.mean()),'spanX':float((xs.max()-xs.min()+1)/width) if len(xs) else 0,'spanY':float((ys.max()-ys.min()+1)/height) if len(ys) else 0})
 err=proc.stderr.read().decode();code=proc.wait()
 if code:raise ValueError(err)
 low=sorted(rows,key=lambda r:r['ink240'])[:30]
 report={'frames':len(rows),'lowestInk':low,'perScene':[]}
 timing=json.loads((ROOT/'artifacts/data/final-native-observed.json').read_text(encoding='utf-8'));start=0
 for s in timing['scenes']:
  subset=[r for r in rows if start<=r['seconds']<start+s['sceneSeconds']]
  report['perScene'].append({'id':s['id'],'minimum':min(subset,key=lambda r:r['ink240']),'medianInk':float(np.median([r['ink240'] for r in subset]))});start+=s['sceneSeconds']
 (out/'frames.json').write_text(json.dumps(rows),encoding='utf-8');(out/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(report))

if __name__=='__main__':main()

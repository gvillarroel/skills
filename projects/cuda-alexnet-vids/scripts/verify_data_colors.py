#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3"]
# ///
"""Verify the real encoded input matrix retains its grayscale data during focus."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent.parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--video',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if not a.output.resolve().is_relative_to(ROOT):p.error('Keep project color verification inside the project.')
 timing=json.loads((ROOT/'artifacts/data/final-native-observed.json').read_text(encoding='utf-8'))['scenes'];cues=json.loads((ROOT/'artifacts/data/cues.json').read_text(encoding='utf-8'))['scenes'];index=next(i for i,s in enumerate(timing) if s['id']=='alexnet-model');cue=next(c for c in cues[index]['cues'] if c['target']=='pixels');seconds=sum(s['sceneSeconds'] for s in timing[:index])+cue['at']+.15
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(a.video)]))['streams'][0];assert (probe['width'],probe['height'])==(1920,1080)
 raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(seconds),'-i',str(a.video),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);image=np.frombuffer(raw,np.uint8).reshape(1080,1920,3);cells=[]
 for row in range(5):
  for col in range(5):
   x=round(110+col*34+14.5);y=round(420+row*34+14.5);rgb=np.median(image[y-3:y+4,x-3:x+4].reshape(-1,3),axis=0);dark=row==col or row+col==4
   passed=float(np.max(rgb)-np.min(rgb))<15 and (float(rgb.mean())<170 if dark else float(rgb.mean())>200)
   cells.append({'row':row,'column':col,'expected':'dark-gray' if dark else 'light-gray','actualRgb':rgb.tolist(),'passed':passed})
 report={'ok':all(c['passed'] for c in cells),'video':str(a.video.resolve()),'scene':'alexnet-model','target':'pixels','seconds':seconds,'checkedCells':25,'passedCells':sum(c['passed'] for c in cells),'cells':cells,'scope':'Actual encoded interior colors at the spoken input-matrix focus; guide/border pixels are excluded.'};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['ok','seconds','checkedCells','passedCells']}));return 0 if report['ok'] else 2

if __name__=='__main__':raise SystemExit(main())

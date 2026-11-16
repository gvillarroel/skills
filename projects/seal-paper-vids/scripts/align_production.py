#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare exact native scene clocks and reviewed ASR phrase alternatives."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def main():
 story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'))
 durations=[35.040,29.481,32.081,32.000,39.920,39.280]
 alternatives={'En la figura uno':['En la figura 1'],'con LoRA':['con la hora'],'al veinte por ciento':['al 20'],'setenta y dos coma cinco':['72,5'],'alcanza cien':['alcanza 100'],'treinta y tres coma cinco':['33,5'],'cuarenta y siete':['47'],'cuarenta y seis coma tres':['46,3'],'cero coma siete':['0,7'],'cincuenta y nueve coma cuatro':['59,4'],'cincuenta y ocho coma dos':['58,2'],'cuarenta y nueve coma dos':['49,2'],'cuarenta y seis coma cuatro':['46,4']}
 cursor=0;timing=[];spec=[]
 for s,d in zip(story['scenes'],durations):
  timing.append({'id':s['id'],'start':cursor,'end':cursor+d,'duration':d,'observed':True,'evidence':'Actual Google Vids selected-scene announcement, milliseconds where reported.'});cursor+=d
  spec.append({'id':s['id'],'cues':[{'target':c['target'],'phrase':c['phrase'],'alternatives':alternatives.get(c['phrase'],[]),'travelSeconds':.28} for c in s['cues']]})
 data=ROOT/'artifacts/data'
 (data/'native-timing.json').write_text(json.dumps({'voice':'Nyla','nativeUrl':'https://docs.google.com/videos/d/1xE-nlSa3WwpO0CggajlAYQA09OnymGae2ch7l2DcpPA/edit','duration':cursor,'scenes':timing},indent=2)+'\n',encoding='utf-8')
 (data/'cue-spec.json').write_text(json.dumps({'scenes':spec},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 if (data/'aligned-cues.json').exists():
  aligned=json.loads((data/'aligned-cues.json').read_text(encoding='utf-8'))
  for s,d,a in zip(story['scenes'],durations,aligned['scenes']):
   s['duration']=math.ceil(d*30-1e-7)/30
   for c,v in zip(s['cues'],a['cues']):c.update(at=round(v['at'],5),audioStart=v['audioStart'],audioEnd=v['audioEnd'],timingEvidence=v['evidence'])
  (ROOT/'story.json').write_text(json.dumps(story,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'ok':True,'observedDuration':cursor,'aligned':(data/'aligned-cues.json').exists()}))
if __name__=='__main__':main()

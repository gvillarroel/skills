#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind measured native audio words to semantic cues and frame-aligned scene budgets."""
import argparse,copy,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PLUGIN=ROOT/'resources/plugin/skills'
if not PLUGIN.is_dir():PLUGIN=ROOT.parent.parent/'skills'
sys.path.insert(0,str(PLUGIN/'line-world-google-vids/scripts'))
from narration_cues import align
sys.path.insert(0,str(PLUGIN/'line-world-video/scripts'))
import video_edit as edit
def main():
 p=argparse.ArgumentParser();p.add_argument('--observed',type=Path,default=ROOT/'artifacts/data/native-observed.json');p.add_argument('--reference',type=Path,default=ROOT/'artifacts/sources/native-voice-reference.mp4');a=p.parse_args()
 story=edit.read(ROOT/'story.json');observed=edit.read(a.observed);transcript=edit.read(ROOT/'artifacts/data/transcript.json');start=0;timing=[]
 for s in observed['scenes']:
  duration=s['sceneSeconds'];timing.append({'id':s['id'],'start':start,'end':start+duration,'duration':duration});start+=duration
 spec={'scenes':[{'id':s['id'],'cues':copy.deepcopy(s['cues'])} for s in story['scenes']]}
 alternatives={('turning-point','alexnet'):['Alex Ned'],('parallel-work','threads'):['muchos siglos'],('imagenet-scale','images-count'):['1 200 000'],('two-gpus','memory'):['3 GB'],('two-gpus','training-days'):['5 y 6 días'],('training-recipe','relu'):['Relo'],('imagenet-result','winner'):['15 3'],('imagenet-result','runner-up'):['26 2'],('imagenet-result','gap'):['10 9'],('historical-impact','legacy-alexnet'):['Alex Net'],('historical-impact','legacy-convergence'):['las tres']}
 # Exact alternative spellings observed in the current native-reference ASR.
 alternatives.update({('cuda-platform','person-ian-buck'):['Ian Bock'],('imagenet-scale','person-fei-fei-li'):['Faye Faye Lee'],('imagenet-scale','person-jia-deng'):['JaDeng'],('alexnet-model','person-alex-krizhevsky'):['Alex Khrishavsky'],('alexnet-model','person-ilya-sutskever'):['Ilya Sutskaber'],('alexnet-model','person-geoffrey-hinton'):['Jeffrey Hinton']})
 alternatives[('imagenet-scale','images-count')].append('1 millón 200 mil')
 alternatives[('alexnet-model','person-alex-krizhevsky')].append('Alex Crisewski')
 alternatives[('alexnet-model','person-ilya-sutskever')].append('Ilya Suskebert')
 for block in spec['scenes']:
  for c in block['cues']:
   c['travelSeconds']=.28
   if (block['id'],c['target']) in alternatives:c['alternatives']=alternatives[(block['id'],c['target'])]
   if block['id']=='alexnet-model' and c['target'] in ['author-alex','author-ilya','author-hinton']:c['alternatives']={'author-alex':['Alex Kritschewski'],'author-ilya':['Ilya Sutskiver'],'author-hinton':['Jeffrey Hinton']}[c['target']]
 cues=align(transcript,{'scenes':timing},spec);cues['sourceVideoSha256']=edit.sha(a.reference)
 for name,data in [('cue-spec.json',spec),('voice-timing.json',{'scenes':timing}),('cues.json',cues)]:edit.atomic(ROOT/'artifacts/data'/name,edit.encode(data))
 changes=[]
 for s,measured,block in zip(story['scenes'],observed['scenes'],cues['scenes']):
  duration=math.ceil((measured['sceneSeconds']-1e-9)*30)/30
  essential=min(duration,max(c['end'] for c in block['cues'])+.35)
  changes.extend([{'file':'story','path':f'scenes[id={s["id"]}].clipSeconds','value':duration},{'file':'story','path':f'scenes[id={s["id"]}].essentialAnimationSeconds','value':essential}])
 patch={'changes':changes};edit.atomic(ROOT/'artifacts/data/measured-timing-patch.json',edit.encode(patch));receipt=edit.apply(ROOT,patch);edit.atomic(ROOT/'artifacts/manifests/timing-edit.json',edit.encode(receipt))
 print(json.dumps({'ok':True,'sceneCount':len(cues['scenes']),'cueCount':sum(len(s['cues']) for s in cues['scenes']),'measuredVoiceSceneTotal':start,'frameAlignedTotal':sum(edit.read(ROOT/'story.json')['scenes'][i]['clipSeconds'] for i in range(len(timing)))}))
if __name__=='__main__':main()

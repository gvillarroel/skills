#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare, compile and verify a measured native Google Vids scene handoff."""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path


def read(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def positive(value,label,allow_zero=False):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<(0 if allow_zero else .000001):
        raise ValueError(label+' must be a finite '+('nonnegative' if allow_zero else 'positive')+' number.')
    return float(value)


def validate_story(story):
    if not isinstance(story,dict) or not isinstance(story.get('projectTitle'),str) or not story['projectTitle'].strip():raise ValueError('projectTitle is required.')
    scenes=story.get('scenes')
    if not isinstance(scenes,list) or not scenes:raise ValueError('Provide an ordered nonempty scenes list.')
    ids=[]
    for s in scenes:
        if not isinstance(s,dict) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',s.get('id','')):raise ValueError('Each scene needs a lowercase stable ID.')
        ids.append(s['id'])
        if not isinstance(s.get('script'),str) or not s['script'].strip():raise ValueError('Each scene needs its exact narration script.')
        if len(s['script'])>2000:raise ValueError('Split this narration segment; the handoff uses a conservative 2,000-character editing budget.')
        if not s.get('clip') and not s.get('sourceClip') and not s.get('visual'):raise ValueError('Each scene needs a sourceClip/clip path or a visual brief.')
        clip=positive(s.get('clipSeconds'),'clipSeconds')
        essential=positive(s.get('essentialAnimationSeconds',0),'essentialAnimationSeconds',True)
        if essential>clip:raise ValueError('Essential animation exceeds its available clip.')
    if len(ids)!=len(set(ids)):raise ValueError('Scene IDs must be unique.')
    fps=story.get('fps',30)
    if isinstance(fps,bool) or not isinstance(fps,int) or not 1<=fps<=120:raise ValueError('fps must be an integer from 1 to 120.')
    return story


def prepare(story,output):
    story=validate_story(story);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    worksheet={'projectUrl':story.get('googleVidsUrl',''),'voice':'','measurementMethod':'native Vids voice/scene properties','scenes':[{'id':s['id'],'observed':False,'voiceoverSeconds':None,'sceneSeconds':None,'audioLeadSeconds':0,'tailSeconds':0} for s in story['scenes']]}
    target=output/'observed.json'
    if target.exists():raise ValueError('Refusing to replace existing observations; choose a fresh handoff folder.')
    write(target,worksheet)
    draft={'status':'draft-unmeasured','projectTitle':story['projectTitle'],'language':story.get('language','es'),'fps':story.get('fps',30),'sceneCount':len(story['scenes']),'scenes':[{'order':i+1,'id':s['id'],'clip':s.get('clip') or s.get('sourceClip'),'script':s['script'],'wordCount':len(s['script'].split()),'estimatedSpeechSeconds':round(len(s['script'].split())/2.4,2),'clipSeconds':s['clipSeconds'],'essentialAnimationSeconds':s.get('essentialAnimationSeconds',0)} for i,s in enumerate(story['scenes'])]}
    write(output/'insertion-plan.json',draft)
    scripts='\n\n'.join(f"SCENE {i+1:02d} / {s['id']}\n{s['script']}" for i,s in enumerate(story['scenes']))
    (output/'scripts.txt').write_text(scripts+'\n',encoding='utf-8')
    (output/'upload-checklist.md').write_text('# Native Vids insertion checklist\n\nFor each ordered ID, verify the selected scene, exact clip, exact script, consistent voice, inserted audio, measured duration and complete essential animation. Recheck scene length after adding video. Export the complete MP4 and inspect the actual file.\n',encoding='utf-8')
    return {'ok':True,'status':'draft-unmeasured','sceneCount':len(story['scenes']),'output':str(output)}


def compile_timing(story,observed):
    story=validate_story(story);fps=story.get('fps',30)
    if not isinstance(observed.get('voice'),str) or not observed['voice'].strip():raise ValueError('Record the actual native voice.')
    rows=observed.get('scenes',[])
    if len(rows)!=len(story['scenes']) or len({r.get('id') for r in rows})!=len(rows):raise ValueError('Provide exactly one observation per scene.')
    by_id={r['id']:r for r in rows}
    if set(by_id)!={s['id'] for s in story['scenes']}:raise ValueError('Observed IDs do not match the story.')
    clock=0;timeline=[]
    for s in story['scenes']:
        r=by_id[s['id']]
        if r.get('observed') is not True:raise ValueError('Unmeasured duration cannot become a release timing: '+s['id'])
        speech=positive(r.get('voiceoverSeconds'),'voiceoverSeconds')
        duration=positive(r.get('sceneSeconds'),'sceneSeconds')
        lead=positive(r.get('audioLeadSeconds',0),'audioLeadSeconds',True)
        tail=positive(r.get('tailSeconds',0),'tailSeconds',True)
        if speech+lead+tail>duration+1/fps:raise ValueError('Scene clips narration or an explicit pause: '+s['id'])
        if duration+1/fps<s.get('essentialAnimationSeconds',0):raise ValueError('Scene cuts essential animation: '+s['id'])
        if duration>s['clipSeconds']+1/fps and not r.get('extendedVisualVerified'):raise ValueError('Visual coverage is shorter than the scene: '+s['id'])
        frames=round(duration*fps)
        if abs(frames/fps-duration)>1/fps:raise ValueError('Scene duration does not fit the frame clock.')
        timeline.append({'id':s['id'],'order':len(timeline)+1,'startFrame':clock,'endFrame':clock+frames,'frames':frames,'start':clock/fps,'end':(clock+frames)/fps,'duration':frames/fps,'voiceoverSeconds':speech,'audioLeadSeconds':lead,'tailSeconds':tail,'clip':s.get('clip') or s.get('sourceClip'),'script':s['script']})
        clock+=frames
    return {'ok':True,'status':'measured-native-timing','projectTitle':story['projectTitle'],'projectUrl':observed.get('projectUrl',story.get('googleVidsUrl','')),'voice':observed['voice'],'language':story.get('language','es'),'fps':fps,'frames':clock,'duration':clock/fps,'scenes':timeline,'measurementMethod':observed.get('measurementMethod','native Vids properties')}


def verify_export(video,timing,output):
    if timing.get('status')!='measured-native-timing':raise ValueError('Verify against measured native timing, not estimates.')
    if not shutil.which('ffprobe') or not shutil.which('ffmpeg'):raise ValueError('Install FFmpeg/FFprobe before export verification.')
    video=Path(video)
    if not video.is_file() or video.stat().st_size==0:raise ValueError('The downloaded video is missing or empty.')
    probe=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],capture_output=True,text=True,check=True)
    info=json.loads(probe.stdout);streams=info['streams'];v=next((s for s in streams if s['codec_type']=='video'),None);audio=[s for s in streams if s['codec_type']=='audio']
    duration=float(info['format']['duration'])
    decoded=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
    checks={'videoPresent':v is not None,'audioPresent':bool(audio),'fullDecode':decoded.returncode==0 and not decoded.stderr.strip(),'durationMatches':abs(duration-timing['duration'])<=max(2/timing['fps'],.1)}
    report={'ok':all(checks.values()),'checks':checks,'video':str(video.resolve()),'bytes':video.stat().st_size,'duration':duration,'expectedDuration':timing['duration'],'width':v.get('width') if v else None,'height':v.get('height') if v else None,'audioStreams':len(audio),'note':'Decode and total duration do not replace listening to narration and inspecting scene joins.'}
    write(output,report);return report


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('prepare','compile'):
        q=sub.add_parser(name);q.add_argument('--story',required=True,type=Path);q.add_argument('--output',required=True,type=Path)
        if name=='compile':q.add_argument('--observed',required=True,type=Path)
    q=sub.add_parser('verify-export');q.add_argument('--video',required=True,type=Path);q.add_argument('--timing',required=True,type=Path);q.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    try:
        if a.command=='prepare':result=prepare(read(a.story),a.output)
        elif a.command=='compile':result=compile_timing(read(a.story),read(a.observed));write(a.output,result)
        else:result=verify_export(a.video,read(a.timing),a.output)
        print(json.dumps(result if a.command!='compile' else {k:v for k,v in result.items() if k!='scenes'},ensure_ascii=False));return 0 if result.get('ok') else 2
    except (ValueError,OSError,KeyError,TypeError,subprocess.CalledProcessError) as error:
        print(json.dumps({'ok':False,'error':str(error)}),file=sys.stderr);return 2


if __name__=='__main__':raise SystemExit(main())

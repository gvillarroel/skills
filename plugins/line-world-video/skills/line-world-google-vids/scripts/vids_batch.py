#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Batch a resumable native Vids handoff, measured clip preparation and selective edits."""
import argparse
import copy
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path
from batch_clips import atomic_json,inside,signature,prepare_job,materialize,sha
from vids_plan import read,validate_story,positive,compile_timing

def load(root):
    root=Path(root).resolve();story=validate_story(read(root/'story.json'));path=inside(root,'.vids/state.json')
    state=read(path) if path.is_file() else {'schemaVersion':1,'voice':story.get('voice',''),'observations':{},'confirmed':{},'clips':{}}
    return root,story,state
def voice_hash(story,state,s):return signature({'script':s['script'],'language':story.get('language','es'),'voice':story.get('voice') or state.get('voice','')})
def save(root,state):atomic_json(inside(root,'.vids/state.json'),state)
def init(root,source):
    root=Path(root).resolve();story=validate_story(read(source));target=inside(root,'story.json')
    if target.exists():raise ValueError('Project exists; use edit/build to preserve its progress.')
    for s in story['scenes']:
        for key in ('clip','sourceClip'):
            if s.get(key) and not Path(s[key]).is_absolute():s[key]=str((Path(source).resolve().parent/s[key]).resolve())
    atomic_json(target,story);return build(root,False)
def patch_story(root,patch):
    root,story,state=load(root);before=copy.deepcopy(story)
    if not isinstance(patch,dict):raise ValueError('Patch must be a JSON object.')
    allowed={'projectTitle','language','voice','scenes','order'}
    if set(patch)-allowed:raise ValueError('Edit supports title, language, voice, scenes and order; edit producer motion at its source.')
    by_id={s['id']:s for s in story['scenes']};seen=set()
    for row in patch.get('scenes',[]):
        sid=row.get('id')
        if sid not in by_id or sid in seen:raise ValueError('Patch needs unique existing scene IDs.')
        seen.add(sid)
        if set(row)-{'id','script','sourceClip','clip','visual','clipSeconds','essentialAnimationSeconds','staticHoldAfterSeconds'}:raise ValueError('Unsupported scene patch field.')
        by_id[sid].update(row)
    for key in allowed-{'scenes','order'}:
        if key in patch:story[key]=patch[key]
    if 'order' in patch:
        order=patch['order']
        if not isinstance(order,list) or len(order)!=len(by_id) or set(order)!=set(by_id):raise ValueError('order must contain every ID exactly once.')
        story['scenes']=[by_id[sid] for sid in order]
    validate_story(story)
    changed=signature(before)!=signature(story)
    if changed:
        atomic_json(inside(root,'.vids/history/'+signature(before)+'.json'),before)
        atomic_json(root/'story.json',story)
        for sid in seen:state['clips'].pop(sid,None)
        save(root,state)
        stale=inside(root,'handoff/timing.json')
        if stale.exists():stale.unlink()
    return {'ok':True,'changed':changed,'changedSceneIds':[s['id'] for s in story['scenes'] if s!=next(a for a in before['scenes'] if a['id']==s['id'])],'orderChanged':[s['id'] for s in before['scenes']]!=[s['id'] for s in story['scenes']]}
def announcements(text,story):
    found={};total=len(story['scenes'])
    for match in re.finditer(r'Scene\s+(\d+)\s+of\s+(\d+),\s*duration\s+([^\r\n]+)',text):
        order,count=int(match[1]),int(match[2]);value=match[3]
        if count!=total or not 1<=order<=total:raise ValueError('Native scene count/order does not match the story.')
        units=re.findall(r'(\d+(?:\.\d+)?)\s*(milliseconds?|minutes?|seconds?)\b',value)
        if not units:raise ValueError('No duration in native scene announcement.')
        seconds=sum(float(v)*(.001 if u.startswith('millisecond') else 60 if u.startswith('minute') else 1) for v,u in units)
        sid=story['scenes'][order-1]['id']
        if sid in found and abs(found[sid]-seconds)>1e-8:raise ValueError('Conflicting native duration announcements for '+sid)
        found[sid]=positive(seconds,'native duration')
    if not found:raise ValueError('No native scene announcements found.')
    return [{'id':sid,'observed':True,'voiceoverSeconds':v,'sceneSeconds':v,'voiceoverEvidence':'Conservative upper bound from observed scene containing its complete native voice.'} for sid,v in found.items()]
def observe(root,input_path,voice=None,from_text=False,order_verified=False,voiceovers_inserted=False):
    root,story,state=load(root)
    if from_text:
        if not order_verified or not voiceovers_inserted:raise ValueError('Text import requires verified native order and inserted voiceovers.')
        rows=announcements(Path(input_path).read_text(encoding='utf-8-sig'),story);actual_voice=voice
    else:
        data=read(input_path);rows=data['scenes'];actual_voice=voice or data.get('voice')
    if not isinstance(actual_voice,str) or not actual_voice.strip():raise ValueError('Record the observed native voice.')
    if story.get('voice') and actual_voice!=story['voice']:raise ValueError('Observed voice differs from requested voice.')
    by_id={s['id']:s for s in story['scenes']};pending={};seen=set();state=copy.deepcopy(state);state['voice']=actual_voice
    input_digest=sha(input_path);previous=state.get('observationImports',{}).get(input_digest,{})
    for row in rows:
        sid=row.get('id')
        if sid not in by_id or sid in seen:raise ValueError('Measurements need unique known stable IDs.')
        seen.add(sid)
        if row.get('observed') is not True:raise ValueError('Only observed native measurements can be imported.')
        speech=positive(row.get('voiceoverSeconds'),'voiceoverSeconds');duration=positive(row.get('sceneSeconds'),'sceneSeconds')
        lead=positive(row.get('audioLeadSeconds',0),'audioLeadSeconds',True);tail=positive(row.get('tailSeconds',0),'tailSeconds',True)
        if speech+lead+tail>duration+1e-8:raise ValueError('Measured scene cuts narration or explicit pauses: '+sid)
        fingerprint=voice_hash(story,state,by_id[sid])
        if row.get('narrationHash') and row['narrationHash']!=fingerprint:raise ValueError('Observation names an older narration: '+sid)
        if previous.get(sid) and previous[sid]!=fingerprint:raise ValueError('This observation file belongs to older narration; capture fresh native evidence: '+sid)
        pending[sid]={**row,'narrationHash':fingerprint}
    state['observations'].update(pending)
    for sid in pending:state['clips'].pop(sid,None)
    state.setdefault('observationImports',{})[input_digest]={sid:row['narrationHash'] for sid,row in pending.items()}
    save(root,state)
    stale=inside(root,'handoff/timing.json')
    if stale.exists():stale.unlink()
    return {'ok':True,'imported':list(pending),'voice':actual_voice,'measurementKind':'scene-bound' if from_text else 'supplied-native-properties'}
def current_observation(story,state,scene):
    row=state['observations'].get(scene['id'])
    return row if row and row.get('narrationHash')==voice_hash(story,state,scene) else None
def queue(root,story,state):
    jobs=[];order=[s['id'] for s in story['scenes']]
    def add(kind,sid,payload,key):jobs.append({'taskId':kind+':'+(sid or 'all')+':'+key,'kind':kind,'sceneId':sid,**payload})
    if state.get('confirmedOrder')!=signature(order):add('verify-order',None,{'order':order},signature(order))
    for index,s in enumerate(story['scenes']):
        sid=s['id'];obs=current_observation(story,state,s);nh=voice_hash(story,state,s)
        if not obs:
            add('voiceover',sid,{'order':index+1,'script':s['script'],'voice':story.get('voice') or state.get('voice',''),'next':'Generate/insert the native voice and import its measured duration.'},nh);continue
        clip=state.get('clips',{}).get(sid)
        source=Path(s.get('sourceClip',s.get('clip','')))
        if not source.is_absolute():source=root/source
        target=Path(clip['target']) if clip else None
        if not clip or clip.get('narrationHash')!=nh or not source.is_file() or sha(source)!=clip.get('sourceSha256') or not target.is_file() or sha(target)!=clip.get('sha256'):
            add('prepare-clip',sid,{'next':'Run build after rendering the source.'},nh);continue
        if state['confirmed'].get(sid)!=clip['sha256']:
            add('upload',sid,{'order':index+1,'file':clip['target'],'duration':clip['duration'],'clipSha256':clip['sha256'],'next':'Insert/replace this scene video, retain its voice, then confirm observed placement.'},clip['sha256'])
    atomic_json(inside(root,'handoff/queue.json'),{'scope':'Native UI actions require fresh observations. Local preparation does not execute them.','tasks':jobs})
    return jobs
def build(root,encode=True):
    root,story,state=load(root);pending=[s['id'] for s in story['scenes'] if not current_observation(story,state,s)];ready=[s for s in story['scenes'] if s['id'] not in pending]
    jobs=[]
    if encode and ready:
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise ValueError('Install FFmpeg/FFprobe for clip preparation.')
        # Preflight the entire ready batch before encoding any output.
        jobs=[prepare_job(root,story,s,current_observation(story,state,s)) for s in ready]
    materialized=[]
    for job in jobs:
        result=materialize(root,job);s=next(s for s in story['scenes'] if s['id']==job['id']);result['narrationHash']=voice_hash(story,state,s)
        state['clips'][job['id']]=result;materialized.append(result)
    scripts='\n\n'.join(f"SCENE {i+1:02d} / {s['id']}\n{s['script']}" for i,s in enumerate(story['scenes']))+'\n'
    path=inside(root,'handoff/scripts.txt');path.parent.mkdir(parents=True,exist_ok=True);path.write_text(scripts,encoding='utf-8')
    timing=None
    if not pending and len(materialized)==len(story['scenes']):
        resolved=copy.deepcopy(story);observed={'voice':story.get('voice') or state['voice'],'projectUrl':story.get('googleVidsUrl',''),'measurementMethod':'Imported observed native properties; scene-bound imports are explicit conservative speech bounds. Visual coverage ceiled to frames.','scenes':[]}
        for s in resolved['scenes']:
            clip=state['clips'][s['id']];s.update(clip=clip['target'],clipSeconds=clip['duration'])
            row=copy.deepcopy(current_observation(story,state,s));row['sceneSeconds']=clip['duration'];observed['scenes'].append(row)
        timing=compile_timing(resolved,observed);atomic_json(inside(root,'handoff/timing.json'),timing);atomic_json(inside(root,'handoff/resolved-story.json'),resolved);atomic_json(inside(root,'handoff/observed.json'),observed)
        state['storyHash']=signature(story)
    else:
        # Keep prior measurements in state but never expose an outdated final timeline.
        timing_path=inside(root,'handoff/timing.json')
        if not encode and not pending and state.get('storyHash')==signature(story) and timing_path.exists():timing=read(timing_path)
        elif timing_path.exists():timing_path.unlink()
    save(root,state)
    actions=queue(root,story,state)
    if timing and any(t['kind'] in ('voiceover','prepare-clip') for t in actions):
        timing=None;timing_path=inside(root,'handoff/timing.json')
        if timing_path.exists():timing_path.unlink()
    result={'ok':True,'sceneCount':len(story['scenes']),'pendingVoiceovers':pending,'preparedClips':len(materialized),'encodedClips':sum(s['operation']=='encode' for s in materialized),'copiedClips':sum(s['operation']=='copy' for s in materialized),'reusedClips':sum(s['reused'] for s in materialized),'pendingNativeActions':len(actions),'bulkVoiceEligible':len(pending)==len(story['scenes']) and bool(pending),'timingReady':timing is not None,'duration':timing['duration'] if timing else None}
    atomic_json(inside(root,'handoff/build.json'),result);return result
def confirm(root,receipt):
    root,story,state=load(root);actions=queue(root,story,state);tasks={r['taskId']:r for r in actions};pending=copy.deepcopy(state)
    if not isinstance(receipt,list) or not receipt:raise ValueError('Provide a nonempty receipt list.')
    for row in receipt:
        if row.get('observed') is not True or not isinstance(row.get('evidence'),str) or not row['evidence'].strip():raise ValueError('Confirmation needs observed=true and concrete native UI evidence.')
        task=tasks.get(row.get('taskId'))
        if not task or task['kind'] not in ('verify-order','upload'):raise ValueError('Receipt is stale or action is not confirmable; rebuild/measure first.')
        if task['kind']=='verify-order':pending['confirmedOrder']=signature(task['order'])
        else:
            target=Path(task['file'])
            if not target.is_file() or sha(target)!=task['clipSha256']:raise ValueError('Prepared clip changed since the queued upload.')
            pending['confirmed'][task['sceneId']]=task['clipSha256']
    pending.setdefault('receipts',[]).extend(receipt);save(root,pending);remaining=queue(root,story,pending)
    return {'ok':True,'confirmed':len(receipt),'pendingNativeActions':len(remaining)}

def deliver(root,video,evidence=None):
    from vids_delivery import template,finalize,safe_outputs
    root,story,state=load(root)
    actions=queue(root,story,state)
    if actions:raise ValueError('Complete the pending native queue before delivery: '+actions[0]['kind'])
    resolved=inside(root,'handoff/resolved-story.json');timing=inside(root,'handoff/timing.json')
    if not resolved.is_file() or not timing.is_file():raise ValueError('Build the current measured handoff before delivery.')
    evidence=Path(evidence).resolve() if evidence else inside(root,'handoff/delivery-evidence.json')
    if not evidence.exists():
        safe_outputs([evidence],[resolved,timing,video])
        atomic_json(evidence,template(read(resolved),resolved.parent,video))
        return {'ok':False,'status':'collect-observations','evidence':str(evidence),'next':'Fill only observed native, export, Drive playback/download and continuity fields; rerun deliver.'}
    return finalize(resolved,timing,evidence,video,inside(root,'handoff/delivery.json'))

def delivery_status(root):
    """Resumability hint; check fingerprints before calling a saved delivery ready."""
    from vids_delivery import revision
    report=inside(root,'handoff/delivery.json');resolved=inside(root,'handoff/resolved-story.json')
    if not report.is_file() or not resolved.is_file():return {'status':'awaiting-delivery','next':'Run deliver --video <native-download.mp4> to prepare or check the receipt.'}
    try:
        data=read(report);evidence=Path(data.get('evidencePath',inside(root,'handoff/delivery-evidence.json')));video=Path(data['video']);timing=inside(root,'handoff/timing.json')
        if data['revision']!=revision(read(resolved),resolved.parent) or not video.is_file() or sha(video)!=data['videoSha256'] or not evidence.is_file() or sha(evidence)!=data['evidenceSha256'] or not timing.is_file() or sha(timing)!=data.get('timingSha256'):
            return {'status':'stale-delivery','next':'Run deliver again with the current native download and observations.'}
        return {k:data[k] for k in ('status','projectUrl','videoUrl','pending')}
    except (ValueError,OSError,KeyError,TypeError):return {'status':'awaiting-delivery','next':'Run deliver to rebuild the current receipt.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('init','edit','observe','build','next','confirm','deliver'):
        q=sub.add_parser(name);q.add_argument('--project',required=True,type=Path)
        if name=='init':q.add_argument('--story',required=True,type=Path)
        if name=='edit':q.add_argument('--patch',required=True,type=Path)
        if name=='observe':
            q.add_argument('--input',required=True,type=Path);q.add_argument('--voice');q.add_argument('--announcements',action='store_true');q.add_argument('--order-verified',action='store_true');q.add_argument('--voiceovers-inserted',action='store_true')
        if name=='build':
            q.add_argument('--plan-only',action='store_true');q.add_argument('--observed',type=Path,help='Import current observed JSON and prepare all ready clips in the same call.')
        if name=='next':q.add_argument('--limit',type=int,default=3)
        if name=='confirm':q.add_argument('--receipt',required=True,type=Path)
        if name=='deliver':q.add_argument('--video',required=True,type=Path);q.add_argument('--evidence',type=Path)
    a=p.parse_args()
    try:
        if a.command=='init':result=init(a.project,a.story)
        elif a.command=='edit':result=patch_story(a.project,read(a.patch))
        elif a.command=='observe':result=observe(a.project,a.input,a.voice,a.announcements,a.order_verified,a.voiceovers_inserted)
        elif a.command=='build':
            if a.observed:observe(a.project,a.observed)
            result=build(a.project,not a.plan_only)
        elif a.command=='confirm':result=confirm(a.project,read(a.receipt))
        elif a.command=='deliver':result=deliver(a.project,a.video,a.evidence)
        else:
            root,story,state=load(a.project);tasks=queue(root,story,state);result={'ok':True,'pending':len(tasks),'tasks':tasks[:max(1,a.limit)]}
            if not tasks:result['delivery']=delivery_status(root)
        print(json.dumps(result,ensure_ascii=True));return 0 if result.get('ok') else 2
    except (ValueError,OSError,KeyError,TypeError,subprocess.CalledProcessError) as e:
        print(json.dumps({'ok':False,'error':str(e)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Preflight and cache frame-aligned upload clips; no native UI access."""
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from vids_plan import positive

VERSION=2
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def signature(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def inside(root,relative):
    path=(Path(root)/relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):raise ValueError('Generated path escapes the project: '+str(relative))
    return path
def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False,suffix='.json') as stream:
        tmp=Path(stream.name);stream.write(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
    try:os.replace(tmp,path)
    finally:
        if tmp.exists():tmp.unlink()
def probe(path):
    result=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],capture_output=True,text=True,check=True)
    info=json.loads(result.stdout);v=next((s for s in info['streams'] if s['codec_type']=='video'),None)
    if not v:raise ValueError('Source contains no video: '+str(path))
    num,den=map(float,v['r_frame_rate'].split('/'))
    return {'duration':float(v.get('duration',info['format']['duration'])),'fps':num/den,'width':v['width'],'height':v['height'],'codec':v['codec_name'],'pixelFormat':v.get('pix_fmt'),'frames':int(v.get('nb_frames',0)),'hasAudio':any(s['codec_type']=='audio' for s in info['streams'])}
def prepare_job(root,story,scene,observation):
    fps=story.get('fps',30);speech=positive(observation.get('voiceoverSeconds'),'voiceoverSeconds')
    lead=positive(observation.get('audioLeadSeconds',0),'audioLeadSeconds',True);tail=positive(observation.get('tailSeconds',0),'tailSeconds',True)
    native=positive(observation.get('sceneSeconds'),'sceneSeconds')
    # Native milliseconds are rounded upward, never shortened by frame rounding.
    frames=math.ceil(max(native,speech+lead+tail)*fps-1e-8);seconds=frames/fps
    if scene.get('essentialAnimationSeconds',0)>seconds+1e-8:raise ValueError('Essential animation exceeds measured speech budget: '+scene['id'])
    source=Path(scene.get('sourceClip',scene.get('clip','')))
    if not source.is_absolute():source=Path(root)/source
    if not source.is_file():raise ValueError('Provide the rendered sourceClip for '+scene['id'])
    info=probe(source);hold=scene.get('staticHoldAfterSeconds')
    if hold is not None:
        hold=positive(hold,'staticHoldAfterSeconds',True)
        if hold<scene.get('essentialAnimationSeconds',0):raise ValueError('Static hold begins before essential animation finishes: '+scene['id'])
        if hold>min(info['duration'],seconds)+1e-8:raise ValueError('Retiming would cut the declared motion: '+scene['id'])
    if abs(seconds-info['duration'])>1/fps*.25 and hold is None:
        raise ValueError('Declare staticHoldAfterSeconds before trimming/extending '+scene['id'])
    width=story.get('width',info['width']);height=story.get('height',info['height'])
    if (width,height)!=(info['width'],info['height']):raise ValueError('Render the requested dimensions before upload: '+scene['id'])
    source_sha=sha(source)
    key=signature({'version':VERSION,'source':source_sha,'frames':frames,'fps':fps,'width':width,'height':height,'hold':hold,'codec':'libx264','preset':'fast','crf':18})
    exact=info['codec']=='h264' and info['pixelFormat']=='yuv420p' and not info['hasAudio'] and abs(info['fps']-fps)<1e-8 and info['frames']==frames and abs(info['duration']-seconds)<=.001
    target=inside(root,'media/'+scene['id']+'.mp4')
    if source.resolve()==target:target=inside(root,'media/prepared/'+scene['id']+'.mp4')
    return {'id':scene['id'],'key':key,'source':str(source.resolve()),'sourceSha256':source_sha,'frames':frames,'duration':seconds,'fps':fps,'width':width,'height':height,'copyExact':exact,'sourceDuration':info['duration'],'target':str(target)}
def materialize(root,job):
    cache=inside(root,'.vids/cache/'+job['key']);cache.mkdir(parents=True,exist_ok=True)
    media=cache/'clip.mp4';receipt=cache/'receipt.json';reused=False
    if media.is_file() and receipt.is_file():
        try:
            record=json.loads(receipt.read_text());reused=record.get('key')==job['key'] and record.get('sha256')==sha(media)
        except (ValueError,OSError,AttributeError):reused=False
    if not reused:
        with tempfile.NamedTemporaryFile(dir=cache,delete=False,suffix='.mp4') as stream:temporary=Path(stream.name)
        try:
            if job['copyExact']:shutil.copyfile(job['source'],temporary)
            else:
                pad=max(0,job['duration']-job['sourceDuration'])+.1
                cmd=['ffmpeg','-y','-v','error','-i',job['source'],'-vf',f"fps={job['fps']},tpad=stop_mode=clone:stop_duration={pad}",'-frames:v',str(job['frames']),'-an','-sn','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(temporary)]
                subprocess.run(cmd,check=True,capture_output=True)
            info=probe(temporary)
            if info['frames']!=job['frames'] or info['hasAudio'] or (info['width'],info['height'])!=(job['width'],job['height']):raise ValueError('Encoded clip failed media checks: '+job['id'])
            os.replace(temporary,media);atomic_json(receipt,{'key':job['key'],'sha256':sha(media),'media':info})
        finally:
            if temporary.exists():temporary.unlink()
    target=Path(job['target']);target.parent.mkdir(parents=True,exist_ok=True);digest=sha(media)
    if not target.is_file() or sha(target)!=digest:
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False,suffix='.mp4') as stream:temporary=Path(stream.name)
        try:shutil.copyfile(media,temporary);os.replace(temporary,target)
        finally:
            if temporary.exists():temporary.unlink()
    return {**job,'sha256':digest,'reused':reused,'operation':'cached' if reused else 'copy' if job['copyExact'] else 'encode'}

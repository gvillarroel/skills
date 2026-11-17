#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["edge-tts>=7,<8", "numpy>=2,<3", "pillow>=11,<13"]
# ///
"""Measure real narration, bind source shots to its words and prepare conservative media crops."""
import asyncio
import hashlib
import html
import json
import math
import shutil
import subprocess
import unicodedata
import re
import wave
from pathlib import Path
import edge_tts
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parents[1]


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def normalized(text):return re.findall(r'[a-z0-9]+',''.join(c for c in unicodedata.normalize('NFKD',text.lower()) if not unicodedata.combining(c)))


def boundary(words,phrase):
    tokens=[(token,word['at']) for word in words for token in normalized(word['text'])]
    query=normalized(phrase)
    matches=[i for i in range(len(tokens)-len(query)+1) if [x[0] for x in tokens[i:i+len(query)]]==query]
    if len(matches)!=1:raise ValueError('A unique actual word boundary is required: '+phrase)
    return tokens[matches[0]][1]


async def voice(scene,settings):
    target=ROOT/'artifacts/audio'/(scene['id']+'.mp3');target.parent.mkdir(parents=True,exist_ok=True)
    record=target.with_suffix('.json');key=hashlib.sha256(json.dumps([scene['script'],settings],sort_keys=True).encode()).hexdigest()
    if record.is_file() and target.is_file():
        existing=read(record)
        if existing['key']==key and existing['sha256']==sha(target):return existing
    chunks=[];words=[]
    stream=edge_tts.Communicate(scene['script'],settings['name'],rate=settings['rate'],boundary='WordBoundary')
    async for item in stream.stream():
        if item['type']=='audio':chunks.append(item['data'])
        elif item['type']=='WordBoundary':words.append({'text':html.unescape(item['text']),'at':item['offset']/1e7,'duration':item['duration']/1e7})
    target.write_bytes(b''.join(chunks))
    decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(target),'-f','s16le','-ar','48000','-ac','1','pipe:1'])
    result={'key':key,'sha256':sha(target),'seconds':len(decoded)/96000,'words':words,'file':target.relative_to(ROOT).as_posix(),'provider':settings['provider'],'voice':settings['name'],'rate':settings['rate'],'nativeGoogleVids':False}
    save(record,result);return result


def crop(row):
    source=ROOT/row['file'];times=[.1,min(row['seconds']*.45,12),max(.1,min(row['seconds']-.15,25))];bounds=[]
    for t in times:
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(source),'-frames:v','1','-vf','scale=480:270','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        pixels=np.frombuffer(raw,np.uint8).reshape(270,480,3);active=pixels.max(axis=2)>12
        columns=np.flatnonzero(active.mean(axis=0)>.02);rows=np.flatnonzero(active.mean(axis=1)>.02)
        if not len(columns) or not len(rows):raise ValueError('Blank source crop sample: '+row['alias'])
        bounds.append([int(columns[0]),int(rows[0]),int(columns[-1]+1),int(rows[-1]+1)])
    x0=max(0,min(b[0] for b in bounds)*4-12);y0=max(0,min(b[1] for b in bounds)*4-12)
    x1=min(1920,max(b[2] for b in bounds)*4+12);y1=min(1080,max(b[3] for b in bounds)*4+12)
    return {'x':x0,'y':y0,'width':x1-x0,'height':y1-y0,'evidence':{'sampleSeconds':times,'sampleBounds480':bounds,'policy':'Union of sampled nonblack extents with 12 original pixels of safety; remove only constant source matte, preserve subject and aspect ratio.'}}


async def main():
    source=read(ROOT/'story-source.json');selected=read(ROOT/'artifacts/data/selected-clips.json');media={r['alias']:r for r in selected}
    review=ROOT/'artifacts/reviews/narration.json'
    subprocess.run(['uv','run','--script',str(REPO/'skills/line-world-video/scripts/narration_review.py'),'--story',str(ROOT/'story-source.json'),'--output',str(review)],check=True)
    crops_path=ROOT/'artifacts/data/crops.json';crops=read(crops_path) if crops_path.is_file() else {}
    for row in selected:
        if row['alias'] not in crops or crops[row['alias']].get('sourceSha256')!=row['sha256']:
            crops[row['alias']]={**crop(row),'sourceSha256':row['sha256']};save(crops_path,crops)
    story={**source,'scenes':[]};start=0;pcm=[];timing=source['timing'];fps=source['fps']
    for raw_scene in source['scenes']:
        scene=dict(raw_scene);measured=await voice(scene,source['voice'])
        decoded_source=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/measured['file']),'-f','s16le','-ar','48000','-ac','1','pipe:1'])
        samples_array=np.frombuffer(decoded_source,dtype='<i2')
        audible=np.flatnonzero(np.abs(samples_array.astype(np.int32))>33)
        boundary_end=max(w['at']+w['duration'] for w in measured['words'])
        audible_end=(int(audible[-1])+1)/48000 if len(audible) else 0
        # Retain both the last actual word boundary and audible samples, followed
        # by 220 ms. The immutable MP3 stays intact; only redundant end padding
        # is excluded from this new, unapproved voice assembly.
        kept=min(len(samples_array),math.ceil((max(boundary_end,audible_end)+.22)*48000))
        decoded=decoded_source[:kept*2]
        lead=1.0 if not story['scenes'] else timing['leadSeconds']
        scene.update(start=start,audio=measured['file'],audioLead=lead,voiceSeconds=len(decoded)/96000,sourceVoiceSeconds=measured['seconds'],trimmedTrailingPaddingSeconds=(len(decoded_source)-len(decoded))/96000,lastWordBoundaryEnd=boundary_end,lastAudibleSampleEnd=audible_end)
        scene['duration']=math.ceil((lead+scene['voiceSeconds']+timing['tailSeconds'])*fps)/fps
        scene['frames']=round(scene['duration']*fps)
        scene['cues']=[{'target':p['target'],'phrase':p['phrase'],'at':round(lead+boundary(measured['words'],p['phrase']),5),'travelSeconds':timing['guideTravelSeconds'],'evidence':scene['audio'].replace('.mp3','.json')} for p in scene['phrases']]
        if scene.get('primary'):
            previous=0;segments=[]
            for item in scene['primary']:
                end=lead+boundary(measured['words'],item['untilPhrase']) if item.get('untilPhrase') else scene['duration']
                end=round(end*fps)/fps
                if end-previous<.8:raise ValueError('A source cut is too short to read.')
                row=media[item['asset']]
                segments.append({**item,'start':previous,'end':end,'duration':end-previous,'availableSeconds':max(0,row['seconds']-item['offset']),'holdSeconds':max(0,end-previous-(row['seconds']-item['offset']))})
                previous=end
            scene['primary']=segments
        scene['panSeconds']=0 if not story['scenes'] else timing['panSeconds']
        samples=int(scene['duration']*48000+0.5);lead_samples=round(lead*48000)
        if len(decoded)//2+lead_samples>samples:raise ValueError('Speech exceeds its scene budget.')
        pcm.append(bytes(lead_samples*2)+decoded+bytes((samples-lead_samples-len(decoded)//2)*2))
        scene['end']=start+scene['duration'];start=scene['end'];story['scenes'].append(scene)
        print(json.dumps({'scene':scene['id'],'voiceSeconds':scene['voiceSeconds'],'sourceVoiceSeconds':measured['seconds'],'trimmedTrailingPaddingSeconds':scene['trimmedTrailingPaddingSeconds'],'duration':scene['duration'],'cues':len(scene['cues'])}),flush=True)
    story['duration']=start;story['frames']=sum(s['frames'] for s in story['scenes']);story['media']=media;story['crops']=crops
    folder=ROOT/'composition';folder.mkdir(exist_ok=True)
    for name,src in [('focus.js',REPO/'skills/line-world-video/assets/runtime/focus.js'),('gentle-motion.js',REPO/'skills/line-world-video/assets/runtime/gentle-motion.js'),('space-grotesk.ttf',REPO/'skills/line-world-video/assets/fonts/space-grotesk.ttf')]:shutil.copyfile(src,folder/name)
    save(ROOT/'story.json',story);(folder/'story.js').write_text('window.STORY='+json.dumps(story,ensure_ascii=False)+';\n',encoding='utf-8')
    save(ROOT/'artifacts/data/review-story.json',{'fps':fps,'width':source['width'],'height':source['height'],'scenes':[{**s,'clipSeconds':s['duration']} for s in story['scenes']]})
    voice_file=ROOT/'artifacts/audio/voice.wav'
    with wave.open(str(voice_file),'wb') as out:out.setnchannels(1);out.setsampwidth(2);out.setframerate(48000);out.writeframes(b''.join(pcm))
    save(ROOT/'artifacts/manifests/timing.json',{'duration':start,'fps':fps,'frames':story['frames'],'masterClock':'Measured decoded narration; source cuts and guide arrivals use actual Edge word boundaries.','scenes':[{k:s[k] for k in ['id','start','end','duration','audioLead','voiceSeconds','sourceVoiceSeconds','trimmedTrailingPaddingSeconds','lastWordBoundaryEnd','lastAudibleSampleEnd','cues','panSeconds']} for s in story['scenes']]})
    print(json.dumps({'ok':True,'duration':start,'frames':story['frames'],'story':str(ROOT/'story.json')}))


if __name__=='__main__':asyncio.run(main())

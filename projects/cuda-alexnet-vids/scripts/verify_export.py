#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=2,<3","scipy>=1.14,<2","pillow>=11,<13"]
# ///
"""Verify the actual native export, every frame, cue poses and original voice windows."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from scipy.signal import correlate,correlation_lags
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def pcm(path):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-vn','-sn','-f','f32le','-acodec','pcm_f32le','-ac','1','-ar','16000','pipe:1']),dtype=np.float32)
def main():
 p=argparse.ArgumentParser();p.add_argument('--video',type=Path,required=True);p.add_argument('--voice-reference',type=Path,default=ROOT/'artifacts/sources/native-voice-reference.mp4');p.add_argument('--reference-timing',type=Path,default=ROOT/'artifacts/data/native-observed.json');a=p.parse_args();video=a.video.resolve();out=ROOT/'artifacts/reviews';images=ROOT/'artifacts/screenshots/native';images.mkdir(parents=True,exist_ok=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True));v=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio');story=read(ROOT/'story.json');render=read(out/'render.json');observed=read(ROOT/'artifacts/data/final-native-observed.json');initial=read(a.reference_timing);cues=read(ROOT/'artifacts/data/cues.json');report={'ok':False,'video':str(video),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'duration':float(probe['format']['duration']),'width':v['width'],'height':v['height'],'frames':int(v['nb_frames']),'codec':v['codec_name'],'encoder':v.get('tags',{}).get('encoder',probe['format'].get('tags',{}).get('encoder')),'audioCodec':audio['codec_name'],'nativeProject':observed['projectUrl'],'voiceReference':str(a.voice_reference),'voiceReferenceSha256':hashlib.sha256(a.voice_reference.read_bytes()).hexdigest(),'checks':{}}
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-map','0:v:0','-map','0:a:0','-sn','-f','null','-'],capture_output=True,text=True);report['checks']['completeDecode']=decode.returncode==0 and not decode.stderr.strip()
 stats=ROOT/'artifacts/data/native-frame-stats.txt';subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf','scale=480:270,signalstats,metadata=mode=print:file=native-frame-stats.txt','-an','-sn','-f','null','-'],cwd=stats.parent,check=True,capture_output=True)
 minima=[];maxima=[]
 for line in stats.read_text(encoding='utf-8').splitlines():
  if line.startswith('lavfi.signalstats.YMIN='):minima.append(float(line.split('=')[1]))
  if line.startswith('lavfi.signalstats.YMAX='):maxima.append(float(line.split('=')[1]))
 report['checks']['allFrames']={'count':len(minima),'whiteFrames':[i for i,x in enumerate(minima) if x>=235],'blackFrames':[i for i,x in enumerate(maxima) if x<=24]}
 original=pcm(a.voice_reference);final=pcm(video);voice=[];before=0;after=0
 for base,current in zip(initial['scenes'],observed['scenes']):
  length=min(10,base['sceneSeconds']-2);x=original[round((before+.8)*16000):round((before+.8+length)*16000)].astype(np.float64);padded=final[max(0,round((after+.8-.25)*16000)):round((after+.8+length+.25)*16000)].astype(np.float64)
  cc=correlate(padded,x,mode='valid',method='fft');index=int(np.argmax(cc));matched=padded[index:index+len(x)];rho=float(np.dot(x,matched)/(np.linalg.norm(x)*np.linalg.norm(matched)));shift=index/16000-.25;voice.append({'id':base['id'],'correlation':rho,'localOffsetSeconds':shift,'windowSeconds':length});before+=base['sceneSeconds'];after+=current['sceneSeconds']
 report['checks']['voiceWindows']=voice;report['checks']['wholePcmIdentical']=len(original)==len(final) and original.tobytes()==final.tobytes()
 starts=[];cursor=0
 for s in observed['scenes']:starts.append(cursor);cursor+=s['sceneSeconds']
 arrivals=[]
 for i,(block,geometry) in enumerate(zip(cues['scenes'],render['scenes'])):
  for c,pose in zip(block['cues'],geometry['cues']):
   timestamp=starts[i]+c['at'];raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(timestamp),'-i',str(video),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1']);frame=np.frombuffer(raw,dtype=np.uint8).reshape(1080,1920,3);mask=(frame[:,:,0]>95)&(frame[:,:,0]<205)&(frame[:,:,1]<65)&(frame[:,:,2]>20)&(frame[:,:,2]<115);x,y=round(pose['x']),round(pose['y']);patch=mask[max(0,y-18):y+19,max(0,x-18):x+19];ys,xs=np.nonzero(patch);distance=float(np.hypot(xs-18,ys-18).min()) if len(xs) else None;arrivals.append({'scene':block['id'],'target':c['target'],'seconds':timestamp,'redNearPort':distance is not None and distance<=12,'nearestRedPixels':distance})
   if block['id']=='imagenet-result' and c['target'] in ['winner','runner-up','top-five']:Image.fromarray(frame).save(images/(c['target']+'.png'))
   if c['target'].startswith('person-'):Image.fromarray(frame).save(images/(c['target']+'.png'))
  at=starts[i]+min(geometry['duration']-1,max(2,geometry['duration']/2));target=images/f'{i+1:02d}-{block["id"]}.png';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(at),'-i',str(video),'-frames:v','1',str(target)],check=True,capture_output=True)
 report['checks']['encodedCueArrivals']=arrivals
 sheet=Image.new('RGB',(1920,1440),'white')
 for i,s in enumerate(story['scenes']):sheet.paste(Image.open(images/f'{i+1:02d}-{s["id"]}.png').resize((640,360)),((i%3)*640,(i//3)*360))
 sheet.save(images/'contact-sheet.jpg',quality=94)
 expected=sum(s['clipSeconds'] for s in story['scenes']);report['checks']['timing']={'expectedFrameBudget':expected,'actualDuration':report['duration'],'difference':report['duration']-expected,'nativeAnnouncementTotal':cursor};report['ok']=report['checks']['completeDecode'] and report['width']==1920 and report['height']==1080 and len(minima)==report['frames'] and not report['checks']['allFrames']['whiteFrames'] and not report['checks']['allFrames']['blackFrames'] and abs(report['duration']-expected)<.12 and all(s['correlation']>.985 and abs(s['localOffsetSeconds'])<.1 for s in voice) and all(s['redNearPort'] for s in arrivals)
 (out/'native-export.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'report':str(out/'native-export.json'),'duration':report['duration'],'frames':report['frames'],'whiteFrames':len(report['checks']['allFrames']['whiteFrames']),'blackFrames':len(report['checks']['allFrames']['blackFrames']),'cueArrivals':sum(s['redNearPort'] for s in arrivals),'cueCount':len(arrivals),'minimumVoiceCorrelation':min(s['correlation'] for s in voice)}));return 0 if report['ok'] else 2
if __name__=='__main__':main()

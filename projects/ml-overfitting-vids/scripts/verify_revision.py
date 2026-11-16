#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13", "numpy>=2,<3"]
# ///
"""Verify the actual revised Google Vids export against audio and visual evidence."""
import hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
def run(args):return subprocess.check_output(args)
def main():
 out=ROOT/'artifacts/revision';images=out/'native';images.mkdir(parents=True,exist_ok=True)
 video=ROOT/'artifacts/videos/ml-overfitting-google-vids-revised.mp4';original=video.with_name('ml-overfitting-google-vids-final.mp4');timing=json.loads((ROOT/'artifacts/handoff/timing.json').read_text());layout=json.loads((out/'layout-focus-audit.json').read_text(encoding='utf-8'));cues=json.loads((out/'cues.json').read_text(encoding='utf-8'))
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));samples=[]
 def frame(t,name):
  path=images/name;subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-update','1',str(path)],check=True);return Image.open(path).convert('RGB'),path
 for s in timing['scenes']:
  t=min(s['start']+12.5,s['end']-.5);im,path=frame(t,s['id']+'.png');samples.append({'id':s['id'],'time':t,'file':str(path)})
 sheet=Image.new('RGB',(1440,1080),'white')
 for i,s in enumerate(samples):sheet.paste(Image.open(s['file']).resize((480,270)),((i%3)*480,(i//3)*270))
 sheet.save(images/'contact-sheet.jpg',quality=94)
 focus=[];sequence=Image.new('RGB',(1920,360),'white')
 for j,target in enumerate(['split-train','split-validation','split-test']):
  c=next(c for c in cues['scenes'][2]['cues'] if c['target']==target);port=next(c for c in layout['plans'][2]['cues'] if c['target']==target);t=c['audioStart']+.06;im,path=frame(t,target+'.png');a=np.asarray(im);x,y=round(port['x']),round(port['y']);crop=a[y-18:y+19,x-18:x+19];red=(crop[:,:,0]>115)&(crop[:,:,0]<190)&(crop[:,:,1]<65)&(crop[:,:,2]>20)&(crop[:,:,2]<90);yy,xx=np.where(red);distance=float(np.hypot(xx.mean()-18,yy.mean()-18)) if len(xx) else None;focus.append({'target':target,'spokenStart':c['audioStart'],'inspectedAt':t,'expectedPort':{'x':x,'y':y},'redPixels':len(xx),'centerDistance':distance,'ok':len(xx)>70 and distance<7,'image':str(path)});sequence.paste(im.resize((640,360)),(j*640,0))
 sequence.save(images/'60-20-20-sequence.jpg',quality=96)
 objects=[]
 for i,target in [(3,'apply-model'),(4,'cv-large'),(7,'best-state'),(7,'training-curve'),(8,'more-data'),(10,'real-error')]:
  port=next(c for c in layout['plans'][i]['cues'] if c['target']==target);t=timing['scenes'][i]['start']+port['at']+.06;im,path=frame(t,'object-'+target+'.png');x,y=round(port['x']),round(port['y']);crop=np.asarray(im)[y-18:y+19,x-18:x+19];red=(crop[:,:,0]>115)&(crop[:,:,0]<190)&(crop[:,:,1]<65)&(crop[:,:,2]>20)&(crop[:,:,2]<90);yy,xx=np.where(red);distance=float(np.hypot(xx.mean()-18,yy.mean()-18)) if len(xx) else None;objects.append({'target':target,'inspectedAt':t,'expectedPort':{'x':x,'y':y},'redPixels':len(xx),'centerDistance':distance,'ok':len(xx)>70 and distance<7,'image':str(path)})
 bar=np.asarray(Image.open(images/'baseline.png').convert('RGB'))[350:450,280:340].mean(axis=(0,1));gray_ok=bool(np.max(np.abs(bar-np.array([105,105,105])))<5)
 def pcm(path):return run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar','16000','-f','s16le','pipe:1'])
 a,b=pcm(original),pcm(video);pa,pb=np.frombuffer(a,dtype='<i2').astype(float),np.frombuffer(b,dtype='<i2').astype(float);length=min(len(pa),len(pb));corr=float(np.corrcoef(pa[:length],pb[:length])[0,1]);tail=pa[length:] if len(pa)>len(pb) else pb[length:];shared=a[:length*2]==b[:length*2];padding_only=shared and len(tail)<=1600 and (not len(tail) or np.max(np.abs(tail))==0);audio={'decodedSamplesOriginal':len(pa),'decodedSamplesRevised':len(pb),'samePcmBytes':a==b,'sharedPcmBytesIdentical':shared,'trailingPaddingSamples':len(tail),'trailingPaddingPeak':float(np.max(np.abs(tail))) if len(tail) else 0,'trailingSilentPaddingOnly':bool(padding_only),'correlation':corr,'ok':bool(padding_only)}
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-an','-sn','-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);count=0;blank=[];black=[]
 while True:
  raw=proc.stdout.read(14400)
  if not raw:break
  if len(raw)!=14400:raise ValueError('Incomplete decoded frame.')
  pixels=np.frombuffer(raw,dtype=np.uint8)
  if np.mean(pixels<245)<.0005:blank.append(count)
  if np.mean(pixels>10)<.001:black.append(count)
  count+=1
 error=proc.stderr.read().decode();code=proc.wait()
 if code:raise ValueError(error)
 v=next(s for s in probe['streams'] if s['codec_type']=='video');report={'ok':layout['ok'] and gray_ok and all(f['ok'] for f in focus) and audio['ok'] and not blank and not black,'nativeGoogleVidsExport':str(video),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'encoder':probe['format'].get('tags',{}).get('encoder'),'width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'duration':float(probe['format']['duration']),'decodedFrames':count,'blankFrames':blank,'blackFrames':black,'sourceReadingLayoutAudit':layout['ok'],'sourceCueCount':sum(len(s['cues']) for s in cues['scenes']),'sourceGuideTextCollisions':len(layout['pointerCollisions']),'secondaryBarMeanRGB':bar.tolist(),'secondaryBarGrayCorrect':gray_ok,'voicePreservation':audio,'spokenPercentageFocus':focus,'samples':samples,'scope':'All native frames decoded at thumbnail size; full-size scene samples, three percentage cue ports and secondary gray sampled. Source vector audit covers settled reading frames and all post-pan guide poses. ASR word boundaries remain approximate.'}
 report['scope']='All native frames decoded at thumbnail size; full-size scene samples, three percentage cue ports, six other semantic ports and secondary gray sampled. Source audit covers all twelve reading states and every 30 fps guide pose, including pans and the summary zoom. ASR word boundaries remain approximate.'
 report['importantObjectFocus']=objects;report['sourceCueArrivalMismatches']=layout.get('cueArrivalMismatches',[]);report['readingSceneImportantMarkPortsClear']=layout.get('readingSceneImportantMarkPortsClear',False);report['ok']=report['ok'] and all(o['ok'] for o in objects) and not report['sourceCueArrivalMismatches'] and report['readingSceneImportantMarkPortsClear']
 (out/'native-verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['samples','spokenPercentageFocus','importantObjectFocus']}));return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())

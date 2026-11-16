#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11,<13"]
# ///
"""Inspect every native video frame for blank flashes and sample each scene."""
import json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
video=ROOT/'artifacts/videos/ml-overfitting-google-vids-final.mp4';reviews=ROOT/'artifacts/reviews';reviews.mkdir(parents=True,exist_ok=True)
timing=json.loads((ROOT/'artifacts/handoff/timing.json').read_text());images=ROOT/'artifacts/images/native';images.mkdir(parents=True,exist_ok=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-an','-sn','-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
count=0;blank=[];black=[];minimum=(1,0)
while True:
    frame=proc.stdout.read(160*90)
    if not frame:break
    if len(frame)!=160*90:raise ValueError('Incomplete decoded thumbnail frame.')
    ink=sum(p<245 for p in frame)/len(frame)
    if ink<minimum[0]:minimum=(ink,count)
    if ink<.0005:blank.append(count)
    if sum(p>10 for p in frame)<len(frame)*.001:black.append(count)
    count+=1
err=proc.stderr.read().decode();code=proc.wait()
if code:raise ValueError(err)
samples=[]
for s in timing['scenes']:
    t=min(s['start']+12.5,s['end']-.5);path=images/(s['id']+'.png')
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-update','1',str(path)],check=True)
    samples.append({'id':s['id'],'time':t,'file':str(path)})
sheet=Image.new('RGB',(1440,1080),'white')
for i,s in enumerate(samples):sheet.paste(Image.open(s['file']).resize((480,270)),((i%3)*480,(i//3)*270))
sheet.save(images/'native-contact-sheet.jpg',quality=94)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-map','0:s:0',str(reviews/'native-captions.srt')],check=True)
report={'ok':not blank and not black,'nativeExport':str(video),'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'nativeEncoderTag':probe['format']['tags'].get('encoder'),'allDecodedFrames':count,'blankFrames':blank,'blackFrames':black,'minimumInkFraction':minimum[0],'minimumInkFrame':minimum[1],'nativeDuration':float(probe['format']['duration']),'plannedDuration':timing['duration'],'durationDelta':float(probe['format']['duration'])-timing['duration'],'samples':samples,'contactSheet':str(images/'native-contact-sheet.jpg'),'checksScope':'All low-resolution decoded frames checked for missing visual content; full-resolution scene samples retained for manual inspection. ASR and captions are separate evidence.'}
(reviews/'native-frame-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='samples'}))

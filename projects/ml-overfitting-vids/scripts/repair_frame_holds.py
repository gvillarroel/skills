#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Ceil native millisecond extents to frame boundaries without clipping speech."""
import json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
observed=[20.440,22.600,20.681,21.600,22,21.080,25.800,20.240,22.321,21.699,22.400,24.899]
story=json.loads((ROOT/'story.json').read_text(encoding='utf-8-sig'))
worksheet=json.loads((ROOT/'artifacts/handoff/observed.json').read_text(encoding='utf-8-sig'))
worksheet['measurementMethod']='Native scene selection announcements with millisecond resolution, followed by video hold ceiling to the next 30 fps frame. VoiceoverSeconds records a conservative bound from the observed native scene containing the complete generated voice, not an isolated waveform measurement.'
receipt=[]
for i,(s,native) in enumerate(zip(story['scenes'],observed)):
    frames=math.ceil(native*30-1e-8);duration=frames/30;source=Path(s['clip'])
    if duration>s['clipSeconds']+1e-6:
        target=source.with_name(source.stem+'-f30.mp4')
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-vf','tpad=stop_mode=clone:stop_duration=0.2','-frames:v',str(frames),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
        s['clip']=str(target.resolve());s['clipSeconds']=duration
        receipt.append({'scene':i+1,'id':s['id'],'file':target.name,'frames':frames,'duration':duration,'observedNativeExtent':native})
    worksheet['scenes'][i].update(observed=True,voiceoverSeconds=native,sceneSeconds=duration,nativeSceneBeforeFrameRepair=native,voiceoverEvidence='upper bound from native scene extent; complete voice remains inserted')
(ROOT/'story.json').write_text(json.dumps(story,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(ROOT/'artifacts/handoff/observed.json').write_text(json.dumps(worksheet,indent=2)+'\n',encoding='utf-8')
(ROOT/'artifacts/handoff/frame-repair.json').write_text(json.dumps({'nativeExtents':observed,'replacements':receipt},indent=2)+'\n')
print(json.dumps({'ok':True,'replacements':receipt,'expectedFrames':sum(round(r['sceneSeconds']*30) for r in worksheet['scenes']),'duration':sum(r['sceneSeconds'] for r in worksheet['scenes'])}))

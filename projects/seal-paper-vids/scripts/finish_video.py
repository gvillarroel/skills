#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compose reviewed paper clips with the actual native Google Vids voice export."""
import hashlib,json,subprocess,wave
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'));native=json.loads((ROOT/'artifacts/data/native-timing.json').read_text())
 videos=ROOT/'artifacts/videos';clips=videos/'clips';work=ROOT/'artifacts/data';source=videos/'native-voice-reference.mp4'
 pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-map','0:a:0','-f','s16le','-acodec','pcm_s16le','-ar','44100','-ac','2','pipe:1'])
 rate=44100;stride=4;parts=[];receipts=[];recovered=[]
 for i,(s,n) in enumerate(zip(story['scenes'],native['scenes'])):
  first=round(n['start']*rate)*stride;last=round(n['end']*rate)*stride if i<len(story['scenes'])-1 else len(pcm)
  voice=pcm[first:last];frames=round(s['duration']*30);samples=frames*1470;target=samples*stride
  if len(voice)>target:raise ValueError('The measured voice exceeds its frame-rounded scene.')
  recovered.append(voice);parts.append(voice+bytes(target-len(voice)))
  receipts.append({'id':s['id'],'nativeStart':n['start'],'nativeEnd':n['end'],'videoFrames':frames,'duration':frames/30,'sourceSamples':len(voice)//stride,'paddingSamples':(target-len(voice))//stride})
 if b''.join(recovered)!=pcm:raise ValueError('The native voice partition dropped or duplicated samples.')
 with wave.open(str(work/'narration.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes(b''.join(parts))
 clip_paths=[(clips/f'{i+1:02}-{s["id"]}.mp4').resolve() for i,s in enumerate(story['scenes'])]
 if not all(p.is_file() for p in clip_paths):raise ValueError('Every current scene clip is required.')
 (work/'concat.txt').write_text(''.join("file '"+p.as_posix()+"'\n" for p in clip_paths),encoding='utf-8')
 output=videos/'seal-paper-final.mp4'
 command=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(work/'concat.txt'),'-i',str(work/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(sum(s['duration'] for s in story['scenes'])),'-movflags','+faststart','-metadata','comment=Original SEAL paper 2506.10943v2, CC BY 4.0, Zweiger et al. Original page captures with added Spanish narration, focus overlays and derived charts. Voice generated in Google Vids; final assembly local.',str(output)]
 subprocess.run(command,check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]))
 subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
 receipt={'ok':True,'video':str(output),'sha256':sha(output.read_bytes()),'sourceVoiceVideoSha256':sha(source.read_bytes()),'nativeVoicePcmSha256':sha(pcm),'allNativeVoiceSamplesPreservedBeforeFinalEncoding':True,'scenes':receipts,'probe':probe,'provenance':'Native Google Vids Nyla voice reference and original PDF browser-captured visuals; local comparison assembly. The current native editor export is verified separately.'}
 (ROOT/'artifacts/reviews/delivery.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'ok':True,'video':str(output),'frames':sum(r['videoFrames'] for r in receipts),'duration':probe['format']['duration'],'allNativeVoiceSamplesPreserved':True}))
if __name__=='__main__':main()

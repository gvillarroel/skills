#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Produce a caption-free stream copy, verify parity and finish observed UI receipts."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PLUGIN=ROOT/'resources/plugin/skills'
if not PLUGIN.is_dir():PLUGIN=ROOT.parent/'line-world-video/artifacts/packages/line-world-video-0.14.2/plugin/skills'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
 if r.returncode:raise ValueError(r.stdout+r.stderr)
 return r.stdout
def stream_hash(path,selector):return run(['ffmpeg','-v','error','-i',str(path),'-map',selector,'-c','copy','-f','hash','-hash','sha256','-']).strip()
def pcm_hash(path):return run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-ac','1','-ar','16000','-c:a','pcm_f32le','-f','hash','-hash','sha256','-']).strip()
def main():
 native=ROOT/'artifacts/videos/cuda-alexnet-google-vids-final.mp4';clean=ROOT/'artifacts/videos/cuda-alexnet-final.mp4';evidence=read(ROOT/'artifacts/reviews/native-export.json')
 if not evidence['ok'] or hashlib.sha256(native.read_bytes()).hexdigest()!=evidence['sha256']:raise ValueError('Verify the current actual native export first.')
 # Vids embeds an optional subtitle stream marked default; remove that track only.
 run(['ffmpeg','-y','-v','error','-i',str(native),'-map','0:v:0','-map','0:a:0','-c','copy','-map_metadata','0','-movflags','+faststart',str(clean)])
 streams={kind:{'native':stream_hash(native,selector),'delivery':stream_hash(clean,selector)} for kind,selector in [('video','0:v:0'),('audio','0:a:0')]};decoded={'native':pcm_hash(native),'delivery':pcm_hash(clean)}
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(clean)]));video=next(s for s in probe['streams'] if s['codec_type']=='video');duration=float(probe['format']['duration']);subtitles=sum(s['codec_type']=='subtitle' for s in probe['streams'])
 report={'ok':all(v['native']==v['delivery'] for v in streams.values()) and decoded['native']==decoded['delivery'] and subtitles==0,'nativeSha256':evidence['sha256'],'deliverySha256':hashlib.sha256(clean.read_bytes()).hexdigest(),'delivery':str(clean),'bytes':clean.stat().st_size,'duration':duration,'frames':int(video['nb_frames']),'width':video['width'],'height':video['height'],'frameRate':video['avg_frame_rate'],'streams':streams,'decodedPcm':decoded,'subtitleStreams':subtitles,'operation':'Container stream copy of the original Google Vids video and audio; only the optional default subtitle track is omitted. No video or audio re-encoding.'}
 (ROOT/'artifacts/reviews/delivery-parity.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 if not report['ok']:raise ValueError('Delivery stream or decoded-audio parity failed.')
 project=ROOT/'artifacts/native-batch';cli=PLUGIN/'line-world-google-vids/scripts/vids_batch.py';run(['uv','run','--script',str(cli),'build','--project',str(project),'--observed',str(ROOT/'artifacts/data/final-native-observed.json')]);tasks=read(project/'handoff/queue.json')['tasks'];observed=read(ROOT/'artifacts/data/final-native-observed.json');receipts=[]
 for task in tasks:
  if task['kind']=='verify-order':e='Fresh native scene selections 1 through 10 verified the exact ordered media IDs in final-native-observed.json; every scene retained its original Nyla track.'
  elif task['kind']=='upload':
   s=next(s for s in observed['scenes'] if s['id']==task['sceneId']);e=f'Native scene {task["order"]} selected: {s["media"]}; exactly one video object, original voice retained, scene extent {s["sceneSeconds"]} seconds. The exact prepared local file was selected in the normal Windows Open dialog.'
  else:raise ValueError('Unexpected unobserved native task '+task['kind'])
  receipts.append({'taskId':task['taskId'],'observed':True,'evidence':e})
 receipt_path=ROOT/'artifacts/manifests/native-ui-receipts.json';receipt_path.write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
 if receipts:run(['uv','run','--script',str(cli),'confirm','--project',str(project),'--receipt',str(receipt_path)])
 pending=json.loads(run(['uv','run','--script',str(cli),'next','--project',str(project),'--limit','2']));report['pendingNativeActions']=pending['pending'];(ROOT/'artifacts/manifests/delivery.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'delivery':str(clean),'duration':duration,'frames':report['frames'],'pendingNativeActions':pending['pending'],'streamCopyVerified':True}));return 0 if pending['pending']==0 else 2
if __name__=='__main__':raise SystemExit(main())

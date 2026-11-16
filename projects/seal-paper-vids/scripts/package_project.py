#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package this reviewed project with its exact reusable paper-video runtime."""
import hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent;REPO=ROOT.parent.parent;VERSION='0.17.0'
def main():
 packages=ROOT/'artifacts/packages';packages.mkdir(exist_ok=True);staging=packages/f'seal-paper-editable-{VERSION}'
 if staging.exists():raise ValueError('Preserve immutable source packages; choose a new package version.')
 staging.mkdir();files=[]
 def add(source,relative):
  dest=staging/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 for name in ['story.json','production.md']:add(ROOT/name,name)
 for name in ['finish_video.py','review_delivery.py','align_production.py','transcribe_native.py','revise_motion.py']:add(ROOT/'scripts'/name,'scripts/'+name)
 for root in ['artifacts/composition','artifacts/videos']:
  for p in (ROOT/root).rglob('*'):
   if p.is_file() and p.name!='seal-google-vids-before-pan.mp4':add(p,p.relative_to(ROOT))
 for name in ['native-timing.json','transcript.json','aligned-cues.json','cue-spec.json']:
  add(ROOT/'artifacts/data'/name,'artifacts/data/'+name)
 for name in ['delivery.json','encoded-review.json','encoded-content.json','visual-decisions.json','pan-render.json','pan-audio-parity.json','native-pan-inventory.json','native-drive-export.json','native-encoded-review.json','native-content.json']:
  add(ROOT/'artifacts/reviews'/name,'artifacts/reviews/'+name)
 for p in (ROOT/'artifacts/reviews/delivery-0.17.0').glob('*'):
  if p.is_file():add(p,p.relative_to(ROOT))
 for p in (ROOT/'artifacts/images').glob('*'):
  if p.is_file():add(p,p.relative_to(ROOT))
 skill=REPO/'skills/line-world-video'
 add(skill/'scripts/paper_video.py','tools/line-world-video/scripts/paper_video.py')
 for p in (skill/'assets/paper-video').glob('*'):add(p,'tools/line-world-video/assets/paper-video/'+p.name)
 add(REPO/'skills/line-world-google-vids/scripts/narration_cues.py','tools/line-world-google-vids/scripts/narration_cues.py')
 add(REPO/'projects/line-world-video/artifacts/packages'/f'line-world-video-{VERSION}.zip',f'plugin/line-world-video-{VERSION}.zip')
 for p in sorted(staging.rglob('*')):
  if p.is_file():files.append({'path':p.relative_to(staging).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (staging/'source-manifest.json').write_text(json.dumps({'version':VERSION,'files':files,'source':'Pinned SEAL paper with original captures, calm camera and margin marks; native Nyla voice and native Google Vids final export; local comparison retained.'},indent=2)+'\n',encoding='utf-8')
 archive=packages/f'seal-paper-editable-{VERSION}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(staging.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(staging).as_posix())
 print(json.dumps({'ok':True,'archive':str(archive),'files':len(files)+1,'bytes':archive.stat().st_size,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
if __name__=='__main__':main()

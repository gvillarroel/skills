#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare measured native uploads and journal actual renderer endpoint receipts."""
import copy,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PLUGIN=ROOT/'resources/plugin/skills'
if not PLUGIN.is_dir():PLUGIN=ROOT.parent/'line-world-video/artifacts/packages/line-world-video-0.14.2/plugin/skills'
sys.path.insert(0,str(PLUGIN/'line-world-video/scripts'))
import video_edit as edit
def main():
 story=edit.read(ROOT/'story.json');render=edit.read(ROOT/'artifacts/reviews/render.json')
 if not render['ok'] or len(render['scenes'])!=len(story['scenes']):raise ValueError('Complete visual verification is required before upload preparation.')
 source=copy.deepcopy(story);receipts=[];status=edit.status(ROOT,True);fingerprints={s['id']:s['inputsSha256'] for s in status['scenes']}
 for i,(scene,r) in enumerate(zip(source['scenes'],render['scenes'])):
  clip=ROOT/'artifacts/videos/clips'/f'{i+1:02d}-{scene["id"]}.mp4'
  scene['sourceClip']=str(clip);scene['clip']=str(clip);scene['staticHoldAfterSeconds']=scene['essentialAnimationSeconds']
  receipts.append({'id':scene['id'],'inputsSha256':fingerprints[scene['id']],'artifact':clip.relative_to(ROOT).as_posix(),'firstPose':r['firstPose'],'lastPose':r['lastPose']})
 edit.atomic(ROOT/'artifacts/manifests/render-receipts.json',edit.encode(receipts));edit.record(ROOT,receipts)
 input_path=ROOT/'artifacts/data/upload-story.json';edit.atomic(input_path,edit.encode(source));project=ROOT/'artifacts/native-batch';cli=PLUGIN/'line-world-google-vids/scripts/vids_batch.py'
 if not (project/'story.json').is_file():subprocess.run(['uv','run','--script',str(cli),'init','--story',str(input_path),'--project',str(project)],check=True)
 subprocess.run(['uv','run','--script',str(cli),'build','--project',str(project),'--observed',str(ROOT/'artifacts/data/native-observed.json')],check=True)
 print(json.dumps({'ok':True,'uploadProject':str(project),'localRenderCache':edit.status(ROOT)}))
if __name__=='__main__':main()

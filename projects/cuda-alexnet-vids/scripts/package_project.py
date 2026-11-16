#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package exact editable sources, measured evidence and the six-skill runtime."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PLUGIN=ROOT/'resources/plugin'
if not PLUGIN.is_dir():PLUGIN=ROOT.parent/'line-world-video/artifacts/packages/line-world-video-0.19.0/plugin'
def main():
 files={}
 def add(path,rel=None):
  if path.is_file() and '__pycache__' not in path.parts and path.suffix not in ['.pyc','.pyo']:files[rel or path.relative_to(ROOT).as_posix()]=path.read_bytes()
 for name in ['story.json','theme.json','theme.css','production.md','logos-and-portraits.md','visual-review.md','content-and-color.md','icon-alignment.md','people-context.md']:add(ROOT/name)
 for directory in ['scripts','templates','.line-world','artifacts/composition','artifacts/data','artifacts/media','artifacts/sources/portraits','artifacts/sources/logos','artifacts/svgs','artifacts/manifests','artifacts/reviews']:
  for path in (ROOT/directory).rglob('*'):
   if path.is_file() and not {'visual-source','content-development'}.intersection(path.parts) and not path.name.startswith('source-bundle') and path.name not in ['native-frame-stats.txt','frame-stats.txt'] and path.suffix not in ['.raw','.rgb']:add(path)
 for path in (ROOT/'artifacts/baseline-visual-review').rglob('*'):
  if path.is_file():add(path)
 for path in (ROOT/'artifacts/baseline-content-coverage').rglob('*'):
  if path.is_file():add(path)
 for path in (ROOT/'artifacts/videos/clips').glob('*.mp4'):add(path)
 for name in ['cuda-alexnet-final.mp4','cuda-alexnet-google-vids-final.mp4']:add(ROOT/'artifacts/videos'/name)
 add(ROOT/'artifacts/sources/native-voice-reference.mp4')
 for name in ['native-voice-reference.mp4','voice-observed.json','native-voice-inventory.json','native-final-1-5.json','native-final-6-10.json','native-final-inventory.json','native-inventory-check.json','spoken-context.json','cloud-metadata.json','cloud-observations.json','scripts-to-generate.json']:
  add(ROOT/'artifacts/revisions/people-context-0190'/name)
 add(ROOT/'artifacts/screenshots/google-vids-people-context.jpg')
 for name in ['google-vids-final.jpg','google-vids-portraits.jpg','google-vids-visual-review.jpg','google-vids-empty-scene.jpg','google-vids-content-contrast.jpg','google-vids-red-outline.jpg','google-vids-solid-items.jpg','contact-sheet.jpg','media-graph.png']:add(ROOT/'artifacts/screenshots'/name)
 for path in PLUGIN.rglob('*'):
  if path.is_file():add(path,'resources/plugin/'+path.relative_to(PLUGIN).as_posix())
 manifest={'project':'cuda-alexnet-vids','pluginVersion':'0.19.0','nativeProject':'https://docs.google.com/videos/d/16jOs0a09fPGfJr4Ft3ZjpbCv3RhsEA3ClYEGg7oi_dA/edit','files':[{'path':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()} for rel,data in sorted(files.items())]};files['source-manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode('utf-8');out=ROOT/'artifacts/packages/cuda-alexnet-editable-0.19.0.zip';out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as archive:
  for rel,data in sorted(files.items()):
   info=zipfile.ZipInfo(rel,date_time=(2026,11,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data)
 report={'ok':True,'archive':str(out),'bytes':out.stat().st_size,'files':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()};(ROOT/'artifacts/packages/package.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package the revised editable visual sources and verify clean extraction."""
import hashlib,json,subprocess,zipfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def main():
 report=json.loads((ROOT/'artifacts/revision/native-verification.json').read_text(encoding='utf-8'));assert report['ok']
 story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'));files={}
 for name in ['build_visuals.py','scene.js','render_clips.py','audit_revision.py','train_demo.py','verify_revision.py','verify_solid_surfaces.py','finish_solid.py']:
  files['scripts/'+name]=(ROOT/'scripts'/name).read_bytes()
 for file in (ROOT/'artifacts/composition').iterdir():
  if file.is_file():files[file.relative_to(ROOT).as_posix()]=file.read_bytes()
 for name in ['production.md','artifacts/data/experiment.json','artifacts/handoff/timing.json','artifacts/handoff/observed.json','artifacts/revision/cues.json','artifacts/revision/cue-spec.json','artifacts/revision/native-verification.json','artifacts/revision/solid-native-inventory.json','artifacts/revision/solid-surfaces.json','artifacts/revision/layout-focus-audit.json','artifacts/revision/solid-review-notes.json','artifacts/revision/solid-delivery.json','artifacts/revision/google-vids-solid-items.jpg']:
  files[name]=(ROOT/name).read_bytes()
 for path in (ROOT/'artifacts/revision/solid-review-final').rglob('*'):
  if path.is_file():files[path.relative_to(ROOT).as_posix()]=path.read_bytes()
 for name in ['ml-overfitting-google-vids-final.mp4','ml-overfitting-google-vids-revised.mp4','ml-overfitting-solid-final.mp4']:
  files['artifacts/videos/'+name]=(ROOT/'artifacts/videos'/name).read_bytes()
 for scene in story['scenes']:
  source=Path(scene['clip']);name=source.relative_to(ROOT).as_posix();files[name]=source.read_bytes();scene['clip']=name
 files['story.json']=(json.dumps(story,indent=2,ensure_ascii=False)+'\n').encode()
 files['artifacts/composition/story.js']=('window.PRODUCTION='+json.dumps(story,ensure_ascii=False)+';\n').encode()
 output=ROOT/'artifacts/packages/ml-overfitting-solid-editable-0.18.0.zip';output.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for name,data in sorted(files.items()):z.writestr(name,data)
 extracted=Path(tempfile.mkdtemp(prefix='source-check-solid-',dir=ROOT/'artifacts/revision'))
 with zipfile.ZipFile(output) as z:z.extractall(extracted)
 for script in ['build_visuals.py','audit_revision.py']:
  subprocess.run(['uv','run','--script',str(extracted/'scripts'/script)],check=True,capture_output=True,text=True)
 verification={'ok':True,'archive':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'fileCount':len(files),'cleanExtractedBuildAndAudit':True,'nativeExportSha256':report['sha256'],'nativeVoicePcmPreserved':report['voicePreservation']['samePcmBytes']}
 (ROOT/'artifacts/revision/source-package-check.json').write_text(json.dumps(verification,indent=2)+'\n');print(json.dumps(verification))
if __name__=='__main__':main()

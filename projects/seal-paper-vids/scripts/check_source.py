#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Extract the actual source ZIP, verify all hashes and rebuild from its own tools."""
import hashlib,json,subprocess,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parent.parent;VERSION='0.17.0'
def main():
 archive=ROOT/'artifacts/packages'/f'seal-paper-editable-{VERSION}.zip';dest=ROOT/'artifacts'/f'source-check-{VERSION}'
 if dest.exists():raise ValueError('Keep prior source-check evidence; use a fresh destination.')
 dest.mkdir()
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   p=PurePosixPath(name)
   if p.is_absolute() or '..' in p.parts or ':' in name or '\\' in name:raise ValueError('Unsafe archive member.')
  z.extractall(dest)
 manifest=json.loads((dest/'source-manifest.json').read_text(encoding='utf-8'))
 for v in manifest['files']:
  if hashlib.sha256((dest/v['path']).read_bytes()).hexdigest()!=v['sha256']:raise ValueError('Source file digest differs: '+v['path'])
 builder=dest/'tools/line-world-video/scripts/paper_video.py';project=dest/'artifacts/composition'
 timing=json.loads((project/'timing.json').read_text(encoding='utf-8'))
 commands=[['uv','run','--script',str(builder),'build','--project',str(project),'--story',str(dest/'story.json')],['uv','run','--script',str(builder),'audit','--project',str(project),'--report',str(dest/'verification/audit.json'),'--poster',str(dest/'verification/hero.png'),'--poster-scene','knowledge-table','--poster-at','26']]
 results=[]
 for command in commands:
  value=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=120)
  results.append({'command':command,'exitCode':value.returncode,'stdout':value.stdout,'stderr':value.stderr})
  if value.returncode:raise ValueError('Standalone rebuild failed: '+value.stdout+value.stderr)
 if json.loads((project/'timing.json').read_text())!=timing:raise ValueError('Standalone scene timing changed.')
 report={'ok':True,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'verifiedFiles':len(manifest['files']),'timingUnchanged':True,'actualBrowserAudit':json.loads((dest/'verification/audit.json').read_text())['ok'],'commands':results,'scope':'Actual ZIP extraction, exact payload digests, own-tool rebuild and complete browser trajectories. No repository skill or live browser session is used by the extracted build.'}
 (ROOT/'artifacts/reviews/source-bundle.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['ok','verifiedFiles','timingUnchanged','actualBrowserAudit']}))
if __name__=='__main__':main()

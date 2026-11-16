#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Extract, verify and rebuild the complete project using only its bundled plugin."""
import functools,hashlib,http.server,json,os,subprocess,tempfile,threading,zipfile
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def command(args,cwd):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise ValueError(p.stdout+p.stderr)
 return p.stdout
def main():
 base=ROOT/'artifacts/source-check';base.mkdir(parents=True,exist_ok=True);work=Path(tempfile.mkdtemp(prefix='clean-',dir=base));archive=ROOT/'artifacts/packages/cuda-alexnet-editable-0.19.0.zip'
 with zipfile.ZipFile(archive) as z:z.extractall(work)
 manifest=json.loads((work/'source-manifest.json').read_text(encoding='utf-8'));report={'ok':False,'workdir':str(work),'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'pluginVersion':manifest['pluginVersion'],'files':len(manifest['files']),'errors':[]}
 try:
  for rec in manifest['files']:
   p=work/rec['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'],rec['path']
  report['payloadHashesMatch']=True
  report['rebuild']=command(['uv','run','--script','scripts/prepare_project.py'],work)
  result=command(['uv','run','--script','resources/plugin/skills/line-world-video/scripts/video_edit.py','status','--project',str(work)],work);report['localCache']=json.loads(result);expected={s['id'] for s in json.loads((work/'story.json').read_text(encoding='utf-8'))['scenes']};assert set(report['localCache']['reuse'])|set(report['localCache']['render'])==expected;assert not set(report['localCache']['reuse'])&set(report['localCache']['render']);report['cacheScope']='The changed shared runtime conservatively invalidates prior render fingerprints; this check verifies the complete scene inventory and does not stamp old clips as rerendered.'
  report['audit']=command(['uv','run','--script','scripts/render_video.py'],work);assert json.loads((work/'artifacts/reviews/visual-audit.json').read_text(encoding='utf-8'))['ok']
  report['peopleContext']=command(['uv','run','--script','resources/plugin/skills/line-world-video/scripts/people_context.py','--story','story.json','--media','artifacts/media/manifest.json','--html','artifacts/composition/index.html','--cues','artifacts/data/cues.json','--require-observed','--output','artifacts/reviews/portable-people.json'],work);assert json.loads((work/'artifacts/reviews/portable-people.json').read_text(encoding='utf-8'))['ok']
  server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(work)));threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   with sync_playwright() as pw:
    paths=sorted((Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True);browser=pw.chromium.launch(executable_path=str(paths[0]) if paths else None,headless=True);page=browser.new_page(viewport={'width':1280,'height':840});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/artifacts/composition/preview.html');page.evaluate('async()=>{await ready}');assert page.locator('#pick option').count()==10;page.select_option('#pick','8');page.evaluate('''()=>{const s=document.querySelector('#seek');s.value=9.7;s.dispatchEvent(new Event('input'))}''');state=page.evaluate('snapshot()');assert state['visibleScene']==8;page.screenshot(path=str(work/'preview-check.png'));assert not errors;report['preview']={'sceneOptions':10,'selectedScene':state['visibleScene'],'browserErrors':errors}
    # Open the portable review directly; the preview-only HTTP fixture has no byte-range video serving.
    review=json.loads((work/'artifacts/reviews/people-context-review/report.json').read_text(encoding='utf-8'));assert review['deliveryReady'] and review['content']['ok'],'The current portable review needs verified content and explicit visual decisions.';sample_count=len(review['samples'])
    page.goto((work/'artifacts/reviews/people-context-review/index.html').as_uri());page.wait_for_function('Number.isFinite(document.querySelector("video").duration)');assert page.locator('main section').count()==10;assert page.locator('button[data-time]').count()==sample_count
    loaded=page.evaluate('''async()=>Promise.all([...document.images].map(e=>new Promise((ok,bad)=>{const i=new Image();i.onload=()=>ok(i.naturalWidth>0);i.onerror=()=>bad(Error(e.getAttribute('src')));i.src=e.src})))''');assert all(loaded)
    target=page.locator('button[title$="cue:runner-up"]');timestamp=float(target.get_attribute('data-time'));target.click();page.wait_for_function('t=>{const v=document.querySelector("video");return Math.abs(v.currentTime-t)<0.1&&!v.seeking&&v.readyState>=2}',arg=timestamp)
    duration=page.evaluate('document.querySelector("video").duration');expected_duration=json.loads((work/'artifacts/reviews/native-export.json').read_text(encoding='utf-8'))['duration'];assert abs(duration-expected_duration)<.1,f'Portable review duration {duration} differs from the current native export {expected_duration}.';assert not errors
    baseline=work/'artifacts/baseline-visual-review/artifacts/videos/cuda-alexnet-final.mp4';assert baseline.is_file();report['reviewGallery']={'scenes':10,'sampleButtons':sample_count,'imagesLoaded':len(loaded),'movieDuration':duration,'seekSeconds':timestamp,'baselineMovieIncluded':True,'browserErrors':errors};page.screenshot(path=str(work/'review-gallery-check.png'));browser.close()
  finally:server.shutdown();server.server_close()
  report['ok']=True
 except Exception as e:report['errors'].append(str(e))
 (ROOT/'artifacts/reviews/source-bundle.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'files':report['files'],'errors':report['errors'],'workdir':str(work)}));return 0 if report['ok'] else 2
if __name__=='__main__':main()

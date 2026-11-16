#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Audit the authored local movie's reading frames and audio-linked focus."""
import functools,http.server,json,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def main():
 out=ROOT/'artifacts/revision';out.mkdir(parents=True,exist_ok=True)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'artifacts/composition')));threading.Thread(target=server.serve_forever,daemon=True).start()
 paths=sorted((Path(os.environ['LOCALAPPDATA'])/'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True)
 report={'scenes':[],'errors':[],'pointerCollisions':[]}
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=str(paths[0]),headless=True);page=browser.new_page(viewport={'width':1920,'height':1080});page.on('pageerror',lambda e:report['errors'].append(str(e)))
  page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.evaluate('document.fonts.ready')
  try:plans=page.evaluate('prepareFocus()')
  except Exception as e:
   report['errors'].append(str(e));plans=[]
  for i,p in enumerate(plans):
   page.evaluate('([i,t])=>renderAt(i,t)',[i,12])
   if i<12:
    a=page.evaluate('LineWorldFocus.audit(document.querySelector("#stage"))');report['scenes'].append({'index':i,**a})
   # Validate the actual dot envelope, including its keyline, throughout every pan and against text and bodies.
   duration=page.evaluate('i=>PRODUCTION.scenes[i].clipSeconds',i)
   times=sorted(set([round(n/30,6) for n in range(round(duration*30))]+[c['at'] for c in p['cues']]))
   hits=page.evaluate('''([i,times])=>{const hits=[];for(const t of times){const s=renderAt(i,t);for(const issue of LineWorldVisualReview.guide(document.querySelector('#stage')).issues)hits.push({t,target:s.target,...issue})}return hits}''',[i,times])
   report['pointerCollisions']+=({'index':i,**h} for h in hits)
   page.evaluate('([i,t])=>renderAt(i,t)',[i,12]);page.screenshot(path=str(out/f'{i+1:02d}-reading.png'))
  arrivals=page.evaluate('''()=>{const issues=[];for(const [i,p] of prepareFocus().entries())for(const c of p.cues){const pose=LineWorldFocus.pose(p.cues,c.at,p.origin);if(Math.hypot(pose.x-c.x,pose.y-c.y)>.01)issues.push({scene:i,target:c.target,at:c.at,actual:pose})}return issues}''') if plans else []
  report['cueArrivalMismatches']=arrivals;report['readingSceneImportantMarkPortsClear']=bool(plans) and not report['errors'];report['plans']=plans;report['ok']=not report['errors'] and all(s['ok'] for s in report['scenes']) and not report['pointerCollisions'] and not arrivals
  browser.close()
 server.shutdown();(out/'layout-focus-audit.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(json.dumps({'ok':report['ok'],'scenes':report['scenes'],'errors':report['errors'],'pointerCollisionCount':len(report['pointerCollisions']),'pointerCollisionSample':report['pointerCollisions'][:5]},ensure_ascii=True))
 return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())

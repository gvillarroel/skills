#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Inspect a standalone local narrated scene without scaffolding a demo project."""
import argparse,functools,http.server,json,math,os,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
SKILL=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def browser_path():
 cache=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'.cache')))/'ms-playwright'
 cached=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True)
 return next((str(p) for p in [os.environ.get('LINE_WORLD_BROWSER',''),*cached,'C:/Program Files/Google/Chrome/Application/chrome.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','/usr/bin/google-chrome','/usr/bin/chromium'] if str(p) and Path(p).is_file()),None)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--html',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--screenshot',type=Path,required=True);p.add_argument('--times',default='0,2.2,4.1,5,9');p.add_argument('--guide',default='#guide');p.add_argument('--scene-index',type=int);a=p.parse_args()
 html=a.html.resolve();times=[float(t) for t in a.times.split(',')]
 if not times or any(not math.isfinite(t) or t<0 for t in times):p.error('Times must be finite nonnegative seconds.')
 for output in [a.output,a.screenshot]:
  if output.resolve().is_relative_to(SKILL):p.error('Keep generated outputs outside the skill.')
  output.parent.mkdir(parents=True,exist_ok=True)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(html.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
 report={'ok':False,'samples':[],'browserErrors':[],'scope':'Local authored HTML; supplied cue times do not prove independently measured audio.'}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch(executable_path=browser_path(),headless=True);page=browser.new_page(viewport={'width':1920,'height':1080});page.on('pageerror',lambda e:report['browserErrors'].append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/{html.name}')
   page.evaluate('async()=>{await document.fonts.ready;if(window.ready?.then)await window.ready;else if(typeof window.prepareFocus==="function")window.prepareFocus()}')
   page.add_script_tag(path=str(SKILL/'assets/runtime/focus.js'))
   render=lambda t:page.evaluate('([t,i])=>i===null?window.renderAt(t):typeof window.renderClip==="function"?window.renderClip(i,t):window.renderAt(i,t)',[t,a.scene_index])
   for t in times:
    state=render(t)
    audit=page.evaluate('''selector=>{const stage=document.querySelector('#stage')||document.querySelector('svg'),a=LineWorldFocus.audit(stage),guide=document.querySelector(selector),hits=[];if(!guide)return {...a,ok:false,guideMissing:true};const b=guide.getBoundingClientRect(),s=getComputedStyle(guide),half=(parseFloat(s.strokeWidth)||0)/2,g={x0:b.left-half,y0:b.top-half,x1:b.right+half,y1:b.bottom+half},shown=s.display!=='none'&&s.visibility!=='hidden'&&+s.opacity>0;if(shown)for(const e of stage.querySelectorAll('text')){const q=e.getBoundingClientRect();if(e.textContent&&LineWorldFocus.overlap(g,{x0:q.left,x1:q.right,y0:q.top,y1:q.bottom},3))hits.push(e.textContent)}return {...a,ok:a.ok&&!hits.length,guide:{x:(b.left+b.right)/2,y:(b.top+b.bottom)/2,fill:s.fill,visible:shown},guideTextCollisions:hits}}''',a.guide)
    surfaces=page.evaluate('()=>window.LineWorldTheme?.audit?.(document.querySelector("#stage"))||null')
    report['samples'].append({'seconds':t,'state':state,'audit':audit,'surfaces':surfaces})
   render(times[0]);repeat=render(times[-1]);report['repeatSeek']=repeat==report['samples'][-1]['state'];page.screenshot(path=str(a.screenshot.resolve()));report['ok']=not report['browserErrors'] and report['repeatSeek'] and all(x['audit']['ok'] and (x['surfaces'] is None or x['surfaces']['ok']) for x in report['samples']);browser.close()
 except Exception as e:report['browserErrors'].append(str(e))
 finally:server.shutdown();server.server_close()
 a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'samples':len(report['samples']),'output':str(a.output)}));return 0 if report['ok'] else 2
if __name__=='__main__':raise SystemExit(main())

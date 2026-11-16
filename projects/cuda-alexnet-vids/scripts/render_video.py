#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2","pillow>=11,<13"]
# ///
"""Audit and render authored local HTML; preserve measured speech-linked motion."""
import argparse,functools,hashlib,http.server,io,json,os,subprocess,threading
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def main():
 p=argparse.ArgumentParser();p.add_argument('--render',action='store_true');p.add_argument('--scene',action='append');a=p.parse_args()
 out=ROOT/'artifacts/videos/clips';out.mkdir(parents=True,exist_ok=True);images=ROOT/'artifacts/screenshots';project=ROOT/'artifacts/composition';story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'))
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(project)));threading.Thread(target=server.serve_forever,daemon=True).start()
 report={'ok':False,'browserErrors':[],'scenes':[],'renderer':'Real D3 + native Mermaid SVG + isolated Playwright browser + FFmpeg','nativeHyperFrames':False,'nativeGoogleVidsFinal':False};previous=None;captures=0;reuses=0
 try:
  with sync_playwright() as pw:
   cache=Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright';paths=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True);browser=pw.chromium.launch(executable_path=str(paths[0]) if paths else None,headless=True);page=browser.new_page(viewport={'width':1920,'height':1080});page.on('pageerror',lambda e:report['browserErrors'].append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.evaluate('async()=>await window.ready');report['activeCssAnimations']=page.evaluate('document.getAnimations().length')
   for i,s in enumerate(story['scenes']):
    duration=s['clipSeconds'];audit=page.evaluate('i=>auditScene(i)',i);ports=page.evaluate('i=>RESOLVED_CUES[i]',i);snapshots={};guide_issues=[]
    for cue in ports:
     state=page.evaluate('([i,t])=>renderClip(i,t)',[i,cue['at']]);snapshots[cue['target']]=state
     expected={'x':cells_x(i)+cue['x'],'y':(0 if i<5 else 1080)+cue['y']}
     if abs(state['guide']['x']-expected['x'])>1e-6 or abs(state['guide']['y']-expected['y'])>1e-6:guide_issues.append(cue['target'])
    first_pose=page.evaluate('i=>renderClip(i,0)',i);first=page.screenshot();last_pose=page.evaluate('([i,t])=>renderClip(i,t)',[i,duration]);last=page.screenshot();(images/f'{i+1:02d}-{s["id"]}.png').write_bytes(last)
    mean=max(ImageStat.Stat(ImageChops.difference(Image.open(io.BytesIO(first)).convert('RGB'),Image.open(io.BytesIO(previous)).convert('RGB'))).mean) if previous else 0
    previous=last;page.evaluate('([i,t])=>renderClip(i,t)',[i,max(2,duration/2)]);page.screenshot(path=str(images/f'{i+1:02d}-reading.png'))
    media=page.evaluate('''id=>[...document.querySelectorAll('#scene-'+id+' [data-media-id]')].map(g=>{const b=g.querySelector('image').getBoundingClientRect();return{id:g.dataset.mediaId,x:b.x,y:b.y,width:b.width,height:b.height}})''',s['id'])
    page.evaluate('([i,t])=>renderClip(i,t)',[i,1]);repeat=page.evaluate('([i,t])=>renderClip(i,t)',[i,duration]);repeat_ok=repeat==last_pose
    item={'id':s['id'],'audit':audit,'guideArrivalIssues':guide_issues,'cueCount':len(ports),'cues':ports,'joinMeanDifference':mean,'joinTolerance':.01,'repeatSeek':repeat_ok,'firstPose':first_pose,'lastPose':last_pose,'duration':duration,'frames':round(duration*30),'media':media};report['scenes'].append(item)
    if not audit['ok'] or guide_issues or mean>.01 or not repeat_ok:continue
    if a.render and (not a.scene or s['id'] in a.scene):
     video=out/f'{i+1:02d}-{s["id"]}.mp4';command=['ffmpeg','-y','-v','error','-f','image2pipe','-vcodec','png','-framerate','30','-i','pipe:0','-frames:v',str(item['frames']),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)];proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE);signature=None;png=None
     for n in range(item['frames']):
      state=page.evaluate('([i,t])=>renderClip(i,t)',[i,n/30]);key=json.dumps(state,sort_keys=True)
      if key!=signature:png=page.screenshot();signature=key;captures+=1
      else:reuses+=1
      proc.stdin.write(png)
     proc.stdin.close();error=proc.stderr.read().decode();code=proc.wait()
     if code:raise ValueError(error)
     item['video']=str(video);item['sha256']=hashlib.sha256(video.read_bytes()).hexdigest();print(json.dumps({'rendered':s['id'],'frames':item['frames']}),flush=True)
   browser.close()
  report['capturedFrames']=captures;report['reusedFrameImages']=reuses;report['ok']=not report['browserErrors'] and not report['activeCssAnimations'] and all(s['audit']['ok'] and not s['guideArrivalIssues'] and s['joinMeanDifference']<=.01 and s['repeatSeek'] for s in report['scenes'])
  sheet=Image.new('RGB',(1920,1440),'white')
  for i in range(10):sheet.paste(Image.open(images/f'{i+1:02d}-reading.png').resize((640,360)),((i%3)*640,(i//3)*360))
  sheet.save(images/'contact-sheet.jpg',quality=93)
 except Exception as e:report['browserErrors'].append(str(e))
 finally:server.shutdown();server.server_close()
 target=ROOT/'artifacts/reviews'/('render.json' if a.render else 'visual-audit.json');target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(json.dumps({'ok':report['ok'],'report':str(target),'errors':report['browserErrors'],'failures':[{'id':s['id'],'issues':s['audit'].get('issues'), 'ports':s['audit'].get('guidePortCollisions'),'arrival':s['guideArrivalIssues'],'join':s['joinMeanDifference']} for s in report['scenes'] if not s['audit']['ok'] or s['guideArrivalIssues'] or s['joinMeanDifference']>.01]}));return 0 if report['ok'] else 2
def cells_x(i):return (i if i<5 else 9-i)*1920
if __name__=='__main__':main()

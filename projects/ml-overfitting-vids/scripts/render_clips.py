#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Render only the authored local composition; never connect to a user browser."""
import argparse
import functools
import http.server
import json
import os
import subprocess
import threading
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--audit-only',action='store_true');parser.add_argument('--start-scene',type=int,default=1);parser.add_argument('--scene',action='append',help='Render only these stable scene IDs; audit all joins.');a=parser.parse_args()
    project=ROOT/'artifacts/composition';out=ROOT/'artifacts/videos/clips-revised';out.mkdir(parents=True,exist_ok=True)
    images=ROOT/'artifacts/revision/images';images.mkdir(parents=True,exist_ok=True)
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(project)));threading.Thread(target=server.serve_forever,daemon=True).start()
    cache=Path(os.environ['LOCALAPPDATA'])/'ms-playwright';paths=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True)
    story=json.loads((ROOT/'story.json').read_text(encoding='utf-8-sig'));receipts=[];last=None;moving=story.get('motion',{}).get('animationSeconds',12)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=str(paths[0]) if paths else 'C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        page=browser.new_page(viewport={'width':1920,'height':1080});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{server.server_port}/index.html');page.evaluate('async()=>await window.ready')
        cache_signature=None;cache_png=None;captured=0;reused=0
        def capture(i,t):
            nonlocal cache_signature,cache_png,captured,reused
            state=page.evaluate('([i,t])=>renderAt(i,t)',[i,t]);signature=json.dumps(state,sort_keys=True)
            if signature!=cache_signature:
                cache_png=page.screenshot(type='png');cache_signature=signature;captured+=1
            else:reused+=1
            return cache_png
        for i,scene in enumerate(story['scenes']):
            duration=scene['clipSeconds'];first=capture(i,0);final=capture(i,duration);target=images/f'{i+1:02d}-{scene["id"]}.png';target.write_bytes(final)
            # Start of a new scene must equal the previous held pose exactly.
            first_file=images/f'{i+1:02d}-start.png';first_file.write_bytes(first)
            if last:
                import io
                diff=ImageChops.difference(Image.open(io.BytesIO(first)).convert('RGB'),Image.open(io.BytesIO(last)).convert('RGB'))
                join_mean=max(ImageStat.Stat(diff).mean)
                # Identical geometry can differ slightly at antialiased GPU edges.
                changed=join_mean>.01
            else:changed=False;join_mean=0
            if changed:raise ValueError('Camera or guide continuity mismatch before '+scene['id'])
            last=final
            duration=scene['clipSeconds'];frames=round(duration*30);video=out/f'{i+1:02d}-{scene["id"]}.mp4'
            did_render=not a.audit_only and i+1>=a.start_scene and (not a.scene or scene['id'] in a.scene)
            if did_render:
                command=['ffmpeg','-y','-v','error','-f','image2pipe','-vcodec','png','-framerate','30','-i','pipe:0','-frames:v',str(frames),'-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
                proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
                for n in range(frames):
                    proc.stdin.write(capture(i,n/30))
                    if n%90==0:print(json.dumps({'scene':i+1,'capturedFrames':n}),flush=True)
                proc.stdin.close();err=proc.stderr.read().decode();code=proc.wait()
                if code:raise RuntimeError(err)
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True)) if video.is_file() else None
            if i:
                states=page.evaluate('([i,d])=>[renderAt(i-1,d),renderAt(i,0)]',[i,story['scenes'][i-1]['clipSeconds']])
                for key in ['scale','cx','cy','guideX','guideY','guideRadius']:
                    if abs(states[0][key]-states[1][key])>1e-8:raise ValueError('Actual pose discontinuity: '+key)
            receipts.append({'id':scene['id'],'clip':str(video),'targetDuration':duration,'targetFrames':frames,'actualDuration':float(probe['format']['duration']) if probe else None,'actualFrames':int(probe['streams'][0]['nb_frames']) if probe else None,'continuousStart':not changed,'joinMeanChannelDifference':join_mean,'joinTolerance':.01,'exactCameraGuidePose':True,'image':str(target)})
            print(json.dumps({'scene':i+1,'id':scene['id'],'rendered':did_render}),flush=True)
        browser.close()
    server.shutdown()
    sheet=Image.new('RGB',(1440,1080),'white')
    for i,row in enumerate(receipts):sheet.paste(Image.open(row['image']).resize((480,270)),((i%3)*480,(i//3)*270))
    sheet.save(images/'contact-sheet.jpg',quality=93)
    report={'ok':not errors,'renderer':'D3 SVG + isolated browser screenshots + FFmpeg; full audio-clock duration','nativeHyperFrames':False,'browserErrors':errors,'capturedScreenshots':captured,'reusedScreenshots':reused,'scenes':receipts}
    (ROOT/'artifacts/revision/render-report.json').write_text(json.dumps(report,indent=2)+'\n')
    if errors:raise ValueError(errors)

if __name__=='__main__':main()

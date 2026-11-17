#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "resvg-py==0.5.0", "pillow>=11,<13"]
# ///
"""Check actual MP4 playback and exact source-preview seeks in a fresh local browser."""
import functools
import hashlib
import http.server
import json
import os
import tempfile
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from render_movie import Quiet, browser_path

ROOT=Path(__file__).resolve().parent.parent
ART=ROOT/'artifacts'


def main():
    temporary=ART/'browser-temp';temporary.mkdir(exist_ok=True)
    os.environ['TMP']=str(temporary);os.environ['TEMP']=str(temporary);tempfile.tempdir=str(temporary)
    story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'));video=ART/'videos/sixties-lifestyle.mp4'
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start();errors=[];checks=[]
    try:
        with sync_playwright() as pw:
            chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
            browser=pw.chromium.launch(executable_path=str(chrome) if chrome.is_file() else browser_path(),headless=True,args=['--autoplay-policy=no-user-gesture-required'])
            page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            origin=f'http://127.0.0.1:{server.server_port}';page.goto(origin+'/artifacts/index.html')
            element=page.locator('video');metadata=element.evaluate('''async e=>{e.muted=true;if(e.readyState<1)await new Promise((ok,bad)=>{e.addEventListener('loadedmetadata',ok,{once:true});e.addEventListener('error',bad,{once:true})});return{duration:e.duration,width:e.videoWidth,height:e.videoHeight}}''')
            url=element.evaluate('e=>e.src||e.querySelector("source").src');head=page.request.head(url);partial=page.request.get(url,headers={'Range':'bytes=0-4095'})
            if head.status!=200 or int(head.headers['content-length'])!=video.stat().st_size or partial.status!=206 or len(partial.body())!=4096:raise ValueError('MP4 access/range delivery failed.')
            for scene in story['scenes']:
                target=scene['start']+4
                element.evaluate('''async(e,t)=>{if(Math.abs(e.currentTime-t)>.01)await new Promise((ok,bad)=>{e.addEventListener('seeked',ok,{once:true});e.addEventListener('error',bad,{once:true});e.currentTime=t});await e.play()}''',target)
                page.wait_for_function('(t)=>{const e=document.querySelector("video");return e.readyState>=2&&e.currentTime>t+.15}',arg=target,timeout=15000)
                state=element.evaluate('e=>{e.pause();return{time:e.currentTime,error:e.error?.code||null,readyState:e.readyState,decodedFrames:e.getVideoPlaybackQuality().totalVideoFrames}}')
                if state['error'] or not state['decodedFrames']:raise ValueError('Actual native video playback failed.')
                checks.append({'scene':scene['id'],'target':target,**state})
            page.screenshot(path=str(ART/'images/playback.png'))
            page.goto(origin+'/composition/index.html?graphics=1');page.evaluate('async()=>await window.ready');previews=[]
            for scene in story['scenes']:
                t=scene['start']+scene['cues'][2]['at']+.1
                result=page.evaluate('async t=>await seekMedia(t)',t)
                observed=page.evaluate('''()=>[...document.querySelectorAll('video')].filter(e=>getComputedStyle(e).display!=='none').map(e=>({id:e.dataset.id,time:e.currentTime,ready:e.readyState,error:e.error?.code||null}))''')
                if any(abs(e['time']-result['t'])>.05 or e['ready']<2 or e['error'] for e in observed):raise ValueError('A source preview did not display its actual requested time.')
                previews.append({'requested':t,'state':result,'media':observed})
            browser.close()
    finally:server.shutdown();server.server_close()
    result={'ok':not errors,'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'metadata':metadata,'nativePlayback':checks,'sourcePreviewSeeks':previews,'pageErrors':errors,'httpStatus':head.status,'rangeStatus':partial.status,'scope':'Fresh Chrome, actual metadata/range access, seek and muted native playback. Source preview time checks are separate. No listening pass or native Google Vids playback is claimed.'}
    (ART/'reviews/playback.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'ok':result['ok'],'nativeScenes':len(checks),'exactSourceSeeks':len(previews),'rangeStatus':partial.status,'errors':errors}))
    if errors:raise SystemExit(2)


if __name__=='__main__':main()

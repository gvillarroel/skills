#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Verify current MP4 access, metadata, seeking and actual fresh-browser playback."""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parents[1]
sys.path.insert(0,str(REPO/'skills/line-world-video/scripts'))
from inspect_focus import browser_path


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
    def copyfile(self,source,outputfile):
        try:return super().copyfile(source,outputfile)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError):pass  # A paused/closed media request can end early.


def main():
    report_path=ROOT/'artifacts/playback.json'
    summary=json.loads((ROOT/'artifacts/current/summary.json').read_text(encoding='utf-8'))
    rows=[r for r in summary['videos'] if r['role']=='current']
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(REPO/'projects')))
    threading.Thread(target=server.serve_forever,daemon=True).start();results=[]
    try:
        with sync_playwright() as pw:
            chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
            browser=pw.chromium.launch(executable_path=str(chrome) if chrome.is_file() else browser_path(),headless=True,args=['--autoplay-policy=no-user-gesture-required'])
            page=browser.new_page(viewport={'width':1440,'height':1000})
            page.goto(f'http://127.0.0.1:{server.server_port}/line-world-quality-review/artifacts/current/index.html')
            if page.locator('video').count()!=len(rows):raise ValueError('The current index lacks an expected video player.')
            for i,row in enumerate(rows):
                media=page.locator('video').nth(i);src=media.evaluate('e=>e.src');response=page.request.head(src)
                metadata=media.evaluate('''async e=>{e.muted=true;e.preload='auto';e.load();if(e.readyState<1)await new Promise((ok,bad)=>{e.addEventListener('loadedmetadata',ok,{once:true});e.addEventListener('error',()=>bad(Error('Media error '+e.error?.code)),{once:true})});return{duration:e.duration,width:e.videoWidth,height:e.videoHeight}}''')
                target=min(2,metadata['duration']*.2);media.evaluate('(e,t)=>{e.currentTime=t}',target)
                media.evaluate('async e=>await e.play()')
                page.wait_for_function('([i,t])=>{const e=document.querySelectorAll("video")[i];return e.readyState>=2&&e.currentTime>t+.1}',arg=[i,target],timeout=15000)
                state=media.evaluate('e=>{e.pause();return{currentTime:e.currentTime,readyState:e.readyState,error:e.error?.code||null,decodedFrames:e.getVideoPlaybackQuality?.().totalVideoFrames,muted:e.muted}}')
                ok=response.status==200 and int(response.headers.get('content-length','0'))==Path(row['video']).stat().st_size and metadata['width']==1920 and metadata['height']==1080 and state['error'] is None and state['decodedFrames']>0
                results.append({'id':row['id'],'ok':ok,'videoSha256':row['videoSha256'],'httpStatus':response.status,'contentLength':response.headers.get('content-length'),**metadata,**state})
                print(json.dumps(results[-1]),flush=True)
            page.screenshot(path=str(ROOT/'artifacts/playback-index.png'));browser.close()
    finally:server.shutdown();server.server_close()
    report={'ok':len(results)==len(rows) and all(r['ok'] for r in results),'videos':results,'scope':'Fresh local Chrome profile, local review index and actual H.264 MP4 playback/seek. Muted playback; not Google Vids cloud playback or a new listening pass.'}
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if not report['ok']:raise SystemExit(2)


if __name__=='__main__':main()

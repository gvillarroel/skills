#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "numpy>=2,<3"]
# ///
"""Compare semantic solid bodies with pixels in the actual exported movie."""
import argparse, functools, hashlib, http.server, json, os, subprocess, threading
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path(__file__).resolve().parent.parent)
    for name in ['video','output']: p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); root=a.project.resolve()
    if not a.video.is_file():p.error('The actual exported video file must exist.')
    story=json.loads((root/'story.json').read_text(encoding='utf-8'))
    cuda=(root/'artifacts/data/final-native-observed.json').is_file()
    timing=json.loads((root/('artifacts/data/final-native-observed.json' if cuda else 'artifacts/handoff/timing.json')).read_text(encoding='utf-8'))
    cues=json.loads((root/('artifacts/data/cues.json' if cuda else 'artifacts/revision/cues.json')).read_text(encoding='utf-8'))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root/'artifacts/composition')))
    threading.Thread(target=server.serve_forever,daemon=True).start(); checks=[]; cursor=0
    try:
        with sync_playwright() as pw:
            paths=sorted((Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True)
            browser=pw.chromium.launch(executable_path=str(paths[0]) if paths else None,headless=True)
            page=browser.new_page(viewport={'width':1920,'height':1080}); page.goto(f'http://127.0.0.1:{server.server_port}/index.html')
            page.evaluate('async()=>{await document.fonts.ready;if(window.ready)await window.ready;else window.prepareFocus?.();}')
            for i,scene in enumerate(story['scenes']):
                local_times=sorted(set([min(scene['clipSeconds']*.5,12.5)]+[min(c['at']+.12,scene['clipSeconds']-.1) for c in cues['scenes'][i]['cues']]))
                for t in local_times:
                    page.evaluate('([i,t,cuda])=>cuda?window.renderClip(i,t):window.renderAt(i,t)',[i,t,cuda])
                    source=page.evaluate(r'''()=>{const root=document.querySelector('#stage'),items=[];for(const e of root.querySelectorAll('[data-lw-surface="item"]')){const b=e.getBoundingClientRect(),c=getComputedStyle(e),m=c.fill.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);if(!m||b.width<24||b.height<24||b.x<0||b.y<0||b.right>1920||b.bottom>1080)continue;let visible=true;for(let q=e;q;q=q.parentElement)if(Number(getComputedStyle(q).opacity)<.95||getComputedStyle(q).display==='none')visible=false;if(!visible)continue;items.push({tag:e.tagName.toLowerCase(),x:b.x,y:b.y,w:b.width,h:b.height,rgb:m.slice(1).map(Number)});}return{audit:LineWorldTheme.audit(root),items,whiteLabels:[...root.querySelectorAll('text')].filter(e=>{const b=e.getBoundingClientRect();let shown=true;for(let q=e;q;q=q.parentElement)if(Number(getComputedStyle(q).opacity)<.95||getComputedStyle(q).display==='none')shown=false;return shown&&getComputedStyle(e).fill==='rgb(255, 255, 255)'&&b.x>=0&&b.y>=0&&b.right<=1920&&b.bottom<=1080&&b.width>20}).map(e=>{const b=e.getBoundingClientRect();return{x:b.x,y:b.y,w:b.width,h:b.height,text:e.textContent}})};}''')
                    encoded=[]; labels=[]
                    if source['items']:
                        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(cursor+t),'-i',str(a.video),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
                        image=np.frombuffer(raw,np.uint8).reshape(1080,1920,3)
                        for item in source['items']:
                            points=[]
                            for u in np.linspace(.18,.82,9):
                                for v in np.linspace(.18,.82,9):
                                    if item['tag'] in ['circle','ellipse'] and (u-.5)**2+(v-.5)**2>.12:continue
                                    points.append(image[min(1079,round(item['y']+v*item['h'])),min(1919,round(item['x']+u*item['w']))])
                            error=float(np.median(np.max(np.abs(np.array(points,dtype=float)-item['rgb']),axis=1)))
                            # YUV 4:2:0 affects small red bodies more than neutral gray.
                            tolerance=18 if item['rgb']==[158,27,50] else 13
                            encoded.append({**item,'medianRgbError':error,'tolerance':tolerance,'ok':error<=tolerance})
                        for label in source['whiteLabels']:
                            x,y=max(0,int(label['x'])),max(0,int(label['y']));patch=image[y:min(1080,int(label['y']+label['h'])+1),x:min(1920,int(label['x']+label['w'])+1)]
                            white=int(np.sum(np.min(patch,axis=2)>215)) if patch.size else 0
                            labels.append({**label,'encodedWhitePixels':white,'ok':white>=5})
                    checks.append({'scene':scene['id'],'localSeconds':t,'seconds':cursor+t,'sourceSurfaces':source['audit'],'encodedItems':encoded,'whiteLabels':labels,'ok':source['audit']['ok'] and all(e['ok'] for e in encoded) and all(l['ok'] for l in labels)})
                entry=timing['scenes'][i];cursor+=entry.get('sceneSeconds',entry.get('duration',0))
            browser.close()
    finally: server.shutdown();server.server_close()
    report={'ok':all(c['ok'] for c in checks),'videoSha256':hashlib.sha256(a.video.read_bytes()).hexdigest(),'poses':len(checks),'encodedItemChecks':sum(len(c['encodedItems']) for c in checks),'encodedWhiteLabelChecks':sum(len(c['whiteLabels']) for c in checks),'checks':checks,'scope':'Source semantic item/group contract at cue and reading poses, sparse interior pixel comparisons in actual native export, and encoded white-label presence. Excludes unmarked data encodings, photographs and small marks. No composition-area quotas; this does not prove every pixel or every aesthetic decision.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['ok','poses','encodedItemChecks','encodedWhiteLabelChecks']}));return 0 if report['ok'] else 2

if __name__=='__main__':raise SystemExit(main())

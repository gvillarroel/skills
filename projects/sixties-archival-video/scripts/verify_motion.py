#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "resvg-py==0.5.0", "pillow>=11,<13", "numpy>=2,<3"]
# ///
"""Inspect the actual encoded television camera and the complete floating groups."""
import functools
import hashlib
import http.server
import io
import json
import subprocess
import threading
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from render_movie import Quiet, browser_path
from build_delivery import sheet

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / 'artifacts'


def frame(path, seconds):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(seconds), '-i', str(path), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', 'pipe:1'])
    return Image.open(io.BytesIO(data)).convert('RGB')


def main():
    story = json.loads((ROOT / 'story.json').read_text(encoding='utf-8'))
    scene = next(s for s in story['scenes'] if s['id'] == 'communication')
    cue = next(c for c in scene['cues'] if c['target'] == 'media-tv')['at']
    detail = story['motion']['detail']
    times = [cue-detail['inSeconds'], cue, cue+detail['holdSeconds']-.1, cue+detail['holdSeconds']+detail['outSeconds']]
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(executable_path=browser_path(), headless=True)
            page = browser.new_page(viewport={'width':1920, 'height':1080})
            page.goto(f'http://127.0.0.1:{server.server_port}/composition/index.html?graphics=1')
            page.evaluate('async()=>await window.ready')
            samples = [page.evaluate('t=>renderAt(t)', scene['start']+t) for t in times]
            floats = page.evaluate('''()=>STORY.scenes.filter(s=>s.kind!=='overview').map(s=>{const a=renderAt(s.start+4),b=renderAt(s.start+8);return{id:s.id,first:a.gentle.float,last:b.gentle.float}})''')
            browser.close()
    finally:
        server.shutdown(); server.server_close()
    viewport = story['layout']['television']
    x,y,w,h = [viewport[k] for k in ['x','y','w','h']]
    video = ART / 'videos/sixties-lifestyle.mp4'
    crops=[]; entries=[]; output=ART/'images/motion'; output.mkdir(parents=True, exist_ok=True)
    source = frame(ART/'panels/communication-tv.mp4', times[0])
    comparisons=[]
    for index,(t,state) in enumerate(zip(times,samples,strict=True)):
        # Snap to the same output frame clock as the native encoder.
        exact = int((scene['start']+t)*story['fps']+1e-6)/story['fps']
        image = frame(video, exact); crop=image.crop((x,y,x+w,y+h)); crops.append(crop)
        file=output/f'television-{index}.jpg'; image.save(file, quality=94); entries.append((file,f'TV {t:.2f}s | scale {state["gentle"]["camera"]["scale"]:.3f}'))
        camera=state['gentle']['camera']; scale=camera['scale']
        sx,sy=camera['sourceX'],camera['sourceY']
        expected=source.crop((sx,sy,sx+w/scale,sy+h/scale)).resize((w,h),Image.Resampling.LANCZOS)
        # Integer chroma and native zoompan rounding differ slightly from PIL.
        # Blur/downsample only for this independent structural parity measure.
        actual_array=np.asarray(crop.resize((140,105),Image.Resampling.LANCZOS),dtype=float)
        expected_array=np.asarray(expected.resize((140,105),Image.Resampling.LANCZOS),dtype=float)
        baseline=np.asarray(source.resize((140,105),Image.Resampling.LANCZOS),dtype=float)
        comparisons.append({'localSeconds':t,'scale':scale,'expectedMeanAbsoluteDifference':float(np.abs(actual_array-expected_array).mean()),'unzoomedMeanAbsoluteDifference':float(np.abs(actual_array-baseline).mean())})
    sheet(entries,ART/'images/encoded-detail-motion.jpg',columns=2)
    for row in comparisons:
        if row['expectedMeanAbsoluteDifference']>10: raise ValueError('Native detail differs from the reviewed camera.')
    for row in comparisons[1:3]:
        if row['expectedMeanAbsoluteDifference']>=row['unzoomedMeanAbsoluteDifference']: raise ValueError('Encoded detail did not perform the intended zoom.')
    if any(f['first']==f['last'] for f in floats): raise ValueError('A floating concept group did not move.')
    result={'ok':True,'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'cameraSamples':comparisons,'floatSamples':floats,'scope':'Independent structural camera parity and source transforms. Contact sheet still needs human review. No comfort guarantee or listening pass.'}
    (ART/'reviews/gentle-movie-motion.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':True,'cameraSamples':comparisons,'floatingGroups':len(floats)}))


if __name__=='__main__': main()

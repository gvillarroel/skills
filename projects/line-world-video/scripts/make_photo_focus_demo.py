#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Demonstrate original-color focus using the reviewed cached component photos."""
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / 'skills/line-world-video'
SOURCE = ROOT / 'projects/cuda-alexnet-vids/artifacts/media/objects'
OUTPUT = ROOT / 'projects/line-world-video/artifacts/photo-focus-demo'


def main():
    media = OUTPUT / 'media'; media.mkdir(parents=True, exist_ok=True)
    records = [a for a in json.loads((SOURCE / 'manifest.json').read_text())['assets'] if a['id'] in ['cpu', 'gtx580']]
    for a in records:
        for file in [a['id'] + '.prepared.png', a['id'] + '-gray.png', a['original']]:
            target = media / file; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(SOURCE / file, target)
    (media / 'manifest.json').write_text(json.dumps({'assets': records}, indent=2) + '\n')
    (media / 'credits.json').write_text(json.dumps([{'id': a['id'], 'sourcePage': a['sourcePage'], 'rights': a['rights'], 'scope': a['scope']} for a in records], indent=2) + '\n')
    bindings = {'bindings': [
        {'id': 'cpu', 'target': '#cpu-photo', 'asset': 'cpu', 'variant': 'gray', 'transition': .35, 'windows': [{'start': .6, 'end': 3.5}]},
        {'id': 'gpu', 'target': '#gpu-photo', 'asset': 'gtx580', 'variant': 'gray', 'transition': .35, 'windows': [{'start': 4.1, 'end': 7.5}]}
    ]}
    (OUTPUT / 'bindings.json').write_text(json.dumps(bindings, indent=2) + '\n')
    subprocess.run(['uv', 'run', '--script', str(SKILL / 'scripts/photo_focus.py'), 'plan', '--manifest', str(media / 'manifest.json'), '--bindings', str(OUTPUT / 'bindings.json'), '--html-root', str(OUTPUT), '--output', str(OUTPUT / 'photo-focus.json')], check=True)
    plan = json.loads((OUTPUT / 'photo-focus.json').read_text())
    shutil.copyfile(SKILL / 'assets/runtime/photo-focus.js', OUTPUT / 'photo-focus.js')
    html = '''<!doctype html><html lang="es"><meta charset="utf-8"><style>body{margin:0;background:white}svg{display:block;width:100vw;height:100vh}text{font:30px Arial;fill:#333e48}</style>
<svg id="stage" viewBox="0 0 1920 1080" role="img" aria-label="Componentes fotográficos con color original solamente durante el foco">
<path d="M960 0V1080" fill="none" stroke="#cfcfcf" stroke-width="1.5"/>
<image id="cpu-photo" data-documentary-id="cpu" x="275" y="320" width="410" height="460" href="media/cpu-gray.png" preserveAspectRatio="xMidYMid meet"/>
<text x="480" y="850" text-anchor="middle">CPU</text>
<image id="gpu-photo" data-documentary-id="gtx580" x="1140" y="340" width="600" height="440" href="media/gtx580-gray.png" preserveAspectRatio="xMidYMid meet"/>
<text x="1440" y="850" text-anchor="middle">GTX 580</text>
<circle id="guide" cx="725" cy="550" r="10" fill="#9e1b32"/></svg>
<script src="photo-focus.js"></script><script>
window.PHOTO_FOCUS_PLAN=PLAN;
const photos=LineWorldPhotoFocus.attach(document.querySelector('#stage'),PHOTO_FOCUS_PLAN.bindings);
const ease=q=>{q=Math.max(0,Math.min(1,q));return q*q*(3-2*q)};
window.renderAt=t=>{const guide=document.querySelector('#guide'),travel=ease((t-3.5)/.6);guide.setAttribute('cx',725+380*travel);guide.style.opacity=String(Math.min(ease((t-.3)/.3),1-ease((t-7.3)/.2)));return{seconds:t,photos:photos.render(t)}};
window.ready=Promise.all([document.fonts.ready,photos.ready]).then(()=>renderAt(0));
</script></html>'''.replace('PLAN;', json.dumps(plan) + ';')
    (OUTPUT / 'scene.html').write_text(html, encoding='utf-8')
    subprocess.run(['uv', 'run', '--script', str(SKILL / 'scripts/photo_focus.py'), 'inspect', '--html', str(OUTPUT / 'scene.html'), '--plan', str(OUTPUT / 'photo-focus.json'), '--output', str(OUTPUT / 'photo-review.json'), '--screenshot', str(OUTPUT / 'poster.png'), '--video', str(OUTPUT / 'photo-focus-demo.mp4'), '--duration', '9'], check=True)
    for name, time in [('neutral', .1), ('cpu-color', 2), ('gpu-color', 5.5), ('neutral-return', 8.4)]:
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(time), '-i', str(OUTPUT / 'photo-focus-demo.mp4'), '-frames:v', '1', '-update', '1', str(OUTPUT / (name + '.png'))], check=True)
    print(json.dumps({'ok': True, 'video': str(OUTPUT / 'photo-focus-demo.mp4'), 'seconds': 9, 'audio': False}))


if __name__ == '__main__': main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Materialize the project-owned D3 continuous-canvas composition."""
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
REPO=ROOT.parent.parent
out=ROOT/'artifacts/composition'
out.mkdir(parents=True,exist_ok=True)
for name in ['d3.min.js']:
    if not (out/name).is_file():shutil.copyfile(REPO/'skills/line-world-video/assets/vendor'/name,out/name)
for name in ['space-grotesk.ttf','OFL.txt']:
    if not (out/name).is_file():shutil.copyfile(REPO/'skills/line-world-video/assets/fonts'/name,out/name)
if not (out/'D3-LICENSE.txt').is_file():shutil.copyfile(REPO/'skills/line-world-video/assets/vendor/D3-LICENSE.txt',out/'D3-LICENSE.txt')
data=json.loads((ROOT/'artifacts/data/experiment.json').read_text())
(out/'data.js').write_text('window.DATA='+json.dumps(data)+';\n',encoding='utf-8')
story=json.loads((ROOT/'story.json').read_text(encoding='utf-8-sig'))
(out/'story.js').write_text('window.PRODUCTION='+json.dumps(story,ensure_ascii=False)+';\n',encoding='utf-8')
shutil.copyfile(ROOT/'scripts/scene.js',out/'scene.js')
for name in ['theme.js','theme.css','visual-review.js','focus-motion.js','photo-focus.js','scene-effects.js']:
    source=REPO/'skills/line-world-video/assets/runtime'/name
    if source.is_file():shutil.copyfile(source,out/name)
    elif not (out/name).is_file():raise ValueError('The portable project needs its bundled '+name)
focus=REPO/'skills/line-world-video/assets/runtime/focus.js'
if focus.is_file():shutil.copyfile(focus,out/'focus.js')
elif not (out/'focus.js').is_file():raise ValueError('The portable project needs its bundled focus.js.')
cues=json.loads((ROOT/'artifacts/revision/cues.json').read_text(encoding='utf-8'))
(out/'cues.js').write_text('window.NARRATION_CUES='+json.dumps(cues,ensure_ascii=False)+';\n',encoding='utf-8')
(out/'index.html').write_text('''<!doctype html><html lang="es"><meta charset="utf-8"><title>ML visual composition</title><link rel="stylesheet" href="theme.css"><style>@font-face{font-family:Space Grotesk;src:url(space-grotesk.ttf)}html,body{margin:0;overflow:hidden;background:white}svg{display:block;width:100vw;height:100vh}</style><svg id="stage" xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"></svg><script src="d3.min.js"></script><script src="data.js"></script><script src="story.js"></script><script src="cues.js"></script><script src="focus.js"></script><script src="visual-review.js"></script><script src="theme.js"></script><script src="scene.js"></script></html>''',encoding='utf-8')
shutil.copyfile(ROOT/'scripts/effects.js',out/'effects.js')
html=(out/'index.html').read_text(encoding='utf-8')
html=html.replace('<script src="scene.js"></script>', '<script src="focus-motion.js"></script><script src="photo-focus.js"></script><script src="scene-effects.js"></script><script src="scene.js"></script><script src="effects.js"></script>')
(out/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'ok':True,'output':str(out)}))
preview=(out/'index.html').read_text(encoding='utf-8').replace('<svg id="stage"','<div id="viewer"><svg id="stage"').replace('</svg>','</svg></div><div id="controls"><button id="play">Play</button> <select id="scene"></select> <input id="seek" type="range" min="0" step="0.01" value="0"> <output id="clock"></output></div>')
preview=preview.replace('</style>','''#viewer{width:min(100vw,1280px);aspect-ratio:16/9;margin:auto}#stage{width:100%;height:100%}html,body{overflow:auto;background:#f7f7f7}#controls{box-sizing:border-box;max-width:1280px;margin:16px auto;padding:12px;font:16px Arial;display:flex;gap:12px;align-items:center}#seek{flex:1}</style>''')
preview=preview.replace('</html>','''<script>document.fonts.ready.then(()=>{prepareFocus();let scene=0,time=0,playing=false,last=0;const pick=document.querySelector('#scene'),seek=document.querySelector('#seek'),clock=document.querySelector('#clock'),play=document.querySelector('#play');PRODUCTION.scenes.forEach((s,i)=>{let o=document.createElement('option');o.value=i;o.textContent=(i+1)+' · '+s.id;pick.append(o)});function draw(){seek.max=PRODUCTION.scenes[scene].clipSeconds;seek.value=time;clock.textContent=time.toFixed(2)+' / '+Number(seek.max).toFixed(2)+' s';renderAt(scene,time)}pick.onchange=()=>{scene=+pick.value;time=0;draw()};seek.oninput=()=>{time=+seek.value;draw()};play.onclick=()=>{playing=!playing;play.textContent=playing?'Pause':'Play'};function tick(now){if(playing&&last){time+=Math.min(.1,(now-last)/1000);if(time>=+seek.max){if(scene<11){scene++;pick.value=scene;time=0}else{time=+seek.max;playing=false;play.textContent='Play'}}draw()}last=now;requestAnimationFrame(tick)}draw();requestAnimationFrame(tick)});</script></html>''')
preview=preview.replace('document.fonts.ready.then(()=>{prepareFocus();','window.ready.then(()=>{')
(out/'preview.html').write_text(preview,encoding='utf-8')

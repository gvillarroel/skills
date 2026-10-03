#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Render the authored vector-field geometry with evaluator-only scene handles."""
import argparse,json,threading,http.server,functools,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/arrow-contrast-custom/artifacts'
parser=argparse.ArgumentParser();parser.add_argument('--phase',default='after',choices=('before','after'));args=parser.parse_args()
for sub in ('data','screenshots'): (OUT/sub).mkdir(parents=True,exist_ok=True)
source=ROOT/'skills/threejs-animated-3d/assets/examples/threejs-animated-3d'
main=(source/'src/main.js').read_text(encoding='utf-8').replace("import './styles.css'",'').replace('return { id: example.id, replay, render, dispose }','return { id: example.id, replay, render, dispose, scene, root, camera, state }').replace('  requestAnimationFrame(animate)','  // evaluator freezes the gallery loop')
(OUT/'data/three-instrumented.js').write_text(main,encoding='utf-8')
html=(source/'index.html').read_text(encoding='utf-8').replace('<script type="module" src="./src/main.js"></script>','<link rel="stylesheet" href="/skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/styles.css"><script type="importmap">{"imports":{"three":"/skills/threejs-animated-3d/assets/vendor/three.module.min.js"}}</script><script type="module" src="./three-instrumented.js"></script>')
(OUT/'data/three-instrumented.html').write_text(html,encoding='utf-8')
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
records=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge',args=['--enable-webgl','--use-gl=angle','--use-angle=swiftshader'])
 page=browser.new_page(viewport={'width':1600,'height':1100})
 page.goto(f'http://127.0.0.1:{server.server_port}/projects/arrow-contrast-custom/artifacts/data/three-instrumented.html')
 page.wait_for_function('window.__threeGalleryReady')
 card=page.locator('article[data-example-id="vector-field"]');card.scroll_into_view_if_needed()
 for second in (0,1,2,3,4):
  result=page.evaluate("""second=>{
   const instance=window.__threeGalleryScenes.find(s=>s.id==='vector-field');
   const arrows=instance.root.children.filter(o=>o.isGroup&&o.children.some(c=>c.geometry?.type==='ConeGeometry'));
   const canvas=document.querySelector('[data-example-id="vector-field"] canvas'),context=canvas.getContext('2d');
   instance.render(instance.state.startTime+second*1000);instance.scene.updateMatrixWorld(true);
   const samples=arrows.map(arrow=>{const head=arrow.children.find(c=>c.geometry.type==='ConeGeometry');const p=head.localToWorld(head.position.clone().set(0,.055,0)).project(instance.camera);return {x:Math.round((p.x+1)*canvas.width/2),y:Math.round((1-p.y)*canvas.height/2),color:'#'+head.material.color.getHexString()};});
   const pixel=p=>Array.from(context.getImageData(p.x,p.y,1,1).data).slice(0,3); const patch=p=>{const values=context.getImageData(p.x-1,p.y-1,3,3).data;return Array.from({length:9},(_,i)=>Array.from(values.slice(i*4,i*4+3)));};
   samples.forEach(p=>{p.actual=pixel(p);p.interiorPatch=patch(p)});arrows.forEach(a=>a.visible=false);instance.render(instance.state.startTime+second*1000);
   samples.forEach(p=>p.backing=pixel(p));arrows.forEach(a=>a.visible=true);instance.render(instance.state.startTime+second*1000);
   return {second,samples};
  }""",second)
  records.append(result)
  if second in (0,2,4):card.screenshot(path=str(OUT/'screenshots'/f'three-vector-field-{args.phase}-{second}.png'))
 browser.close()
server.shutdown()
def lum(rgb): return sum((v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4)*w for v,w in zip(rgb,(.2126,.7152,.0722)))
for record in records:
 for sample in record['samples']:
  a,b=lum(sample['actual']),lum(sample['backing']);sample['contrast']=(max(a,b)+.05)/(min(a,b)+.05)
  wanted=[int(sample['color'][i:i+2],16) for i in (1,3,5)];closest=min(sample['interiorPatch'],key=lambda pixel:sum((a-b)**2 for a,b in zip(pixel,wanted)))
  sample['interiorContrast']=(max(lum(closest),b)+.05)/(min(lum(closest),b)+.05);sample['distanceToMaterial']=math.sqrt(sum((a-b)**2 for a,b in zip(closest,wanted)))
report={'phase':args.phase,'records':records,'failingSamples':sum(s['interiorContrast']<3 or s['distanceToMaterial']>=80 for r in records for s in r['samples'])}
(OUT/'data'/f'three-vector-field-{args.phase}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
compact={'date':'2026-10-03','phase':args.phase,'sampleCount':sum(len(r['samples']) for r in records),'failingSamples':report['failingSamples'],'rows':[{'second':r['second'],'headCount':len(r['samples']),'minimumInteriorContrast':min(s['interiorContrast'] for s in r['samples']),'maximumPaintDistance':max(s['distanceToMaterial'] for s in r['samples'])} for r in records]}
(ROOT/f'evaluations/arrow-contrast-custom/three-field-{args.phase}-20261003.json').write_text(json.dumps(compact,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'phase':args.phase,'sampleCount':sum(len(r['samples']) for r in records),'failingSamples':report['failingSamples']}))
raise SystemExit(0 if report['failingSamples']==0 else 1)

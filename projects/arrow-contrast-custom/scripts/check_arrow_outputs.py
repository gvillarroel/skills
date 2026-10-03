#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Inspect actual arrows, exports and motion states independently of the builders."""
import json,subprocess,importlib.util,sys,math,argparse
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-custom/artifacts';EVIDENCE=ROOT/'evaluations/arrow-contrast-custom'
for folder in (OUT/'data',OUT/'screenshots',OUT/'svgs',EVIDENCE):folder.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--d3-only',action='store_true');args=parser.parse_args()
def run(*argv):
 completed=subprocess.run(['uv','run','--script',*argv],cwd=ROOT,capture_output=True,text=True,encoding='utf-8');assert completed.returncode==0,completed.stdout+completed.stderr
 return completed.stdout
for palette in ('colorset1','colorset2'):
 if not args.d3_only:run('skills/threejs-animated-3d/scripts/build_standalone_threejs.py',str(OUT/'data'/f'field-{palette}.html'),'--scene','vector-field','--token-count','20','--colorset',palette,'--force')
 for kind,builder in (('pid','build_process_pid_control_loop.py'),('bowtie','build_critical_bowtie_barrier.py')):
  run('skills/d3/scripts/'+builder,str(OUT/'data'/f'{kind}-{palette}.html'),'--colorset',palette)
 if not args.d3_only:run('skills/procedural-svg-animation/scripts/build_procedural_svg.py','procedural-svg-vector-field','--output',str(OUT/'svgs'/f'vectors-{palette}.svg'),'--palette',palette,'--motion','reduced','--force')
def lum(rgb):return sum((v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4)*w for v,w in zip(rgb,(.2126,.7152,.0722)))
def ratio(a,b):return (max(lum(a),lum(b))+.05)/(min(lum(a),lum(b))+.05)
rows=[];errors=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge',args=['--enable-webgl','--use-gl=angle','--use-angle=swiftshader'])
 for palette in ('colorset1','colorset2'):
  for width,motion in ((1280,'no-preference'),(390,'no-preference'),(1280,'reduce')):
   if args.d3_only:continue
   page=browser.new_page(viewport={'width':width,'height':900},reduced_motion=motion);page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto((OUT/'data'/f'field-{palette}.html').as_uri());page.wait_for_function('window.__threeRuntimeSceneReady')
   page.locator('#replay').focus()
   for second in ((0,) if motion=='reduce' else (0,1.7,3.2)):
    samples=page.evaluate('s=>window.__threeRuntimeScene.arrowPixelSamples(s)',second)
    for sample in samples:
     wanted=[int(sample['color'][i:i+2],16) for i in (1,3,5)]
     closest=min(sample['interiorPatch'],key=lambda pixel:sum((a-b)**2 for a,b in zip(pixel,wanted)))
     sample['interiorContrast']=ratio(closest,sample['backing']);sample['distanceToMaterial']=math.sqrt(sum((a-b)**2 for a,b in zip(closest,wanted)))
    rows.append({'route':'three-runtime','palette':palette,'width':width,'motion':motion,'second':second,'sampleCount':len(samples),'minimumInteriorContrast':min(s['interiorContrast'] for s in samples),'maximumPaintDistance':max(s['distanceToMaterial'] for s in samples),'samples':samples,'passed':all(s['interiorContrast']>=3 and s['distanceToMaterial']<80 for s in samples)})
   page.screenshot(path=str(OUT/'screenshots'/f'field-{palette}-{width}-{motion}.png'))
   page.close()
  for kind in ('pid','bowtie'):
   for motion in ('no-preference','reduce'):
    page=browser.new_page(viewport={'width':1280,'height':900},reduced_motion=motion);page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((OUT/'data'/f'{kind}-{palette}.html').as_uri());page.wait_for_function("document.querySelector('svg').dataset.fillStyle==='solid-first'");page.wait_for_timeout(2500)
    for helper in ('arrow_audit.ts','glyph_audit.ts','label_audit.ts'):page.evaluate(Path(__file__).with_name(helper).read_text(encoding='utf-8'))
    for second in (3.1,4.8,6.2):
     page.locator('svg').evaluate('(svg,t)=>{svg.pauseAnimations();svg.setCurrentTime(t)}',second)
     page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
     arrows=page.evaluate('window.auditRenderedArrows()');glyphs=page.evaluate('window.auditDirectionalGlyphs()');glyph_low=sum(min(g.get('contrast',21),g.get('headContrast',21),g.get('shaftContrast',21))<3 for g in glyphs)
     ports=[a['targetPortAudit'] for a in arrows if a['targetPortAudit']];labels=page.evaluate('window.auditInstrumentLabels()');callouts=page.evaluate('window.auditCalloutLabels()')
     rows.append({'route':'d3-production','kind':kind,'palette':palette,'motion':motion,'second':second,'arrowCount':len(arrows),'glyphCount':len(glyphs),'glyphLow':glyph_low,'targetPorts':ports,'instrumentLabels':labels,'calloutLabels':callouts,'headLow':sum(a['headContrast']<3 for a in arrows),'shaftLow':sum(a['shaftMinimumContrast']<3 for a in arrows),'hiddenHeads':sum(a['headHidden'] for a in arrows),'unresolved':[a['unresolved'] for a in arrows if a['unresolved']],'passed':not glyph_low and all(p['passed'] for p in ports) and all(label['passed'] for label in labels+callouts) and (kind!='pid' or len(labels)==8) and (kind!='bowtie' or len(callouts)==2) and all(a['headContrast']>=3 and a['shaftMinimumContrast']>=3 and not a['headHidden'] and not a['unresolved'] for a in arrows),'arrows':arrows,'glyphs':glyphs})
    svg=page.locator('svg').evaluate('svg=>svg.outerHTML');svg=svg if 'xmlns=' in svg.split('>')[0] else svg.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" ',1)
    output=OUT/'svgs'/f'{kind}-{palette}-{motion}-export.svg';output.write_text(svg,encoding='utf-8')
    page.screenshot(path=str(OUT/'screenshots'/f'{kind}-{palette}-{motion}.png'))
    page.goto(output.as_uri());page.wait_for_timeout(2500)
    for helper in ('arrow_audit.ts','label_audit.ts'):page.evaluate(Path(__file__).with_name(helper).read_text(encoding='utf-8'))
    arrows=page.evaluate('window.auditRenderedArrows()');ports=[a['targetPortAudit'] for a in arrows if a['targetPortAudit']];labels=page.evaluate('window.auditInstrumentLabels()');callouts=page.evaluate('window.auditCalloutLabels()');rows.append({'route':'d3-export','kind':kind,'palette':palette,'motion':motion,'arrowCount':len(arrows),'targetPorts':ports,'instrumentLabels':labels,'calloutLabels':callouts,'headLow':sum(a['headContrast']<3 for a in arrows),'shaftLow':sum(a['shaftMinimumContrast']<3 for a in arrows),'hiddenHeads':sum(a['headHidden'] for a in arrows),'passed':all(p['passed'] for p in ports) and all(label['passed'] for label in labels+callouts) and (kind!='pid' or len(labels)==8) and (kind!='bowtie' or len(callouts)==2) and all(a['headContrast']>=3 and a['shaftMinimumContrast']>=3 and not a['headHidden'] for a in arrows)})
    page.close()
  if args.d3_only:continue
  page=browser.new_page(viewport={'width':1100,'height':800});page.goto((OUT/'svgs'/f'vectors-{palette}.svg').as_uri())
  marks=page.locator('[data-direction-role="vector-line"]').evaluate_all("es=>es.map(e=>({stroke:getComputedStyle(e).stroke,opacity:getComputedStyle(e).opacity,x1:e.getAttribute('x1'),y1:e.getAttribute('y1'),x2:e.getAttribute('x2'),y2:e.getAttribute('y2')}))")
  ratios=[ratio([int(v) for v in m['stroke'][4:-1].split(',')],[255,255,255]) for m in marks]
  rows.append({'route':'procedural-reduced','palette':palette,'lineCount':len(marks),'headCount':page.locator('[marker-end]').count(),'minimumContrast':min(ratios),'passed':len(marks)==135 and min(ratios)>=3 and all(float(m['opacity'])==1 for m in marks)})
  page.screenshot(path=str(OUT/'screenshots'/f'vectors-{palette}.png'));page.close()
 browser.close()
report={'date':'2026-10-03','passed':all(row['passed'] for row in rows) and not errors,'errors':errors,'rows':rows}
stem='focused-d3-check' if args.d3_only else 'focused-arrow-check'
(OUT/f'data/{stem}.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
compact={**report,'rows':[{k:v for k,v in row.items() if k not in ('samples','arrows','glyphs')} for row in rows]}
(EVIDENCE/f'{stem}-20261003.json').write_text(json.dumps(compact,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'rowCount':len(rows),'failures':[{k:v for k,v in row.items() if k not in ('samples','arrows')} for row in rows if not row['passed']],'errors':errors},indent=2))
raise SystemExit(0 if report['passed'] else 1)

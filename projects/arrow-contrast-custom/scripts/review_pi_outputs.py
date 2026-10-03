#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Bind independent arrow artifacts to immutable strict runtime payloads."""
import hashlib,importlib.util,json,math,xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-custom/artifacts';EVIDENCE=ROOT/'evaluations/arrow-contrast-custom'
spec=importlib.util.spec_from_file_location('harness',ROOT/'scripts/run-pi-skill-eval.py');HARNESS=importlib.util.module_from_spec(spec);spec.loader.exec_module(HARNESS)
SKILLS=('d3','threejs-animated-3d','procedural-svg-animation','svg-brief-design','vectorize-art-patterns')
def payload(skill):
 tree=HARNESS.snapshot_tree(ROOT/'skills'/skill)
 tree={k:v for k,v in tree.items() if not any(p in HARNESS.COPY_IGNORE for p in Path(k).parts) and not k.startswith('assets/examples/')}
 return {'fileCount':len(tree),'payloadSha256':HARNESS.snapshot_digest(tree)}
def lum(rgb):return sum((v/255/12.92 if v/255<=.04045 else ((v/255+.055)/1.055)**2.4)*w for v,w in zip(rgb,(.2126,.7152,.0722)))
def ratio(a,b):return (max(lum(a),lum(b))+.05)/(min(lum(a),lum(b))+.05)
def rgb(color):return [int(color[i:i+2],16) for i in (1,3,5)]
payloads={skill:payload(skill) for skill in SKILLS};records=[];errors=[]
with sync_playwright() as engine:
 browser=engine.chromium.launch(channel='msedge',args=['--enable-webgl','--use-gl=angle','--use-angle=swiftshader'])
 for folder in sorted((ROOT/'evaluations/runs').glob('custom-arrow-*-20261003-luna-*')):
  if not (folder/'evaluation-result.json').is_file():continue
  manifest=json.loads((folder/'run-manifest.json').read_text(encoding='utf-8'));result=json.loads((folder/'evaluation-result.json').read_text(encoding='utf-8'));events=json.loads((folder/'event-check.json').read_text(encoding='utf-8'));skill=manifest['skill']['name'];workspace=folder/'workspace'
  record={'runId':folder.name,'skill':skill,'strictPassed':result['passed'],'payloadSha256':manifest['skill']['payloadSha256'],'matchesFinalPayload':manifest['skill']['payloadSha256']==payloads[skill]['payloadSha256'],'observedModels':events['observedModels'],'toolErrorCount':sum(call['isError'] for call in events['calls']),'readSurface':[call['path'] for call in events['calls'] if call['tool']=='read'],'gates':result['gates'],'durationSeconds':result['durationSeconds'],'artifactPassed':False,'outputs':{name:{'sizeBytes':(workspace/name).stat().st_size,'sha256':hashlib.sha256((workspace/name).read_bytes()).hexdigest()} for name in manifest['expectedOutputs'] if (workspace/name).is_file()}}
  try:
   assert record['strictPassed'] and record['toolErrorCount']==0
   page=browser.new_page(viewport={'width':1280,'height':900});page_errors=[];page.on('pageerror',lambda error:page_errors.append(str(error)))
   if skill=='d3':
    inspections=[]
    for name in ('pid-cs1.html','pid-cs2.html'):
     page.goto((workspace/name).as_uri());page.wait_for_function("document.querySelector('svg').dataset.fillStyle==='solid-first'");page.wait_for_timeout(3200)
     for helper in ('arrow_audit.ts','glyph_audit.ts','label_audit.ts'):page.evaluate(Path(__file__).with_name(helper).read_text(encoding='utf-8'))
     for second in (3.1,4.8,6.2):
      page.locator('svg').evaluate('(svg,t)=>{svg.pauseAnimations();svg.setCurrentTime(t)}',second);page.evaluate('()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
      arrows=page.evaluate('window.auditRenderedArrows()');glyphs=page.evaluate('window.auditDirectionalGlyphs()')
      assert len(arrows)==6 and len(glyphs)==1
      assert all(a['headContrast']>=3 and a['shaftMinimumContrast']>=3 and not a['headHidden'] and not a['unresolved'] for a in arrows),arrows
      ports=[a['targetPortAudit'] for a in arrows if a['targetPortAudit']];assert len(ports)==1 and all(p['passed'] for p in ports),ports
      assert all(g['contrast']>=3 and not g['unresolved'] for g in glyphs),glyphs
      labels=page.evaluate('window.auditInstrumentLabels()');assert len(labels)==8 and all(label['passed'] for label in labels),labels
      inspections.append({'output':name,'second':second,'markerArrowCount':len(arrows),'glyphCount':len(glyphs),'targetPorts':ports,'instrumentLabels':labels,'minimumHeadContrast':min(a['headContrast'] for a in arrows),'minimumShaftContrast':min(a['shaftMinimumContrast'] for a in arrows),'glyphMinimumContrast':min(g['contrast'] for g in glyphs)})
     page.screenshot(path=str(OUT/'screenshots'/f'{folder.name}-{name}.png'))
    record['inspection']=inspections
   elif skill=='threejs-animated-3d':
    samples=[]
    for motion in ('no-preference','reduce'):
     page.emulate_media(reduced_motion=motion);page.goto((workspace/'field.html').as_uri());page.wait_for_function('window.__threeRuntimeSceneReady');page.locator('#replay').focus()
     observed=page.evaluate('window.__threeRuntimeScene.inspect()');assert observed['tokenCount']==20 and observed['decorativeOutlineCount']==0
     assert page.locator('h1').inner_text()=='Directed flow'
     for second in ((0,) if motion=='reduce' else (0,1.7,3.2)):
      actual=page.evaluate('s=>window.__threeRuntimeScene.arrowPixelSamples(s)',second);assert len(actual)==40
      for sample in actual:
       wanted=rgb(sample['color']);closest=min(sample['interiorPatch'],key=lambda pixel:sum((a-b)**2 for a,b in zip(pixel,wanted)))
       assert ratio(closest,sample['backing'])>=3 and math.sqrt(sum((a-b)**2 for a,b in zip(closest,wanted)))<80,sample
      samples.append({'motion':motion,'second':second,'pixelSampleCount':len(actual),'minimumInteriorContrast':min(ratio(min(s['interiorPatch'],key=lambda p:sum((a-b)**2 for a,b in zip(p,rgb(s['color'])))),s['backing']) for s in actual)})
     page.screenshot(path=str(OUT/'screenshots'/f'{folder.name}-{motion}.png'))
    record['inspection']=samples
   elif skill=='svg-brief-design':
    checks=[]
    for name,backing,paint in (('light.svg','#ffffff','rgb(0, 0, 0)'),('dark.svg','#1c1c1c','rgb(255, 255, 255)')):
     page.goto((workspace/name).as_uri());marks=page.locator('rect[id^="node-"]').evaluate_all("es=>es.map(e=>({fill:getComputedStyle(e).fill,stroke:getComputedStyle(e).stroke,x:+e.getAttribute('x'),width:+e.getAttribute('width')}))")
     labels=page.locator('text').evaluate_all("es=>es.map(e=>getComputedStyle(e).fill)")
     arrows=page.locator('[data-direction-role]').evaluate_all("es=>es.map(e=>({stroke:getComputedStyle(e).stroke,fill:getComputedStyle(e).fill,role:e.dataset.directionRole,x1:+e.getAttribute('x1'),x2:+e.getAttribute('x2')}))")
     assert len(marks)==3 and all(m['fill']=='rgb(241, 195, 25)' and m['stroke']=='none' for m in marks)
     assert all(label=='rgb(0, 0, 0)' for label in labels) and len(arrows)==4 and all(a['stroke']==paint for a in arrows)
     shafts=[a for a in arrows if a['role']=='shaft'];assert all(a['x1']-marks[i]['x']-marks[i]['width']>=4 and marks[i+1]['x']-a['x2']>=4 for i,a in enumerate(shafts))
     assert all(a['fill']=='none' for a in arrows if a['role']=='head')
     checks.append({'output':name,'arrowCount':2,'tipClearance':4,'contrast':ratio(rgb('#000000' if name=='light.svg' else '#ffffff'),rgb(backing))})
     page.screenshot(path=str(OUT/'screenshots'/f'{folder.name}-{name}.png'))
    record['inspection']=checks
   elif skill=='procedural-svg-animation':
    geometry=[];checks=[]
    for name in ('field.svg','field-static.svg'):
     root=ET.parse(workspace/name).getroot();assert root.get('data-pattern-id')=='procedural-svg-vector-field' and root.get('data-palette')=='colorset2' and root.get('data-seed')=='89' and root.get('data-duration-ms')=='4000'
     art=next(e for e in root.iter() if e.get('data-role')=='procedural-art')
     marks=[e for e in art.iter() if e.get('data-direction-role')=='vector-line'];assert len(marks)==135,{'output':name,'firstArtLineCount':len(marks)}
     geometry.append([{key:e.get(key) for key in ('x1','x2','y1','y2','stroke')} for e in marks])
     assert all(ratio(rgb(e.get('stroke')),[255,255,255])>=3 for e in marks)
     assert not any(e.get('marker-end') for e in root.iter())
     if name=='field-static.svg':assert not any(e.tag.split('}')[-1].startswith('animate') for e in root.iter())
     page.goto((workspace/name).as_uri());page.screenshot(path=str(OUT/'screenshots'/f'{folder.name}-{name}.png'))
     checks.append({'output':name,'bareLineCount':len(marks),'headCount':0,'minimumFullEmphasisContrast':min(ratio(rgb(e.get('stroke')),[255,255,255]) for e in marks)})
    assert geometry[0]==geometry[1],'Geometry/paint differ between primary animated art and static output';record['geometryPreservedAcrossMotionModes']=True;record['inspection']=checks
   assert not page_errors,page_errors;record['browserErrors']=page_errors;record['artifactPassed']=True;page.close()
  except Exception as error:record['artifactError']=str(error)
  if not record['matchesFinalPayload']:record['superseded']=True
  records.append(record)
 browser.close()
summary={'date':'2026-10-03','finalPayloads':payloads,'attempts':records,'strictPasses':sum(r['strictPassed'] for r in records),'jointCurrentPasses':sum(r['strictPassed'] and r['matchesFinalPayload'] and r['artifactPassed'] for r in records),'behaviorChangedBundles':list(SKILLS[:-1]),'inventoryOnlyBundle':'vectorize-art-patterns'}
(EVIDENCE/'results-20261003.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='attempts'},indent=2))
for record in records:print(json.dumps({k:v for k,v in record.items() if k not in ('readSurface','outputs','inspection')}))

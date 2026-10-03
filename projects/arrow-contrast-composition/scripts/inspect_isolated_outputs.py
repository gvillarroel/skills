#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "Pillow>=11,<13"]
# ///
"""Seal strict current-payload cases and independently inspect actual visual outputs."""
import importlib.util,json,hashlib,subprocess,functools,http.server,threading,xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-composition/artifacts/pi-inspection';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('pi_harness',ROOT/'scripts/run-pi-skill-eval.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
results=[]
def jread(p):return json.loads(p.read_text(encoding='utf-8'))
def arrows(value):
 if isinstance(value,dict):
  if 'shaftCount' in value and 'records' in value:yield value
  else:
   for x in value.values():yield from arrows(x)
 elif isinstance(value,list):
  for x in value:yield from arrows(x)
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1200})
 for case in jread(ROOT/'evaluations/arrow-contrast-composition/isolated-retry-20261003.json'):
  if case['exitCode'] or case.get('traceExitCode',0):continue
  skill=case['skill'];run=ROOT/'evaluations/runs'/case['runId'];workspace=run/'workspace';manifest=jread(run/'run-manifest.json');evaluation=jread(run/'evaluation-result.json')
  assert evaluation['passed'] and all(evaluation['gates'][k] for k in ['events','artifacts','skillIntegrity']),evaluation
  source=h.snapshot_tree(ROOT/'skills'/skill);source={p:v for p,v in source.items() if not any(part in h.COPY_IGNORE for part in Path(p).parts) and not Path(p).is_relative_to(Path('assets/examples'))}
  digest=h.snapshot_digest(source);assert digest==manifest['skill']['payloadSha256'],(skill,digest,manifest['skill'])
  copied=h.snapshot_tree(workspace/'skills'/skill);assert copied==source,skill
  outputs={p:{'sizeBytes':(workspace/p).stat().st_size,'sha256':h.sha256_file(workspace/p)} for p in case['expectedOutputs']}
  artifact=jread(run/'artifact-check.json')
  expected_checks=artifact.get('outputs',artifact.get('artifacts',[]))
  for check in expected_checks:
   if check.get('sha256'):assert outputs[check['path']]['sha256']==check['sha256'],check
  reports=[]
  for p in (workspace/'output').glob('*.json'):
   for report in arrows(jread(p)):
    assert not report['issues'],(p,report['issues']);reports.append({'path':p.relative_to(workspace).as_posix(),'shafts':report['shaftCount'],'heads':report['headCount'],'minimum':min((x['minimum'] for x in report['records'] if x.get('minimum') is not None),default=None)})
  independent=[]
  if skill in ['compose-synchronized-svg','diagram-composition','usefulcharts-style']:
   svg=workspace/('output/poster.svg' if skill=='usefulcharts-style' else 'output/diagram.svg')
   page.set_viewport_size({'width':1800,'height':2700} if skill=='usefulcharts-style' else {'width':1600,'height':1200});page.goto(base+svg.relative_to(ROOT).as_posix());page.evaluate('document.fonts.ready')
   page.evaluate('()=>{window.svgSync?.pause();window.svgSync?.pauseCamera();}')
   report=page.evaluate(ARROW_AUDIT);assert not report['issues'],(skill,report['issues']);assert report['shaftCount'] and report['headCount'],skill
   independent.append(report);page.screenshot(path=str(OUT/(skill+'.png')))
  if skill=='hyperframes-explainer':
   audit=jread(workspace/'output/audit.json');assert audit['ok'] and not audit['findings'],audit
   reports=[{'path':'output/audit.json','states':len(audit['arrowStates']),'shafts':sum(r['shaftCount'] for r in audit['arrowStates']),'heads':sum(r['headCount'] for r in audit['arrowStates']),'minimum':min(x['minimum'] for r in audit['arrowStates'] for x in r['records'] if x.get('minimum') is not None)}]
   assert reports[0]['heads']>0
   page.set_viewport_size({'width':960,'height':540});page.goto(base+(workspace/'output/project/index.html').relative_to(ROOT).as_posix());page.wait_for_function('typeof explainer==="object"')
   for time in [0,4,7]:
    page.evaluate('time=>explainer.seek(time)',time);report=page.evaluate(ARROW_AUDIT);assert not report['issues'],(skill,time,report['issues']);independent.append({'time':time,**report})
   page.screenshot(path=str(OUT/(skill+'.png')))
  if skill=='video':
   page.set_viewport_size({'width':720,'height':360});page.goto(base+(workspace/'output/index.html').relative_to(ROOT).as_posix());page.wait_for_function('typeof renderConceptFrame==="function"')
   for time in [0,.5,1,1.5,23/12,2]:
    page.evaluate('time=>renderConceptFrame("arrow-check",time,{capture:true,duration:2})',time);report=page.evaluate(ARROW_AUDIT);assert not report['issues'] and report['headCount'] and report['shaftCount'],(time,report);independent.append({'time':time,**report})
    if time==1:page.screenshot(path=str(OUT/(skill+'.png')))
  media=[]
  for p in case['expectedOutputs']:
   if not p.endswith('.mp4'):continue
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(workspace/p)],text=True));assert abs(float(probe['format']['duration'])-2)<.1,probe
   target=OUT/(skill+'-decoded.png');subprocess.run(['ffmpeg','-v','error','-y','-ss','1','-i',str(workspace/p),'-frames:v','1',str(target)],check=True)
   im=Image.open(target).convert('RGB');assert im.size==(720,360),im.size
   item={'path':p,'probe':probe,'decodedFrame':target.relative_to(ROOT).as_posix()}
   if skill=='manim-svg-video':
    allowed=set(jread(workspace/'skills/manim-svg-video/assets/palettes/colorsets.json')['colorsets']['colorset1']['allowed'])
    sourcepaint={value.lower() for node in ET.parse(workspace/'output/source.svg').getroot().iter() for key,value in node.attrib.items() if key in ['fill','stroke'] and value.startswith('#')}
    assert sourcepaint<=allowed,(skill,'authored source paint outside palette',sorted(sourcepaint-allowed))
    item['authoredSourcePaints']=sorted(sourcepaint)
    composition=jread(workspace/'output/composition/composition-manifest.json');prepared=Path(composition['assets'][0]['prepared_source']);prepared=prepared if prepared.is_absolute() else workspace/prepared
    assetaudit=jread(prepared.with_suffix('.arrow-audit.json'));assert not assetaudit['issues'] and assetaudit['headCount'] and assetaudit['shaftCount'],assetaudit
    sourcebody=[(x,y) for y in range(im.height) for x in range(im.width) if (lambda c:135<=c[0]<=175 and c[1]<=45 and 25<=c[2]<=70)(im.getpixel((x,y)))]
    assert sourcebody,(skill,'Decoded Source identity/fill is absent')
    rows=(min(y for x,y in sourcebody),max(y for x,y in sourcebody))
    gray=[(x,y) for y in range(rows[0],rows[1]+1) for x in range(im.width) if (lambda c:90<=c[0]<=130 and max(c)-min(c)<=3)(im.getpixel((x,y)))]
    assert len(gray)>100,gray
    box=[min(x for x,y in gray),min(y for x,y in gray),max(x for x,y in gray),max(y for x,y in gray)]
    assert box[3]-box[1]>=12,box
    head=[(x,y) for x,y in gray if x>=box[2]-32];headheight=max(y for x,y in head)-min(y for x,y in head)
    assert headheight>=12,(skill,'Decoded terminal must contain a head beyond the narrow shaft',headheight)
    item.update(preparedAudit=assetaudit,decodedOpaqueArrowPixels=len(gray),decodedOpaqueArrowBounds=box,decodedTerminalHeadHeight=headheight)
   media.append(item)
  results.append({'skill':skill,'runId':case['runId'],'model':case['model'],'passed':True,'runtimePayloadSha256':digest,'runtimeFileCount':len(source),'outputs':outputs,'reportedArrows':reports,'independentBrowser':independent,'media':media})
 browser.close()
server.shutdown();report={'passed':len(results)==6,'completedCases':len(results),'results':results};(OUT/'results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':report['passed'],'completedCases':len(results),'cases':[r['skill'] for r in results]}))

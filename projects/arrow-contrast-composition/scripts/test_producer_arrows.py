#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "pyyaml>=6"]
# ///
"""Exercise actual native arrows, pale semantic roles and marker snapshot guards."""
import importlib.util,sys,json,subprocess,copy,xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'projects/arrow-contrast-composition/artifacts/producers';OUT.mkdir(parents=True,exist_ok=True)
results=[]
def load(skill,filename):
 directory=ROOT/'skills'/skill/'scripts';sys.path.insert(0,str(directory))
 for name in ['palette_contract','arrow_quality']:sys.modules.pop(name,None)
 spec=importlib.util.spec_from_file_location(filename,directory/(filename+'.py'));module=importlib.util.module_from_spec(spec);sys.modules[filename]=module;spec.loader.exec_module(module);return module
native=load('diagram-composition','build_panels')
fixtures=load('diagram-composition','test_native_panels')
for mode in ['colorset1','colorset2']:
 colors=json.loads((ROOT/'skills/diagram-composition/assets/palettes/colorsets.json').read_text())['colorsets'][mode]['roles']
 for kind in ['cycle','boundary','hub']:
  renderer=native.Renderer(900,650,18,OUT,{'engine':colors['primary']});getattr(renderer,kind)(copy.deepcopy(fixtures.DATA[kind]));target=OUT/f'{mode}-{kind}.svg';target.write_text(ET.tostring(renderer.root,encoding='unicode'),encoding='utf-8')
poster=load('usefulcharts-style','render_chart');charts=load('usefulcharts-style','test_chart')
for mode,paints in [('colorset1',['#9e1b32','#696969']),('colorset2',['#ffd332','#00ace6'])]:
 data=charts.graph();data['id']='direction-study';data['palette']=mode
 for group,paint in zip(data['groups'],paints):group['color']=paint
 data['unions']=[];data['edges']=[{'id':'influence','source':'a','target':'c','kind':'influence'},{'id':'succession','source':'b','target':'d','kind':'succession'}]
 target=OUT/f'{mode}-poster.svg';target.write_text(poster.Poster(data).render()[0],encoding='utf-8')
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1800})
 for target in sorted(OUT.glob('colorset*.svg')):
  page.goto(target.resolve().as_uri());page.evaluate('document.fonts.ready');r=page.evaluate(ARROW_AUDIT);assert target.stem.endswith('-hub') or r['shaftCount'] and r['headCount'],(target,r);assert not r['issues'],(target,r['issues']);r['source']=str(target);results.append(r);page.screenshot(path=str(target.with_suffix('.png')))
 browser.close()
manim=load('manim-svg-video','compose_svg_video')
source=ROOT/'projects/arrow-contrast-composition/artifacts/baseline/manim-marker.svg'
args=SimpleNamespace(import_mode='svg',render_source='final',snapshot_seconds=0)
try:manim.prepare_asset(manim.Asset(source,source,'marker'),1,args,OUT);raise AssertionError('Vector markers must refuse preparation')
except ValueError as e:assert 'Vector import would omit' in str(e);results.append({'id':'explicit-vector-marker-refused','reason':str(e)})
animated=OUT/'hidden.animated.svg';animated.write_text(source.read_text().replace('<svg ','<svg ').replace('<path d="M60', '<path d="M60'),encoding='utf-8')
# Preserve the original source geometry while adding a real CSS source timeline.
text=source.read_text();text=text.replace('</svg>','<style>@keyframes show {from {opacity:0} to {opacity:1}} path[marker-end] {animation:show 1s linear both}</style></svg>');animated.write_text(text,encoding='utf-8')
args.import_mode='auto'
try:manim.prepare_asset(manim.Asset(animated,animated,'animated'),2,args,OUT);raise AssertionError('Final animated marker source must require companion')
except ValueError as e:assert 'static.svg' in str(e);results.append({'id':'missing-final-companion-refused','reason':str(e)})
args.render_source='animated'
try:manim.prepare_asset(manim.Asset(animated,animated,'hidden'),3,args,OUT);raise AssertionError('Hidden marked source at time zero must fail')
except RuntimeError as e:assert 'hidden arrow' in str(e);results.append({'id':'hidden-zero-snapshot-refused','reason':str(e)})
args.snapshot_seconds=1
asset=manim.prepare_asset(manim.Asset(animated,animated,'readable'),4,args,OUT);assert asset.import_mode=='image' and asset.prepared_source.is_file();results.append({'id':'readable-one-second-snapshot','source':str(asset.prepared_source)})
(OUT/'results.json').write_text(json.dumps({'passed':True,'results':results},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(results)}))

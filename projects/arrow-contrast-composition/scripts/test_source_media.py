#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["manim>=0.20.0", "pyyaml>=6", "playwright>=1.55,<2", "Pillow>=11,<13"]
# ///
"""Qualify exact-asset source fidelity without weakening authored arrow gates."""
import importlib.util,sys,json,hashlib,subprocess
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'projects/arrow-contrast-composition/artifacts/source-media';OUT.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'skills/manim-svg-video/scripts'));spec=importlib.util.spec_from_file_location('compositor',ROOT/'skills/manim-svg-video/scripts/compose_svg_video.py');m=importlib.util.module_from_spec(spec);sys.modules['compositor']=m;spec.loader.exec_module(m)
source=OUT/'pale-original.svg';source.write_text((ROOT/'projects/arrow-contrast-composition/artifacts/baseline/manim-marker.svg').read_text().replace('#696969','#cfcfcf'),encoding='utf-8');before=hashlib.sha256(source.read_bytes()).hexdigest();results=[]
args=SimpleNamespace(import_mode='auto',render_source='final',snapshot_seconds=0,preserve_source_media=[])
try:m.prepare_asset(m.Asset(source,source,'authored'),1,args,OUT);raise AssertionError('Authored pale arrows must fail')
except RuntimeError as e:assert 'arrow-low-contrast' in str(e);results.append({'id':'authored-pale-refused','reason':str(e)})
args.preserve_source_media=[source]
a=m.prepare_asset(m.Asset(source,source,'preserved'),2,args,OUT);audit=json.loads(a.prepared_source.with_suffix('.arrow-audit.json').read_text());assert a.source_media_preserved and audit['issues'] and not audit['sourceMediaPreservation']['authoredQualityPassed'];assert {i['kind'] for i in audit['issues']}=={'arrow-low-contrast'}
im=Image.open(a.prepared_source).convert('RGBA');scale=im.width/360;points={'shaft':(int(180*scale),int(90*scale)),'head':(int(258*scale),int(90*scale))};pixels={k:im.getpixel(p) for k,p in points.items()};assert all(max(abs(c-207) for c in p[:3])<=1 and p[3]==255 for p in pixels.values()),pixels
results.append({'id':'exact-original-preserved','sourceSha256':before,'prepared':str(a.prepared_source),'retainedFindings':audit['issues'],'actualPixels':pixels,'actualPoints':points,'width':im.width,'height':im.height})
args.preserve_source_media=[OUT/'different.svg']
try:m.prepare_asset(m.Asset(source,source,'other'),3,args,OUT);raise AssertionError('Other asset must keep authored gate')
except RuntimeError as e:assert 'arrow-low-contrast' in str(e);results.append({'id':'unmatched-path-no-exemption','reason':str(e)})
hidden=OUT/'hidden-original.svg';hidden.write_text(source.read_text().replace('<path d="M94','<path opacity="0" d="M94'),encoding='utf-8');args.preserve_source_media=[hidden]
try:m.prepare_asset(m.Asset(hidden,hidden,'hidden'),4,args,OUT);raise AssertionError('Preservation must not bypass unreadable marker snapshot')
except RuntimeError as e:assert 'hidden arrow' in str(e);results.append({'id':'preserved-hidden-snapshot-refused','reason':str(e)})
covered=OUT/'covered-original.svg';covered.write_text(source.read_text().replace('</svg>','<rect x="240" y="65" width="35" height="50" fill="#333e48"/></svg>'),encoding='utf-8');args.preserve_source_media=[covered]
try:m.prepare_asset(m.Asset(covered,covered,'covered'),5,args,OUT);raise AssertionError('Preservation must not bypass covered head')
except RuntimeError as e:assert 'arrow-head-occluded' in str(e);results.append({'id':'preserved-covered-head-refused','reason':str(e)})
for ident,replace in [('transparent-head',lambda s:s.replace('fill="#cfcfcf"/>','fill="#cfcfcf" fill-opacity="0"/>',1)),('transparent-shaft',lambda s:s.replace('stroke-width="4"','stroke-opacity="0" stroke-width="4"',1))]:
 transparent=OUT/(ident+'.svg');transparent.write_text(replace(source.read_text()),encoding='utf-8');args.preserve_source_media=[transparent]
 try:m.prepare_asset(m.Asset(transparent,transparent,ident),6,args,OUT);raise AssertionError('Source preservation must not waive absent paint')
 except RuntimeError as e:assert 'hidden arrow' in str(e);results.append({'id':'preserved-'+ident+'-refused','reason':str(e)})
args.import_mode='svg';args.preserve_source_media=[source]
try:m.prepare_asset(m.Asset(source,source,'vector'),6,args,OUT);raise AssertionError('Preservation must not permit marker-losing vector mode')
except ValueError as e:assert 'Vector import would omit' in str(e);results.append({'id':'preserved-vector-marker-refused','reason':str(e)})
args.import_mode='auto';args.preserve_source_media=[]
for ident,style in [('custom-property','--head: url(#arrow); marker-end: var(--head)'),('shorthand-end','marker: url(#arrow); marker-start: none; marker-mid: none')]:
 css=OUT/(ident+'.svg');css.write_text((ROOT/'projects/arrow-contrast-composition/artifacts/baseline/manim-marker.svg').read_text().replace('marker-end="url(#arrow)"',f'style="{style}"'),encoding='utf-8');assert m.has_svg_markers(css),ident
 prepared=m.prepare_asset(m.Asset(css,css,ident),7,args,OUT);cssaudit=json.loads(prepared.prepared_source.with_suffix('.arrow-audit.json').read_text());assert prepared.import_mode=='image' and cssaudit['headCount'] and not cssaudit['issues'],cssaudit
 results.append({'id':'css-'+ident+'-marker-preserved','prepared':str(prepared.prepared_source),'audit':cssaudit})
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
transparent=OUT/'transparent-tile.svg';transparent.write_text((ROOT/'projects/arrow-contrast-composition/artifacts/baseline/manim-marker.svg').read_text().replace('<rect width="360" height="180" fill="#ffffff"/>',''),encoding='utf-8');args.tile_fill='#333e48';args.preserve_source_media=[]
try:m.prepare_asset(m.Asset(transparent,transparent,'dark-tile'),8,args,OUT);raise AssertionError('Transparent source must be audited against actual dark tile')
except RuntimeError as e:assert 'arrow-low-contrast' in str(e);results.append({'id':'transparent-dark-delivery-refused','reason':str(e)})
args.preserve_source_media=[transparent];prepared=m.prepare_asset(m.Asset(transparent,transparent,'preserved-dark-tile'),9,args,OUT);tileaudit=json.loads(prepared.prepared_source.with_suffix('.arrow-audit.json').read_text());assert tileaudit['deliveryBacking']=='#333e48' and not tileaudit['sourceMediaPreservation']['authoredQualityPassed'];assert {i['kind'] for i in tileaudit['issues']}=={'arrow-low-contrast'};assert all(abs(i['minimum']-1.988817387226247)<1e-10 for i in tileaudit['issues']);assert Image.open(prepared.prepared_source).convert('RGBA').getpixel((0,0))[3]==0
results.append({'id':'preserved-transparent-dark-delivery-disclosed','audit':tileaudit,'transparentPng':True})
args.preserve_source_media=[];opaque=ROOT/'projects/arrow-contrast-composition/artifacts/baseline/manim-marker.svg';prepared=m.prepare_asset(m.Asset(opaque,opaque,'white-source-dark-tile'),10,args,OUT);tileaudit=json.loads(prepared.prepared_source.with_suffix('.arrow-audit.json').read_text());assert not tileaudit['issues'] and tileaudit['deliveryBacking']=='#333e48';results.append({'id':'opaque-white-source-over-dark-tile-passed','audit':tileaudit})
args.tile_fill='#ffffff';prepared=m.prepare_asset(m.Asset(transparent,transparent,'white-tile'),11,args,OUT);tileaudit=json.loads(prepared.prepared_source.with_suffix('.arrow-audit.json').read_text());assert not tileaudit['issues'] and tileaudit['deliveryBacking']=='#ffffff';results.append({'id':'transparent-white-delivery-passed','audit':tileaudit})
cmd=['uv','run','--script','skills/manim-svg-video/scripts/compose_svg_video.py','--discover-root',str(OUT.relative_to(ROOT)),'--include','pale-original.svg','--preserve-source-media',str(source.relative_to(ROOT)),'--out',str((OUT/'after').relative_to(ROOT)),'--dry-run'];r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True);assert r.returncode==0,(r.stdout,r.stderr);manifest=json.loads((OUT/'after/composition-manifest.json').read_text());assert manifest['assets'][0]['source_media_preserved'] and len(manifest['settings']['preserve_source_media'])==1;results.append({'id':'cli-preserved-manifest','command':cmd,'exitCode':r.returncode,'manifestSource':manifest['assets'][0]})
(OUT/'results.json').write_text(json.dumps({'passed':True,'cases':results},indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'cases':len(results),'preservedRatio':audit['issues'][0]['minimum']}))

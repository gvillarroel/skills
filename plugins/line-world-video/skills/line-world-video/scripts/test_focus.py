#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Exercise real geometry clearance and deterministic audio-clock focus."""
import json,os,unittest,tempfile,subprocess,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
class FocusTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pw=sync_playwright().start();cache=Path(os.environ.get('LOCALAPPDATA',''))/'ms-playwright';paths=sorted(cache.glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'),reverse=True);cls.browser=cls.pw.chromium.launch(executable_path=str(paths[0]) if paths else None,headless=True);cls.page=cls.browser.new_page(viewport={'width':1000,'height':600})
 @classmethod
 def tearDownClass(cls):cls.browser.close();cls.pw.stop()
 def setUp(self):
  self.page.set_content('<style>body{margin:0}text{font:24px Arial}</style><svg width="1000" height="600" id="stage"></svg>');self.page.add_script_tag(path=str(ROOT/'assets/runtime/focus.js'))
 def test_safe_port_and_impossible_port(self):
  self.assertTrue(self.page.evaluate('''()=>{const F=LineWorldFocus,b={x0:100,y0:100,x1:200,y1:140},p=F.port(b,{x0:0,y0:0,x1:1000,y1:600},[b]);return p.x<100&&p.x+18<100}'''))
  self.assertTrue(self.page.evaluate('''()=>{try{LineWorldFocus.port({x0:0,y0:0,x1:10,y1:10},{x0:0,y0:0,x1:10,y1:10});return false}catch(e){return true}}'''))
 def test_audio_arrivals_and_backward_seek(self):
  r=self.page.evaluate('''()=>{const c=[{target:'train',at:7.37,x:100,y:100},{target:'validation',at:8.27,x:500,y:100},{target:'test',at:8.85,x:800,y:100}],o={x:20,y:100},a=LineWorldFocus.pose(c,8.85,o);LineWorldFocus.pose(c,12,o);return {targets:c.map(q=>LineWorldFocus.pose(c,q.at,o).target),position:a.x,repeat:JSON.stringify(a)===JSON.stringify(LineWorldFocus.pose(c,8.85,o)),travel:LineWorldFocus.pose(c,8.1,o).radius}}''');self.assertEqual(r['targets'],['train','validation','test']);self.assertEqual(r['position'],800);self.assertTrue(r['repeat']);self.assertEqual(r['travel'],6)
 def test_diagonal_port_clears_a_curve_and_vertical_reference(self):
  r=self.page.evaluate('''()=>{const f=LineWorldFocus,p=f.port({x0:493,y0:293,x1:507,y1:307},{x0:0,y0:0,x1:1000,y1:600},[{x0:0,y0:297,x1:1000,y1:303},{x0:497,y0:0,x1:503,y1:600}]);return p}''');self.assertIn('-',r['side']);self.assertGreater(abs(r['x']-500),25);self.assertGreater(abs(r['y']-300),25)
 def test_clear_route_bends_around_a_label(self):
  r=self.page.evaluate('''()=>{const F=LineWorldFocus,p=F.route({x:20,y:100},{x:900,y:100},[{x0:300,y0:50,x1:600,y1:150}],{x0:0,y0:0,x1:1000,y1:600});return {n:p.length,mid:F.along(p,.5)}}''');self.assertGreater(r['n'],2);self.assertTrue(r['mid']['y']<50 or r['mid']['y']>150)
 def test_pan_keeps_the_routed_guide_inside_the_camera(self):
  r=self.page.evaluate('''()=>{const F=LineWorldFocus,path=[{x:3500,y:900},{x:100,y:900},{x:100,y:450}],result=[];for(let k=0;k<=100;k++){const u=k/100,camera=1900*(1-u),bounds={x0:camera+45,x1:camera+1875,y0:45,y1:1035},p=F.visibleAlong(path,u,bounds);result.push(p.x>=bounds.x0-1e-6&&p.x<=bounds.x1+1e-6&&p.y>=bounds.y0&&p.y<=bounds.y1&&(Math.abs(p.y-900)<1e-6||Math.abs(p.x-100)<1e-6));}return result.every(Boolean)}''');self.assertTrue(r)
 def test_pan_rejects_a_route_outside_the_camera(self):
  r=self.page.evaluate('''()=>{try{LineWorldFocus.visibleAlong([{x:10,y:10},{x:20,y:20}],.5,{x0:200,x1:400,y0:200,y1:400});return false}catch(e){return e.message.includes('camera')}}''');self.assertTrue(r)
 def test_real_stroke_conflict_and_clean_clip(self):
  self.page.locator('#stage').evaluate('''e=>e.innerHTML='<text x="100" y="100">Readable</text><path d="M80 90 L260 90" stroke="red"/>' ''');r=self.page.evaluate('LineWorldFocus.audit(document.querySelector("#stage"))');self.assertFalse(r['ok']);self.assertEqual(r['issues'][0]['kind'],'stroke-through-text')
  self.page.locator('#stage').evaluate('''e=>e.innerHTML='<defs><clipPath id="c"><rect x="300" y="50" width="100" height="100"/></clipPath></defs><text x="100" y="100">Readable</text><g clip-path="url(#c)"><path d="M80 90 L500 90" stroke="red"/></g>' ''');self.assertTrue(self.page.evaluate('LineWorldFocus.audit(document.querySelector("#stage")).ok'))
 def test_text_overlap_and_clipping_are_detected(self):
  self.page.locator('#stage').evaluate('''e=>e.innerHTML='<text x="100" y="100">First</text><text x="110" y="100">Second</text><text x="980" y="200">Clipped</text>' ''');k=self.page.evaluate('LineWorldFocus.audit(document.querySelector("#stage")).issues.map(v=>v.kind)');self.assertIn('text-overlap',k);self.assertIn('clipped-text',k)
 def test_secondary_gray_exception_is_quantitative_and_bounded(self):
  from color_audit import BROWSER_CHECK
  self.page.evaluate("window.STORY={colorSequence:['#9e1b32','#b5b5b5','#000000']}")
  self.page.locator('#stage').evaluate('''e=>e.innerHTML='<rect id="bar" x="200" y="100" width="120" height="300" fill="#696969" data-color-role="secondary-highlight" data-encoding="quantity" data-value="0.9"/>' ''');self.assertTrue(self.page.evaluate(BROWSER_CHECK)['ok'])
  self.page.locator('#bar').evaluate("e=>e.removeAttribute('data-encoding')");self.assertFalse(self.page.evaluate(BROWSER_CHECK)['ok'])
  self.page.locator('#bar').evaluate("e=>{e.dataset.encoding='quantity';e.setAttribute('fill','#000000')}");self.assertFalse(self.page.evaluate(BROWSER_CHECK)['ok'])
 def test_palette_rejects_pink_and_translucent_red_surfaces(self):
  from color_audit import BROWSER_CHECK
  self.page.evaluate("window.STORY={colorSequence:['#9e1b32','#b5b5b5','#000000']}")
  self.page.locator('#stage').evaluate('''e=>e.innerHTML='<rect id="face" x="200" y="100" width="100" height="80" fill="#ffccd5"/>' ''')
  self.assertEqual(len(self.page.evaluate(BROWSER_CHECK)['pinkSurfaces']),1)
  self.page.locator('#face').evaluate("e=>{e.setAttribute('fill','#9e1b32');e.setAttribute('fill-opacity','.2')}")
  self.assertFalse(self.page.evaluate(BROWSER_CHECK)['ok'])
  self.page.locator('#face').evaluate("e=>e.setAttribute('fill-opacity','1')");self.assertTrue(self.page.evaluate(BROWSER_CHECK)['ok'])
  self.page.locator('#face').evaluate("e=>e.setAttribute('fill','white')");self.assertTrue(self.page.evaluate(BROWSER_CHECK)['ok'])
 def test_standalone_inspector_checks_actual_guide_and_preserves_html(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);html=p/'figure.html';source='<svg id="stage" width="1920" height="1080"><text x="130" y="100">Readable</text><circle id="guide" cx="80" cy="95" r="10" fill="#9e1b32"/></svg><script>window.renderAt=t=>({seconds:t});</script>';html.write_text(source,encoding='utf-8')
   args=[sys.executable,str(ROOT/'scripts/inspect_focus.py'),'--html',str(html),'--times','0,1','--output',str(p/'check.json'),'--screenshot',str(p/'preview.png')];run=subprocess.run(args,capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);self.assertTrue(json.loads((p/'check.json').read_text())['ok']);self.assertEqual(html.read_text(),source)
   html.write_text(source.replace('cx="80"','cx="150"'),encoding='utf-8');run=subprocess.run(args,capture_output=True,text=True);self.assertEqual(run.returncode,2);self.assertFalse(json.loads((p/'check.json').read_text())['ok'])
if __name__=='__main__':unittest.main()

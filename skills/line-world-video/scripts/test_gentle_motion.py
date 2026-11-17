#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Check actual float/detail pixels, identity, bounds and repeated seeking."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from inspect_gentle_motion import inspect

SKILL=Path(__file__).resolve().parent.parent


class GentleMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder=Path(os.environ.get('LINE_WORLD_TEST_ROOT',str(Path.cwd()/'output/gentle-motion-tests'))).resolve();folder.mkdir(parents=True,exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(dir=folder);os.environ['TEMP']=cls.temp.name;os.environ['TMP']=cls.temp.name
        cls.pw=sync_playwright().start();chrome=Path('C:/Program Files/Google/Chrome/Application/chrome.exe')
        cls.browser=cls.pw.chromium.launch(headless=True,**({'executable_path':str(chrome)} if chrome.is_file() else {}));cls.page=cls.browser.new_page(viewport={'width':800,'height':450})

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.temp.cleanup()

    def setUp(self):
        self.page.set_content('''<svg id="stage" width="800" height="450"><rect width="800" height="450" fill="white"/><g transform="translate(30 80)"><g id="brand"><circle cx="90" cy="90" r="42" fill="#9e1b32"/><text x="90" y="165" text-anchor="middle" font-size="24">Brand</text></g></g><svg id="viewport" x="370" y="50" width="400" height="300" viewBox="0 0 400 300" overflow="hidden"><g id="camera"><image id="source" x="0" y="0" width="400" height="300" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='300'%3E%3Crect width='400' height='300' fill='%23e7e7e7'/%3E%3Ccircle cx='275' cy='100' r='52' fill='%239e1b32'/%3E%3Cpath d='M0 250 L400 50 M0 0 L400 300' stroke='%23696969' stroke-width='8'/%3E%3C/svg%3E"/></g></svg><text id="caption" x="570" y="395" text-anchor="middle" font-size="24">Source caption</text></svg>''')
        self.page.add_script_tag(path=str(SKILL/'assets/runtime/gentle-motion.js'))
        self.page.evaluate('''()=>{window.f={id:'brand',target:'#brand',type:'float',start:0,end:24};window.d={id:'detail',target:'#camera',type:'detail',start:2,end:13,width:400,height:300,focus:[.4,.1,.8,.5],zoom:1.15,inSeconds:4,holdSeconds:3,outSeconds:4};window.m=LineWorldGentleMotion.attach(document.querySelector('#stage'),[f,d])}''')
        self.page.evaluate('async()=>await m.ready')

    def test_float_changes_real_pixels_and_keeps_logo_label_together(self):
        region={'x':40,'y':100,'width':230,'height':240}
        self.page.evaluate('m.render(3)');before=self.page.screenshot(clip=region);before_box=self.page.locator('#brand').bounding_box();a=self.page.evaluate('''()=>{const a=document.querySelector('#brand circle').getBoundingClientRect(),b=document.querySelector('#brand text').getBoundingClientRect();return[b.x-a.x,b.y-a.y]}''')
        self.page.evaluate('m.render(6)');self.assertNotEqual(before,self.page.screenshot(clip=region));self.assertNotEqual(before_box,self.page.locator('#brand').bounding_box())
        b=self.page.evaluate('''()=>{const a=document.querySelector('#brand circle').getBoundingClientRect(),b=document.querySelector('#brand text').getBoundingClientRect();return[b.x-a.x,b.y-a.y]}''')
        for x,y in zip(a,b,strict=True):self.assertAlmostEqual(x,y,places=4)

    def test_entire_float_envelope_is_bounded(self):
        states=self.page.evaluate('''()=>{const c=LineWorldGentleMotion.compile(f);return Array.from({length:721},(_,i)=>c.at(i/30))}''')
        self.assertTrue(any(abs(s['y'])>5 for s in states));self.assertTrue(all(abs(s['x'])<=3 and abs(s['y'])<=8 and s['scale']==1 for s in states))

    def test_stable_ids_desynchronize_independent_logos(self):
        self.assertTrue(self.page.evaluate('''()=>JSON.stringify(LineWorldGentleMotion.compile(f).at(5))!==JSON.stringify(LineWorldGentleMotion.compile({...f,id:'other'}).at(5))'''))

    def test_project_inspector_accepts_actual_motion(self):
        self.page.evaluate('()=>{window.renderAt=t=>m.render(t)}')
        report=inspect(self.page,[0,3,7,8,13,24],['#brand'],'#camera','#viewport',['#caption'])
        self.assertTrue(report['ok'],report['findings'])

    def test_project_inspector_rejects_moving_caption(self):
        self.page.evaluate('()=>{window.renderAt=t=>{m.render(t);document.querySelector("#caption").setAttribute("x",570+t)}}')
        report=inspect(self.page,[0,3,7,8,13,24],['#brand'],'#camera','#viewport',['#caption'])
        self.assertFalse(report['ok'])
        self.assertTrue(any(f['kind']=='fixed-element-moved' for f in report['findings']))

    def test_project_inspector_rejects_empty_image_edge(self):
        self.page.evaluate('window.renderAt=t=>m.render(t);document.querySelector("#source").setAttribute("width",380)')
        report=inspect(self.page,[0,3,7,8,13,24],['#brand'],'#camera','#viewport',['#caption'])
        self.assertFalse(report['ok'])
        self.assertTrue(any(f['kind']=='empty-detail-viewport' for f in report['findings']),report)

    def test_detail_enters_holds_returns_and_preserves_source(self):
        href=self.page.locator('#source').get_attribute('href');caption=self.page.locator('#caption').bounding_box()
        self.page.evaluate('m.render(0)');initial=self.page.locator('#viewport').screenshot()
        self.page.evaluate('m.render(7)');held=self.page.locator('#viewport').screenshot();self.assertNotEqual(initial,held)
        self.page.evaluate('m.render(8.5)');self.assertEqual(held,self.page.locator('#viewport').screenshot())
        self.page.evaluate('m.render(14)');self.assertEqual(initial,self.page.locator('#viewport').screenshot())
        self.assertEqual(href,self.page.locator('#source').get_attribute('href'));self.assertEqual(caption,self.page.locator('#caption').bounding_box())

    def test_detail_never_exposes_empty_image_space(self):
        states=self.page.evaluate('''()=>{const c=LineWorldGentleMotion.compile(d);return Array.from({length:451},(_,i)=>c.at(i/30))}''')
        for s in states:
            self.assertGreaterEqual(s['scale'],1);self.assertLessEqual(s['scale'],1.15)
            self.assertGreaterEqual(s['sourceX'],0);self.assertGreaterEqual(s['sourceY'],0)
            self.assertLessEqual(s['sourceX']+400/s['scale'],400.0001);self.assertLessEqual(s['sourceY']+300/s['scale'],300.0001)

    def test_forward_backward_seek_reproduces_exact_pixels_and_state(self):
        state=self.page.evaluate('m.render(7.1)');pixels=self.page.screenshot()
        self.page.evaluate('m.render(19);m.render(0)');self.assertEqual(state,self.page.evaluate('m.render(7.1)'));self.assertEqual(pixels,self.page.screenshot())

    def test_unsafe_speed_zoom_and_amplitudes_are_rejected(self):
        invalid=[{'type':'float','period':2},{'type':'float','amplitudeY':25},{'type':'detail','zoom':1.4},{'type':'detail','inSeconds':1},{'type':'detail','holdSeconds':.2},{'type':'detail','end':7},{'type':'detail','focus':[.8,.2,.1,.5]}]
        for patch in invalid:
            self.assertTrue(self.page.evaluate('p=>{try{LineWorldGentleMotion.compile({...((p.type===\'float\')?f:d),...p});return false}catch(e){return true}}',patch))

    def test_reduced_motion_and_inactive_states_remain_static(self):
        result=self.page.evaluate('''()=>{const c=LineWorldGentleMotion.compile(d,{reducedMotion:true});return[c.at(4),c.at(8)]}''')
        self.assertEqual(result[0],result[1]);self.assertEqual(result[0]['scale'],1);self.assertFalse(result[0]['active'])
        self.assertEqual(self.page.evaluate('m.render(-1)'),self.page.evaluate('m.render(30)'))

    def test_destroy_restores_authored_children_and_wrappers(self):
        self.page.evaluate('m.render(6);m.destroy()');self.assertIsNone(self.page.locator('#brand').get_attribute('transform'));self.assertIsNone(self.page.locator('#camera').get_attribute('transform'))
        self.assertEqual(self.page.locator('#brand circle').get_attribute('r'),'42')


if __name__=='__main__':unittest.main()

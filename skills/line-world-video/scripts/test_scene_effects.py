#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Verify scene clock conversion and real frame-cache invalidation."""
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from inspect_focus import browser_path

SKILL=Path(__file__).resolve().parent.parent


class SceneEffectsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path=browser_path(),headless=True)
        cls.page=cls.browser.new_page(viewport={'width':800,'height':450})

    @classmethod
    def tearDownClass(cls): cls.browser.close();cls.pw.stop()

    def setUp(self):
        self.page.set_content('<svg id="stage" width="800" height="450"><path id="curve" d="M100 300Q300 40 650 200" fill="none" stroke="#696969"/><text x="650" y="180">42</text></svg>')
        for name in ['focus-motion.js','scene-effects.js']:self.page.add_script_tag(path=str(SKILL/'assets/runtime'/name))
        self.page.evaluate('''()=>{window.plan={scenes:[{id:'first',duration:5},{id:'second',duration:7}],motion:[{id:'flow',sceneId:'second',source:'#curve',kind:'chart',start:1,end:6}]};window.bridge=LineWorldSceneEffects.attach(document.querySelector('#stage'),plan)}''')

    def test_offsets_and_exact_boundary_use_next_scene(self):
        self.assertEqual(self.page.evaluate('bridge.windows[0].start'),6)
        self.assertEqual(self.page.evaluate('bridge.locate(5)'),{'index':1,'seconds':0})
        self.assertEqual(self.page.evaluate('bridge.locate(99)'),{'index':1,'seconds':7})

    def test_active_motion_invalidates_unchanged_authored_pose(self):
        self.page.evaluate('bridge.frame(1,1.4,{camera:42})');first=self.page.screenshot()
        a=self.page.evaluate('bridge.snapshot()')
        b=self.page.evaluate('bridge.frame(1,2.4,{camera:42})')
        self.assertNotEqual(a,b);self.assertNotEqual(first,self.page.screenshot())
        self.assertEqual(self.page.locator('#stage text').text_content(),'42')

    def test_inactive_motion_preserves_hold_cache_identity(self):
        self.assertEqual(self.page.evaluate('bridge.frame(0,1,{camera:42})'),self.page.evaluate('bridge.frame(0,4,{camera:42})'))
        self.assertEqual(self.page.evaluate('bridge.snapshot().effects.motion'),[])

    def test_backward_seek_reproduces_pixels_and_state(self):
        first=self.page.evaluate('bridge.frame(1,2.1,{camera:42})');pixels=self.page.screenshot()
        self.page.evaluate('bridge.frame(1,5.4,{});bridge.frame(0,0,{})')
        self.assertEqual(first,self.page.evaluate('bridge.frame(1,2.1,{camera:42})'));self.assertEqual(pixels,self.page.screenshot())

    def test_invalid_scene_windows_fail_before_source_mutation(self):
        self.page.evaluate('bridge.destroy()')
        self.assertTrue(self.page.evaluate('''()=>{try{LineWorldSceneEffects.attach(document.querySelector('#stage'),{...plan,motion:[{...plan.motion[0],end:8}]});return false}catch(e){return true}}'''))
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').count(),0)


if __name__=='__main__':unittest.main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2", "numpy>=2,<3"]
# ///
"""Check rendered atlas typography and actual quantity flights from a fresh bundle."""
import functools
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from inspect_focus import Quiet,browser_path
from atlas_audit import CHECKS

SKILL=Path(__file__).resolve().parent.parent


class AtlasReadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();root=Path(cls.temp.name)/'film'
        subprocess.run([sys.executable,str(SKILL/'scripts/line_world.py'),'init','--project',str(root),'--layout','atlas'],check=True,capture_output=True)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(root)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch(executable_path=browser_path(),headless=True)
        cls.page=cls.browser.new_page(viewport={'width':1920,'height':1080})
        cls.page.goto(f'http://127.0.0.1:{cls.server.server_port}/index.html');cls.page.evaluate('async()=>await window.ready')

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop();cls.server.shutdown();cls.server.server_close();cls.temp.cleanup()

    def test_reading_labels_stay_clear_and_legible_after_native_fit(self):
        for identity in ['parts','profiles','history','shares']:
            self.page.evaluate('id=>{const b=STORY.beats.find(s=>s.id===id);renderAt(b.start+b.duration*.65)}',identity)
            result=self.page.evaluate(CHECKS)
            self.assertEqual(result['issues'],[],identity)
            self.assertEqual(result['warnings'],[],identity)

    def test_quantity_flights_preserve_values_and_avoid_all_four_legends(self):
        beat=self.page.evaluate('STORY.beats.find(s=>s.id==="shares")')
        config=self.page.evaluate('STORY.attention');transition=self.page.evaluate('STORY.camera.transitionSeconds')
        hold=(beat['duration']-transition)/4
        for row in range(4):
            at=beat['start']+transition+row*hold+(.38/3+.035)*hold+.17+config['flightSeconds']*.5
            self.page.evaluate('t=>renderAt(t)',at);result=self.page.evaluate(CHECKS)
            self.assertEqual(result['issues'],[],result['issues'])
            self.assertEqual([q['quantity'] for q in result['quantities']],[12,8,16,6])

    def test_guide_travel_and_repeated_seek_keep_the_same_state(self):
        for time in [44.7,48.2,118.3,121.8,162.65]:
            first=self.page.evaluate('t=>renderAt(t)',time)
            self.page.evaluate('renderAt(0);renderAt(175)')
            self.assertEqual(first,self.page.evaluate('t=>renderAt(t)',time))

    def test_long_reading_holds_are_not_disabled_by_short_guide_visits(self):
        windows=self.page.evaluate('FOCUS_PLAN.windows')
        self.assertTrue(any(w['end']-w['start']>2 for w in windows))
        self.page.evaluate('renderAt(162.5)')
        self.assertTrue(self.page.locator('[data-lw-motion-overlay]').evaluate_all('es=>es.some(e=>getComputedStyle(e).display!=="none")'))


if __name__=='__main__':unittest.main()

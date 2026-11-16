#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "Pillow>=11,<13"]
# ///
"""Verify actual long-hold pixels, fixed data, guide exclusion and clock seeking."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from inspect_focus import browser_path
from inspect_focus_motion import equivalent_pixels
from PIL import Image

SKILL = Path(__file__).resolve().parent.parent
MARKUP = '<style>body{margin:0;background:white}text{font:30px Arial}</style><svg id="stage" width="1920" height="1080"><g id="figure"><path id="curve" d="M200 720 Q700 100 1300 420" stroke="#696969" stroke-width="3" fill="none"/><text id="value" x="1300" y="380">0.82</text></g><circle id="guide" cx="160" cy="720" r="10" fill="#9e1b32"/></svg>'


class FocusMotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start(); cls.browser = cls.pw.chromium.launch(executable_path=browser_path(), headless=True)
        cls.page = cls.browser.new_page(viewport={'width': 1920, 'height': 1080})

    @classmethod
    def tearDownClass(cls): cls.browser.close(); cls.pw.stop()

    def setUp(self):
        self.page.set_content(MARKUP); self.page.add_script_tag(path=str(SKILL / 'assets/runtime/focus-motion.js'))

    def controller(self, end=5, mode='trace'):
        self.page.evaluate('''([end,mode])=>{window.motion=LineWorldFocusMotion.attach(document.querySelector('#stage'),[{id:'curve',source:'#curve',kind:'chart',start:0,end,mode}]);}''', [end, mode])

    def fixture(self, folder, code, end=5):
        root = Path(folder); shutil.copyfile(SKILL / 'assets/runtime/focus-motion.js', root / 'motion.js')
        html = root / 'scene.html'
        html.write_text(MARKUP + '<script src="motion.js"></script><script>window.FOCUS_PLAN={windows:[{id:"curve",source:"#curve",scope:"#figure",kind:"chart",start:0,end:' + str(end) + '}]};' + code + '</script>', encoding='utf-8')
        return html

    def audit(self, root, html, video=False):
        args = [sys.executable, str(SKILL / 'scripts/inspect_focus_motion.py'), '--html', str(html), '--output', str(root / 'audit.json'), '--screenshot', str(root / 'preview.png')]
        if video: args += ['--video', str(root / 'preview.mp4'), '--duration', '3']
        result = subprocess.run(args, capture_output=True, text=True)
        report = json.loads((root / 'audit.json').read_text())
        self.assertEqual(result.returncode, 0 if report['ok'] else 2, result.stderr)
        return report

    def test_two_seconds_are_exempt_and_longer_holds_activate(self):
        self.controller(2)
        self.assertFalse(self.page.evaluate('motion.render(1)[0].eligible'))
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').evaluate('e=>getComputedStyle(e).display'), 'none')
        self.page.evaluate('motion.destroy()'); self.controller(2.001)
        self.assertTrue(self.page.evaluate('motion.render(1)[0].active'))

    def test_trace_changes_actual_pixels_without_changing_data(self):
        self.controller(); original = self.page.locator('#curve').get_attribute('d')
        self.page.evaluate('motion.render(.5)'); first = self.page.screenshot()
        self.page.evaluate('motion.render(1.5)'); second = self.page.screenshot()
        self.assertNotEqual(first, second); self.assertEqual(original, self.page.locator('#curve').get_attribute('d'))
        self.assertEqual(self.page.locator('#value').text_content(), '0.82')

    def test_thick_primary_red_marks_have_a_visible_inset_trace(self):
        self.page.locator('#curve').evaluate('e=>{e.style.stroke="#9e1b32";e.style.strokeWidth="10"}')
        self.controller();self.page.evaluate('motion.render(.5)');first=self.page.screenshot()
        self.page.evaluate('motion.render(1.5)');self.assertNotEqual(first,self.page.screenshot())
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').evaluate('e=>getComputedStyle(e).stroke'),'rgb(255, 255, 255)')
        self.assertEqual(self.page.locator('#curve').evaluate('e=>getComputedStyle(e).strokeWidth'),'10px')

    def test_producer_css_cannot_fill_an_overlay_or_cover_reading_text(self):
        self.page.set_content('<style>body{margin:0}.node rect{fill:white!important;stroke:none!important}</style><svg id="stage" width="800" height="450"><g class="node"><rect id="tile" x="100" y="100" width="400" height="200" style="fill:#9e1b32!important;stroke:none!important"/><text x="260" y="210" fill="white">Read me</text></g></svg>')
        self.page.add_script_tag(path=str(SKILL/'assets/runtime/focus-motion.js'))
        self.page.evaluate('window.m=LineWorldFocusMotion.attach(document.querySelector("#stage"),[{id:"tile",source:"#tile",kind:"diagram",mode:"pulse",start:0,end:5}]);m.render(1.4)')
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').evaluate('e=>getComputedStyle(e).fill'),'none')
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').evaluate('e=>getComputedStyle(e).stroke'),'rgb(158, 27, 50)')
        import io
        pixels=Image.open(io.BytesIO(self.page.screenshot())).convert('RGB')
        self.assertEqual(pixels.getpixel((150,150)),(158,27,50))
        self.assertEqual(self.page.locator('text').evaluate('e=>getComputedStyle(e).fill'),'rgb(255, 255, 255)')

    def test_sparse_edge_antialiasing_does_not_allow_interior_or_large_changes(self):
        first=Image.new('RGB',(100,100),'white');first.paste('#696969',(25,25,75,75))
        edge=first.copy();edge.putpixel((25,40),(130,130,130))
        self.assertTrue(equivalent_pixels(first,edge))
        interior=first.copy();interior.putpixel((50,50),(130,130,130))
        self.assertFalse(equivalent_pixels(first,interior))
        large=first.copy();large.paste('#898989',(25,25,30,75))
        self.assertFalse(equivalent_pixels(first,large))

    def test_backward_seek_and_focus_exit_are_deterministic(self):
        self.controller(); self.page.evaluate('motion.render(1.4)'); before = self.page.screenshot()
        self.page.evaluate('motion.render(4);motion.render(0);motion.render(1.4)')
        self.assertEqual(before, self.page.screenshot())
        self.page.evaluate('motion.render(5)')
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').evaluate('e=>getComputedStyle(e).display'), 'none')

    def test_pulse_keeps_geometry_and_has_visible_ink_change(self):
        self.controller(mode='pulse'); self.page.evaluate('motion.render(.3)'); first = self.page.screenshot()
        self.page.evaluate('motion.render(1.5)'); self.assertNotEqual(first, self.page.screenshot())
        self.assertEqual(self.page.locator('[data-lw-motion-overlay]').get_attribute('d'), self.page.locator('#curve').get_attribute('d'))

    def test_fast_period_and_duplicate_windows_are_rejected(self):
        result = self.page.evaluate('''()=>{const w={id:'a',kind:'chart',source:'#curve',start:0,end:5};return [.7,null].map(p=>{try{LineWorldFocusMotion.validate(p===null?[w,w]:[{...w,period:p}]);return false}catch(e){return true}})}''')
        self.assertEqual(result, [True, True])

    def test_disconnected_edges_need_separate_traces_or_pulse(self):
        self.page.locator('#curve').evaluate('e=>e.setAttribute("d","M200 500H400M500 500H700")')
        rejected = self.page.evaluate('''()=>{try{LineWorldFocusMotion.attach(document.querySelector('#stage'),[{id:'flow',source:'#curve',kind:'diagram',start:0,end:4}]);return false}catch(e){return true}}''')
        self.assertTrue(rejected)
        self.controller(mode='pulse'); self.assertTrue(self.page.evaluate('motion.render(1)[0].active'))

    def test_pixel_audit_accepts_motion_and_exports_a_real_preview(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); html = self.fixture(folder, 'window.motion=LineWorldFocusMotion.attach(document.querySelector("#stage"),FOCUS_PLAN.windows);window.renderAt=t=>motion.render(t);', 3)
            report = self.audit(root, html, video=True)
            self.assertTrue(report['ok'], report); self.assertGreater(report['windows'][0]['changedPixels'], 12)
            stream = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(root / 'preview.mp4')]))['streams'][0]
            self.assertEqual(int(stream['nb_frames']), 90)

    def test_moving_guide_does_not_pass_for_static_chart_motion(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); html = self.fixture(folder, 'window.renderAt=t=>document.querySelector("#guide").setAttribute("cx",200+t*100);')
            report = self.audit(root, html)
            self.assertFalse(report['ok']); self.assertEqual(report['windows'][0]['changedPixels'], 0)

    def test_inspector_rejects_opaque_emphasis_even_when_it_moves(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            html=self.fixture(folder,'window.motion=LineWorldFocusMotion.attach(document.querySelector("#stage"),FOCUS_PLAN.windows);window.renderAt=t=>{motion.render(t);document.querySelector("[data-lw-motion-overlay]").style.setProperty("fill","white","important")};')
            report=self.audit(root,html)
            self.assertFalse(report['ok'])
            self.assertFalse(report['windows'][0]['transparentEmphasis'])
            self.assertIn('emphasis overlay fills',' '.join(report['issues']))

    def test_value_geometry_or_label_motion_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); html = self.fixture(folder, 'window.renderAt=t=>{document.querySelector("#curve").setAttribute("transform","translate("+t*5+" 0)");document.querySelector("#value").textContent=t.toFixed(2)};')
            report = self.audit(root, html)
            self.assertFalse(report['ok']); self.assertFalse(report['windows'][0]['stableGeometryAndLabels'])

    def test_default_starter_declares_and_animates_its_long_holds(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'film'
            subprocess.run([sys.executable, str(SKILL / 'scripts/line_world.py'), 'init', '--project', str(root)], check=True, capture_output=True)
            report = self.audit(root, root / 'index.html')
            self.assertTrue(report['ok'], report)
            self.assertTrue(any(w['required'] for w in report['windows']))


if __name__ == '__main__': unittest.main()

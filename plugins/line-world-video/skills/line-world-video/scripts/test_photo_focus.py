#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Verify original-color focus, neutral recovery, aligned geometry and native pixels."""
import functools
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright
from inspect_focus import Quiet, browser_path
from photo_focus import normalize, plan

SKILL = Path(__file__).resolve().parent.parent


class PhotoFocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start(); cls.browser = cls.pw.chromium.launch(executable_path=browser_path(), headless=True)

    @classmethod
    def tearDownClass(cls): cls.browser.close(); cls.pw.stop()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.root = Path(self.temp.name)
        image = Image.new('RGB', (160, 100), (30, 130, 210)); image.paste((220, 90, 20), (80, 0, 160, 100)); image.save(self.root / 'original.png')
        ImageOps.grayscale(image).save(self.root / 'neutral.png')
        shutil.copyfile(SKILL / 'assets/runtime/photo-focus.js', self.root / 'photo-focus.js')
        self.binding = {'id': 'card', 'target': '#card', 'neutral': 'neutral.png', 'color': 'original.png', 'windows': [{'start': 1, 'end': 4}], 'transition': .4}
        self.html = self.root / 'scene.html'
        self.html.write_text('''<!doctype html><style>body{margin:0;background:white}</style><svg width="1920" height="1080"><g transform="translate(20 30)"><image id="card" data-documentary-id="card" href="neutral.png" x="80" y="90" width="320" height="200" preserveAspectRatio="xMidYMid meet"/></g></svg><script src="photo-focus.js"></script><script>window.PHOTO_FOCUS_PLAN=PLAN;window.photos=LineWorldPhotoFocus.attach(document.querySelector('svg'),PHOTO_FOCUS_PLAN.bindings);window.renderAt=t=>photos.render(t);window.ready=photos.ready.then(()=>renderAt(0));</script>'''.replace('PLAN;', json.dumps({'bindings': [self.binding]}) + ';'), encoding='utf-8')
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(self.root))); threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.page = self.browser.new_page(viewport={'width': 1920, 'height': 1080})
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}/scene.html'); self.page.evaluate('async()=>await window.ready')

    def tearDown(self): self.page.close(); self.server.shutdown(); self.server.server_close(); self.temp.cleanup()

    def image(self, time):
        self.page.evaluate('t=>renderAt(t)', time)
        return Image.open(io.BytesIO(self.page.screenshot())).convert('RGB')

    def test_color_is_original_during_focus_and_neutral_outside(self):
        self.assertEqual(self.image(0).getpixel((120, 150)), (109, 109, 109))
        self.assertEqual(self.image(2).getpixel((120, 150)), (30, 130, 210))
        self.assertEqual(self.image(4).getpixel((120, 150)), (109, 109, 109))
        self.assertEqual(self.image(8).getpixel((120, 150)), (109, 109, 109))

    def test_transition_is_inside_focus_and_has_intermediate_pixels(self):
        base = self.image(1).getpixel((120, 150)); mid = self.image(1.2).getpixel((120, 150)); color = self.image(2).getpixel((120, 150))
        self.assertNotEqual(mid, base); self.assertNotEqual(mid, color)
        self.assertEqual(base, self.image(4).getpixel((120, 150)))

    def test_no_geometry_crop_or_source_identity_changes(self):
        original = self.page.locator('#card').evaluate('e=>({box:e.getBoundingClientRect().toJSON(),href:e.getAttribute("href"),fit:e.getAttribute("preserveAspectRatio")})')
        self.image(2)
        self.assertEqual(original, self.page.locator('#card').evaluate('e=>({box:e.getBoundingClientRect().toJSON(),href:e.getAttribute("href"),fit:e.getAttribute("preserveAspectRatio")})'))
        self.assertEqual(self.page.locator('[data-documentary-id]').count(), 1)

    def test_repeated_and_backward_seeking_are_exact(self):
        before = self.image(1.2).tobytes(); self.image(8); self.image(.1)
        self.assertEqual(before, self.image(1.2).tobytes())

    def test_short_holds_reach_color_and_adjacent_windows_stay_color(self):
        result = self.page.evaluate('''()=>{const b={id:'a',windows:[{start:1,end:1.1},{start:1.1,end:1.2}]};return[LineWorldPhotoFocus.state(b,1.1).color,LineWorldPhotoFocus.state(b,1.2).color]}''')
        self.assertEqual(result, [1, 0])

    def test_invalid_intervals_and_duplicate_targets_are_rejected(self):
        result = self.page.evaluate('''()=>[()=>LineWorldPhotoFocus.state({windows:[{start:2,end:1}]},1),()=>LineWorldPhotoFocus.state({windows:[{start:1,end:3}],transition:-1},1),()=>LineWorldPhotoFocus.attach(document.querySelector('svg'),PHOTO_FOCUS_PLAN.bindings)].map(f=>{try{f();return false}catch(e){return true}})''')
        self.assertEqual(result, [True, True, True])

    def test_destroy_restores_original_dom_and_neutral_pixels(self):
        self.image(2); self.page.evaluate('photos.destroy()')
        self.assertEqual(self.page.locator('[data-lw-photo-focus]').count(), 0)
        self.assertEqual(self.page.locator('#card').get_attribute('href'), 'neutral.png')

    def test_misaligned_original_is_rejected_by_readiness(self):
        Image.new('RGB', (80, 50), 'red').save(self.root / 'wrong.png')
        result = self.page.evaluate('''async()=>{photos.destroy();try{const c=LineWorldPhotoFocus.attach(document.querySelector('svg'),[{...PHOTO_FOCUS_PLAN.bindings[0],color:'wrong.png'}]);await c.ready;return false}catch(e){return e.message.includes('aligned')}}''')
        self.assertTrue(result)

    def fixture_manifest(self, wrong_digest=False):
        original = self.root / 'card.prepared.png'; shutil.copyfile(self.root / 'original.png', original)
        digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        manifest = self.root / 'manifest.json'
        manifest.write_text(json.dumps({'assets': [{'id': 'card', 'preparedSha256': digest(original), 'sourceSha256': 'reviewed-source', 'variants': [{'id': 'gray', 'png': 'neutral.png', 'pngSha256': 'wrong' if wrong_digest else digest(self.root / 'neutral.png')}]}]}))
        bindings = self.root / 'bindings.json'; bindings.write_text(json.dumps({'bindings': [{**self.binding, 'asset': 'card', 'variant': 'gray'}]}))
        return manifest, bindings

    def test_plan_reuses_same_prepared_original_and_verifies_digests(self):
        manifest, bindings = self.fixture_manifest(); output = self.root / 'focus.json'
        self.assertTrue(plan(manifest, bindings, self.root, output)['ok'])
        actual = json.loads(output.read_text())['bindings'][0]
        self.assertEqual(actual['color'], 'card.prepared.png'); self.assertEqual(actual['neutral'], 'neutral.png')
        manifest, bindings = self.fixture_manifest(True)
        with self.assertRaises(ValueError): plan(manifest, bindings, self.root, output)

    def test_plan_rejects_colored_secondary_treatment(self):
        shutil.copyfile(self.root / 'original.png', self.root / 'neutral.png')
        manifest, bindings = self.fixture_manifest()
        with self.assertRaisesRegex(ValueError, 'grayscale'): plan(manifest, bindings, self.root, self.root / 'focus.json')

    def test_plan_merges_touching_focus_and_rejects_duplicate_targets(self):
        binding = {**self.binding, 'windows': [{'start': 2, 'end': 4}, {'start': 1, 'end': 2}]}
        self.assertEqual(normalize([binding])[0]['windows'], [{'start': 1, 'end': 4}])
        with self.assertRaises(ValueError): normalize([binding, {**binding, 'id': 'other'}])

    def audit(self, video=False):
        args = [sys.executable, str(SKILL / 'scripts/photo_focus.py'), 'inspect', '--html', str(self.html), '--output', str(self.root / 'review.json'), '--screenshot', str(self.root / 'poster.png')]
        if video: args += ['--video', str(self.root / 'preview.mp4'), '--duration', '5', '--fps', '24']
        result = subprocess.run(args, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads((self.root / 'review.json').read_text())

    def test_actual_pixel_inspector_and_encoded_preview(self):
        report = self.audit(video=True); self.assertTrue(report['ok']); self.assertTrue(report['photos'][0]['checks'][0]['visibleColorDifference'])
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(self.root / 'preview.mp4')], text=True))
        self.assertEqual(int(probe['streams'][0]['nb_frames']), 120)

    def test_inspector_excludes_its_own_color_clone_from_broad_photo_selector(self):
        self.page.close()
        self.html.write_text(self.html.read_text().replace('"target": "#card"', '"target": "image"'))
        report=self.audit()
        self.assertTrue(report['ok'],report)

    def test_inspector_rejects_a_stuck_color_layer(self):
        self.page.close()
        self.html.write_text(self.html.read_text().replace('window.renderAt=t=>photos.render(t)', 'window.renderAt=t=>photos.render(2)'))
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/photo_focus.py'), 'inspect', '--html', str(self.html), '--output', str(self.root / 'bad.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('neutralAtExit', ' '.join(json.loads((self.root / 'bad.json').read_text())['issues']))

    def test_inspector_rejects_external_plan_that_differs_from_browser(self):
        plan_path = self.root / 'different.json'
        plan_path.write_text(json.dumps({'bindings': [{**self.binding, 'windows': [{'start': 2, 'end': 5}]}]}))
        result = subprocess.run([sys.executable, str(SKILL / 'scripts/photo_focus.py'), 'inspect', '--html', str(self.html), '--plan', str(plan_path), '--output', str(self.root / 'mismatch.json')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn('plans differ', result.stdout)


if __name__ == '__main__': unittest.main()

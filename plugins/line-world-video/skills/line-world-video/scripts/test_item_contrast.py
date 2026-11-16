#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2", "pillow>=11,<13"]
# ///
"""Check final icon pixels, centered content and reversible semantic styling."""
import io
import os
import unittest
from pathlib import Path
from urllib.parse import quote
from PIL import Image
from playwright.sync_api import sync_playwright

SKILL = Path(__file__).resolve().parent.parent


class ItemContrastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        bins = sorted((Path(os.environ.get('LOCALAPPDATA', ''))/'ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'), reverse=True)
        cls.browser = cls.pw.chromium.launch(executable_path=str(bins[0]) if bins else None, headless=True)
        cls.page = cls.browser.new_page(viewport={'width': 800, 'height': 450})

    @classmethod
    def tearDownClass(cls):
        cls.browser.close(); cls.pw.stop()

    def setUp(self):
        source = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 2H22V22H2Z" fill="none" stroke="#828282" stroke-width="3"/></svg>'
        image = 'data:image/svg+xml,'+quote(source)
        self.page.set_content(f'''<style>body{{margin:0}}text{{font:24px Arial;fill:#333e48}}</style>
<svg id="stage" width="800" height="450"><defs><symbol id="source" viewBox="0 0 24 24"><path d="M2 2H22V22H2Z" fill="none" stroke="#828282" stroke-width="3"/></symbol></defs>
<g id="a"><rect id="face-a" data-lw-surface="item" x="70" y="70" width="180" height="160" fill="white"/>
<g id="glyph" data-lw-icon="monochrome" transform="translate(100 90) scale(2)"><path d="M2 2H22V22H2Z" fill="none" stroke="#828282" stroke-width="3"/></g></g>
<g id="b"><rect id="face-b" data-lw-surface="item" x="310" y="70" width="180" height="160" fill="white"/>
<use id="use" data-lw-icon="monochrome" href="#source" x="340" y="90" width="48" height="48"/></g>
<g id="c"><rect id="face-c" data-lw-surface="item" x="550" y="70" width="180" height="160" fill="white"/>
<image id="image" data-lw-icon="monochrome" href="{image}" x="580" y="90" width="48" height="48"/></g></svg>''')
        self.page.add_style_tag(path=str(SKILL/'assets/runtime/theme.css'))
        self.page.add_script_tag(path=str(SKILL/'assets/runtime/theme.js'))
        self.page.evaluate("LineWorldTheme.finish(document.querySelector('#stage'))")
        self.page.evaluate("async()=>{await Promise.all([...document.images].map(i=>i.decode()));await new Promise(requestAnimationFrame)}")

    def focus(self, value="[document.querySelector('#a'),document.querySelector('#b'),document.querySelector('#c')]", role='primary'):
        self.page.evaluate(f"LineWorldTheme.focus(document.querySelector('#stage'),{value},'{role}')")

    def audit(self):
        return self.page.evaluate("LineWorldTheme.audit(document.querySelector('#stage'))")

    def white_pixels(self, selector):
        raw = self.page.locator(selector).screenshot()
        with Image.open(io.BytesIO(raw)) as image:
            pixels=image.convert('RGB').tobytes();return sum(min(pixels[n:n+3])>235 for n in range(0,len(pixels),3))

    def test_svg_use_and_external_image_are_visibly_white_on_red(self):
        self.focus()
        for selector in ('#glyph', '#use', '#image'):
            with self.subTest(selector=selector): self.assertGreater(self.white_pixels(selector), 70)
        self.assertTrue(self.audit()['ok'], self.audit()); self.assertEqual(self.audit()['icons'], 3)

    def test_actual_background_controls_custom_repaint_and_reset(self):
        result = self.page.evaluate("""()=>{const root=document.querySelector('#stage'),face=document.querySelector('#face-a'),icon=document.querySelector('#glyph');face.style.fill='#9e1b32';LineWorldTheme.contrast(root);const red=getComputedStyle(icon).filter;face.style.fill='#e7e7e7';LineWorldTheme.contrast(root);return{red,gray:getComputedStyle(icon).filter,color:getComputedStyle(icon).color}}""")
        self.assertNotEqual(result['red'], result['gray']); self.assertEqual(result['color'], 'rgb(51, 62, 72)')

    def test_secondary_gray_also_has_white_glyphs(self):
        self.focus(role='secondary'); self.assertGreater(self.white_pixels('#glyph'), 70); self.assertTrue(self.audit()['ok'])

    def test_single_icon_is_centered_on_both_axes(self):
        self.assertEqual(self.audit()['centered'], 3)
        result = self.page.evaluate("""()=>{const a=document.querySelector('#glyph').getBoundingClientRect(),b=document.querySelector('#face-a').getBoundingClientRect();return{x:(a.left+a.right-b.left-b.right)/2,y:(a.top+a.bottom-b.top-b.bottom)/2}}""")
        self.assertLess(abs(result['x']), .01); self.assertLess(abs(result['y']), .01)

    def test_icon_and_label_center_as_one_block(self):
        self.page.locator('#a').evaluate("e=>{e.querySelector('[data-lw-content]').remove();e.insertAdjacentHTML('beforeend','<g data-lw-content data-lw-for=\"face-a\"><g data-lw-icon=\"monochrome\" transform=\"translate(90 90)\"><path d=\"M0 0H20V20H0Z\" fill=\"none\" stroke=\"gray\" stroke-width=\"3\"/></g><text x=\"120\" y=\"110\">Model</text></g>')}")
        self.page.evaluate("LineWorldTheme.finish(document.querySelector('#stage'))")
        self.assertTrue(self.audit()['ok'], self.audit())
        self.assertEqual(self.page.locator('#a [data-lw-content]').count(), 1)

    def test_centering_works_under_nonuniform_scaled_parent(self):
        self.page.locator('#a').evaluate("e=>e.setAttribute('transform','translate(10 25) scale(1.2 .8)')")
        self.page.evaluate("LineWorldTheme.center(document.querySelector('#stage'))")
        self.assertTrue(self.audit()['ok'], self.audit())

    def test_flat_minus_icon_keeps_its_stroke_and_visibility(self):
        self.page.locator('#glyph').evaluate("e=>e.innerHTML='<path d=\"M2 12H22\" fill=\"none\" stroke=\"gray\" stroke-width=\"4\"/>'")
        self.page.evaluate("LineWorldTheme.finish(document.querySelector('#stage'))"); self.focus()
        # A full-card screenshot includes stroke ink even when the geometry bbox has zero height.
        self.assertGreater(self.white_pixels('#a'), 70); self.assertTrue(self.audit()['ok'], self.audit())

    def test_icon_only_target_can_select_its_face(self):
        self.focus("document.querySelector('#glyph')")
        self.assertEqual(self.page.locator('#face-a').evaluate('e=>getComputedStyle(e).fill'), 'rgb(158, 27, 50)')
        self.assertGreater(self.white_pixels('#glyph'), 70)

    def test_missing_filter_and_off_center_content_are_reported(self):
        self.focus(); self.page.locator('#glyph').evaluate("e=>e.style.setProperty('filter','none','important')")
        self.page.locator('#a [data-lw-content]').evaluate("e=>e.setAttribute('transform','translate(18 8) '+e.getAttribute('transform'))")
        kinds = [v['kind'] for v in self.audit()['violations']]
        self.assertIn('icon-contrast', kinds); self.assertIn('content-not-centered', kinds)

    def test_encoded_values_keep_their_deliberate_alignment(self):
        result = self.page.evaluate("""()=>{const r=document.querySelector('#stage');r.insertAdjacentHTML('beforeend','<g><rect id="bar" data-lw-surface="item" data-encoding="quantity" x="70" y="300" width="300" height="70" fill="#696969"/><text id="value" x="330" y="345">9</text></g>');const a=document.querySelector('#value').getBoundingClientRect().x;LineWorldTheme.finish(r);return{same:a===document.querySelector('#value').getBoundingClientRect().x,wrapped:!!document.querySelector('#value').closest('[data-lw-content]')}}""")
        self.assertTrue(result['same']); self.assertFalse(result['wrapped'])

    def test_brand_assets_are_not_tinted(self):
        self.page.locator('#image').evaluate("e=>{e.setAttribute('data-lw-icon','brand');e.style.removeProperty('filter');e.style.removeProperty('color')}")
        self.focus(); self.assertEqual(self.page.locator('#image').evaluate('e=>getComputedStyle(e).filter'), 'none')

    def test_repeated_finish_and_focus_are_deterministic(self):
        self.focus(); first = self.page.locator('#stage').evaluate('e=>e.outerHTML')
        self.focus('null'); self.focus(); self.assertEqual(first, self.page.locator('#stage').evaluate('e=>e.outerHTML'))
        self.focus('null'); self.page.evaluate("LineWorldTheme.center(document.querySelector('#stage'))"); a = self.page.locator('#a').evaluate('e=>e.outerHTML')
        self.page.evaluate("LineWorldTheme.center(document.querySelector('#stage'))"); self.assertEqual(a, self.page.locator('#a').evaluate('e=>e.outerHTML'))


if __name__ == '__main__': unittest.main()

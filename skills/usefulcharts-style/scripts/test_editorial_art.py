#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "pillow>=11,<13"]
# ///
"""Verify visible small-size identity for formerly aliased poster emblems."""

import io
import unittest
import xml.etree.ElementTree as ET

from PIL import Image
from playwright.sync_api import sync_playwright

from editorial_art import symbol

FAMILIES = [('star', 'sun', 'compass'), ('astrolabe', 'orbit', 'globe'), ('wheel', 'gear'),
            ('lens', 'prism'), ('anchor', 'ship'), ('tower', 'observatory')]
KINDS = [kind for family in FAMILIES for kind in family]


class SemanticEmblems(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pixels = {}
        cls.bounds = {}
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={'width': 160, 'height': 160}, device_scale_factor=1)
            for size in (29, 37, 50):
                for kind in KINDS:
                    mark = symbol(kind, '#77BDDD')
                    page.set_content(f'<style>body{{margin:0}}svg{{display:block;background:white}}</style><svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 100 100"><g>{mark}</g></svg>')
                    png = page.locator('svg').screenshot()
                    raw = Image.open(io.BytesIO(png)).convert('RGB').tobytes()
                    cls.pixels[size, kind] = [tuple(raw[i:i+3]) for i in range(0, len(raw), 3)]
                    cls.bounds[size, kind] = page.locator('svg>g').evaluate('(e)=>{const b=e.getBBox();return [b.x,b.y,b.width,b.height]}')
            browser.close()

    def test_former_aliases_have_distinct_visible_small_silhouettes(self):
        for size in (29, 37, 50):
            for family in FAMILIES:
                for index, first in enumerate(family):
                    for second in family[index + 1:]:
                        with self.subTest(size=size, first=first, second=second):
                            a, b = self.pixels[size, first], self.pixels[size, second]
                            difference = sum(abs(x-y) for p,q in zip(a,b) for x,y in zip(p,q)) / (255 * 3 * len(a))
                            self.assertGreater(difference, .025)

    def test_marks_have_visible_ink_and_keep_their_nominal_footprint(self):
        for (size, kind), pixels in self.pixels.items():
            with self.subTest(size=size, kind=kind):
                ink = sum(min(pixel) < 220 for pixel in pixels) / len(pixels)
                self.assertGreater(ink, .05)
                self.assertLess(ink, .75)
                x,y,w,h = self.bounds[size, kind]
                self.assertGreaterEqual(x, -1)
                self.assertGreaterEqual(y, -1)
                self.assertLessEqual(x+w, 101)
                self.assertLessEqual(y+h, 101)

    def test_vector_resources_are_self_contained_and_deterministic(self):
        for kind in KINDS:
            mark = symbol(kind, '#B58CC9')
            root = ET.fromstring('<svg>' + mark + '</svg>')
            self.assertEqual(mark, symbol(kind, '#B58CC9'))
            self.assertTrue(list(root))
            for node in root.iter():
                self.assertNotIn(node.tag, ('script', 'image', 'foreignObject'))
                self.assertFalse(any(key.startswith('on') or key in ('href', 'xlink:href') for key in node.attrib))


if __name__ == '__main__':
    unittest.main()

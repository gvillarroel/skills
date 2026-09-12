#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Inspect actual caption pixels/geometry and reject altered visible captions."""

import unittest
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright
from audit_chart import AUDIT, check_source
from compose_branching_history import compose_history
from editorial_poster import EditorialPoster
from test_branching_layout import history

NS = {'s': 'http://www.w3.org/2000/svg'}
ET.register_namespace('', NS['s'])


class BranchCaptionAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = history()
        data['annotations'] = [
            dict(node='garden', kind='pill', label='FIELD SCIENCE COLLECTIONS', width=330, size=18, group='science'),
            dict(node='society', kind='heading', label='Western Readers', width=240, size=20, icon='book'),
        ]
        cls.source, _ = compose_history(data)
        cls.svg, _ = EditorialPoster(cls.source).render()
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()
        cls.page = cls.browser.new_page(viewport={'width':1500, 'height':1400})

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def inspect(self, svg):
        self.page.set_content(svg)
        self.page.evaluate('document.fonts.ready')
        report = self.page.evaluate(AUDIT)
        check_source(report, self.source)
        return report

    def test_full_render_retains_visible_local_captions(self):
        report = self.inspect(self.svg)
        self.assertEqual(report['findings'], [])
        self.assertEqual(len(report['branch_captions']), 2)
        self.assertTrue(report['branch_captions'][1]['artwork'])

    def test_caption_mutations_are_detected_from_rendered_svg(self):
        def target(root):
            return root.find('.//s:g[@data-annotation-id="annotation-0"]', NS)
        def remove(root):
            root.remove(target(root))
        mutations = [
            ('inventory', remove, 'source-branch-caption-inventory'),
            ('invisible', lambda root: target(root).set('opacity', '0'), 'source-branch-caption-type-or-visibility'),
            ('label', lambda root: setattr(target(root).find('s:text', NS), 'text', 'Changed claim'), 'source-branch-caption-label'),
            ('type', lambda root: target(root).find('s:text', NS).set('font-size', '8'), 'source-branch-caption-type-or-visibility'),
            ('position', lambda root: target(root).set('transform', 'translate(24 0)'), 'source-branch-caption-anchor'),
            ('color', lambda root: target(root).find('s:rect', NS).set('stroke', '#F56550'), 'source-branch-caption-color'),
        ]
        for name, mutate, expected in mutations:
            with self.subTest(mutation=name):
                root = ET.fromstring(self.svg)
                mutate(root)
                report = self.inspect(ET.tostring(root, encoding='unicode'))
                self.assertIn(expected, {finding['type'] for finding in report['findings']})

    def test_hidden_illustration_is_detected(self):
        root = ET.fromstring(self.svg)
        heading = root.find('.//s:g[@data-annotation-id="annotation-1"]', NS)
        art = next(child for child in heading if child.get('data-artwork'))
        art.set('opacity', '0')
        report = self.inspect(ET.tostring(root, encoding='unicode'))
        self.assertIn('source-branch-caption-artwork', {finding['type'] for finding in report['findings']})

    def test_unrelated_painted_path_cannot_hide_behind_family_pill(self):
        root = ET.fromstring(self.svg)
        box = root.find('.//s:g[@data-annotation-id="annotation-0"]/s:rect', NS)
        x, y, width, height = (float(box.get(key)) for key in ('x', 'y', 'width', 'height'))
        path = root.find('.//s:path[@data-edge-id="e4"]', NS)
        path.set('d', f'M {x+8} {y+height/2} L {x+width-8} {y+height/2}')
        report = self.inspect(ET.tostring(root, encoding='unicode'))
        self.assertIn('branch-caption-unrelated-path', {finding['type'] for finding in report['findings']})


if __name__ == '__main__':
    unittest.main()

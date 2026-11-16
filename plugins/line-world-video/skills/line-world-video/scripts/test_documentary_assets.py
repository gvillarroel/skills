#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13", "playwright>=1.51,<2"]
# ///
"""Verify photo identity boundaries, treatment provenance and reproducible reuse."""
import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
from PIL import Image, ImageDraw
from documentary_assets import acquire, audit, check, prepare, prepare_image


def entry():
    return {'id': 'reviewed-device', 'label': 'Fixture device', 'sourceFile': 'photo.png',
            'sourcePage': 'https://example.org/source', 'reviewed': True,
            'identityEvidence': 'Fictional acceptance fixture, manually supplied identity',
            'scope': 'Fixture only; no historical claim',
            'rights': {'creator': 'Fixture author', 'license': 'Test fixture', 'credit': 'Fixture author'},
            'model': {'expected': 'Model 580', 'observed': 'Model 580'},
            'variant': {'expected': '3 GB', 'observed': '3 GB'}, 'width': 96,
            'treatments': [{'id': 'gray', 'mode': 'grayscale'}, {'id': 'one-bit', 'mode': 'one-bit', 'ink': '#696969', 'cell': 2}]}


class DocumentaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.root = Path(self.tmp.name)
        image = Image.new('RGB', (120, 80), 'white'); d = ImageDraw.Draw(image)
        d.rounded_rectangle((10, 12, 110, 68), radius=8, fill='#426075'); d.ellipse((70, 20, 105, 55), fill='#aaaaaa')
        image.save(self.root / 'photo.png')

    def tearDown(self): self.tmp.cleanup()

    def request(self, value=None):
        path = self.root / 'request.json'; path.write_text(json.dumps({'assets': [value or entry()]}), encoding='utf-8'); return path

    def test_different_model_rejected(self):
        e = entry(); e['model']['observed'] = 'Model 590'
        with self.assertRaisesRegex(ValueError, 'model'): check(e)

    def test_wrong_memory_variant_rejected(self):
        e = entry(); e['variant']['observed'] = '1.5 GB'
        with self.assertRaisesRegex(ValueError, 'variant'): check(e)

    def test_source_review_and_rights_required(self):
        e = entry(); e['reviewed'] = False
        with self.assertRaisesRegex(ValueError, 'Review'): check(e)
        e = entry(); del e['rights']['creator']
        with self.assertRaisesRegex(ValueError, 'rights'): check(e)

    def test_crop_cannot_invent_padding(self):
        e = entry(); e['crop'] = [0, 0, 140, 80]
        with self.assertRaisesRegex(ValueError, 'Crop'): prepare_image((self.root / 'photo.png').read_bytes(), e)

    def test_local_file_takes_priority_over_provenance_url(self):
        e = entry(); e['downloadUrl'] = 'https://example.org/source-image.png'
        with patch('documentary_assets.fetch', side_effect=AssertionError('Do not redownload a supplied local file.')):
            self.assertTrue(prepare(self.request(e), self.root / 'media')['ok'])

    def test_acquisition_cache_keeps_identity_review_pending(self):
        path = self.root / 'sources/device.png'; data = (self.root / 'photo.png').read_bytes()
        with patch('documentary_assets.fetch', return_value=data) as network:
            first = acquire('https://example.org/device.png', path)
            second = acquire('https://example.org/device.png', path)
            self.assertEqual(network.call_count, 1)
        self.assertEqual(first['identityReview'], 'pending'); self.assertTrue(second['reused'])

    def test_onebit_is_exact_gray_white_and_self_contained(self):
        out = self.root / 'media'; result = prepare(self.request(), out)
        self.assertTrue(result['ok'])
        image = Image.open(out / 'reviewed-device-one-bit.png').convert('RGB')
        self.assertEqual({color for _, color in image.getcolors()}, {(105, 105, 105), (255, 255, 255)})
        root = ET.parse(out / 'reviewed-device-one-bit.svg').getroot()
        self.assertFalse(any(e.tag.split('}')[-1] in {'image', 'script', 'foreignObject'} for e in root.iter()))
        self.assertEqual((out / 'originals/reviewed-device.png').read_bytes(), (self.root / 'photo.png').read_bytes())

    def test_cache_reuses_and_repairs_modified_variant(self):
        request = self.request(); out = self.root / 'media'; prepare(request, out)
        self.assertEqual(len(prepare(request, out)['reused']), 2)
        (out / 'reviewed-device-gray.png').write_bytes(b'changed')
        result = prepare(request, out)
        self.assertEqual(result['reused'], ['reviewed-device/one-bit'])
        Image.open(out / 'reviewed-device-gray.png').verify()

    def test_physical_identity_diagram_fails_but_mechanism_passes(self):
        out = self.root / 'media'; prepare(self.request(), out)
        story = self.root / 'story.json'
        story.write_text(json.dumps({'scenes': [{'id': 'hardware', 'objects': [{'id': 'card', 'kind': 'physical', 'purpose': 'identity', 'depiction': 'diagram', 'reason': 'Decorative likeness'}]}]}))
        self.assertFalse(audit(story, out / 'manifest.json', self.root / 'bad.json')['ok'])
        story.write_text(json.dumps({'scenes': [{'id': 'mechanism', 'objects': [{'id': 'work', 'kind': 'concept', 'purpose': 'mechanism', 'depiction': 'diagram', 'reason': 'Shows task partitioning'}]}]}))
        self.assertTrue(audit(story, out / 'manifest.json', self.root / 'good.json')['ok'])

    def test_valid_photo_binding_is_not_rendered_proof(self):
        out = self.root / 'media'; prepare(self.request(), out)
        story = self.root / 'story.json'; story.write_text(json.dumps({'scenes': [{'id': 'hardware', 'objects': [{'id': 'card', 'kind': 'physical', 'purpose': 'identity', 'depiction': 'photo-treatment', 'asset': 'reviewed-device', 'variant': 'gray'}]}]}))
        result = audit(story, out / 'manifest.json', self.root / 'review.json')
        self.assertTrue(result['ok']); self.assertEqual(result['renderedVerification'], 'pending'); self.assertEqual(result['photoBindings'], 1)
        self.assertEqual(result['sourceAssetsVerified'], 1); self.assertEqual(result['oneBitPalettesVerified'], 1)

    def test_source_tamper_is_detected(self):
        out = self.root / 'media'; prepare(self.request(), out)
        (out / 'originals/reviewed-device.png').write_bytes(b'changed original')
        story = self.root / 'story.json'; story.write_text('{"scenes":[]}')
        result = audit(story, out / 'manifest.json', self.root / 'review.json')
        self.assertFalse(result['ok']); self.assertIn('changed source', result['issues'][0])

    def test_rendered_audit_captures_static_scene(self):
        out = self.root / 'media'; prepare(self.request(), out)
        story = self.root / 'story.json'; story.write_text(json.dumps({'scenes': [{'id': 'hardware', 'objects': [{'id': 'card', 'kind': 'physical', 'purpose': 'identity', 'depiction': 'photo-treatment', 'asset': 'reviewed-device', 'variant': 'gray'}]}]}))
        page = self.root / 'scene.html'; page.write_text('<div id="scene-hardware"><div data-object-id="card"><img data-documentary-id="reviewed-device" src="media/reviewed-device-gray.png"></div></div>')
        shot = self.root / 'scene.png'
        result = audit(story, out / 'manifest.json', self.root / 'review.json', page, shot)
        self.assertTrue(result['ok']); self.assertEqual(result['renderedVerification'], 'observed')
        with Image.open(shot) as image: self.assertEqual(image.size, (1920, 1080))


if __name__ == '__main__': unittest.main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Verify that the delivered source, visible poster and audit are one version."""

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from create_branch_poster import FILES, create_bundle
from test_branching_layout import history


class BranchPosterBundle(unittest.TestCase):
    def test_data_only_input_exports_one_replayable_version(self):
        data = history()
        for key in ('design', 'mode', 'layout'):
            data.pop(key)
        data['annotations'] = [dict(node='garden', kind='pill', label='FIELD COLLECTIONS', width=280, size=18)]
        original = copy.deepcopy(data)
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)/'result'
            summary = create_bundle(data, directory)
            self.assertEqual(data, original)
            self.assertEqual(set(path.name for path in directory.iterdir()), set(FILES))
            source = json.loads((directory/'source.json').read_text(encoding='utf-8'))
            self.assertEqual(source['layout'], 'authored')
            self.assertTrue(all('x' in n and 'y' in n for n in source['nodes']))
            digest = hashlib.sha256(json.dumps(source, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            root = ET.parse(directory/'poster.svg').getroot()
            metadata = json.loads(root.find('{http://www.w3.org/2000/svg}metadata[@id="chart-data"]').text)
            browser = json.loads((directory/'browser.json').read_text(encoding='utf-8'))
            self.assertEqual(metadata['data_sha256'], digest)
            self.assertEqual(browser['metadata']['data_sha256'], digest)
            self.assertEqual(browser['findings'], [])
            self.assertTrue(summary['original_fields_preserved'])

    def test_explicit_incompatible_profile_is_not_overridden(self):
        with tempfile.TemporaryDirectory() as folder:
            for key, value in [('mode', 'genealogy'), ('design', 'classic'), ('layout', 'authored')]:
                data = history()
                data[key] = value
                with self.subTest(field=key), self.assertRaises(ValueError):
                    create_bundle(data, Path(folder)/'result')

    def test_cli_cannot_overwrite_the_original_source(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            original = directory/'source.json'
            original.write_text(json.dumps(history()), encoding='utf-8')
            before = original.read_bytes()
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('create_branch_poster.py')),
                                     str(original), '--output-dir', str(directory)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('input and output paths must be distinct', result.stderr)
            self.assertEqual(original.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()

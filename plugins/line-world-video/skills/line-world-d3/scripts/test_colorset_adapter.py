#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check actual named-builder palette defaults and paint adaptation boundaries."""
import json
from pathlib import Path
import tempfile
import unittest
from colorset_adapter import adapt_artifact, CONTRACT
from check_palette_contract import validate_artifact


class ColorsetTests(unittest.TestCase):
    def test_default_preserves_geometry_labels_and_source_bytes(self):
        source = '<body><svg viewBox="0 0 200 80"><path fill="#007298" d="M1,2L30,40"/><image href="data:image/png;base64,aBc123=="/><text fill="#9ecae1">Exact label</text></svg></body>'
        adapted = adapt_artifact(source)
        self.assertIn('d="M1,2L30,40"', adapted)
        self.assertIn('data:image/png;base64,aBc123==', adapted)
        self.assertIn('Exact label', adapted)
        self.assertIn('data-colorset="colorset1"', adapted)
        self.assertNotIn('#007298', adapted)

    def test_both_contracts_accept_every_extended_and_legacy_token(self):
        palette = json.loads(CONTRACT.read_text())["colorsets"]["colorset2"]["allowed"]
        source = '<body><svg>' + ''.join(f'<path fill="{value}"/>' for value in palette + ['#fff', '#9ecae1']) + '</svg></body>'
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            for active in ('colorset1', 'colorset2'):
                output = Path(directory) / (active + '.html')
                output.write_text(adapt_artifact(source, active), encoding='utf-8')
                self.assertTrue(validate_artifact(output, colorset=active)["ok"])

    def test_unknown_contract_rejected(self):
        with self.assertRaises(ValueError):
            adapt_artifact('<svg/>', 'neon')

    def test_vendor_runtime_bytes_are_not_authored_paint(self):
        vendor = '<script id="d3-runtime">const libraryDefault="#007298"; const hiddenMarkup="<svg fill=\\"#123456\\">";</script>'
        source = '<body>' + vendor + '<svg><rect fill="#007298"/></svg></body>'
        adapted = adapt_artifact(source)
        self.assertIn(vendor, adapted)
        self.assertIn('<rect fill="#333e48"/>', adapted)

    def test_hex_looking_geometry_references_are_preserved(self):
        source = '<svg><style>#abcdef {stroke:#123456}</style><defs><marker id="abcdef"/></defs><path marker-end="url(#abcdef)" stroke="#123456"/><use href="#abcdef"/></svg>'
        adapted = adapt_artifact(source)
        self.assertIn('#abcdef {', adapted)
        self.assertIn('url(#abcdef)', adapted)
        self.assertIn('href="#abcdef"', adapted)
        self.assertNotIn('stroke="#123456"', adapted)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            output = Path(directory) / "geometry.svg"
            output.write_text(adapted, encoding="utf-8")
            self.assertTrue(validate_artifact(output, colorset="colorset1")["ok"])


if __name__ == '__main__':
    unittest.main()

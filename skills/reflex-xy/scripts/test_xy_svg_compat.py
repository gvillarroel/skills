#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Test the narrowly scoped native XY line-symbol SVG compatibility repair."""
import unittest
import xml.etree.ElementTree as ET

from xy_svg_compat import repair_duplicate_line_symbol_fill

PREFIX = '<svg xmlns="http://www.w3.org/2000/svg">'
BROKEN = '<path d="M 1 2 L 3 4" fill="none" fill="#9e1b32" stroke="#9e1b32" stroke-width="1"/>'


class SvgCompatibility(unittest.TestCase):
    def test_known_broken_glyph_retains_path_and_stroke_with_no_fill(self):
        source = PREFIX + BROKEN + '</svg>'
        result, count = repair_duplicate_line_symbol_fill(source)
        self.assertEqual(count, 1)
        self.assertEqual(result, source.replace('fill="#9e1b32"', '', 1))
        node = ET.fromstring(result)[0]
        self.assertEqual(node.attrib, {"d": "M 1 2 L 3 4", "fill": "none", "stroke": "#9e1b32", "stroke-width": "1"})

    def test_valid_svg_and_comment_text_remain_byte_identical(self):
        source = PREFIX + '<!-- ' + BROKEN + ' -->' + '<path d="M 1 2" fill="none" stroke="#000000"/></svg>'
        self.assertEqual(repair_duplicate_line_symbol_fill(source), (source, 0))

    def test_multiple_line_glyphs_are_counted_without_touching_solid_shapes(self):
        solid = '<path d="M 0 0 L 1 1" fill="#9e1b32"/>'
        source = PREFIX + BROKEN + solid + BROKEN.replace('#9e1b32', '#007298') + '</svg>'
        result, count = repair_duplicate_line_symbol_fill(source)
        self.assertEqual(count, 2)
        nodes = ET.fromstring(result)
        self.assertEqual([n.get('fill') for n in nodes], ['none', '#9e1b32', 'none'])
        self.assertIn(solid, result)

    def test_unrelated_duplicate_attributes_are_rejected(self):
        for broken in (
            '<path d="M 0 0" fill="#ffffff" fill="#000000" stroke="#000000"/>',
            '<path d="M 0 0" fill="none" fill="#9e1b32" stroke="#000000"/>',
            '<rect fill="none" fill="#9e1b32" stroke="#9e1b32"/>',
            BROKEN.replace('stroke-width="1"', 'stroke-width="1" stroke-width="2"'),
        ):
            with self.subTest(broken=broken), self.assertRaises(ValueError):
                repair_duplicate_line_symbol_fill(PREFIX + broken + '</svg>')

    def test_other_malformed_xml_is_not_hidden_by_a_known_glyph(self):
        with self.assertRaises(ValueError):
            repair_duplicate_line_symbol_fill(PREFIX + BROKEN + '<g></svg>')

    def test_non_svg_root_is_rejected(self):
        with self.assertRaises(ValueError):
            repair_duplicate_line_symbol_fill('<root/>')


if __name__ == '__main__':
    unittest.main()

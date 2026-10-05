#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check categorical priorities without changing existing numeric SVG bands."""
from dataclasses import replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from build_procedural_svg import Context, ORDERED_VALUE_COLORS, PALETTES, render_join_tree_mastery, render_simulation
from build_connected_scene import build_scene, NS
from solid_style import category_style

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'assets/palettes/colorsets.json'


def context(name):
    return Context(spec={'id': 'numeric-test', 'variant': 4, 'signature': 'numeric-test'}, seed=73, width=960, height=640, duration_ms=6000, palette_name=name, palette=PALETTES[name], motion='full', parameters={})


class CategoryOrderTests(unittest.TestCase):
    def test_connected_nodes_and_allocator_follow_usable_categories(self):
        palette = json.loads(CONTRACT.read_text(encoding='utf-8'))['colorsets']['colorset1']
        labels = ['Receive', 'Barcode', 'Analyze', 'Review', 'Archive', 'Quarantine']
        root = build_scene(dict(labels=labels, palette='colorset1', seed=73, duration_ms=6000, width=None, height=None, include_return=True))
        actual = [node.find(f'{{{NS}}}rect').get('fill') for node in root.findall(f'.//{{{NS}}}g[@id="scene-nodes"]/{{{NS}}}g')]
        expected = [category_style(i, palette)['fill'] for i in range(len(labels))]
        self.assertEqual(actual, expected)
        self.assertEqual(actual[:3], ['#9e1b32', '#000000', '#828282'])
        for index, paint in enumerate(palette['solidSequence']):
            self.assertEqual(context('colorset1').color(index), [value for value in palette['solidSequence'] if value != '#ffffff'][index % 16])

    def test_gray_scott_svg_bands_match_legacy_numeric_mapping_byte_for_byte(self):
        frame = [[.025 + (column % 6 + .1) / 24 for column in range(32)] for _ in range(20)]
        with patch('build_procedural_svg.precompute_gray_scott', return_value=[frame, frame]):
            for name in ['colorset1', 'colorset2']:
                ctx = context(name)
                current = render_simulation(ctx)
                legacy = replace(ctx, palette=dict(ctx.palette, accents=list(ORDERED_VALUE_COLORS[name])))
                with patch.object(Context, 'value_color', Context.color):
                    prior = render_simulation(legacy)
                self.assertEqual(current, prior)
                self.assertTrue(all(f'fill="{paint}"' in current for paint in ORDERED_VALUE_COLORS[name]))

    def test_join_tree_scalar_field_keeps_legacy_values_and_geometry(self):
        samples = [dict(id=i, x=i / 5, y=.5, value=i / 5) for i in range(6)]
        state = {'geometry': {'samples': samples, 'triangles': [], 'joinTree': {'nodes': [], 'arcs': []}, 'columns': 6, 'rows': 1}}
        with patch('build_procedural_svg.render_snapshot_series', return_value=''), patch('build_procedural_svg.mastery_timeline', return_value=''):
            for name in ['colorset1', 'colorset2']:
                ctx = context(name)
                field = render_join_tree_mastery(ctx, state)['field']
                legacy = replace(ctx, palette=dict(ctx.palette, accents=list(ORDERED_VALUE_COLORS[name])))
                with patch.object(Context, 'value_color', Context.color):
                    prior = render_join_tree_mastery(legacy, state)['field']
                self.assertEqual(field, prior)
                self.assertTrue(all(f'fill="{paint}"' in field for paint in ORDERED_VALUE_COLORS[name]))


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check source fidelity while allowing legitimate composed geometry."""

import copy
import unittest

from compose_branching_history import compose_history
from test_branching_layout import history
from verify_branch_source import verify_fields


class BranchSourcePreservation(unittest.TestCase):
    def setUp(self):
        self.source = history()
        self.source['annotations'] = [dict(node='garden', kind='pill', label='FIELD COLLECTIONS', width=280, size=18)]
        self.resolved, _ = compose_history(self.source)

    def test_added_coordinates_corridors_and_caption_offsets_are_valid(self):
        self.assertNotEqual(self.source['nodes'], self.resolved['nodes'])
        self.assertNotEqual(self.source['edges'], self.resolved['edges'])
        self.assertNotEqual(self.source['annotations'], self.resolved['annotations'])
        self.assertEqual(verify_fields(self.source, self.resolved)['findings'], [])
        reordered = copy.deepcopy(self.resolved)
        reordered['nodes'].reverse()
        reordered['edges'].reverse()
        self.assertEqual(verify_fields(self.source, reordered)['findings'], [])

    def test_changed_source_meaning_cannot_hide_behind_new_geometry(self):
        changes = [
            lambda data: data['nodes'][0].update(label='A different institution'),
            lambda data: data['nodes'][0].update(founded=1850),
            lambda data: data['nodes'][0].pop('detail'),
            lambda data: data['edges'][0].update(kind='influence'),
            lambda data: data['annotations'][0].update(label='A different branch'),
            lambda data: data['groups'][0].update(color='#F56550'),
            lambda data: data['nodes'].append(dict(data['nodes'][0])),
            lambda data: data['nodes'].__setitem__(1, dict(data['nodes'][0])),
        ]
        for index, change in enumerate(changes):
            with self.subTest(change=index):
                value = copy.deepcopy(self.resolved)
                change(value)
                self.assertEqual(verify_fields(self.source, value)['status'], 'fail')

    def test_nested_source_claims_and_explicit_geometry_remain_required(self):
        original = dict(nodes=[dict(id='n', research={'shelves':['A','B'], 'verified':True}, width=210)])
        resolved = dict(nodes=[dict(id='n', research={'shelves':['A','B'], 'verified':True, 'index':4}, width=210, x=400)])
        self.assertEqual(verify_fields(original, resolved)['status'], 'pass')
        for key, value in [('width', 190), ('research', {'shelves':['B','A'], 'verified':True}),
                           ('research', {'shelves':['A','B'], 'verified':1})]:
            changed = copy.deepcopy(resolved)
            changed['nodes'][0][key] = value
            self.assertEqual(verify_fields(original, changed)['status'], 'fail')


if __name__ == '__main__':
    unittest.main()

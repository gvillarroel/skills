#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify complete data-first branching composition and its supported boundaries."""

import copy
import unittest

from compose_branching_history import compose_history
from editorial_poster import EditorialPoster
from render_chart import collinear_overlap


def history():
    return dict(id='branch-composition', title='A HISTORY OF PUBLIC COLLECTIONS', design='editorial', mode='lineage',
                layout='branches', source_note='Fictional development data.',
                groups=[dict(id='civic', label='Civic collections', color='#F7CD26'),
                        dict(id='science', label='Scientific collections', color='#77BDDD')],
                nodes=[dict(id=nid, label=label, founded=year, date_label=str(year), group=group, detail=detail)
                       for nid, label, year, group, detail in [
                           ('cabinet', 'Common Cabinet', 1700, 'civic', ''),
                           ('room', 'Eastern Reading Room', 1714, 'civic', 'A separate subscribing body'),
                           ('garden', 'Garden Archive', 1721, 'science', ''),
                           ('society', 'Western Book Society', 1736, 'civic', ''),
                           ('register', 'Seed Register', 1740, 'science', ''),
                           ('library', 'United Public Library', 1778, 'civic', 'The two collections unite'),
                           ('institute', 'Field Study Institute', 1820, 'science', '')]],
                edges=[dict(id=f'e{i}', source=a, target=b, kind=kind) for i, (a, b, kind) in enumerate([
                    ('cabinet', 'room', 'branch'), ('cabinet', 'garden', 'branch'),
                    ('room', 'society', 'branch'), ('garden', 'register', 'branch'),
                    ('room', 'library', 'branch'), ('society', 'library', 'branch'),
                    ('register', 'institute', 'branch'), ('library', 'institute', 'influence')])])


class BranchingLayoutTests(unittest.TestCase):
    def test_complete_composition_preserves_facts_and_chooses_influence_ports(self):
        source = history()
        source['nodes'][2]['research'] = {'shelf': 'B', 'wording': 'exact source wording'}
        before = copy.deepcopy(source)
        result, report = compose_history(source)
        self.assertEqual(source, before)
        self.assertEqual(result['groups'], source['groups'])
        for original, resolved in zip(source['nodes'], result['nodes']):
            self.assertEqual({k: resolved[k] for k in original}, original)
        for original, resolved in zip(source['edges'], result['edges']):
            self.assertEqual({k: resolved[k] for k in original}, original)
            self.assertIn('via', resolved)
        self.assertEqual(report['node_count'], 7)
        self.assertEqual(report['edge_count'], 8)
        self.assertEqual(result['layout'], 'authored')
        self.assertEqual(report['influence_choices'][0]['search'], 'local')
        poster = EditorialPoster(result)
        poster.render()
        for i, a in enumerate(poster.routes):
            for b in poster.routes[i + 1:]:
                if {a['source'], a['target']} & {b['source'], b['target']}:
                    continue
                self.assertFalse(any(collinear_overlap(p, q, r, s, tolerance=2.3) > .05
                                     for p, q in zip(a['points'], a['points'][1:])
                                     for r, s in zip(b['points'], b['points'][1:])))

    def test_partial_dates_do_not_create_a_calendar_or_invent_years(self):
        source = history()
        source['nodes'][0].pop('founded')
        source['nodes'][0]['date_label'] = 'date unknown'
        result, report = compose_history(source)
        self.assertEqual(report['order'], 'causal')
        self.assertNotIn('founded', result['nodes'][0])
        self.assertEqual(result['nodes'][0]['date_label'], 'date unknown')

    def test_explicit_foundation_order_requires_complete_finite_dates(self):
        for missing in (None, 'unknown', float('nan'), True):
            source = history()
            source['branch_order'] = 'founded'
            source['nodes'][0]['founded'] = missing
            with self.subTest(value=missing), self.assertRaisesRegex(ValueError, 'finite numeric founded'):
                compose_history(source)

    def test_dates_and_tall_captions_retain_complete_attachment_space(self):
        source = history()
        source['nodes'][2]['detail'] = 'The entire original descriptive note survives across several wrapped lines of ordinary explanatory text.'
        source['nodes'][2]['size'] = 22
        source['font_size'] = 20
        result, _ = compose_history(source)
        self.assertEqual(result['font_size'], 20)
        self.assertEqual(result['nodes'][2]['size'], 22)
        self.assertEqual(result['nodes'][2]['detail'], source['nodes'][2]['detail'])
        self.assertEqual(EditorialPoster(result).render()[1]['node_collisions'], 0)

    def test_prescribed_positions_routes_and_small_pages_are_not_silently_overridden(self):
        for field, value, error in [('x', 400, 'infer positions'), ('y', 350, 'infer positions')]:
            source = history()
            source['nodes'][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, error):
                compose_history(source)
        source = history()
        source['edges'][0]['via'] = [[100, 300], [400, 300]]
        with self.assertRaisesRegex(ValueError, 'absolute routes'):
            compose_history(source)
        for key, value, error in [('width', 400, 'widest branching stage'), ('height', 600, 'branching stories need')]:
            source = history()
            source[key] = value
            with self.subTest(field=key), self.assertRaisesRegex(ValueError, error):
                compose_history(source)

    def test_cycles_unknown_endpoints_and_partnerships_require_correct_source_structure(self):
        source = history()
        source['edges'].append(dict(id='cycle', source='institute', target='cabinet', kind='branch'))
        with self.assertRaisesRegex(ValueError, 'cycle'):
            compose_history(source)
        source = history()
        source['edges'][0]['target'] = 'missing'
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            compose_history(source)
        source = history()
        source['unions'] = [dict(id='partners', partners=['room', 'garden'])]
        with self.assertRaisesRegex(ValueError, 'partnerships'):
            compose_history(source)


if __name__ == '__main__':
    unittest.main()

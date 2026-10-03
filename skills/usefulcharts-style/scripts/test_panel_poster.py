#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Check semantic preservation and balanced packing on adversarial small graphs."""
import copy
import unittest
from pathlib import Path
import json
import tempfile
from create_panel_poster import compose, assign_columns, render
from audit_panel_poster import audit

class PanelCases(unittest.TestCase):
    def source(self):
        return dict(title='Three branches',position_semantics='A schematic outline, not numeric time.',
            groups=[dict(id='a',label='Alpha',color='#4f4f4f'),dict(id='b',label='Beta',color='#9e1b32')],
            nodes=[dict(id='a1',group='a',label='Alpha',date_label='Date disputed',detail='Preserve this qualification.'),
                   dict(id='a2',group='a',label='Second',date_label='1981–83'),
                   dict(id='b1',group='b',label='Third',date_label='Unknown')],
            edges=[dict(id='one',source='a1',target='a2',kind='branch'),dict(id='two',source='a2',target='b1',kind='influence')])

    def test_input_and_qualified_fields_remain_unchanged(self):
        source=self.source();before=copy.deepcopy(source);copied,layout=compose(source)
        self.assertEqual(source,before);self.assertEqual(copied,before)
        copied['nodes'][0]['detail']='changed';self.assertEqual(source,before)
        self.assertEqual(set(layout['nodes']),{'a1','a2','b1'})

    def test_typed_portals_have_both_named_endpoints(self):
        _,layout=compose(self.source())
        a=layout['nodes']['a2']['links'][0];b=layout['nodes']['b1']['links'][0]
        self.assertEqual((a['other'],b['other']),('b1','a2'))
        self.assertEqual((a['role'],b['role']),('out','in'))
        self.assertIn('contribution',a['text']);self.assertEqual(a['number'],b['number'])

    def test_small_finished_columns_are_reclaimed(self):
        # Greedy source order produces loads 124 and 192. Reassignment produces
        # 188 and 128 while preserving the source order inside each column.
        heights=[100,40,40,40]
        assignment=assign_columns(heights,2)
        loads=[sum(h+24 for h,c in zip(heights,assignment) if c==i) for i in range(2)]
        self.assertEqual(max(loads),188)

    def test_local_cycle_is_rejected(self):
        source=self.source();source['edges'].append(dict(id='cycle',source='a2',target='a1',kind='branch'))
        with self.assertRaisesRegex(ValueError,'acyclic'):compose(source)

    def test_merge_is_not_silently_converted_to_one_parent(self):
        source=self.source();source['nodes'].append(dict(id='a3',label='Additional parent',group='a'))
        source['edges'].append(dict(id='extra',source='a3',target='a2',kind='branch'))
        with self.assertRaisesRegex(ValueError,'one incoming'):compose(source)
        source['edges'][-1]['portal']=True
        _,layout=compose(source);self.assertEqual(len(layout['portals']),2)

    def test_missing_endpoint_fails(self):
        source=self.source();source['edges'][0]['target']='missing'
        with self.assertRaisesRegex(ValueError,'endpoints'):compose(source)

    def test_no_implicit_axis_or_dropped_rich_objects(self):
        source=self.source();source.pop('position_semantics')
        with self.assertRaisesRegex(ValueError,'position_semantics'):compose(source)
        source=self.source();source['unions']=[dict(id='union')]
        with self.assertRaisesRegex(ValueError,'does not render'):compose(source)

    def test_color_contrast_is_enforced(self):
        source=self.source();source['groups'][0]['color']='#e7e7e7'
        with self.assertRaisesRegex(ValueError,'contrast'):compose(source)

    def test_narrow_panels_keep_qualified_labels(self):
        source=self.source();_,layout=compose(source,columns=3,panel_width=420)
        visible=' '.join(e['text'] for n in layout['nodes'].values() for e in n['entries'])
        self.assertIn('Date disputed',visible);self.assertIn('1981–83',visible)

    def test_nested_art_exports_root_and_detects_text_occlusion(self):
        source,layout=compose(self.source());svg=render(source,layout)
        node=layout['nodes']['a1'];x,y=node['x'],node['y']
        nested=f'<svg data-art-id="covering-art" x="{x}" y="{y}" width="200" height="70" viewBox="0 0 200 70"><rect width="200" height="70" fill="#000"/></svg>'
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            base=Path(folder);(base/'source.json').write_text(json.dumps(source));(base/'poster.svg').write_text(svg.replace('</svg>',nested+'</svg>'),encoding='utf-8')
            report=audit(base/'poster.svg',base/'source.json',base/'poster.png')
            self.assertTrue((base/'poster.png').is_file())
            self.assertTrue(any(i['type']=='image-text-overlap' for i in report['findings']))

    def test_clipped_sheet_bounds_do_not_create_false_overlaps(self):
        source,layout=compose(self.source());svg=render(source,layout)
        nested='<svg data-art-id="clipped-sheet" x="5" y="195" width="15" height="15" viewBox="0 0 15 15" overflow="hidden"><rect width="5000" height="5000" fill="#000"/></svg>'
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as folder:
            base=Path(folder);(base/'source.json').write_text(json.dumps(source));(base/'poster.svg').write_text(svg.replace('</svg>',nested+'</svg>'),encoding='utf-8')
            report=audit(base/'poster.svg',base/'source.json')
            self.assertFalse(any(i['type']=='image-text-overlap' for i in report['findings']))
            self.assertEqual(report['images'][0]['box'],dict(x=5,y=195,w=15,h=15))

if __name__=='__main__':unittest.main()

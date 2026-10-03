#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check fixed calendar footprints, interval reuse and complete source retention."""
import copy
import unittest
from pack_shared_rows import pack


class SharedRows(unittest.TestCase):
    def brief(self):
        return dict(mode='numeric',width=800,top=60,gap=10,row_gap=20,
                    groups=[dict(id='a',members=['one','two','overlap'],header_height=30)],
                    records=[dict(id='one',owner='ship-a',x0=100,x1=200,height=70),
                             dict(id='two',owner='ship-a',x0=400,x1=500,height=70),
                             dict(id='overlap',owner='ship-b',x0=150,x1=280,height=80)])

    def test_fixed_x_and_reused_track(self):
        src=self.brief();out=pack(src);box={b['id']:b for b in out['layout']['boxes']}
        self.assertEqual(box['one']['y'],box['two']['y'])
        self.assertNotEqual(box['one']['y'],box['overlap']['y'])
        for r in src['records']:
            self.assertEqual((box[r['id']]['x'],box[r['id']]['w']),(r['x0'],r['x1']-r['x0']))
        self.assertEqual(out['layout']['row_count'],2)

    def test_source_and_identity_preserved(self):
        src=self.brief();before=copy.deepcopy(src);out=pack(src)
        self.assertEqual(src,before);self.assertEqual(out['source'],before)
        out['source']['records'][0]['owner']='changed'
        self.assertEqual(src,before)

    def test_compact_groups_reuse_empty_epochs(self):
        src=self.brief();src['compact_groups']=True
        src['records']+=[dict(id='late',owner='later',x0=550,x1=680,height=50)]
        src['groups']+=[dict(id='b',members=['late'],header_height=30,label_width=150)]
        out=pack(src)['layout'];a,b=out['groups']
        self.assertEqual(a['y'],b['y'])
        self.assertGreaterEqual(b['x'],a['x']+a['w']+src['gap'])

    def test_title_envelope_forces_vertical_separation(self):
        src=self.brief();src['compact_groups']=True;src['groups'][0]['label_width']=600
        src['records']+=[dict(id='late',x0=550,x1=680,height=50)]
        src['groups']+=[dict(id='b',members=['late'])]
        a,b=pack(src)['layout']['groups']
        self.assertGreaterEqual(b['y'],a['y']+a['h']+src['row_gap'])

    def test_reuse_one_track_while_another_family_track_continues(self):
        src=dict(mode='numeric',width=900,top=30,gap=12,track_gap=16,
                 reuse_tracks=True,labels_in_footprints=True,
                 groups=[dict(id='first',members=['long','short']),dict(id='next',members=['later'])],
                 records=[dict(id='long',owner='long',x0=60,x1=800,height=70),
                          dict(id='short',owner='short',x0=80,x1=200,height=100),
                          dict(id='later',owner='later',x0=220,x1=500,height=80)])
        before=copy.deepcopy(src);out=pack(src);boxes={b['id']:b for b in out['layout']['boxes']}
        self.assertEqual(out['source'],before);self.assertEqual(src,before)
        self.assertEqual(boxes['short']['row'],boxes['later']['row'])
        self.assertNotEqual(boxes['long']['row'],boxes['later']['row'])
        self.assertEqual(out['layout']['cross_group_rows'],1)
        self.assertEqual(out['layout']['height'],216)
        for r in src['records']:
            self.assertEqual((boxes[r['id']]['x'],boxes[r['id']]['w']),(r['x0'],r['x1']-r['x0']))

    def test_track_reuse_requires_measured_local_identity(self):
        src=self.brief();src['reuse_tracks']=True
        with self.assertRaisesRegex(ValueError,'locally identified'):pack(src)
        src['labels_in_footprints']=True
        with self.assertRaisesRegex(ValueError,'local labels'):pack(src)

    def test_reused_track_clearance_at_exact_boundary(self):
        src=self.brief();src.update(reuse_tracks=True,labels_in_footprints=True)
        src['groups'][0].pop('header_height');src['records'][1]['x0']=210
        box={b['id']:b for b in pack(src)['layout']['boxes']}
        self.assertEqual(box['one']['row'],box['two']['row'])
        src['records'][1]['x0']=209.9
        box={b['id']:b for b in pack(src)['layout']['boxes']}
        self.assertNotEqual(box['one']['row'],box['two']['row'])

    def test_invalid_contracts_fail(self):
        for change in ('outside','nan','missing','duplicate','empty-id','title-outside'):
            with self.subTest(change=change):
                src=self.brief()
                if change=='outside':src['records'][0]['x1']=900
                if change=='nan':src['records'][0]['height']=float('nan')
                if change=='missing':src['groups'][0]['members'].pop()
                if change=='duplicate':src['groups'][0]['members'].append('one')
                if change=='empty-id':src['records'][0]['id']=''
                if change=='title-outside':src.update(compact_groups=True);src['groups'][0]['label_width']=900
                with self.assertRaises(ValueError):pack(src)


if __name__=='__main__':unittest.main()

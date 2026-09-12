#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "shapely>=2,<3"]
# ///
"""Check context fidelity, bounded placement, and complete obstacle avoidance."""

import copy
import math
import unittest
import xml.etree.ElementTree as ET

from editorial_poster import EditorialPoster
from editorial_landmarks import landmark_content
from place_context_landmarks import fit_landmarks


def brief():
    return dict(id='landmark-contract',title='A REGIONAL HISTORY',design='editorial',mode='lineage',layout='authored',
        width=1200,height=1000,source_note='Fictional test data.',
        groups=[dict(id='red',label='Alder',color='#F56550')],
        nodes=[dict(id='a',label='First archive',realm='The Alder March',group='red',x=450,y=250,width=140),
            dict(id='b',label='Later archive',realm='Bayeux & Coast',group='red',x=700,y=500,width=140)],
        edges=[dict(id='e',source='a',target='b',kind='branch')],
        annotations=[dict(kind='landmark',node='b',field='realm',width=160,size=18,dx=-160,dy=0,
            icon='heraldry',art_size=36,art_position='beside')])


class LandmarkTests(unittest.TestCase):
    def test_render_preserves_source_and_exposes_exact_visible_value(self):
        data=brief();before=copy.deepcopy(data);svg,_=EditorialPoster(data).render()
        self.assertEqual(data,before);root=ET.fromstring(svg);ns={'s':'http://www.w3.org/2000/svg'}
        a=root.find('.//s:g[@data-annotation-kind="landmark"]',ns)
        self.assertEqual(a.get('data-context-node'),'b');self.assertEqual(a.get('data-source-value'),'Bayeux & Coast')
        words=' '.join(t.text for t in a.findall('s:text[@data-content-role="landmark-label"]',ns))
        self.assertEqual(words,'Bayeux & Coast')

    def test_mismatched_annotation_label_is_rejected(self):
        data=brief();data['annotations'][0]['label']='Invented place'
        with self.assertRaisesRegex(ValueError,'match'):EditorialPoster(data).render()

    def test_missing_source_field_is_rejected(self):
        data=brief();data['annotations'][0]['field']='missing'
        with self.assertRaisesRegex(ValueError,'existing source field'):EditorialPoster(data).render()

    def test_unknown_anchor_is_rejected(self):
        data=brief();data['annotations'][0].pop('node')
        with self.assertRaisesRegex(ValueError,'known person'):EditorialPoster(data).render()

    def test_category_cannot_be_reassigned(self):
        data=brief();data['annotations'][0]['group']='blue'
        with self.assertRaisesRegex(ValueError,'category'):EditorialPoster(data).render()

    def test_numeric_field_cannot_be_presented_as_a_place(self):
        data=brief();data['annotations'][0]['field']='x'
        with self.assertRaisesRegex(ValueError,'text value'):EditorialPoster(data).render()

    def test_landmark_covering_a_node_is_rejected(self):
        data=brief();data['annotations'][0]['dx']=0
        with self.assertRaisesRegex(ValueError,'covers a person'):EditorialPoster(data).render()

    def test_artwork_requires_an_identifier(self):
        data=brief();a=data['annotations'][0];a.pop('icon')
        with self.assertRaisesRegex(ValueError,'icon identifier'):landmark_content(a,data['nodes'][1])

    def test_unreadable_eyebrow_is_rejected(self):
        data=brief();a=data['annotations'][0];a['eyebrow_size']=5
        with self.assertRaisesRegex(ValueError,'eight'):landmark_content(a,data['nodes'][1])

    def test_full_path_blocks_the_requested_label_pocket(self):
        data=brief();nodes={n['id']:n for n in data['nodes']};before=copy.deepcopy(data)
        geometry=dict(rectangles=[[630,480,770,520]],paths=[[[500,350],[500,650]]])
        result,report=fit_landmarks(data,geometry,nodes,1200,1000,step=8)
        a=result['annotations'][0];n=nodes['b'];m=landmark_content(a,n);x=n['x']+a['dx']
        self.assertFalse(x-m['width']/2<505 and x+m['width']/2>495)
        self.assertEqual(data,before);self.assertEqual(result['nodes'],data['nodes']);self.assertEqual(result['edges'],data['edges'])
        self.assertLessEqual(math.hypot(a['dx'],a['dy']),240);self.assertEqual(len(report['placements']),1)

    def test_impossible_local_pocket_keeps_original_data(self):
        data=brief();before=copy.deepcopy(data);nodes={n['id']:n for n in data['nodes']}
        with self.assertRaisesRegex(ValueError,'No local pocket'):
            fit_landmarks(data,dict(rectangles=[[0,0,1200,1000]],paths=[]),nodes,1200,1000,step=8)
        self.assertEqual(data,before)

    def test_placement_does_not_silently_expand_search(self):
        data=brief();data['annotations'][0]['vertical_radius']=400
        with self.assertRaisesRegex(ValueError,'local search radius'):
            fit_landmarks(data,dict(rectangles=[],paths=[]),{n['id']:n for n in data['nodes']},1200,1000,step=8)

    def test_clear_pocket_cannot_belong_to_a_closer_competing_category(self):
        data=brief();data['nodes'].append(dict(id='rival',label='Another family',group='blue',x=540,y=500,width=120))
        nodes={n['id']:n for n in data['nodes']}
        result,_=fit_landmarks(data,dict(rectangles=[[630,480,770,520],[480,480,600,520]],paths=[]),nodes,1200,1000,step=8)
        a=result['annotations'][0];x=700+a['dx'];y=500+a['dy']
        same=min(math.hypot(x-n['x'],y-n['y']) for n in data['nodes'] if n['group']=='red')
        other=math.hypot(x-540,y-500)
        self.assertLessEqual(same,other+12)


if __name__=='__main__':unittest.main(verbosity=2)

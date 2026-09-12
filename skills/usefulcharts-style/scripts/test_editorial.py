#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify editorial-specific semantics, artwork safety, and numeric geometry."""

import copy
import json
import unittest
import xml.etree.ElementTree as ET

from editorial_poster import EditorialPoster
from render_chart import segment_hits

NS={'s':'http://www.w3.org/2000/svg'}


def graph():
    return dict(id='editorial-contract',title='A SMALL HISTORY',design='editorial',mode='lineage',width=1200,height=1400,
        source_note='Synthetic test data.',groups=[dict(id='red',label='Red',color='#F56550'),dict(id='blue',label='Blue',color='#77BDDD')],
        nodes=[dict(id='root',label='The founding school',group='red',x=600,y=240,width=145,style='pill'),
               dict(id='left',label='Western academy',group='red',x=320,y=510,width=120,style='plain'),
               dict(id='right',label='Eastern society',group='blue',x=820,y=640,width=120,style='emblem',icon='book',icon_width=25)],
        edges=[dict(id='a',source='root',target='left',kind='branch'),dict(id='b',source='root',target='right',kind='influence')])


def timeline():
    return dict(id='editorial-time',title='CHRONOLOGY',design='editorial',mode='timeline',width=1200,height=1400,
        source_note='Synthetic intervals.',groups=[dict(id='g',label='Region',color='#98BD92')],
        time=dict(start=1000,end=2000,step=100),lanes=[dict(id='lane',label='A region')],
        periods=[dict(id='a',label='Early council',group='g',lane='lane',start=1000,end=1400,offset=30,bar_width=40),
                 dict(id='b',label='Later council',group='g',lane='lane',start=1450,end=2000,offset=60,bar_width=55)],
        transitions=[dict(id='s',source='a',target='b',kind='succession')],
        events=[dict(lane='lane',year=1300,label='A dated event',offset=190,width=200)])


class EditorialTests(unittest.TestCase):
    def test_source_is_unchanged_and_all_entities_survive(self):
        data=graph();before=copy.deepcopy(data)
        svg,report=EditorialPoster(data).render();root=ET.fromstring(svg)
        self.assertEqual(data,before)
        self.assertEqual({g.attrib['data-node-id'] for g in root.findall('.//s:g[@data-node-id]',NS)},{'root','left','right'})
        self.assertEqual(report['edge_count'],2)

    def test_actual_paths_have_rounded_bends_and_distinct_semantics(self):
        svg,_=EditorialPoster(graph()).render();root=ET.fromstring(svg)
        paths=root.findall('.//s:path[@data-edge-id]',NS)
        self.assertTrue(all('Q' in p.attrib['d'] for p in paths))
        self.assertEqual({p.attrib['data-kind'] for p in paths},{'branch','influence'})
        self.assertTrue(next(p for p in paths if p.attrib['data-kind']=='influence').attrib['stroke-dasharray'])

    def test_automatic_layout_can_render_an_unplaced_brief(self):
        data=graph();data['layout']='auto'
        for n in data['nodes']:
            for key in ('x','y','width','style','icon'):n.pop(key,None)
        svg,report=EditorialPoster(data).render()
        self.assertEqual(report['node_count'],3)
        self.assertEqual(len(report['resolved_layout']['nodes']),3)

    def test_artwork_attribute_injection_is_rejected(self):
        data=graph();data['nodes'][2]['icon']='book" onload="alert(1)'
        with self.assertRaisesRegex(ValueError,'Unknown original artwork'):EditorialPoster(data).render()

    def test_museum_sample_is_embedded_with_source_identity(self):
        data=graph();data['nodes'][2]['icon']='museum-864'
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        image=root.find('.//s:image',NS)
        self.assertTrue(image.attrib['href'].startswith('data:image/jpeg;base64,'))
        credit=root.find('.//s:metadata[@data-artwork-source]',NS)
        self.assertEqual(json.loads(credit.text)['id'],864)

    def test_unknown_parent_is_not_silently_dropped(self):
        data=graph();data['edges'][0]['source']='missing'
        with self.assertRaisesRegex(ValueError,'Unresolved relation'):EditorialPoster(data).render()

    def test_corridor_beyond_target_does_not_enter_target(self):
        data=graph();data['edges'][0]['corridor_y']=560
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        meta=json.loads(root.find('.//s:metadata[@id="chart-data"]',NS).text)
        for edge in meta['routes']:
            self.assertFalse(any(segment_hits(a,b,box) for a,b in zip(edge['points'],edge['points'][1:]) for box in meta['boxes'].values()))

    def test_authored_route_through_own_box_is_rejected(self):
        data=graph();data['edges'][0]['via']=[[600,240],[320,240]]
        with self.assertRaisesRegex(ValueError,'crosses a node'):EditorialPoster(data).render()

    def test_rotated_interval_keeps_exact_time_endpoints(self):
        data=timeline();svg,report=EditorialPoster(data).render();root=ET.fromstring(svg)
        metadata=json.loads(root.find('.//s:metadata[@id="chart-data"]',NS).text)
        top,bottom=metadata['time_y']
        box=root.find('.//s:g[@data-node-id="a"]/s:rect[@data-node-box]',NS)
        self.assertAlmostEqual(float(box.attrib['y']),top,places=2)
        self.assertAlmostEqual(float(box.attrib['height']),.4*(bottom-top),places=2)
        self.assertEqual(report['edge_count'],1)
        self.assertIn('rotate(-90',svg)

    def test_event_date_is_placed_on_the_shared_scale(self):
        svg,_=EditorialPoster(timeline()).render();root=ET.fromstring(svg)
        meta=json.loads(root.find('.//s:metadata[@id="chart-data"]',NS).text)
        y0,y1=meta['time_y'];expected=y0+.3*(y1-y0)+10.5
        event=next(t for t in root.findall('.//s:text',NS) if t.text=='A dated event')
        self.assertAlmostEqual(float(event.attrib['y']),expected,places=2)

    def test_duplicate_transitions_are_rejected(self):
        data=timeline();data['transitions']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate timeline transition'):EditorialPoster(data).render()

    def test_filled_transition_preserves_period_endpoints(self):
        data=timeline();data['transitions'][0]['style']='ribbon'
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        fill=root.find('.//s:path[@data-transition-fill]',NS)
        self.assertIsNotNone(fill)
        meta=json.loads(root.find('.//s:metadata[@id="chart-data"]',NS).text)
        a,b=meta['boxes']['a'],meta['boxes']['b'];path=meta['routes'][0]['points']
        self.assertAlmostEqual(path[0][1],a[1]+a[3])
        self.assertAlmostEqual(path[-1][1],b[1])

    def test_object_sample_preserves_aspect_and_provenance(self):
        data=timeline();data['events'][0]['icon']='object-90589'
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        self.assertEqual(root.find('.//s:image',NS).attrib['preserveAspectRatio'],'xMidYMid meet')
        self.assertEqual(json.loads(root.find('.//s:metadata[@data-artwork-source]',NS).text)['title'],'Astrolabe')

    def test_backward_continuation_is_rejected(self):
        data=timeline();data['transitions'][0].update(source='b',target='a')
        with self.assertRaisesRegex(ValueError,'must not go backward'):EditorialPoster(data).render()


if __name__=='__main__':unittest.main(verbosity=2)

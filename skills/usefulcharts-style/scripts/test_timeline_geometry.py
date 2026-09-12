#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Verify visible duration, weighted lanes, exact attachments and note clearance."""

import copy
import unittest
import xml.etree.ElementTree as ET

from editorial_poster import EditorialPoster
from pack_timeline_events import pack_events, obstacles_for
from test_editorial import timeline
from timeline_geometry import lane_geometry, period_parts, transition_geometry
from shapely.geometry import box

NS = {'s': 'http://www.w3.org/2000/svg'}


class TimelineGeometryTests(unittest.TestCase):
    def test_equal_lane_defaults_keep_previous_coordinates(self):
        lanes = [dict(id=str(i)) for i in range(5)]
        result = lane_geometry(lanes, 1800)
        self.assertEqual(result, {str(i): (110+i*325,325) for i in range(5)})
        for lane in lanes: lane['weight'] = 3
        self.assertEqual(result, lane_geometry(lanes, 1800))

    def test_weights_allocate_space_without_changing_order_or_total(self):
        lanes = [dict(id='a',weight=3),dict(id='b',weight=1)]
        original = copy.deepcopy(lanes); result = lane_geometry(lanes,1175)
        self.assertEqual(result, {'a':(110,750),'b':(860,250)})
        self.assertEqual(lanes,original)

    def test_invalid_lane_definitions_fail(self):
        for lanes in ([],[dict(id='a'),dict(id='a')],[dict(id='a',weight=0)],
                      [dict(id='a',weight=-1)],[dict(id='a',weight=float('nan'))]):
            with self.subTest(lanes=lanes), self.assertRaises(ValueError): lane_geometry(lanes,1200)

    def test_stem_draws_exact_duration_and_separate_name_capsule(self):
        data=timeline(); data['periods'][0].update(treatment='stem',stem_width=4)
        before=copy.deepcopy(data);poster=EditorialPoster(data);svg,_=poster.render();root=ET.fromstring(svg)
        node=root.find('.//s:g[@data-node-id="a"]',NS);stem=node.find('s:rect[@data-period-stem]',NS)
        label=node.find('s:rect[@data-period-label]',NS);envelope=poster.boxes['a']
        self.assertEqual(float(stem.get('width')),4)
        self.assertAlmostEqual(float(stem.get('y')),190)
        self.assertAlmostEqual(float(stem.get('height')),(1400-302)*.4,places=2)
        self.assertLess(float(label.get('height')),envelope[3]/2)
        self.assertEqual(node.find('s:rect[@data-node-box]',NS).get('fill'),'none')
        self.assertEqual(data,before)

    def test_name_position_changes_no_dates_or_endpoints(self):
        data=timeline();node=data['periods'][0];node.update(treatment='stem',label_position=0)
        first=EditorialPoster(data);first.render();node['label_position']=1
        last=EditorialPoster(data);last.render()
        self.assertEqual(first.boxes,last.boxes)
        self.assertEqual(first.routes,last.routes)
        self.assertLess(first.nodes['a']['_label_box'][1],last.nodes['a']['_label_box'][1])

    def test_invalid_treatment_or_style_fields_fail(self):
        for fields in (dict(treatment='bubble'),dict(stem_width=5),dict(label_position=.5),
                       dict(treatment='stem',stem_width=1),dict(treatment='stem',stem_width=41),
                       dict(treatment='stem',label_position=1.1)):
            with self.subTest(fields=fields):
                data=timeline();data['periods'][0].update(fields)
                with self.assertRaises(ValueError):EditorialPoster(data).render()

    def test_stem_ports_must_attach_to_the_visible_center(self):
        data=timeline();data['periods'][0]['treatment']='stem';data['transitions'][0]['source_port']=.3
        with self.assertRaisesRegex(ValueError,'centered'):EditorialPoster(data).render()
        with self.assertRaisesRegex(ValueError,'centered'):pack_events(data)

    def test_bridge_tapers_to_actual_stem_without_widening_duration(self):
        a=dict(treatment='stem',stem_width=4);b={}
        first,last,spans=transition_geometry(dict(style='ribbon',ribbon_width=10),a,b,(100,200,40,200),(300,430,60,100))
        self.assertEqual((first,last),((120,400),(330,430)))
        self.assertEqual(spans,[(118,122),(325,335)])
        self.assertEqual(transition_geometry(dict(style='ribbon'),a,b,(100,200,40,200),(300,430,60,100))[2],[(118,122),(300,360)])

    def test_weighted_periods_and_events_share_one_origin(self):
        data=timeline();data['lanes']=[dict(id='other',label='Narrow',weight=1),dict(id='lane',label='Wide',weight=3)]
        data['events'][0]['id']='note';poster=EditorialPoster(data);svg,_=poster.render();root=ET.fromstring(svg)
        lane_x=110+(1200-175)/4
        self.assertAlmostEqual(poster.boxes['a'][0],lane_x+30)
        event=root.find('.//s:g[@data-event-id="note"]/s:text',NS)
        self.assertAlmostEqual(float(event.get('x')),lane_x+190)

    def test_compact_timeline_respects_weighted_measured_label_widths(self):
        data=timeline();data.update(layout='compact');data.pop('height');data.pop('width')
        data['lanes']=[dict(id='lane',label='Wide',weight=2),dict(id='narrow',label='Narrow',weight=1)]
        data['events']=[];poster=EditorialPoster(data);poster.render()
        lane_width=(poster.w-175)*2/3
        self.assertEqual(poster.nodes['a']['label_width'],lane_width-30-40-30)

    def test_packer_uses_free_space_beside_stem_but_reserves_capsule(self):
        data=timeline();data['periods']=data['periods'][:1];data['transitions']=[]
        data['periods'][0].update(treatment='stem',label_position=1,offset=0,bar_width=280)
        data['events']=[dict(id='note',lane='lane',year=1030,label='A note',detail='A short record.',offset=0,width=110)]
        original=copy.deepcopy(data);result,_=pack_events(data,max_width=110)
        self.assertEqual(result['events'][0]['offset'],0)
        self.assertEqual(data,original)
        scale=lambda year:190+(year-1000)/1000*1098
        shapes=obstacles_for(result,scale,lane_geometry(result['lanes'],1200))
        parts=period_parts(result['periods'][0],(110,190,280,439.2))
        self.assertEqual(len(shapes),2)
        x,y,w,h=parts[1]
        self.assertTrue(any(shape.intersects(box(x+1,y+1,x+w-1,y+h-1)) for shape in shapes))


if __name__=='__main__':unittest.main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Check preservation and difficult boundaries of dated note placement."""

import copy
import unittest
from pack_timeline_events import pack_events
from timeline_annotations import event_content


def brief():
    return dict(design='editorial',mode='timeline',width=1100,height=1500,
        time=dict(start=1800,end=2000),lanes=[dict(id='east'),dict(id='west')],
        periods=[dict(id='early',lane='east',start=1800,end=1870,offset=0,bar_width=30),
                 dict(id='later',lane='east',start=1890,end=2000,offset=160,bar_width=30)],
        transitions=[dict(id='change',source='early',target='later',kind='succession',style='ribbon')],
        events=[dict(id='late',lane='west',year=1920,label='A shared charter',detail='Two town councils agree common rules.',size=13,detail_size=11),
                dict(id='first',lane='east',year=1840,label='A school opens',detail='Teachers establish public classes.',size=13,detail_size=11)])


class NarrativePlacementTests(unittest.TestCase):
    def test_preserves_complete_source_and_input_order(self):
        source=brief();original=copy.deepcopy(source);result,report=pack_events(source)
        self.assertEqual(source,original)
        self.assertEqual([e['id'] for e in result['events']],['late','first'])
        for event in result['events']:
            event.pop('offset');event.pop('width')
        self.assertEqual(result,original)
        self.assertEqual(report['event_count'],2)

    def test_places_note_outside_its_contemporary_period(self):
        result,_=pack_events(brief());event=result['events'][1]
        self.assertGreaterEqual(event['offset'],30)
        self.assertEqual((event['year'],event['size']),(1840,13))

    def test_retains_exact_boundary_year_after_a_period_ends(self):
        source=brief();source['transitions']=[]
        source['events']=[dict(id='boundary',lane='east',year=1870,label='1870',width=80,offset=0)]
        result,_=pack_events(source)
        self.assertEqual(result['events'][0]['year'],1870)
        self.assertEqual(result['events'][0]['offset'],0)

    def test_rejects_an_obstructed_note_instead_of_moving_its_date(self):
        source=brief();source['lanes']=[dict(id='east')]
        source['periods']=[dict(id='full',lane='east',start=1800,end=2000,offset=0,bar_width=925)]
        source['transitions']=[];source['events']=source['events'][1:]
        with self.assertRaisesRegex(ValueError,'No readable placement'):pack_events(source)

    def test_reserves_the_whole_image_and_preserves_dimensions(self):
        source=brief();source['events']=source['events'][:1]
        source['events'][0].update(icon='illustration-clock-escapement',art_width=90,art_height=120)
        result,report=pack_events(source)
        self.assertEqual(result['events'][0]['art_height'],120)
        self.assertGreater(report['decisions'][0]['height'],120)
        self.assertGreaterEqual(result['events'][0]['width'],90)

    def test_catches_an_image_that_cannot_fit(self):
        source=brief();source['events']=source['events'][:1]
        source['events'][0].update(icon='illustration-clock-escapement',art_width=900,art_height=120)
        with self.assertRaisesRegex(ValueError,'No readable placement'):pack_events(source)

    def test_supports_uncertain_orthogonal_continuity(self):
        source=brief();source['transitions'][0].update(kind='uncertain',style='dotted')
        result,_=pack_events(source)
        self.assertEqual(result['transitions'],source['transitions'])

    def test_rejects_duplicate_events_and_unknown_lanes(self):
        source=brief();source['events'].append(copy.deepcopy(source['events'][0]))
        with self.assertRaisesRegex(ValueError,'distinct IDs'):pack_events(source)
        source=brief();source['events'][0]['lane']='missing'
        with self.assertRaisesRegex(ValueError,'known lanes'):pack_events(source)

    def test_rejects_backwards_time_and_invalid_ports(self):
        source=brief();source['periods'][1]['start']=1850
        with self.assertRaisesRegex(ValueError,'backward'):pack_events(source)
        source=brief();source['transitions'][0]['source_port']=0
        with self.assertRaisesRegex(ValueError,'five units'):pack_events(source)

    def test_above_image_reserves_a_preceding_period(self):
        source=brief();source['transitions']=[]
        source['events']=[dict(id='boundary',lane='east',year=1870,label='1870',width=150,offset=0,
            icon='illustration-square-rigged-ship',art_position='above',art_width=100,art_height=120)]
        result,_=pack_events(source)
        self.assertGreater(result['events'][0]['offset'],0)
        self.assertEqual(result['events'][0]['year'],1870)

    def test_above_image_must_fit_below_timeline_header(self):
        source=brief();source['events']=source['events'][:1]
        source['events'][0].update(year=1800,icon='illustration-stagecoach',art_position='above',art_width=100,art_height=45)
        with self.assertRaisesRegex(ValueError,'No readable placement'):pack_events(source)

    def test_each_arrangement_keeps_words_dates_dimensions_and_type(self):
        for position in ('above','below','left','right'):
            with self.subTest(position=position):
                source=brief();source['events']=source['events'][:1]
                source['events'][0].update(icon='illustration-stagecoach',art_position=position,art_width=70,art_height=35)
                result,_=pack_events(source,max_width=220)
                result['events'][0].pop('offset');result['events'][0].pop('width')
                self.assertEqual(result,source)

    def test_invalid_art_arrangement_reports_the_actual_problem(self):
        for extra in (dict(art_position='above'),dict(icon='illustration-stagecoach',art_position='under')):
            source=brief();source['events'][0].update(extra)
            with self.assertRaisesRegex(ValueError,'art_position'):pack_events(source)

    def test_text_date_anchor_is_independent_of_image_direction(self):
        for position in ('above','below','left','right'):
            event=dict(label='A brief heading',detail='A complete explanatory note.',icon='illustration-stagecoach',
                art_position=position,art_width=60,art_height=30,size=13,detail_size=11)
            content=event_content(event,220);art=content['art'];line=content['lines'][0]
            self.assertEqual(line['y'],0)
            self.assertEqual(line['x'],68 if position=='left' else 0)
            self.assertEqual(art[2:],(60,30))
            if position=='above':self.assertEqual(art[1],-35)
            elif position=='below':self.assertGreater(art[1],content['lines'][-1]['box'][1])
            else:self.assertEqual(art[1],0)

    def test_side_art_leaves_readable_text_width(self):
        event=dict(label='A complete heading',icon='illustration-stagecoach',art_position='left',art_width=100,art_height=40)
        with self.assertRaisesRegex(ValueError,'positive text width'):event_content(event,108)

    def test_default_side_width_adds_image_to_the_prose_budget(self):
        source=brief();source['events']=source['events'][:1]
        source['events'][0].update(icon='illustration-stagecoach',art_position='left',art_width=110,art_height=45)
        result,_=pack_events(source)
        self.assertEqual(result['events'][0]['width'],288)
        capped,_=pack_events(source,max_width=220)
        self.assertLessEqual(capped['events'][0]['width'],220)

    def test_an_earlier_note_cannot_be_covered_by_later_above_art(self):
        source=brief();source['periods']=[];source['transitions']=[]
        source['events']=[dict(id='one',lane='west',year=1900,label='Existing note',offset=0,width=160),
            dict(id='two',lane='west',year=1910,label='Later note',offset=0,width=160,
            icon='illustration-square-rigged-ship',art_position='above',art_width=110,art_height=110)]
        result,_=pack_events(source)
        self.assertGreater(result['events'][1]['offset'],result['events'][0]['offset'])


if __name__=='__main__':unittest.main()

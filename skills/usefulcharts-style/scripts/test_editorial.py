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
    def test_influence_attachments_follow_all_four_envelope_sides(self):
        from editorial_poster import attachment_port
        for source_side in ('left','right','top','bottom'):
            for target_side in ('left','right','top','bottom'):
                with self.subTest(source=source_side,target=target_side):
                    data=graph();data['edges'][1].update(source_port=source_side,target_port=target_side)
                    before=copy.deepcopy(data);poster=EditorialPoster(data);svg,_=poster.render()
                    route=next(edge for edge in poster.routes if edge['id']=='b')
                    self.assertEqual(route['points'][0],attachment_port(poster.boxes['root'],source_side)[0])
                    self.assertEqual(route['points'][-1],attachment_port(poster.boxes['right'],target_side)[0])
                    self.assertFalse(any(segment_hits(a,b,box) for a,b in zip(route['points'],route['points'][1:]) for box in poster.boxes.values()))
                    self.assertEqual(data,before)

    def test_lateral_descent_and_unknown_ports_are_rejected(self):
        for kind,side in [('branch','left'),('influence','diagonal')]:
            with self.subTest(kind=kind,side=side):
                data=graph();data['edges'][1].update(kind=kind,source_port=side)
                with self.assertRaises(ValueError):EditorialPoster(data).render()

    def test_lateral_authored_path_cannot_enter_its_own_target(self):
        data=graph();data['edges'][1].update(source_port='right',target_port='left',via=[[900,240],[900,640]])
        with self.assertRaisesRegex(ValueError,'crosses a node'):EditorialPoster(data).render()

    def test_influence_composer_freezes_complete_facts_and_preserves_input(self):
        from route_influences import compose_influences
        data=graph();before=copy.deepcopy(data);result,report=compose_influences(data)
        self.assertEqual(data,before);self.assertEqual(result['nodes'],before['nodes'])
        self.assertEqual(report['selected'],['b'])
        for original,edge in zip(data['edges'],result['edges']):
            self.assertEqual({k:v for k,v in edge.items() if k not in ('via','source_port','target_port')},original)
        self.assertEqual(EditorialPoster(result).render()[1]['edge_count'],2)

    def test_influence_composer_retains_authored_choices_unless_requested(self):
        from route_influences import compose_influences
        data=graph();data['edges'][1].update(source_port='right',target_port='left')
        result,report=compose_influences(data)
        self.assertEqual(result,data);self.assertFalse(report['changed'])
        result,report=compose_influences(data,replace_authored=True)
        self.assertTrue(report['changed']);self.assertEqual(report['selected'],['b'])

    def test_influence_composer_rejects_unresolved_coordinates(self):
        from route_influences import compose_influences
        for layout in ('auto','packed','cohorts'):
            with self.subTest(layout=layout):
                data=graph();data['layout']=layout
                with self.assertRaisesRegex(ValueError,'Resolve the first layout'):compose_influences(data)

    def test_heading_icon_clears_complete_multiline_heading(self):
        data=graph();data['annotations']=[dict(x=950,y=320,width=180,size=18,kind='heading',
            label='A thousand years\nof recorded descent',icon='crown')]
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        heading=root.find('.//s:g[@data-annotation-kind="heading"]',NS)
        self.assertIsNotNone(heading);self.assertEqual(heading.get('data-annotation-id'),'annotation-0')
        art=heading.find('s:g[@data-artwork="crown"]',NS)
        import re
        x,y,sx,sy=map(float,re.findall(r'-?\d+(?:\.\d+)?',art.get('transform')))
        first=min(float(t.get('y')) for t in heading.findall('s:text',NS))
        self.assertLessEqual(y+100*sy,first-18)

    def test_packed_story_measures_page_without_mutating_relative_hints(self):
        data=graph();data.update(layout='packed');data.pop('width');data.pop('height')
        for node in data['nodes']:
            node.pop('width');node.pop('style',None)
            node.update(date_label='c. 1710',detail='A named historical consequence.')
        before=copy.deepcopy(data);poster=EditorialPoster(data);svg,report=poster.render()
        self.assertEqual(data,before);self.assertEqual(poster.font,18)
        self.assertLess(poster.w*poster.h,1200*1400)
        self.assertEqual(report['resolved_layout']['layout'],'packed')
        by_id={n['id']:n for n in report['resolved_layout']['nodes']}
        self.assertLess(by_id['left']['x'],by_id['root']['x']);self.assertLess(by_id['root']['x'],by_id['right']['x'])
        self.assertLess(by_id['root']['y'],by_id['left']['y']);self.assertLess(by_id['left']['y'],by_id['right']['y'])
        root=ET.fromstring(svg)
        self.assertEqual(len(root.findall('.//s:text[@data-content-role="date"]',NS)),3)
        self.assertLess(max(c['box'][1]+c['box'][3] for c in poster.data['_cohort_key']['cells']),min(b[1] for b in poster.boxes.values()))

    def test_packed_story_rejects_ambiguous_hints_and_absolute_routes(self):
        data=graph();data.update(layout='packed');data['nodes'][1].update(x=600,y=240)
        with self.assertRaisesRegex(ValueError,'identical hints'):EditorialPoster(data).render()
        data=graph();data.update(layout='packed');data['edges'][0]['corridor_y']=400
        with self.assertRaisesRegex(ValueError,'absolute routes'):EditorialPoster(data).render()
        data=graph();data.update(layout='packed');data['nodes'][1]['y']=100
        with self.assertRaisesRegex(ValueError,'successor below'):EditorialPoster(data).render()

    def test_packed_long_labels_keep_all_pairs_separated_and_all_merger_ports(self):
        data=graph();data.update(layout='packed');data.pop('width');data.pop('height')
        data['nodes']=[dict(id=f'n{i}',label=f'Public collection and historical reading society {i}',detail='A documented consequence retained in full.',date_label=str(1700+i),group='red' if i%2 else 'blue',x=(i%4)*3+(i//4)*.2,y=i//4+1) for i in range(16)]
        data['edges']=[dict(id=f'e{i}',source=f'n{i-4}',target=f'n{i}',kind='branch') for i in range(4,16)]
        data['edges'].append(dict(id='merger',source='n9',target='n12',kind='branch'))
        poster=EditorialPoster(data);svg,report=poster.render()
        self.assertEqual(report['node_count'],16);self.assertEqual(report['edge_count'],13)
        self.assertEqual(report['node_collisions'],0)
        self.assertTrue(all(n['size']>=18 for n in poster.nodes.values()))
        self.assertTrue(all(not segment_hits(a,b,box,0) for edge in poster.routes for a,b in zip(edge['points'],edge['points'][1:]) for box in poster.boxes.values()))

    def test_external_date_name_and_caption_preserve_content_and_compact_color(self):
        data=graph()
        data['nodes'][1].update(detail_position='outside',date_label='c. 1710–1715',detail='The two collections unite in a public institution.',style='card')
        before=copy.deepcopy(data);poster=EditorialPoster(data);svg,_=poster.render();root=ET.fromstring(svg)
        self.assertEqual(data,before)
        node=root.find('.//s:g[@data-node-id="left"]',NS)
        envelope=node.find('s:rect[@data-content-envelope]',NS);panel=node.find('s:rect[@data-name-panel]',NS)
        top=float(panel.get('y'));bottom=top+float(panel.get('height'))
        self.assertLess(float(panel.get('height')),float(envelope.get('height'))*.6)
        for role,expected in [('date','c. 1710–1715'),('name','Western academy'),('caption',data['nodes'][1]['detail'])]:
            lines=node.findall(f's:text[@data-content-role="{role}"]',NS)
            self.assertEqual(' '.join(t.text for t in lines),expected)
            for line in lines:
                y=float(line.get('y'))
                if role=='date':self.assertLess(y,top)
                elif role=='caption':self.assertGreater(y,bottom)
                else:self.assertTrue(top<y<bottom)

    def test_routes_avoid_external_captions_and_connect_above_dates(self):
        data=graph()
        for n in data['nodes']:n.update(detail_position='outside',date_label='1750',detail='A documented historical consequence.')
        poster=EditorialPoster(data);poster.render()
        for edge in poster.routes:
            source=poster.boxes[edge['source']];target=poster.boxes[edge['target']]
            self.assertEqual(edge['points'][0][1],source[1]+source[3])
            self.assertEqual(edge['points'][-1][1],target[1])
            self.assertFalse(any(segment_hits(a,b,box,0) for a,b in zip(edge['points'],edge['points'][1:]) for box in poster.boxes.values()))

    def test_separate_date_cannot_be_silently_dropped(self):
        data=graph();data['nodes'][0]['date_label']='1720'
        with self.assertRaisesRegex(ValueError,'date_label requires detail_position'):EditorialPoster(data).render()
        data['nodes'][0].update(detail_position='floating')
        with self.assertRaisesRegex(ValueError,'detail_position must be'):EditorialPoster(data).render()

    def test_external_content_measures_empty_and_wrapped_variants(self):
        for fields in ({},{'date_label':'1710'},{'detail':'Reorganised after the collections were combined.'},{'date_label':'Founded circa 1710; reorganised in 1740','detail':'Two predecessor societies unite.'}):
            data=graph();data.update(layout='auto');data.pop('width');data.pop('height')
            for node in data['nodes']:node.update(detail_position='outside',**fields)
            svg,report=EditorialPoster(data).render()
            self.assertEqual(report['node_count'],3)
            root=ET.fromstring(svg)
            self.assertEqual(len(root.findall('.//s:rect[@data-content-envelope]',NS)),3)

    def test_compact_cohort_key_wraps_above_the_first_generation(self):
        data=graph();data.update(mode='genealogy',layout='cohorts',edges=[])
        data.pop('width');data.pop('height')
        palette=['#77BDDD','#F56550','#98BD92','#EBCB3C','#B992C9','#EFAC63','#A7A49D']
        data['groups']=[dict(id=f'g{i}',label=f'Founding house {i} and its documented descendants',color=palette[i]) for i in range(7)]
        data['nodes']=[dict(id='a',label='First founder',group='g0',row=0),dict(id='c',label='Second founder',group='g2',row=0),dict(id='b',label='Their child',group='g1',row=1)]
        data['unions']=[dict(id='u',partners=['a','c'],children=['b'])]
        poster=EditorialPoster(data);svg,_=poster.render()
        key=poster.data['_cohort_key'];self.assertEqual(len(key['cells']),7)
        self.assertGreater(key['height'],25)
        first=min(box[1] for box in poster.boxes.values())
        self.assertLess(max(c['box'][1]+c['box'][3] for c in key['cells']),first)
        for group in data['groups']:self.assertIn(group['label'].split()[2],svg)
        data['legend']=False;without_key=EditorialPoster(data);without_key.render()
        self.assertNotIn('_cohort_key',without_key.data)
        self.assertLess(without_key.h,poster.h)

    def test_small_cohorts_measure_page_and_keep_partner_categories(self):
        data=graph();data.update(mode='genealogy',layout='cohorts',edges=[])
        data.pop('width');data.pop('height')
        data['nodes']=[dict(id='a',label='A long founding name',detail='1800–1870',group='red',row=0),
                       dict(id='b',label='A second founder',detail='1802–1878',group='blue',row=0),
                       dict(id='c',label='The recorded child',detail='1830–1900',group='blue',row=1)]
        data['unions']=[dict(id='u',partners=['a','b'],children=['c'])]
        before=copy.deepcopy(data);poster=EditorialPoster(data);svg,report=poster.render()
        self.assertEqual(data,before);self.assertLess(poster.h,1000);self.assertEqual(poster.font,18)
        root=ET.fromstring(svg)
        self.assertEqual(root.find('.//s:g[@data-node-id="c"]',NS).get('data-group'),'blue')
        positions={n['id']:n for n in report['resolved_layout']['nodes']}
        self.assertEqual(positions['a']['y'],positions['b']['y'])
        self.assertLess(positions['c']['y']-positions['a']['y'],400)

    def test_compact_timeline_has_readable_horizontal_dates_and_exact_duration(self):
        data=timeline();data.update(layout='compact',events=[])
        data.pop('width');data.pop('height')
        for period in data['periods']:
            for key in ('offset','bar_width'):period.pop(key,None)
        before=copy.deepcopy(data);poster=EditorialPoster(data);svg,_=poster.render();root=ET.fromstring(svg)
        self.assertEqual(data,before);self.assertLess(poster.h,1200)
        for period in data['periods']:
            node=root.find(f'.//s:g[@data-node-id="{period["id"]}"]',NS)
            self.assertIsNotNone(node.find('s:rect[@data-label-box="true"]',NS))
            labels=node.findall('s:text',NS)
            self.assertTrue(all('transform' not in t.attrib for t in labels))
            self.assertIn(str(period['start']),''.join(t.text or '' for t in labels))
            box=poster.boxes[period['id']]
            self.assertAlmostEqual(box[1],poster.top+(period['start']-1000)/1000*(poster.bottom-poster.top))
            self.assertAlmostEqual(box[3],(period['end']-period['start'])/1000*(poster.bottom-poster.top))

    def test_compact_timeline_rejects_short_page_without_falsifying_dates(self):
        data=timeline();data.update(layout='compact',height=600,events=[])
        data['periods'][0].update(end=1002,label='A consequential event with a long exact name')
        with self.assertRaisesRegex(ValueError,'more vertical space'):EditorialPoster(data).render()

    def test_compact_auto_measures_content_and_keeps_merger_category(self):
        data=graph();data.update(layout='auto')
        data.pop('width');data.pop('height')
        for n in data['nodes']:
            for k in ('x','y','width','style','icon'):n.pop(k,None)
        data['nodes'].append(dict(id='merged',label='Regional Institute',group='red',detail='Two schools combined'))
        data['edges']=[dict(id='a',source='root',target='left',kind='branch'),dict(id='b',source='root',target='right',kind='branch'),
            dict(id='c',source='left',target='merged',kind='branch'),dict(id='d',source='right',target='merged',kind='branch')]
        before=copy.deepcopy(data);poster=EditorialPoster(data);svg,report=poster.render();root=ET.fromstring(svg)
        self.assertEqual(data,before);self.assertLess(poster.h,1200);self.assertEqual(poster.font,18)
        merged=root.find('.//s:g[@data-node-id="merged"]',NS)
        self.assertEqual(merged.attrib['data-group'],'red');self.assertEqual(merged.attrib['data-treatment'],'hero')
        self.assertEqual((report['node_count'],report['edge_count']),(4,4))

    def test_major_era_rules_leave_the_year_gutter_clear(self):
        data=timeline();data['eras']=[dict(start=1200,end=1600,label='Middle era')]
        poster=EditorialPoster(data);svg,_=poster.render();root=ET.fromstring(svg)
        rule=root.find('.//s:path[@data-era-rule="1200"]',NS)
        first_x=float(rule.attrib['d'].split()[1])
        label=next(t for t in root.findall('.//s:text',NS) if t.text=='1200')
        self.assertGreater(first_x,float(label.attrib['x'])+5)

    def test_source_illustrations_embed_once_with_identity(self):
        data=graph()
        for node in data['nodes'][1:]:node.update(icon='illustration-astrolabe-observation',icon_width=25,width=170)
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        self.assertEqual(svg.count('data:image/svg+xml;base64,'),1)
        self.assertEqual(len(root.findall('.//s:use',NS)),2)
        credit=root.find('.//s:metadata[@data-artwork-source="astrolabe-observation.svg"]',NS)
        self.assertIn('Pearson Scott Foresman',json.loads(credit.text)['creator'])
        data['nodes'][1]['icon']='illustration-../../outside'
        with self.assertRaisesRegex(ValueError,'Unknown source illustration'):EditorialPoster(data).render()

    def test_timeline_artwork_cannot_cover_a_period(self):
        data=timeline();data['events'][0].update(icon='illustration-sextant-1904',offset=0,width=65,art_size=60)
        with self.assertRaisesRegex(ValueError,'artwork overlaps period'):EditorialPoster(data).render()

    def test_rectangular_event_illustration_keeps_declared_viewport(self):
        data=timeline();data['events'][0].update(icon='illustration-astrolabe-observation',art_width=160,art_height=110)
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        art=root.find('.//s:svg[@data-illustration-id="astrolabe-observation"]',NS)
        self.assertEqual(art.attrib['viewBox'],'0 0 160 110')
        use=art.find('s:use',NS)
        self.assertEqual((use.attrib['width'],use.attrib['height']),('160','110'))
        data['events'][0]['art_height']=-1
        with self.assertRaisesRegex(ValueError,'positive dimensions'):EditorialPoster(data).render()

    def test_map_has_an_adjacent_source_derived_key(self):
        data=graph();data['insets']=[dict(kind='map',title='Regions',box=[90,780,450,350],countries={'FRA':'red','DEU':'blue'},legend=True)]
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        labels=[t for t in root.findall('.//s:text',NS) if t.text in ('Red','Blue')]
        self.assertEqual({t.text for t in labels},{'Red','Blue'})
        self.assertTrue(all(800<float(t.attrib['y'])<900 for t in labels))

    def test_map_rejects_unresolved_categories(self):
        data=graph();data['insets']=[dict(kind='map',title='Regions',box=[90,780,450,350],countries={'FRA':'missing'},legend=True)]
        with self.assertRaisesRegex(ValueError,'unknown group'):EditorialPoster(data).render()

    def test_isotype_can_include_a_small_named_category(self):
        data=graph();data['insets']=[dict(kind='isotype',title='Records',box=[90,780,450,350],groups=['blue'])]
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        labels=[t.text for t in root.findall('.//s:text',NS)]
        self.assertIn('Blue',labels);self.assertIn('1',labels)
        data['insets'][0]['groups']=['blue','blue']
        with self.assertRaisesRegex(ValueError,'unique known'):EditorialPoster(data).render()

    def test_occupied_search_port_fails_with_the_neighbour(self):
        data=graph();poster=EditorialPoster(data)
        left=next(n for n in data['nodes'] if n['id']=='left');right=next(n for n in data['nodes'] if n['id']=='right')
        left_height=poster.node_content(left,left['width'])[2]
        right_height=poster.node_content(right,right['width'])[2]
        right.update(x=left['x'],y=left['y']-left_height/2-12-right_height/2)
        with self.assertRaisesRegex(ValueError,'crowded target port near right'):EditorialPoster(data).render()

    def test_cohorts_follow_family_units_and_preserve_all_records(self):
        data=graph();data.update(mode='genealogy',layout='cohorts',edges=[],unions=[])
        data['nodes']=[dict(id=f'p{i}',label=f'Person {i}',group='red',row=row,width=90,style='plain') for i,row in enumerate([0,0,1,1,1,1,1,2,2])]
        data['unions']=[dict(id='u0',partners=['p0','p1'],children=['p2','p4','p6']),dict(id='u1',partners=['p2','p3'],children=['p7']),dict(id='u2',partners=['p4','p5'],children=['p8'])]
        before=copy.deepcopy(data);svg,report=EditorialPoster(data).render()
        self.assertEqual(data,before);self.assertEqual(report['node_count'],9);self.assertEqual(report['edge_count'],5)
        nodes={n['id']:n for n in report['resolved_layout']['nodes']}
        self.assertEqual(nodes['p2']['y'],nodes['p3']['y'])
        self.assertLess(nodes['p2']['x'],nodes['p4']['x'])
        self.assertGreater(nodes['p7']['y'],nodes['p2']['y'])

    def test_cohorts_reject_backward_and_duplicate_unions(self):
        data=graph();data.update(mode='genealogy',layout='cohorts',edges=[],unions=[dict(id='u',partners=['left','right'],children=['root'])])
        for n in data['nodes']:n['row']=0 if n['id']=='root' else 1
        with self.assertRaisesRegex(ValueError,'later row'):EditorialPoster(data).render()
        data['unions'][0]['children']=[];data['unions']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate cohort union'):EditorialPoster(data).render()

    def test_cohorts_reject_row_overflow_instead_of_losing_people(self):
        data=graph();data.update(mode='genealogy',layout='cohorts',edges=[])
        for n in data['nodes']:n.update(row=0,width=650)
        with self.assertRaisesRegex(ValueError,'exceeds page width'):EditorialPoster(data).render()

    def test_node_anchored_annotation_is_placed_after_layout(self):
        data=graph();data['annotations']=[dict(node='left',dx=0,dy=-90,label='WESTERN BRANCH',kind='pill',width=180)]
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        text=next(t for t in root.findall('.//s:text',NS) if t.text=='WESTERN BRANCH')
        self.assertEqual(float(text.attrib['x']),320)

    def test_division_ports_keep_declared_semantics(self):
        data=timeline();data['periods'].append(dict(data['periods'][1],id='c',offset=210))
        data['transitions']=[dict(id='split-left',source='a',target='b',kind='division',style='ribbon',source_port=.3,ribbon_width=10),dict(id='split-right',source='a',target='c',kind='division',style='ribbon',source_port=.7,ribbon_width=10)]
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        self.assertEqual([p.attrib['data-kind'] for p in root.findall('.//s:path[@data-edge-id]',NS)],['division','division'])
        self.assertEqual(len(root.findall('.//s:path[@data-transition-fill]',NS)),2)

    def test_invalid_timeline_attachment_cannot_escape_the_period(self):
        for changes in [dict(source_port=1.2),dict(style='ribbon',ribbon_width=80)]:
            data=timeline();data['transitions'][0].update(changes)
            with self.assertRaises(ValueError):EditorialPoster(data).render()

    def test_event_has_an_independently_inspectable_date_anchor(self):
        data=timeline();data['events'][0].update(id='recorded-event',detail='An explanatory consequence.')
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        event=root.find('.//s:g[@data-event-id="recorded-event"]',NS)
        self.assertEqual(float(event.attrib['data-year']),1300)
        meta=json.loads(root.find('.//s:metadata[@id="chart-data"]',NS).text)
        top,bottom=meta['time_y'];self.assertAlmostEqual(float(event.attrib['data-origin-y']),top+.3*(bottom-top),places=2)
        self.assertIn('explanatory consequence',svg)

    def test_historical_map_is_self_contained_with_provenance(self):
        data=timeline();data['map_texture']='milner-1850'
        svg,_=EditorialPoster(data).render();root=ET.fromstring(svg)
        self.assertTrue(root.find('.//s:image[@data-artwork="historical-map"]',NS).attrib['href'].startswith('data:image/jpeg;base64,'))
        self.assertEqual(json.loads(root.find('.//s:metadata[@data-artwork-source="milner-1850.jpg"]',NS).text)['date'],1850)

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

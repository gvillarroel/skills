#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Exercise complete contextual prose, exact count marks and reserved routing."""

import copy
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright
from editorial_insets import inset_content
from editorial_poster import EditorialPoster
from audit_chart import AUDIT, check_source, capture_detail
from compose_context_insets import compose_context

NS={'s':'http://www.w3.org/2000/svg'}
ET.register_namespace('',NS['s'])


def brief():
    return dict(id='contextual-collections',title='A HISTORY OF PUBLIC COLLECTIONS',design='editorial',mode='lineage',layout='authored',
                width=1200,height=1100,font_size=18,source_note='Fictional institutions and illustrative emblems.',
                groups=[dict(id='craft',label='Workshop collections',color='#F7CD26'),dict(id='public',label='Public institutions',color='#77BDDD')],
                nodes=[dict(id='a',label='Cabinet of Instruments',group='craft',x=400,y=250,width=180),
                       dict(id='b',label='Public Library',group='public',x=400,y=850,width=180),
                       dict(id='c',label='Reading Society',group='public',x=750,y=850,width=180)],
                edges=[dict(id='a-b',source='a',target='b',kind='branch')],
                insets=[dict(id='opening-story',kind='story',box=[210,385,400,220],title='A collection becomes public',
                             text='The cabinet gives rise to the public library. The reading society remains a separate institution.',
                             source_nodes=['a','b','c'],icon='lens'),
                        dict(id='record-counts',kind='counts',box=[780,185,340,190],title='Institutions in this history',columns=2)])


class ContextualInsets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=brief();cls.svg,cls.layout=EditorialPoster(cls.source).render()
        cls.pw=sync_playwright().start();cls.browser=cls.pw.chromium.launch()
        cls.page=cls.browser.new_page(viewport={'width':1400,'height':1200})

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.pw.stop()

    def inspect(self, svg, source=None):
        self.page.set_content(svg)
        self.page.evaluate('document.fonts.ready')
        report=self.page.evaluate(AUDIT)
        check_source(report, source or self.source)
        return report

    def test_preserves_source_and_complete_visible_text(self):
        source=brief();before=copy.deepcopy(source)
        svg,_=EditorialPoster(source).render()
        self.assertEqual(source,before)
        report=self.inspect(svg)
        self.assertFalse(report['findings'])
        self.assertEqual(len(report['context_insets']),2)
        counts=next(item for item in report['context_insets'] if item['kind']=='counts')
        self.assertEqual([len(group['marks']) for group in counts['groups']],[1,2])
        frozen,summary=compose_context(source)
        self.assertEqual(source,before)
        self.assertEqual(frozen['nodes'],source['nodes'])
        self.assertEqual(frozen['insets'],source['insets'])
        self.assertTrue(all(edge['via'] for edge in frozen['edges']))
        replay,_=EditorialPoster(frozen).render()
        self.assertFalse(self.inspect(replay,frozen)['findings'])
        self.assertEqual(summary['node_count'],3)

    def test_routes_around_the_whole_story_footprint(self):
        report=self.inspect(self.svg)
        self.assertFalse(report['findings'])
        # The unimpeded source/target centers align at x=400, but the story
        # occupies that corridor. The real route must leave it and return.
        edge=next(edge for edge in report['edges'] if edge['id']=='a-b')
        self.assertIn('L',edge['d'])
        self.assertGreater(len(edge['d'].split()),10)

    def test_fits_height_without_shrinking_content(self):
        source=brief();source['insets'][0]['box'][3]=50
        before=copy.deepcopy(source)
        result,report=compose_context(source,fit=True)
        self.assertEqual(source,before)
        self.assertEqual(result['nodes'],source['nodes'])
        self.assertGreater(result['insets'][0]['box'][3],50)
        self.assertEqual({k:v for k,v in result['insets'][0].items() if k!='box'},
                         {k:v for k,v in source['insets'][0].items() if k!='box'})
        self.assertEqual(len(report['pocket_adjustments']),1)
        svg,_=EditorialPoster(result).render()
        self.assertFalse(self.inspect(svg,result)['findings'])

    def test_fits_printable_boundary_and_avoids_institution(self):
        source=brief();source['insets'][1]['box']=[880,110,340,190]
        result,report=compose_context(source,fit=True)
        box=result['insets'][1]['box']
        self.assertGreaterEqual(box[1],130)
        self.assertLessEqual(box[0]+box[2],1152)
        self.assertTrue(report['pocket_adjustments'])
        # Move a proposed story close enough to its root to overlap it.
        source=brief();source['insets'][0]['box'][1]=275
        result,_=compose_context(source,fit=True)
        self.assertEqual(result['nodes'],source['nodes'])
        svg,_=EditorialPoster(result).render()
        self.assertFalse(self.inspect(svg,result)['findings'])

    def test_rejects_an_impossible_pocket(self):
        source=brief();source['insets'][0]['box']=[48,130,1100,800]
        with self.assertRaisesRegex(ValueError,'No clear inset pocket'):compose_context(source,fit=True)

    def test_preserves_already_valid_pockets(self):
        source=brief();result,report=compose_context(source,fit=True)
        self.assertEqual(result['insets'],source['insets'])
        self.assertEqual(report['pocket_adjustments'],[])

    def test_browser_renders_an_exact_source_coordinate_detail(self):
        self.page.set_content(self.svg)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'detail.png'
            capture_detail(self.page,path,[180,360,470,280],[1200,1100])
            self.assertEqual(struct.unpack('>II',path.read_bytes()[16:24]),(470,280))
            self.assertEqual(self.page.locator('svg').first.get_attribute('viewBox'),'180 360 470 280')

    def test_browser_rejects_outside_or_invalid_detail(self):
        for box in ([1100,100,200,200],[0,0,0,20],[0,0,float('nan'),20]):
            with self.subTest(box=box),self.assertRaises(ValueError):
                capture_detail(self.page,Path('unused-detail.png'),box,[1200,1100])

    def test_count_marks_wrap_without_losing_records(self):
        source=brief()
        source['nodes'] += [dict(id=f'extra-{i}',label='Archive',group='public') for i in range(35)]
        item=copy.deepcopy(source['insets'][1]);item['box']=[100,100,340,250]
        content=inset_content(item,source)
        cell=next(cell for cell in content['cells'] if cell['group']=='public')
        self.assertEqual(cell['count'],37)
        self.assertGreater(cell['marker_rows'],1)

    def test_rejects_missing_source_bindings_and_invalid_columns(self):
        for change in ('unknown-node','duplicate-node','unknown-group','duplicate-group','invalid-columns','zero-art'):
            source=brief()
            if change=='unknown-node':source['insets'][0]['source_nodes']=['absent']
            if change=='duplicate-node':source['insets'][0]['source_nodes']=['a','a']
            if change=='unknown-group':source['insets'][1]['groups']=['absent']
            if change=='duplicate-group':source['insets'][1]['groups']=['craft','craft']
            if change=='invalid-columns':source['insets'][1]['columns']=0
            if change=='zero-art':source['insets'][0]['art_width']=0
            with self.subTest(change=change),self.assertRaises(ValueError):EditorialPoster(source).render()

    def test_rejects_undersized_prose_and_count_boxes(self):
        for index in (0,1):
            source=brief();source['insets'][index]['box'][3]=50
            with self.subTest(index=index),self.assertRaisesRegex(ValueError,'too short|at least'):EditorialPoster(source).render()

    def test_rejects_colliding_pockets_and_duplicate_ids(self):
        for change in ('node','inset','id'):
            source=brief()
            if change=='node':source['insets'][0]['box']=[210,185,400,220]
            if change=='inset':source['insets'][1]['box']=[230,400,340,220]
            if change=='id':source['insets'][1]['id']='opening-story'
            with self.subTest(change=change),self.assertRaises(ValueError):EditorialPoster(source).render()

    def test_browser_rejects_corrupted_counts_and_presentation(self):
        cases=[('delete','source-inset-count'),('hide','inset-hidden-content'),('paint','source-inset-group-color'),
               ('total','source-inset-count'),('overlap','inset-mark-overlap'),('font','source-inset-type')]
        for change,expected in cases:
            root=ET.fromstring(self.svg)
            group=root.find('.//s:g[@data-count-group="public"]',NS)
            marks=group.findall('s:path[@data-count-mark]',NS)
            if change=='delete':group.remove(marks[0])
            if change=='hide':marks[0].set('opacity','0')
            if change=='paint':marks[0].set('fill','#FF0000')
            if change=='total':group.find('s:text[@data-inset-role="count"]',NS).text='99'
            if change=='overlap':marks[1].set('d',marks[0].get('d'))
            if change=='font':group.find('s:text[@data-inset-role="count"]',NS).set('font-size','8')
            report=self.inspect(ET.tostring(root,encoding='unicode'))
            with self.subTest(change=change):self.assertIn(expected,[item['type'] for item in report['findings']])

    def test_browser_rejects_changed_prose_art_and_placement(self):
        for change,expected in [('text','source-inset-prose'),('art','source-inset-art'),('move','source-inset-position'),('path','inset-path-collision')]:
            root=ET.fromstring(self.svg)
            story=root.find('.//s:g[@data-inset-id="opening-story"]',NS)
            if change=='text':story.find('s:text[@data-inset-role="story"]',NS).text='Invented history'
            if change=='art':story.find('.//s:g[@data-artwork]',NS).set('data-artwork','prism')
            if change=='move':story.set('transform','translate(15 0)')
            if change=='path':root.find('.//s:path[@data-edge-id="a-b"]',NS).set('d','M400 280L400 820')
            report=self.inspect(ET.tostring(root,encoding='unicode'))
            with self.subTest(change=change):self.assertIn(expected,[item['type'] for item in report['findings']])


if __name__=='__main__':unittest.main()

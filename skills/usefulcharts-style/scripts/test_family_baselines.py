#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Check fact preservation and feasible local genealogy composition."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from editorial_poster import EditorialPoster
from space_family_branches import fit_baselines, space_branches


def family():
    return dict(id='family-baselines',title='A SYNTHETIC FAMILY',design='editorial',
        mode='genealogy',layout='cohorts',source_note='Synthetic test records.',
        groups=[dict(id='a',label='Alder',color='#F56550'),dict(id='b',label='Birch',color='#77BDDD')],
        nodes=[dict(id='p1',label='Anna',detail='1800–1874',birth=1800,death=1874,group='a',row=0),
               dict(id='p2',label='Ben',detail='1802–1877',birth=1802,death=1877,group='b',row=0),
               dict(id='c1',label='Clara',detail='1822–1890',birth=1822,death=1890,group='a',row=1),
               dict(id='c2',label='Daniel',detail='1840–1912',birth=1840,death=1912,group='b',row=1),
               dict(id='c3',label='Elin',detail='Dates unknown',group='a',row=1)],
        unions=[dict(id='u1',partners=['p1','p2'],children=['c1','c2','c3'])],edges=[])


def unit(row,left=0,right=40,height=20):
    return dict(row=row,height=height,parts=[dict(left=left,right=right,top=-height/2,bottom=height/2,kind='node')])


class BaselineTests(unittest.TestCase):
    def test_reserved_context_keeps_records_and_routes_around_caption(self):
        data=family();data['nodes'][2]['place']='Alder school'
        data['annotations']=[dict(kind='landmark',node='c1',field='place',width=160,size=20,icon='heraldry',art_size=32,art_position='beside')]
        before=copy.deepcopy(data);result,report=space_branches(data,reserve_context=True)
        self.assertEqual(data,before);self.assertEqual(report['reserved_context_count'],1)
        for source,node in zip(data['nodes'],result['nodes']):
            for key,value in source.items():self.assertEqual(node[key],value)
        self.assertEqual(result['unions'],data['unions']);self.assertEqual(result['edges'],data['edges'])
        poster=EditorialPoster(result);svg,render=poster.render()
        self.assertEqual(render['node_count'],5);self.assertEqual(render['edge_count'],3)
        self.assertIn('data-context-node="c1"',svg)

    def test_reserved_context_requires_a_measured_canvas(self):
        data=family();data['width']=1400
        with self.assertRaisesRegex(ValueError,'omit explicit page dimensions'):space_branches(data,reserve_context=True)

    def test_reserved_context_rejects_multiple_captions_on_one_person(self):
        data=family();data['nodes'][2]['place']='Alder school'
        a=dict(kind='landmark',node='c1',field='place')
        data['annotations']=[a,copy.deepcopy(a)]
        with self.assertRaisesRegex(ValueError,'multiple captions|one context'):space_branches(data,reserve_context=True)

    def test_two_unit_projection_matches_analytic_solution(self):
        positions,report=fit_baselines({'a':unit(0),'b':unit(1)},[('a','b')],{'a':50,'b':50},0,100)
        self.assertAlmostEqual(positions['a'],31,places=4);self.assertAlmostEqual(positions['b'],69,places=4)
        self.assertLess(report['max_violation'],.001)

    def test_all_facts_source_order_and_cross_family_membership_survive(self):
        data=family();data['nodes'].reverse();before=copy.deepcopy(data);result,report=space_branches(data,date_scale=2)
        self.assertEqual(data,before)
        self.assertEqual([n['id'] for n in result['nodes']],[n['id'] for n in data['nodes']])
        for original,node in zip(data['nodes'],result['nodes']):
            for key,value in original.items():self.assertEqual(node[key],value)
        self.assertEqual(result['unions'],data['unions']);self.assertEqual(result['edges'],data['edges'])
        by_id={n['id']:n for n in result['nodes']}
        self.assertEqual(by_id['p1']['y'],by_id['p2']['y']);self.assertLess(by_id['c1']['y'],by_id['c2']['y'])
        self.assertEqual(report['undated_units'],['person:c3']);self.assertNotIn('birth',by_id['c3'])
        svg,render=EditorialPoster(result).render()
        self.assertEqual(render['node_count'],5);self.assertEqual(render['edge_count'],3)
        self.assertIn('Dates unknown',svg);self.assertEqual(result['font_size'],18);self.assertIn('_cohort_key',result)

    def test_full_parental_height_reserves_lateral_departure(self):
        positions,_=fit_baselines({'a':unit(0,0,40,100),'b':unit(1,300,340,20)},[('a','b')],{'a':80,'b':100},0,300)
        self.assertGreaterEqual(positions['b']-positions['a'],78-.001)

    def test_component_geometry_keeps_unoccupied_portrait_side_usable(self):
        units={'a':dict(row=0,height=100,parts=[dict(left=0,right=40,top=-50,bottom=50,kind='node'),
            dict(left=100,right=140,top=-10,bottom=10,kind='node')]),'b':unit(1,100,140,20)}
        positions,_=fit_baselines(units,[],{'a':60,'b':100},0,200)
        self.assertAlmostEqual(positions['a'],60,places=4);self.assertAlmostEqual(positions['b'],100,places=4)

    def test_pill_moves_with_actual_person_and_keeps_label_and_color(self):
        data=family();data['annotations']=[dict(node='c1',dx=350,dy=0,width=130,size=12,label='ALDER OF THE HILL',kind='pill',group='a')]
        result,report=space_branches(data,local_labels=True);label=result['annotations'][0]
        self.assertEqual(label['node'],'c1');self.assertEqual(label['group'],'a')
        self.assertEqual(label['label'],data['annotations'][0]['label']);self.assertEqual(label['dx'],0)
        self.assertLess(label['dy'],-35);self.assertEqual(report['moved_label_indices'],[0])
        EditorialPoster(result).render()

    def test_undated_family_gets_no_invented_dates(self):
        data=family()
        for node in data['nodes']:node.pop('birth',None)
        result,report=space_branches(data)
        self.assertEqual(report['date_scale'],0);self.assertTrue(all('birth' not in node for node in result['nodes']))

    def test_medium_family_without_dimensions_gets_measured_readable_page(self):
        data=family();data['unions']=[];data['nodes']=[];data['edges']=[]
        for i in range(36):
            data['nodes'].append(dict(id=f'p{i}',label=f'Person {i}',detail=f'{1700+i*5}–{1760+i*5}',birth=1700+i*5,group='a',row=i//6))
            if i>=6:data['edges'].append(dict(id=f'e{i}',source=f'p{i-6}',target=f'p{i}',kind='descent'))
        result,_=space_branches(data)
        self.assertEqual(result['font_size'],18);self.assertLess(result['width']*result['height'],1800*2700)
        self.assertEqual(len(result['nodes']),36);self.assertIn('_cohort_key',result)
        by_id={n['id']:n for n in result['nodes']}
        self.assertEqual(by_id['p0']['style'],'hero');self.assertEqual(by_id['p12']['style'],'card')
        self.assertEqual(by_id['p35']['style'],'plain');self.assertEqual(by_id['p12']['detail_position'],'outside')
        self.assertEqual(by_id['p12']['size'],18);self.assertEqual(by_id['p12']['detail_size'],13)
        _,report=EditorialPoster(result).render();self.assertEqual(report['edge_count'],30)

    def test_medium_defaults_respect_explicit_typography_and_treatment(self):
        data=family();data['unions']=[]
        data['nodes']=[dict(id=f'n{i}',label=f'Name {i}',detail='1850–1915',birth=1850+i,
            group='a',row=i//5) for i in range(35)]
        data['nodes'][12].update(style='emblem',size=20,detail_size=14,width=190,emphasis=True)
        result,_=space_branches(data)
        node=next(n for n in result['nodes'] if n['id']=='n12')
        self.assertEqual((node['style'],node['size'],node['detail_size'],node['width']),('emblem',20,14,190))

    def test_numeric_date_contract_rejects_labels_booleans_and_nonfinite(self):
        for value in ['1800',True,float('nan'),float('inf')]:
            data=family();data['nodes'][0]['birth']=value
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'numeric finite'):space_branches(data)
        for scale in [-1,float('nan'),float('inf')]:
            with self.subTest(scale=scale),self.assertRaisesRegex(ValueError,'Date scale'):space_branches(family(),date_scale=scale)

    def test_infeasible_span_and_nonadvancing_relation_fail(self):
        with self.assertRaisesRegex(ValueError,'only 20.00'):
            fit_baselines({'a':unit(0),'b':unit(1)},[('a','b')],{'a':5,'b':10},0,20)
        with self.assertRaisesRegex(ValueError,'later generation'):
            fit_baselines({'a':unit(0),'b':unit(1)},[('b','a')],{'a':5,'b':10},0,100)

    def test_fixed_geometry_requires_deliberate_recomposition(self):
        for change,message in [({'insets':[dict(x=100,y=100)]},'fixed insets'),
            ({'annotations':[dict(x=100,y=100,label='Fixed')]},'person-anchored'),
            ({'edges':[dict(source='p1',target='c1',kind='descent',corridor_y=300)]},'absolute route')]:
            data=family();data.update(change)
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,message):space_branches(data)

    def test_multipartnership_and_misaligned_partners_fail(self):
        data=family();data['unions'].append(dict(id='second',partners=['p1','p2'],children=[]))
        with self.assertRaisesRegex(ValueError,'Multiple partnerships'):space_branches(data)
        data=family();data['nodes'][1]['row_offset']=10
        with self.assertRaisesRegex(ValueError,'same row_offset'):space_branches(data)

    def test_cli_exact_paths_and_failed_inputs_do_not_overwrite_source(self):
        with tempfile.TemporaryDirectory(prefix='.family-test-',dir=Path.cwd()) as directory:
            root=Path(directory);source=root/'input.json';source.write_text(json.dumps(family()),encoding='utf-8')
            original=source.read_bytes();script=Path(__file__).with_name('space_family_branches.py')
            output=root/'nested/resolved.json';report=root/'audit/spacing.json'
            result=subprocess.run([sys.executable,str(script),str(source),'--output',str(output),'--report',str(report)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr);self.assertEqual(json.loads(report.read_text())['status'],'pass')
            self.assertEqual(json.loads(output.read_text())['layout'],'authored')
            failed=subprocess.run([sys.executable,str(script),str(source),'--output',str(source)],capture_output=True,text=True)
            self.assertEqual(failed.returncode,1);self.assertEqual(source.read_bytes(),original)
            invalid=family();invalid['nodes'][0]['birth']='unknown';source.write_text(json.dumps(invalid),encoding='utf-8')
            missing=root/'should-not-exist.json'
            failed=subprocess.run([sys.executable,str(script),str(source),'--output',str(missing)],capture_output=True,text=True)
            self.assertEqual(failed.returncode,1);self.assertFalse(missing.exists())


if __name__=='__main__':unittest.main()

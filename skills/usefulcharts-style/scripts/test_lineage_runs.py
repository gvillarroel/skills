#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Protect independent institutional branches from ambiguous shared strokes."""

import copy
import unittest

from editorial_poster import EditorialPoster
from render_chart import collinear_overlap, route


def crossed_brief():
    return dict(id='separate-institutions',title='INDEPENDENT INSTITUTIONAL BRANCHES',
        design='editorial',mode='lineage',width=1400,height=1000,source_note='Synthetic test records.',
        groups=[dict(id='g',label='Institutions',color='#F56550')],
        nodes=[dict(id=nid,label=nid.upper(),group='g',width=100,x=x,y=y)
               for nid,x,y in [('a',200,250),('b',850,600),('c',500,250),('d',1100,600)]],
        edges=[dict(id='first',source='a',target='b',kind='branch'),dict(id='second',source='c',target='d',kind='branch')])


class SeparateRunsTests(unittest.TestCase):
    def test_collinear_runs_are_distinct_from_crossings_and_touching(self):
        self.assertEqual(collinear_overlap((0,0),(100,0),(25,0),(75,0)),50)
        self.assertEqual(collinear_overlap((0,0),(0,100),(0,75),(0,25)),50)
        self.assertEqual(collinear_overlap((0,0),(100,0),(50,-20),(50,20)),0)
        self.assertEqual(collinear_overlap((0,0),(50,0),(50,0),(100,0)),0)
        self.assertEqual(collinear_overlap((0,0),(100,0),(25,8),(75,8)),0)

    def test_reserved_route_finds_a_parallel_clear_run(self):
        reserved=[((250,300),(550,300))]
        path=route((200,200),(600,400),[],(0,0,800,600),reserved,reserved=reserved)
        self.assertEqual((path[0],path[-1]),((200,200),(600,400)))
        self.assertFalse(any(collinear_overlap(a,b,c,d)>.05 for a,b in zip(path,path[1:]) for c,d in reserved))

    def test_almost_coincident_painted_runs_keep_a_visible_gutter(self):
        for offset in (.022173913, 1.5, 3.9):
            reserved=[((250,300+offset),(550,300+offset))]
            path=route((200,200),(600,400),[],(0,0,800,600),reserved,reserved=reserved)
            self.assertFalse(any(collinear_overlap(a,b,c,d,tolerance=4)>.05
                                 for a,b in zip(path,path[1:]) for c,d in reserved))

    def test_unrelated_automatic_paths_do_not_share_a_trunk(self):
        data=crossed_brief();original=copy.deepcopy(data);poster=EditorialPoster(data);poster.render()
        first,second=poster.routes
        self.assertFalse(any(collinear_overlap(a,b,c,d)>.05 for a,b in zip(first['points'],first['points'][1:])
            for c,d in zip(second['points'],second['points'][1:])))
        self.assertEqual(data,original)

    def test_explicit_corridor_is_preserved_for_external_review(self):
        data=crossed_brief()
        data['edges'][1]['via']=[[500,430],[1100,430]]
        poster=EditorialPoster(data);poster.render()
        self.assertEqual(poster.routes[1]['points'][1:-1],[(500.,430.),(1100.,430.)])

    def test_siblings_may_share_their_actual_origin(self):
        data=crossed_brief();data['nodes']=[n for n in data['nodes'] if n['id']!='c']
        data['edges'][1]['source']='a';poster=EditorialPoster(data);poster.render()
        self.assertEqual(poster.routes[0]['points'][0],poster.routes[1]['points'][0])


if __name__=='__main__':unittest.main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Portable contrast, native-gutter, marker-identity and geometry regressions."""
import math
import unittest
import xml.etree.ElementTree as ET
from arrow_contrast import contrast, safe_paint, path_points, contains, finish_native_arrows, property_value

def document(body,family='flowchart-v2'):
    return ET.fromstring(f'<svg aria-roledescription="{family}">{body}</svg>')

def marker():
    return '<defs><marker id="head" viewBox="0 0 10 10" markerWidth="5" markerHeight="5" refX="10" refY="5" orient="auto"><polygon points="0,0 10,5 0,10" fill="#9e1b32"/></marker></defs>'

class ArrowTests(unittest.TestCase):
    def test_allowed_hue_is_preserved(self):
        self.assertEqual(safe_paint('#9e1b32',['#ffffff'],'colorset1'),'#9e1b32')

    def test_all_crossed_backings_contrast(self):
        paint=safe_paint('#696969',['#ffffff','#294d19'],'colorset2')
        self.assertGreaterEqual(min(contrast(paint,b) for b in ['#ffffff','#294d19']),3)

    def test_incompatible_regions_require_routing(self):
        with self.assertRaises(ValueError):safe_paint('#696969',['#000000','#ffffff','#828282'],'colorset1')

    def test_arc_is_not_a_straight_chord(self):
        points=path_points(ET.fromstring('<path d="M0 0 A10 10 0 0 1 20 0"/>'))
        self.assertAlmostEqual(points[-1][0],20)
        self.assertGreater(max(abs(y) for _,y in points),9.9)
        for x,y in points:self.assertAlmostEqual(math.hypot(x-10,y),10,places=8)

    def test_polygon_uses_contour(self):
        triangle=ET.fromstring('<polygon points="0,0 20,0 0,20"/>')
        self.assertTrue(contains(triangle,(2,2)))
        self.assertFalse(contains(triangle,(18,18)))

    def test_marker_clearance_scales_with_viewbox_and_stroke(self):
        root=document(marker()+'<path id="edge" d="M0 0L100 0" stroke="#9e1b32" stroke-width="2" fill="none" marker-end="url(#head)"/>')
        finish_native_arrows(root,'colorset1')
        clone=next(e for e in root.iter() if e.get('data-arrow-owner'))
        self.assertGreaterEqual(float(clone.get('refX')),13)
        self.assertEqual(clone.get('orient'),'auto')

    def test_animated_alias_matches_static_marker(self):
        root=document(marker()+'<path d="M0 0L100 0" fill="none" stroke="#9e1b32" marker-end="url(#head)" style="--am-marker-end:url(#head);--am-delay:100ms"/>')
        finish_native_arrows(root,'colorset1');edge=list(root)[1]
        self.assertEqual(property_value(edge,'--am-marker-end'),edge.get('marker-end'))
        self.assertIn('--am-delay:100ms',edge.get('style'))
        before=ET.tostring(root);finish_native_arrows(root,'colorset1')
        self.assertEqual(before,ET.tostring(root))

    def test_hollow_cardinality_retains_white_void_and_visible_rim(self):
        root=document('<defs><marker id="head" orient="auto"><circle fill="white" cx="8" cy="8" r="4"/></marker></defs><path d="M0 0L100 0" fill="none" stroke="#9e1b32" marker-end="url(#head)"/>')
        finish_native_arrows(root,'colorset1')
        child=next(e for e in root.iter() if e.get('data-arrow-owner'))[0]
        self.assertEqual(property_value(child,'fill'),'#ffffff')
        self.assertEqual(property_value(child,'stroke'),'#9e1b32')

    def test_c4_bypass_routes_around_intermediate_body(self):
        body=''.join(f'<g class="person-man"><rect x="50" y="{y}" width="100" height="40" fill="#9e1b32"/></g>' for y in [0,100,200])
        root=document(marker()+body+'<path d="M100 40L100 200" stroke="#696969" fill="none" marker-end="url(#head)"/>','c4')
        finish_native_arrows(root,'colorset1');edge=list(root)[-1]
        self.assertEqual(edge.get('data-arrow-gutter'),'true')
        self.assertFalse(any(contains(list(root)[2][0],p) for p in path_points(edge)))

    def test_event_card_approach_is_perpendicular(self):
        root=document(marker()+'<rect x="100" y="100" width="100" height="60" fill="#828282" style="stroke:none"/><path class="em-relation" d="M0 60L150 100" fill="none" stroke="#696969" marker-end="url(#head)"/>','eventmodeling')
        finish_native_arrows(root,'colorset1');edge=list(root)[-1];pts=path_points(edge)
        self.assertAlmostEqual(pts[-1][0],pts[-2][0]);self.assertEqual(pts[-1][1],97)

    def test_filled_head_has_no_added_outline(self):
        root=document('<path class="arrow" d="M0 0L10 5L0 10Z" fill="#9e1b32"/>')
        finish_native_arrows(root,'colorset1')
        self.assertEqual(property_value(root[0],'stroke'),'none')

    def test_native_filled_nodes_are_unchanged(self):
        node='<rect x="100" y="20" width="80" height="40" fill="#9e1b32" style="stroke:none"/>'
        root=document(marker()+node+'<path d="M0 0L100 0" stroke="#cfcfcf" fill="none" marker-end="url(#head)"/>')
        before=ET.tostring(root[1]);finish_native_arrows(root,'colorset1')
        self.assertEqual(before,ET.tostring(root[1]))

    def test_narrow_er_gutter_requires_rerender(self):
        root=document('<defs><marker id="one" refX="0"><path d="M9 0L9 18M15 0L15 18"/></marker><marker id="many" refX="27"><circle cx="9" cy="18" r="6"/><path d="M21 18Q39 0 57 18Q39 36 21 18"/></marker></defs><path d="M0 0L0 70" fill="none" stroke="#696969" marker-start="url(#one)" marker-end="url(#many)"/>','er')
        with self.assertRaisesRegex(ValueError,'rankSpacing'):finish_native_arrows(root,'colorset1')

    def test_plantuml_compound_region_arrow_uses_actual_polygon(self):
        root=document('<polygon points="0,0 100,0 100,70 0,70" fill="#294d19"/><g class="link"><path d="M50 50L50 120" stroke="#696969" fill="none"/><polygon points="47,114 50,120 53,114" fill="#696969"/></g>')
        finish_native_arrows(root,'colorset2','plantuml')
        shaft=root[1][0];paint=property_value(shaft,'stroke')
        self.assertGreaterEqual(contrast(paint,'#294d19'),3)
        self.assertGreaterEqual(contrast(paint,'#ffffff'),3)
        self.assertGreaterEqual(contrast(property_value(root[1][1],'fill'),'#ffffff'),3)

if __name__=='__main__':unittest.main()

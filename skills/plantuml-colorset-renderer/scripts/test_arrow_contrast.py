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

    def test_plantuml_json_port_and_ungrouped_shaft(self):
        root = document('<rect x="0" y="0" width="40" height="40" fill="#007298"/><path d="M20 20 L70 20" fill="none" stroke="#696969"/><path d="M70 17 L77 20 L70 23Z" fill="#696969"/><ellipse cx="20" cy="20" rx="3" ry="3" fill="#696969" stroke="#696969"/>')
        root.set('data-diagram-type', 'JSON')
        finish_native_arrows(root, 'colorset2', 'plantuml')
        for edge in (root[1], root[3]):
            paint = property_value(edge, 'stroke')
            self.assertGreaterEqual(contrast(paint, '#007298'), 3)
        self.assertGreaterEqual(contrast(property_value(root[1], 'stroke'), '#ffffff'), 3)
        self.assertEqual(root[0].get('fill'), '#007298')

    def test_plantuml_sequence_message_and_railroad_head(self):
        root = document('<g class="message"><line x1="0" y1="20" x2="70" y2="20" stroke="#cfcfcf"/><polygon points="70,17 77,20 70,23" fill="#cfcfcf"/></g>')
        finish_native_arrows(root, 'colorset1', 'plantuml')
        for edge in root[0]:
            self.assertGreaterEqual(contrast(property_value(edge, 'stroke'), '#ffffff'), 3)
        rails = document('<path d="M0 10 L30 10" fill="none" stroke="#cfcfcf"/><path d="M30 7 L37 10 L30 13Z" fill="#cfcfcf"/>')
        rails.set('data-diagram-type', 'REGEX')
        finish_native_arrows(rails, 'colorset1', 'plantuml')
        self.assertGreaterEqual(contrast(property_value(rails[1], 'fill'), '#ffffff'), 3)

    def test_plantuml_hollow_native_diamond_retains_void(self):
        root = document('<g class="link"><polygon points="0,5 5,0 10,5 5,10" fill="#ffffff" stroke="#696969"/></g>')
        finish_native_arrows(root, 'colorset1', 'plantuml')
        self.assertEqual(property_value(root[0][0], 'fill'), '#ffffff')

    def test_plantuml_grouped_shaft_contact_moves_out_of_body(self):
        root = document('<polygon points="40,20 80,20 80,60 40,60" fill="#333e48"/><g class="link"><path d="M40,30 L0,30" fill="none" stroke="#696969"/></g>')
        finish_native_arrows(root, 'colorset1', 'plantuml')
        shaft = root[1][0]
        self.assertLess(path_points(shaft)[0][0], 37)
        self.assertEqual(shaft.get('data-arrow-clearance'), 'native-body-gutter-3px')
        self.assertEqual(root[0].get('points'), '40,20 80,20 80,60 40,60')

    def test_complete_head_stroke_has_gutter_when_tip_starts_outside(self):
        root = document('<rect x="70" y="0" width="40" height="40" fill="#007298"/><g class="link"><path d="M20 20L60 20" fill="none" stroke="#696969"/><polygon points="60,16 69.65,20 60,24" fill="#696969" style="stroke-width:1.5"/></g>')
        finish_native_arrows(root, 'colorset2', 'plantuml')
        head = root[1][1]
        self.assertLessEqual(max(x for x,y in path_points(head))+.75, 67)
        self.assertEqual(head.get('data-arrow-clearance'), 'native-tip-gutter-3px')

    def test_native_shaft_shallow_inset_clears_complete_stroke(self):
        root = document('<rect x="20" y="40" width="60" height="52.1972" fill="#333e48"/><g class="link"><path d="M50,92.1086 L50,140" fill="none" stroke="#696969" style="stroke-width:1.5"/></g>')
        before = ET.tostring(root[0])
        finish_native_arrows(root, 'colorset1', 'plantuml')
        shaft = root[1][0]
        self.assertGreaterEqual(path_points(shaft)[0][1]-.75, 95.1972)
        self.assertEqual(shaft.get('data-arrow-clearance'), 'native-body-gutter-3px')
        self.assertEqual(ET.tostring(root[0]), before)

    def test_mindmap_branch_rounding_contact_clears_body(self):
        root = document('<rect x="190.2754" y="0" width="73.4893" height="40" fill="#9e1b32"/><path d="M263.7646,20 L310,20" fill="none" stroke="#696969"/>')
        root.set('data-diagram-type', 'MINDMAP')
        finish_native_arrows(root, 'colorset1', 'plantuml')
        self.assertGreater(path_points(root[1])[0][0]-.5, 266.7647)
        self.assertEqual(root[1].get('data-arrow-clearance'), 'native-body-gutter-3px')

    def test_activity_source_and_hollow_stop_receive_full_gutter(self):
        root = document('<rect x="30" y="30" width="60" height="40" fill="#4f4f4f"/><ellipse cx="60" cy="101" rx="11" ry="11" fill="none" stroke="#e8002a" stroke-width="1.5"/><line x1="60" y1="70" x2="60" y2="90" fill="none" stroke="#696969" stroke-width="1.5"/><polygon points="56,80 60,90 64,80 60,84" fill="#696969" stroke-width="1"/>')
        root.set('data-diagram-type', 'ACTIVITY')
        ring = ET.tostring(root[1])
        finish_native_arrows(root, 'colorset1', 'plantuml')
        shaft, head = root[2], root[3]
        self.assertGreaterEqual(path_points(shaft)[0][1]-.75, 73)
        self.assertLessEqual(path_points(shaft)[-1][1]+.75, 87)
        self.assertLessEqual(max(y for x,y in path_points(head))+.5, 87)
        self.assertEqual(ET.tostring(root[1]), ring)

    def test_short_wbs_stem_clears_later_painted_child(self):
        root = document('<line x1="20" y1="20" x2="30" y2="20" stroke="#696969" stroke-width="1.5"/><rect x="30" y="0" width="40" height="40" fill="#9e1b32"/>')
        root.set('data-diagram-type', 'WBS')
        finish_native_arrows(root, 'colorset2', 'plantuml')
        self.assertLessEqual(path_points(root[0])[-1][0]+.75, 27)
        self.assertGreater(path_points(root[0])[-1][0], 20)
        self.assertEqual(root[0].get('data-arrow-clearance'), 'native-body-gutter-3px')

if __name__=='__main__':unittest.main()

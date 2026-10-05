#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0", "resvg-py>=0.5,<0.6"]
# ///
"""Regression tests for actual native paint, semantic geometry, and theme refresh."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from native_styles import finish_native_styles, style_findings, source_has_style, STYLE_RULES
from arrow_contrast import property_value
from render_plantuml_directory import inject_theme
from palette_paints import solid_colors, solid_style, readable_text


def svg(content, family="DESCRIPTION"):
    return ET.fromstring(f'<svg data-diagram-type="{family}">{content}</svg>')


def label(text="Label", fill="#ffffff", x=15, y=25):
    return f'<text x="{x}" y="{y}" textLength="30" font-size="14" fill="{fill}">{text}</text>'


class NativeStyleTests(unittest.TestCase):
    def test_exact_cs1_interleaved_capacity_and_canvas_exclusion(self):
        expected = ['#9e1b32', '#000000', '#828282', '#1c1c1c', '#9c9c9c',
                    '#363636', '#b5b5b5', '#333e48', '#cfcfcf', '#4f4f4f',
                    '#e7e7e7', '#696969', '#f7f7f7', '#ffffff', '#6d1222',
                    '#e8002a', '#ffccd5']
        for canvas in ['#ffffff', '#f7f7f7', '#000000', '#9e1b32']:
            usable = [paint for paint in expected if paint != canvas]
            self.assertEqual(solid_colors('colorset1', canvas), usable)
            for index, fill in enumerate(usable):
                style = solid_style(index, 'colorset1', canvas)
                self.assertEqual(style['fill'], fill)
                self.assertEqual(style['text'], readable_text(fill))
                self.assertEqual(style['strokeWidth'], 0)
                self.assertFalse(style['overflow'])
            self.assertTrue(solid_style(len(usable), 'colorset1', canvas)['overflow'])

    def test_external_participant_label_and_internal_curve(self):
        root = svg('<g class="participant">'+label(y=20)+'<path d="M10 35 L60 35 L60 70 L10 70 Z" fill="#431f47"/><path d="M10 40 Q35 55 60 40" fill="none"/></g>', "SEQUENCE")
        finish_native_styles(root, "colorset2")
        self.assertEqual(root.find(".//text").get("fill"), "#000000")
        self.assertEqual(property_value(root.findall(".//path")[1], "stroke"), "#ffffff")

    def test_native_category_pools_exclude_actual_canvas_and_keep_semantic_roles(self):
        native = ['#c9ffc9', '#c2f0ff', '#ffffcc', '#ccccff', '#f8e7c0', '#97ff97', '#ffe0e0']
        roles = ['technology', 'application', 'business', 'motivation', 'strategy', 'physical', 'implementation']
        ranked = ['business', 'application', 'technology', 'motivation', 'strategy', 'physical', 'implementation']
        literal = ['#9e1b32', '#000000', '#828282', '#1c1c1c', '#9c9c9c',
                   '#363636', '#b5b5b5', '#333e48', '#cfcfcf', '#4f4f4f',
                   '#e7e7e7', '#696969', '#f7f7f7', '#ffffff', '#6d1222',
                   '#e8002a', '#ffccd5']
        for canvas in ['#ffffff', '#f7f7f7', '#000000', '#9e1b32']:
            root = svg(''.join(f'<rect fill="{paint}"/>' for paint in native))
            root.set('style', f'background:{canvas}')
            geometry = [dict(node.attrib) for node in root]
            finish_native_styles(root, 'colorset1')
            expected = dict(zip(ranked, [fill for fill in literal if fill != canvas]))
            self.assertEqual([node.get('fill') for node in root], [expected[role] for role in roles])
            self.assertTrue(all(node.get('data-native-layer') == role for node, role in zip(root, roles)))
            self.assertEqual([set(node.attrib) - set(old) for node, old in zip(root, geometry)],
                             [{'style', 'data-style-role', 'data-native-layer'}] * 7)
        self.assertEqual(STYLE_RULES['colorsets']['colorset1']['archimate'],
                         {'technology': '#4f4f4f', 'application': '#333e48', 'business': '#9e1b32',
                          'motivation': '#696969', 'strategy': '#828282', 'physical': '#9c9c9c',
                          'implementation': '#b5b5b5'})

    def test_label_uses_actual_nested_backing(self):
        root = svg('<rect x="0" y="0" width="100" height="100" fill="#333e48"/><rect x="10" y="10" width="60" height="40" fill="#f1c319"/>'+label())
        finish_native_styles(root, "colorset2")
        self.assertEqual(root.find("text").get("fill"), "#000000")
        self.assertEqual(style_findings(root), [])
        root.find("text").set("fill", "#ffffff")
        self.assertIn("label must use the higher-contrast black or white", style_findings(root))

    def test_transparent_lifeline_is_not_text_backing(self):
        root = svg('<rect x="0" y="0" width="100" height="100" fill="#000000" fill-opacity="0"/>'+label())
        finish_native_styles(root, "colorset2")
        self.assertEqual(root.find("text").get("fill"), "#000000")

    def test_component_icon_and_compartment_survive(self):
        root = svg('<g class="entity"><rect x="0" y="0" width="100" height="100" fill="#004d66"/><rect x="70" y="8" width="15" height="10" fill="#004d66"/><line x1="0" y1="40" x2="100" y2="40"/></g>')
        finish_native_styles(root, "colorset2")
        self.assertEqual(property_value(root.findall(".//rect")[1], "stroke"), "#ffffff")
        self.assertEqual(property_value(root.find(".//line"), "stroke"), "#ffffff")
        self.assertEqual(property_value(root.find(".//rect"), "stroke", "none"), "none")

    def test_railroad_bodies_borderless_but_reference_and_rails_retained(self):
        root = svg('<rect x="10" y="10" width="50" height="25" fill="#9e1b32" style="stroke:#696969;stroke-width:1.5"/><rect x="80" y="10" width="50" height="25" fill="none" style="stroke:#696969;stroke-width:1;stroke-dasharray:5,5"/><path d="M60 22 L80 22" fill="none" stroke="#696969"/>'+label(), "EBNF")
        finish_native_styles(root, "colorset1")
        self.assertEqual(property_value(root.find("rect"), "stroke"), "none")
        self.assertEqual(property_value(root.findall("rect")[1], "stroke-dasharray"), "5,5")
        self.assertEqual(root.find("path").get("stroke"), "#696969")
        root.find("rect").set("style", "stroke:#000000;stroke-width:2")
        self.assertIn("solid body has a decorative outline", style_findings(root))

    def test_salt_native_button_and_archimate_layers(self):
        root = svg('<rect x="0" y="0" width="70" height="35" fill="#eeeeee" style="stroke:#000000;stroke-width:2.5"/>'+label(), "SALT")
        finish_native_styles(root, "colorset1")
        self.assertEqual(root.find("rect").get("fill"), "#9e1b32")
        self.assertEqual(root.find("text").get("fill"), "#ffffff")
        layers = svg('<rect fill="#c9ffc9"/><rect fill="#c2f0ff"/><rect fill="#ffffcc"/>')
        finish_native_styles(layers, "colorset2")
        self.assertEqual([node.get("fill") for node in layers], ["#45842a", "#007298", "#e77204"])

    def test_explicit_source_border_and_font_are_preserved(self):
        root = svg('<rect x="0" y="0" width="70" height="35" fill="#9e1b32" style="stroke:#000000;stroke-width:3"/>'+label(fill="#000000"), "EBNF")
        finish_native_styles(root, "colorset1", "skinparam DefaultFontColor #000000\n<style>\nroot { LineThickness 3 }\n</style>")
        self.assertEqual(property_value(root.find("rect"), "stroke-width"), "3")
        self.assertEqual(root.find("text").get("fill"), "#000000")

    def test_theme_switch_replaces_owned_block_and_preserves_overrides(self):
        source = "@startuml\nskinparam Padding 18\nA --> B\n@enduml\n"
        first = inject_theme(source, "skinparam ArrowColor #333e48")
        second = inject_theme(first, "skinparam ArrowColor #007298")
        self.assertNotIn("ArrowColor #333e48", second)
        self.assertEqual(second.count("theme-begin"), 1)
        self.assertIn("skinparam Padding 18", second)
        legacy = "@startuml\n' plantuml-colorset-renderer: cs1 custom theme\nskinparam Padding 6\n<style>\nroot {}\n</style>\nskinparam Padding 18\n@enduml\n"
        self.assertNotIn("Padding 6", inject_theme(legacy, "root {}"))
        self.assertIn("Padding 18", inject_theme(legacy, "root {}"))

    def test_grammar_canvas_differs_from_solid_tokens(self):
        root = svg('<rect x="10" y="10" width="70" height="30" fill="#e77204" stroke="#696969"/>'+label(fill='#000000'), "EBNF")
        root.set('style', 'background:#e77204')
        finish_native_styles(root, 'colorset2')
        self.assertEqual(property_value(root, 'background'), '#ffffff')
        self.assertEqual(root.find('rect').get('fill'), '#e77204')

    def test_explicit_canvas_backs_exterior_labels(self):
        root = svg(label(fill='#000000'))
        root.set('style', 'background:#333e48')
        finish_native_styles(root, 'colorset1', 'skinparam backgroundColor #333e48')
        self.assertEqual(root.find('text').get('fill'), '#ffffff')
        self.assertEqual(style_findings(root), [])

    def test_fact_colors_and_layout_settings_do_not_disable_native_defaults(self):
        for source in ["' revision #abcdef", 'title Color Sprite #abcdef', 'title Colored shapes', 'caption Colored [#abcdef] legend', 'rectangle "FontColor #abcdef" as A', 'A --> B : revision #abcdef', "skinparam Padding 18", "<style>root { Padding 18 }</style>", "/' color #abcdef '/"]:
            self.assertFalse(source_has_style(source), source)
        for source in ['skinparam rectangleBorderThickness 3', 'skinparam rectangle { BorderColor #007298 }', '<style>root { LineThickness 3 }</style>', 'rectangle "Card" as A #9e1b32', 'A -[#007298]-> B']:
            self.assertTrue(source_has_style(source), source)
        root = svg('<rect fill="#c9ffc9" stroke="#696969" stroke-width=".5"/>')
        finish_native_styles(root, 'colorset2', "' revision #abcdef\nskinparam Padding 18")
        self.assertEqual(root.find('rect').get('fill'), '#45842a')
        self.assertEqual(property_value(root.find('rect'), 'stroke'), 'none')

    def test_grammar_full_canvas_rect_is_separate_from_tokens(self):
        root = svg('<rect x="0" y="0" width="100" height="80" fill="#e77204"/><rect x="10" y="10" width="50" height="30" fill="#e77204"/>'+label(fill='#000000'), 'EBNF')
        root.set('viewBox', '0 0 100 80')
        finish_native_styles(root, 'colorset2')
        self.assertEqual(root[0].get('fill'), '#ffffff')
        self.assertEqual(root[0].get('data-style-role'), 'canvas')
        self.assertEqual(root[1].get('fill'), '#e77204')
        self.assertEqual(style_findings(root), [])

    def test_comment_property_names_do_not_override_canvas_or_labels(self):
        root = svg('<rect x="10" y="10" width="70" height="30" fill="#9e1b32"/>'+label(fill='#000000'), 'EBNF')
        root.set('style', 'background:#9e1b32')
        finish_native_styles(root, 'colorset1', "' backgroundColor #9e1b32 FontColor #000000")
        self.assertEqual(property_value(root, 'background'), '#ffffff')
        self.assertEqual(root.find('text').get('fill'), '#ffffff')

    def test_all_seven_archimate_layers_have_distinct_borderless_solids(self):
        native = ['#c9ffc9', '#c2f0ff', '#ffffcc', '#ccccff', '#f8e7c0', '#97ff97', '#ffe0e0']
        for colorset in ['colorset1', 'colorset2']:
            root = svg(''.join(f'<rect fill="{paint}" stroke="#696969" stroke-width=".5"/>' for paint in native))
            finish_native_styles(root, colorset)
            expected = (['#828282', '#000000', '#9e1b32', '#1c1c1c', '#9c9c9c', '#363636', '#b5b5b5']
                        if colorset == 'colorset1' else ['#45842a', '#007298', '#e77204', '#652f6c', '#f1c319', '#00ace6', '#e8002a'])
            self.assertEqual([node.get('fill') for node in root], expected)
            self.assertEqual(len({node.get('fill') for node in root}), 7)
            self.assertTrue(all(property_value(node, 'stroke') == 'none' for node in root))
            self.assertEqual(style_findings(root), [])

    def test_cs1_archimate_compresses_absent_layers_before_other_colors(self):
        for native, expected in [
            (['#c9ffc9'], ['#9e1b32']),
            (['#c2f0ff'], ['#9e1b32']),
            (['#ccccff', '#97ff97'], ['#9e1b32', '#000000']),
            (['#c9ffc9', '#c2f0ff'], ['#000000', '#9e1b32']),
        ]:
            root = svg(''.join(f'<rect fill="{paint}"/>' for paint in native))
            report = finish_native_styles(root, 'colorset1')
            self.assertEqual([node.get('fill') for node in root], expected)
            self.assertEqual(set(report['archimateLayers'].values()), set(expected))
            self.assertTrue(all(node.get('data-native-layer') for node in root))
        root = svg('<rect fill="#4f4f4f"/>')
        finish_native_styles(root, 'colorset1', 'rectangle "Explicit category" #4f4f4f')
        self.assertEqual(root[0].get('fill'), '#4f4f4f')
        self.assertIsNone(root.get('data-native-layer-map'))

    def test_cs1_default_family_bodies_start_with_primary_red(self):
        theme = (Path(__file__).resolve().parent.parent/'assets/themes/cs1.puml').read_text(encoding='utf-8')
        for family in ['SequenceParticipant', 'Usecase', 'Class', 'Object', 'Activity', 'Component', 'Node', 'State']:
            self.assertIn(f'skinparam {family}BackgroundColor #9e1b32\n', theme)
        self.assertNotIn('#6d1222', theme)
        self.assertNotIn('#e8002a', theme)
        self.assertIn('skinparam ActivityDiamondBackgroundColor #333e48\n', theme)
        self.assertIn('skinparam DatabaseBackgroundColor #333e48\n', theme)

    def test_timing_terminal_label_surface_preserves_native_event_geometry(self):
        trace = '<line x1="10" y1="20" x2="60" y2="20" stroke="#9e1b32"/>'
        state = '<polygon points="60,40 90,40 90,65 60,65 50,52" fill="#9e1b32"/>'
        root = svg(trace+state+label('Terminal', '#ffffff', x=65, y=57), 'TIMING')
        root.set('viewBox', '0 0 120 80')
        native_geometry = [ET.tostring(root[0]), ET.tostring(root[1])]
        report = finish_native_styles(root, 'colorset1')
        self.assertEqual([ET.tostring(root[0]), ET.tostring(root[1])], native_geometry)
        self.assertEqual(report['labelSurfaceCount'], 1)
        self.assertEqual(root.find('text').get('x'), '65')
        self.assertEqual(root.find('text').get('y'), '57')
        self.assertEqual(root.find('text').get('fill'), '#ffffff')
        surface = root.find('rect')
        self.assertEqual(surface.get('data-style-role'), 'label-surface')
        self.assertEqual(surface.get('fill'), '#9e1b32')
        self.assertEqual(style_findings(root), [])
        surface.set('stroke', '#000000')
        surface.set('stroke-width', '2')
        self.assertIn('solid body has a decorative outline', style_findings(root))

    def test_timing_label_padding_changes_only_outer_display_frame(self):
        root = svg('<line x1="90" y1="20" x2="90" y2="70" stroke="#696969" stroke-width="1"/>'
                   '<line x1="10" y1="20" x2="90" y2="20" stroke="#696969" stroke-width="1"/>'
                   '<line x1="50" y1="75" x2="90" y2="75" stroke="#696969" stroke-width="1.5"/>'
                   '<polygon points="60,40 90,40 90,65 60,65 50,52" fill="#9e1b32"/>'
                   +label('Terminal', '#ffffff', x=65, y=57), 'TIMING')
        root.set('viewBox', '0 0 120 80')
        axis, state = ET.tostring(root[2]), ET.tostring(root[3])
        finish_native_styles(root, 'colorset1')
        self.assertEqual(root[0].get('x1'), '101')
        self.assertEqual(root[1].get('x2'), '101')
        self.assertEqual(ET.tostring(root[2]), axis)
        self.assertEqual(ET.tostring(root[3]), state)

    def test_cs1_chart_compresses_active_mark_kinds_without_changing_data(self):
        for source, expected in [('line "Target" [50, 70]', '#9e1b32'),
                                 ('bar "Actual" [40, 60]\nline "Target" [50, 70]', '#000000')]:
            root = svg('<line x1="10" y1="50" x2="70" y2="30" stroke="#333e48" stroke-width="2"/>'
                       '<line x1="10" y1="70" x2="70" y2="70" stroke="#696969"/>', 'CHART')
            finish_native_styles(root, 'colorset1', source)
            self.assertEqual(property_value(root[0], 'stroke'), expected)
            self.assertEqual(root[0].get('x1'), '10')
            self.assertEqual(root[0].get('y2'), '30')
            self.assertEqual(root[1].get('stroke'), '#696969')
        root = svg('<ellipse cx="25" cy="50" rx="4" ry="4" fill="#4f4f4f" stroke="#4f4f4f"/>', 'CHART')
        finish_native_styles(root, 'colorset1', 'scatter "Sample" [50]')
        self.assertEqual(root[0].get('fill'), '#9e1b32')
        self.assertEqual(property_value(root[0], 'stroke'), 'none')
        root = svg('<line x1="10" y1="50" x2="70" y2="30" stroke="#333e48"/>', 'CHART')
        finish_native_styles(root, 'colorset1', 'line "Target" [50, 70]\nskinparam LineColor #333e48')
        self.assertEqual(property_value(root[0], 'stroke'), '#333e48')
        self.assertIsNone(root.get('data-native-mark-map'))


if __name__ == "__main__":
    unittest.main()

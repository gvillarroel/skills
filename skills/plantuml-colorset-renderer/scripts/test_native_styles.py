#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11.0", "resvg-py>=0.5,<0.6"]
# ///
"""Regression tests for actual native paint, semantic geometry, and theme refresh."""
import unittest
import xml.etree.ElementTree as ET
from native_styles import finish_native_styles, style_findings, source_has_style, STYLE_RULES
from arrow_contrast import property_value
from render_plantuml_directory import inject_theme


def svg(content, family="DESCRIPTION"):
    return ET.fromstring(f'<svg data-diagram-type="{family}">{content}</svg>')


def label(text="Label", fill="#ffffff", x=15, y=25):
    return f'<text x="{x}" y="{y}" textLength="30" font-size="14" fill="{fill}">{text}</text>'


class NativeStyleTests(unittest.TestCase):
    def test_external_participant_label_and_internal_curve(self):
        root = svg('<g class="participant">'+label(y=20)+'<path d="M10 35 L60 35 L60 70 L10 70 Z" fill="#431f47"/><path d="M10 40 Q35 55 60 40" fill="none"/></g>', "SEQUENCE")
        finish_native_styles(root, "colorset2")
        self.assertEqual(root.find(".//text").get("fill"), "#000000")
        self.assertEqual(property_value(root.findall(".//path")[1], "stroke"), "#ffffff")

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
            self.assertEqual([node.get('fill') for node in root], list(STYLE_RULES['colorsets'][colorset]['archimate'].values()))
            self.assertEqual(len({node.get('fill') for node in root}), 7)
            self.assertTrue(all(property_value(node, 'stroke') == 'none' for node in root))
            self.assertEqual(style_findings(root), [])


if __name__ == "__main__":
    unittest.main()

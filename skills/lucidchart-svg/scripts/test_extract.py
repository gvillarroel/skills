#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent metadata extraction, geometry, compatibility, and CLI boundary checks."""

from __future__ import annotations

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("extract_native.py")
SPEC = importlib.util.spec_from_file_location("extract_native_tested", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def svg(inner: str, attrs: str = 'viewBox="0 0 500 200"') -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>{inner}</svg>'


def rect(identifier="a", x=20, y=40, width=100, height=60, extra='fill="#ffffff" stroke="#333333"') -> str:
    return f'<rect data-node-id="{identifier}" x="{x}" y="{y}" width="{width}" height="{height}" {extra}/>'


def flow(edge_extra='stroke="#333333" fill="none"', route='d="M120 70L200 70"') -> str:
    return rect() + rect("b", 200) + f'<path id="e" data-source="a" data-target="b" {route} {edge_extra}/>'


class ExtractionTests(unittest.TestCase):
    def map(self, inner: str, *, attrs='viewBox="0 0 500 200"', coordinates="user-space", semantic=False, viewport=None):
        mapper = MODULE.Mapper(ET.fromstring(svg(inner, attrs)), coordinates=coordinates, semantic_edges=semantic, viewport=viewport)
        return mapper.extract()

    def accepted(self, inner: str, **kwargs):
        graph, report = self.map(inner, **kwargs)
        self.assertIsNotNone(graph, report["ledger"])
        self.assertEqual(report["native_mapping_eligibility"], "eligible")
        self.assertEqual(report["live_import"], "not executed")
        return graph, report

    def refused(self, inner: str, fragment: str | None = None, **kwargs):
        graph, report = self.map(inner, **kwargs)
        self.assertIsNone(graph)
        self.assertEqual(report["native_mapping_eligibility"], "blocked")
        self.assertTrue(any(item["action"] == "blocked" for item in report["ledger"]))
        if fragment:
            self.assertIn(fragment, json.dumps(report))
        return report

    def test_explicit_topology_and_ports_no_default_arrow(self):
        graph, report = self.accepted(flow())
        self.assertEqual((len(graph["nodes"]), len(graph["edges"])), (2, 1))
        edge = graph["edges"][0]
        self.assertEqual((edge["source"], edge["target"]), ("a", "b"))
        self.assertEqual(edge["source_port"], {"x": 1, "y": .5})
        self.assertEqual(edge["target_port"], {"x": 0, "y": .5})
        self.assertEqual((edge["source_marker"], edge["target_marker"]), ("none", "none"))
        self.assertEqual((graph["page_width"], graph["page_height"]), (500, 200))
        self.assertTrue(any(item["feature"] == "source-visible-edge" for item in report["ledger"]))

    def test_no_proximity_topology_inference(self):
        self.refused('<rect x="20" y="40" width="100" height="60"/><rect x="200" y="40" width="100" height="60"/><path d="M120 70L200 70" stroke="#333333"/>', "missing-node-metadata")

    def test_semantic_edge_is_explicit_adaptation(self):
        self.refused(flow(edge_extra=""), "--semantic-edges")
        graph, report = self.accepted(flow(edge_extra=""), semantic=True)
        self.assertEqual((graph["edges"][0]["stroke_width"], graph["edges"][0]["target_marker"]), (1, "arrow"))
        adaptation = next(item for item in report["ledger"] if item["feature"] == "semantic-edge-artwork")
        self.assertFalse(adaptation["source_visible_stroke"])
        self.assertFalse(adaptation["source_visible_markers"])

    def test_vertical_translated_ellipse(self):
        inner = '<g transform="translate(10 20)"><ellipse data-node-id="a" cx="170" cy="50" rx="70" ry="30" fill="#ffeecc"/><rect data-node-id="b" x="100" y="170" width="140" height="60" fill="#ffffff"/><path id="e" data-source="a" data-target="b" d="M170 80L170 170"/></g>'
        graph, _ = self.accepted(inner, attrs='viewBox="0 0 400 500"', semantic=True)
        first = graph["nodes"][0]
        self.assertEqual([first[key] for key in ("x", "y", "width", "height")], [110, 40, 140, 60])
        edge = graph["edges"][0]
        self.assertEqual(edge["source_port"], {"x": .5, "y": 1})
        self.assertEqual(edge["target_port"], {"x": .5, "y": 0})

    def test_viewport_default_meet_exact(self):
        graph, _ = self.accepted(rect(x=5, y=10, width=20, height=30, extra='fill="#ffffff"'), attrs='width="300" height="200" viewBox="0 0 100 100"', coordinates="viewport-pixels")
        self.assertEqual([graph["nodes"][0][key] for key in ("x", "y", "width", "height")], [60, 20, 40, 60])

    def test_viewport_none_anisotropic_geometry(self):
        graph, _ = self.accepted(rect(x=5, y=10, width=20, height=30, extra='fill="#ffffff"'), attrs='width="300" height="200" viewBox="0 0 100 100" preserveAspectRatio="none"', coordinates="viewport-pixels")
        self.assertEqual([graph["nodes"][0][key] for key in ("x", "y", "width", "height")], [15, 20, 60, 60])

    def test_viewport_slice_alignment_exact(self):
        graph, _ = self.accepted(rect(x=10, y=10, width=10, height=10, extra='fill="#ffffff"'), attrs='width="300" height="200" viewBox="0 0 100 100" preserveAspectRatio="xMinYMin slice"', coordinates="viewport-pixels")
        self.assertEqual([graph["nodes"][0][key] for key in ("x", "y", "width", "height")], [30, 30, 30, 30])

    def test_viewbox_origin_and_mode_are_distinct(self):
        inner = rect(x=110, y=-40, width=20, height=30, extra='fill="#ffffff"')
        attrs = 'width="400" height="200" viewBox="100 -50 200 100"'
        author, _ = self.accepted(inner, attrs=attrs)
        rendered, _ = self.accepted(inner, attrs=attrs, coordinates="viewport-pixels")
        self.assertEqual([author["nodes"][0][key] for key in ("x", "y", "width", "height")], [10, 10, 20, 30])
        self.assertEqual([rendered["nodes"][0][key] for key in ("x", "y", "width", "height")], [20, 20, 40, 60])

    def test_viewport_override_and_missing_resolution(self):
        inner = rect(x=5, y=10, width=20, height=30, extra='fill="#ffffff"')
        self.refused(inner, "requires explicit root dimensions", coordinates="viewport-pixels")
        graph, _ = self.accepted(inner, coordinates="viewport-pixels", viewport=[500, 200])
        self.assertEqual(graph["nodes"][0]["x"], 5)

    def test_transform_order_independent_expected_values(self):
        a, _ = self.accepted('<g transform="translate(10 20) scale(2)">' + rect(x=5, y=7, width=10, height=10, extra='fill="#ffffff"') + '</g>')
        b, _ = self.accepted('<g transform="scale(2)"><g transform="translate(10 20)">' + rect(x=5, y=7, width=10, height=10, extra='fill="#ffffff"') + '</g></g>')
        self.assertEqual((a["nodes"][0]["x"], a["nodes"][0]["y"]), (20, 34))
        self.assertEqual((b["nodes"][0]["x"], b["nodes"][0]["y"]), (30, 54))

    def test_positive_axis_matrix_and_refusals(self):
        graph, _ = self.accepted('<g transform="matrix(2 0 0 3 10 20)">' + rect(x=5, y=7, width=10, height=10, extra='fill="#ffffff"') + '</g>')
        self.assertEqual([graph["nodes"][0][key] for key in ("x", "y", "width", "height")], [20, 41, 20, 30])
        for value in ("rotate(45)", "skewX(10)", "scale(-1 1)", "scale(0)", "matrix(1 1 0 1 0 0)", "translate(nan)"):
            with self.subTest(transform=value):
                self.refused(f'<g transform="{value}">' + rect() + '</g>')

    def test_nested_viewport_refused_with_specific_feature(self):
        self.refused('<svg x="20" y="30" width="100" height="50" viewBox="0 0 20 10">' + rect(x=1, y=1, width=10, height=5) + '</svg>', "nested-viewport")

    def test_inherited_paint_and_inline_override(self):
        graph, _ = self.accepted('<g fill="#ffeecc" stroke="#333333" stroke-width="3">' + rect(extra='style="fill:#00ff00;stroke:#123456"') + '</g>')
        node = graph["nodes"][0]
        self.assertEqual((node["fill"], node["stroke"], node["stroke_width"]), ("#00ff00", "#123456", 3))

    def test_inline_geometry_override(self):
        graph, _ = self.accepted(rect(extra='style="x:40px;width:80px;fill:#ffffff"'))
        self.assertEqual((graph["nodes"][0]["x"], graph["nodes"][0]["width"]), (40, 80))

    def test_stylesheet_cascade_and_complex_inline_css_refused(self):
        self.refused('<style>#a{fill:#00ff00}</style>' + rect(extra='id="a" fill="#ff0000"'), "stylesheet-cascade")
        for style in ("fill:var(--color)", "fill:red!important", "fill:u\\72l(remote)", "font:14px Arial", "fill:red/*x*/"):
            with self.subTest(style=style):
                self.refused(rect(extra=f'style="{style}"'))

    def test_solid_color_normalization_and_alpha_refusals(self):
        for value, expected in (("#ABCDEF", "#abcdef"), ("#abc", "#aabbcc"), ("red", "#ff0000"), ("rgb(1, 2, 3)", "#010203")):
            with self.subTest(color=value):
                graph, _ = self.accepted(rect(extra=f'fill="{value}"'))
                self.assertEqual(graph["nodes"][0]["fill"], expected)
        for value in ("none", "transparent", "#abcd", "rgba(1,2,3,.5)", "currentColor", "url(#g)"):
            with self.subTest(color=value):
                self.refused(rect(extra=f'fill="{value}"'))

    def test_no_stroke_and_svg_initial_fill(self):
        graph, report = self.accepted(rect(extra=""))
        self.assertEqual((graph["nodes"][0]["fill"], graph["nodes"][0]["stroke_width"]), ("#000000", 0))
        self.assertTrue(any(item["feature"] == "no-visible-stroke" and item["action"] == "unknown" for item in report["ledger"]))

    def test_dash_class_disclosure_and_fractional_width_refusal(self):
        graph, report = self.accepted(rect(extra='fill="#ffffff" stroke="#333333" stroke-width="3" stroke-dasharray="4 2"'))
        self.assertEqual(graph["nodes"][0]["stroke_style"], "dashed")
        self.assertTrue(any(item["feature"] == "dash-pattern" and item["action"] == "adapted" for item in report["ledger"]))
        self.refused(rect(extra='fill="#ffffff" stroke="#333333" stroke-width="1.5"'), "whole number")
        self.refused(rect(extra='fill="#ffffff" stroke="#333333" stroke-dasharray="1 2 3 4"'))

    def test_rounding_maps_diameter_and_elliptical_radius_refused(self):
        graph, _ = self.accepted(rect(extra='fill="#ffffff" rx="5"'))
        self.assertEqual(graph["nodes"][0]["rounding"], 10)
        self.refused(rect(extra='fill="#ffffff" rx="5" ry="3"'), "Elliptical corner")

    def test_opacity_preserved_only_when_fusion_does_not_change_text(self):
        graph, _ = self.accepted(rect(extra='fill="#ffffff" opacity="0.4"'))
        self.assertEqual(graph["nodes"][0]["opacity"], 40)
        self.refused('<g opacity="0.5">' + rect() + '</g>', "group-opacity")
        self.refused(rect(extra='fill="#ffffff" fill-opacity="0.4"'), "fill-opacity")
        self.refused('<g data-node-id="a"><rect x="20" y="40" width="100" height="60" opacity="0.5"/><text>A</text></g>', "fused native label")
        self.refused(rect(), "group-opacity", attrs='viewBox="0 0 500 200" opacity="0.5"')
        self.refused('<a opacity="0.5">' + rect() + '</a>', "group-opacity")

    def test_nonuniform_stroke_and_text_scaling_refused(self):
        self.refused('<g transform="scale(1 2)">' + rect() + '</g>', "Nonuniform stroke")
        self.refused('<g transform="scale(1 2)"><text data-node-id="a" data-box="20 20 100 40">Text</text></g>', "Nonuniform text")
        graph, _ = self.accepted('<g transform="scale(1 2)">' + rect(extra='fill="#ffffff" stroke="#333333" vector-effect="non-scaling-stroke"') + '</g>')
        self.assertEqual(graph["nodes"][0]["stroke_width"], 1)

    def test_circle_and_diamond_geometry(self):
        graph, _ = self.accepted('<circle data-node-id="a" cx="70" cy="70" r="30"/><polygon data-node-id="b" points="250,40 300,80 250,120 200,80"/>')
        self.assertEqual([graph["nodes"][0][key] for key in ("x", "y", "width", "height")], [40, 40, 60, 60])
        self.assertEqual([graph["nodes"][1][key] for key in ("x", "y", "width", "height")], [200, 40, 100, 80])
        self.refused('<polygon data-node-id="a" points="20,20 80,20 70,80 20,80"/>', "symmetric diamond")

    def test_text_box_labels_preserve_entities_and_whitespace(self):
        graph, report = self.accepted('<text data-node-id="note" data-box="20 20 200 40" fill="#111111" xml:space="preserve">  Review &amp; publish →  </text>')
        self.assertEqual(graph["nodes"][0]["label"], "  Review & publish →  ")
        self.assertEqual(graph["nodes"][0]["text_color"], "#111111")
        self.assertNotIn("fill", graph["nodes"][0])
        self.assertTrue(any(item["feature"] == "text-layout" for item in report["ledger"]))

    def test_group_text_box_and_plain_span(self):
        graph, _ = self.accepted('<g data-node-id="a" data-box="20 20 100 40"><text>A<tspan>B</tspan>C</text></g>')
        self.assertEqual(graph["nodes"][0]["label"], "ABC")
        self.refused('<text data-node-id="a" data-box="20 20 100 40">First<tspan x="20" dy="20">Second</tspan></text>', "Positioned/styled")

    def test_font_fields_copied_and_unsupported_formats_refused(self):
        graph, _ = self.accepted('<g font-family="Arial" font-size="18" font-weight="bold" fill="#123456"><text data-node-id="a" data-box="20 20 100 40" font-style="italic" text-anchor="middle">Hello</text></g>')
        node = graph["nodes"][0]
        self.assertEqual((node["font_family"], node["font_size"], node["text_color"], node["bold"], node["italic"], node["text_align"]), ("Arial", 18, "#123456", True, True, "center"))
        for attrs in ('font-family="Arial, sans-serif"', 'font-weight="500"', 'text-anchor="end"', 'font-style="oblique"', 'stroke="#333333"'):
            with self.subTest(attrs=attrs):
                self.refused(f'<text data-node-id="a" data-box="20 20 100 40" {attrs}>Hello</text>')

    def test_hidden_and_definition_content_not_visible_labels(self):
        graph, report = self.accepted('<defs><text id="template">Template</text></defs>' + rect())
        self.assertEqual(len(graph["nodes"]), 1)
        self.assertTrue(any(item["feature"] == "definition-geometry" for item in report["ledger"]))
        self.refused('<g display="none">' + rect() + '</g>', "hidden-content")
        self.refused('<defs>' + rect() + '</defs>', "definition/foreign")

    def test_internal_use_and_cycles_require_normalization(self):
        for inner in ('<defs><rect id="template" width="20" height="30"/></defs><use data-node-id="a" href="#template"/>', '<defs><g id="loop"><use href="#loop"/></g></defs><use data-node-id="a" href="#loop"/>'):
            with self.subTest(inner=inner):
                self.refused(inner, '"feature": "use"')

    def test_multiple_primitives_and_competing_labels_refused(self):
        self.refused('<g data-node-id="a"><rect width="100" height="60"/><circle cx="20" cy="20" r="5"/></g>', "exactly one primary")
        self.refused('<g data-node-id="a"><rect width="100" height="60"/><text>A</text><text>B</text></g>', "Multiple text candidates")
        self.refused('<g data-node-id="a" data-label="A"><rect width="100" height="60"/><text>B</text></g>', "conflicts")

    def test_foreign_namespace_and_outline_only_text_are_not_inferred(self):
        self.refused('<other:rect xmlns:other="urn:other" data-node-id="a" width="20" height="30"/>', "foreign-namespace")
        self.refused('<path data-node-id="a" data-label="Outlined" d="M0 0L5 10L10 0Z"/>', "supported primary geometry")

    def test_rich_features_have_source_referenced_diagnostics(self):
        cases = {
            "gradient": '<defs><linearGradient id="g"><stop offset="0" stop-color="#ffffff"/></linearGradient></defs>' + rect(extra='fill="url(#g)"'),
            "filter": '<defs><filter id="f"/></defs>' + rect(extra='filter="url(#f)"'),
            "mask": '<defs><mask id="m"/></defs>' + rect(extra='mask="url(#m)"'),
            "clip": '<defs><clipPath id="c"/></defs>' + rect(extra='clip-path="url(#c)"'),
            "image": '<image data-node-id="a" href="data:image/png;base64,aGVsbG8="/>',
            "foreignObject": '<foreignObject data-node-id="a"><div xmlns="http://www.w3.org/1999/xhtml">Hello</div></foreignObject>',
            "SMIL": rect() + '<animate attributeName="x" from="0" to="10"/>',
            "CSS-animation": '<style>@keyframes move{to{transform:translateX(10px)}}.a{animation:move 1s infinite}</style>' + rect(),
        }
        for name, inner in cases.items():
            with self.subTest(feature=name):
                report = self.refused(inner)
                self.assertTrue(all("source_ref" in item and "feature" in item for item in report["ledger"]))
                self.assertIn("asset", report["asset_route"].lower())

    def test_geometry_and_reference_errors(self):
        for inner in (rect(width=-20), rect(width=0), rect(x=-1), rect(x=480), rect().replace('width="100"', 'width="NaN"'), flow(route='d="this is not path data"'), flow(route='d="M120 70C140 20 180 20 200 70"'), flow().replace('data-target="b"', 'data-target="missing"'), flow().replace('data-target="b"', ''), rect() + rect(), flow().replace('id="e"', 'id="a"')):
            with self.subTest(inner=inner):
                self.refused(inner)

    def test_endpoint_match_requires_declared_contour(self):
        self.refused(flow(route='d="M100 70L200 70"'), "inside the node")
        self.refused(flow(route='d="M121 70L200 70"'), "does not match")
        inner = '<ellipse data-node-id="a" cx="70" cy="70" rx="50" ry="30"/>' + rect("b", 200) + '<path id="e" data-source="a" data-target="b" d="M120 40L200 70" stroke="#333333"/>'
        self.refused(inner, "source contour")
        rounded = rect(extra='fill="#ffffff" rx="10" stroke="#333333"') + rect("b", 200) + '<path id="e" data-source="a" data-target="b" d="M20 40L200 70" stroke="#333333"/>'
        self.refused(rounded, "Rounded rectangle")
        tangent = rounded.replace('d="M20 40L200 70"', 'd="M30 40L200 70"')
        graph, _ = self.accepted(tangent)
        self.assertEqual(graph["edges"][0]["source_port"], {"x": .1, "y": 0})

    def test_linear_path_relative_commands_and_joints(self):
        graph, _ = self.accepted(flow(route='d="m120 70 h30 v10 h50 v-10"'))
        self.assertEqual(graph["edges"][0]["joints"], [{"x": 150, "y": 70}, {"x": 150, "y": 80}, {"x": 200, "y": 80}])
        self.refused(flow(edge_extra='stroke="#333333"', route='d="M120 70L150 90L200 70"'), "filled region")

    def test_edge_label_content_and_style(self):
        graph, report = self.accepted(flow() + '<text data-edge-id="e" x="150" y="60" fill="#123456" font-size="12" font-family="Arial">yes &amp; next</text>')
        edge = graph["edges"][0]
        self.assertEqual((edge["label"], edge["label_color"], edge["label_font_size"]), ("yes & next", "#123456", 12))
        self.assertTrue(any(item["feature"] == "edge-label-placement" for item in report["ledger"]))

    def test_recognized_marker_and_marker_refusals(self):
        marker = '<defs><marker id="arrow" orient="auto" viewBox="0 0 10 10" refX="10" refY="5"><polygon points="0,0 10,5 0,10" fill="#333333"/></marker></defs>'
        graph, report = self.accepted(marker + flow(edge_extra='stroke="#333333" fill="none" marker-end="url(#arrow)"'))
        self.assertEqual(graph["edges"][0]["target_marker"], "arrow")
        self.assertTrue(any(item["feature"] == "marker" and item["action"] == "adapted" for item in report["ledger"]))
        self.refused(marker.replace('fill="#333333"', 'fill="#ff0000"') + flow(edge_extra='stroke="#333333" marker-end="url(#arrow)"'), "marker color")
        self.refused(marker + flow(edge_extra='stroke="#333333" marker-start="url(#arrow)"'), "face outward")
        self.refused(marker.replace('<polygon points="0,0 10,5 0,10" fill="#333333"/>', '<path d="M0 0L10 5L0 10Z"/>') + flow(edge_extra='stroke="#333333" marker-end="url(#arrow)"'), "triangular polygon")
        self.refused(flow(edge_extra='stroke="#333333" marker-end="url(#missing)"'), "unresolved")
        self.refused(marker.replace('refX="10"', 'refX="0"') + flow(edge_extra='stroke="#333333" marker-end="url(#arrow)"'), "reference point")
        self.refused(marker.replace('orient="auto"', 'orient="auto" opacity="0"') + flow(edge_extra='stroke="#333333" marker-end="url(#arrow)"'), "marker opacity")
        self.refused(marker.replace('<polygon ', '<polygon transform="translate(20 0)" ') + flow(edge_extra='stroke="#333333" marker-end="url(#arrow)"'), "Transformed marker")

    def test_catalog_type_is_explicit_and_properties_are_strict(self):
        graph, _ = self.accepted(rect(extra='fill="#ffffff" data-lucid-type="process"'))
        self.assertEqual(graph["nodes"][0]["type"], "process")
        self.refused(rect(extra='data-lucid-type="inventedNativeType"'), "not verified")
        self.refused(rect(extra="data-lucid-properties='{&quot;one&quot;:1,&quot;one&quot;:2}'"), "Duplicate field")
        self.refused(rect(extra="data-lucid-properties='{&quot;one&quot;:NaN}'"), "Nonfinite JSON")
        self.refused(rect(extra="data-lucid-properties='{&quot;one&quot;:[&quot;\\ud800&quot;]}'"), "valid Unicode")

    def test_unowned_artwork_and_dangling_edge_label_refused(self):
        self.refused(rect() + '<circle cx="200" cy="50" r="5"/>', "unmapped-artwork")
        self.refused(flow() + '<text data-edge-id="missing">dangling</text>', "unmapped-artwork")

    def test_unsafe_ids_rewritten_consistently(self):
        graph, report = self.accepted(flow().replace('data-node-id="a"', 'data-node-id="unsafe source id"').replace('data-source="a"', 'data-source="unsafe source id"'))
        native_id = graph["nodes"][0]["id"]
        self.assertRegex(native_id, r"^[A-Za-z0-9_.~-]{1,36}$")
        self.assertEqual(graph["edges"][0]["source"], native_id)
        self.assertEqual(report["source_to_native_ids"]["unsafe source id"], native_id)


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lucid-extract-", dir=Path.cwd())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.output, self.report = (self.root / name for name in ("source.svg", "out/graph.json", "out/report.json"))

    def run_cli(self, source: str, *extra):
        self.source.write_text(source, encoding="utf-8")
        original = self.source.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), "--coordinates", "user-space", "--output", str(self.output), "--report", str(self.report), *extra], capture_output=True)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertNotIn(b"Traceback", result.stderr)
        return result

    def test_accepted_exact_paths_and_compiler_contract(self):
        result = self.run_cli(svg(flow()))
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8"))
        self.assertTrue(self.output.is_file())
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertTrue(report["graph_written"])
        self.assertEqual(report["blocking_count"], 0)
        self.assertEqual(json.loads(result.stdout)["live_import"], "not executed")

    def test_blocked_report_written_no_graph_for_rich_source(self):
        result = self.run_cli(svg(rect() + '<foreignObject><div xmlns="http://www.w3.org/1999/xhtml">Hello</div></foreignObject>'))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.output.exists())
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertFalse(report["graph_written"])
        self.assertTrue(any(item["feature"] == "foreignObject" for item in report["ledger"]))

    def test_invalid_xml_and_resource_error_report_written(self):
        for source in ('<svg', svg(rect() + '<image href="https://example.com/x.png"/>')):
            with self.subTest(source=source):
                result = self.run_cli(source, "--overwrite")
                self.assertEqual(result.returncode, 2)
                self.assertTrue(self.report.is_file())
                self.assertFalse(self.output.exists())

    def test_output_preservation_and_source_collision(self):
        self.output.parent.mkdir(parents=True)
        self.output.write_bytes(b"prior graph")
        result = self.run_cli(svg(flow()))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.output.read_bytes(), b"prior graph")
        self.assertTrue(self.report.is_file())
        original = self.source.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), "--coordinates", "user-space", "--output", str(self.source), "--report", str(self.report), "--overwrite"], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_unicode_stdout_under_legacy_encoding(self):
        source = svg('<text data-node-id="a" data-box="20 20 100 40">Review → publish</text>')
        self.source.write_text(source, encoding="utf-8")
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), "--coordinates", "user-space", "--output", str(self.output), "--report", str(self.report)], capture_output=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8"))["nodes"][0]["label"], "Review → publish")
        self.assertEqual(json.loads(result.stdout)["native_mapping_eligibility"], "eligible")

    def test_output_write_error_report_is_accurate(self):
        self.output.mkdir(parents=True)
        result = self.run_cli(svg(flow()), "--overwrite")
        self.assertEqual(result.returncode, 2)
        report = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertFalse(report["graph_written"])
        self.assertEqual(report["native_mapping_eligibility"], "blocked")
        self.assertTrue(any(item["feature"] == "output-write" for item in report["ledger"]))

    def test_nonfinite_viewport_diagnostic(self):
        result = self.run_cli(svg(rect()), "--viewport", "nan", "200")
        self.assertEqual(result.returncode, 2)
        self.assertTrue(self.report.is_file())
        self.assertFalse(self.output.exists())

    def test_hardlink_alias_does_not_modify_source(self):
        self.source.write_text(svg(flow()), encoding="utf-8")
        self.output.parent.mkdir(parents=True)
        os.link(self.source, self.output)
        original = self.source.read_bytes()
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.source), "--coordinates", "user-space", "--output", str(self.output), "--report", str(self.report), "--overwrite"], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.source.read_bytes(), original)

    def test_copied_runtime_resource_remains_unchanged(self):
        bundle = SCRIPT.parent.parent
        copied = self.root / "skill"
        shutil.copytree(bundle, copied, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "node_modules", "examples"))
        def digests():
            return {str(path.relative_to(copied)): hashlib.sha256(path.read_bytes()).hexdigest() for path in copied.rglob("*") if path.is_file()}
        before = digests()
        self.source.write_text(svg(flow()), encoding="utf-8")
        result = subprocess.run([sys.executable, str(copied / "scripts/extract_native.py"), str(self.source), "--coordinates", "user-space", "--output", str(self.output), "--report", str(self.report)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(digests(), before)
        self.assertEqual(list(copied.rglob("*.pyc")), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

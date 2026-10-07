#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise local Standard Import packaging without network or account access.

Run: uv run --script scripts/test_native.py
"""

from __future__ import annotations

import importlib.util
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).with_name("build_native.py")
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("build_native", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
NATIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NATIVE)


def fixture() -> dict:
    return {
        "title": "Explicit graph",
        "nodes": [
            {"id": "page1", "type": "rectangle", "x": 20, "y": 30, "width": 100, "height": 60,
             "label": "Start <draft> & review\nNext line", "fill": "#ABCDEF", "stroke": "#123456", "text_color": "#456789", "font_size": 16},
            {"id": "choice", "type": "diamond", "x": 170, "y": 25, "width": 80, "height": 70, "label": "Ready?"},
            {"id": "finish", "type": "ellipse", "x": 300, "y": 35, "width": 100, "height": 50, "label": "Done"},
            {"id": "note", "type": "text", "x": 40, "y": 140, "width": 200, "height": 40, "label": "Note", "text_color": "#AABBCC", "font_size": 12},
        ],
        "edges": [
            {"id": "e1", "source": "page1", "target": "choice", "label": "yes <1>", "source_port": {"x": 1, "y": .5}, "target_port": {"x": 0, "y": .5}},
            {"id": "e2", "source": "choice", "target": "finish"},
        ],
    }


class NativePackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="lucidchart-native-", dir=Path.cwd())
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.graph = self.root / "source.json"
        self.output = self.root / "nested" / "exact-name.lucid"
        self.document = self.root / "other" / "exact-document.json"

    def run_builder(self, graph: object, *extra: str) -> subprocess.CompletedProcess:
        self.graph.write_text(json.dumps(graph), encoding="utf-8")
        return subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(self.output), *extra], capture_output=True, text=True, encoding="utf-8", check=False)

    def test_unicode_output_path_with_legacy_pipe_encoding(self) -> None:
        self.graph.write_text(json.dumps(fixture()), encoding="utf-8")
        output = self.root / "review-→-publish.lucid"
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(output)], capture_output=True, env=environment)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["package"], str(output))
        self.assertTrue(output.is_file())

    def test_exact_package_contents_native_shapes_and_attachment(self) -> None:
        result = self.run_builder(fixture(), "--document-json", str(self.document))
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual((status["shape_count"], status["connector_count"]), (4, 2))
        self.assertEqual(status["live_import"], "not executed")
        self.assertEqual(len(status["approximations"]), 1)
        self.assertIn("ellipse", status["approximations"][0])
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(archive.namelist(), ["document.json"])
            raw = archive.read("document.json")
            self.assertIsNone(archive.testzip())
            entry = archive.getinfo("document.json")
            self.assertEqual(entry.date_time, (2000, 1, 1, 0, 0, 0))
            self.assertEqual(entry.compress_type, zipfile.ZIP_STORED)
        self.assertEqual(raw, self.document.read_bytes())
        native = json.loads(raw)
        self.assertEqual(native["version"], 1)
        page = native["pages"][0]
        self.assertEqual(page["id"], "page2")
        self.assertEqual(page["title"], "Explicit graph")
        shapes = {shape["id"]: shape for shape in page["shapes"]}
        self.assertEqual(shapes["page1"]["boundingBox"], {"x": 20, "y": 30, "w": 100, "h": 60})
        self.assertEqual(shapes["page1"]["style"]["fill"], {"type": "color", "color": "#abcdef"})
        self.assertIn("Start &lt;draft&gt; &amp; review<br>Next line", shapes["page1"]["text"])
        self.assertEqual(shapes["finish"]["type"], "circle")
        self.assertEqual(shapes["choice"]["type"], "diamond")
        self.assertNotIn("style", shapes["note"])
        self.assertIn("color:#aabbcc", shapes["note"]["text"])
        observed_edges = [(line["endpoint1"]["shapeId"], line["endpoint2"]["shapeId"]) for line in page["lines"]]
        self.assertEqual(observed_edges, [("page1", "choice"), ("choice", "finish")])
        self.assertEqual(page["lines"][1]["endpoint2"]["position"], {"x": 0, "y": .5})
        self.assertIn("yes &lt;1&gt;", page["lines"][0]["text"][0]["text"])
        self.assertEqual(page["lines"][0]["endpoint2"]["style"], "arrow")

    def test_deterministic_bytes_and_unchanged_source(self) -> None:
        self.assertEqual(self.run_builder(fixture()).returncode, 0)
        first, source = self.output.read_bytes(), self.graph.read_bytes()
        self.assertEqual(self.run_builder(fixture()).returncode, 0)
        self.assertEqual(self.output.read_bytes(), first)
        self.assertEqual(self.graph.read_bytes(), source)

    def test_baseline_package_bytes_are_backward_compatible(self) -> None:
        raw = NATIVE.document_bytes(NATIVE.build_document(fixture()))
        self.assertEqual(hashlib.sha256(raw).hexdigest(), "5dc61f8e9e8ec035bd416502c0d5ba354d252e8e7fecd2daff8714ae8cc12ce5")
        self.assertEqual(hashlib.sha256(NATIVE.package_bytes(raw)).hexdigest(), "e18ba4157b2f469f634aa2d737c8b071631d193cc5dd9f936b5031a0870a405f")

    def test_cli_does_not_mutate_isolated_skill_resources(self) -> None:
        resource = self.root / "skill"
        scripts = resource / "scripts"
        references = resource / "references"
        scripts.mkdir(parents=True)
        references.mkdir()
        for name in ("build_native.py", "native_catalog.py"):
            shutil.copyfile(SCRIPT.with_name(name), scripts / name)
        shutil.copyfile(SCRIPT.parent.parent / "references" / "native-shapes.json", references / "native-shapes.json")
        before = {str(path.relative_to(resource)): path.read_bytes() for path in resource.rglob("*") if path.is_file()}
        self.graph.write_text(json.dumps(fixture()), encoding="utf-8")
        environment = dict(os.environ)
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        result = subprocess.run([sys.executable, str(scripts / "build_native.py"), str(self.graph), "--output", str(self.output)],
                                env=environment, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        after = {str(path.relative_to(resource)): path.read_bytes() for path in resource.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_rich_styles_literal_text_and_explicit_page(self) -> None:
        graph = fixture()
        graph.update(page_width=500.5, page_height=250, page_fill="#112233", infinite_canvas=False, auto_tiling=False)
        graph["nodes"][0].update(stroke_width=3, stroke_style="dashed", rounding=24, rotation=15.5,
                                 opacity=85, z_index=-2, font_family="Georgia, serif", bold=True, italic=True,
                                 underline=True, strike=True, text_align="left", vertical_align="center")
        graph["edges"][0].update(stroke="#AA1133", stroke_width=2, stroke_style="dotted",
                                 source_marker="openCircle", target_marker="hollowArrow", z_index=4,
                                 label_position=.8, label_side="bottom", label_color="#223344", label_font_size=18,
                                 label_font_family="Georgia", label_bold=True, label_italic=True, label_underline=True,
                                 label_strike=True, label_align="left", label_vertical_align="center")
        page = NATIVE.build_document(graph)["pages"][0]
        shape = page["shapes"][0]
        self.assertEqual(shape["style"], {"fill": {"type": "color", "color": "#abcdef"},
                                         "stroke": {"color": "#123456", "width": 3, "style": "dashed"},
                                         "textColor": "#456789", "rounding": 24})
        self.assertEqual((shape["boundingBox"]["rotation"], shape["opacity"], shape["zIndex"]), (15.5, 85, -2))
        self.assertIn('font-family:Georgia, serif;font-size:16px;color:#456789;text-align:left;vertical-align:center', shape["text"])
        self.assertIn('<b><i><u><s>Start &lt;draft&gt; &amp; review<br>Next line</s></u></i></b>', shape["text"])
        line = page["lines"][0]
        self.assertEqual(line["stroke"], {"color": "#aa1133", "width": 2, "style": "dotted"})
        self.assertEqual((line["endpoint1"]["style"], line["endpoint2"]["style"], line["zIndex"]), ("openCircle", "hollowArrow", 4))
        self.assertEqual((line["text"][0]["position"], line["text"][0]["side"]), (.8, "bottom"))
        self.assertIn('font-family:Georgia;font-size:18px;color:#223344;text-align:left', line["text"][0]["text"])
        self.assertIn('<b><i><u><s>yes &lt;1&gt;</s></u></i></b>', line["text"][0]["text"])
        self.assertEqual(page["settings"], {"fillColor": "#112233", "size": {"type": "custom", "w": 500.5, "h": 250},
                                            "infiniteCanvas": False, "autoTiling": False})

    def test_all_documented_marker_styles_on_both_ends(self) -> None:
        expected = {"none", "aggregation", "arrow", "hollowArrow", "openArrow", "async1", "async2", "closedSquare",
                    "openSquare", "bpmnConditional", "bpmnDefault", "closedCircle", "openCircle", "composition",
                    "exactlyOne", "generalization", "many", "nesting", "one", "oneOrMore", "zeroOrMore", "zeroOrOne"}
        self.assertEqual(NATIVE.MARKERS, expected)
        graph = fixture()
        graph["edges"] = [{"id": f"e{index}", "source": "page1", "target": "choice", "source_marker": marker, "target_marker": marker}
                          for index, marker in enumerate(sorted(expected))]
        lines = NATIVE.build_document(graph)["pages"][0]["lines"]
        self.assertEqual({line["endpoint1"]["style"] for line in lines}, expected)
        self.assertEqual({line["endpoint2"]["style"] for line in lines}, expected)

    def test_straight_joints_elbow_routes_and_smart_ports(self) -> None:
        graph = fixture()
        graph["edges"] = [
            {"id": "poly", "source": "page1", "target": "choice", "joints": [{"x": -10, "y": 100}, {"x": 155.5, "y": 130}]},
            {"id": "orthogonal", "source": "page1", "target": "choice", "line_type": "elbow",
             "elbow_points": [{"x": 140, "y": 60}, {"x": 140, "y": 110}, {"x": 150, "y": 110}, {"x": 150, "y": 60}]},
            {"id": "auto", "source": "page1", "target": "choice", "line_type": "elbow", "smart": True},
        ]
        lines = NATIVE.build_document(graph)["pages"][0]["lines"]
        self.assertEqual(lines[0]["joints"], graph["edges"][0]["joints"])
        self.assertEqual(lines[1]["elbowControlPoints"], graph["edges"][1]["elbow_points"])
        self.assertNotIn("position", lines[2]["endpoint1"])
        self.assertNotIn("position", lines[2]["endpoint2"])
        self.assertEqual(lines[2]["endpoint1"]["shapeId"], "page1")

    def test_multi_labels_and_explicit_endpoint_types(self) -> None:
        graph = fixture()
        graph["edges"] = [
            {"id": "link", "source": {"type": "positionEndpoint", "position": {"x": -50, "y": 90}},
             "target": {"type": "lineEndpoint", "lineId": "main", "position": .75}, "target_marker": "none", "labels": [
                 {"text": "0..* <optional>", "position": .05, "side": "bottom", "bold": True, "font_family": "Georgia", "color": "#AABBCC"},
                 {"text": "1", "position": .95, "side": "middle", "italic": True},
             ]},
            {"id": "main", "source": {"type": "shapeEndpoint", "shapeId": "page1"},
             "target": {"type": "shapeEndpoint", "shapeId": "choice", "position": {"x": 0, "y": .25}}, "labels": []},
        ]
        lines = NATIVE.build_document(graph)["pages"][0]["lines"]
        self.assertEqual(lines[0]["endpoint1"], {"type": "positionEndpoint", "style": "none", "position": {"x": -50, "y": 90}})
        self.assertEqual(lines[0]["endpoint2"], {"type": "lineEndpoint", "style": "none", "lineId": "main", "position": .75})
        self.assertEqual([(label["position"], label["side"]) for label in lines[0]["text"]], [(.05, "bottom"), (.95, "middle")])
        self.assertIn('<b>0..* &lt;optional&gt;</b>', lines[0]["text"][0]["text"])
        self.assertIn('font-family:Georgia;font-size:14px;color:#aabbcc', lines[0]["text"][0]["text"])
        self.assertIn('<i>1</i>', lines[0]["text"][1]["text"])
        self.assertNotIn("position", lines[1]["endpoint1"])
        self.assertEqual(lines[1]["endpoint2"]["position"], {"x": 0, "y": .25})
        self.assertEqual(lines[1]["text"], [])

    def test_nested_groups_and_layers_preserve_membership_and_stack(self) -> None:
        graph = fixture()
        graph.update(groups=[{"id": "inner", "items": ["page1", "choice", "e1"], "z_index": -4},
                             {"id": "outer", "items": ["inner", "finish", "e2"], "z_index": 5}],
                     layers=[{"id": "foreground", "title": "Foreground <literal>", "items": ["outer", "note"], "layer_index": 3}])
        page = NATIVE.build_document(graph)["pages"][0]
        self.assertEqual(page["groups"], [{"id": "inner", "items": ["page1", "choice", "e1"], "zIndex": -4},
                                           {"id": "outer", "items": ["inner", "finish", "e2"], "zIndex": 5}])
        self.assertEqual(page["layers"], [{"id": "foreground", "title": "Foreground <literal>", "items": ["outer", "note"], "layerIndex": 3}])
        self.assertEqual(graph["groups"][0]["z_index"], -4)

    def test_catalog_properties_emit_literal_labels_and_reject_unsupported_common_fields(self) -> None:
        graph = fixture()
        graph["nodes"][0].update(type="rectangleContainer", properties={"containerTitle": {"text": "<b>literal</b> & two\nlines"}, "magnetize": True, "assistedLayout": False})
        shape = NATIVE.build_document(graph)["pages"][0]["shapes"][0]
        self.assertEqual(shape["containerTitle"]["text"], "&lt;b&gt;literal&lt;/b&gt; &amp; two<br/>lines")
        self.assertEqual((shape["magnetize"], shape["assistedLayout"]), (True, False))
        self.assertEqual(graph["nodes"][0]["properties"]["containerTitle"]["text"], "<b>literal</b> & two\nlines")
        hotspot = {"nodes": [{"id": "h", "type": "hotspot", "x": 0, "y": 0, "width": 30, "height": 40, "label": ""}]}
        self.assertNotIn("text", NATIVE.build_document(hotspot)["pages"][0]["shapes"][0])
        for mutate in (
            lambda: graph["nodes"][0].update(rotation=0),
            lambda: graph["nodes"][0].update(properties={"unsupported": True}),
            lambda: hotspot["nodes"][0].update(label="not allowed"),
        ):
            original = json.loads(json.dumps(graph))
            mutate()
            with self.assertRaises(NATIVE.GraphError):
                NATIVE.build_document(hotspot if hotspot["nodes"][0]["label"] else graph)
            graph = original

    def test_infinite_canvas_and_explicit_opacity_boundaries(self) -> None:
        graph = fixture()
        graph["infinite_canvas"] = True
        graph["nodes"][0]["opacity"] = 0
        graph["nodes"][1]["opacity"] = 100
        page = NATIVE.build_document(graph)["pages"][0]
        self.assertEqual(page["settings"], {"fillColor": "#ffffff", "infiniteCanvas": True})
        self.assertEqual([page["shapes"][index]["opacity"] for index in (0, 1)], [0, 100])

    def test_cloud_native_style_defaults_are_not_overridden(self) -> None:
        graph = {"nodes": [{"id": "gcp", "type": "namedShape", "x": 0, "y": 0, "width": 80, "height": 80,
                             "label": "Compute <P1>", "properties": {"className": "GCP2021ComputeEngineIcon"}}]}
        shape = NATIVE.build_document(graph)["pages"][0]["shapes"][0]
        self.assertNotIn("style", shape)
        self.assertEqual(shape["text"], "Compute &lt;P1&gt;")
        graph["nodes"][0].update(stroke_width=3, font_size=18, italic=True)
        document = NATIVE.build_document(graph)
        shape = document["pages"][0]["shapes"][0]
        self.assertEqual(shape["style"], {"stroke": {"width": 3}})
        self.assertEqual(shape["text"], '<p style="font-size:18px"><i>Compute &lt;P1&gt;</i></p>')
        report = NATIVE.compatibility_report(graph, document)
        self.assertIn("native_library_defaults", {item["feature"] for item in report["requires_live_check"]})

    def test_numeric_and_punctuated_font_names_are_safely_quoted(self) -> None:
        graph = fixture()
        graph["nodes"][0]["font_family"] = "Source Sans 3, Font.Name, serif"
        shape = NATIVE.build_document(graph)["pages"][0]["shapes"][0]
        self.assertIn("font-family:'Source Sans 3','Font.Name', serif;", html.unescape(shape["text"]))
        graph["nodes"][0]["font_family"] = "Georgia,,serif"
        with self.assertRaises(NATIVE.GraphError):
            NATIVE.build_document(graph)

    def test_compatibility_report_and_exact_output_contract(self) -> None:
        graph = fixture()
        graph["nodes"][0].update(stroke_width=0, font_family="Georgia", rotation=12)
        graph["edges"][1].update(line_type="curved", stroke_width=0)
        report_path = self.root / "report.json"
        result = self.run_builder(graph, "--report", str(report_path), "--document-json", str(self.document))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["live_import"], "not executed")
        self.assertIn("not measured", report["rendered_fidelity"])
        self.assertEqual(len(report["approximations"]), 2)
        self.assertEqual({item["feature"] for item in report["requires_live_check"]}, {"font_family", "rotation", "zero_width_stroke"})
        self.assertEqual(report["defaults"]["target_marker"], "arrow")
        self.assertIn("labels", report["supported_fields"]["edge"])
        self.assertEqual(len(report["enums"]["marker"]), 22)
        document = json.loads(self.document.read_text(encoding="utf-8"))["pages"][0]
        self.assertEqual([item["emitted"] for item in report["decisions"]], document["shapes"] + document["lines"])
        self.assertEqual(report["page_settings"], document["settings"])
        self.assertEqual(json.loads(result.stdout)["report"], str(report_path))
        first = report_path.read_bytes()
        self.assertEqual(self.run_builder(graph, "--report", str(report_path), "--document-json", str(self.document)).returncode, 0)
        self.assertEqual(first, report_path.read_bytes())

    def test_extended_invalid_fields_and_conflicts_rejected(self) -> None:
        mutations = []
        for field, value in (("stroke_width", 2.5), ("stroke_width", True), ("stroke_width", -1),
                             ("stroke_style", "none"), ("rounding", 1.5), ("rounding", -1),
                             ("rotation", 361), ("opacity", 50.5), ("opacity", 101), ("z_index", 1.5),
                             ("font_family", 'Georgia; color:red'), ("font_family", '<b>Arial</b>'),
                             ("font_family", 'Arial" onmouseover="x'), ("font_family", " "),
                             ("bold", 1), ("italic", "true"), ("underline", []), ("strike", None),
                             ("text_align", "right"), ("vertical_align", "top"), ("properties", {"unsupported": 1})):
            mutations.append((f"node-{field}-{value}", lambda graph, field=field, value=value: graph["nodes"][0].update({field: value})))
        for field, value in (("stroke_width", 2.5), ("stroke_style", "dash5 3"), ("source_marker", "triangle"),
                             ("target_marker", "block"), ("smart", 1), ("source_port", None), ("source", None),
                             ("line_type", "bezier"), ("label_position", 1.1), ("label_side", "left"),
                             ("label_font_family", "Arial;stroke:none"), ("label_bold", "yes"),
                             ("labels", [{"text": "x", "position": -1}]), ("labels", [{"text": "x", "html": "bad"}]),
                             ("labels", {}), ("labels", [{"side": "top"}])):
            mutations.append((f"edge-{field}-{value}", lambda graph, field=field, value=value: graph["edges"][1].update({field: value})))
        mutations += [
            ("smart-port", lambda graph: graph["edges"][0].update(smart=True)),
            ("smart-joints", lambda graph: graph["edges"][1].update(smart=True, joints=[])),
            ("curved-joints", lambda graph: graph["edges"][1].update(line_type="curved", joints=[])),
            ("straight-elbows", lambda graph: graph["edges"][1].update(elbow_points=[])),
            ("diagonal-elbow", lambda graph: graph["edges"][0].update(line_type="elbow", elbow_points=[{"x": 140, "y": 70}])),
            ("collinear-elbow", lambda graph: graph["edges"][0].update(line_type="elbow", elbow_points=[{"x": 130, "y": 60}, {"x": 140, "y": 60}])),
            ("unknown-joint-fields", lambda graph: graph["edges"][1].update(joints=[{"x": 1, "y": 2, "cp": 3}])),
            ("missing-label", lambda graph: graph["edges"][1].update(label_font_size=12)),
            ("multi-and-legacy-label", lambda graph: graph["edges"][0].update(labels=[])),
            ("multi-and-legacy-style", lambda graph: graph["edges"][1].update(labels=[], label_bold=False)),
            ("text-border", lambda graph: graph["nodes"][3].update(stroke_width=0)),
            ("text-rounding", lambda graph: graph["nodes"][3].update(rounding=0)),
            ("partial-page", lambda graph: graph.update(page_width=500)),
            ("oversized-page", lambda graph: graph.update(page_width=20001, page_height=200)),
            ("zero-page", lambda graph: graph.update(page_width=0, page_height=200)),
            ("bad-page-color", lambda graph: graph.update(page_fill="none")),
            ("infinite-size", lambda graph: graph.update(infinite_canvas=True, page_width=500, page_height=200)),
            ("infinite-tiling", lambda graph: graph.update(infinite_canvas=True, auto_tiling=False)),
            ("bad-tiling", lambda graph: graph.update(auto_tiling=1)),
            ("unknown-group-id", lambda graph: graph.update(groups=[{"id": "g", "items": ["missing"]}])),
            ("duplicate-membership", lambda graph: graph.update(groups=[{"id": "g", "items": ["choice", "choice"]}])),
            ("duplicate-global-id", lambda graph: graph.update(groups=[{"id": "e1", "items": []}])),
            ("group-cycle", lambda graph: graph.update(groups=[{"id": "g1", "items": ["g2"]}, {"id": "g2", "items": ["g1"]}])),
            ("group-self-cycle", lambda graph: graph.update(groups=[{"id": "g1", "items": ["g1"]}])),
            ("two-parents", lambda graph: graph.update(groups=[{"id": "g1", "items": ["choice"]}, {"id": "g2", "items": ["choice"]}])),
            ("group-layer-parent-conflict", lambda graph: graph.update(groups=[{"id": "g", "items": ["choice"]}], layers=[{"id": "l", "title": "L", "items": ["choice"]}])),
            ("layer-in-group", lambda graph: graph.update(groups=[{"id": "g", "items": ["l"]}], layers=[{"id": "l", "title": "L", "items": []}])),
            ("layer-in-layer", lambda graph: graph.update(layers=[{"id": "l", "title": "L", "items": ["other"]}, {"id": "other", "title": "Other", "items": []}])),
            ("wrong-group-array", lambda graph: graph.update(groups={})),
            ("group-unknown-key", lambda graph: graph.update(groups=[{"id": "g", "items": [], "rotation": 0}])),
            ("layer-wrong-integer", lambda graph: graph.update(layers=[{"id": "l", "title": "L", "items": [], "layer_index": True}])),
        ]
        for name, mutate in mutations:
            with self.subTest(case=name):
                graph = fixture()
                mutate(graph)
                with self.assertRaises(NATIVE.GraphError):
                    NATIVE.build_document(graph)

    def test_huge_legal_json_integers_fail_without_tracebacks(self) -> None:
        huge = 10 ** 400
        for scope, field in (("node", "font_size"), ("node", "stroke_width"), ("node", "z_index"),
                             ("node", "height"), ("edge", "stroke_width"), ("edge", "z_index"), ("page", "page_width")):
            with self.subTest(scope=scope, field=field):
                graph = fixture()
                if scope == "page":
                    graph.update(page_width=huge, page_height=100)
                else:
                    graph["nodes" if scope == "node" else "edges"][0][field] = huge
                with self.assertRaises(NATIVE.GraphError):
                    NATIVE.build_document(graph)
                result = self.run_builder(graph)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.output.exists())

    def test_endpoint_reference_and_routing_failures(self) -> None:
        cases = [
            {"source": {"type": "shapeEndpoint", "shapeId": "missing"}},
            {"source": {"type": "shapeEndpoint", "shapeId": "page1", "position": {"x": 2, "y": .5}}},
            {"source": {"type": "shapeEndpoint", "shapeId": "page1", "style": "none"}},
            {"source": {"type": "shapeEndpoint", "shapeId": "page1"}, "source_port": {"x": 1, "y": .5}},
            {"source": {"type": "lineEndpoint", "lineId": "missing", "position": .5}},
            {"source": {"type": "lineEndpoint", "lineId": "e2", "position": .5}},
            {"source": {"type": "lineEndpoint", "lineId": "e1", "position": 2}},
            {"source": {"type": "positionEndpoint", "position": {"x": -20001, "y": 0}}},
            {"source": {"type": "positionEndpoint", "position": {"x": 1, "y": 0}}, "smart": True},
            {"source": {"type": "shapeEndpoint", "shapeId": "page1", "position": {"x": 1, "y": .5}}, "smart": True},
            {"source": {"type": "lineEndpoint", "lineId": "e1", "position": .5}, "line_type": "elbow", "elbow_points": []},
            {"source": {"type": "shapeEndpoint", "shapeId": "page1"}, "line_type": "elbow", "elbow_points": []},
        ]
        for fields in cases:
            with self.subTest(fields=fields):
                graph = fixture()
                graph["edges"][1].update(fields)
                with self.assertRaises(NATIVE.GraphError):
                    NATIVE.build_document(graph)
        graph = fixture()
        graph["edges"][0]["source"] = {"type": "lineEndpoint", "lineId": "e2", "position": .5}
        graph["edges"][0].pop("source_port")
        graph["edges"][1]["source"] = {"type": "lineEndpoint", "lineId": "e1", "position": .5}
        with self.assertRaisesRegex(NATIVE.GraphError, "acyclic"):
            NATIVE.build_document(graph)

    def test_exact_elbow_points_with_absolute_endpoints(self) -> None:
        graph = {"nodes": [], "edges": [{"id": "route", "line_type": "elbow", "source_marker": "none", "target_marker": "none",
                                         "source": {"type": "positionEndpoint", "position": {"x": -10, "y": 0}},
                                         "target": {"type": "positionEndpoint", "position": {"x": 10, "y": 20}},
                                         "elbow_points": [{"x": 10, "y": 0}]}]}
        line = NATIVE.build_document(graph)["pages"][0]["lines"][0]
        self.assertEqual(line["elbowControlPoints"], [{"x": 10, "y": 0}])
        self.assertEqual(line["endpoint2"]["position"], {"x": 10, "y": 20})

    def test_invalid_graphs_fail_before_writing(self) -> None:
        cases = []
        for field, value in (("id", "bad id"), ("id", "x" * 37), ("type", "path"), ("type", []),
                             ("x", -1), ("x", True), ("width", 0), ("width", "100"),
                             ("height", float("inf")), ("height", float("nan")),
                             ("font_size", 0), ("font_size", True), ("fill", "red"),
                             ("stroke", "#123"), ("text_color", "#gggggg"), ("label", 7)):
            graph = fixture()
            graph["nodes"][0][field] = value
            cases.append((f"node-{field}-{value}", graph))
        for modify in (
            lambda graph: graph["nodes"][1].update(id="page1"),
            lambda graph: graph["edges"][0].update(id="page1"),
            lambda graph: graph["edges"][1].update(id="e1"),
            lambda graph: graph["edges"][0].update(source="missing"),
            lambda graph: graph["edges"][0].update(target="missing"),
            lambda graph: graph["edges"][0].update(source_port={"x": 1.1, "y": .5}),
            lambda graph: graph["edges"][0].update(target_port={"x": 0, "y": -.1}),
            lambda graph: graph["edges"][0].update(target_port={"x": 0}),
            lambda graph: graph["edges"][0].update(label=[]),
            lambda graph: graph["nodes"][0].update(x=19999),
            lambda graph: graph["nodes"][3].update(fill="#ffffff"),
            lambda graph: graph["nodes"][0].pop("label"),
            lambda graph: graph.update(nodes={}),
            lambda graph: graph.update(edges="wrong"),
            lambda graph: graph.update(svg="unsupported.svg"),
            lambda graph: graph.update(title=" "),
        ):
            graph = fixture()
            modify(graph)
            cases.append((repr(graph), graph))
        for name, graph in cases:
            with self.subTest(case=name):
                result = self.run_builder(graph)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn("Error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertFalse(self.output.exists())

    def test_duplicate_json_fields_and_surrogates_rejected(self) -> None:
        for raw in ('{"nodes":[],"nodes":[],"edges":[]}', '{"nodes":[],"edges":[],"title":"\\ud800"}'):
            with self.subTest(raw=raw):
                self.graph.write_text(raw, encoding="utf-8")
                result = subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(self.output)], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.output.exists())

    def test_output_path_contract(self) -> None:
        self.graph.write_text(json.dumps(fixture()), encoding="utf-8")
        for output, extra in ((self.root / "diagram.zip", []), (self.output, ["--document-json", str(self.output)]),
                              (self.output, ["--document-json", str(self.graph)]), (self.output, ["--report", str(self.graph)]),
                              (self.output, ["--report", str(self.output)]),
                              (self.output, ["--report", str(self.document), "--document-json", str(self.document)])):
            with self.subTest(output=output, extra=extra):
                source = self.graph.read_bytes()
                result = subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(output), *extra], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.graph.read_bytes(), source)
                self.assertFalse(output.exists())

    def test_hard_link_aliases_cannot_mutate_source_or_outputs(self) -> None:
        source = json.dumps(fixture()).encode("utf-8")
        self.graph.write_bytes(source)
        alias = self.root / "source-alias.lucid"
        try:
            os.link(self.graph, alias)
        except OSError as error:
            self.skipTest(f"Hard links unavailable: {error}")
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(alias)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.graph.read_bytes(), source)
        self.assertEqual(alias.read_bytes(), source)
        self.output.parent.mkdir()
        report = self.root / "report.json"
        report.write_bytes(b"existing evidence")
        os.link(report, self.output)
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(self.output), "--report", str(report)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report.read_bytes(), b"existing evidence")
        self.assertEqual(self.output.read_bytes(), b"existing evidence")

    def test_document_size_limit(self) -> None:
        graph = fixture()
        graph["nodes"][0]["label"] = "x" * 2_000_000
        result = self.run_builder(graph)
        self.assertEqual(result.returncode, 2)
        self.assertIn("2000000-byte limit", result.stderr)
        self.assertFalse(self.output.exists())

    def test_page_boundary_and_empty_supported_document(self) -> None:
        graph = fixture()
        graph["nodes"][0].update(x=19900, y=19940)
        document = NATIVE.build_document(graph)
        size = document["pages"][0]["settings"]["size"]
        self.assertEqual(size, {"type": "custom", "w": 20000, "h": 20000})
        empty = NATIVE.build_document({"nodes": [], "edges": []})
        self.assertEqual(empty["pages"][0]["title"], "Imported diagram")
        self.assertEqual(empty["pages"][0]["shapes"], [])
        without_edges = NATIVE.build_document({"nodes": []})
        self.assertEqual(without_edges["pages"][0]["lines"], [])

    def test_optional_edges_via_positional_cli(self) -> None:
        graph = fixture()
        graph.pop("edges")
        graph["nodes"] = [node for node in graph["nodes"] if node["type"] != "ellipse"]
        result = self.run_builder(graph)
        self.assertEqual(result.returncode, 0, result.stderr)
        status = json.loads(result.stdout)
        self.assertEqual(status["connector_count"], 0)
        self.assertEqual(status["approximations"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

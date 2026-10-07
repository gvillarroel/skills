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
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).with_name("build_native.py")
sys.dont_write_bytecode = True
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
                              (self.output, ["--document-json", str(self.graph)])):
            with self.subTest(output=output, extra=extra):
                source = self.graph.read_bytes()
                result = subprocess.run([sys.executable, str(SCRIPT), str(self.graph), "--output", str(output), *extra], capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.graph.read_bytes(), source)
                self.assertFalse(output.exists())

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
